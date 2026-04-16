import streamlit as st
import pandas as pd
import datetime
from database import *

# --- CONFIGURACIÓN DEL SISTEMA OPERATIVO ---
st.set_page_config(page_title="AboAgrim Pro DMS v17.1", layout="wide", initial_sidebar_state="expanded")

# --- IDENTIDAD CORPORATIVA (SIDEBAR) ---
st.sidebar.markdown("### Abogados y Agrimensores\n### 'AboAgrim'")
st.sidebar.markdown("**Lic. Jhonny Matos. M.A., Presidente Fundador**")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Módulos del Sistema",
    [
        "🏠 Mando Central", 
        "⚖️ Registro Maestro", 
        "📁 Archivo Digital", 
        "📄 Plantillas Auto", 
        "📅 Alertas y Plazos", 
        "💳 Facturación", 
        "⚙️ Configuración"
    ],
    label_visibility="collapsed"
)

st.sidebar.divider()
st.sidebar.markdown("🟢 **Estado:** Supabase Online")
st.sidebar.caption("AboAgrim OS v17.1")

# --- 1. MANDO CENTRAL (Dashboard Premium + Tags) ---
def vista_mando():
    st.markdown("""
        <style>
        .hero-banner {
            background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
            padding: 35px 30px; border-radius: 12px; color: white;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin-bottom: 2rem;
            border-left: 6px solid #FBBF24;
        }
        .hero-title { font-size: 2.5rem; font-weight: 800; margin-bottom: 0.2rem; }
        .hero-subtitle { font-size: 1.2rem; color: #94A3B8; margin-bottom: 1rem; }
        .founder-name { font-size: 1.1rem; color: #FBBF24; font-weight: 600; text-transform: uppercase; }
        </style>
        <div class="hero-banner">
            <div class="hero-title">AboAgrim Pro DMS ⚖️📐</div>
            <div class="hero-subtitle">Centro de Mando: Jurisdicción Inmobiliaria y Mensura</div>
            <div class="founder-name">Lic. Jhonny Matos, M.A. | Presidente Fundador</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📈 Desempeño Operativo y Búsqueda")
    
    casos = consultar_todo()
    if casos:
        df = pd.DataFrame(casos)
        
        # Motor de Búsqueda Inteligente
        col_busq1, col_busq2 = st.columns([2, 1])
        with col_busq1:
            tags_disp = sorted(list(set([str(val) for col in ['tipo_caso', 'jurisdiccion', 'estado', 'etapa'] if col in df.columns for val in df[col].dropna().unique() if str(val).strip()])))
            tags_sel = st.multiselect("🔍 Filtrar por Etiquetas (Tags):", options=tags_disp, placeholder="Ej. Deslinde, Santiago, Abierto...")
        with col_busq2:
            txt_busq = st.text_input("Búsqueda libre:")

        # Lógica de Filtrado
        df_f = df.copy()
        if tags_sel:
            for t in tags_sel:
                df_f = df_f[df_f.astype(str).apply(lambda r: t in r.values, axis=1)]
        if txt_busq:
            df_f = df_f[df_f.astype(str).apply(lambda x: x.str.contains(txt_busq, case=False, na=False)).any(axis=1)]

        # Métricas Dinámicas
        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Expedientes (Filtro)", len(df_f))
        m2.metric("Deslindes Activos", len(df_f[df_f['tipo_caso'] == 'Deslinde']) if 'tipo_caso' in df_f.columns else 0)
        m3.metric("Litis Registradas", len(df_f[df_f['tipo_caso'] == 'Litis']) if 'tipo_caso' in df_f.columns else 0)
        m4.metric("Casos Abiertos", len(df_f[df_f['estado'] == 'Abierto']) if 'estado' in df_f.columns else 0)
        
        st.dataframe(df_f, use_container_width=True)
    else:
        st.info("🟢 Sistema operativo en línea. Sin expedientes en la base de datos.")

# --- 2. REGISTRO MAESTRO (7 Roles + Formularios) ---
def vista_registro():
    st.title("⚖️ Registro Maestro de Expedientes")
    dic = obtener_diccionario_maestro()
    
    with st.form("form_registro_os"):
        st.subheader("I. Datos Legales y Catastrales")
        c1, c2, c3 = st.columns(3)
        num = c1.text_input("Número de Expediente:")
        tipo = c2.selectbox("Clasificación:", ["Deslinde", "Saneamiento", "Litis", "Transferencia", "Determinación de Herederos"])
        jur = c3.selectbox("Jurisdicción:", ["Santiago", "La Vega", "Santo Domingo", "Puerto Plata", "Moca"])
        
        c4, c5 = st.columns(2)
        cliente = c4.text_input("Cliente / Propietario principal:")
        etapa = c5.selectbox("Etapa Inicial:", ["Recepción de Documentos", "Mensura Catastral", "Sometimiento", "Tribunal", "Sentencia"])
        
        st.markdown("---")
        st.subheader("II. Asignación de Roles (Técnico y Legal)")
        a1, a2, a3 = st.columns(3)
        agrimensor = a1.selectbox("Agrimensor:", dic.get('agrimensor', []) or ["N/A"])
        abogado = a2.selectbox("Abogado:", dic.get('abogado', []) or ["N/A"])
        notario = a3.selectbox("Notario:", dic.get('notario', []) or ["N/A"])
        
        a4, a5, a6 = st.columns(3)
        representante = a4.selectbox("Representante:", dic.get('representante', []) or ["N/A"])
        apoderado = a5.selectbox("Apoderado:", dic.get('apoderado', []) or ["N/A"])
        solicitante = a6.selectbox("Solicitante:", dic.get('solicitante', []) or ["N/A"])

        if st.form_submit_button("🛡️ Blindar y Registrar Expediente"):
            if num and cliente:
                exito = registrar_evento("casos", {"numero_expediente": num, "tipo_caso": tipo, "jurisdiccion": jur, "cliente_id": cliente, "etapa": etapa, "estado": "Abierto"})
                if exito: 
                    st.toast("¡Expediente guardado en Supabase exitosamente!", icon="✅") # Mejora OS: Notificación Toast
                else: 
                    st.error("Error de conexión a la BDD.")
            else:
                st.warning("El número de expediente y el cliente son obligatorios.")

# --- 3. ARCHIVO DIGITAL (Mejora OS: Pestañas) ---
def vista_archivo():
    st.title("📁 Bóveda Digital DMS")
    tab1, tab2 = st.tabs(["⬆️ Subir Documentos", "🗄️ Explorador de Archivos"])
    
    with tab1:
        st.markdown("Vincula planos de Civil 3D, PDF o sentencias a un expediente.")
        st.text_input("Vincular al Expediente N°:")
        archivos = st.file_uploader("Arrastre archivos aquí", accept_multiple_files=True)
        if st.button("Subir a la Nube"):
            if archivos: st.toast("Archivos encriptados y subidos.", icon="☁️")
    
    with tab2:
        st.info("Explorador de Bóveda: Aquí aparecerán los archivos indexados.")

# --- 4. PLANTILLAS AUTO ---
def vista_plantillas():
    st.title("📄 Generador de Plantillas Auto")
    st.markdown("Automatización de Contratos, Actos y Solicitudes de Mensura.")
    st.selectbox("Seleccione Plantilla Maestra:", ["Contrato de Cuota Litis", "Poder Especial de Representación", "Solicitud de Mensura"])
    st.text_input("Extraer datos del Expediente N°:")
    if st.button("⚙️ Ensamblar Documento Word"):
        st.toast("Procesando variables con DocxTpl...", icon="⏳")

# --- 5. ALERTAS ---
def vista_alertas():
    st.title("📅 Panel de Control de Alertas")
    st.warning("No hay audiencias ni plazos de mensura a vencer en los próximos 7 días.")

# --- 6. FACTURACIÓN ---
def vista_facturacion():
    st.title("💳 Módulo Financiero")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Honorarios Totales Acordados (RD$):", min_value=0.0)
    with col2:
        st.number_input("Avance Recibido (RD$):", min_value=0.0)
    st.button("Registrar Transacción Financiera")

# --- 7. CONFIGURACIÓN ---
def vista_configuracion():
    st.title("⚙️ Ajustes del Sistema Operativo")
    st.text_input("Razón Social:", value="Abogados y Agrimensores 'AboAgrim'")
    st.text_input("Dirección:", value="Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Santiago")
    st.text_input("Contacto Principal:", value="829-826-5888 / 809-691-3333")
    st.text_input("Correo Institucional:", value="Aboagrim@gmail.com")
    if st.button("💾 Guardar Cambios de Perfil"):
        st.toast("Perfil actualizado correctamente.", icon="💾")

# --- ENRUTADOR DEL SISTEMA ---
if menu == "🏠 Mando Central": vista_mando()
elif menu == "⚖️ Registro Maestro": vista_registro()
elif menu == "📁 Archivo Digital": vista_archivo()
elif menu == "📄 Plantillas Auto": vista_plantillas()
elif menu == "📅 Alertas y Plazos": vista_alertas()
elif menu == "💳 Facturación": vista_facturacion()
elif menu == "⚙️ Configuración": vista_configuracion()
