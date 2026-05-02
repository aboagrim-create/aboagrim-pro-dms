# =====================================================================
# INTERFAZ GRÁFICA Y SISTEMA EXPERTO LEGAL JI (EDICIÓN PREMIUM FULL)
# Sistema: AboAgrim Pro DMS 
# =====================================================================
from database import db as supabase
import streamlit as st
import zipfile
import os
import shutil
import io
import json
from datetime import datetime, timedelta
from docxtpl import DocxTemplate
# from fpdf import FPDF  <-- Agréguela aquí si usa la parte de facturación
# --- OCULTAR ICONOS Y MENÚ DE STREAMLIT PARA UN DISEÑO LIMPIO ---
ocultar_iconos = """
    <style>
    /* Oculta las herramientas de programador (Deploy, GitHub), pero mantiene el menú ☰ del celular */
    [data-testid="stToolbar"] {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    </style>
    """
st.markdown(ocultar_iconos, unsafe_allow_html=True)
# === DATOS MAESTROS DE LA FIRMA ABOAGRIM ===
PRESIDENTE_FIRMA = "Lic. Jhonny Matos, M.A."
DIRECCION_FIRMA = "Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Centro Ciudad, Santiago."
TELEFONOS_FIRMA = "829-826-5888 / 809-691-3333"
CORREO_FIRMA = "aboagrim@gmail.com"
# --- INICIALIZACIÓN DE MEMORIA DEL SISTEMA ---
if "bandeja_descargas" not in st.session_state:
    st.session_state["bandeja_descargas"] = []
    
if "plantillas_cargadas" not in st.session_state:
    st.session_state["plantillas_cargadas"] = []

# --- MOTOR DE GENERACIÓN DE DOCUMENTOS WORD ---
def generar_documento_word(ruta_plantilla, diccionario_datos):
    """
    Toma una plantilla .docx y la llena con los datos del diccionario.
    """
    try:
        doc = DocxTemplate(ruta_plantilla)
        
        # Agregamos metadatos de la firma automáticamente
        diccionario_datos.update({
            "firma_nombre": PRESIDENTE_FIRMA,
            "firma_direccion": DIRECCION_FIRMA,
            "firma_tel": TELEFONOS_FIRMA,
            "firma_correo": CORREO_FIRMA,
            "fecha_hoy": datetime.now().strftime("%d de %B de %Y")
        })
        
        doc.render(diccionario_datos)
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"❌ Error en la forja del documento: {e}")
        return None


# ==========================================
# 👔 ESTILO VISUAL PROFESIONAL (CSS)
# ==========================================
st.markdown("""
    <style>
    /* Fondo principal elegante (Gris oscuro/Azul noche) */
    .stApp {
        background-color: #0b0f19;
    }
    
    /* Contenedores y formularios con borde sutil */
    div[data-testid="stForm"], div[data-testid="stContainer"] {
        background-color: #131a2a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Títulos con el color institucional */
    h1, h2, h3 {
        color: #e2e8f0;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Botones ejecutivos */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        border: 1px solid #334155;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        border-color: #d4af37; /* Toque dorado elegante al pasar el ratón */
        color: #d4af37;
    }
    </style>
""", unsafe_allow_html=True)
# ==========================================
# MOTOR DE GENERACIÓN DE DOCUMENTOS WORD
# ==========================================
from docxtpl import DocxTemplate
import io


# --- CONEXIÓN A SUPABASE (CEREBRO DIGITAL) ---
url_supabase = "https://wqcpbxrltttfnusdrawq.supabase.co"
clave_supabase = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndxY3BieHJsdHR0Zm51c2RyYXdxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYyMTI2NjEsImV4cCI6MjA5MTc4ODY2MX0.uD7v_-rY0b4dJGRSeF1mtDeftNzopFNnyyx7IEhPKPs"

try:
    supabase: Client = create_client(url_supabase, clave_supabase)
except Exception as e:
    pass

from google.oauth2 import service_account
from googleapiclient.discovery import build

def crear_oficina_virtual(nombre_cliente, id_expediente, id_maestra):
    try:
        # Cargamos los secretos que pegamos en Streamlit
        info_llave = st.secrets["google_drive"]
        creds = service_account.Credentials.from_service_account_info(info_llave)
        drive_service = build('drive', 'v3', credentials=creds)

        nombre_carpeta = f"EXP-{id_expediente} | {nombre_cliente}"

        # 1. Crear Carpeta Principal
        meta_principal = {
            'name': nombre_carpeta,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [id_maestra]
        }
        archivo = drive_service.files().create(body=meta_principal, fields='id, webViewLink').execute()
        folder_id = archivo.get('id')
        link_web = archivo.get('webViewLink')

        # 2. Crear las 3 Subcarpetas (Orden Diamante)
        subcarpetas = ["01_DOCUMENTOS_LEGALES", "02_PLANOS_Y_TECNICO", "03_RECIBOS_Y_PAGOS"]
        for sub in subcarpetas:
            meta_sub = {'name': sub, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [folder_id]}
            drive_service.files().create(body=meta_sub).execute()

        return link_web
    except Exception as e:
        st.error(f"Error en Drive: {e}")
        return None
def generar_paquete_documentos(datos_formulario, rutas_plantillas):
    import io
    
    # 1. El Mega Diccionario (Atrapa todo lo de la pantalla)
    contexto = dict(datos_formulario)
    contexto['profesional'] = "Lic. Jhonny Matos. M.A."
    contexto['cargo'] = "Presidente fundador AboAgrim"
    
    # 2. Si solo es un archivo, lo procesamos normal
    if len(rutas_plantillas) == 1:
        doc = DocxTemplate(rutas_plantillas[0])
        doc.render(contexto)
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer, f"Expediente_{contexto.get('nom_prop', 'AboAgrim')}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    # 3. Si son VARIOS archivos, creamos un archivo .ZIP con todos adentro
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for ruta in rutas_plantillas:
            doc = DocxTemplate(ruta)
            doc.render(contexto)
            
            temp_buffer = io.BytesIO()
            doc.save(temp_buffer)
            
            # Nombre del archivo procesado
            nombre_archivo = f"Listo_{os.path.basename(ruta)}"
            zip_file.writestr(nombre_archivo, temp_buffer.getvalue())
            
    zip_buffer.seek(0)
    return zip_buffer, f"Paquete_Expediente_{contexto.get('nom_prop', 'AboAgrim')}.zip", "application/zip"
# Asegúrese de que no haya nada repetido debajo de este bloque.
# =====================================================================
# MÓDULO 1: MANDO CENTRAL
# =====================================================================
def vista_mando():
    import os
    
    # --- 1. PRESENTACIÓN DE LA OFICINA (LOGO Y DATOS) ---
    col_logo, col_info = st.columns([1, 3])
    
    with col_logo:
        # Busca el logo que usted tiene en su carpeta
        if os.path.exists("logo_aboagrim.jpg"):
            st.image("logo_aboagrim.jpg", use_container_width=True)
        else:
            st.markdown("🏢 **[LOGO ABOAGRIM]**") # Por si no lo encuentra
            
    with col_info:
        st.markdown(f"<h1 style='margin-bottom: 0px; color: #1E3A8A;'>AboAgrim Pro DMS</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='margin-top: 0px; color: #64748B;'>Servicios Legales y Catastrales</h3>", unsafe_allow_html=True)
        st.write(f"**{PRESIDENTE_FIRMA}**")
        st.caption(f"📍 {DIRECCION_FIRMA}")
        st.caption(f"📞 {TELEFONOS_FIRMA} | ✉️ {CORREO_FIRMA}")
        
    st.divider()

    # --- 2. GRÁFICOS E INDICADORES (MÉTRICAS RÁPIDAS) ---
    st.subheader("📊 Estado General de Operaciones")
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric(label="Expedientes Activos", value="24", delta="3 Nuevos")
    c2.metric(label="Plazos en Riesgo", value="2", delta="-1 Resuelto", delta_color="inverse")
    c3.metric(label="Mensuras en Proceso", value="8", delta="Estable", delta_color="off")
    c4.metric(label="Títulos Listos", value="5", delta="Esta semana")
    
    st.write("---")

    # --- 3. DESPLEGABLE DE EXPEDIENTES (VISOR RÁPIDO) ---
    st.subheader("📂 Visor Rápido de Expedientes")
    
    # Aquí luego conectaremos su base de datos real (Supabase). Por ahora es una simulación visual.
    lista_simulada = [
        "2026-0001 | Juan Pérez | Deslinde | 🟢 A Tiempo",
        "2026-0002 | Constructora El Norte | Saneamiento | 🟡 Revisión",
        "2026-0003 | María Rodríguez | Litis de Derechos | 🔴 Urgente"
    ]
    
    expediente_sel = st.selectbox("Seleccione un expediente para revisar su estado actual:", ["-- Seleccione --"] + lista_simulada)
    
    if expediente_sel != "-- Seleccione --":
        st.info(f"🔎 **Inspeccionando:** {expediente_sel}")
        # Aquí se puede agregar un resumen rápido de lo que pasa con ese cliente
        st.write("Última actualización: *Hoy a las 09:30 AM* - Fase de revisión técnica aprobada.")

    st.write("---")

    # --- 4. PANEL DE ALERTAS Y PLAZOS ---
    st.subheader("🚨 Radar de Alertas Inminentes")
    
    alerta1, alerta2 = st.columns(2)
    with alerta1:
        st.warning("⏳ **Exp. 2026-0003 (María R.):** Vence plazo para depósito de réplica en Tribunal de Tierras en 3 días.")
        st.error("❗ **Exp. 2026-0002 (Const. Norte):** Falta firma de contrato de cuota litis.")
        
    with alerta2:
        st.success("✅ **Exp. 2025-0089 (José Reyes):** Certificado de Título recibido de Jurisdicción Original.")
        st.info("💡 **Aviso del Sistema:** Recuerde hacer respaldo de la Bóveda Digital este viernes.")

# =====================================================================
# MÓDULO 2: REGISTRO MAESTRO (CON PESTAÑAS Y 7 ROLES)
# =====================================================================

# =====================================================================
# MÓDULO 3: ARCHIVO DIGITAL (BÓVEDA, EXPLORADOR Y DESCARGA ZIP)
# =====================================================================


# =====================================================================
# MÓDULO 4: PLANTILLAS Y LEY 108-05
# =====================================================================
def vista_registro_maestro():
    import streamlit as st
    from datetime import datetime
    
    st.title("👤 Registro Maestro de Expedientes")
    st.markdown("### 🗃️ Creación y Actualización de Casos")

    # --- 0. INICIALIZACIÓN DE MEMORIA DINÁMICA ---
    # Agregamos "cant_do_rm" para controlar la cantidad de Documentos/Actuaciones
    roles_rm = ["cant_cl_rm", "cant_ap_rm", "cant_ab_rm", "cant_ag_rm", "cant_no_rm", "cant_al_rm", "cant_in_rm", "cant_do_rm"]
    for rol in roles_rm:
        if rol not in st.session_state:
            st.session_state[rol] = 1

    def mod_cant_rm(rol, operacion):
        if operacion == "add":
            st.session_state[rol] += 1
        elif operacion == "del" and st.session_state[rol] > 0:
            st.session_state[rol] -= 1

    if "db_expedientes" not in st.session_state:
        st.session_state["db_expedientes"] = {}

    with st.container(border=True):
        col_e1, col_e2 = st.columns([1, 2])
        st.info("💡 Formato oficial de la firma: **YYYY-0000** (Ej. 2026-0001)")
        num_expediente = col_e1.text_input("📁 Número de Expediente:", placeholder="2026-0001")
        asunto = col_e2.text_input("📌 Asunto o Referencia del Caso:", placeholder="Saneamiento Familia García...")
    
    st.write("---")

    # --- 1. PARTES Y REPRESENTANTES ---
    with st.expander("👥 1. Partes, Clientes y Representantes", expanded=False):
        t_cli, t_apo = st.tabs(["👤 Clientes / Propietarios", "🤝 Apoderados / Representantes"])
        
        with t_cli:
            c_btn1, c_btn2 = st.columns([1, 4])
            c_btn1.button("➕ Agregar Cliente", on_click=mod_cant_rm, args=("cant_cl_rm", "add"), key="rm_add_cl")
            c_btn2.button("➖ Quitar", on_click=mod_cant_rm, args=("cant_cl_rm", "del"), key="rm_del_cl")
            lista_clientes = []
            for i in range(st.session_state["cant_cl_rm"]):
                st.markdown(f"**Cliente {i+1}**")
                c1, c2, c3 = st.columns(3)
                n = c1.text_input("Nombre / Razón Social:", key=f"rm_cl_n_{i}")
                c = c2.text_input("Cédula / RNC:", key=f"rm_cl_c_{i}")
                t = c3.text_input("Teléfono(s):", key=f"rm_cl_t_{i}")
                c4, c5 = st.columns([2, 1])
                d = c4.text_input("Domicilio Exacto:", key=f"rm_cl_d_{i}")
                e = c5.text_input("Correo Electrónico:", key=f"rm_cl_e_{i}")
                if n: lista_clientes.append({"nombre": n, "cedula": c, "telefono": t, "domicilio": d, "email": e})

        with t_apo:
            c_btn1, c_btn2 = st.columns([1, 4])
            c_btn1.button("➕ Agregar Apoderado", on_click=mod_cant_rm, args=("cant_ap_rm", "add"), key="rm_add_ap")
            c_btn2.button("➖ Quitar", on_click=mod_cant_rm, args=("cant_ap_rm", "del"), key="rm_del_ap")
            lista_apoderados = []
            for i in range(st.session_state["cant_ap_rm"]):
                st.markdown(f"**Apoderado {i+1}**")
                c1, c2, c3 = st.columns(3)
                n = c1.text_input("Nombre Completo:", key=f"rm_ap_n_{i}")
                c = c2.text_input("Cédula:", key=f"rm_ap_c_{i}")
                q = c3.text_input("Calidad (Ej. Poder Especial):", key=f"rm_ap_q_{i}")
                c4, c5 = st.columns([2, 1])
                d = c4.text_input("Domicilio:", key=f"rm_ap_d_{i}")
                te = c5.text_input("Teléfono / Email:", key=f"rm_ap_te_{i}")
                if n: lista_apoderados.append({"nombre": n, "cedula": c, "calidad": q, "domicilio": d, "contacto": te})

    # --- 2. PROFESIONALES ---
    with st.expander("⚖️ 2. Profesionales Actuantes", expanded=False):
        t_abo, t_agr, t_not, t_alg = st.tabs(["💼 Abogados", "📐 Agrimensores", "✒️ Notarios", "⚖️ Alguaciles"])

        with t_abo:
            c_btn1, c_btn2 = st.columns([1, 4])
            c_btn1.button("➕ Agregar Abogado", on_click=mod_cant_rm, args=("cant_ab_rm", "add"), key="rm_add_ab")
            c_btn2.button("➖ Quitar", on_click=mod_cant_rm, args=("cant_ab_rm", "del"), key="rm_del_ab")
            lista_abogados = []
            for i in range(st.session_state["cant_ab_rm"]):
                c1, c2, c3 = st.columns(3)
                n = c1.text_input("Nombre:", key=f"rm_ab_n_{i}")
                c = c2.text_input("Cédula:", key=f"rm_ab_c_{i}")
                m = c3.text_input("CARD:", key=f"rm_ab_m_{i}")
                c4, c5, c6 = st.columns(3)
                d = c4.text_input("Estudio/Domicilio:", key=f"rm_ab_d_{i}")
                t = c5.text_input("Teléfono:", key=f"rm_ab_t_{i}")
                e = c6.text_input("Email:", key=f"rm_ab_e_{i}")
                if n: lista_abogados.append({"nombre": n, "cedula": c, "matricula": m, "domicilio": d, "telefono": t, "email": e})

        with t_agr:
            c_btn1, c_btn2 = st.columns([1, 4])
            c_btn1.button("➕ Agregar Agrimensor", on_click=mod_cant_rm, args=("cant_ag_rm", "add"), key="rm_add_ag")
            c_btn2.button("➖ Quitar", on_click=mod_cant_rm, args=("cant_ag_rm", "del"), key="rm_del_ag")
            lista_agrimensores = []
            for i in range(st.session_state["cant_ag_rm"]):
                c1, c2, c3 = st.columns(3)
                n = c1.text_input("Nombre:", key=f"rm_ag_n_{i}")
                c = c2.text_input("Cédula:", key=f"rm_ag_c_{i}")
                m = c3.text_input("CODIA:", key=f"rm_ag_m_{i}")
                c4, c5, c6 = st.columns(3)
                d = c4.text_input("Oficina:", key=f"rm_ag_d_{i}")
                t = c5.text_input("Teléfono:", key=f"rm_ag_t_{i}")
                e = c6.text_input("Email:", key=f"rm_ag_e_{i}")
                if n: lista_agrimensores.append({"nombre": n, "cedula": c, "matricula": m, "domicilio": d, "telefono": t, "email": e})
        
        with t_not:
            c_btn1, c_btn2 = st.columns([1, 4])
            c_btn1.button("➕ Agregar Notario", on_click=mod_cant_rm, args=("cant_no_rm", "add"), key="rm_add_no")
            c_btn2.button("➖ Quitar", on_click=mod_cant_rm, args=("cant_no_rm", "del"), key="rm_del_no")
            lista_notarios = []
            for i in range(st.session_state["cant_no_rm"]):
                c1, c2, c3 = st.columns(3)
                n = c1.text_input("Nombre:", key=f"rm_no_n_{i}")
                c = c2.text_input("Cédula:", key=f"rm_no_c_{i}")
                m = c3.text_input("Matrícula Notarial:", key=f"rm_no_m_{i}")
                if n: lista_notarios.append({"nombre": n, "cedula": c, "matricula": m})

        with t_alg:
            c_btn1, c_btn2 = st.columns([1, 4])
            c_btn1.button("➕ Agregar Alguacil", on_click=mod_cant_rm, args=("cant_al_rm", "add"), key="rm_add_al")
            c_btn2.button("➖ Quitar", on_click=mod_cant_rm, args=("cant_al_rm", "del"), key="rm_del_al")
            lista_alguaciles = []
            for i in range(st.session_state["cant_al_rm"]):
                c1, c2, c3 = st.columns(3)
                n = c1.text_input("Nombre:", key=f"rm_al_n_{i}")
                c = c2.text_input("Cédula:", key=f"rm_al_c_{i}")
                m = c3.text_input("Tribunal:", key=f"rm_al_m_{i}")
                if n: lista_alguaciles.append({"nombre": n, "cedula": c, "matricula": m})

    # --- 3. INMUEBLES Y TÍTULOS (AMPLIADO) ---
    with st.expander("📍 3. Inmuebles, Parcelas y Títulos", expanded=False):
        c_btn1, c_btn2 = st.columns([1, 4])
        c_btn1.button("➕ Agregar Inmueble", on_click=mod_cant_rm, args=("cant_in_rm", "add"), key="rm_add_in")
        c_btn2.button("➖ Quitar", on_click=mod_cant_rm, args=("cant_in_rm", "del"), key="rm_del_in")
        
        lista_inmuebles = []
        for i in range(st.session_state["cant_in_rm"]):
            st.markdown(f"**Inmueble / Parcela {i+1}**")
            c1, c2, c3 = st.columns(3)
            p = c1.text_input("Parcela/Solar:", key=f"rm_in_p_{i}")
            dc = c2.text_input("DC / Municipio:", key=f"rm_in_dc_{i}")
            prov = c3.text_input("Provincia:", key=f"rm_in_prov_{i}")
            
            c4, c5, c6 = st.columns(3)
            coord = c4.text_input("Coordenadas (UTM/Geo):", key=f"rm_in_co_{i}")
            sup = c5.text_input("Superficie:", key=f"rm_in_sup_{i}")
            tdoc = c6.selectbox("Tipo de Documento:", ["Certificado de Título", "Constancia Anotada", "Acto de Venta", "Otro"], key=f"rm_in_td_{i}")
            
            c7, c8, c9, c10 = st.columns(4)
            num = c7.text_input("Matrícula/No.:", key=f"rm_in_n_{i}")
            lib = c8.text_input("Libro:", key=f"rm_in_l_{i}")
            fol = c9.text_input("Folio:", key=f"rm_in_f_{i}")
            f_ins = c10.text_input("Fecha de Inscripción:", key=f"rm_in_fi_{i}")
            
            if p: lista_inmuebles.append({"parcela": p, "dc": dc, "provincia": prov, "coordenadas": coord, "superficie": sup, "tipo_doc": tdoc, "numero": num, "libro": lib, "folio": fol, "fecha_ins": f_ins})

    # --- 4. NUEVO: ACTUACIONES Y DOCUMENTOS ---
    with st.expander("📝 4. Actuaciones y Documentos del Expediente", expanded=True):
        st.info("Registre las instancias, demandas, actos y notificaciones vinculadas a este caso.")
        c_btn1, c_btn2 = st.columns([1, 4])
        c_btn1.button("➕ Agregar Documento", on_click=mod_cant_rm, args=("cant_do_rm", "add"), key="rm_add_do")
        c_btn2.button("➖ Quitar", on_click=mod_cant_rm, args=("cant_do_rm", "del"), key="rm_del_do")
        
        lista_documentos = []
        for i in range(st.session_state["cant_do_rm"]):
            st.markdown(f"**Actuación / Documento {i+1}**")
            c1, c2, c3, c4 = st.columns([2, 3, 2, 2])
            
            tipos_doc = ["Acto", "Acta", "Instancia", "Solicitud", "Informe", "Demanda", "Carta", "Notificación", "Otro"]
            tipo_d = c1.selectbox("Clasificación:", tipos_doc, key=f"rm_do_t_{i}")
            desc_d = c2.text_input("Descripción / Título:", placeholder="Ej. Instancia de fijación de audiencia", key=f"rm_do_d_{i}")
            fecha_d = c3.date_input("Fecha:", key=f"rm_do_f_{i}")
            estado_d = c4.selectbox("Estado Actual:", ["Redactado", "Depositado", "Notificado", "Aprobado", "Rechazado"], key=f"rm_do_e_{i}")
            
            if desc_d: lista_documentos.append({"tipo": tipo_d, "descripcion": desc_d, "fecha": str(fecha_d), "estado": estado_d})

    st.write("---")
    
    # --- BOTÓN DE GUARDADO MAESTRO ---
    if st.button("💾 Guardar / Actualizar Expediente en Bóveda", type="primary", use_container_width=True):
        if num_expediente and asunto:
            st.session_state["db_expedientes"][num_expediente] = {
                "asunto": asunto,
                "fecha_creacion": datetime.now().strftime("%Y-%m-%d"),
                "clientes": lista_clientes,
                "apoderados": lista_apoderados,
                "abogados": lista_abogados,
                "agrimensores": lista_agrimensores,
                "notarios": lista_notarios,
                "alguaciles": lista_alguaciles,
                "inmuebles": lista_inmuebles,
                "documentos": lista_documentos # Guardamos la nueva lista de actuaciones
            }
            st.success(f"✅ ¡Expediente {num_expediente} guardado exitosamente en el Registro Maestro!")
            st.balloons()
        else:
            st.error("⚠️ Debe indicar al menos el Número de Expediente y el Asunto para poder guardar.")

    # --- LISTADO DE EXPEDIENTES ---
    st.divider()
    st.subheader("🗂️ Archivo de Expedientes Registrados")
    if st.session_state["db_expedientes"]:
        for exp_num, exp_data in st.session_state["db_expedientes"].items():
            with st.expander(f"📁 Expediente: {exp_num} - {exp_data['asunto']}"):
                col_d1, col_d2, col_d3 = st.columns(3)
                col_d1.write(f"**Fecha Registro:** {exp_data['fecha_creacion']}")
                col_d1.write(f"**Clientes:** {len(exp_data['clientes'])}")
                
                col_d2.write(f"**Profesionales:** {len(exp_data['abogados']) + len(exp_data['agrimensores'])}")
                col_d2.write(f"**Inmuebles:** {len(exp_data['inmuebles'])}")
                
                # Usamos .get() por si hay expedientes viejos que no tenían la lista de documentos
                col_d3.write(f"**Actuaciones/Docs:** {len(exp_data.get('documentos', []))}")
                
                if st.button("🗑️ Eliminar Expediente", key=f"del_exp_{exp_num}"):
                    del st.session_state["db_expedientes"][exp_num]
                    st.rerun()
    else:
        st.info("No hay expedientes registrados aún. Llene los datos arriba y presione Guardar.")
# =====================================================================
# MÓDULO 5: ALERTAS Y PLAZOS
# =====================================================================

def vista_alertas_plazos():
    st.title("📅 Radar de Alertas y Plazos JI")
    st.subheader("Control Normativo Ley 108-05 | AboAgrim Pro")
    
    # 1. BOTÓN DINÁMICO DE BÚSQUEDA
    st.markdown("### 🔍 Motor de Rastreo de Expedientes")
    col_scan, col_info = st.columns([1, 2])
    escanear = col_scan.button("🚀 Escanear Plazos Activos", type="primary", use_container_width=True)
    col_info.info("Haga clic para sincronizar las fechas con la nube y calcular los vencimientos normativos de sus expedientes.")
    
    # 2. LAS TRES GRANDES ÁREAS DE LA JURISDICCIÓN INMOBILIARIA
    tab_tecnica, tab_judicial, tab_registro = st.tabs([
        "📐 Área Técnica (Mensuras)", 
        "⚖️ Judicial y Recursos", 
        "📜 Registro de Títulos"
    ])
    
    hoy = datetime.now().date()
    
    if escanear:
        # Extraemos la data de la base de datos maestra
        try:
            res = supabase.table("expedientes_maestros").select("*").execute()
            expedientes = res.data if res.data else []
        except Exception as e:
            expedientes = []
            st.error(f"Error de conexión a la Nube: {e}")
            
        with tab_tecnica:
            st.markdown("#### ⏳ Plazos de la Dirección Regional de Mensuras Catastrales")
            st.write("Control de autorizaciones, trabajo de campo y revisión técnica.")
            
            if expedientes:
                for caso in expedientes:
                    if caso.get('fecha_creacion'):
                        f_ini = datetime.strptime(caso['fecha_creacion'][:10], '%Y-%m-%d').date()
                        
                        # CÁLCULOS TÉCNICOS AMPLIADOS (Ley 108-05)
                        venc_campo = f_ini + timedelta(days=60) # Plazo de ejecución de mensura
                        venc_deposito = venc_campo + timedelta(days=15) # Plazo para depósito tras el trabajo
                        
                        dias_campo = (venc_campo - hoy).days
                        
                        with st.container(border=True):
                            c1, c2 = st.columns([3, 1])
                            c1.markdown(f"**Exp:** {caso['expediente']} | **Propietario:** {caso.get('nombre_propietario', 'N/A')}")
                            c1.caption(f"Operación: {caso.get('tipo_acto', 'Mensura Catastral')} | Fecha de Inicio: {f_ini}")
                            
                            if dias_campo < 0:
                                c2.error(f"Vencido hace {abs(dias_campo)} días")
                            elif dias_campo <= 15:
                                c2.warning(f"Queda(n) {dias_campo} día(s) (CRÍTICO)")
                            else:
                                c2.success(f"En tiempo ({dias_campo} días)")
                                
                            # Desglose Dinámico
                            with st.expander("Ver Desglose de Plazos Técnicos"):
                                st.write(f"🟢 **Vencimiento Autorización (60 días):** {venc_campo.strftime('%d/%m/%Y')}")
                                st.write(f"🟡 **Límite Depósito de Planos (+15 días):** {venc_deposito.strftime('%d/%m/%Y')}")
            else:
                st.warning("No se encontraron expedientes técnicos activos.")
                
        with tab_judicial:
            st.markdown("#### ⚖️ Control de Audiencias y Vías de Recurso")
            st.write("Gestión de plazos ante los Tribunales de Tierras y la SCJ.")
            
            with st.container(border=True):
                st.markdown("**📌 Alarmas Normativas para Recursos:**")
                c_j1, c_j2 = st.columns(2)
                
                with c_j1:
                    st.error("**Vía Administrativa:**")
                    st.write("• **Recurso de Reconsideración:** 15 días (Ante el mismo órgano).")
                    st.write("• **Recurso Jerárquico:** 15 días (Ante el órgano superior).")
                
                with c_j2:
                    st.error("**Vía Jurisdiccional:**")
                    st.write("• **Recurso de Apelación:** 30 días (Tribunal Superior de Tierras).")
                    st.write("• **Recurso de Casación:** 30 días (Suprema Corte de Justicia).")
                    
            st.info("💡 Utilice el 'Registro Maestro' para registrar las fechas de notificación de las sentencias u oficios y activar automáticamente estas cuentas regresivas.")

        with tab_registro:
            st.markdown("#### 📜 Control del Registro de Títulos")
            st.write("Seguimiento a emisión de Certificados de Título y depósitos registrales.")
            
            with st.container(border=True):
                st.markdown("**📌 Plazos Normativos Registrales:**")
                st.write("• **Calificación y Emisión de Título:** 45 días laborables.")
                st.write("• **Anotación de Litis sobre Derechos Registrados:** 15 días laborables.")
                st.write("• **Inscripción de Hipotecas / Privilegios:** 15 días laborables.")
                st.write("• **Aprobación de Condominios:** 45 días laborables.")
            
            st.info("💡 Los expedientes que pasen a la fase de 'Registro de Títulos' iniciarán su cuenta regresiva de 45 días laborables aquí.")
            
    else:
        # Pantalla en espera si no se ha hecho clic en el botón
        st.info("👈 Presione el botón azul 'Escanear Plazos Activos' arriba para iniciar el rastreo normativo en su base de datos.")
            
def vista_configuracion():
    st.title("⚙️ Panel de Control Maestro")
    
    if st.session_state.get("admin_autenticado", False):
        tab_perfil, tab_usuarios, tab_sistema = st.tabs(["👤 Mi Perfil", "👥 Gestión de Personal", "🛠️ Base de Datos"])
        
        # --- TAB 1: PERFIL PROFESIONAL ---
        with tab_perfil:
            with st.container(border=True):
                c1, c2 = st.columns([1, 3])
                c1.markdown("## ⚖️")
                c2.markdown(f"### {st.session_state.get('usuario', 'Lic. Jhonny Matos')}")
                c2.caption(f"**Cargo:** {st.session_state.get('rol', 'Presidente Fundador')}")
                
                st.divider()
                st.markdown("**Información de Contacto Institucional:**")
                st.write("📧 **Email:** Aboagrim@gmail.com")
                st.write("📞 **Teléfonos:** 829-826-5888 | 809-691-3333")
                st.write("📍 **Oficina:** Calle Boy Scout 83, Plaza Jasansa, Santiago.")
        
        # === 2. PESTAÑA DE USUARIOS (RECONSTRUIDA Y POTENCIADA) ===
    with tab_usuarios:
        st.subheader("👥 Gestión de Capital Humano y Permisos")
        st.write("Administre los niveles de acceso y roles oficiales de la firma.")

        # --- SECCIÓN A: LISTA OFICIAL DE PERSONAL ---
        st.markdown("### 📋 Directorio de Usuarios")
        # Aquí recuperamos los roles que teníamos en el 'blindaje'
        df_usuarios = {
            "Nombre Completo": ["Lic. Jhonny Matos", "Lic. Pedro Almonte", "Ing. Marcos Díaz", "Ana Cabrera"],
            "Usuario": ["JMatos", "PAlmonte", "MDiaz", "ACabrera"],
            "Rol Oficial": ["Presidente-Fundador", "Abogado Senior", "Agrimensor Principal", "Asistente Legal"],
            "Especialidad": ["Derecho Inmobiliario", "Litis y Tierras", "Mensuras y Deslindes", "Tramitaciones"],
            "Acceso": ["🟢 Total", "🟡 Parcial", "🟡 Parcial", "🔵 Limitado"]
        }
        st.dataframe(df_usuarios, use_container_width=True)

        st.divider()

        # --- SECCIÓN B: REGISTRO DE NUEVO TALENTO ---
        with st.expander("➕ Dar de Alta a Nuevo Miembro del Equipo", expanded=False):
            c_u1, c_u2 = st.columns(2)
            with c_u1:
                nuevo_nombre = st.text_input("Nombre y Apellidos:")
                nuevo_user = st.text_input("Nombre de Usuario (Login):")
                nueva_clave = st.text_input("Contraseña Inicial:", type="password")
            with c_u2:
                # Recuperamos los roles exactos para el sistema de blindaje
                nuevo_rol = st.selectbox("Rol en el Sistema:", [
                    "Abogado", 
                    "Agrimensor", 
                    "Asistente", 
                    "Pasante",
                    "Contabilidad"
                ])
                nueva_especialidad = st.text_input("Especialidad / Área:")
                estado_cuenta = st.radio("Estado Inicial:", ["Activo", "En Prueba"], horizontal=True)

            if st.button("💾 Registrar y Crear Credenciales", use_container_width=True):
                st.success(f"✅ Usuario {nuevo_user} creado con éxito bajo el rol de {nuevo_rol}.")

        st.divider()

        # --- SECCIÓN C: MATRIZ DE PERMISOS (BLINDAJE MAESTRO) ---
        st.markdown("### 🔐 Matriz de Acceso por Módulo")
        st.info("Configure qué módulos son visibles para cada rol. (Blindaje de Seguridad)")
        
        col_perm1, col_perm2 = st.columns(2)
        with col_perm1:
            st.markdown("**📂 Gestión de Expedientes**")
            p_abog = st.checkbox("Abogados", value=True)
            p_agrim = st.checkbox("Agrimensores", value=True)
            p_pasant = st.checkbox("Pasantes", value=False)
            
            st.markdown("**💰 Gestión de Honorarios (Finanzas)**")
            f_abog = st.checkbox("Abogados (Solo ver)", value=True)
            f_cont = st.checkbox("Contabilidad (Acceso Total)", value=True)
            f_pasant = st.checkbox("Pasantes (Acceso Denegado)", value=False, disabled=True)

        with col_perm2:
            st.markdown("**📄 Fábrica de Documentos**")
            d_abog = st.checkbox("Acceso Abogados", value=True)
            d_agrim = st.checkbox("Acceso Agrimensores", value=True)
            
            st.markdown("**⚙️ Configuración del Sistema**")
            c_master = st.checkbox("Solo Presidente (Blindaje Activo)", value=True, disabled=True)
            
        if st.button("🔄 Actualizar Matriz de Blindaje", type="primary"):
            st.warning("Los permisos han sido actualizados. Los usuarios verán los cambios en su próximo inicio de sesión.")

        # --- TAB 3: ESTADO DE LA BASE DE DATOS ---
        with tab_sistema:
            st.subheader("Estado de la Nube (Supabase)")
            
            # Intentamos contar registros reales para que no esté vacío
            try:
                res_exp = supabase.table("expedientes_maestros").select("id", count="exact").execute()
                count_exp = res_exp.count if res_exp.count else 0
                
                res_doc = supabase.table("archivo_digital").select("id", count="exact").execute()
                count_doc = res_doc.count if res_doc.count else 0
            except:
                count_exp, count_doc = 0, 0

            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Expedientes", count_exp)
            col_s1.caption("Total de casos en nube")
            
            col_s2.metric("Documentos", count_doc)
            col_s2.caption("Archivos vinculados")
            
            col_s3.metric("Estado", "Online", delta="Conectado")
            
            st.divider()
            st.info("💡 La base de datos está sincronizada con Supabase Cloud. Los respaldos se realizan cada 24 horas automáticamente.")

        st.divider()
        if st.button("🚪 Cerrar Sesión del Sistema"):
            st.session_state.admin_autenticado = False
            st.rerun()

        else:
            # LOGIN (Para cuando no está autenticado)
            st.markdown("### 🔑 Autenticación Requerida")
            u = st.text_input("Usuario Master:")
            p = st.text_input("PIN de Seguridad:", type="password")
            
            if st.button("Desbloquear Panel"):
                if u == "JhonnyMatos" and p == "0681":
                    st.session_state.admin_autenticado = True
                    st.session_state.usuario = "Jhonny Matos"
                    st.session_state.rol = "Presidente Fundador"
                    st.rerun()
                else:
                    st.error("Credenciales inválidas.")
            # Nota: Esto se complementa con CSS personalizado en el inicio del script
        # Aquí va la función de agregar/borrar usuarios...
def login_sistema():
    st.markdown("""
        <style>
        .login-box {
            background-color: #f0f2f6;
            padding: 30px;
            border-radius: 15px;
            border: 2px solid #1E3A8A;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.image("https://vuestra-url-logo.com/logo.png", width=200) # Si tiene logo
        st.header("🔐 Acceso AboAgrim Pro")
        
        u_ingreso = st.text_input("Nombre de Usuario:")
        p_ingreso = st.text_input("PIN de Seguridad:", type="password", max_chars=4)
        
        if st.button("Ingresar al Sistema", use_container_width=True):
            # Buscamos en la tabla de usuarios que ya creamos en Supabase
            res = supabase.table("usuarios_sistema").select("*").eq("nombre_usuario", u_ingreso).eq("pin_acceso", p_ingreso).eq("estado", "Activo").execute()
            
            if res.data:
                st.session_state.autenticado_global = True
                st.session_state.usuario_actual = u_ingreso
                st.success(f"Bienvenido, {u_ingreso}")
                st.rerun()
            else:
                st.error("Usuario o PIN incorrectos, o cuenta inactiva.")

def vista_archivo_digital():
    import streamlit as st
    import os

    st.title("🗄️ Archivo Digital y Bóveda")
    st.markdown("### Repositorio Central de Expedientes y Anexos Técnicos")
    
    # --- 1. SINCRONIZACIÓN CON EL REGISTRO MAESTRO ---
    # Verificamos si el otro módulo ya creó expedientes en la memoria
    if "db_expedientes" not in st.session_state or not st.session_state["db_expedientes"]:
        st.info("ℹ️ El Archivo Digital está esperando datos. Registre un caso en el 'Registro Maestro' primero para que aparezca aquí.")
        return

    # Crear estructura física de la bóveda si no existe
    if not os.path.exists("boveda_digital"):
        os.makedirs("boveda_digital")

    st.write("---")

    # --- 2. BUSCADOR INTELIGENTE INTERCONECTADO ---
    lista_exps = list(st.session_state["db_expedientes"].keys())
    
    col_busq1, col_busq2 = st.columns([3, 1])
    with col_busq1:
        exp_seleccionado = st.selectbox("🔍 Buscar y Seleccionar Expediente:", lista_exps)
    
    # El sistema crea una carpeta única para ese expediente automáticamente
    ruta_exp = os.path.join("boveda_digital", exp_seleccionado)
    if not os.path.exists(ruta_exp):
        os.makedirs(ruta_exp)

    # Extraemos los datos que usted llenó en el Registro Maestro
    datos_exp = st.session_state["db_expedientes"][exp_seleccionado]

    # --- 3. INTERFAZ DE GESTIÓN DOCUMENTAL ---
    tab_resumen, tab_anexos, tab_zip = st.tabs([
        "📋 Resumen del Caso", "📎 Subir Anexos (Planos, PDF)", "📦 Empaquetar Expediente"
    ])

    # PESTAÑA A: Visor de Memoria
    with tab_resumen:
        st.subheader(f"Radiografía: {exp_seleccionado}")
        st.markdown(f"**Trámite Solicitado:** {datos_exp.get('tramite', 'No especificado')}")
        st.markdown(f"**Jurisdicción:** {datos_exp.get('jurisdiccion', 'No especificada')}")
        
        estado = datos_exp.get('estado', 'N/A')
        # Etiqueta de estado con colores dinámicos
        if estado in ["Aprobado", "Cerrado"]:
            st.success(f"**Estado del Caso:** {estado}")
        elif estado == "En Litigio":
            st.error(f"**Estado del Caso:** {estado}")
        else:
            st.warning(f"**Estado del Caso:** {estado}")
            
        st.info("💡 Este módulo lee en tiempo real los datos que usted ingresa en el Registro Maestro. Si modifica algo allá, se reflejará aquí.")

    # PESTAÑA B: Bóveda de Anexos
    with tab_anexos:
        st.subheader("Bóveda de Anexos Físicos y Planos")
        st.write("Suba aquí copias de cédulas, planos topográficos (DWG), sentencias y actos firmados.")
        
        archivos_subidos = st.file_uploader(f"Anexar a {exp_seleccionado}", accept_multiple_files=True, help="Puede subir PDF, JPG, DWG, DOCX...")
        
        if archivos_subidos:
            if st.button("💾 Guardar Anexos en Bóveda", type="primary"):
                for archivo in archivos_subidos:
                    with open(os.path.join(ruta_exp, archivo.name), "wb") as f:
                        f.write(archivo.getbuffer())
                st.success(f"✅ {len(archivos_subidos)} documento(s) blindado(s) exitosamente.")
                st.rerun()
        
        # Listador de documentos anexos con opción a borrar
        st.write("---")
        st.markdown(f"**Documentos actualmente en la carpeta {exp_seleccionado}:**")
        archivos_guardados = os.listdir(ruta_exp)
        
        if archivos_guardados:
            for arch in archivos_guardados:
                col_file, col_del = st.columns([4, 1])
                col_file.markdown(f"📄 `{arch}`")
                if col_del.button("❌ Borrar", key=f"del_{exp_seleccionado}_{arch}"):
                    os.remove(os.path.join(ruta_exp, arch))
                    st.rerun()
        else:
            st.caption("No hay documentos anexos todavía.")

    # PESTAÑA C: Empaquetado para el Tribunal
    with tab_zip:
        st.subheader("Preparación para Depósito / Entrega")
        st.write("Genere un archivo comprimido (.zip) con todo el contenido del expediente para enviarlo por correo o subirlo a la plataforma virtual de la Jurisdicción Inmobiliaria.")
        
        if st.button("📦 Empaquetar Todo en ZIP", use_container_width=True):
            if not os.listdir(ruta_exp):
                st.warning("⚠️ El expediente no tiene documentos para empaquetar.")
            else:
                import io
                import zipfile
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for root, _, files in os.walk(ruta_exp):
                        for file in files:
                            ruta_completa = os.path.join(root, file)
                            zip_file.write(ruta_completa, file)
                
                zip_buffer.seek(0)
                st.success("✅ Paquete de depósito generado con éxito.")
                st.download_button(
                    label=f"⬇️ Descargar {exp_seleccionado}_Completo.zip",
                    data=zip_buffer,
                    file_name=f"{exp_seleccionado}_AboAgrim_Completo.zip",
                    mime="application/zip",
                    type="primary"
                )

# Aquí debajo empieza su def generar_documento_word...


def generar_documento_word(ruta_plantilla, diccionario_datos):
    """
    Toma una plantilla de la carpeta 'plantillas_maestras' y la llena con los datos.
    Devuelve un objeto de memoria (BytesIO) listo para descargar o subir a Drive.
    """
    try:
        # Cargamos el archivo base usando la ruta exacta que le manda el sistema
        doc = DocxTemplate(ruta_plantilla)
        
        # Fusionamos el Word con el diccionario de datos (las llaves {{ }})
        doc.render(diccionario_datos)
        
        # Lo guardamos en memoria para que descargue rápido
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return buffer
        
    except FileNotFoundError:
        st.error(f"❌ No se encontró la plantilla en la ruta: {ruta_plantilla}. Verifique en su Administrador de Archivos.")
        return None
    except Exception as e:
        st.error(f"❌ Error en la forja del documento: {e}")
        return None

# =======================================================
# 1. DISEÑO DE LA PANTALLA DE PLANTILLAS
# =======================================================

# ==========================================
# 🚦 ENRUTADOR REFORZADO - ABOAGRIM PRO
# ==========================================

# 1. Asegurar el Rol de Presidente (Blindaje)
usuario_actual = st.session_state.get("usuario", "Invitado")

# Si es usted, forzamos el rango máximo automáticamente
if "Jhonny" in usuario_actual or usuario_actual == "JhonnyMatos":
    st.session_state["rol"] = "Presidente Fundador"
    st.session_state["admin_autenticado"] = True

rol_usuario = st.session_state.get("rol", "Pasante")


def vista_alertas_plazos():
    import streamlit as st
    from datetime import date

    st.title("⏱️ Sistema Integrado de Plazos (SIP)")
    st.markdown("### Motor Lógico de Caducidad y Rutas Críticas")

    # --- 1. CATÁLOGO LEGAL ---
    catalogo_acciones = {
        # MENSURAS CATASTRALES
        'Vigencia Autorización de Mensura': {
            'cat': 'Mensuras Catastrales', 'tipo': 'plazo', 'unidad': 'dias', 'plazo': 60,
            'baseLegal': "Art. 25, Ley 108-05 | Reg. Mensuras Catastrales",
            'jurisprudencia': "SCJ: Plazo busca evitar la inercia en el saneamiento (Art. 51 Const).",
            'diagnosticoAprobado': "Autorización para trabajos de mensura vigente.",
            'diagnosticoRechazado': "¡Caducidad! Han pasado más de 60 días sin presentar los trabajos.",
            'estrategia': "Solicitar prórroga justificada o tramitar nueva autorización.",
            'requisitos': ["Contrato de mensura firmado", "Copia de cédulas de los reclamantes", "Croquis ilustrativo de la porción a sanear", "Instancia motivada de solicitud"],
            'procedimientos': ["1. Depósito de solicitud vía ventanilla de la Jurisdicción Original.", "2. Apoderamiento del tribunal y emisión de la Autorización (Auto).", "3. Notificación a la Dirección Regional de Mensuras Catastrales."]
        },
        'Plazo Aviso de Mensura (Colindantes)': {
            'cat': 'Mensuras Catastrales', 'tipo': 'plazo_inverso', 'unidad': 'dias', 'plazo': 15,
            'baseLegal': "Art. 69, Reglamento General de Mensuras Catastrales",
            'jurisprudencia': "TC: La falta de notificación vulnera el debido proceso y acarrea nulidad.",
            'diagnosticoAprobado': "Plazo correcto para avisar a colindantes antes del terreno.",
            'diagnosticoRechazado': "Defecto de Plazo. No hay tiempo para el aviso previo legal.",
            'estrategia': "Reprogramar la fecha del levantamiento en el terreno.",
            'requisitos': ["Autorización de mensura / Contrato", "Formulario de Aviso de Mensura", "Lista de colindantes e interesados"],
            'procedimientos': ["1. Redactar el aviso indicando fecha y hora del levantamiento.", "2. Notificar vía acto de alguacil, carta con acuse o publicación en prensa.", "3. Anexar constancias de notificación al expediente técnico."]
        },
        'Subsanar Expediente Técnico Observado': {
            'cat': 'Mensuras Catastrales', 'tipo': 'plazo', 'unidad': 'dias', 'plazo': 30,
            'baseLegal': "Art. 22, Reglamento General de Mensuras Catastrales (Res. 790-2022)",
            'jurisprudencia': "Garantía de debido proceso administrativo ante rechazos provisionales.",
            'diagnosticoAprobado': "Plazo hábil para reingresar el expediente técnico.",
            'diagnosticoRechazado': "Rechazo Definitivo. Se agotó el plazo para subsanar.",
            'estrategia': "Someter como expediente nuevo y pagar tasas.",
            'requisitos': ["Oficio de observaciones emitido por el calificador", "Planos o XML corregidos", "Carta de reingreso motivada"],
            'procedimientos': ["1. Corregir los defectos indicados en el sistema gráfico/documental.", "2. Reingresar el expediente.", "3. Dar seguimiento al nuevo turno de calificación."]
        },
        'Recurso Reconsideración (Dir. Regional)': {
            'cat': 'Mensuras Catastrales', 'tipo': 'plazo', 'unidad': 'dias', 'plazo': 15,
            'baseLegal': "Art. 74, Ley 108-05",
            'jurisprudencia': "Agotamiento obligatorio de vías administrativas previas.",
            'diagnosticoAprobado': "Plazo hábil para recurrir ante el Dir. Regional.",
            'diagnosticoRechazado': "Caducidad. Acto técnico firme.",
            'estrategia': "La calificación técnica adquiere carácter definitivo.",
            'requisitos': ["Instancia motivada dirigida al Director Regional", "Acto impugnado (Calificación rechazada)", "Pruebas técnicas que desmientan la observación"],
            'procedimientos': ["1. Redactar instancia de reconsideración anexando pruebas.", "2. Depositar vía Secretaría de la Dirección Regional.", "3. Esperar resolución administrativa en un plazo de 15 días."]
        },

        # REGISTRO DE TÍTULOS
        'Subsanar Expediente Registral Observado': {
            'cat': 'Registro de Títulos', 'tipo': 'plazo', 'unidad': 'dias', 'plazo': 30,
            'baseLegal': "Art. 54, Reglamento General de Registro de Títulos",
            'jurisprudencia': "Principios registrales de rogación y legalidad.",
            'diagnosticoAprobado': "Plazo hábil para levantar el Rechazo Provisional.",
            'diagnosticoRechazado': "Rechazo Definitivo Registral.",
            'estrategia': "Reingresar la solicitud como expediente nuevo.",
            'requisitos': ["Documento faltante (Impuestos DGII, Cédulas, Actas de Estado Civil)", "Copia del oficio de rechazo provisional"],
            'procedimientos': ["1. Obtener la documentación omitida o corregir el acto jurídico.", "2. Depositar por ventanilla el complemento del expediente.", "3. Esperar la calificación definitiva."]
        },
        'Caducidad de Anotación Preventiva': {
            'cat': 'Registro de Títulos', 'tipo': 'plazo', 'unidad': 'anos', 'plazo': 1,
            'baseLegal': "Art. 89, Ley 108-05 | Reg. de Registro de Títulos",
            'jurisprudencia': "La anotación caduca de pleno derecho si no se interpone demanda de fondo.",
            'diagnosticoAprobado': "Anotación Preventiva mantiene vigencia.",
            'diagnosticoRechazado': "Anotación Caducada de pleno derecho.",
            'estrategia': "Solicitar cancelación administrativa por caducidad.",
            'requisitos': ["Instancia solicitando anotación preventiva", "Prueba fehaciente del derecho o crédito reclamado", "Pago de tasas registrales"],
            'procedimientos': ["1. Depositar instancia con pruebas ante el Registro de Títulos.", "2. El registrador inscribe el bloqueo preventivo.", "3. Obligación de demandar el fondo en los tribunales antes de 1 año."]
        },
        'Reclamo Indemnización (Fondo de Garantía)': {
            'cat': 'Registro de Títulos', 'tipo': 'plazo', 'unidad': 'anos', 'plazo': 1,
            'baseLegal': "Art. 39, Ley 108-05",
            'jurisprudencia': "SCJ: La indemnización por errores registrales o desalojos sin negligencia del titular tiene un plazo de caducidad estricto de 1 año.",
            'diagnosticoAprobado': "Acción indemnizatoria viable ante el Estado.",
            'diagnosticoRechazado': "Acción caducada frente al Fondo de Garantía.",
            'estrategia': "Reclamación inadmisible. No hay fondos públicos disponibles.",
            'requisitos': ["Sentencia definitiva de privación de derecho", "Prueba de no negligencia del titular", "Tasación del inmueble"],
            'procedimientos': ["1. Incoar demanda contra el Fondo ante el Tribunal Superior de Tierras.", "2. Demostrar el daño emergente.", "3. Ejecutar sentencia contra el Estado para el pago compensatorio."]
        },

        # TRIBUNALES
        'Notificar Demanda Introductiva (10 días)': {
            'cat': 'Tribunales (Litis e Incidentes)', 'tipo': 'plazo', 'unidad': 'dias', 'plazo': 10,
            'baseLegal': "Art. 30, Ley 108-05 | Art. 62, Reglamento Tribunales",
            'jurisprudencia': "TC/0071/13: La notificación oportuna garantiza la tutela judicial efectiva.",
            'diagnosticoAprobado': "Plazo hábil para emplazar a la contraparte.",
            'diagnosticoRechazado': "Caducidad del depósito por falta de emplazamiento.",
            'estrategia': "Depositar nueva demanda inicial en Secretaría.",
            'requisitos': ["Instancia original sellada por el tribunal", "Acto de alguacil (Emplazamiento)", "Fijación de audiencia (Si aplica)"],
            'procedimientos': ["1. Depositar instancia en la Secretaría.", "2. Retirar instancia sellada.", "3. Alguacil notifica en 10 días máximo.", "4. Depositar acto de notificación en tribunal."]
        },
        'Caducidad de Instancia (Inactividad 3 años)': {
            'cat': 'Tribunales (Litis e Incidentes)', 'tipo': 'plazo', 'unidad': 'anos', 'plazo': 3,
            'baseLegal': "Art. 397 y ss. del Código de Procedimiento Civil",
            'jurisprudencia': "SCJ: La inactividad de las partes por 3 años extingue el proceso, asimilándose al abandono.",
            'diagnosticoAprobado': "Proceso activo. Se interrumpió la caducidad.",
            'diagnosticoRechazado': "Presunción de abandono. Plazo cumplido.",
            'estrategia': "Oponer incidente de Caducidad de Instancia.",
            'requisitos': ["Certificación de inactividad expedida por Secretaría", "Último acto procesal fechado hace más de 3 años", "Conclusiones incidentales"],
            'procedimientos': ["1. Solicitar fijación de audiencia.", "2. Presentar in limine litis la demanda en caducidad.", "3. El tribunal extingue el proceso sin fallar el fondo."]
        },
        'Litis: Nulidad Absoluta (Falsedad/Simulación)': {
            'cat': 'Tribunales (Litis e Incidentes)', 'tipo': 'plazo', 'unidad': 'anos', 'plazo': 20,
            'baseLegal': "Art. 2262, Código Civil | Principio VIII, Ley 108-05",
            'jurisprudencia': "SCJ: Cómputo inicia desde publicidad en Registro de Títulos.",
            'diagnosticoAprobado': "Litis viable. Acción viva.",
            'diagnosticoRechazado': "Acción prescrita. Consolidación veintenal.",
            'estrategia': "Oponer Medio de Inadmisión por prescripción.",
            'requisitos': ["Acto atacado (Contrato falso/simulado)", "Pruebas del vicio", "Certificación de Estado Jurídico"],
            'procedimientos': ["1. Depósito de demanda en Jurisdicción Original.", "2. Notificación en 10 días.", "3. Audiencia de Sometimiento de Pruebas.", "4. Audiencia de Fondo y conclusiones."]
        },
        'Solicitud Fuerza Pública (Abogado del Estado)': {
            'cat': 'Tribunales (Litis e Incidentes)', 'tipo': 'plazo', 'unidad': 'dias', 'plazo': 15,
            'baseLegal': "Art. 47, Ley 108-05",
            'jurisprudencia': "SCJ: El Abogado del Estado ejecuta desalojos de intrusos sin título.",
            'diagnosticoAprobado': "Plazo de intimación voluntaria corriendo.",
            'diagnosticoRechazado': "Venció el plazo. Fuerza pública ejecutable.",
            'estrategia': "Coordinar fuerza pública con Policía Nacional.",
            'requisitos': ["Certificado de Título a nombre del solicitante", "Certificación de Estado Jurídico", "Acto de intimación a desocupar (15 días antelación)", "Comprobación de invasión"],
            'procedimientos': ["1. Notificar acto de alguacil a los intrusos dando 15 días.", "2. Solicitar Fuerza Pública al Abogado del Estado anexando pruebas.", "3. Autorización y coordinación con fuerza pública para el lanzamiento."]
        },

        # ALTAS CORTES Y RECURSOS
        'Recurso de Apelación (TST)': {
            'cat': 'Altas Cortes y Recursos', 'tipo': 'plazo', 'unidad': 'dias', 'plazo': 30,
            'baseLegal': "Art. 80, Ley 108-05",
            'jurisprudencia': "SCJ: Plazos de orden público; inobservancia acarrea inadmisibilidad.",
            'diagnosticoAprobado': "Plazo abierto para depositar apelación.",
            'diagnosticoRechazado': "Plazo vencido. Sentencia firme.",
            'estrategia': "Solicitar Certificado de No Apelación.",
            'requisitos': ["Instancia de recurso motivando los agravios", "Sentencia impugnada notificada", "Pago de tasas judiciales"],
            'procedimientos': ["1. Depositar recurso en la Secretaría del Tribunal que dictó la sentencia.", "2. Notificar a la contraparte en 10 días.", "3. El expediente es remitido al Tribunal Superior de Tierras."]
        },
        'Revisión Constitucional (Tribunal Constitucional)': {
            'cat': 'Altas Cortes y Recursos', 'tipo': 'plazo', 'unidad': 'dias', 'plazo': 30,
            'baseLegal': "Art. 53, Ley 137-11 (Orgánica del Tribunal Constitucional)",
            'jurisprudencia': "TC: Procede contra decisiones jurisdiccionales firmes que vulneren derechos fundamentales.",
            'diagnosticoAprobado': "Plazo hábil para interponer revisión ante el TC.",
            'diagnosticoRechazado': "Recurso extemporáneo. Sentencia inatacable.",
            'estrategia': "Ejecutar de forma definitiva la decisión de la SCJ.",
            'requisitos': ["Sentencia de la Suprema Corte (irrevocable)", "Escrito motivando la vulneración constitucional", "Notificación previa a la SCJ"],
            'procedimientos': ["1. Depositar recurso ante la Secretaría de la corte que dictó la decisión (SCJ).", "2. La corte lo tramita al TC.", "3. Notificar a la contraparte y esperar juicio de admisibilidad del TC."]
        },

        # IMPRESCRIPTIBLES
        'Reivindicación, Deslinde, Saneamiento y Partición': {
            'cat': 'Acciones Imprescriptibles', 'tipo': 'imprescriptible', 'unidad': None, 'plazo': None,
            'baseLegal': "Principio IV, Ley 108-05 | Art. 51 Constitución",
            'jurisprudencia': "TC/0214/18: Derechos registrados son imprescriptibles contra ocupantes ilegales.",
            'diagnosticoAprobado': "La acción es de orden público y NO prescribe.",
            'diagnosticoRechazado': "La acción es de orden público y NO prescribe.",
            'estrategia': "Proceder sin restricciones de tiempo.",
            'requisitos': ["Certificado de Título", "Identificación de ocupantes o linderos conflictivos", "Levantamiento planimétrico del agrimensor (Evidencia técnica)"],
            'procedimientos': ["1. Preparar el plano de levantamiento o replanteo.", "2. Incoar la demanda en Reivindicación (o Deslinde) ante J.O.", "3. Probar la titularidad y la ocupación ilegal en audiencia."]
        }
    }

    # --- 2. INTERFAZ DE USUARIO ---
    with st.container(border=True):
        st.markdown("#### Depuración y Operaciones")
        
        c_cat, c_acc = st.columns(2)
        with c_cat:
            categoria_sel = st.selectbox("1. Categoría de la Actuación:", 
                                         ["Mensuras Catastrales", "Registro de Títulos", "Tribunales (Litis e Incidentes)", "Altas Cortes y Recursos", "Acciones Imprescriptibles"])
        
        acciones_filtradas = [k for k, v in catalogo_acciones.items() if v['cat'] == categoria_sel]
        
        with c_acc:
            accion_sel = st.selectbox("2. Actuación Legal o Técnica:", acciones_filtradas)
        
        datos_accion = catalogo_acciones[accion_sel]

        fecha_ref = None
        if datos_accion['tipo'] != 'imprescriptible':
            if accion_sel == 'Plazo Aviso de Mensura (Colindantes)':
                label_f = "Fecha proyectada para los trabajos de terreno:"
            elif accion_sel == 'Solicitud Fuerza Pública (Abogado del Estado)':
                label_f = "Fecha en que se notificó la intimación a desocupar:"
            else:
                label_f = "Fecha de inicio del cómputo (Depósito, Notificación o Título):"
                
            fecha_ref = st.date_input(label_f, value=date.today())
            st.info("⚠️ **Atención:** Para plazos procesales, el cálculo excluye fines de semana si la norma indica 'días hábiles' o francos. El sistema calcula en días calendario base.")

    # --- 3. MOTOR DE CÁLCULO Y RESULTADOS ---
    if st.button("🚀 Generar Ruta Crítica y Diagnóstico", type="primary", use_container_width=True):
        st.write("---")
        
        hoy = date.today()
        esta_prescrita = False
        texto_tiempo = ""
        limite_ley = "No aplica"

        if datos_accion['tipo'] == 'imprescriptible':
            color_badge = "#007bff"
            titulo_alerta = "🔵 ACCIÓN DE ORDEN PÚBLICO (IMPRESCRIPTIBLE)"
            texto_tiempo = "N/A"
            diag_final = datos_accion['diagnosticoAprobado']
        else:
            limite_ley = f"{datos_accion['plazo']} {datos_accion['unidad']}"
            
            if datos_accion['tipo'] == 'plazo_inverso':
                if fecha_ref < hoy:
                    st.error("❌ Error: Para avisos y desalojos, la fecha objetivo debe ser futura.")
                    st.stop()
                dias_faltantes = (fecha_ref - hoy).days
                esta_prescrita = dias_faltantes < datos_accion['plazo']
                texto_tiempo = f"Faltan {dias_faltantes} días para el evento"
                
            elif datos_accion['unidad'] == 'anos':
                anios_transcurridos = hoy.year - fecha_ref.year - ((hoy.month, hoy.day) < (fecha_ref.month, fecha_ref.day))
                esta_prescrita = anios_transcurridos >= datos_accion['plazo']
                texto_tiempo = f"{anios_transcurridos} años completos"
                
            elif datos_accion['unidad'] == 'dias':
                dias_transcurridos = (hoy - fecha_ref).days
                esta_prescrita = dias_transcurridos > datos_accion['plazo']
                texto_tiempo = f"{dias_transcurridos} días transcurridos"

            if esta_prescrita:
                color_badge = "#dc3545"
                titulo_alerta = "🔴 PLAZO VENCIDO / CADUCIDAD"
                diag_final = datos_accion['diagnosticoRechazado']
            else:
                color_badge = "#28a745"
                titulo_alerta = "🟢 DENTRO DEL PLAZO LEGAL / ACTIVO"
                diag_final = datos_accion['diagnosticoAprobado']

        # --- 4. RENDERIZADO DEL DICTAMEN ---
        with st.container(border=True):
            st.markdown(f"<h2 style='text-align: center; color: #0d253f; font-family: serif;'>DICTAMEN TÉCNICO-LEGAL</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: gray; font-size: 0.85rem;'>Expedido vía plataforma automatizada • {hoy.strftime('%d de %B de %Y')}</p>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style='background-color: {color_badge}20; color: {color_badge}; border: 1px solid {color_badge}; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 1.1rem; margin-bottom: 20px;'>
                {titulo_alerta}
            </div>
            """, unsafe_allow_html=True)

            if datos_accion['tipo'] != 'imprescriptible':
                st.markdown(f"**Tiempo medido:** {texto_tiempo}")
                st.markdown(f"**Límite normativo:** {limite_ley}")
            
            st.markdown(f"**Diagnóstico:** <span style='color: #0d253f; font-size: 1.1rem; font-weight: bold;'>{diag_final}</span>", unsafe_allow_html=True)
            st.markdown(f"**Acción a tomar:** {datos_accion['estrategia']}")
            
            st.write("---")
            
            c_req, c_proc = st.columns(2)
            with c_req:
                st.markdown("#### 📌 Requisitos Documentales")
                for req in datos_accion['requisitos']:
                    st.markdown(f"- {req}")
            with c_proc:
                st.markdown("#### ⚙️ Procedimiento (Ruta Crítica)")
                for proc in datos_accion['procedimientos']:
                    st.markdown(f"{proc}")
            
            st.write("---")
            st.info(f"**⚖️ Normativa Legal:** {datos_accion['baseLegal']}\n\n**🏛️ Jurisprudencia:** {datos_accion['jurisprudencia']}")
            
            st.markdown(f"""
            <div style="margin-top: 20px; text-align: right; font-size: 0.95rem; color: #333;">
                <div style="font-family: serif; font-size: 1.4rem; color: #c5a059; font-weight: bold; margin-bottom: 5px;">ABOAGRIM</div>
                <strong>Lic. Jhonny Matos, M.A.</strong><br>
                <span style="color: #0d253f; font-weight: 600;">Presidente | Abogado y Agrimensor</span><br>
                <span style="color: gray; font-size: 0.85rem;">Tel: 829-826-5888</span>
            </div>
            """, unsafe_allow_html=True)

        # --- 5. BOTÓN DE EXPORTACIÓN (Instrucción visual) ---
        st.write("")
        if st.button("🖨️ Exportar Dictamen a PDF", use_container_width=True):
            st.toast("⌨️ Presione Ctrl + P en su teclado para abrir el menú de impresión o guardado PDF.", icon="🖨️")
            st.success("💡 **Instrucción para el equipo:** Presione **`Ctrl + P`** (o `Cmd + P` en Mac) y seleccione **Guardar como PDF** en la ventana que aparecerá en su navegador.")
def vista_plantillas():
    import streamlit as st
    import os
    from datetime import datetime

    st.title("📄 Motor de Redacción y Plantillas")
    st.markdown("### *AboAgrim Pro: Sistema Experto de Forja Documental*")

    # --- 0. INICIALIZACIÓN DE MEMORIA DINÁMICA GLOBAL ---
    roles_dinamicos = ["cant_ab", "cant_ag", "cant_no", "cant_al", "cant_cl", "cant_ap", "cant_in", "cant_pg", "cant_de"]
    for rol in roles_dinamicos:
        if rol not in st.session_state:
            st.session_state[rol] = 1

    def mod_cant(rol, operacion):
        if operacion == "add":
            st.session_state[rol] += 1
        elif operacion == "del" and st.session_state[rol] > 0:
            st.session_state[rol] -= 1

    carpetas_base = ["1_mensuras_catastrales", "2_jurisdiccion_original", "3_registro_titulos"]
    if not os.path.exists("plantillas_maestras"):
        os.makedirs("plantillas_maestras")
    for c in carpetas_base:
        if not os.path.exists(os.path.join("plantillas_maestras", c)):
            os.makedirs(os.path.join("plantillas_maestras", c))

    tab_redaccion, tab_boveda = st.tabs(["⚙️ Taller de Redacción (Generar)", "📂 Bóveda de Modelos (Administrar)"])

    with tab_redaccion:
        lista_exps = ["-- Expediente Independiente --"] + list(st.session_state.get("db_expedientes", {}).keys())
            
        col_sel1, col_sel2 = st.columns([1, 2])
        with col_sel1:
            exp_seleccionado = st.selectbox("Vincular a Expediente:", lista_exps)
        with col_sel2:
            organo_ji = st.selectbox("Órgano Destino (Buscar Plantilla en):", ["Mensuras Catastrales", "Jurisdicción Original", "Registro de Títulos"])

        st.write("---")
        
        # --- 1. PARTES Y REPRESENTANTES (DINÁMICO) ---
        with st.expander("👥 1. Partes, Clientes y Representantes", expanded=True):
            t_cli, t_apo = st.tabs(["👤 Clientes / Propietarios", "🤝 Apoderados / Representantes"])
            
            with t_cli:
                c_btn1, c_btn2 = st.columns([1, 4])
                c_btn1.button("➕ Agregar Cliente", on_click=mod_cant, args=("cant_cl", "add"), key="add_cl")
                c_btn2.button("➖ Quitar", on_click=mod_cant, args=("cant_cl", "del"), key="del_cl")
                
                lista_clientes = []
                for i in range(st.session_state["cant_cl"]):
                    st.markdown(f"**Cliente {i+1}**")
                    c1, c2, c3 = st.columns(3)
                    n = c1.text_input("Nombre / Razón Social:", key=f"cl_n_{i}")
                    c = c2.text_input("Cédula / RNC:", key=f"cl_c_{i}")
                    t = c3.text_input("Teléfono(s):", key=f"cl_t_{i}")
                    c4, c5 = st.columns([2, 1])
                    d = c4.text_input("Domicilio Exacto:", key=f"cl_d_{i}")
                    e = c5.text_input("Correo Electrónico:", key=f"cl_e_{i}")
                    if n: lista_clientes.append({"nombre": n, "cedula": c, "telefono": t, "domicilio": d, "email": e})

            with t_apo:
                c_btn1, c_btn2 = st.columns([1, 4])
                c_btn1.button("➕ Agregar Apoderado", on_click=mod_cant, args=("cant_ap", "add"), key="add_ap")
                c_btn2.button("➖ Quitar", on_click=mod_cant, args=("cant_ap", "del"), key="del_ap")
                
                lista_apoderados = []
                for i in range(st.session_state["cant_ap"]):
                    st.markdown(f"**Apoderado {i+1}**")
                    c1, c2, c3 = st.columns(3)
                    n = c1.text_input("Nombre Completo:", key=f"ap_n_{i}")
                    c = c2.text_input("Cédula:", key=f"ap_c_{i}")
                    q = c3.text_input("Calidad (Ej. Poder Especial):", key=f"ap_q_{i}")
                    c4, c5 = st.columns([2, 1])
                    d = c4.text_input("Domicilio:", key=f"ap_d_{i}")
                    t = c5.text_input("Teléfono / Email:", key=f"ap_te_{i}")
                    if n: lista_apoderados.append({"nombre": n, "cedula": c, "calidad": q, "domicilio": d, "contacto": t})

        # --- 2. PROFESIONALES (DINÁMICO CON TELÉFONOS/EMAIL) ---
        with st.expander("⚖️ 2. Profesionales Actuantes", expanded=False):
            t_abo, t_agr, t_not, t_alg = st.tabs(["💼 Abogados", "📐 Agrimensores", "✒️ Notarios", "⚖️ Alguaciles"])

            with t_abo:
                c_btn1, c_btn2 = st.columns([1, 4])
                c_btn1.button("➕ Agregar Abogado", on_click=mod_cant, args=("cant_ab", "add"), key="add_ab")
                c_btn2.button("➖ Quitar", on_click=mod_cant, args=("cant_ab", "del"), key="del_ab")
                lista_abogados = []
                for i in range(st.session_state["cant_ab"]):
                    c1, c2, c3 = st.columns(3)
                    n = c1.text_input("Nombre:", key=f"ab_n_{i}")
                    c = c2.text_input("Cédula:", key=f"ab_c_{i}")
                    m = c3.text_input("CARD:", key=f"ab_m_{i}")
                    c4, c5, c6 = st.columns(3)
                    d = c4.text_input("Estudio/Domicilio:", key=f"ab_d_{i}")
                    t = c5.text_input("Teléfono:", key=f"ab_t_{i}")
                    e = c6.text_input("Email:", key=f"ab_e_{i}")
                    if n: lista_abogados.append({"nombre": n, "cedula": c, "matricula": m, "domicilio": d, "telefono": t, "email": e})

            with t_agr:
                c_btn1, c_btn2 = st.columns([1, 4])
                c_btn1.button("➕ Agregar Agrimensor", on_click=mod_cant, args=("cant_ag", "add"), key="add_ag")
                c_btn2.button("➖ Quitar", on_click=mod_cant, args=("cant_ag", "del"), key="del_ag")
                lista_agrimensores = []
                for i in range(st.session_state["cant_ag"]):
                    c1, c2, c3 = st.columns(3)
                    n = c1.text_input("Nombre:", key=f"ag_n_{i}")
                    c = c2.text_input("Cédula:", key=f"ag_c_{i}")
                    m = c3.text_input("CODIA:", key=f"ag_m_{i}")
                    c4, c5, c6 = st.columns(3)
                    d = c4.text_input("Oficina:", key=f"ag_d_{i}")
                    t = c5.text_input("Teléfono:", key=f"ag_t_{i}")
                    e = c6.text_input("Email:", key=f"ag_e_{i}")
                    if n: lista_agrimensores.append({"nombre": n, "cedula": c, "matricula": m, "domicilio": d, "telefono": t, "email": e})

            with t_not:
                c_btn1, c_btn2 = st.columns([1, 4])
                c_btn1.button("➕ Agregar Notario", on_click=mod_cant, args=("cant_no", "add"), key="add_no")
                c_btn2.button("➖ Quitar", on_click=mod_cant, args=("cant_no", "del"), key="del_no")
                lista_notarios = []
                for i in range(st.session_state["cant_no"]):
                    c1, c2, c3 = st.columns(3)
                    n = c1.text_input("Nombre:", key=f"no_n_{i}")
                    c = c2.text_input("Cédula:", key=f"no_c_{i}")
                    m = c3.text_input("Matrícula:", key=f"no_m_{i}")
                    c4, c5, c6 = st.columns(3)
                    d = c4.text_input("Jurisdicción:", key=f"no_d_{i}")
                    t = c5.text_input("Teléfono:", key=f"no_t_{i}")
                    e = c6.text_input("Email:", key=f"no_e_{i}")
                    if n: lista_notarios.append({"nombre": n, "cedula": c, "matricula": m, "domicilio": d, "telefono": t, "email": e})

            with t_alg:
                c_btn1, c_btn2 = st.columns([1, 4])
                c_btn1.button("➕ Agregar Alguacil", on_click=mod_cant, args=("cant_al", "add"), key="add_al")
                c_btn2.button("➖ Quitar", on_click=mod_cant, args=("cant_al", "del"), key="del_al")
                lista_alguaciles = []
                for i in range(st.session_state["cant_al"]):
                    c1, c2, c3 = st.columns(3)
                    n = c1.text_input("Nombre:", key=f"al_n_{i}")
                    c = c2.text_input("Cédula:", key=f"al_c_{i}")
                    m = c3.text_input("Tribunal:", key=f"al_m_{i}")
                    c4, c5 = st.columns([2, 1])
                    d = c4.text_input("Domicilio:", key=f"al_d_{i}")
                    t = c5.text_input("Teléfono:", key=f"al_t_{i}")
                    if n: lista_alguaciles.append({"nombre": n, "cedula": c, "matricula": m, "domicilio": d, "telefono": t})

        # --- 3. INMUEBLES (DINÁMICO CON LIBROS, FOLIOS, COORDENADAS) ---
        with st.expander("📍 3. Inmuebles y Sustentos Legales", expanded=False):
            c_btn1, c_btn2 = st.columns([1, 4])
            c_btn1.button("➕ Agregar Inmueble", on_click=mod_cant, args=("cant_in", "add"), key="add_in")
            c_btn2.button("➖ Quitar", on_click=mod_cant, args=("cant_in", "del"), key="del_in")
            
            lista_inmuebles = []
            for i in range(st.session_state["cant_in"]):
                st.markdown(f"**Inmueble / Parcela {i+1}**")
                c1, c2, c3 = st.columns(3)
                p = c1.text_input("Parcela/Solar:", key=f"in_p_{i}")
                dc = c2.text_input("DC / Municipio:", key=f"in_dc_{i}")
                prov = c3.text_input("Provincia:", key=f"in_prov_{i}")
                
                c4, c5, c6 = st.columns(3)
                coord = c4.text_input("Coordenadas (UTM/Geográficas):", key=f"in_co_{i}")
                sup = c5.text_input("Superficie:", key=f"in_sup_{i}")
                tdoc = c6.selectbox("Tipo de Documento Base:", ["Certificado de Título", "Constancia Anotada", "Acto de Venta", "Otro"], key=f"in_td_{i}")
                
                c7, c8, c9, c10 = st.columns(4)
                num = c7.text_input("Matrícula/Número:", key=f"in_n_{i}")
                lib = c8.text_input("Libro:", key=f"in_l_{i}")
                fol = c9.text_input("Folio:", key=f"in_f_{i}")
                f_ins = c10.text_input("Fecha Inscripción:", key=f"in_fi_{i}")
                
                if p: lista_inmuebles.append({"parcela": p, "dc": dc, "provincia": prov, "coord": coord, "superficie": sup, "tipo_doc": tdoc, "numero": num, "libro": lib, "folio": fol, "fecha_ins": f_ins})

        # --- 4. TRANSACCIONES (DINÁMICO) ---
        with st.expander("💰 4. Datos Transaccionales y Testigos", expanded=False):
            c_btn1, c_btn2 = st.columns([1, 4])
            c_btn1.button("➕ Agregar Pago/Transacción", on_click=mod_cant, args=("cant_pg", "add"), key="add_pg")
            c_btn2.button("➖ Quitar", on_click=mod_cant, args=("cant_pg", "del"), key="del_pg")
            
            lista_pagos = []
            for i in range(st.session_state["cant_pg"]):
                c1, c2, c3 = st.columns(3)
                m = c1.text_input("Monto / Precio:", key=f"pg_m_{i}")
                f = c2.text_input("Forma de Pago (Cheque, Transferencia):", key=f"pg_f_{i}")
                b = c3.text_input("Banco o Detalle:", key=f"pg_b_{i}")
                if m: lista_pagos.append({"monto": m, "forma": f, "banco": b})
            
            st.write("---")
            testigos = st.text_area("Testigos Instrumentales (Nombres, Cédulas y Domicilios separados por comas):", height=68)

        # --- 5. DEPOSITANTES Y REQUISITOS (DINÁMICO) ---
        with st.expander("📝 5. Depositantes, Impuestos y Requisitos (JI)", expanded=False):
            c_btn1, c_btn2 = st.columns([1, 4])
            c_btn1.button("➕ Agregar Tramitante", on_click=mod_cant, args=("cant_de", "add"), key="add_de")
            c_btn2.button("➖ Quitar", on_click=mod_cant, args=("cant_de", "del"), key="del_de")
            
            lista_depositantes = []
            for i in range(st.session_state["cant_de"]):
                c1, c2, c3 = st.columns(3)
                n = c1.text_input("Nombre del Tramitante:", key=f"de_n_{i}")
                c = c2.text_input("Cédula:", key=f"de_c_{i}")
                q = c3.text_input("Calidad (Gestor, etc.):", key=f"de_q_{i}")
                c4, c5 = st.columns(2)
                t = c4.text_input("Teléfono:", key=f"de_t_{i}")
                e = c5.text_input("Email:", key=f"de_e_{i}")
                if n: lista_depositantes.append({"nombre": n, "cedula": c, "calidad": q, "telefono": t, "email": e})
            
            st.write("---")
            impuestos_pagados = st.multiselect("Impuestos, Tasas y Sellos:", ["Recibo de Ley 108-05 (JI)", "Sello de Ley 33-91 (CARD)", "Recibo CODIA", "Impuesto DGII", "Recibo Ley 196", "Poder Legalizado PGR"])
            inventario_anexos = st.text_area("Lista de Anexos Físicos:", height=100)

        st.write("---")
        
        # --- MOTOR DE COMPILACIÓN Y FABRICACIÓN ---
        mapping_carpetas = {"Mensuras Catastrales": "1_mensuras_catastrales", "Jurisdicción Original": "2_jurisdiccion_original", "Registro de Títulos": "3_registro_titulos"}
        ruta_carpeta = os.path.join("plantillas_maestras", mapping_carpetas[organo_ji])
        
        if os.path.exists(ruta_carpeta):
            opciones = [f for f in os.listdir(ruta_carpeta) if f.endswith(".docx")]
            plantillas_elegidas = st.multiselect("📑 Seleccione la(s) plantilla(s) a forjar:", opciones)
            
            if st.button("🚀 FORJAR DOCUMENTO AHORA", type="primary", use_container_width=True):
                if plantillas_elegidas:
                    
                    # === GENERADORES DE PÁRRAFOS AUTOMÁTICOS ===
                    cl_nombres = " y ".join([c['nombre'] for c in lista_clientes]) if lista_clientes else "N/A"
                    cl_generales = "; y ".join([f"{c['nombre']}, dominicano(a), mayor de edad, portador(a) de la cédula No. {c['cedula']}, domiciliado(a) en {c['domicilio']}, Tel: {c['telefono']}, Email: {c['email']}" for c in lista_clientes]) if lista_clientes else "N/A"
                    
                    ap_nombres = " y ".join([a['nombre'] for a in lista_apoderados]) if lista_apoderados else "N/A"
                    ap_generales = "; y ".join([f"{a['nombre']}, dominicano(a), mayor de edad, portador(a) de la cédula No. {a['cedula']}, actuando en calidad de {a['calidad']}, con domicilio en {a['domicilio']}, Contacto: {a['contacto']}" for a in lista_apoderados]) if lista_apoderados else "N/A"

                    ab_nombres = " y ".join([a['nombre'] for a in lista_abogados]) if lista_abogados else "N/A"
                    ab_generales = "; y ".join([f"{a['nombre']}, portador(a) de la cédula No. {a['cedula']}, CARD {a['matricula']}, estudio en {a['domicilio']}, Tel: {a['telefono']}, Email: {a['email']}" for a in lista_abogados]) if lista_abogados else "N/A"
                    
                    ag_nombres = " y ".join([a['nombre'] for a in lista_agrimensores]) if lista_agrimensores else "N/A"
                    ag_generales = "; y ".join([f"{a['nombre']}, cédula No. {a['cedula']}, CODIA {a['matricula']}, oficina en {a['domicilio']}, Tel: {a['telefono']}, Email: {a['email']}" for a in lista_agrimensores]) if lista_agrimensores else "N/A"
                    
                    no_nombres = " y ".join([a['nombre'] for a in lista_notarios]) if lista_notarios else "N/A"
                    no_generales = "; y ".join([f"{a['nombre']}, Notario de {a['domicilio']}, Matrícula {a['matricula']}, cédula No. {a['cedula']}, Tel: {a['telefono']}" for a in lista_notarios]) if lista_notarios else "N/A"
                    
                    al_nombres = " y ".join([a['nombre'] for a in lista_alguaciles]) if lista_alguaciles else "N/A"
                    al_generales = "; y ".join([f"{a['nombre']}, cédula No. {a['cedula']}, Alguacil del {a['matricula']}, Tel: {a['telefono']}" for a in lista_alguaciles]) if lista_alguaciles else "N/A"

                    in_descripciones = "\n".join([f"Parcela {i['parcela']}, DC {i['dc']}, {i['provincia']}. Superficie: {i['superficie']}. Coordenadas: {i['coord']}. Sustentado en {i['tipo_doc']} No. {i['numero']}, Libro {i['libro']}, Folio {i['folio']}, inscrito en fecha {i['fecha_ins']}." for i in lista_inmuebles]) if lista_inmuebles else "N/A"

                    pg_detalles = "\n".join([f"Monto de {p['monto']} pagadero mediante {p['forma']} ({p['banco']})." for p in lista_pagos]) if lista_pagos else "N/A"
                    
                    de_nombres = " y ".join([d['nombre'] for d in lista_depositantes]) if lista_depositantes else "N/A"
                    de_generales = "; y ".join([f"{d['nombre']}, portador(a) de la cédula No. {d['cedula']}, en calidad de {d['calidad']}, Tel: {d['telefono']}, Email: {d['email']}" for d in lista_depositantes]) if lista_depositantes else "N/A"

                    impuestos_str = ", ".join(impuestos_pagados) if impuestos_pagados else "N/A"
                    
                    datos_para_word = {
                        "expediente": exp_seleccionado, "fecha_hoy": datetime.now().strftime("%d de %B del %Y"),
                        "clientes_nombres": cl_nombres, "clientes_generales": cl_generales,
                        "apoderados_nombres": ap_nombres, "apoderados_generales": ap_generales,
                        "abogados_nombres": ab_nombres, "abogados_generales": ab_generales,
                        "agrimensores_nombres": ag_nombres, "agrimensores_generales": ag_generales,
                        "notarios_nombres": no_nombres, "notarios_generales": no_generales,
                        "alguaciles_nombres": al_nombres, "alguaciles_generales": al_generales,
                        "inmuebles_detalle": in_descripciones,
                        "pagos_detalle": pg_detalles, "testigos": testigos,
                        "depositantes_nombres": de_nombres, "depositantes_generales": de_generales,
                        "impuestos_pagados": impuestos_str, "inventario_anexos": inventario_anexos
                    }
                    
                    archivos_generados = 0
                    for p in plantillas_elegidas:
                        buffer = generar_documento_word(os.path.join(ruta_carpeta, p), datos_para_word)
                        if buffer:
                            prefijo = exp_seleccionado if exp_seleccionado != "-- Expediente Independiente --" else "Doc"
                            st.download_button(label=f"⬇️ Descargar: {p}", data=buffer, file_name=f"{prefijo}_{p}")
                            archivos_generados += 1
                    if archivos_generados > 0:
                        st.success(f"⚖️ ¡Impecable! Se redactaron {archivos_generados} documentos.")

    with tab_boveda:
        st.subheader("Gestión de Archivos Maestros (.docx)")
        
        # 🛡️ VERIFICACIÓN DE SEGURIDAD (SOLO ADMIN PUEDE SUBIR)
        if st.session_state.get("rol_actual") == "Administrador":
            col_up1, col_up2 = st.columns([2, 3])
            with col_up1:
                destino = st.selectbox("Cargar en:", carpetas_base)
            with col_up2:
                archivos_subidos = st.file_uploader("Arrastrar Plantillas Nuevas", type=["docx"], accept_multiple_files=True)

            if archivos_subidos:
                for archivo in archivos_subidos:
                    with open(os.path.join("plantillas_maestras", destino, archivo.name), "wb") as f:
                        f.write(archivo.getbuffer())
                st.success("✅ Plantillas guardadas en la bóveda.")
                st.rerun()

            st.divider()
            st.write("**Borrar Plantillas Existentes**")
            cat_ver = st.selectbox("Revisar categoría:", carpetas_base)
            ruta_ver = os.path.join("plantillas_maestras", cat_ver)
            if os.path.exists(ruta_ver):
                archivos_en_cat = [f for f in os.listdir(ruta_ver) if f.endswith(".docx")]
                if archivos_en_cat:
                    c_del1, c_del2 = st.columns([3, 1])
                    archivo_borrar = c_del1.selectbox("Seleccione para eliminar:", archivos_en_cat)
                    if c_del2.button("🔥 Eliminar Modelo"):
                        os.remove(os.path.join(ruta_ver, archivo_borrar))
                        st.rerun()
        else:
            st.error("⛔ Acceso Denegado: Nivel de autorización insuficiente.")
            st.warning("Solo el Administrador General (Lic. Jhonny Matos) tiene permisos para alterar las plantillas estratégicas.")

def vista_honorarios():
    import streamlit as st
    import streamlit.components.v1 as components
    from datetime import datetime

    st.title("💳 Gestión de Honorarios y Facturación")
    st.markdown("### *Cotizaciones y Facturas Proforma de AboAgrim*")

    # --- 1. MEMORIA PARA ITEMS DINÁMICOS ---
    if "cant_items_fac" not in st.session_state:
        st.session_state["cant_items_fac"] = 1
    if "contador_factura" not in st.session_state:
        st.session_state["contador_factura"] = 1

    def mod_items(operacion):
        if operacion == "add":
            st.session_state["cant_items_fac"] += 1
        elif operacion == "del" and st.session_state["cant_items_fac"] > 1:
            st.session_state["cant_items_fac"] -= 1

    # --- 2. VINCULACIÓN CON EXPEDIENTES ---
    lista_exps = ["-- Factura Independiente --"] + list(st.session_state.get("db_expedientes", {}).keys())
    
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        exp_seleccionado = st.selectbox("Vincular a Expediente:", lista_exps)
    with col_sel2:
        tipo_documento = st.radio("Tipo de Documento:", ["Cotización", "Factura Proforma", "Factura de Honorarios"], horizontal=True)

    st.write("---")

    # --- 3. DATOS DEL CLIENTE Y FACTURA ---
    with st.expander("👤 Datos del Cliente y Comprobante", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            cliente_nombre = st.text_input("A nombre de (Cliente / Empresa):")
            cliente_rnc = st.text_input("RNC / Cédula:")
            cliente_dir = st.text_input("Dirección del Cliente:")
        with c2:
            fecha_fac = st.date_input("Fecha de Emisión:")
            num_factura = st.text_input("Número de Documento:", value=f"FAC-{datetime.now().year}-{st.session_state['contador_factura']:04d}")
            ncf = st.text_input("NCF (Opcional, si aplica):", placeholder="Ej. B0200000001")

    # --- 4. ITEMS DE FACTURACIÓN (DINÁMICO) ---
    with st.expander("🛒 Conceptos y Servicios (Agregar/Quitar)", expanded=True):
        c_btn1, c_btn2 = st.columns([1, 4])
        c_btn1.button("➕ Agregar Concepto", on_click=mod_items, args=("add",), key="add_item")
        c_btn2.button("➖ Quitar", on_click=mod_items, args=("del",), key="del_item")
        
        lista_conceptos = []
        subtotal = 0.0
        
        for i in range(st.session_state["cant_items_fac"]):
            c1, c2, c3 = st.columns([3, 1, 1])
            desc = c1.text_input(f"Descripción del Servicio {i+1}:", key=f"item_d_{i}", placeholder="Ej. Honorarios por Saneamiento, Tasa DGII...")
            cant = c2.number_input(f"Cantidad:", min_value=1, value=1, key=f"item_c_{i}")
            precio = c3.number_input(f"Precio Unitario (RD$):", min_value=0.0, value=0.0, format="%.2f", key=f"item_p_{i}")
            
            if desc and precio > 0:
                total_linea = cant * precio
                subtotal += total_linea
                lista_conceptos.append({"desc": desc, "cant": cant, "precio": precio, "total": total_linea})

    # --- 5. IMPUESTOS Y TOTALES ---
    with st.expander("📊 Impuestos y Retenciones", expanded=True):
        c_tax1, c_tax2, c_tax3 = st.columns(3)
        aplicar_itbis = c_tax1.checkbox("Sumar ITBIS (18%)", value=False)
        aplicar_isr = c_tax2.checkbox("Retención ISR (10% Profesionales)", value=False)
        aplicar_ret_itbis = c_tax3.checkbox("Retención ITBIS (100% o 30%)", value=False)
        
        notas_factura = st.text_area("Notas / Términos de Pago:", value="El pago del 50% es requerido para iniciar los trabajos. Los gastos de impuestos y tasas registrales no incluyen ITBIS.")

        # Cálculos Matemáticos
        itbis = subtotal * 0.18 if aplicar_itbis else 0.0
        isr = subtotal * 0.10 if aplicar_isr else 0.0
        # Simplificación: Si retienen ITBIS, asumimos el 100% del ITBIS generado si es entre empresas, o ajustable. 
        # Para honorarios jurídicos a empresas suele ser el 100% del ITBIS.
        ret_itbis = itbis if aplicar_ret_itbis else 0.0
        
        total_neto = subtotal + itbis - isr - ret_itbis

    st.write("---")

    # --- 6. GENERADOR DEL DISEÑO WEB PREMIUM (HTML) ---
    if st.button("👁️ Generar Vista Previa de la Factura", type="primary", use_container_width=True):
        
        # Construcción de las filas de la tabla HTML
        filas_html = ""
        for item in lista_conceptos:
            filas_html += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 12px; text-align: left;">{item['desc']}</td>
                <td style="padding: 12px; text-align: center;">{item['cant']}</td>
                <td style="padding: 12px; text-align: right;">RD$ {item['precio']:,.2f}</td>
                <td style="padding: 12px; text-align: right; color: #1E3A8A; font-weight: bold;">RD$ {item['total']:,.2f}</td>
            </tr>
            """
            
        # Bloque de Impuestos Condicional en HTML
        impuestos_html = ""
        if aplicar_itbis: impuestos_html += f"<tr><td colspan='3' style='text-align: right; padding: 5px 12px;'><strong>ITBIS (18%):</strong></td><td style='text-align: right; padding: 5px 12px;'>RD$ {itbis:,.2f}</td></tr>"
        if aplicar_isr: impuestos_html += f"<tr><td colspan='3' style='text-align: right; padding: 5px 12px; color: #dc3545;'><strong>Retención ISR (10%):</strong></td><td style='text-align: right; padding: 5px 12px; color: #dc3545;'>- RD$ {isr:,.2f}</td></tr>"
        if aplicar_ret_itbis: impuestos_html += f"<tr><td colspan='3' style='text-align: right; padding: 5px 12px; color: #dc3545;'><strong>Retención ITBIS:</strong></td><td style='text-align: right; padding: 5px 12px; color: #dc3545;'>- RD$ {ret_itbis:,.2f}</td></tr>"

        # PLANTILLA MAESTRA HTML / CSS
        html_factura = f"""
        <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; max-width: 800px; margin: auto; padding: 40px; border: 1px solid #ddd; box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.1); background-color: white; border-top: 8px solid #1E3A8A;">
            
            <!-- ENCABEZADO CORPORATIVO -->
            <table style="width: 100%; margin-bottom: 30px;">
                <tr>
                    <td style="width: 50%;">
                        <h1 style="color: #1E3A8A; margin: 0; font-size: 32px; font-weight: 900; letter-spacing: 1px;">ABOAGRIM</h1>
                        <p style="color: #FBBF24; margin: 0; font-size: 14px; font-weight: bold; text-transform: uppercase;">Servicios Legales y Catastrales</p>
                        <p style="color: #666; margin: 5px 0 0 0; font-size: 12px;">Lic. Jhonny Matos, M.A.<br>Santiago, Rep. Dom.<br>Tel: 829-826-5888</p>
                    </td>
                    <td style="width: 50%; text-align: right; vertical-align: top;">
                        <h2 style="color: #333; margin: 0; font-size: 24px; text-transform: uppercase;">{tipo_documento}</h2>
                        <p style="color: #555; font-size: 14px; margin: 5px 0;"><strong>No:</strong> {num_factura}</p>
                        <p style="color: #555; font-size: 14px; margin: 0;"><strong>Fecha:</strong> {fecha_fac.strftime('%d/%m/%Y')}</p>
                        <p style="color: #555; font-size: 14px; margin: 5px 0;"><strong>NCF:</strong> {ncf if ncf else 'N/A'}</p>
                    </td>
                </tr>
            </table>
            
            <!-- DATOS DEL CLIENTE -->
            <div style="background-color: #f8fafc; padding: 15px; border-left: 4px solid #FBBF24; margin-bottom: 30px;">
                <p style="margin: 0 0 5px 0; font-size: 14px; color: #1E3A8A;"><strong>FACTURADO A:</strong></p>
                <h3 style="margin: 0 0 5px 0; color: #333; font-size: 18px;">{cliente_nombre if cliente_nombre else '_______________________'}</h3>
                <p style="margin: 0 0 5px 0; font-size: 14px; color: #555;"><strong>RNC/Cédula:</strong> {cliente_rnc}</p>
                <p style="margin: 0; font-size: 14px; color: #555;"><strong>Dirección:</strong> {cliente_dir}</p>
            </div>
            
            <!-- TABLA DE CONCEPTOS -->
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
                <thead>
                    <tr style="background-color: #1E3A8A; color: white;">
                        <th style="padding: 12px; text-align: left; font-size: 14px;">DESCRIPCIÓN DEL SERVICIO</th>
                        <th style="padding: 12px; text-align: center; font-size: 14px;">CANT.</th>
                        <th style="padding: 12px; text-align: right; font-size: 14px;">PRECIO UNIT.</th>
                        <th style="padding: 12px; text-align: right; font-size: 14px;">TOTAL</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
            
            <!-- TOTALES -->
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
                <tr>
                    <td style="width: 50%; vertical-align: top; padding-right: 20px;">
                        <p style="font-size: 12px; color: #666; background-color: #f1f5f9; padding: 10px; border-radius: 4px;"><strong>Términos y Condiciones:</strong><br>{notas_factura}</p>
                    </td>
                    <td style="width: 50%;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 14px; color: #333;">
                            <tr>
                                <td style="text-align: right; padding: 5px 12px;"><strong>Subtotal:</strong></td>
                                <td style="text-align: right; padding: 5px 12px;">RD$ {subtotal:,.2f}</td>
                            </tr>
                            {impuestos_html}
                            <tr style="background-color: #FBBF24; color: #1E3A8A; font-size: 18px;">
                                <td style="text-align: right; padding: 12px;"><strong>TOTAL NETO A PAGAR:</strong></td>
                                <td style="text-align: right; padding: 12px;"><strong>RD$ {total_neto:,.2f}</strong></td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
            
            <!-- PIE DE PÁGINA -->
            <div style="text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #888;">
                <p style="margin: 0;">Gracias por confiar en AboAgrim Pro.</p>
                <p style="margin: 0;">Firma de Abogados y Oficina de Agrimensura | Santiago, República Dominicana</p>
            </div>
        </div>
        """

        # Mostrar en pantalla la vista previa exacta
        st.markdown("### 📄 Vista Previa del Documento:")
        components.html(html_factura, height=900, scrolling=True)

        # Botón para descargar el HTML y guardarlo o imprimirlo
        st.success("✅ Diseño generado con éxito. Haga clic en el botón de abajo para descargar la factura. Una vez abierta en su navegador, presione `Ctrl + P` para guardarla como PDF o imprimirla.")
        
        st.download_button(
            label="⬇️ Descargar Factura (Lista para Imprimir/PDF)",
            data=html_factura,
            file_name=f"{num_factura}_{cliente_nombre.replace(' ', '_')}.html",
            mime="text/html",
            type="primary"
        )

def vista_configuracion():
    import streamlit as st
    
    st.title("⚙️ Configuración Maestra del Sistema")
    st.markdown("### 🎛️ Centro de Mando: Personalización y Seguridad")
    
    if st.session_state.get("rol_actual") != "Administrador":
        st.error("⛔ Acceso Denegado. Área exclusiva de la Presidencia.")
        return

    # Inicializar variables de marca si no existen
    if "color_primario" not in st.session_state: st.session_state["color_primario"] = "#1E3A8A"
    if "color_fondo" not in st.session_state: st.session_state["color_fondo"] = "#0E1117"
    if "tipo_letra" not in st.session_state: st.session_state["tipo_letra"] = "sans-serif"
    if "nombre_oficina" not in st.session_state: st.session_state["nombre_oficina"] = "OFICINA PRINCIPAL"
    if "dir_oficina" not in st.session_state: st.session_state["dir_oficina"] = "Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Centro Ciudad, Santiago."
    if "tel_oficina" not in st.session_state: st.session_state["tel_oficina"] = "829-826-5888 / 809-691-3333"

    # Dividimos la pantalla en 3 pestañas profesionales
    tab_usuarios, tab_apariencia, tab_oficina = st.tabs(["👥 Usuarios y Accesos", "🎨 Diseño y Marca", "🏢 Datos de la Firma"])
    
    with tab_usuarios:
        db = st.session_state["db_usuarios"]
        st.subheader("📋 Directorio de Usuarios Activos")
        for usr, datos in db.items():
            col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
            col1.write(f"**ID:** {usr}")
            col2.write(f"**Nombre:** {datos['nombre']}")
            col3.write(f"**Rol:** {datos['rol']}")
            with col4:
                if usr.lower() == "jmatos":
                    st.info("👑 Admin Principal")
                else:
                    if st.button("🗑️ Borrar", key=f"del_{usr}"):
                        del st.session_state["db_usuarios"][usr]
                        st.rerun()
        st.write("---")
        c_izq, c_der = st.columns(2)
        with c_izq:
            st.markdown("**➕ Agregar Personal**")
            nuevo_usr = st.text_input("ID de Usuario (Ej. asistente2):")
            nuevo_pass = st.text_input("Contraseña Temporal:", type="password")
            nuevo_nombre = st.text_input("Nombre Completo:")
            nuevo_rol = st.selectbox("Nivel de Acceso:", ["Usuario", "Administrador"])
            if st.button("💾 Inscribir", type="primary"):
                if nuevo_usr and nuevo_pass:
                    st.session_state["db_usuarios"][nuevo_usr] = {"pass": nuevo_pass, "rol": nuevo_rol, "nombre": nuevo_nombre}
                    st.success("✅ Usuario agregado.")
                    st.rerun()
        with c_der:
            st.markdown("**🔑 Cambiar Contraseñas**")
            usr_modificar = st.selectbox("Seleccione la cuenta:", list(db.keys()))
            nueva_clave = st.text_input("Escriba la Nueva Contraseña:", type="password")
            if st.button("🔄 Actualizar", type="primary"):
                if nueva_clave:
                    st.session_state["db_usuarios"][usr_modificar]["pass"] = nueva_clave
                    st.success("✅ Contraseña cambiada.")

    with tab_apariencia:
        st.subheader("🎨 Personalización Visual del Sistema")
        st.info("💡 Cambie los colores corporativos y la tipografía. Para ver los cambios, haga clic en Aplicar Diseño.")
        
        c_color1, c_color2 = st.columns(2)
        with c_color1:
            nuevo_primario = st.color_picker("Color Principal (Botones y Títulos):", st.session_state["color_primario"])
            nuevo_fondo = st.color_picker("Color de Fondo (Pantalla):", st.session_state["color_fondo"])
        with c_color2:
            nueva_letra = st.selectbox("Tipografía (Letra):", ["sans-serif", "serif", "monospace", "Arial", "Courier New", "Georgia"])
            logo_subido = st.file_uploader("Subir Logo de la Firma (PNG/JPG):", type=["png", "jpg", "jpeg"])
            
        if st.button("💾 Aplicar y Guardar Diseño", type="primary", use_container_width=True):
            st.session_state["color_primario"] = nuevo_primario
            st.session_state["color_fondo"] = nuevo_fondo
            st.session_state["tipo_letra"] = nueva_letra
            if logo_subido:
                st.session_state["logo_firma"] = logo_subido.getvalue()
            st.success("✅ Diseño actualizado. El sistema adoptará su marca ahora mismo.")
            st.rerun()

    with tab_oficina:
        st.subheader("🏢 Datos Oficiales de la Firma")
        st.markdown("Estos datos alimentarán automáticamente la barra lateral de su sistema.")
        
        nuevo_n_oficina = st.text_input("Nombre de la Firma / Oficina:", st.session_state["nombre_oficina"])
        nueva_dir = st.text_input("Dirección Principal:", st.session_state["dir_oficina"])
        nuevo_tel = st.text_input("Teléfonos de Contacto:", st.session_state["tel_oficina"])
        
        if st.button("💾 Guardar Datos Corporativos", type="primary", use_container_width=True):
            st.session_state["nombre_oficina"] = nuevo_n_oficina
            st.session_state["dir_oficina"] = nueva_dir
            st.session_state["tel_oficina"] = nuevo_tel
            st.success("✅ Datos corporativos actualizados.")
            st.rerun()

# ==========================================
# 🔒 SISTEMA DE SEGURIDAD Y LOGIN DINÁMICO
# ==========================================
if "db_usuarios" not in st.session_state:
    st.session_state["db_usuarios"] = {
        "Jmatos": {"pass": "0681", "rol": "Administrador", "nombre": "Lic. Jhonny Matos"},
        "asistente": {"pass": "abo123", "rol": "Usuario", "nombre": "Asistente Legal"}
    }

if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = None
    st.session_state["rol_actual"] = None

if st.session_state["usuario_actual"] is None:
    st.markdown("<br><br><h2 style='text-align: center; color: #1E3A8A;'>🔒 Acceso Restringido</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>AboAgrim Pro - Sistema de Gestión Integral</p>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.container(border=True):
            usuario_input = st.text_input("👤 Usuario:")
            pass_input = st.text_input("🔑 Contraseña:", type="password")
            
            if st.button("Iniciar Sesión", use_container_width=True, type="primary"):
                db = st.session_state["db_usuarios"]
                usuario_valido = next((u for u in db if u.lower() == usuario_input.lower()), None)
                
                if usuario_valido and db[usuario_valido]["pass"] == pass_input:
                    st.session_state["usuario_actual"] = usuario_valido
                    st.session_state["rol_actual"] = db[usuario_valido]["rol"]
                    st.session_state["nombre_usuario"] = db[usuario_valido]["nombre"]
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas. Sistema bloqueado.")
    st.stop()

# ==========================================
# 🎨 APLICADOR DE DISEÑO GLOBAL
# ==========================================
if "color_primario" in st.session_state:
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {st.session_state["color_fondo"]};
            font-family: {st.session_state["tipo_letra"]};
        }}
        .stButton>button[kind="primary"] {{
            background-color: {st.session_state["color_primario"]};
            border-color: {st.session_state["color_primario"]};
        }}
        h1, h2, h3 {{
            color: {st.session_state["color_primario"]} !important;
            font-family: {st.session_state["tipo_letra"]};
        }}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 📱 MENÚ LATERAL AUTORIZADO Y PERFIL
# ==========================================
with st.sidebar:
    # Si subió un logo en configuración, lo mostramos en todo lo alto del menú
    if st.session_state.get("logo_firma"):
        st.image(st.session_state["logo_firma"], use_container_width=True)
        st.divider()

    st.markdown(f"### 🧑‍💼 {st.session_state['nombre_usuario']}")
    st.caption(f"🛡️ Nivel de acceso: **{st.session_state['rol_actual']}**")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["usuario_actual"] = None
        st.session_state["rol_actual"] = None
        st.rerun()
    
    st.write("---")
    st.markdown("**Navegación:**")
    
    opciones_menu = ["🏠 Mando Central", "👤 Registro Maestro", "📁 Archivo Digital", "📄 Plantillas Auto", "⏱️ Alertas y Plazos"]
    
    if st.session_state["rol_actual"] == "Administrador":
        opciones_menu.extend(["💳 Gestión de Honorarios", "⚙️ Configuración"])
        
    menu = st.radio("Módulos", opciones_menu, label_visibility="collapsed")

    st.write("---")
    
    # Datos de la firma extraídos de la configuración en tiempo real
    st.markdown(f"### 🏢 {st.session_state.get('nombre_oficina', 'OFICINA PRINCIPAL')}")
    st.markdown(f"📍 {st.session_state.get('dir_oficina', 'Santiago')}")
    st.markdown(f"📞 {st.session_state.get('tel_oficina', '829-826-5888 / 809-691-3333')}")
    st.markdown("**Lic. Jhonny Matos. M.A.**\n*(Presidente-Fundador)*")

# ==========================================
# 🚀 EJECUCIÓN DE MÓDULOS
# ==========================================
if menu == "🏠 Mando Central":
    vista_mando()
elif menu == "👤 Registro Maestro":
    vista_registro_maestro()
elif menu == "📁 Archivo Digital":
    vista_archivo_digital()
elif menu == "📄 Plantillas Auto":
    vista_plantillas()
elif menu == "⏱️ Alertas y Plazos":
    vista_alertas_plazos()
elif menu == "💳 Gestión de Honorarios":
    vista_honorarios()
elif menu == "⚙️ Configuración":
    vista_configuracion()
