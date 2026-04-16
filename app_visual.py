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

# --- 1. MANDO CENTRAL (DISEÑO MODERNO + BÚSQUEDA POR TAGS) ---
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
    
    # Extraer datos reales
    casos = consultar_todo()
    if casos:
        df = pd.DataFrame(casos)
        
        # --- NUEVO: MOTOR DE BÚSQUEDA POR TAGS ---
        st.markdown("#### 🔍 Filtros Avanzados")
        
        # 1. Recolectar dinámicamente los tags de la base de datos
        tags_disponibles = []
        columnas_tag = ['tipo_caso', 'jurisdiccion', 'estado', 'etapa']
        for col in columnas_tag:
            if col in df.columns:
                # Añade los valores únicos que no estén vacíos
                tags_disponibles.extend([str(val) for val in df[col].dropna().unique() if str(val).strip() != ""])
        
        tags_disponibles = sorted(list(set(tags_disponibles))) # Elimina duplicados y ordena alfabéticamente

        # 2. Interfaz de búsqueda
        col_filtro1, col_filtro2 = st.columns([2, 1])
        with col_filtro1:
            tags_seleccionados = st.multiselect(
                "Filtrar por Etiquetas (Tags):",
                options=tags_disponibles,
                placeholder="Ej. Selecciona 'Deslinde' y 'Santiago'..."
            )
        with col_filtro2:
            busqueda_texto = st.text_input("Búsqueda por Expediente o Cliente:")

        # 3. Lógica de filtrado
        df_filtrado = df.copy()
        
        # Filtrar por Tags (Condición AND: debe cumplir con todos los tags seleccionados)
        if tags_seleccionados:
            for tag in tags_seleccionados:
                # Aplica el filtro fila por fila buscando coincidencias exactas
                mask = df_filtrado.astype(str).apply(lambda row: tag in row.values, axis=1)
                df_filtrado = df_filtrado[mask]
                
        # Filtrar por texto libre
        if busqueda_texto:
            # Busca en todas las columnas si alguna contiene el texto escrito
            mask_texto = df_filtrado.astype(str).apply(lambda x: x.str.contains(busqueda_texto, case=False, na=False)).any(axis=1)
            df_filtrado = df_filtrado[mask_texto]
        
        # --- FIN DEL MOTOR DE BÚSQUEDA ---

        # Actualizar las métricas para que reflejen los datos filtrados, no el total
        st.markdown("<br>", unsafe_allow_html=True) # Espacio visual
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Resultados de Búsqueda", len(df_filtrado))
        c2.metric("En Proceso (Filtrados)", len(df_filtrado[df_filtrado['estado'] == 'Abierto']) if 'estado' in df_filtrado.columns else 0)
        c3.metric("Deslindes (Filtrados)", len(df_filtrado[df_filtrado['tipo_caso'] == 'Deslinde']) if 'tipo_caso' in df_filtrado.columns else 0)
        c4.metric("Litis (Filtradas)", len(df_filtrado[df_filtrado['tipo_caso'] == 'Litis']) if 'tipo_caso' in df_filtrado.columns else 0)
        
        st.divider()
        st.subheader("📋 Base de Datos de Expedientes")
        if not df_filtrado.empty:
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("No se encontraron expedientes con los tags y criterios de búsqueda especificados.")
    else:
        st.info("🟢 El motor de base de datos está en línea y operando de manera óptima. Inicie registrando su primer expediente.")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ⚖️ Área de Derecho")
            st.markdown("- Gestión automatizada de Litis y Demandas\n- Redacción inteligente de Contratos\n- Seguimiento de Audiencias y Plazos")
        with col2:
            st.markdown("#### 📐 Área de Agrimensura")
            st.markdown("- Control de Saneamientos y Deslindes\n- Bóveda digital para planos y AutoCAD\n- Control de etapas de Mensura")l para planos y AutoCAD\n- Control de etapas de Mensura")

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
