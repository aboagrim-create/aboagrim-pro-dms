# =====================================================================
# INTERFAZ GRÁFICA Y SISTEMA EXPERTO LEGAL JI (EDICIÓN PREMIUM FULL)
# Sistema: AboAgrim Pro DMS 
# =====================================================================

import streamlit as st
import pandas as pd
import datetime
import zipfile
import io
from docx import Document # Nueva librería para generar Word
from database import *

# --- CONFIGURACIÓN DE MARCA Y SISTEMA ---
st.set_page_config(page_title="AboAgrim Pro DMS", layout="wide", initial_sidebar_state="expanded")

# --- LÓGICA DE SEGURIDAD (LOGIN) ---
if 'autenticado' not in st.session_state: 
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><h2 style='text-align: center; color: #1E3A8A;'>⚖️ AboAgrim Pro DMS</h2>", unsafe_allow_html=True)
        with st.form("Login_Seguro"):
            u = st.text_input("Correo Institucional:").strip()
            p = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("Entrar al Sistema", use_container_width=True):
                exito, user = autenticar_usuario(u, p)
                if exito:
                    st.session_state['autenticado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else: st.error("❌ Credenciales incorrectas.")
    st.stop()

# --- INTERFAZ PRINCIPAL (BARRA LATERAL) ---
st.sidebar.markdown(f"### AboAgrim Pro\n**Lic. Jhonny Matos, M.A.**\n`Usuario: {st.session_state['user']}`")
st.sidebar.divider()
menu = st.sidebar.radio("Navegación", ["🏠 Mando Central", "👤 Registro Maestro", "📁 Archivo Digital", "📄 Plantillas Auto", "📅 Alertas y Plazos", "💳 Facturación", "⚙️ Configuración"])

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state['autenticado'] = False
    st.rerun()

# =====================================================================
# MÓDULOS 1 AL 3 (MANDO, REGISTRO Y ARCHIVO CON ZIP)
# =====================================================================
def vista_mando():
    st.markdown("<div style='background:linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); padding:30px; border-radius:12px; color:white; border-left:6px solid #FBBF24;'><h2>AboAgrim Pro DMS ⚖️📐</h2><p>Centro de Mando: Jurisdicción Inmobiliaria y Mensura</p></div><br>", unsafe_allow_html=True)
    casos = consultar_todo()
    if casos:
        df = pd.DataFrame(casos)
        c1, c2 = st.columns([2, 1])
        busq = c2.text_input("📝 Búsqueda libre:")
        df_f = df.copy()
        if busq: df_f = df_f[df_f.astype(str).apply(lambda x: x.str.contains(busq, case=False)).any(axis=1)]
        st.dataframe(df_f, use_container_width=True)
    else: st.info("Registre su primer expediente.")

def vista_registro_maestro():
    st.title("👤 Registro Maestro de Expedientes")
    dic = obtener_diccionario_maestro()
    with st.form("registro_expediente_full", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        num = c1.text_input("N° Expediente:")
        cli = c2.text_input("Cliente Principal:")
        tipo = c3.selectbox("Tipo de Acto:", ["Deslinde", "Saneamiento", "Litis", "Transferencia"])
        
        c4, c5 = st.columns(2)
        jur = c4.selectbox("Jurisdicción:", ["Santiago", "La Vega", "Santo Domingo", "Puerto Plata", "Moca"])
        eta = c5.selectbox("Etapa Inicial:", ["Recepción", "Mensura", "Sometimiento", "Tribunal", "Sentencia"])
        
        st.markdown("---")
        if st.form_submit_button("🛡️ Registrar Expediente"):
            if num and cli:
                datos = {"numero_expediente": num, "cliente_id": cli, "tipo_caso": tipo, "jurisdiccion": jur, "etapa": eta, "estado": "Abierto"}
                if registrar_evento("casos", datos): st.success("✅ Guardado en la nube.")
                else: st.error("Error al guardar.")
            else: st.warning("⚠️ N° Expediente y Cliente son obligatorios.")

def vista_archivo():
    st.title("📁 Bóveda Digital DMS")
    tab1, tab2 = st.tabs(["⬆️ Cargar Documentos", "🗄️ Explorador de Bóveda"])
    with tab1:
        exp = st.text_input("Vincular al Expediente N°:", key="up_exp")
        archivos = st.file_uploader("Arrastre archivos aquí:", accept_multiple_files=True)
        if st.button("⬆️ Subir a la Nube"):
            if exp and archivos:
                with st.spinner("Subiendo..."):
                    for arch in archivos:
                        subir_documento("expedientes", f"{exp.strip()}/{arch.name}", arch.read())
                    st.success("✅ Archivos guardados.")
    with tab2:
        exp_busq = st.text_input("Buscar N° de Expediente:", key="sc_exp")
        if st.button("🗂️ Buscar"):
            archivos_enc = listar_documentos("expedientes", exp_busq.strip())
            if archivos_enc:
                for arch in archivos_enc:
                    if arch.get('name') != '.emptyFolderPlaceholder':
                        url = obtener_url_descarga("expedientes", f"{exp_busq.strip()}/{arch.get('name')}")
                        st.markdown(f"📄 {arch.get('name')} - [⬇️ Descargar]({url})")
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for arch in archivos_enc:
                        if arch.get('name') != '.emptyFolderPlaceholder':
                            f_bytes = descargar_documento_bytes("expedientes", f"{exp_busq.strip()}/{arch.get('name')}")
                            if f_bytes: zip_file.writestr(arch.get('name'), f_bytes)
                st.download_button("📦 Descargar ZIP Completo", zip_buffer.getvalue(), f"Expediente_{exp_busq}.zip", "application/zip")

# =====================================================================
# MÓDULO 4: PLANTILLAS AUTO (NUEVO MOTOR WORD)
# =====================================================================
def vista_plantillas():
    st.title("📄 Motor de Redacción Legal (Word)")
    st.info("Genera documentos en formato .docx listos para imprimir y firmar.")
    
    casos = consultar_todo()
if not casos:
        st.warning("Debe registrar al menos un expediente en el sistema.")
        return
        
    lista_exps = [f"{c.get('numero_expediente')} - {c.get('cliente_id')}" for c in casos]
    exp_seleccionado = st.selectbox("Seleccione el Expediente:", lista_exps)
    tipo_doc = st.selectbox("Seleccione el Documento a Generar:", ["Contrato de Prestación de Servicios y Cuota Litis", "Instancia Introductiva (Genérica)"])
    
    if st.button("⚙️ Generar Documento Word"):
        with st.spinner("Ensamblando documento legal..."):
            # Creamos un Word en blanco en la memoria
            doc = Document()
            
            # Extraemos los datos del texto seleccionado
            num_exp = exp_seleccionado.split(" - ")[0]
            cliente = exp_seleccionado.split(" - ")[1]
            
            # Redacción Automática
            doc.add_heading(f'{tipo_doc.upper()}', 0)
            doc.add_paragraph(f"Expediente Vinculado: {num_exp}")
            doc.add_paragraph(f"Fecha: {datetime.datetime.now().strftime('%d de %B del %Y')}")
            doc.add_paragraph("\nENTRE LAS PARTES:")
            doc.add_paragraph(f"De una parte, el Lic. JHONNY MATOS, M.A., Abogado/Agrimensor...")
            doc.add_paragraph(f"Y de la otra parte, el señor(a) {cliente}, quien en lo adelante se denominará EL CLIENTE.")
            doc.add_paragraph("\nSE HA CONVENIDO Y PACTADO LO SIGUIENTE:")
            doc.add_paragraph("PRIMERO: EL CLIENTE apodera a la firma AboAgrim para realizar los trabajos legales y técnicos correspondientes al caso.")
            
            # Lo guardamos en bytes para la descarga
            word_buffer = io.BytesIO()
            doc.save(word_buffer)
            word_buffer.seek(0)
            
            st.success("✅ Documento generado con éxito.")
            st.download_button(
                label="⬇️ Descargar Archivo de Word",
                data=word_buffer,
                file_name=f"{tipo_doc}_{num_exp}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

# =====================================================================
# MÓDULOS 5 AL 7 (ALERTAS, FACTURACIÓN NUEVA Y CONFIGURACIÓN)
# =====================================================================
def vista_alertas():
    st.title("📅 Alertas y Plazos Legales")
    st.info("Módulo en desarrollo: Próximamente se vinculará con las fechas de la Ley 108-05.")

def vista_facturacion():
    st.title("💳 Finanzas y Control de Honorarios")
    
    # Formulario de Ingresos
    with st.form("form_pagos", clear_on_submit=True):
        st.subheader("Registrar un Nuevo Pago / Abono")
        c1, c2, c3 = st.columns(3)
        exp = c1.text_input("Expediente N°:")
        tot = c2.number_input("Honorarios Acordados (RD$):", min_value=0.0, step=1000.0)
        abo = c3.number_input("Monto Abonado Hoy (RD$):", min_value=0.0, step=1000.0)
        
        if st.form_submit_button("💳 Registrar Ingreso"):
            if exp and abo > 0:
                datos_pago = {
                    "expediente_id": exp, "honorarios_totales": tot, 
                    "monto_pagado": abo, "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d")
                }
                if registrar_evento("pagos", datos_pago): st.success(f"✅ Pago de RD$ {abo:,.2f} registrado.")
                else: st.error("Error al registrar el pago.")
            else: st.warning("Ingrese Expediente y Monto.")
            
    st.divider()
    
    # Historial Financiero
    st.subheader("📊 Historial de Movimientos")
    facturas = consultar_facturas()
    if facturas:
        df_pagos = pd.DataFrame(facturas)
        df_pagos['Balance Pendiente'] = pd.to_numeric(df_pagos['honorarios_totales']) - pd.to_numeric(df_pagos['monto_pagado'])
        st.dataframe(df_pagos[['fecha_registro', 'expediente_id', 'honorarios_totales', 'monto_pagado', 'Balance Pendiente']], use_container_width=True)
        
        # Métrica Total
        total_ingresos = pd.to_numeric(df_pagos['monto_pagado']).sum()
        st.metric("Total Ingresos Históricos (RD$)", f"RD$ {total_ingresos:,.2f}")
    else:
        st.info("No hay pagos registrados aún.")

def vista_configuracion():
    st.title("⚙️ Ajustes del Sistema")
    st.markdown("**Sede Principal:** Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Santiago.")

# --- ENRUTADOR ---
vistas = {
    "🏠 Mando Central": vista_mando, "👤 Registro Maestro": vista_registro_maestro, 
    "📁 Archivo Digital": vista_archivo, "📄 Plantillas Auto": vista_plantillas, 
    "📅 Alertas y Plazos": vista_alertas, "💳 Facturación": vista_facturacion, 
    "⚙️ Configuración": vista_configuracion
}
vistas[menu]()
