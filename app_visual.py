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
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
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
    from datetime import datetime
    import streamlit as st

    st.title("👤 Registro Maestro de Expedientes")
    st.markdown("### Control Integral de Actuaciones y Generales")

    # --- MEMORIA TEMPORAL ---
    if "db_expedientes" not in st.session_state:
        st.session_state["db_expedientes"] = {}
    if "contador_registro" not in st.session_state:
        st.session_state["contador_registro"] = 1

    ano_actual = datetime.now().year
    expediente_nuevo_sugerido = f"{ano_actual}-{st.session_state['contador_registro']:04d}"

    modo_accion = st.radio("Acción a realizar:", ["✨ Nuevo Expediente", "✏️ Modificar Existente", "🗑️ Borrar Expediente"], horizontal=True)

    exp_seleccionado = None
    if modo_accion != "✨ Nuevo Expediente":
        lista_exps = list(st.session_state["db_expedientes"].keys())
        if not lista_exps:
            st.warning("No hay expedientes registrados aún.")
        else:
            exp_seleccionado = st.selectbox("Seleccione el Expediente:", lista_exps)
            if modo_accion == "🗑️ Borrar Expediente" and exp_seleccionado:
                if st.button("🚨 Confirmar Borrado", type="primary"):
                    del st.session_state["db_expedientes"][exp_seleccionado]
                    st.success(f"Expediente {exp_seleccionado} eliminado.")
                    st.rerun()
                st.stop()

    st.write("---")
    exp_actual = exp_seleccionado if modo_accion == "✏️ Modificar Existente" else expediente_nuevo_sugerido
    st.markdown(f"#### 📂 Trabajando en Expediente: **{exp_actual}**")

    tab_base, tab_partes, tab_prof, tab_inmueble = st.tabs([
        "📄 Datos Base", "👥 Partes Involucradas", "⚖️ Profesionales", "📍 Inmueble y Título"
    ])

    with tab_base:
        st.subheader("Información del Trámite")
        c1, c2 = st.columns(2)
        with c1:
            lista_tramites = [
                "--- MENSURAS CATASTRALES ---", "Saneamiento", "Deslinde", "Subdivisión", "Refundición", "Urbanización", "Constitución de Condominio", "Modificación de Condominio", "Actualización de Mensura",
                "--- JURISDICCIÓN Y REGISTRO ---", "Transferencia (Venta / Donación)", "Determinación de Herederos", "Litis sobre Derechos Registrados", "Inscripción de Hipoteca / Privilegio", "Cancelación de Hipoteca", "Corrección de Error Material", "Pérdida o Deterioro de Título", "Inscripción de Litis / Oposición", "Certificación de Estado Jurídico",
                "--- OTROS ---", "✍️ Otro (Especificar Nuevo)"
            ]
            tramite_sel = st.selectbox("Tipo de Trámite:", lista_tramites)
            if tramite_sel.startswith("---"):
                st.warning("☝️ Seleccione un trámite válido de la lista o elija 'Otro'.")
                tramite_final = ""
            elif tramite_sel == "✍️ Otro (Especificar Nuevo)":
                tramite_final = st.text_input("Escriba el nombre exacto del trámite:")
            else:
                tramite_final = tramite_sel

        with c2:
            jurisdiccion = st.selectbox("Órgano Jurisdiccional:", ["Tribunal de Tierras (Original)", "Tribunal Superior de Tierras", "Mensuras Catastrales", "Registro de Títulos"])
            estado_exp = st.selectbox("Estado Actual:", ["Recepción", "En Proceso", "Observado", "Aprobado", "En Litigio", "Cerrado"])

    with tab_partes:
        with st.expander("🟢 Parte Activa (Solicitantes / Demandantes / Compradores / Propietarios)"):
            tipo_activa = st.multiselect("Rol(es):", ["Solicitante", "Demandante", "Reclamante", "Comprador", "Acreedor", "Dueño/Propietario"])
            nombre_activa = st.text_input("Nombre / Razón Social (Parte Activa):")
            c_act1, c_act2 = st.columns(2)
            c_act1.text_input("Cédula / Pasaporte / RNC (Parte Activa):")
            c_act2.text_input("Nacionalidad y Estado Civil:")
            st.text_input("Profesión / Oficio (Parte Activa):")
            st.text_area("Domicilio Exacto (Parte Activa):", height=68)

        with st.expander("🔴 Parte Pasiva (Demandados / Vendedores / Deudores / Inquilinos)"):
            tipo_pasiva = st.multiselect("Rol(es) Pasivos:", ["Demandado", "Vendedor", "Deudor", "Inquilino", "Arrendatario"])
            nombre_pasiva = st.text_input("Nombre / Razón Social (Parte Pasiva):")
            c_pas1, c_pas2 = st.columns(2)
            c_pas1.text_input("Cédula / Pasaporte / RNC (Parte Pasiva):")
            c_pas2.text_input("Nacionalidad y Estado Civil (Pasiva):")
            st.text_area("Domicilio Exacto (Parte Pasiva):", height=68)

    with tab_prof:
        with st.expander("📐 Técnica (Agrimensores)"):
            st.text_input("Nombre del Agrimensor:")
            c_ag1, c_ag2 = st.columns(2)
            c_ag1.text_input("Cédula (Agrimensor):")
            c_ag2.text_input("Codiatur (CODIA):")
        with st.expander("⚖️ Legal (Abogados / Notarios)"):
            st.text_input("Nombre del Abogado / Notario:")
            c_ab1, c_ab2 = st.columns(2)
            c_ab1.text_input("Cédula (Legal):")
            c_ab2.text_input("Colegiatura (CARD / Matrícula Notarial):")
        with st.expander("🤝 Mandatarios (Apoderados / Gestores / Autorizados)"):
            st.text_input("Nombre del Apoderado o Gestor:")
            c_ap1, c_ap2 = st.columns(2)
            c_ap1.text_input("Calidad (Ej. Apoderado Especial):")
            c_ap2.text_input("Cédula del Apoderado:")

    with tab_inmueble:
        c_inm1, c_inm2, c_inm3 = st.columns(3)
        with c_inm1:
            st.text_input("Provincia:")
            st.text_input("Parcela / Solar:")
            st.text_input("Matrícula No.:")
        with c_inm2:
            st.text_input("Municipio:")
            st.text_input("Distrito Catastral (DC):")
            st.text_input("Libro:")
        with c_inm3:
            st.text_input("Sector / Paraje:")
            st.text_input("Manzana:")
            st.text_input("Folio:")
            
        c_sup1, c_sup2 = st.columns(2)
        c_sup1.text_input("Superficie Total (Metros Cuadrados):")
        c_sup2.text_input("Designación Posicional:")
        
        c_lin1, c_lin2, c_lin3, c_lin4 = st.columns(4)
        c_lin1.text_input("Norte:")
        c_lin2.text_input("Sur:")
        c_lin3.text_input("Este:")
        c_lin4.text_input("Oeste:")

    st.write("---")
    if st.button("💾 GUARDAR / ACTUALIZAR EXPEDIENTE", type="primary", use_container_width=True):
        if not tramite_final:
            st.error("Debe especificar el tipo de trámite.")
        else:
            st.session_state["db_expedientes"][exp_actual] = {"tramite": tramite_final, "jurisdiccion": jurisdiccion, "estado": estado_exp}
            if modo_accion == "✨ Nuevo Expediente":
                st.session_state["contador_registro"] += 1
            st.success(f"✅ ¡Expediente {exp_actual} guardado exitosamente!")
            st.rerun()
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

def motor_de_fabricacion_final(cliente_nombre, tramite_nombre, expediente_num, organo_ji):
        cli_limpio = cliente_nombre.replace("/", "-").strip() if cliente_nombre else "Sin_Cliente"
        tram_limpio = tramite_nombre.replace("/", "-").strip() if tramite_nombre else "Sin_Tramite"
        exp_limpio = expediente_num.replace("/", "-").strip()
        
        nombre_carpeta = f"{organo_ji}_{exp_limpio} - {cli_limpio} - {tram_limpio}"
        
        ruta_sede = "Carpeta_Temporal_Nube"
        ruta_fisica = os.path.join(ruta_sede, nombre_carpeta)
        
        os.makedirs(ruta_fisica, exist_ok=True)
        
        # --- 2. EMPAQUETADO DE DATOS ---
        diccionario_datos = {
            "expediente_ji": ji_exp_ji if 'ji_exp_ji' in locals() else "",
            "ubicacion": ji_ubicacion if 'ji_ubicacion' in locals() else "Santiago",
            "area": ji_area if 'ji_area' in locals() else "",
            "coordenadas": ji_coordenadas if 'ji_coordenadas' in locals() else "",
            "demandante": ji_demandante if 'ji_demandante' in locals() else "",
            "demandado": ji_demandado if 'ji_demandado' in locals() else "",
            "cliente_nombre": cli_limpio,
            "tramite_nombre": tram_limpio,
            "organo_ji": organo_ji,
            "expediente_num": exp_limpio
        }

        # --- SINCRONIZACIÓN CON LA NUBE (SUPABASE) ---
        try:
        
            # Datos listos para su tabla "Maestros de Expedientes"
            datos_nube = {
                "expediente_ji": expediente_num,
                "nombre_propietario": cliente_nombre,
                "tramite_tipo": tramite_nombre,
                "jurisdiccion": organo_ji,
                "estatus": "Registrado",
                "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
            # Subida automática a Supabase
            res = supabase.table("expedientes_maestros").insert(datos_nube).execute()
            
            if res.data:
                st.info("☁️ Expediente sincronizado con la nube exitosamente.")
        
        except Exception as e:
            st.error(f"❌ Error de conexión con la nube: {e}")
        
        # --- 3. FORJA Y GUARDADO ---
        st.session_state["bandeja_descargas"] = []
        archivos_creados = 0
        
        for plantilla in plantillas_elegidas:
            ruta_exacta = f"plantillas_maestras/{plantilla}"
            buffer = generar_documento_word(ruta_exacta, diccionario_datos)
            
            if buffer:
                nombre_limpio = plantilla.split('/')[-1]
                nombre_final_word = f"{organo_ji}_{nombre_limpio}"
                ruta_guardado_word = os.path.join(ruta_fisica, nombre_final_word)
                
                with open(ruta_guardado_word, "wb") as f:
                    f.write(buffer.getvalue())
                    
                st.session_state["bandeja_descargas"].append({
                    "nombre": nombre_final_word,
                    "buffer": buffer
                })
                archivos_creados += 1
                                    
            # --- 4. CONEXIÓN CON EL ARCHIVO DIGITAL ---
            if archivos_creados > 0:
                archivo_memoria = "memoria_expedientes.json"
                memoria = {}
                if os.path.exists(archivo_memoria):
                    with open(archivo_memoria, "r") as f:
                        memoria = json.load(f)
                        
                memoria[exp_limpio] = {
                    "carpeta_relativa": nombre_carpeta,
                    "organo": organo_ji,
                    "cliente": cli_limpio
                }
                
                with open(archivo_memoria, "w") as f:
                    json.dump(memoria, f, indent=4)
                    
                st.success(f"✅ ¡Éxito Total! Se forjaron {archivos_creados} documentos y se guardaron en la bóveda local bajo: {nombre_carpeta}")
            else:
                st.error("❌ Ocurrió un error al forjar los documentos. Verifique las plantillas.")
                                        
        
                # (Asegúrese de que esta 'r' quede a la misma altura que el 'if' o 'else' de arriba)
            ruta_limpieza = f"plantillas_maestras/{carpeta_borrar}"
            archivos = os.listdir(ruta_limpieza) if os.path.exists(ruta_limpieza) else []
        
            if archivos:
                archivo_a_borrar = st.selectbox("Seleccione el archivo a eliminar:", archivos)
                if st.button("🗑️ Eliminar Plantilla"):
                    try:
                        os.remove(f"{ruta_limpieza}/{archivo_a_borrar}")
                        st.success(f"✅ Archivo {archivo_a_borrar} eliminado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al eliminar: {e}")
            else:
                st.info("ℹ️ Carpeta vacía. No hay modelos para borrar.")

# Aquí sigue def generar_documento_word(nombre_plantilla, diccionario_datos):
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
                    # 1. Clientes y Apoderados
                    cl_nombres = " y ".join([c['nombre'] for c in lista_clientes]) if lista_clientes else "N/A"
                    cl_generales = "; y ".join([f"{c['nombre']}, dominicano(a), mayor de edad, portador(a) de la cédula No. {c['cedula']}, domiciliado(a) en {c['domicilio']}, Tel: {c['telefono']}, Email: {c['email']}" for c in lista_clientes]) if lista_clientes else "N/A"
                    
                    ap_nombres = " y ".join([a['nombre'] for a in lista_apoderados]) if lista_apoderados else "N/A"
                    ap_generales = "; y ".join([f"{a['nombre']}, dominicano(a), mayor de edad, portador(a) de la cédula No. {a['cedula']}, actuando en calidad de {a['calidad']}, con domicilio en {a['domicilio']}, Contacto: {a['contacto']}" for a in lista_apoderados]) if lista_apoderados else "N/A"

                    # 2. Profesionales
                    ab_nombres = " y ".join([a['nombre'] for a in lista_abogados]) if lista_abogados else "N/A"
                    ab_generales = "; y ".join([f"{a['nombre']}, portador(a) de la cédula No. {a['cedula']}, CARD {a['matricula']}, estudio en {a['domicilio']}, Tel: {a['telefono']}, Email: {a['email']}" for a in lista_abogados]) if lista_abogados else "N/A"
                    
                    ag_nombres = " y ".join([a['nombre'] for a in lista_agrimensores]) if lista_agrimensores else "N/A"
                    ag_generales = "; y ".join([f"{a['nombre']}, cédula No. {a['cedula']}, CODIA {a['matricula']}, oficina en {a['domicilio']}, Tel: {a['telefono']}, Email: {a['email']}" for a in lista_agrimensores]) if lista_agrimensores else "N/A"
                    
                    no_nombres = " y ".join([a['nombre'] for a in lista_notarios]) if lista_notarios else "N/A"
                    no_generales = "; y ".join([f"{a['nombre']}, Notario de {a['domicilio']}, Matrícula {a['matricula']}, cédula No. {a['cedula']}, Tel: {a['telefono']}" for a in lista_notarios]) if lista_notarios else "N/A"
                    
                    al_nombres = " y ".join([a['nombre'] for a in lista_alguaciles]) if lista_alguaciles else "N/A"
                    al_generales = "; y ".join([f"{a['nombre']}, cédula No. {a['cedula']}, Alguacil del {a['matricula']}, Tel: {a['telefono']}" for a in lista_alguaciles]) if lista_alguaciles else "N/A"

                    # 3. Inmuebles
                    in_descripciones = "\n".join([f"Parcela {i['parcela']}, DC {i['dc']}, {i['provincia']}. Superficie: {i['superficie']}. Coordenadas: {i['coord']}. Sustentado en {i['tipo_doc']} No. {i['numero']}, Libro {i['libro']}, Folio {i['folio']}, inscrito en fecha {i['fecha_ins']}." for i in lista_inmuebles]) if lista_inmuebles else "N/A"

                    # 4. Transacciones y Depositantes
                    pg_detalles = "\n".join([f"Monto de {p['monto']} pagadero mediante {p['forma']} ({p['banco']})." for p in lista_pagos]) if lista_pagos else "N/A"
                    
                    de_nombres = " y ".join([d['nombre'] for d in lista_depositantes]) if lista_depositantes else "N/A"
                    de_generales = "; y ".join([f"{d['nombre']}, portador(a) de la cédula No. {d['cedula']}, en calidad de {d['calidad']}, Tel: {d['telefono']}, Email: {d['email']}" for d in lista_depositantes]) if lista_depositantes else "N/A"

                    impuestos_str = ", ".join(impuestos_pagados) if impuestos_pagados else "N/A"
                    
                    # MEGA DICCIONARIO
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
                        st.success(f"⚖️ ¡Impecable! Se redactaron {archivos_generados} documentos con generales e inmuebles múltiples.")

    with tab_boveda:
        st.subheader("Gestión de Archivos Maestros (.docx)")
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
# 4. El Gatillo (Enrutamiento)
if menu == "🏠 Mando Central":
    vista_mando()
elif menu == "👤 Registro Maestro":
    vista_registro_maestro()
elif menu == "📁 Archivo Digital":
    vista_archivo_digital()
elif menu == "📄 Plantillas Auto":
    vista_plantillas()  # <-- Quite el "_auto" para que llame a la función correcta
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
            # --- MEMORIA DE DISCO DURO (Sobrevive a actualizaciones de pantalla) ---
            
            archivo_rutas = "config_rutas.json"
            
            # 1. Leer el archivo secreto si existe
            ruta_ab_guardada = ""
            ruta_per_guardada = ""
            if os.path.exists(archivo_rutas):
                try:
                    with open(archivo_rutas, "r") as f:
                        datos_rutas = json.load(f)
                        ruta_ab_guardada = datos_rutas.get("corporativa", "")
                        ruta_per_guardada = datos_rutas.get("personal", "")
                except:
                    pass

            c_drive1, c_drive2 = st.columns(2)
            with c_drive1:
                st.markdown("**Cuenta Corporativa:** `aboagrim@gmail.com`")
                nueva_ruta_ab = st.text_input("ID de la Carpeta Google Drive:", value=ruta_ab_guardada)
            
            with c_drive2:
                st.markdown("**Cuenta Personal:** `lic.jhonnymatos@gmail.com`")
                nueva_ruta_per = st.text_input("Ruta en su PC personal: ", value=ruta_per_guardada)

            if st.button("🔗 Enlazar Cuentas de Google Drive", type="primary"):
                # 2. Guardar las rutas en el archivo físico
                with open(archivo_rutas, "w") as f:
                    json.dump({"corporativa": nueva_ruta_ab, "personal": nueva_ruta_per}, f)
                st.success("✅ ¡Rutas tatuadas en el disco duro! Ya no se borrarán al actualizar la pantalla.")

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

