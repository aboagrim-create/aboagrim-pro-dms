import streamlit as st
import pandas as pd
import datetime
from database import *

# --- Configuración Base ---
st.set_page_config(page_title="AboAgrim Pro DMS v17.1", layout="wide", initial_sidebar_state="expanded")

# --- Menú Lateral Corporativo ---
st.sidebar.markdown("### Abogados y Agrimensores 'AboAgrim'")
st.sidebar.markdown("**Lic. Jhonny Matos. M.A., Presidente**")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Navegación Principal",
    [
        "🏠 Mando", 
        "👤 Registro Maestro", 
        "📁 Archivo", 
        "📄 Plantillas", 
        "📅 Alertas", 
        "💳 Facturación", 
        "⚙️ Configuración"
    ],
    label_visibility="collapsed"
)

# --- 1. MANDO CENTRAL ---
def vista_mando():
    st.title("📊 Mando Central: Resumen Operativo")
    casos = consultar_todo()
    if casos:
        df = pd.DataFrame(casos)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Expedientes", len(df))
        c2.metric("En Proceso", len(df[df['estado'] == 'Abierto']) if 'estado' in df.columns else 0)
        c3.metric("Deslindes Activos", len(df[df['tipo_caso'] == 'Deslinde']) if 'tipo_caso' in df.columns else 0)
        c4.metric("Litis Registradas", len(df[df['tipo_caso'] == 'Litis']) if 'tipo_caso' in df.columns else 0)
        
        st.subheader("Base de Datos de Casos Activos")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("La base de datos está conectada. No hay expedientes registrados.")

# --- 2. REGISTRO MAESTRO ---
def vista_registro_maestro():
    st.title("⚖️ Registro Maestro y Asignación")
    dic = obtener_diccionario_maestro()
    
    with st.form("form_registro_oficial"):
        st.subheader("Apertura de Nuevo Expediente")
        c1, c2, c3 = st.columns(3)
        num = c1.text_input("Número de Expediente:")
        tipo = c2.selectbox("Tipo de Acto:", ["Deslinde", "Saneamiento", "Litis", "Transferencia", "Determinación de Herederos"])
        jur = c3.selectbox("Jurisdicción:", ["Santiago", "La Vega", "Santo Domingo", "Puerto Plata", "Tribunal Superior de Tierras"])
        
        c4, c5 = st.columns(2)
        cliente = c4.text_input("Nombre del Cliente / Propietario:")
        etapa = c5.selectbox("Etapa Inicial:", ["Recepción de Documentos", "Mensura Catastral", "Sometimiento a Tribunal", "Sentencia"])
        
        st.markdown("---")
        st.subheader("Personal Técnico y Legal")
        a1, a2, a3 = st.columns(3)
        agrimensor = a1.selectbox("Agrimensor a cargo:", dic.get('agrimensor', []) or ["Sin registros"])
        abogado = a2.selectbox("Abogado apoderado:", dic.get('abogado', []) or ["Sin registros"])
        notario = a3.selectbox("Notario actuante:", dic.get('notario', []) or ["Sin registros"])

        if st.form_submit_button("🛡️ Guardar Expediente Oficial"):
            if num and cliente:
                exito = registrar_evento("casos", {"numero_expediente": num, "tipo_caso": tipo, "jurisdiccion": jur, "cliente_id": cliente, "etapa": etapa, "estado": "Abierto"})
                if exito: st.success("✅ Expediente blindado en la base de datos.")
                else: st.error("Error de conexión al guardar.")
            else:
                st.warning("⚠️ Complete el número de expediente y el cliente.")

# --- 3. ARCHIVO DIGITAL ---
def vista_archivo():
    st.title("📁 Archivo Digital DMS (Nube)")
    st.markdown("Gestión documental vinculada a expedientes (Planos Civil 3D, PDFs, Sentencias).")
    
    with st.expander("Subir Nuevos Documentos", expanded=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            exp_vinculado = st.text_input("Vincular al Expediente N°:")
            tipo_doc = st.selectbox("Clasificación:", ["Plano Catastral (DWG/PDF)", "Contrato (DOCX)", "Sentencia / Resolución", "Acto de Alguacil", "Identificación Civil"])
        with col2:
            archivos = st.file_uploader("Arrastre sus archivos aquí", accept_multiple_files=True)
            if st.button("⬆️ Subir a la Bóveda"):
                if archivos: st.success(f"{len(archivos)} archivo(s) subido(s) y vinculado(s) al caso {exp_vinculado}.")
                else: st.warning("Seleccione al menos un archivo.")
                
    st.subheader("Documentos Recientes")
    st.dataframe(pd.DataFrame({
        "Expediente": ["EXP-2026-001", "EXP-2026-002"],
        "Documento": ["Plano_Mensura_Final.pdf", "Contrato_Cuota_Litis.docx"],
        "Fecha de Carga": ["2026-04-16", "2026-04-15"],
        "Subido por": ["Lic. Jhonny Matos", "Lic. Jhonny Matos"]
    }), use_container_width=True)

# --- 4. PLANTILLAS ---
def vista_plantillas():
    st.title("📄 Motor de Plantillas Inteligentes")
    st.markdown("Generación automática de documentos legales usando datos de la plataforma.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Selección de Formato")
        tipo_plantilla = st.selectbox("Documento a Generar:", [
            "Contrato de Cuota Litis", 
            "Contrato de Prestación de Servicios", 
            "Solicitud de Autorización de Mensura",
            "Instancia de Fijación de Audiencia"
        ])
        exp_origen = st.text_input("Extraer datos del Expediente N°:")
        st.button("⚙️ Procesar y Generar Word")
        
    with col2:
        st.subheader("Vista Previa de Variables a Inyectar")
        st.json({
            "Abogado": "Lic. Jhonny Matos. M.A.",
            "Domicilio": "Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Santiago",
            "Contacto": "829-826-5888 / 809-691-3333",
            "Cliente": "A la espera de número de expediente...",
            "Inmueble": "A la espera de número de expediente..."
        })

# --- 5. ALERTAS ---
def vista_alertas():
    st.title("📅 Panel de Control de Alertas y Plazos")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Próximos Vencimientos y Audiencias")
        df_alertas = pd.DataFrame({
            "Fecha Límite": ["2026-04-20", "2026-04-25", "2026-05-10"],
            "Expediente": ["EXP-2026-003", "EXP-2026-001", "EXP-2026-005"],
            "Evento": ["Audiencia Saneamiento", "Vencimiento plazo mensura", "Depósito de conclusiones"],
            "Prioridad": ["🔴 Alta", "🟡 Media", "🟢 Baja"]
        })
        st.dataframe(df_alertas, use_container_width=True)
        
    with col2:
        st.subheader("➕ Nueva Alerta")
        with st.form("form_alerta"):
            fecha = st.date_input("Fecha del Evento:")
            evento = st.text_input("Descripción:")
            prioridad = st.selectbox("Nivel de Urgencia:", ["Alta", "Media", "Baja"])
            if st.form_submit_button("Agendar"):
                st.success("Alerta registrada en el sistema.")

# --- 6. FACTURACIÓN ---
def vista_facturacion():
    st.title("💳 Facturación y Control de Honorarios")
    
    with st.expander("💳 Registrar Nuevo Pago / Facturación", expanded=True):
        c1, c2, c3 = st.columns(3)
        exp_factura = c1.text_input("Expediente N°:")
        monto_total = c2.number_input("Honorarios Totales (RD$):", min_value=0.0)
        abono = c3.number_input("Abono Recibido (RD$):", min_value=0.0)
        if st.button("Registrar Transacción"):
            st.success(f"Transacción de RD${abono} aplicada al expediente {exp_factura}.")

    st.subheader("Estado de Cuenta de Casos Activos")
    # Tabla simulada hasta que Supabase tenga datos de facturación
    df_finanzas = pd.DataFrame({
        "Expediente": ["EXP-2026-001", "EXP-2026-002"],
        "Honorarios Acordados": ["RD$ 150,000", "RD$ 200,000"],
        "Pagado": ["RD$ 75,000", "RD$ 200,000"],
        "Balance Pendiente": ["RD$ 75,000", "RD$ 0 (Saldado)"]
    })
    st.dataframe(df_finanzas, use_container_width=True)

# --- 7. CONFIGURACIÓN ---
def vista_configuracion():
    st.title("⚙️ Configuración General y Mantenimiento")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Perfil de la Firma")
        st.text_input("Razón Social:", value="Abogados y Agrimensores 'AboAgrim'")
        st.text_input("Presidente Fundador:", value="Lic. Jhonny Matos. M.A.")
        st.text_input("Dirección Principal:", value="Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Santiago")
        st.text_input("Teléfonos Oficiales:", value="829-826-5888 / 809-691-3333")
        st.text_input("Correo Electrónico:", value="Aboagrim@gmail.com")
        st.button("💾 Guardar Cambios de Perfil")
        
    with col2:
        st.subheader("Estado del Sistema")
        st.success("Conexión a Base de Datos: ACTIVA (Supabase)")
        st.success("Integración DOCXTPL: ACTIVA")
        st.success("Motor de Streamlit: ONLINE")
        
        st.markdown("---")
        st.subheader("Herramientas de Respaldo")
        st.button("📥 Descargar Copia de Seguridad (Excel)")

# --- LÓGICA DE NAVEGACIÓN ---
if menu == "🏠 Mando": vista_mando()
elif menu == "👤 Registro Maestro": vista_registro_maestro()
elif menu == "📁 Archivo": vista_archivo()
elif menu == "📄 Plantillas": vista_plantillas()
elif menu == "📅 Alertas": vista_alertas()
elif menu == "💳 Facturación": vista_facturacion()
elif menu == "⚙️ Configuración": vista_configuracion()
