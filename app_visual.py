import streamlit as st, pandas as pd, plotly.express as px, os, json, io, shutil, zipfile, time
from docxtpl import DocxTemplate
from datetime import datetime
import database as db

st.set_page_config(page_title="AboAgrim Pro DMS", layout="wide", page_icon="⚖️")

# --- 1. CONFIGURACIÓN Y ESTADOS GLOBALES ---
if 'f_nom' not in st.session_state: st.session_state.f_nom = "Lic. Jhonny Matos. M.A., Presidente"
if 'f_dir' not in st.session_state: st.session_state.f_dir = "Abogados y Agrimensores 'AboAgrim' - Plaza Jasansa, Santiago"
if 'f_color' not in st.session_state: st.session_state.f_color = "#1e3a8a"
if 'passwords' not in st.session_state: st.session_state.passwords = {}
if 'unlocked' not in st.session_state: st.session_state.unlocked = ["🏠 Mando", "👤 Registro Maestro", "📂 Archivo", "📄 Plantillas", "📅 Alertas", "💳 Facturación", "⚙️ Configuración"]
if 'p_edit_id' not in st.session_state: st.session_state.p_edit_id = None
if 'zip_reg' not in st.session_state: st.session_state.zip_reg, st.session_state.zip_reg_name = None, "Expediente.zip"
if 'zip_elab' not in st.session_state: st.session_state.zip_elab, st.session_state.zip_elab_name = None, "Documentos.zip"

for k in ['reg_inm', 'reg_apo', 'reg_abog', 'reg_agrim', 'reg_custom']:
    if k not in st.session_state: st.session_state[k] = []

CARPETAS_DESTINO = ["Deslinde", "4_Contratos_Legales", "3_Planos_Gabinete", "1_Identidad", "2_Titulos_Certificaciones", "5_Correspondencia_JI"]
JI_DATA = {
    "Mensuras": {"ACTUALIZACIÓN": [], "DESLINDE": [], "SANEAMIENTO": [], "SUBDIVISIÓN": []},
    "Títulos": {"TRANSFERENCIA": [], "HIPOTECA": []},
    "Tribunales": {"LITIS": [], "HEREDEROS": []}
}
TODOS_LOS_TRAMITES = ["General"] + [f"{j} | {t}" for j, tr in JI_DATA.items() for t in tr.keys()]
ETAPAS_JI = ["Investigación", "Campo", "Gabinete", "Depósito", "Audiencia", "Fallo", "Aprobado", "Cerrado"]
ALERTAS_LEGALES = ["Audiencia (Tribunal)", "Apelación JI (30 días - Ley 108-05)", "Casación (30 días)", "Revisión por Fraude (1 año)", "Prescripción Adquisitiva (10/20 años)", "Caducidad de Instancia (3 años)", "Plazo Administrativo (JI)", "Otro"]

@st.dialog("✏️ Etapa y Cobros")
def modal_editar_estado(e):
    idx = ETAPAS_JI.index(e['estado']) if e['estado'] in ETAPAS_JI else 0
    nes = st.selectbox("Etapa", ETAPAS_JI, index=idx)
    npa = st.number_input("Cobrado RD$", value=float(e.get('pagado',0)))
    if st.button("💾 Guardar"): db.actualizar_expediente_estado(e['id'], nes, npa); st.rerun()

@st.dialog("💵 Abono a Factura")
def modal_abonar(f):
    pend = f['total'] - float(f.get('monto_pagado',0))
    st.info(f"Pendiente: RD$ {pend:,.2f}")
    c1, c2 = st.columns(2)
    m = c1.number_input("Abonar RD$", min_value=0.0, max_value=float(pend), value=float(pend))
    fp = c2.selectbox("Forma", ["Transferencia", "Efectivo", "Cheque"])
    ep = st.selectbox("Etapa", ["Avance", "Intermedio", "Saldo Final"])
    if st.button("💾 Guardar"): db.registrar_abono_factura(f['id'], m, fp, ep); st.rerun()

# --- 2. MOTOR COMPRIMIDO DE VARIABLES (CON CASILLAS DINÁMICAS) ---
def form_estatico(p, d_prev=None):
    ctx = {}
    with st.expander("📄 1. Documento y Proyecto (Metadatos)", expanded=False):
        c1,c2,c3 = st.columns(3)
        ctx['doc_titulo'], ctx['doc_tipo'], ctx['doc_expediente'] = c1.text_input("Título",key=f"{p}1"), c2.selectbox("Tipo", ["Contrato","Informe","Solicitud","Acto","Recurso","Otro"],key=f"{p}2"), c3.text_input("Expediente",key=f"{p}3")
        c4,c5,c6 = st.columns(3)
        ctx['doc_fecha'], ctx['doc_oficina'], ctx['doc_direccion'] = c4.text_input("Fecha",value=datetime.now().strftime("%d/%m/%Y"),key=f"{p}4"), c5.text_input("Oficina",key=f"{p}5"), c6.text_input("Dir. Oficina",key=f"{p}6")
        c7,c8,c9 = st.columns(3)
        ctx['doc_telefono'], ctx['doc_email'], ctx['doc_firma_sol'] = c7.text_input("Teléfono Doc",key=f"{p}7"), c8.text_input("Correo Doc",key=f"{p}8"), c9.text_input("Firma Solicitante",key=f"{p}9")
        c10,c11 = st.columns(2)
        ctx['doc_observaciones'], ctx['doc_notas'] = c10.text_area("Observaciones",key=f"{p}10"), c11.text_area("Notas",key=f"{p}11")
        c12,c13,c14 = st.columns(3)
        ctx['doc_ref_normativas'], ctx['doc_anexos'], ctx['doc_adjuntos'] = c12.text_input("Ref Normativas",key=f"{p}12"), c13.text_input("Anexos",key=f"{p}13"), c14.text_input("Adjuntos",key=f"{p}14")
        
        st.caption("Proyecto / Empresa")
        c15,c16,c17 = st.columns(3)
        ctx['proy_desc'], ctx['proy_empresa'], ctx['proy_marca'] = c15.text_input("Desc Proyecto",key=f"{p}15"), c16.text_input("Empresa",key=f"{p}16"), c17.text_input("Marca",key=f"{p}17")
        c18,c19,c20 = st.columns(3)
        ctx['proy_contacto'], ctx['proy_num_doc'], ctx['proy_estado'] = c18.text_input("Contacto Proy",key=f"{p}18"), c19.text_input("Num Doc Proy",key=f"{p}19"), c20.text_input("Estado Proy",key=f"{p}20")
        c21,c22,c23 = st.columns(3)
        ctx['proy_objetivo'], ctx['proy_alcance'], ctx['proy_indice'] = c21.text_input("Objetivo",key=f"{p}21"), c22.text_input("Alcance",key=f"{p}22"), c23.text_input("Índice",key=f"{p}23")
        ctx['proy_resumen'], ctx['proy_historia'] = st.text_area("Resumen",key=f"{p}24"), st.text_area("Historia",key=f"{p}25")
        c24,c25 = st.columns(2)
        ctx['proy_presupuesto'], ctx['proy_cond_pago'] = c24.text_input("Presupuesto",key=f"{p}26"), c25.text_input("Cond. Pago",key=f"{p}27")
        c26,c27,c28 = st.columns(3)
        ctx['proy_alcance_trab'], ctx['proy_campos'], ctx['proy_normas'] = c26.text_input("Alcance Trab",key=f"{p}28"), c27.text_input("Campos Téc",key=f"{p}29"), c28.text_input("Normas Apl",key=f"{p}30")
        c29,c30,c31 = st.columns(3)
        ctx['proy_riesgos'], ctx['proy_reqs'], ctx['proy_espec'] = c29.text_input("Riesgos",key=f"{p}31"), c30.text_input("Requisitos Proy",key=f"{p}32"), c31.text_input("Especificaciones",key=f"{p}33")
        c32,c33,c34 = st.columns(3)
        ctx['proy_param'], ctx['proy_proc'], ctx['proy_tonalidad'] = c32.text_input("Parámetros",key=f"{p}34"), c33.text_input("Procedimientos",key=f"{p}35"), c34.text_input("Tonalidad",key=f"{p}36")
        ctx['proy_cons'], ctx['proy_clausulas'] = st.text_area("Consentimiento",key=f"{p}37"), st.text_area("Cláusulas Legales Proy",key=f"{p}38")
        ctx['proy_formatos'], ctx['proy_crono'] = st.text_input("Formatos",key=f"{p}39"), st.text_area("Cronograma",key=f"{p}40")
        ctx['proy_desc_serv'], ctx['proy_garantias'] = st.text_area("Desc. Servicio",key=f"{p}41"), st.text_area("Garantías",key=f"{p}42")

    with st.expander("⚖️ 2. Trámites Registrales y Regionales (JI)", expanded=False):
        c1,c2,c3 = st.columns(3)
        ctx['tra_asunto'], ctx['tra_a'], ctx['tra_al'] = c1.text_input("Asunto",key=f"{p}43"), c2.text_input("A",key=f"{p}44"), c3.text_input("Al",key=f"{p}45")
        c4,c5,c6 = st.columns(3)
        ctx['tra_referencia'], ctx['tra_materia'], ctx['tra_demandante'] = c4.text_input("Ref. Legal",key=f"{p}46"), c5.text_input("Materia",key=f"{p}47"), c6.text_input("Demandante",key=f"{p}48")
        c7,c8,c9 = st.columns(3)
        ctx['tra_demandado'], ctx['tra_tribunal'], ctx['tra_organo'] = c7.text_input("Demandado",key=f"{p}49"), c8.text_input("Tribunal",key=f"{p}50"), c9.text_input("Órgano",key=f"{p}51")
        c10,c11,c12 = st.columns(3)
        ctx['tra_jurisdiccion'], ctx['tra_tipo'], ctx['tra_plazo'] = c10.text_input("Jurisdicción",key=f"{p}52"), c11.text_input("Tipo Trámite",key=f"{p}53"), c12.text_input("Plazo Resp.",key=f"{p}54")
        ctx['tra_fundamento'], ctx['tra_clausulas'] = st.text_area("Fundamento Legal",key=f"{p}55"), st.text_area("Cláusulas Trámite",key=f"{p}56")
        ctx['tra_terminos'], ctx['tra_pruebas'] = st.text_area("Términos",key=f"{p}57"), st.text_area("Pruebas",key=f"{p}58")
        c13,c14 = st.columns(2)
        ctx['tra_certificaciones'], ctx['tra_notificaciones'] = c13.text_input("Certificaciones",key=f"{p}59"), c14.text_input("Notificaciones",key=f"{p}60")
        
        st.caption("Direcciones Regionales JI")
        c15,c16,c17 = st.columns(3)
        ctx['ji_referencia'], ctx['ji_exp_regional'], ctx['ji_resolucion'] = c15.text_input("Ref JI",key=f"{p}61"), c16.text_input("Exp Regional",key=f"{p}62"), c17.text_input("Resolución/Acta",key=f"{p}63")
        c18,c19,c20 = st.columns(3)
        ctx['ji_fec_recepcion'], ctx['ji_registro'], ctx['ji_notificaciones'] = c18.text_input("Fec Recepción JI",key=f"{p}64"), c19.text_input("Reg Actuaciones",key=f"{p}65"), c20.text_input("Notif JI",key=f"{p}66")
        ctx['ji_requisitos'], ctx['ji_criterios'] = st.text_area("Requisitos Admin",key=f"{p}67"), st.text_area("Criterios Eval",key=f"{p}68")

    with st.expander("🛠️ 3. Creador de Casillas Personalizadas"):
        st.info("Agregue campos que no existan en el sistema. Escriba el nombre del campo sin espacios (ej. color_auto). En Word use {{ color_auto }}")
        c_p1, c_p2 = st.columns(2)
        nk = c_p1.text_input("Nombre de la Etiqueta (Word)", key=f"{p}ck")
        nv = c_p2.text_input("Valor a Inyectar", key=f"{p}cv")
        if st.button("➕ Añadir Campo Mágico", key=f"{p}cbtn"):
            if nk and nv: st.session_state.reg_custom.append({nk: nv}); st.rerun()
        for i, custom_f in enumerate(st.session_state.reg_custom):
            for k, v in custom_f.items(): st.write(f"✅ `{{{{ {k} }}}}` ➡️ **{v}**")
            if st.button("🗑️ Quitar", key=f"{p}d_{i}"): st.session_state.reg_custom.pop(i); st.rerun()
        for custom_dict in st.session_state.reg_custom: ctx.update(custom_dict)

    return ctx

# --- 3. VISTAS PRINCIPALES ---
def vista_mando():
    st.title(f"📊 Mando Central - {st.session_state.f_nom}")
    df = pd.DataFrame(db.consultar_todo())
    if df.empty: st.info("Sin expedientes."); return
    
    # Nuevos filtros añadidos
    c_f1, c_f2, c_f3 = st.columns(3)
    f_jur = c_f1.selectbox("Jurisdicción", ["Todas"] + list(JI_DATA.keys()))
    f_est = c_f2.selectbox("Etapa", ["Todas"] + ETAPAS_JI)
    f_mes = c_f3.selectbox("Mes de Apertura", ["Todos"] + list(df['fecha_apertura'].str[3:5].unique()) if 'fecha_apertura' in df.columns else ["Todos"])

    df_f = df.copy()
    if f_jur != "Todas": df_f = df_f[df_f['jurisdiccion'] == f_jur]
    if f_est != "Todas": df_f = df_f[df_f['estado'] == f_est]
    if f_mes != "Todas" and 'fecha_apertura' in df.columns: df_f = df_f[df_f['fecha_apertura'].str[3:5] == f_mes]
    
    if df_f.empty: st.warning("Sin datos."); return

    th, tp = df_f['monto'].sum(), df_f['pagado'].sum()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Proyectado", f"RD$ {th:,.2f}"); m2.metric("Cobrado", f"RD$ {tp:,.2f}"); m3.metric("Pendiente", f"RD$ {th-tp:,.2f}"); m4.metric("Casos", len(df_f))
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(px.bar(df_f, x='estado', y='monto', title="Por Etapa"), use_container_width=True)
    with c2: st.plotly_chart(px.pie(df_f, names='jurisdiccion', values='monto', title="Por Jurisdicción", color_discrete_sequence=px.colors.sequential.Blues), use_container_width=True)

def vista_registro():
    st.title("⚖️ Registro Maestro y Redacción")
    
    try:
        # Estas líneas deben estar alineadas perfectamente
        from database import obtener_diccionario_maestro, procesar_plantilla_maestra
        
        diccionario = obtener_diccionario_maestro()
        
        # Esta es la línea 154 que daba error; ahora está alineada
        t1, t2, t3, t4, t5 = st.tabs(["👤 1. Cliente", "🏗️ 2. Inmuebles", "🎓 3. Prof", "📑 4. Trámites", "🚀 5. Generar"])

        with t1:
            st.subheader("Datos del Cliente")
            cli_nom = st.text_input("Nombre Completo", key="c_nom_v")
            cli_ced = st.text_input("Cédula / Pasaporte", key="c_ced_v")
            
        with t2:
            st.subheader("Datos del Inmueble")
            ip = st.text_input("Parcela No.", key="i_parc_v")
            im = st.text_input("Matrícula No.", key="i_matr_v")

        with t5:
            st.header("🚀 Finalizar y Generar")
            
            # Bolsa de datos para el Word
            datos_finales = {
                "cliente_nombre": cli_nom,
                "cedula": cli_ced,
                "parcela": ip,
                "matricula": im,
                "jhonny_matos_titulos": "Lic. Jhonny Matos. M.A., Presidente"
            }
            
            if st.button("Generar Cuota Litis", type="primary"):
                resultado = procesar_plantilla_maestra(datos_finales, "CUOTA_LITIS.docx")
                if "Error" in resultado:
                    st.error(f"Aviso: {resultado}")
                else:
                    st.success(f"✅ Documento guardado en: {resultado}")

    except Exception as e:
        st.error(f"Error de visualización: {e}")
# --- 1. CREAMOS EL MENÚ LATERAL (Para que la variable 'menu' exista) ---
menu = st.sidebar.radio("Navegación", ["🏠 Mando", "👤 Registro Maestro", "⚙ Configuración"])
import streamlit as st

def vista_configuracion():
    st.title("⚙️ Configuración del Sistema")
    st.info("Módulo de configuración en mantenimiento tras la restauración.")
    # Aquí luego agregaremos tus ajustes de plantillas y base de datos
# --- 2. NAVEGACIÓN DEL SISTEMA ---
if menu == "Mando":
    vista_mando()
elif menu == "Registro Maestro":
    vista_registro_maestro()
elif menu == "Configuración":
    vista_configuracion()
