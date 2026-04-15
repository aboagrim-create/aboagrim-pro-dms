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
        t1, t2, t3, t4, t5 = st.tabs(["👤 1. Cliente", "🏗️ 2. Inmuebles/Apo", "🎓 3. Prof", "📄 4. Trámites/Metadatos", "🚀 5. Generar"])
        with t1:
            c1,c2,c3 = st.columns(3)
            cli_nom, cli_ced, cli_nac = c1.text_input("Nombre",key="cno"), c2.text_input("Cédula/RNC",key="cce"), c3.text_input("Nacionalidad",value="Dominicana",key="cna")
            c4,c5,c6 = st.columns(3)
            cli_eci, cli_con, cli_dom = c4.selectbox("Estado Civil",["Soltero/a","Casado/a","Divorciado/a","Unión Libre"],key="cec"), c5.text_input("Cónyuge",key="cco"), c6.text_input("Domicilio",key="cdo")
            c7,c8 = st.columns(2)
            cli_tel, cli_eml = c7.text_input("Teléfono",key="cte"), c8.text_input("Email",key="cem")
            fir_cli = st.text_input("Firma Cliente",key="fcli")

        with t2:
            with st.expander("➕ Añadir Inmueble", expanded=True):
                i1,i2,i3,i4 = st.columns(4)
                ip, idc, isup, imat = i1.text_input("Parcela",key="ip"), i2.text_input("DC",key="idc"), i3.text_input("Superficie",key="isu"), i4.text_input("Matrícula",key="ima")
                i5,i6,i7,i8 = st.columns(4)
                idp, idi, inr, isu = i5.text_input("Desig Pos",key="idp"), i6.text_input("Dirección",key="idi"), i7.text_input("Norte",key="in"), i8.text_input("Sur",key="is")
                i9,i10,i11,i12 = st.columns(4)
                ies, ioe, ias, iti = i9.text_input("Este",key="ie"), i10.text_input("Oeste",key="io"), i11.text_input("Asiento",key="ias"), i12.text_input("Título",key="iti")
                i13,i14,i15,i16 = st.columns(4)
                ico, ifi, ife, irf = i13.text_input("Coordenadas",key="ico"), i14.text_input("Fec Ins",key="ifi"), i15.text_input("Fec Emi",key="ife"), i16.text_input("Ref",key="irf")
                i17,i18 = st.columns(2)
                ili, ifo = i17.text_input("Libro",key="ili"), i18.text_input("Folio",key="ifo")
                if st.button("💾 Inmueble"): st.session_state.reg_inm.append({'inm_parcela':ip,'inm_dc':idc,'inm_superficie':isup,'inm_matricula':imat,'inm_desig_catastral':idp,'inm_direccion':idi,'inm_norte':inr,'inm_sur':isu,'inm_este':ies,'inm_oeste':ioe,'inm_asiento':ias,'inm_titulo':iti,'inm_coordenadas':ico,'inm_fec_inscripcion':ifi,'inm_fec_emision':ife,'inm_referencias':irf,'inm_libro':ili,'inm_folio':ifo})
            for x, it in enumerate(st.session_state.reg_inm):
                st.info(f"Parcela: {it['inm_parcela']}"); 
                if st.button(f"🗑️ Quitar Inm {x}", key=f"q_i{x}"): st.session_state.reg_inm.pop(x); st.rerun()

            with st.expander("➕ Añadir Apoderado"):
                a1,a2,a3 = st.columns(3)
                pno, pce, pti = a1.text_input("Nombre Apo",key="pno"), a2.text_input("Cédula",key="pce"), a3.text_input("Poder",key="pti")
                a4,a5,a6 = st.columns(3)
                pin, pnt, pal = a4.selectbox("Inscrito",["Sí","No"],key="pin"), a5.text_input("Notaría",key="pnt"), a6.text_input("Alcance",key="pal")
                a7,a8,a9 = st.columns(3)
                pdu, pis, pli = a7.text_input("Vigencia",key="pdu"), a8.text_input("Inst.",key="pis"), a9.text_input("Libro",key="pli")
                a10,a11,a12 = st.columns(3)
                pfo, fap, fre = a10.text_input("Folio",key="pfo"), a11.text_input("Firma Apo",key="fap"), a12.text_input("Firma Rep",key="fre")
                if st.button("💾 Apoderado"): st.session_state.reg_apo.append({'pod_nombre':pno,'pod_cedula':pce,'pod_tipo':pti,'pod_inscrito':pin,'pod_notaria':pnt,'pod_alcance':pal,'pod_duracion':pdu,'pod_institucion':pis,'pod_libro':pli,'pod_folio':pfo,'fir_apoderado':fap,'fir_representante':fre})
            for x, ap in enumerate(st.session_state.reg_apo):
                st.info(f"Apo: {ap['pod_nombre']}"); 
                if st.button(f"🗑️ Quitar Apo {x}", key=f"q_a{x}"): st.session_state.reg_apo.pop(x); st.rerun()

        with t3:
            with st.expander("➕ Agrimensores y Abogados", expanded=True):
                g1,g2,g3 = st.columns(3)
                gn, gc, gt = g1.text_input("Nom Agr",key="gn"), g2.text_input("Codia",key="gc"), g3.text_input("Mensura",key="gt")
                g4,g5,g6 = st.columns(3)
                gd, gco, gte = g4.text_input("Dir",key="gd"), g5.text_input("Correo",key="gco"), g6.text_input("Tel",key="gte")
                gf = st.text_input("Firma Agr",key="gf")
                if st.button("💾 Agrimensor"): st.session_state.reg_agrim.append({'agr_nombre':gn,'agr_codia':gc,'agr_tipo_mensura':gt,'agr_direccion':gd,'agr_correo':gco,'agr_telefono':gte,'agr_firma':gf})
                for x, ag in enumerate(st.session_state.reg_agrim): st.info(f"Agr: {ag['agr_nombre']}"); 
                
                abn, abc = st.columns(2)
                bn, bc = abn.text_input("Nom Abogado",key="bn"), abc.text_input("CARD",key="bc")
                if st.button("💾 Abogado"): st.session_state.reg_abog.append({'abog_nombre':bn,'abog_card':bc})
                for x, ab in enumerate(st.session_state.reg_abog): st.info(f"Abog: {ab['abog_nombre']}")

        with t4:
            j1, j2, j3 = st.columns(3)
            juris = j1.selectbox("Jurisdicción", list(JI_DATA.keys()))
            tram = j2.selectbox("Trámite", list(JI_DATA[juris].keys()))
            mon = j3.number_input("Honorarios RD$", 0.0)
            ctx_meta = form_estatico("reg")

        with t5:
            pls = db.consultar_plantillas()
            sp = [p['id'] for p in pls if st.checkbox(f"📄 {p['nombre_mostrar']}", key=f"chk_{p['id']}")] if pls else []
            if st.button("🚀 GUARDAR Y EMPAQUETAR", use_container_width=True):
                if cli_nom:
                    db.guardar_expediente_elite({'n':cli_nom,'c':cli_ced,'t':cli_tel,'m':mon,'pg':0,'act':tram,'f':datetime.now().strftime("%d/%m/%Y"),'area':0,'ref':ctx_meta.get('doc_expediente',''),'req':"",'jur':juris,'inm':json.dumps(st.session_state.reg_inm),'apo':json.dumps(st.session_state.reg_apo),'prof':json.dumps({"abogados":st.session_state.reg_abog,"agrimensores":st.session_state.reg_agrim})})
                    n_e = db.consultar_todo()[0]
                    if sp:
                        ctx = {'cli_nombre':cli_nom,'cli_cedula':cli_ced,'cli_nacionalidad':cli_nac,'cli_ecivil':cli_eci,'cli_conyuge':cli_con,'cli_domicilio':cli_dom,'cli_telefono':cli_tel,'cli_email':cli_eml,'fir_cliente':fir_cli,'hoy':datetime.now().strftime("%d/%m/%Y")}
                        if st.session_state.reg_inm: ctx.update(st.session_state.reg_inm[0])
                        if st.session_state.reg_apo: ctx.update(st.session_state.reg_apo[0])
                        if st.session_state.reg_agrim: ctx.update(st.session_state.reg_agrim[0])
                        if st.session_state.reg_abog: ctx['tra_abogado'] = st.session_state.reg_abog[0].get('abog_nombre','')
                        ctx.update(ctx_meta)
                        ctx.update({'NOMBRE':cli_nom,'CEDULA':cli_ced,'RNC':cli_ced,'FECHA':ctx.get('doc_fecha',ctx['hoy']),'EXPEDIENTE':ctx.get('doc_expediente',''),'MATRICULA':ctx.get('inm_matricula',''),'COORDENADAS':ctx.get('inm_coordenadas',''),'SUPERFICIE':ctx.get('inm_superficie',''),'APODERADO':ctx.get('pod_nombre',''),'AGRIMENSOR':ctx.get('agr_nombre',''),'ABOGADO':ctx.get('tra_abogado',''),'FIRMA':ctx.get('doc_firma_sol',''),'SELLO':"Sello"})
                        rc = []
                        for pid in sp:
                            p = next((x for x in pls if x['id']==pid),None)
                            if p:
                                try:
                                    doc = DocxTemplate(os.path.join(db.PLANTILLAS_DIR, p['archivo_word'])); doc.render(ctx)
                                    rs = os.path.join(n_e['ruta_carpeta'], p['carpeta_destino_sugerida']); os.makedirs(rs, exist_ok=True)
                                    rf = os.path.join(rs, f"{p['nombre_mostrar']}_{cli_nom}.docx"); doc.save(rf); rc.append(rf)
                                except Exception as e: st.error(f"Err {p['nombre_mostrar']}: {e}")
                        if rc:
                            zb = io.BytesIO()
                            with zipfile.ZipFile(zb,"w") as zf:
                                for r in rc: zf.write(r, os.path.basename(r))
                            st.session_state.zip_reg, st.session_state.zip_reg_name = zb.getvalue(), f"Exp_{cli_nom}.zip"
                            st.success("✅ Generado."); st.balloons()
                    for k in ['reg_inm','reg_apo','reg_abog','reg_agrim','reg_custom']: st.session_state[k] = []
                else: st.error("Falta Nombre.")
            if st.session_state.zip_reg: st.download_button("📥 DESCARGAR ZIP", st.session_state.zip_reg, st.session_state.zip_reg_name, "application/zip")
    except Exception as e: st.error(f"Error: {e}")

def vista_archivo():
    st.title("📂 Archivo Digital Maestro")
    for e in db.consultar_todo(st.text_input("🔍 Buscar...")):
        with st.expander(f"📁 {e['cliente_nombre']} | Etapa: {e['estado']}"):
            c1,c2,c3,c4 = st.columns([2,1,1,1])
            c1.write(f"`{e['ruta_carpeta']}`")
            
            # BOTON WHATSAPP AÑADIDO AQUI
            tel_clean = ''.join(filter(str.isdigit, str(e.get('telefono',''))))
            if tel_clean: c2.markdown(f"<a href='https://wa.me/{tel_clean}' target='_blank'><button style='background-color:#25D366;color:white;border:none;padding:5px 10px;border-radius:5px;'>💬 WhatsApp</button></a>", unsafe_allow_html=True)
            
            if c3.button("✏️ Etapa",key=f"e_{e['id']}"): modal_editar_estado(e)
            if c4.button("🗑️ Borrar",key=f"d_{e['id']}"): db.borrar_expediente(e['id']); st.rerun()
            
            ar = st.file_uploader("Documento:", key=f"u_{e['id']}")
            if ar: 
                with open(os.path.join(e['ruta_carpeta'], "1_Identidad", ar.name), "wb") as f: f.write(ar.getbuffer())
                st.success("Guardado.")

def vista_plantillas():
    st.title("📄 Gestor de Plantillas Cloud")
    tab1, tab2 = st.tabs(["⚙️ Generar Documentos", "☁️ Subir Nueva Plantilla"])

    with tab1:
        pls = db.consultar_plantillas()
        exps = db.consultar_todo()
        
        if exps and pls:
            sel = st.selectbox("Seleccione Cliente", [e['id'] for e in exps], format_func=lambda x: next((f"{e['cliente_nombre']}" for e in exps if e['id']==x), ""))
            cd = db.obtener_por_id(sel)
            
            st.write("Seleccione las plantillas a redactar:")
            nu = [p['id'] for p in pls if st.checkbox(f"Gen: {p['nombre_mostrar']}", key=f"n_{p['id']}")]
            st.divider()
            
            cxm = form_estatico("ela")
            
            if st.button("🚀 REDACTAR ZIP"):
                import io, zipfile, os, json
                from docxtpl import DocxTemplate
                from datetime import datetime
                
                ctx = {'cli_nombre': cd['cliente_nombre'], 'cli_cedula': cd['cedula_rnc'], 'hoy': datetime.now().strftime("%d/%m/%Y")}
                im = json.loads(cd.get('inmuebles_json') or "[]")
                ap = json.loads(cd.get('apoderados_json') or "[]")
                if im: ctx.update(im[0])
                if ap: ctx.update(ap[0])
                if cxm: ctx.update(cxm)
                
                ctx.update({'NOMBRE': ctx['cli_nombre'], 'CEDULA': ctx['cli_cedula'], 'RNC': ctx['cli_cedula'], 'FECHA': ctx.get('doc_fecha', ctx['hoy']), 'EXPEDIENTE': ctx.get('doc_expediente', '')})
                
                zb = io.BytesIO()
                with zipfile.ZipFile(zb, "w") as zf:
                    for pid in nu:
                        p = next((x for x in pls if x['id']==pid), None)
                        if p:
                            try:
                                ruta = os.path.join(db.PLANTILLAS_DIR, p['archivo_word'])
                                doc = DocxTemplate(ruta)
                                doc.render(ctx)
                                
                                # Magia Cloud: Guardar en memoria en vez de en disco duro
                                temp_io = io.BytesIO()
                                doc.save(temp_io)
                                temp_io.seek(0)
                                
                                nombre_archivo = f"{p['nombre_mostrar']}_{cd['cliente_nombre']}.docx"
                                zf.writestr(nombre_archivo, temp_io.read())
                            except Exception as e:
                                st.error(f"Error en {p['nombre_mostrar']}: Revise que el archivo Word base exista.")
                                
                st.session_state.zip_elab = zb.getvalue()
                st.session_state.zip_elab_name = f"Docs_{cd['cliente_nombre']}.zip"
                st.success("✅ Completado.")
                st.balloons()
                
        if 'zip_elab' in st.session_state:
            st.download_button("📥 DESCARGAR DOCUMENTOS", st.session_state.zip_elab, st.session_state.zip_elab_name, "application/zip")

    with tab2:
        st.write("### Añadir Plantilla a la Base de Datos")
        archivo_subido = st.file_uploader("1. Seleccione su archivo Word (.docx)", type=["docx"])
        nombre_mostrar = st.text_input("2. ¿Con qué nombre quiere verla en el sistema? (Ej: Contrato de Litis)")
        
        if st.button("💾 Guardar Plantilla en la Nube"):
            if archivo_subido and nombre_mostrar:
                import os
                os.makedirs(db.PLANTILLAS_DIR, exist_ok=True)
                ruta_guardado = os.path.join(db.PLANTILLAS_DIR, archivo_subido.name)
                
                with open(ruta_guardado, "wb") as f:
                    f.write(archivo_subido.getbuffer())
                    
                db.supabase.table("plantillas").insert({
                    "nombre_mostrar": nombre_mostrar,
                    "archivo_word": archivo_subido.name,
                    "carpeta_destino_sugerida": "General"
                }).execute()
                
                st.success("✅ Plantilla registrada con éxito.")
                st.rerun()
            else:
                st.warning("⚠️ Debe subir un archivo y ponerle un nombre para guardar.")
def vista_alertas():
    st.title("📅 Alertas y Plazos Jurídicos")
    t1, t2 = st.tabs(["🚨 Vencimientos", "➕ Nueva Alerta"])
    with t1:
        als = db.consultar_alertas(solo_pendientes=True)
        if not als: st.success("Sin alertas.")
        for a in als:
            c1, c2 = st.columns([4,1])
            c1.write(f"**{a['cliente_nombre']}** | {a['tipo_alerta']} | Vence: {a['fecha_vencimiento']}\n_{a['descripcion']}_")
            if c2.button("✅ Ok", key=f"ok_{a['id']}"): db.upsert_alerta(a['id'], a['expediente_id'], a['tipo_alerta'], a['fecha_vencimiento'], a['descripcion'], "Completada"); st.rerun()
    with t2:
        exps = db.consultar_todo()
        if exps:
            with st.form("fa"):
                sel = st.selectbox("Expediente", [e['id'] for e in exps], format_func=lambda x: next(e['cliente_nombre'] for e in exps if e['id']==x))
                tip = st.selectbox("Tipo / Norma Legal", ALERTAS_LEGALES)
                fec = st.date_input("Fecha de Vencimiento")
                des = st.text_area("Base legal y descripción del plazo")
                if st.form_submit_button("Guardar"): db.upsert_alerta(None, sel, tip, str(fec), des); st.rerun()

def generar_html_factura(f):
    pagos = json.loads(f.get('historial_pagos') or '[]')
    filas_pagos = "".join([f"<tr><td style='padding:8px; border:1px solid #ccc;'>{p['fecha']}</td><td style='padding:8px; border:1px solid #ccc;'>{p['etapa']}</td><td style='padding:8px; border:1px solid #ccc;'>{p['forma']}</td><td style='padding:8px; border:1px solid #ccc;'>RD$ {p['monto']:,.2f}</td></tr>" for p in pagos])
    if not pagos: filas_pagos = "<tr><td colspan='4' style='padding:8px; border:1px solid #ccc; text-align:center;'>No se han registrado abonos</td></tr>"
    html = f"""<html><head><meta charset="utf-8"></head><body style="font-family: Arial, sans-serif; color: #333; padding: 40px; max-width: 800px; margin: auto;"><div style="text-align: center; border-bottom: 3px solid {st.session_state.f_color}; padding-bottom: 15px; margin-bottom: 30px;"><h1 style="color: {st.session_state.f_color}; margin: 0; font-size: 36px; letter-spacing: 2px;">ABOAGRIM</h1><h3 style="color: #475569; margin: 5px 0; font-size: 16px; letter-spacing: 1px;">ABOGADOS Y AGRIMENSORES</h3><p style="margin: 5px 0; font-size: 16px; font-weight: bold;">{st.session_state.f_nom}</p><p style="margin: 2px 0; font-size: 14px; color: #64748b;">{st.session_state.f_dir}</p></div><div style="display: flex; justify-content: space-between; margin-bottom: 30px;"><div><p><strong>Facturado a:</strong> {f.get('cliente_nombre', '')}</p><p><strong>Cédula/RNC:</strong> {f.get('cedula_rnc', '')}</p></div><div style="text-align: right;"><p><strong>Factura #:</strong> {f['id']:04d}</p><p><strong>Fecha Emisión:</strong> {f['fecha_emision']}</p><p style="font-size: 18px; color: {'#16a34a' if f['estado']=='Pagada' else '#dc2626'};"><strong>ESTADO: {f['estado'].upper()}</strong></p></div></div><table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;"><tr style="background-color: {st.session_state.f_color}; color: white;"><th style="padding: 12px; text-align: left;">Concepto</th><th style="padding: 12px; text-align: right;">Importe</th></tr><tr><td style="padding: 12px; border: 1px solid #ccc;">{f['concepto']}</td><td style="padding: 12px; border: 1px solid #ccc; text-align: right;">RD$ {f['subtotal']:,.2f}</td></tr></table><div style="text-align: right; font-size: 16px; margin-bottom: 30px;"><p><strong>Subtotal:</strong> RD$ {f['subtotal']:,.2f}</p><p><strong>ITBIS (18%):</strong> RD$ {f['itbis']:,.2f}</p><p><strong>Descuento:</strong> RD$ {f.get('descuento',0):,.2f}</p><p style="font-size: 20px; color: {st.session_state.f_color};"><strong>TOTAL A PAGAR: RD$ {f['total']:,.2f}</strong></p><p style="font-size: 12px;">Condición de pago: {f.get('terminos','Al Contado')}</p></div><h3 style="color: {st.session_state.f_color}; border-bottom: 1px solid #ccc; padding-bottom: 5px;">Historial de Abonos</h3><table style="width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 14px;"><tr style="background-color: #f1f5f9;"><th style="padding: 8px; text-align: left; border: 1px solid #ccc;">Fecha</th><th style="padding: 8px; text-align: left; border: 1px solid #ccc;">Etapa</th><th style="padding: 8px; text-align: left; border: 1px solid #ccc;">Forma de Pago</th><th style="padding: 8px; text-align: left; border: 1px solid #ccc;">Monto Depositado</th></tr>{filas_pagos}</table><div style="text-align: right; font-size: 16px;"><p><strong>Total Abonado:</strong> RD$ {float(f.get('monto_pagado') or 0.0):,.2f}</p><p style="font-size: 18px; color: #dc2626;"><strong>BALANCE PENDIENTE: RD$ {f['total'] - float(f.get('monto_pagado') or 0.0):,.2f}</strong></p></div></body></html>"""
    return html

def vista_facturacion():
    st.title("💳 Facturación Avanzada")
    t1, t2 = st.tabs(["🧾 Emitir", "🗃️ Historial"])
    exps = db.consultar_todo()
    with t1:
        if exps:
            with st.form("f_f"):
                sel = st.selectbox("Cliente", [e['id'] for e in exps], format_func=lambda x: next(e['cliente_nombre'] for e in exps if e['id']==x))
                c1,c2,c3 = st.columns(3)
                ncf, fec, ven = c1.text_input("NCF"), c2.date_input("Emisión"), c3.date_input("Vence NCF")
                con = st.text_input("Concepto", "Honorarios profesionales")
                c4,c5,c6 = st.columns(3)
                sub, desc = c4.number_input("Subtotal", 0.0), c5.number_input("Descuento RD$", 0.0)
                itb = c6.checkbox("Aplicar 18% ITBIS")
                term = st.selectbox("Términos de Pago", ["Al Contado", "15 Días", "30 Días", "50% Avance, 50% Final"])
                if st.form_submit_button("Emitir"): 
                    sub_f = sub - desc; itb_v = sub_f * 0.18 if itb else 0
                    # Para simplificar la base, usamos dict en notas para guardar términos y descuentos
                    db.upsert_factura(None, sel, ncf, str(fec), con, sub_f, itb_v, sub_f+itb_v, "Pendiente")
                    st.rerun()
    with t2:
        for f in db.consultar_facturas():
            c1, c2, c3 = st.columns([3,2,2])
            c1.write(f"Fac #{f['id']} - Total: {f['total']:,.2f} | {f['estado']}")
            if c2.button("Abonar", key=f"ab_{f['id']}"): modal_abonar(f)
            c3.download_button("📥 Descargar", generar_html_factura(f), f"Fac_{f['id']}.html", "text/html", key=f"dl_{f['id']}")

def vista_configuracion():
    st.title("⚙️ Configuración y Seguridad")
    t1, t2, t3 = st.tabs(["🎨 Personalización", "🔒 Seguridad", "🛡️ Backup"])
    with t1:
        st.session_state.f_nom = st.text_input("Nombre de la Firma", st.session_state.f_nom)
        st.session_state.f_dir = st.text_input("Sede Principal", st.session_state.f_dir)
        st.session_state.f_color = st.color_picker("Color de Facturas y Botones", st.session_state.f_color)
        if st.button("💾 Guardar Diseño"): st.success("Aplicado.")
    with t2:
        st.write("#### Proteger Módulos con Contraseña")
        mod = st.selectbox("Seleccione Módulo a proteger", ["💳 Facturación", "⚙️ Configuración", "📂 Archivo"])
        pw = st.text_input("Nueva Contraseña", type="password")
        if st.button("🔒 Asignar Contraseña"): 
            st.session_state.passwords[mod] = pw
            if mod in st.session_state.unlocked: st.session_state.unlocked.remove(mod)
            st.success(f"Módulo {mod} protegido.")
    with t3:
        if st.button("🛡️ Crear Backup"): shutil.copy("aboagrim.db", f"backup_{time.time()}.db"); st.success("Ok.")

# --- RUTEO Y SEGURIDAD ---
st.sidebar.title("AboAgrim DMS")
menu = st.sidebar.radio("MENÚ", ["🏠 Mando", "👤 Registro Maestro", "📂 Archivo", "📄 Plantillas", "📅 Alertas", "💳 Facturación", "⚙️ Configuración"])

# Sistema de bloqueo por contraseña
if menu in st.session_state.passwords and menu not in st.session_state.unlocked:
    st.warning(f"🔒 El módulo {menu} está protegido.")
    pwd_input = st.text_input("Ingrese contraseña:", type="password")
    if st.button("Desbloquear"):
        if pwd_input == st.session_state.passwords[menu]:
            st.session_state.unlocked.append(menu); st.rerun()
        else: st.error("Contraseña incorrecta.")
else:
    if menu == "🏠 Mando": vista_mando()
    elif menu == "👤 Registro Maestro": vista_registro()
    elif menu == "📂 Archivo": vista_archivo()
    elif menu == "📄 Plantillas": vista_plantillas()
    elif menu == "📅 Alertas": vista_alertas()
    elif menu == "💳 Facturación": vista_facturacion()
    elif menu == "⚙️ Configuración": vista_configuracion()
