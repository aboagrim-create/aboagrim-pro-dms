import streamlit as st
import pandas as pd
from database import *

# --- Configuración de Interfaz ---
st.set_page_config(page_title="AboAgrim Pro DMS", layout="wide", initial_sidebar_state="expanded")

# --- Menú Lateral Oficial ---
st.sidebar.markdown("### Abogados y Agrimensores 'AboAgrim'")
st.sidebar.markdown("**Lic. Jhonny Matos. M.A., Presidente**")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Navegación",
    ["🏠 Mando", "👤 Registro Maestro", "📁 Archivo", "📄 Plantillas", "📅 Alertas", "💳 Facturación", "⚙️ Configuración"],
    label_visibility="collapsed"
)

# --- 1. MANDO CENTRAL (DISEÑO PREMIUM + TAGS) ---
def vista_mando():
    st.markdown("""
        <style>
        .hero-banner {
            background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
            padding: 40px; border-radius: 15px; color: white;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2); margin-bottom: 25px;
            border-left: 8px solid #FBBF24;
        }
        .founder { color: #FBBF24; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
        </style>
        <div class="hero-banner">
            <h1 style='color: white; margin:0;'>AboAgrim Pro DMS ⚖️📐</h1>
            <p style='font-size: 1.2rem; opacity: 0.8;'>Gestión Integral de Jurisdicción Inmobiliaria y Mensura</p>
            <div class="founder">Lic. Jhonny Matos, M.A. | Fundador</div>
        </div>
    """, unsafe_allow_html=True)

    casos = consultar_todo()
    if casos:
        df = pd.DataFrame(casos)
        
        # Sistema de Tags
        st.markdown("#### 🔍 Filtrado por Etiquetas (Tags)")
        cols_tag = ['tipo_caso', 'jurisdiccion', 'estado', 'etapa']
        tags_disp = sorted(list(set([str(val) for col in cols_tag if col in df.columns for val in df[col].dropna().unique() if str(val).strip()])))
        
        c_f1, c_f2 = st.columns([2, 1])
        t_sel = c_f1.multiselect("Tags:", options=tags_disp, placeholder="Filtre por cualquier atributo...")
        b_txt = c_f2.text_input("Buscar Cliente o Expediente:")

        df_f = df.copy()
        if t_sel:
            for t in t_sel:
                df_f = df_f[df_f.astype(str).apply(lambda r: t in r.values, axis=1)]
        if b_txt:
            df_f = df_f[df_f.astype(str).apply(lambda x: x.str.contains(b_txt, case=False, na=False)).any(axis=1)]

        # Métricas Dinámicas
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Resultados", len(df_f))
        m2.metric("Deslindes", len(df_f[df_f['tipo_caso'] == 'Deslinde']) if 'tipo_caso' in df_f.columns else 0)
        m3.metric("Abiertos", len(df_f[df_f['estado'] == 'Abierto']) if 'estado' in df_f.columns else 0)
        m4.metric("Jurisdicción", df_f['jurisdiccion'].mode()[0] if 'jurisdiccion' in df_f.columns and not df_f.empty else "N/A")

        st.divider()
        st.dataframe(df_f, use_container_width=True)
    else:
        st.info("Sistema en línea. Registre su primer expediente para activar el panel.")

# --- 2. REGISTRO MAESTRO (FORMULARIO EXTENDIDO) ---
def vista_registro_maestro():
    st.title("⚖️ Registro Maestro y Redacción")
    dic = obtener_diccionario_maestro()
    
    with st.form("registro_full"):
        st.subheader("I. Datos del Expediente")
        c1, c2, c3 = st.columns(3)
        num = c1.text_input("N° de Expediente:")
        tipo = c2.selectbox("Tipo de Acto:", ["Deslinde", "Saneamiento", "Litis", "Transferencia", "Determinación de Herederos"])
        jur = c3.selectbox("Jurisdicción:", ["Santiago", "La Vega", "Santo Domingo", "Puerto Plata", "Moca"])
        
        st.subheader("II. Partes Interesadas")
        f1, f2, f3 = st.columns(3)
        cli = f1.text_input("Cliente / Reclamante:")
        ced = f2.text_input("Cédula / RNC:")
        eta = f3.selectbox("Etapa Actual:", ["Recepción", "Mensura", "Sometimiento", "Tribunal", "Sentencia"])

        st.subheader("III. Asignación de Profesionales")
        a1, a2, a3 = st.columns(3)
        agrim = a1.selectbox("Agrimensor:", dic.get('agrimensor', []) or ["Sin datos"])
        abog = a2.selectbox("Abogado:", dic.get('abogado', []) or ["Sin datos"])
        notar = a3.selectbox("Notario:", dic.get('notario', []) or ["Sin datos"])
        
        a4, a5, a6 = st.columns(3)
        repre = a4.selectbox("Representante:", dic.get('representante', []) or ["Sin datos"])
        apoder = a5.selectbox("Apoderado:", dic.get('apoderado', []) or ["Sin datos"])
        solic = a6.selectbox("Solicitante:", dic.get('solicitante', []) or ["Sin datos"])

        if st.form_submit_button("🛡️ Registrar Expediente Oficialmente"):
            if num and cli:
                datos = {"numero_expediente": num, "tipo_caso": tipo, "jurisdiccion": jur, "cliente_id": cli, "etapa": eta, "estado": "Abierto"}
                if registrar_evento("casos", datos): st.success("✅ Expediente guardado en la nube.")
                else: st.error("Error al conectar con la base de datos.")

# --- 3. ARCHIVO DIGITAL ---
def vista_archivo():
    st.title("📁 Archivo Digital DMS")
    st.markdown("Gestión de planos Civil 3D, Word y PDF.")
    exp = st.text_input("Vincular al Expediente N°:")
    st.file_uploader("Subir archivos técnicos:", accept_multiple_files=True)
    st.button("⬆️ Cargar a Bóveda")

# --- 4. PLANTILLAS ---
def vista_plantillas():
    st.title("📄 Motor de Plantillas Automáticas")
    st.selectbox("Seleccione Documento:", ["Contrato Cuota Litis", "Poder Especial", "Solicitud Mensura"])
    st.text_input("Número de Expediente para fusión:")
    st.button("⚙️ Generar Word")

# --- 5. ALERTAS ---
def vista_alertas():
    st.title("📅 Panel de Alertas y Plazos")
    st.info("Seguimiento de plazos de Mensura y Fechas de Audiencia.")
    st.dataframe(pd.DataFrame({"Fecha": ["2026-04-20"], "Caso": ["EXP-001"], "Evento": ["Audiencia Santiago"], "Prioridad": ["Alta"]}))

# --- 6. FACTURACIÓN ---
def vista_facturacion():
    st.title("💳 Control de Honorarios")
    st.number_input("Monto Contrato RD$:", min_value=0.0)
    st.number_input("Abonos Recibidos RD$:", min_value=0.0)
    st.button("Actualizar Balance Financiero")

# --- 7. CONFIGURACIÓN ---
def vista_configuracion():
    st.title("⚙️ Configuración")
    st.text_input("Oficina:", value="AboAgrim")
    st.text_input("Dirección:", value="Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Santiago")
    st.success("Sistema conectado a Supabase - Versión 17.1")

# --- NAVEGACIÓN ---
vistas = {"🏠 Mando": vista_mando, "👤 Registro Maestro": vista_registro_maestro, "📁 Archivo": vista_archivo, 
          "📄 Plantillas": vista_plantillas, "📅 Alertas": vista_alertas, "💳 Facturación": vista_facturacion, "⚙️ Configuración": vista_configuracion}
vistas[menu]()
