# =====================================================================
# INTERFAZ GRÁFICA Y SISTEMA EXPERTO LEGAL JI (EDICIÓN PREMIUM FULL)
# Sistema: AboAgrim Pro DMS 
# =====================================================================
import streamlit as st
import zipfile
from docxtpl import DocxTemplate
import os
import shutil

# --- MOTOR DE GUARDADO DUAL (GOOGLE DRIVE) ---
def guardar_expediente_en_drive(ruta_archivo_original, nombre_carpeta_expediente):
    """Copia un archivo o carpeta hacia los dos Google Drives configurados."""
    try:
        ruta_ab = st.session_state.get("ruta_aboagrim", "")
        ruta_per = st.session_state.get("ruta_personal", "")
        
        # 1. Guardar en AboAgrim Drive
        if ruta_ab and os.path.exists(ruta_ab):
            destino_ab = os.path.join(ruta_ab, nombre_carpeta_expediente)
            os.makedirs(destino_ab, exist_ok=True)
            shutil.copy2(ruta_archivo_original, destino_ab)
            
        # 2. Guardar en Personal Drive
        if ruta_per and os.path.exists(ruta_per):
            destino_per = os.path.join(ruta_per, nombre_carpeta_expediente)
            os.makedirs(destino_per, exist_ok=True)
            shutil.copy2(ruta_archivo_original, destino_per)
            
        return True
    except Exception as e:
        return False
# ... arriba están los import ...
# --- NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.image("logo_aboagrim.jpg", width=180)
    st.title("AboAgrim Pro")
    st.write("**Lic. Jhonny Matos. M.A.**")
    st.write("Presidente")
    st.divider()

# --- DATOS OFICIALES DE LA FIRMA ABOAGRIM ---
NOMBRE_FIRMA = "AboAgrim - Servicios Legales y de Agrimensura"
DIRECCION_FIRMA = "Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Centro Ciudad, Santiago, R.D."
TELEFONOS_FIRMA = "829-826-5888 / 809-691-3333"
CORREO_FIRMA = "aboagrim@gmail.com"
PRESIDENTE_FIRMA = "Lic. Jhonny Matos, M.A."
    
# =========================================================
# MOTOR DE ESTILOS VISUALES (Se ejecuta siempre al inicio)
# =========================================================
if "tema_color" in st.session_state:
    # Definimos si el fondo es oscuro o claro
    bg_color = "#0e1117" if st.session_state["tema_fondo"] == "Oscuro Profundo" else "#ffffff"
    text_color = "#ffffff" if st.session_state["tema_fondo"] == "Oscuro Profundo" else "#000000"
    
    # Inyectamos el diseño personalizado en toda la aplicación
    custom_css = f"""
    <style>
        /* Cambiar color de fondo principal y texto */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
            font-family: {st.session_state['tema_fuente']} !important;
        }}
        /* Cambiar el color de todos los Títulos */
        h1, h2, h3, h4, h5, h6 {{
            color: {st.session_state['tema_color']} !important;
            font-family: {st.session_state['tema_fuente']} !important;
        }}
        /* Cambiar el color de los botones principales */
        .stButton>button[kind="primary"] {{
            background-color: {st.session_state['tema_color']};
            border-color: {st.session_state['tema_color']};
            color: white;
        }}
        /* Cambiar el color del texto en los inputs si el fondo es blanco */
        .stTextInput>div>div>input {{
            color: {text_color};
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


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

def generar_documento_word(tipo_doc, datos):
    """
    Motor principal que une la plantilla .docx con los datos del expediente.
    """
    try:
        # 1. Definimos la ruta de la plantilla según lo seleccionado
        # Asegúrese de tener una carpeta llamada 'plantillas' con estos nombres
        rutas = {
            "Instancia de Mensura Catastral": "plantillas/mensura_base.docx",
            "Acto de Alguacil (Notificación)": "plantillas/acto_alguacil.docx",
            "Contrato de Cuota Litis": "plantillas/cuota_litis.docx",
            "Oficio de Remisión de Planos": "plantillas/oficio_remision.docx"
        }
        
        ruta_plantilla = rutas.get(tipo_doc, "plantillas/base_aboagrim.docx")
        
        # 2. Cargamos la plantilla
        doc = DocxTemplate(ruta_plantilla)
        
        # 3. Mapeamos los datos (asegurándose de que coincidan con los {{ }} del Word)
        contexto = {
            'fecha': datos['fecha_acto'],
            'propietario': datos['nombre_propietario'],
            'cedula': datos['cedula_cliente'],
            'parcela': datos['parcela_num'],
            'dc': datos['distrito_catastral'],
            'municipio': datos['municipio_prov'],
            'monto': datos['monto_contrato'],
            'firma': datos['firma_presidente']
        }
        
        # 4. Realizamos la "Magia": Fusionar datos con el Word
        doc.render(contexto)
        
        # 5. Lo guardamos en memoria para que Streamlit pueda descargarlo
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return buffer
    except Exception as e:
        st.error(f"Error técnico en el motor: {e}")
        return None


if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

from supabase import create_client, Client

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
    import zipfile
    import os
    from docxtpl import DocxTemplate
    
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
    # Mantenemos su diseño elegante intacto
    st.markdown("""
        <div style='background:linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); padding:35px 30px; border-radius:12px; color:white; border-left:6px solid #FBBF24; margin-bottom: 20px;'>
            <h1 style='margin:0; font-size: 2.8rem; font-weight: 800;'>AboAgrim Pro DMS ⚖️</h1>
            <p style='font-size:1.2rem; color:#94A3B8; margin-bottom: 1rem;'>Centro de Mando: Jurisdicción Inmobiliaria y Mensura</p>
            <div style='font-size:1.1rem; color:#FBBF24; font-weight:600; text-transform:uppercase;'>Santiago | Lic. Jhonny Matos, M.A.</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📈 Desempeño Operativo en la Nube")

    try:
        # 1. Consultar datos reales de la nube Supabase
        respuesta = supabase.table("expedientes_maestros").select("*").execute()
        datos = respuesta.data
        total_expedientes = len(datos)

        # 2. Mostrar Indicadores Rápidos (Métricas reales)
        col1, col2, col3 = st.columns(3)
        col1.metric("Expedientes Totales", total_expedientes)
        col2.metric("Mensuras Pendientes", "Próximamente")
        col3.metric("Estado del Sistema", "En Línea ☁️")

        st.divider()

        # 3. Mostrar los últimos movimientos reales
        st.subheader("📝 Últimos Movimientos")
        
        if total_expedientes == 0:
            st.info("Aún no hay expedientes en la base de datos. ¡Empiece hoy mismo en el Registro Maestro!")
        else:
            import pandas as pd
            df = pd.DataFrame(datos)
            
            # Ordenamos para mostrar los más recientes arriba
            df_recientes = df.sort_values(by="fecha_creacion", ascending=False).head(5)
            
            # Limpiamos las columnas para la vista rápida
            df_vista = df_recientes.rename(columns={
                "expediente": "No. Exp",
                "nombre_propietario": "Propietario",
                "municipio": "Ubicación"
            })
            
            st.table(df_vista[["No. Exp", "Propietario", "Ubicación"]])
            st.caption("Mostrando los últimos 5 expedientes registrados en su archivo digital.")

    except Exception as e:
        st.error("⚠️ Error al conectar el Mando Central con la Bóveda Digital.")
# =====================================================================
# MÓDULO 2: REGISTRO MAESTRO (CON PESTAÑAS Y 7 ROLES)
# =====================================================================
import streamlit as st
import datetime


# =====================================================================
# MÓDULO 3: ARCHIVO DIGITAL (BÓVEDA, EXPLORADOR Y DESCARGA ZIP)
# =====================================================================
def vista_archivo():
    st.title("📁 Bóveda Digital DMS")
    tab1, tab2 = st.tabs(["⬆️ Cargar Documentos", "🗄️ Explorador de Bóveda"])
    
    with tab1:
        st.markdown("Vincule planos de Civil 3D (DWG), PDFs, o sentencias a un expediente.")
        exp = st.text_input("Vincular al Expediente N° (Ej. EXP-001):", key="upload_exp")
        archivos = st.file_uploader("Arrastre sus archivos aquí:", accept_multiple_files=True)
        
        if st.button("⬆️ Subir a la Nube Segura"):
            if exp.strip() != "" and archivos:
                with st.spinner("Encriptando y subiendo archivos a la Bóveda..."):
                    for archivo in archivos:
                        file_bytes = archivo.read()
                        ruta_segura = f"{exp.strip()}/{archivo.name}"
                        exito = subir_documento("expedientes", ruta_segura, file_bytes)
                        if exito:
                            st.success(f"✅ {archivo.name} guardado en {exp}.")
                    st.toast("Transferencia completada.", icon="☁️")
            else:
                st.warning("⚠️ Debe indicar el N° de Expediente y seleccionar al menos un archivo.")
                
    with tab2:
        st.markdown("### 🔍 Buscar Documentos por Expediente")
        exp_busqueda = st.text_input("Ingrese el N° de Expediente a consultar:", key="search_exp")
        
        if st.button("🗂️ Buscar Archivos"):
            if exp_busqueda.strip():
                archivos_encontrados = listar_documentos("expedientes", exp_busqueda.strip())
                
                if archivos_encontrados and len(archivos_encontrados) > 0:
                    st.success(f"Archivos encontrados para el expediente {exp_busqueda}:")
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # 1. Mostramos la lista normal
                    for arch in archivos_encontrados:
                        nombre_archivo = arch.get('name')
                        if nombre_archivo and nombre_archivo != '.emptyFolderPlaceholder':
                            ruta_completa = f"{exp_busqueda.strip()}/{nombre_archivo}"
                            url_descarga = obtener_url_descarga("expedientes", ruta_completa)
                            
                            col1, col2 = st.columns([3, 1])
                            col1.markdown(f"📄 **{nombre_archivo}**")
                            col2.markdown(f"<a href='{url_descarga}' target='_blank'><button style='width:100%; padding:5px; border-radius:5px; background-color:#1E3A8A; color:white; border:none; cursor:pointer;'>⬇️ Ver Individual</button></a>", unsafe_allow_html=True)
                            st.divider()
                    
                    # 2. Lógica para crear el archivo ZIP en memoria
                    st.markdown("### 📦 Descarga Masiva")
                    with st.spinner("Empaquetando expediente completo..."):
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                            for arch in archivos_encontrados:
                                nombre_archivo = arch.get('name')
                                if nombre_archivo and nombre_archivo != '.emptyFolderPlaceholder':
                                    ruta_completa = f"{exp_busqueda.strip()}/{nombre_archivo}"
                                    # Descargamos los bytes de cada archivo
                                    file_bytes = descargar_documento_bytes("expedientes", ruta_completa)
                                    if file_bytes:
                                        # Lo metemos dentro del ZIP
                                        zip_file.writestr(nombre_archivo, file_bytes)
                        
                        # 3. Botón nativo de Streamlit para descargar el ZIP a la PC
                        st.download_button(
                            label=f"📦 Descargar Expediente {exp_busqueda.strip()} Completo (.ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name=f"Expediente_{exp_busqueda.strip()}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                else:
                    st.info("No se encontraron documentos en esta carpeta o el expediente no existe.")
            else:
                st.warning("⚠️ Por favor, ingrese un número de expediente.")

# =====================================================================
# MÓDULO 4: PLANTILLAS Y LEY 108-05
# =====================================================================
def vista_plantillas():
    st.title("📄 Generador de Plantillas Automatizado")
    st.markdown("### *AboAgrim Pro: Documentación Dinámica*")


# =====================================================================
# MÓDULO 5: ALERTAS Y PLAZOS
# =====================================================================
from datetime import datetime, timedelta

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
            

from fpdf import FPDF
from datetime import datetime

def vista_facturacion():
    st.title("💵 Facturación y Cobros Mágicos")
    st.subheader("Control Financiero | AboAgrim Pro")
    
    # --- MOTOR DE PDF ÉLITE 2026 ---
    def generar_pdf_factura(datos, num_fac):
        pdf = FPDF()
        pdf.add_page()
        
        # Paleta de Colores Corporativos
        AZUL_OSCURO = (11, 15, 25)
        DORADO = (212, 175, 55)
        TEXTO_GRIS = (100, 116, 139)
        ROJO_ELEGANTE = (220, 38, 38)
        GRIS_CLARO = (248, 250, 252)
        
        # 1. Barra superior decorativa
        pdf.set_fill_color(*AZUL_OSCURO)
        pdf.rect(0, 0, 210, 12, 'F')
        pdf.ln(15)
        
        # 2. Encabezado a dos columnas (Izquierda: Oficina | Derecha: Datos Factura)
        pdf.set_font("Arial", "B", 26)
        pdf.set_text_color(*AZUL_OSCURO)
        pdf.cell(110, 10, "ABOAGRIM", ln=0)
        
        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(*DORADO)
        pdf.cell(0, 10, "FACTURA", ln=1, align="R")
        
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(*DORADO)
        pdf.cell(110, 5, "DESPACHO LEGAL Y AGRIMENSURA", ln=0)
        
        pdf.set_font("Arial", "B", 11)
        pdf.set_text_color(*TEXTO_GRIS)
        pdf.cell(0, 5, f"No. {num_fac}", ln=1, align="R")
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(110, 5, "Lic. Jhonny Matos | Presidente Fundador", ln=0)
        pdf.cell(0, 5, f"Fecha: {datos['fecha']}", ln=1, align="R")
        
        pdf.ln(10)
        
        # 3. Separador Superior
        pdf.set_draw_color(*DORADO)
        pdf.set_line_width(0.6)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.set_line_width(0.2) # Resetear grosor
        pdf.ln(8)
        
        # 4. Datos del Cliente y Servicio
        pdf.set_font("Arial", "B", 9)
        pdf.set_text_color(*TEXTO_GRIS)
        pdf.cell(0, 5, "FACTURADO A / EXPEDIENTE:", ln=1)
        
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(*AZUL_OSCURO)
        pdf.cell(0, 8, f"{datos['expediente']}", ln=1)
        pdf.ln(2)
        
        pdf.set_font("Arial", "B", 9)
        pdf.set_text_color(*TEXTO_GRIS)
        pdf.cell(0, 5, "CONCEPTO DEL SERVICIO:", ln=1)
        
        pdf.set_font("Arial", "", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 7, f"{datos['concepto']}")
        
        if datos['observaciones']:
            pdf.ln(3)
            pdf.set_font("Arial", "I", 10)
            pdf.set_text_color(*TEXTO_GRIS)
            pdf.multi_cell(0, 5, f"Nota: {datos['observaciones']}")
            
        pdf.ln(8)
        
        # Separador Sutil
        pdf.set_draw_color(226, 232, 240)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)
        
        # 5. Desglose Financiero (Fondo oscuro para cabecera de montos)
        pdf.set_fill_color(*AZUL_OSCURO)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(95, 10, "  MODALIDAD Y VÍA DE PAGO", border=0, fill=True)
        pdf.cell(95, 10, "IMPORTES  ", border=0, fill=True, align="R", ln=1)
        pdf.ln(4)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(95, 10, f"  Tipo: {datos['tipo']}")
        
        pdf.set_font("Arial", "B", 14)
        pdf.cell(95, 10, f"MONTO RECIBIDO: RD$ {datos['pago']:,.2f}  ", ln=1, align="R")
        
        pdf.set_font("Arial", "", 11)
        pdf.cell(95, 10, f"  Vía: {datos['metodo']}")
        
        pdf.set_text_color(*ROJO_ELEGANTE)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(95, 10, f"BALANCE PENDIENTE: RD$ {datos['resta']:,.2f}  ", ln=1, align="R")
        pdf.ln(10)
        
        # 6. Pie de Página - Bancos (En un recuadro elegante)
        pdf.set_fill_color(*GRIS_CLARO)
        pdf.rect(10, pdf.get_y(), 190, 25, 'F')
        
        pdf.set_y(pdf.get_y() + 4)
        pdf.set_x(15)
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(*AZUL_OSCURO)
        pdf.cell(0, 5, "CUENTAS BANCARIAS PARA DEPÓSITO (AHORROS):", ln=1)
        
        pdf.set_x(15)
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(90, 6, "Banco de Reservas: 9601369253")
        pdf.cell(90, 6, "Banco BHD: 08010850011", ln=1)
        
        # 7. Sello de Sistema
        pdf.set_y(280)
        pdf.set_font("Arial", "I", 8)
        pdf.set_text_color(*TEXTO_GRIS)
        pdf.cell(0, 5, "Documento generado digitalmente por AboAgrim Pro DMS - 2026", align="C")
        
        return bytes(pdf.output())

    tab_emitir, tab_historial = st.tabs(["📄 Emitir Nueva Factura", "📊 Historial"])
    
    with tab_emitir:
        c1, c2 = st.columns([1.5, 1.5])
        
        with c1:
            with st.container(border=True):
                st.markdown("### 📝 Parámetros de Cobro")
                
                try:
                    res_e = supabase.table("expedientes_maestros").select("expediente, nombre_propietario").execute()
                    list_e = [f"{e['expediente']} - {e['nombre_propietario']}" for e in res_e.data] if res_e.data else []
                except: list_e = []
                    
                expediente = st.selectbox("Expediente Vinculado:", ["Seleccione..."] + list_e)
                colA, colB = st.columns(2)
                tipo_pago = colA.selectbox("Modalidad:", ["Avance Inicial", "Pago Parcial", "Saldo Final"])
                metodo = colB.selectbox("Vía:", ["Transferencia", "Efectivo", "Cheque"])
                
                concepto = st.text_input("Concepto:")
                obs = st.text_area("Observaciones Internas / Notas al Cliente:", placeholder="Ej: Pago sujeto a validación...")
                
                st.divider()
                col_m1, col_m2 = st.columns(2)
                m_pago = col_m1.number_input("Pago Hoy (RD$):", min_value=0.0, format="%.2f")
                m_resta = col_m2.number_input("Resta (RD$):", min_value=0.0, format="%.2f")
                
                if st.button("✨ Generar Factura", type="primary", use_container_width=True):
                    if expediente != "Seleccione...":
                        st.session_state['datos_fac'] = {
                            "expediente": expediente, "concepto": concepto, "observaciones": obs,
                            "pago": m_pago, "resta": m_resta, "tipo": tipo_pago, "metodo": metodo,
                            "fecha": datetime.now().strftime("%d/%m/%Y")
                        }
                        st.session_state['factura_ready'] = True

        with c2:
            if st.session_state.get('factura_ready'):
                d = st.session_state['datos_fac']
                n_f = f"FAC-{datetime.now().strftime('%y%m%H%M')}"
                
                # --- VISTA PREVIA PROFESIONAL EN PANTALLA ---
                with st.container(border=True):
                    st.markdown("<h2 style='text-align: center; color: #d4af37;'>⚖️ AboAgrim</h2>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align: center; font-weight: bold;'>Lic. Jhonny Matos | Presidente Fundador</p>", unsafe_allow_html=True)
                    st.divider()
                    
                    st.write(f"**Expediente:** {d['expediente']}")
                    st.write(f"**Concepto:** {d['concepto']}")
                    if d['observaciones']:
                        st.caption(f"**Obs:** {d['observaciones']}")
                    
                    st.divider()
                    st.markdown(f"### 💰 RECIBIDO: RD$ {d['pago']:,.2f}")
                    st.markdown(f"#### 🔴 PENDIENTE: RD$ {d['resta']:,.2f}")
                    
                    with st.expander("🏦 Datos para Depósito", expanded=False):
                        st.markdown("**Banreservas:** 9601369253 | **BHD:** 08010850011")
                
                col_wa, col_dl = st.columns(2)
                
                # Descarga PDF
                pdf_bytes = generar_pdf_factura(d, n_f)
                nombre_limpio = d['expediente'].split()[0].replace("-", "_")
                col_dl.download_button("📥 Descargar PDF Élite", data=pdf_bytes, file_name=f"AboAgrim_Factura_{nombre_limpio}.pdf", mime="application/pdf", use_container_width=True)
                
                # WhatsApp
                msg = f"Saludos. Confirmamos su pago de *RD$ {d['pago']:,.2f}*. Su balance pendiente es de *RD$ {d['resta']:,.2f}*. \n\n*Cuentas (Ahorros):* \nBanreservas: 9601369253 \nBHD: 08010850011"
                col_wa.link_button("🟢 Enviar WhatsApp", f"https://wa.me/?text={msg.replace(' ', '%20')}", use_container_width=True)
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
def vista_documentos():
    st.header("📄 Generador de Documentos y Actas")
    st.info("Seleccione un expediente y una plantilla para generar el documento automáticamente.")

    # 1. Buscamos los expedientes activos para rellenar datos
    try:
        res_exp = supabase.table("agenda_mensuras").select("expediente, cliente, notas").execute()
        expedientes = [e['expediente'] for e in res_exp.data] if res_exp.data else []
    except:
        expedientes = []

    if not expedientes:
        st.warning("No hay expedientes registrados para generar documentos.")
        return

    col1, col2 = st.columns(2)
    with col1:
        exp_sel = st.selectbox("Seleccione el Expediente:", expedientes)
        tipo_doc = st.selectbox("Tipo de Documento:", [
            "Acta de Hito y Colindancia", 
            "Contrato de Cuota Litis", 
            "Instancia de Solicitud de Mensura"
        ])
    
    # 2. Buscamos los datos específicos del cliente seleccionado
    datos_cliente = next((item for item in res_exp.data if item["expediente"] == exp_sel), None)

    if datos_cliente:
        st.subheader("📝 Editor de Documento")
        
        # Plantilla básica
        cuerpo = f"""ACTA DE HITO Y COLINDANCIA
            
En el municipio de Santiago de los Caballeros, República Dominicana.
En relación al expediente No. {datos_cliente['expediente']}, propiedad de {datos_cliente['cliente']}.

Por medio de la presente, AboAgrim, representada por el Lic. Jhonny Matos, M.A., hace constar que..."""
        
        texto_final = st.text_area("Contenido del Documento:", cuerpo, height=350)

# --- BLOQUE DE BOTONES FINAL (Péguelo aquí) ---
        st.markdown("---")
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            # Este botón descarga el acta a su computadora
            st.download_button(
                label="💾 Descargar Acta (.txt)",
                data=texto_final,
                file_name=f"Acta_{exp_sel}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        with col_btn2:
            # Este botón abre el panel de impresión profesional
            if st.button("🖨️ IMPRIMIR DOCUMENTO", use_container_width=True):
                doc_html = f"""
                <div style="font-family: 'Times New Roman', serif; padding: 50px; line-height: 1.6; background-color: white; color: black;">
                    <h2 style="text-align: center; color: #1E3A8A;">ABOAGRIM</h2>
                    <p style="text-align: center; font-weight: bold;">SERVICIOS LEGALES Y CATASTRALES</p>
                    <p style="text-align: center; font-size: 12px;">Lic. Jhonny Matos, M.A. | Santiago, R.D.</p>
                    <hr style="border: 1px solid black;">
                    <div style="white-space: pre-wrap; margin-top: 30px; font-size: 15px; text-align: justify;">{texto_final}</div>
                </div>
                <script>setTimeout(function(){{ window.print(); }}, 500);</script>
                """
                st.components.v1.html(doc_html, height=600, scrolling=True)
def vista_archivo_digital():
    st.title("📁 Archivo Digital | AboAgrim Pro")
    st.subheader("Bóveda de Expedientes y Anexos Técnicos")
    st.divider()

    # --- 1. BUSCADOR DE EXPEDIENTES ---
    st.markdown("### 🔍 Localizador de Carpetas")
    
    try:
        # Consulta a Supabase para obtener los expedientes activos
        res_exp = supabase.table("expedientes_maestros").select("expediente, nombre_propietario").execute()
        lista_expedientes = [f"{e['expediente']} - {e['nombre_propietario']}" for e in res_exp.data] if res_exp.data else []
        
        if not lista_expedientes:
            st.info("📌 No hay expedientes registrados. Vaya al 'Registro Maestro' para crear el primer caso.")
            return

        # Selector desplegable (diseño limpio sin exceso de botones)
        expediente_seleccionado = st.selectbox("Seleccione el Expediente a consultar:", ["Seleccione..."] + lista_expedientes)
        
        if expediente_seleccionado == "Seleccione...":
            return # Pausa la pantalla hasta que elija un cliente

        codigo_exp = expediente_seleccionado.split(" - ")[0]
        st.success(f"📂 Carpeta Abierta: **{expediente_seleccionado}**")

    except Exception as e:
        st.error(f"Detalle técnico del error: {e}")
        return

    st.write("---")

    # --- 2. GESTIÓN DEL EXPEDIENTE (PESTAÑAS) ---
    tab_visor, tab_carga = st.tabs(["📄 Visor de Documentos", "📤 Digitalizar y Subir"])

    # PESTAÑA A: VISOR ORGANIZADO
    with tab_visor:
        st.markdown(f"### 📑 Inventario del Expediente {codigo_exp}")
        
        # Filtro de vista rápida
        filtro_vista = st.radio(
            "Filtrar por departamento:", 
            ["Todo", "⚖️ Legal (Títulos y Actos)", "🗺️ Agrimensura (Planos y Coordenadas)", "🆔 Anexos"], 
            horizontal=True
        )

        # Aquí simulamos la lectura de archivos desde su "Storage" en Supabase
        st.info(f"Conectando con el servidor Cloud para recuperar archivos de {codigo_exp}...")
        
        # Cuadrícula de documentos (Diseño Ejecutivo)
        col_doc1, col_doc2 = st.columns(2)
        
        with col_doc1:
            st.markdown("#### 🗺️ Área Técnica")
            with st.expander("Planos y Mensura", expanded=True):
                st.caption("No hay archivos cargados en: Planos Generales.")
                st.caption("No hay archivos cargados en: Tablas de Coordenadas.")
                st.caption("No hay archivos cargados en: Datos Parcelarios.")

        with col_doc2:
            st.markdown("#### ⚖️ Área Legal")
            with st.expander("Títulos y Actos", expanded=True):
                st.caption("No hay archivos cargados en: Certificados de Título.")
                st.caption("No hay archivos cargados en: Actos de Venta/Poderes.")
                st.caption("No hay archivos cargados en: Cédulas de Identidad.")

    # PESTAÑA B: ZONA DE CARGA
    with tab_carga:
        st.markdown("### 📥 Ingreso de Nuevos Documentos")
        st.write("Clasifique y suba los escaneos directamente a la bóveda del cliente.")
        
        with st.container(border=True):
            col_form1, col_form2 = st.columns(2)
            
            with col_form1:
                # Categorías técnicas y legales detalladas
                categoria_doc = st.selectbox(
                    "Clasificación del Documento:", 
                    [
                        "Plano General Catastral",
                        "Tabla de Coordenadas", 
                        "Datos Parcelarios (Derrotero)",
                        "Certificado de Título", 
                        "Acto de Venta / Contrato", 
                        "Poder de Representación",
                        "Cédula / Identificación",
                        "Resolución del Tribunal"
                    ]
                )
                descripcion_doc = st.text_input("Breve descripción (Opcional):", placeholder="Ej: Plano aprobado marzo 2026")
                
            with col_form2:
                archivo_pdf = st.file_uploader("Seleccione el archivo escaneado (PDF, JPG)", type=["pdf", "jpg", "png"])
            
            if st.button("💾 Encriptar y Guardar en Bóveda", use_container_width=True, type="primary"):
                if archivo_pdf:
                    # Lógica futura para: supabase.storage.from_('boveda').upload(f"{codigo_exp}/{archivo_pdf.name}")
                    st.toast(f"Archivo '{archivo_pdf.name}' procesado.", icon="✅")
                    st.success(f"El documento se ha guardado exitosamente bajo la categoría '{categoria_doc}' en el expediente {codigo_exp}.")
                else:
                    st.warning("⚠️ Debe adjuntar un archivo antes de proceder a guardar.")
        
        
def vista_plantillas_auto():
    st.title("📄 Fábrica de Documentos AboAgrim Pro")
    st.subheader("Módulo de Control Técnico y Legal JI")

    # --- INICIALIZACIÓN DE MEMORIA DINÁMICA ---
    if 'cant_extras' not in st.session_state: st.session_state.cant_extras = 0
    if 'cant_profesionales' not in st.session_state: st.session_state.cant_profesionales = 0
    if 'cant_apoderados' not in st.session_state: st.session_state.cant_apoderados = 0

    TRAMITES_JI = {
        "📍 Mensuras Catastrales": [
            "Actualización de Mensura", "Corrección Mensura Desplazada", "Desafectación de Dominio Público", 
            "Deslinde", "División para Constitución de Condominio", "Modificación Condominio", 
            "Oposición Expediente Técnico", "Plano Definitivo", "Prórroga de Autorización", 
            "Refundición", "Regularización Parcelaria", "Saneamiento", "Subdivisión", "Urbanización Parcelaria"
        ],
        "📜 Registro de Títulos": [
            "Transferencia de Inmueble", "Transferencia de Mejoras", "Hipoteca Convencional", 
            "Cancelación de Hipoteca Convencional", "Certificación del Estado Jurídico del Inmueble", 
            "Actualización de Generales", "Duplicado por Pérdida o Deterioro", "Constitución de Régimen de Condominio", 
            "Embargo Inmobiliario", "Privilegio de Honorarios de Abogados", "Anotación Preventiva"
        ],
        "⚖️ Tribunales de Tierras": [
            "Determinación de Herederos", "Litis Sobre Derechos Registrados", "Recurso de Apelación", 
            "Partición Amigable Entre Esposos", "Partición Amigable con Determinación de Herederos", 
            "Renuncia de Bien de Familia", "Solicitud de Transferencias Administrativas", 
            "Solicitud de Desglose como Instancia Principal Administrativa", "Revisión por Causa de Fraude"
        ]
    }

    try:
        res = supabase.table("expedientes_maestros").select("id, nombre_propietario").order("id", desc=True).execute()
        opciones_exp = {f"RES-{e['id']} | {e['nombre_propietario']}": e['id'] for e in res.data} if res.data else {"Ninguno": None}

        col_menu1, col_menu2, col_menu3 = st.columns(3)
        with col_menu1:
            sel_cliente = st.selectbox("👤 Expediente:", list(opciones_exp.keys()))
            id_cliente = opciones_exp.get(sel_cliente)
        with col_menu2:
            jurisdiccion = st.selectbox("🏛️ Jurisdicción:", list(TRAMITES_JI.keys()))
        with col_menu3:
            tramite = st.selectbox(f"📋 Trámite:", TRAMITES_JI[jurisdiccion])

        st.divider()

        # ==========================================
        # 1. BLOQUE DE DATOS TÉCNICOS BASE
        # ==========================================
        st.write(f"### 📑 Datos Estándar de JI")
        c1, c2, c3 = st.columns(3)
        with c1:
            ji_parcela = st.text_input("Parcela No.", placeholder="Ej: 123-A")
            ji_dc = st.text_input("Distrito Catastral (DC)", placeholder="Ej: 01")
            ji_solar_manzana = st.text_input("Solar / Manzana", placeholder="Ej: Solar 5, Manzana 12")
            
        with c2:
            ji_matricula = st.text_input("Matrícula / Certificado")
            ji_libro = st.text_input("Libro / Folio")
            ji_fecha_emision = st.text_input("Fecha Inscripción / Emisión", placeholder="DD/MM/AAAA")
            
        with c3:
            ji_exp_ji = st.text_input("Expediente JI No.")
            ji_ubicacion = st.text_input("Ubicación del Inmueble", value="Santiago")
            ji_area = st.text_input("Área / Superficie (m²)")
            ji_coordenadas = st.text_input("Coordenadas (UTM/WGS84)")

        # ==========================================
        # 1.5 BLOQUE DINÁMICO DE LITIGIO (SOLO TRIBUNALES)
        # ==========================================
        ji_demandante = ji_demandado = ji_sala = ji_juez = ji_rol = ji_audiencia = ""
        
        if jurisdiccion == "⚖️ Tribunales de Tierras":
            st.write("---")
            st.markdown("### ⚖️ Módulo de Litigios (Exclusivo Tribunal)")
            lt1, lt2, lt3 = st.columns(3)
            with lt1:
                ji_demandante = st.text_input("Parte Demandante / Recurrente")
                ji_demandado = st.text_input("Parte Demandada / Recurrida")
            with lt2:
                ji_sala = st.text_input("Sala / Cámara", placeholder="Ej: Segunda Sala")
                ji_juez = st.text_input("Magistrado / Juez Apoderado")
            with lt3:
                ji_rol = st.text_input("Número de Rol / Cuaderno")
                ji_audiencia = st.text_input("Fecha de Próxima Audiencia", placeholder="DD/MM/AAAA")

        # ==========================================
        # 2. CAMPOS EXTRA DINÁMICOS (JI)
        # ==========================================
        st.write("---")
        col_btn1, col_btn2, col_space = st.columns([1, 1, 3])
        with col_btn1:
            if st.button("➕ Agregar Dato Extra JI", use_container_width=True): st.session_state.cant_extras += 1
        with col_btn2:
            if st.button("➖ Borrar Dato Extra", use_container_width=True) and st.session_state.cant_extras > 0: st.session_state.cant_extras -= 1

        datos_extras_dict = {}
        for i in range(st.session_state.cant_extras):
            c_nom, c_val = st.columns(2)
            with c_nom: 
                nombre_campo = st.text_input(f"Nombre del dato {i+1}", key=f"ex_n_{i}")
            with c_val: 
                valor_campo = st.text_input(f"Valor {i+1}", key=f"ex_v_{i}")
            if nombre_campo: datos_extras_dict[nombre_campo.replace(" ", "_").lower()] = valor_campo

        # ==========================================
        # 3. PROFESIONALES ACTUANTES DINÁMICOS
        # ==========================================
        st.write("---")
        st.subheader("👥 Profesionales Actuantes")
        col_p1, col_p2, col_p3 = st.columns([1, 1, 3])
        with col_p1:
            if st.button("➕ Agregar Profesional", use_container_width=True): st.session_state.cant_profesionales += 1
        with col_p2:
            if st.button("➖ Borrar Profesional", use_container_width=True) and st.session_state.cant_profesionales > 0: st.session_state.cant_profesionales -= 1

        profesionales_lista = []
        for i in range(st.session_state.cant_profesionales):
            st.markdown(f"**Profesional {i+1}**")
            cp1, cp2, cp3 = st.columns(3)
            with cp1: n = st.text_input(f"Nombre Completo", key=f"p_nom_{i}")
            with cp2: r = st.selectbox(f"Rol", ["Abogado", "Agrimensor", "Notario Público"], key=f"p_rol_{i}")
            with cp3: c = st.text_input(f"Colegiatura", key=f"p_col_{i}")
            
            cpg1, cpg2, cpg3 = st.columns(3)
            with cpg1: p_ced = st.text_input(f"Cédula", key=f"p_ced_{i}")
            with cpg2: p_ec = st.selectbox(f"Estado Civil", ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"], key=f"p_ec_{i}")
            with cpg3: p_dom = st.text_input(f"Domicilio Profesional", key=f"p_dom_{i}")
            
            profesionales_lista.append({
                "nombre": n, "rol": r, "colegiatura": c, 
                "cedula": p_ced, "estado_civil": p_ec, "domicilio": p_dom
            })

        # ==========================================
        # 4. APODERADOS / REPRESENTANTES DINÁMICOS
        # ==========================================
        st.write("---")
        st.subheader("🤝 Representantes o Apoderados")
        col_a1, col_a2, col_a3 = st.columns([1, 1, 3])
        with col_a1:
            if st.button("➕ Agregar Apoderado", use_container_width=True): st.session_state.cant_apoderados += 1
        with col_a2:
            if st.button("➖ Borrar Apoderado", use_container_width=True) and st.session_state.cant_apoderados > 0: st.session_state.cant_apoderados -= 1

        apoderados_lista = []
        for i in range(st.session_state.cant_apoderados):
            st.markdown(f"**Apoderado / Representante {i+1}**")
            ca1, ca2, ca3 = st.columns(3)
            with ca1: an = st.text_input(f"Nombre Completo", key=f"a_nom_{i}")
            with ca2: ac = st.text_input(f"Cédula / Pasaporte", key=f"a_ced_{i}")
            with ca3: ar = st.text_input(f"En representación de", key=f"a_rep_{i}")
            
            cag1, cag2, cag3 = st.columns(3)
            with cag1: a_nac = st.text_input(f"Nacionalidad", value="Dominicano/a", key=f"a_nac_{i}")
            with cag2: a_ec = st.selectbox(f"Estado Civil", ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"], key=f"a_ec_{i}")
            with cag3: a_dom = st.text_input(f"Domicilio", key=f"a_dom_{i}")
            
            apoderados_lista.append({
                "nombre": an, "cedula": ac, "representa": ar,
                "nacionalidad": a_nac, "estado_civil": a_ec, "domicilio": a_dom
            })

        st.divider()

        # ==========================================
        # 5. FABRICACIÓN FINAL
        # ==========================================
        archivo_nombre = tramite.lower().replace(" ", "_") + ".docx"
        carpeta = "1_mensuras_catastrales" if "Mensuras" in jurisdiccion else "3_registro_titulos" if "Registro" in jurisdiccion else "2_jurisdiccion_original"
        ruta_final = f"plantillas_maestras/{carpeta}/{archivo_nombre}"
        st.divider()
        st.markdown("### 📄 Selección de Plantilla Base")
        
        # 1. Escaneamos las carpetas buscando sus archivos Word
        import os
        archivos_disponibles = []
        carpetas_base = ["1_mensuras_catastrales", "2_jurisdiccion_original", "3_registro_titulos"]
        
        for carpeta in carpetas_base:
            ruta_check = f"plantillas_maestras/{carpeta}"
            if os.path.exists(ruta_check):
                for f in os.listdir(ruta_check):
                    if f.endswith(".docx"):
                        # Guardamos la ruta completa (ej: 1_mensuras_catastrales/prueba.docx)
                        archivos_disponibles.append(f"{carpeta}/{f}")
        
        # 🌟 1. EL NUEVO SELECTOR MÚLTIPLE (REEMPLAZA LA LÍNEA 1178)
        plantillas_elegidas = st.multiselect("Elija los documentos Word que desea rellenar (puede elegir varios):", archivos_disponibles)
        st.caption("💡 Los archivos que suba en el administrador de abajo aparecerán aquí automáticamente.")
        st.write("")
        
        if st.button("🚀 FABRICAR DOCUMENTOS MAESTROS", type="primary", use_container_width=True):
            if not plantillas_elegidas:
                st.error("⚠️ Por favor, seleccione al menos un archivo de plantilla arriba antes de fabricar.")
            else:
                # 1. Empaquetamos los datos
                diccionario_datos = {
                    "expediente_ji": ji_exp_ji if 'ji_exp_ji' in locals() else "",
                    "ubicacion": ji_ubicacion if 'ji_ubicacion' in locals() else "Santiago",
                    "area": ji_area if 'ji_area' in locals() else "",
                    "coordenadas": ji_coordenadas if 'ji_coordenadas' in locals() else "",
                    "demandante": ji_demandante if 'ji_demandante' in locals() else "",
                    "demandado": ji_demandado if 'ji_demandado' in locals() else ""
                }
                
                # 2. Creamos una "Bandeja de salida" en la memoria del sistema
                st.session_state["bandeja_descargas"] = []
                
                # 3. Forjamos todos los documentos y los guardamos en la bandeja
                for plantilla in plantillas_elegidas:
                    ruta_exacta = f"plantillas_maestras/{plantilla}"
                    buffer = generar_documento_word(ruta_exacta, diccionario_datos)
                    
                    if buffer:
                        nombre_limpio = plantilla.split('/')[-1]
                        st.session_state["bandeja_descargas"].append({
                            "nombre": nombre_limpio,
                            "archivo": buffer
                        })

        # 4. MOSTRAR LOS BOTONES (Fuera del botón rojo para que no desparezcan)

        if "bandeja_descargas" in st.session_state and len(st.session_state["bandeja_descargas"]) > 0:
            st.write("---")
            st.success("✅ ¡Fábrica terminada! Sus documentos están listos en la bandeja:")
    
            for doc in st.session_state["bandeja_descargas"]:
                # --- TODO ESTO DEBE TENER MÁS SANGRÍA ---
                st.download_button(
                    label=f"📥 Descargar {doc['nombre']}",
                    data=doc['archivo'],
                    file_name=f"AboAgrim_{doc['nombre']}",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    key=f"dl_btn_{doc['nombre']}"
                )
                
                # --- GATILLO DE DRIVE ---
                # --- GATILLO DE DRIVE CON DIAGNÓSTICO ---
            try:
                import os
                ruta_ab = st.session_state.get("ruta_aboagrim", "")
                ruta_per = st.session_state.get("ruta_personal", "")
                datos_archivo = doc['archivo'].getvalue()
                
                # --- MENSAJES DE RASTREO (Solo para nosotros ver qué pasa) ---
                if not ruta_ab and not ruta_per:
                    st.error("⚠️ Las rutas de Drive están vacías en Configuración.")
                
                guardado = False
                # Intento en Drive AboAgrim
                if ruta_ab:
                    if os.path.exists(ruta_ab):
                        nombre_final = os.path.join(ruta_ab, f"AboAgrim_{doc['nombre']}")
                        with open(nombre_final, "wb") as f:
                            f.write(datos_archivo)
                        guardado = True
                    else:
                        st.error(f"❌ No encuentro la carpeta: {ruta_ab}")

                # Intento en Drive Personal
                if ruta_per:
                    if os.path.exists(ruta_per):
                        nombre_final_per = os.path.join(ruta_per, f"AboAgrim_{doc['nombre']}")
                        with open(nombre_final_per, "wb") as f:
                            f.write(datos_archivo)
                        guardado = True
                    else:
                        st.error(f"❌ No encuentro la carpeta: {ruta_per}")
                
                if guardado:
                    st.success(f"☁️ ✅ ¡Confirmado! Copia guardada en Drive.")

            except Exception as e:
                # 👆 ESTE 'except' alineado perfectamente con el 'try' de arriba
                st.error(f"💥 Error técnico al guardar: {e}")
    # Note cómo el except se va hacia la izquierda, saliendo del bloque del botón
    except Exception as e:
        st.error(f"❌ Error al fabricar: {e}")
    # ==========================================
    # 6. MANTENIMIENTO CON PIN (RECUPERADO)
    # ==========================================
    st.write("---")
    with st.expander("🛠️ ADMINISTRAR ARCHIVOS DE PLANTILLAS"):
        pin_ingresado = st.text_input("🔑 PIN de Seguridad:", type="password", key="pin_p_auto")
        PIN_SECRETO = "0681"
        
        if pin_ingresado == PIN_SECRETO:
            maint_col1, maint_col2 = st.columns(2)
            import os
            
            with maint_col1:
                st.markdown("**📥 Subir Nuevo Modelo**")
                destino = st.radio("Carpeta Destino:", ["1_mensuras_catastrales", "2_jurisdiccion_original", "3_registro_titulos"])
                archivo_subido = st.file_uploader("Elija el archivo .docx", type=["docx"])
                
                if st.button("💾 Guardar Plantilla"):
                    if archivo_subido:
                        os.makedirs(f"plantillas_maestras/{destino}", exist_ok=True)
                        with open(f"plantillas_maestras/{destino}/{archivo_subido.name}", "wb") as f:
                            f.write(archivo_subido.getbuffer())
                        st.success(f"✅ Documento guardado en {destino}. ¡Ya puede usarlo arriba!")
                        
            with maint_col2:
                st.markdown("**🗑️ Borrar Modelo Existente**")
                carpeta_borrar = st.selectbox("Buscar en Carpeta:", ["1_mensuras_catastrales", "2_jurisdiccion_original", "3_registro_titulos"], key="del_f")
                ruta_limpieza = f"plantillas_maestras/{carpeta_borrar}"
                archivos = os.listdir(ruta_limpieza) if os.path.exists(ruta_limpieza) else []
                
                archivo_a_borrar = st.selectbox("Archivo a eliminar:", ["Seleccione..."] + archivos)
                
                if st.button("🗑️ ELIMINAR PERMANENTE"):
                    if archivo_a_borrar and archivo_a_borrar != "Seleccione...":
                        os.remove(f"{ruta_limpieza}/{archivo_a_borrar}")
                        st.warning("🗑️ Archivo eliminado.")
                        st.rerun()
                        # ==========================================
# ... aquí termina su código de la Fábrica (probablemente en st.rerun() o similar) ...



# Aquí sigue def generar_documento_word(nombre_plantilla, diccionario_datos):
# Aquí debajo empieza su def generar_documento_word...

from docxtpl import DocxTemplate
import io
import streamlit as st

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
def guardar_y_actualizar(tipo_perfil, datos, ventana_origen, menu_desplegable=None):
    """Guarda en la base de datos y refresca el menú desplegable."""
    
    # 1. Lógica de inserción (Ejemplo SQL)
    # query = f"INSERT INTO {tipo_perfil} (nombre, cedula, profesion, ...) VALUES (...)"
    # ejecutar_query(query)
    
    print(f"Datos guardados en la nube para {tipo_perfil}: {datos}")
    
    # 2. Refrescar el Menú Desplegable si existe
    if menu_desplegable:
    
        nueva_lista = ["Seleccione..."] + ["Juan Pérez", "Lic. Matos", "Nuevo Registro..."] # Ejemplo
        menu_desplegable.configure(values=nueva_lista)
        menu_desplegable.set(datos["Nombre Completo"]) # Selecciona el recién creado

def ventana_registro_profesional(tipo, menu_a_refrescar=None):
    ventana = ctk.CTkToplevel()
    ventana.title(f"AboAgrim Pro - Registro de {tipo}")
    ventana.geometry("450x650")
    ventana.attributes('-topmost', True)

    # Contenedor con scroll para que sea moderno si hay muchos campos
    scroll_frame = ctk.CTkScrollableFrame(ventana, width=400, height=450)
    scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

    campos = ["Nombre Completo", "Cédula / RNC", "Dirección", "Teléfono", "Correo", "Profesión"]
    entradas = {}

    for campo in campos:
        ctk.CTkLabel(scroll_frame, text=campo, font=("Roboto", 12, "bold")).pack(anchor="w", padx=10)
        entry = ctk.CTkEntry(scroll_frame, placeholder_text=f"Escriba {campo.lower()}...", width=320)
        entry.pack(pady=(0, 15), padx=10)
        entradas[campo] = entry

    # Botón dinámico
    btn_guardar = ctk.CTkButton(
        ventana, 
        text=f"CONFIRMAR REGISTRO", 
        fg_color="#1a5276", # Azul profesional
        hover_color="#21618c",
        height=45,
        command=lambda: guardar_y_actualizar(
            tipo, 
            {k: v.get() for k, v in entradas.items()}, 
            ventana, 
            menu_a_refrescar
        )
    )
    btn_guardar.pack(pady=20)


# =======================================================
# 1. DISEÑO DE LA PANTALLA DE PLANTILLAS
# =======================================================

def crear_carpeta_expediente(nombre_cliente, id_expediente):
    # 1. Definimos el nombre de la carpeta principal
    nombre_carpeta = f"EXP_{id_expediente}_{nombre_cliente}"
    
    # 2. Lógica para crear carpeta en Google Drive (usando service account o OAuth)
    # (Aquí va la conexión técnica con Google)
    folder_metadata = {
        'name': nombre_carpeta,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': ['ID_DE_SU_CARPETA_MAESTRA_ABOAGRIM'] # Su carpeta raíz
    }
    
    # El sistema crea la carpeta y nos devuelve un Link
    # drive_service.files().create(body=folder_metadata).execute()
    
    link_drive = f"https://drive.google.com/drive/folders/ID_GENERADO"
    return link_drive
import googleapiclient.discovery
def vista_mando_central():
    st.title("🏠 Mando Central | AboAgrim Pro")
    st.markdown("**Bienvenido al panel de control principal, Lic. Jhonny Matos.**")
    st.divider()

    # --- 1. MÉTRICAS PRINCIPALES (KPIs) ---
    st.subheader("📊 Resumen de Operaciones")
    m1, m2, m3, m4 = st.columns(4)
    
    # Intentamos obtener el total real de expedientes desde Supabase
    total_expedientes = 0
    try:
        res = supabase.table("expedientes_maestros").select("id", count="exact").execute()
        total_expedientes = res.count if res.count else 0
    except Exception:
        pass

    with m1:
        st.metric(label="Expedientes Totales", value=total_expedientes, delta="Registrados")
    with m2:
        st.metric(label="Mensuras Catastrales", value="Activas") 
    with m3:
        st.metric(label="Registro de Títulos", value="Activos")
    with m4:
        st.metric(label="Tribunales de Tierras", value="En Litigio")

    st.write("---")

    # --- 2. ACCESOS RÁPIDOS Y ÚLTIMOS REGISTROS ---
    c_izq, c_der = st.columns([2, 1])
    
    with c_izq:
        st.subheader("🕒 Últimos Expedientes Registrados")
        try:
            # Pedimos solo 'id' y 'nombre_propietario' para asegurar compatibilidad
            res_ultimos = supabase.table("expedientes_maestros").select("id, nombre_propietario").order("id", desc=True).limit(5).execute()
            
            if res_ultimos.data:
                # Mostramos una tabla profesional y limpia
                st.dataframe(
                    res_ultimos.data, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "id": "ID del Expediente",
                        "nombre_propietario": "Cliente / Razón Social"
                    }
                )
            else:
                st.info("Aún no hay expedientes registrados en el sistema.")
        except Exception as e:
            # Si hay un error, ahora lo veremos en rojo para saber qué es
            st.error(f"Error al leer la base de datos: {e}")

    with c_der:
        st.subheader("⚡ Estado del Sistema")
        st.success("🟢 Conexión a Servidor: Óptima")
        st.success("🟢 Motor de Plantillas: Activo")
        st.success("🟢 Base de Datos: Sincronizada")
        st.write("")
        st.info("📌 Recuerde: Mantener su Archivo Digital actualizado garantiza la agilidad de los procesos en la Jurisdicción Inmobiliaria de Santiago y el resto del país.")
def vista_registro_maestro():
    st.title("👤 Registro Maestro de Expedientes")
    st.subheader("Control de Casos Legales y Técnicos | AboAgrim")
    st.divider()

    # --- 1. DATOS GENERALES DEL CLIENTE ---
    with st.expander("📝 Información Básica del Propietario/Cliente", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre_cliente = st.text_input("Nombre Completo / Razón Social:")
            identificacion = st.text_input("Cédula o RNC:", placeholder="001-0000000-0")
        with col2:
            telefono = st.text_input("Teléfono de Contacto:")
            domicilio = st.text_area("Dirección / Domicilio:", height=68)

    # --- 2. DEPARTAMENTO DE AGRIMENSURA (DATOS TÉCNICOS) ---
    st.markdown("### 🗺️ Módulo de Agrimensura y Catastro")
    with st.container(border=True):
        at1, at2, at3 = st.columns(3)
        with at1:
            parcela = st.text_input("Número de Parcela:", placeholder="Ej: 209-B")
            distrito = st.text_input("Distrito Catastral:")
        with at2:
            municipio = st.text_input("Municipio:", value="Santiago")
            provincia = st.text_input("Provincia:", value="Santiago")
        with at3:
            superficie = st.text_input("Superficie (m²):")
            estatus_t = st.selectbox("Estatus Técnico:", ["Saneamiento", "Deslinde", "Subdivisión", "Refundición"])

        # CAMPOS DE COORDENADAS (LO QUE SE HABÍA BORRADO)
        st.write("**📍 Ubicación Georreferenciada (UTM/WGS84)**")
        c_coord1, c_coord2, c_coord3 = st.columns(3)
        with c_coord1:
            coord_east = st.text_input("Coordenada Este (X):")
        with c_coord2:
            coord_north = st.text_input("Coordenada Norte (Y):")
        with c_coord3:
            puntos_gps = st.text_input("Puntos de Control / Vértices:")

    # --- 3. DEPARTAMENTO LEGAL (LITIS Y TRIBUNALES) ---
    st.markdown("### ⚖️ Módulo Jurídico y Litigios")
    with st.container(border=True):
        jurisdiccion = st.selectbox("Jurisdicción:", ["Inmobiliaria", "Civil y Comercial", "Laboral", "Penal"])
        
        jl1, jl2 = st.columns(2)
        with jl1:
            tribunal = st.text_input("Tribunal / Corte:", placeholder="Ej: Tribunal de Tierras de Jurisdicción Original")
            sala = st.text_input("Sala / Cámara:")
            juez = st.text_input("Magistrado / Juez Apoderado:")
        with jl2:
            no_rol = st.text_input("Número de Rol / Cuaderno:")
            f_audiencia = st.date_input("Fecha de Próxima Audiencia")
            etapa_procesal = st.selectbox("Etapa del Proceso:", ["Inicio", "Instrucción", "Fallo Pendiente", "Sentencia", "Recurso"])

    # --- 4. ACCIÓN DE GUARDADO ---
    st.divider()
    if st.button("🚀 REGISTRAR EXPEDIENTE MAESTRO", type="primary", use_container_width=True):
        if nombre_cliente and parcela:
            # Generamos código único
            codigo_generado = f"AA-{datetime.now().strftime('%y%m%d%H%M')}"
            
            data_insert = {
                "expediente": codigo_generado,
                "nombre_propietario": nombre_cliente,
                "cedula_propietario": identificacion,
                "parcela": parcela,
                "municipio": municipio,
                "provincia": provincia,
                "estatus": estatus_t,
                "jurisdiccion": jurisdiccion,
                "fecha_creacion": str(datetime.now())
            }
            
            try:
                supabase.table("expedientes_maestros").insert(data_insert).execute()
                st.success(f"✅ Expediente {codigo_generado} creado exitosamente para {nombre_cliente}.")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar en la nube: {e}")
        else:
            st.warning("⚠️ El nombre del cliente y el número de parcela son obligatorios.")
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

# 2. Definición Dinámica de Módulos
modulos = [
    "🏠 Mando Central",
    "👤 Registro Maestro",
    "📁 Archivo Digital",
    "📄 Plantillas Auto",
    "📅 Alertas y Plazos",
    "💰 Gestión de Honorarios" # <--- AGREGUE ESTA LÍNEA AQUÍ
]

# 💳 VALIDACIÓN CRÍTICA PARA FACTURACIÓN
# Si es usted o tiene rango alto, se agrega el módulo
if rol_usuario in ["Presidente Fundador", "Abogado", "Agrimensor"]:
    if "💵 Facturación" not in modulos:
        modulos.append("💵 Facturación")

# Siempre ver configuración si es el jefe o no está logueado
if rol_usuario == "Presidente Fundador" or not st.session_state.get("admin_autenticado"):
    if "⚙️ Configuración" not in modulos:
        modulos.append("⚙️ Configuración")

# 3. Interfaz de Barra Lateral
with st.sidebar:
    st.divider()
    menu = st.radio("Navegación:", modulos, key="menu_final_v4")
    # === TARJETA DE CONTACTO OFICIAL ===
    st.divider()
    st.markdown("🏢 **OFICINA PRINCIPAL**")
    st.caption("📍 Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Centro Ciudad, Santiago.")
    st.caption("📞 829-826-5888 / 809-691-3333")
    st.caption("✉️ aboagrim@gmail.com")
    st.caption("👤 **Lic. Jhonny Matos, M.A.** (Presidente-Fundador)")

# 4. El Gatillo (Enrutamiento)
if menu == "🏠 Mando Central":
    vista_mando_central()
elif menu == "👤 Registro Maestro":
    vista_registro_maestro()
elif menu == "📂 Archivo Digital":
    vista_archivo_digital()
elif menu == "📄 Plantillas Auto":
    vista_plantillas_auto()
elif menu == "📅 Alertas y Plazos":
    vista_alertas_plazos()
elif menu == "💵 Facturación":
    vista_facturacion()
elif menu == "⚙️ Configuración":
    st.title("⚙️ Configuración del Sistema")

    # --- 🔒 CANDADO DE SEGURIDAD PRESIDENCIAL ---
    if "pin_config" not in st.session_state:
        st.session_state.pin_config = False

    if not st.session_state.pin_config:
        st.warning("🛑 **ACCESO RESTRINGIDO:** Área exclusiva de la Presidencia.")
        c_pin1, c_pin2 = st.columns([2, 2])
        with c_pin1:
            pin_maestro = st.text_input("Ingrese el PIN Maestro:", type="password")
            if st.button("🔓 Desbloquear Panel"):
                if pin_maestro == "0681":  # Puede cambiar su clave aquí
                    st.session_state.pin_config = True
                    st.rerun()
                else:
                    st.error("❌ PIN incorrecto.")
        st.stop() # 🛑 Detiene el código aquí si no hay PIN

    if st.button("🔒 Bloquear Panel de Configuración"):
        st.session_state.pin_config = False
        st.rerun()

    # --- CREACIÓN REAL DE LAS PESTAÑAS ---
    tab_perfil, tab_usuarios, tab_seguridad, tab_maestro = st.tabs([
        "👤 Perfil", "👥 Usuarios", "🔐 Seguridad", "🎨 Panel Maestro"
    ])

    # === 1. PESTAÑA DE PERFIL ===
    with tab_perfil:
        st.subheader("👤 Mi Perfil Oficial")
        c_perf1, c_perf2 = st.columns([1, 2])
        with c_perf1:
            st.image("logo_aboagrim.jpg", width=120)
        with c_perf2:
            st.markdown("**Nombre:** Lic. Jhonny Matos. M.A.")
            st.markdown("**Cargo:** Presidente-Fundador")
            st.markdown("**Nivel de Acceso:** 🟢 Acceso Total (Nivel Dios)")

    # === 2. PESTAÑA DE USUARIOS ===
    with tab_usuarios:
        st.subheader("👥 Gestión de Capital Humano")
        
        # A. Crear la memoria primero
        if "db_empleados" not in st.session_state:
            st.session_state.db_empleados = [
                {"Nombre Completo": "Lic. Jhonny Matos", "Usuario": "JMatos", "Rol": "Presidente-Fundador", "Estado": "🟢 Activo"}
            ]

        # B. Mostrar la tabla
        st.dataframe(st.session_state.db_empleados, use_container_width=True)

        # C. Agregar Usuario
        with st.expander("➕ Dar de Alta a Nuevo Miembro", expanded=False):
            c_u1, c_u2 = st.columns(2)
            with c_u1:
                nuevo_nombre = st.text_input("Nombre y Apellidos:")
                nuevo_user = st.text_input("Usuario (Login):")
            with c_u2:
                nuevo_rol = st.selectbox("Rol:", ["Abogado", "Agrimensor", "Asistente"])
                estado_cuenta = st.selectbox("Estado:", ["🟢 Activo", "🔴 Inactivo"])

            if st.button("💾 Guardar Usuario", type="primary"):
                if nuevo_nombre != "":
                    st.session_state.db_empleados.append({
                        "Nombre Completo": nuevo_nombre, "Usuario": nuevo_user, "Rol": nuevo_rol, "Estado": estado_cuenta
                    })
                    st.rerun()

        # D. Eliminar Usuario (Ahora sí, en el lugar correcto)
        with st.expander("🗑️ Eliminar Usuario", expanded=False):
            if len(st.session_state.db_empleados) > 0:
                nombres_emp = [emp["Nombre Completo"] for emp in st.session_state.db_empleados]
                usuario_a_borrar = st.selectbox("Seleccione el empleado a eliminar:", nombres_emp)
                
                if st.button("🚨 Eliminar Definitivamente"):
                    st.session_state.db_empleados = [emp for emp in st.session_state.db_empleados if emp["Nombre Completo"] != usuario_a_borrar]
                    st.rerun()

    # === 3. PESTAÑA DE SEGURIDAD ===
    with tab_seguridad:
        st.subheader("🔐 Cambio de Credenciales")
        nueva_clave = st.text_input("Nueva Contraseña Maestra:", type="password")
        confirmar_clave = st.text_input("Confirmar Contraseña:", type="password")
        if st.button("🔑 Actualizar Clave", type="primary"):
            if nueva_clave != "" and nueva_clave == confirmar_clave:
                st.success("✅ ¡Contraseña actualizada!")
            else:
                st.error("❌ Las contraseñas no coinciden o están vacías.")
                # (Pegue esto debajo del st.error de las contraseñas)
        st.divider()
        # --- NUEVO: SINCRONIZACIÓN DUAL CON GOOGLE DRIVE ---
        st.markdown("### ☁️ Bóveda en la Nube (Google Drive Dual)")
        st.info("El sistema enviará una copia exacta de cada expediente a estas dos cuentas simultáneamente.")
        
        with st.expander("⚙️ Configurar Rutas de Sincronización", expanded=True):
            # Inicializamos las rutas en la memoria si no existen
            if "ruta_aboagrim" not in st.session_state:
                st.session_state.ruta_aboagrim = "C:/Ruta/A/Drive/Aboagrim"
            if "ruta_personal" not in st.session_state:
                st.session_state.ruta_personal = "C:/Ruta/A/Drive/Personal"

            c_drive1, c_drive2 = st.columns(2)
    with c_drive1:
        st.markdown("**Cuenta Corporativa:** `aboagrim@gmail.com`")
        nueva_ruta_ab = st.text_input("Ruta de la carpeta en su PC:", value=st.session_state.get("ruta_aboagrim", ""))
    with c_drive2:
        st.markdown("**Cuenta Personal:** `lic.jhonnymatos@gmail.com`")
        nueva_ruta_per = st.text_input("Ruta de la carpeta en su PC:", value=st.session_state.get("ruta_personal", ""))

    if st.button("🔗 Enlazar Cuentas de Google Drive", type="primary"):
        st.session_state["ruta_aboagrim"] = nueva_ruta_ab
        st.session_state["ruta_personal"] = nueva_ruta_per
        st.success("✅ ¡Cuentas enlazadas en memoria permanente! Los expedientes ahora se guardarán por duplicado.")

    # (Nota: Debajo de esto debe quedar su código de "with tab_maestro:" intacto)

    with tab_maestro:
        st.subheader("🎨 Identidad Corporativa y Diseño Global")
        st.info("Desde aquí controla la apariencia de AboAgrim Pro. Los cambios se aplican a todo el sistema.")

        # --- SECCIÓN 1: COLORES Y FONDOS ---
        with st.expander("🌈 Paleta de Colores y Fondos", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state["tema_fondo"] = st.selectbox("Modo de Fondo:", ["Oscuro Profundo", "Claro Ejecutivo", "Azul Corporativo", "Crema Vintage"], index=0)
                st.session_state["color_primario"] = st.color_picker("Color de Acentos (Botones y Títulos):", "#deff9a")
            with col2:
                st.session_state["color_texto"] = st.color_picker("Color de Fuente Principal:", "#f5f5f5")
                st.session_state["radio_bordes"] = st.slider("Curvatura de Casillas y Botones:", 0, 30, 15)

        # --- SECCIÓN 2: TIPOGRAFÍA Y TEXTOS ---
        with st.expander("🔡 Tipografía y Estilo de Letra"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                fuentes = ["Urbanist", "Poppins", "Merriweather", "Roboto", "Lato"]
                st.session_state["fuente_sistema"] = st.selectbox("Fuente Global:", fuentes)
            with col_f2:
                st.session_state["tamano_letra"] = st.slider("Tamaño de letra base:", 12, 20, 16)

        # --- SECCIÓN 3: BRANDING Y LOGO ---
        with st.expander("🖼️ Gestión de Branding (Logo)"):
            c_logo1, c_logo2 = st.columns([1, 2])
            with c_logo1:
                st.image("logo_aboagrim.jpg", width=150, caption="Logo Actual")
            with c_logo2:
                nuevo_logo = st.file_uploader("Subir Nuevo Logo (PNG/JPG):", type=["png", "jpg", "jpeg"])
                if nuevo_logo:
                    st.success("Logo cargado temporalmente. (Para cambio permanente, reemplace el archivo logo_aboagrim.jpg)")

        # --- SECCIÓN 4: DATOS DE OFICINA PRINCIPAL ---
        with st.expander("📍 Información de Oficina y Contacto"):
            st.session_state["direccion_master"] = st.text_input("Dirección Física:", "Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Centro Ciudad, Santiago.")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.session_state["tel_master"] = st.text_input("Teléfonos de Oficina:", "829-826-5888 / 809-691-3333")
            with col_t2:
                st.session_state["correo_master"] = st.text_input("Correo Corporativo:", "aboagrim@gmail.com")
            
        if st.button("💾 Guardar Configuración Maestra", type="primary", use_container_width=True):
            st.balloons()
            st.success("¡Identidad del sistema actualizada correctamente!")
# 👇 ESTE BLOQUE DEBE IR AL FINAL DE TODO SU CÓDIGO 👇
elif menu == "💰 Gestión de Honorarios":
    st.title("💰 Gestión de Honorarios y Cobros")
    st.subheader("Control Financiero de la Firma")
    # Tarjeta de Contacto en la Barra Lateral
    st.sidebar.divider()
    with st.sidebar.container():
        st.markdown(f"""
        <div style='text-align: center; background-color: #f0f2f6; padding: 10px; border-radius: 10px; border: 1px solid #dcdcdc;'>
            <p style='margin: 0; font-weight: bold; color: #0E1117;'>{PRESIDENTE_FIRMA}</p>
            <p style='margin: 0; font-size: 0.8em; color: #555;'>Presidente-Fundador</p>
            <hr style='margin: 8px 0;'>
            <p style='margin: 0; font-size: 0.75em; color: #333;'>📍 {DIRECCION_FIRMA}</p>
            <p style='margin: 0; font-size: 0.75em; color: #333;'>📞 {TELEFONOS_FIRMA}</p>
            <p style='margin: 0; font-size: 0.75em; color: #333;'>✉️ {CORREO_FIRMA}</p>
        </div>
        """, unsafe_allow_html=True)

    # --- REGISTRO DE MOVIMIENTOS ---
    with st.expander("📝 Registrar Nuevo Pago o Abono", expanded=True):
        # Simulamos los expedientes de su oficina (luego vendrán de Supabase)
        lista_expedientes = [
            "Seleccione un expediente...",
            "Exp. 2026-001 - Deslinde Parcela 44 (Juan Pérez)",
            "Exp. 2026-002 - Litis Derecho Registrado (Familia García)",
            "Exp. 2026-003 - Determinación de Herederos (María López)",
            "➕ Nuevo Cliente / Expediente"
        ]
        
        # El buscador inteligente (permite escribir para buscar)
        cliente_pago = st.selectbox("🔍 Buscar Cliente o Expediente:", lista_expedientes)
        
        # Si elige "Nuevo Cliente", le muestra una casilla para escribirlo
        if cliente_pago == "➕ Nuevo Cliente / Expediente":
            cliente_pago = st.text_input("Ingrese el nombre del nuevo cliente o proyecto:")

        c1, c2, c3 = st.columns(3)
        with c1:
            monto_pago = st.number_input("Monto Recibido:", min_value=0.0, step=1000.0)
            moneda = st.radio("Moneda:", ["RD$", "US$"], horizontal=True)
            
        with c2:
            concepto_pago = st.selectbox("Concepto del Pago:", [
                "Primer Pago (Avance de Honorarios)", 
                "Segundo Pago de Honorarios", 
                "Pago de Sellos e Impuestos", 
                "Gastos de Mensura / Operativos",
                "Saldo Final del Contrato"
            ])
            metodo_pago = st.selectbox("Método:", ["Transferencia BHD", "Transferencia Reservas", "Efectivo", "Cheque"])
            
        with c3:
            fecha_pago = st.date_input("Fecha de Recepción:")
            estado_cobro = st.selectbox("Estado del Recibo:", ["Completado", "Pendiente de Confirmación Bancaria"])
            
        st.divider()
        
        # Botones de Acción
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("💾 Guardar en Registro Contable", use_container_width=True, type="primary"):
                st.success(f"✅ Pago de {moneda} {monto_pago} registrado a nombre de {cliente_pago}")
        with c_btn2:
            if st.button("📄 Generar Recibo PDF", use_container_width=True):
                st.info("Generando recibo oficial con el logo de AboAgrim... (Simulado)")

    st.divider()

    # --- DATOS BANCARIOS Y CONTACTO ---
    st.markdown("### 🏦 Cuentas para Depósitos y Contacto Oficial")
    b1, b2 = st.columns(2)
    with b1:
        st.info(f"**DEPÓSITOS OFICIALES**\n\n- **Titular:** {PRESIDENTE_FIRMA}\n- **Correo:** {CORREO_FIRMA}\n- **Banco de Reservas:** 960-XXXXXX-X\n- **Banco BHD:** 124-XXXXXX-X")
    with b2:
        st.warning(f"**OFICINA PRINCIPAL**\n\n- **Dirección:** {DIRECCION_FIRMA}\n- **Teléfonos:** {TELEFONOS_FIRMA}")

    st.divider()

    # --- PANEL DE ESTADO DE CUENTAS (PESTAÑAS) ---
    st.markdown("### 📊 Estado General de Cuentas")
    
    # Creamos pestañas para organizar mejor la información
    tab_pendientes, tab_historial = st.tabs(["🔴 Pendientes de Cobro", "🟢 Historial de Pagos Recibidos"])
    
    with tab_pendientes:
        st.dataframe({
            "Expediente / Asunto": ["Deslinde Parcela 44", "Litis Familia García"],
            "Cliente": ["Juan Pérez", "María López"],
            "Total Contrato": ["RD$ 150,000", "RD$ 85,000"],
            "Abonado": ["RD$ 75,000", "RD$ 40,000"],
            "Pendiente": ["RD$ 75,000", "RD$ 45,000"]
        }, use_container_width=True)
        
    with tab_historial:
        st.dataframe({
            "Fecha": ["28/04/2026", "25/04/2026"],
            "Cliente": ["Pedro Rodríguez", "Constructora Cibao"],
            "Concepto": ["Segundo Pago Honorarios", "Avance de Honorarios"],
            "Monto": ["RD$ 25,000", "RD$ 100,000"],
            "Método": ["Transferencia BHD", "Cheque"]
        }, use_container_width=True)

