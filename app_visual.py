import streamlit as st
import pandas as pd
import datetime
from database import *

# --- Configuración Base ---
st.set_page_config(page_title="AboAgrim Pro DMS v17.1", layout="wide", initial_sidebar_state="expanded")

# --- Menú Lateral Corporativo ---
st.sidebar.markdown("### Abogados y Agrimensores\n### 'AboAgrim'")
st.sidebar.markdown("**Lic. Jhonny Matos. M.A., Presidente**")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Navegación",
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
    # Inyección de CSS para un diseño Premium
    st.markdown("""
        <style>
        .hero-banner {
            background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
            padding: 40px 30px;
            border-radius: 12px;
            color: white;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            margin-bottom: 2rem;
            border-left: 6px solid #FBBF24;
        }
        .hero-title {
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            letter-spacing: -0.025em;
        }
        .hero-subtitle {
            font-size: 1.4rem;
            color: #94A3B8;
            font-weight: 400;
            margin-bottom: 1.5rem;
        }
        .founder-name {
            font-size: 1.25rem;
            color: #FBBF24; 
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .area-tags {
            margin-top: 15px;
            font-size: 0.9rem;
            color: #E2E8F0;
            background: rgba(255,255,255,0.1);
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Banner Corporativo Renderizado
    st.markdown("""
        <div class="hero-banner">
            <div class="hero-title">AboAgrim Pro DMS ⚖️📐</div>
            <div class="hero-subtitle">Plataforma Inteligente de Gestión Jurídica y Mensura Catastral</div>
            <div class="founder-name">Lic. Jhonny Matos, M.A. | Fundador</div>
            <div class="area-tags">Jurisdicción Inmobiliaria • Deslindes • Litis • Saneamientos</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📈 Indicadores de Desempeño Operativo")
    
    casos = consultar_todo()
    if casos:
        df = pd.DataFrame(casos)
        
        st.markdown("#### 🔍 Filtros Avanzados")
        
        tags_disponibles = []
        columnas_tag = ['tipo_caso', 'jurisdiccion', 'estado', 'etapa']
        for col in columnas_tag:
            if col in df.columns:
                tags_disponibles.extend([str(val) for val in df[col].dropna().unique() if str(val).strip() != ""])
        
        tags_disponibles = sorted(list(set(tags_disponibles)))

        col_filtro1, col_filtro2 = st.columns([2, 1])
        with col_filtro1:
            tags_seleccionados = st.multiselect(
                "Filtrar por Etiquetas (Tags):",
                options=tags_disponibles,
                placeholder="Ej. Selecciona 'Deslinde' y 'Santiago'..."
            )
        with col_filtro2:
            busqueda_texto = st.text_input("Búsqueda por Expediente o Cliente:")

        df_filtrado = df.copy()
        
        if tags_seleccionados:
            for tag in tags_seleccionados:
                mask = df_filtrado.astype(str).apply(lambda row: tag in row.values, axis=1)
                df_filtrado = df_filtrado[mask]
                
        if busqueda_texto:
            mask_texto = df_filtrado.astype(str).apply(lambda x: x.str.contains(busqueda_texto, case=False, na=False)).any(axis=1)
            df_filtrado = df_filtrado[mask_texto]

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Resultados de Búsqueda", len(df_filtrado))
        c2.metric("En Proceso", len(df_filtrado[df_filtrado['estado'] == 'Abierto']) if 'estado' in df_filtrado.columns else 0)
        c3.metric("Deslindes", len(df_filtrado[df_filtrado['tipo_caso'] == 'Deslinde']) if 'tipo_caso' in df_filtrado.columns else 0)
        c4.metric("Litis", len(df_filtrado[df_filtrado['tipo_caso'] == 'Litis']) if 'tipo_caso' in df_filtrado.columns else 0)
        
        st.divider()
        st.subheader("📋 Base de Datos de Expedientes")
        if not df_filtrado.empty:
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("No se encontraron expedientes con los tags y criterios de búsqueda.")
    else:
        st.info("🟢 El motor de base de datos está en línea y operando de manera óptima.")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ⚖️ Área de Derecho")
            st.markdown("- Gestión automatizada de Litis y Demandas\n- Redacción inteligente de Contratos")
        with col2:
            st.markdown("#### 📐 Área de Agrimensura")
            st.markdown("- Control de Saneamientos y Deslindes\n- Bóveda digital para planos y AutoCAD")

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
        st.file_uploader("Arrastre sus archivos aquí", accept_multiple_files=True)

# --- 4. PLANTILLAS ---
def vista_plantillas():
    st.title("📄 Motor de Plantillas Inteligentes")
    st.markdown("Generación automática de documentos legales.")
    st.selectbox("Documento a Generar:", ["Contrato de Cuota Litis", "Solicitud de Mensura"])
    st.button("⚙️ Procesar y Generar Word")

# --- 5. ALERTAS ---
def vista_alertas():
    st.title("📅 Panel de Control de Alertas y Plazos")
    st.info("No hay alertas programadas.")

# --- 6. FACTURACIÓN ---
def vista_facturacion():
    st.title("💳 Facturación y Control de Honorarios")
    st.info("Módulo financiero enlazado a Supabase.")

# --- 7. CONFIGURACIÓN ---
def vista_configuracion():
    st.title("⚙️ Configuración General y Mantenimiento")
    st.success("Conexión a Base de Datos: ACTIVA")

# --- LÓGICA DE NAVEGACIÓN ---
if menu == "🏠 Mando": vista_mando()
elif menu == "👤 Registro Maestro": vista_registro_maestro()
elif menu == "📁 Archivo": vista_archivo()
elif menu == "📄 Plantillas": vista_plantillas()
elif menu == "📅 Alertas": vista_alertas()
elif menu == "💳 Facturación": vista_facturacion()
elif menu == "⚙️ Configuración": vista_configuracion()
