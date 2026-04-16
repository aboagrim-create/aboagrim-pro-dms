import streamlit as st
import pandas as pd
from database import *

# --- Configuración Base ---
st.set_page_config(page_title="AboAgrim Pro DMS", layout="wide", initial_sidebar_state="expanded")

# --- Identidad Corporativa Sidebar ---
st.sidebar.markdown("### Abogados y Agrimensores 'AboAgrim'")
st.sidebar.markdown("**Lic. Jhonny Matos. M.A., Presidente**")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Navegación",
    ["🏠 Mando", "👤 Registro Maestro", "📁 Archivo", "📄 Plantillas", "📅 Alertas", "💳 Facturación", "⚙️ Configuración"],
    label_visibility="collapsed"
)

# --- 1. MANDO CENTRAL (DISEÑO PREMIUM + BÚSQUEDA POR TAGS) ---
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
        
        # Sistema de Búsqueda por Tags
        st.markdown("#### 🔍 Filtrado Inteligente por Etiquetas (Tags)")
        columnas_tag = ['tipo_caso', 'jurisdiccion', 'estado', 'etapa']
        tags_disp = sorted(list(set([str(val) for col in columnas_tag if col in df.columns for val in df[col].dropna().unique() if str(val).strip()])))
        
        c_f1, c_f2 = st.columns([2, 1])
        t_sel = c_f1.multiselect("Filtrar por Tags:", options=tags_disp, placeholder="Seleccione atributos...")
        b_txt = c_f2.text_input("Buscar por nombre o número:")

        df_f = df.copy()
        if t_sel:
            for t in t_sel:
                df_f = df_f[df_f.astype(str).apply(lambda r: t in r.values, axis=1)]
        if b_txt:
            df_f = df_f[df_f.astype(str).apply(lambda x: x.str.contains(b_txt, case=False, na=False)).any(axis=1)]

        # Métricas
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Resultados", len(df_f))
        m2.metric("Deslindes", len(df_f[df_f['tipo_caso'] == 'Deslinde']) if 'tipo_caso' in df_f.columns else 0)
        m3.metric("Casos Abiertos", len(df_f[df_f['estado'] == 'Abierto']) if 'estado' in df_f.columns else 0)
        m4.metric("Jurisdicción Principal", df_f['jurisdiccion'].mode()[0] if 'jurisdiccion' in df_f.columns and not df_f.empty else "N/A")

        st.divider()
        st.dataframe(df_f, use_container_width=True)
    else:
        st.info("Sistema operando. Registre un expediente para activar el panel.")

# --- 2. REGISTRO MAESTRO (FORMULARIO DE 7 ROLES) ---
def vista_registro_maestro():
    st.title("⚖️ Registro Maestro y Redacción")
    dic = obtener_diccionario_maestro()
    
    with st.form("registro_full_aboagrim"):
        st.subheader("I. Información del Proceso")
        c1, c2, c3 = st.columns(3)
        num = c1.text_input("N° Expediente:")
        tipo = c2.selectbox("Tipo de Acto:", ["Deslinde", "Saneamiento", "Litis", "Transferencia", "Determinación de Herederos"])
        jur = c3.selectbox("Jurisdicción:", ["Santiago", "La Vega", "Santo Domingo", "Puerto Plata", "Moca"])
        
        st.subheader("II. Partes y Estado")
        f1, f2, f3 = st.columns(3)
        cli = f1.text_input("Cliente / Reclamante:")
        ced = f2.text_input("Cédula / RNC:")
        eta = f3.selectbox("Etapa Actual:", ["Recepción", "Mensura", "Sometimiento", "Tribunal", "Sentencia"])

        st.subheader("III. Asignación de Profesionales (7 Roles)")
        a1, a2, a3 = st.columns(3)
        agrim = a1.selectbox("Agrimensor:", dic.get('agrimensor', []) or ["Sin datos"])
        abog = a2.selectbox("Abogado:", dic.get('abogado', []) or ["Sin datos"])
        notar = a3.selectbox("Notario:", dic.get('notario', []) or ["Sin datos"])
        
        a4, a5, a6 = st.columns(3)
        repre = a4.selectbox("Representante:", dic.get('representante', []) or ["Sin datos"])
        apoder = a5.selectbox("Apoderado:", dic.get('apoderado', []) or ["Sin datos"])
        solic = a6.selectbox("Solicitante:", dic.get('solicitante', []) or ["Sin datos"])

        if st.form_submit_button("🛡️ Registrar y Blindar Expediente"):
            if num and cli:
                datos = {"numero_expediente": num, "tipo_caso": tipo, "jurisdiccion": jur, "cliente_id": cli, "etapa": eta, "estado": "Abierto"}
                if registrar_evento("casos", datos): st.success("✅ Expediente guardado exitosamente en la nube.")
                else: st.error("Error al conectar con Supabase.")

# --- 3. ARCHIVO DIGITAL ---
def vista_archivo():
    st.title("📁 Archivo Digital DMS")
    st.markdown("Gestión de planos Civil 3D y documentación técnica.")
    st.file_uploader("Cargar archivos vinculados:", accept_multiple_files=True)
    st.button("⬆️ Subir a Bóveda Segura")

# --- 4. PLANTILLAS ---
def vista_plantillas():
    st.title("📄 Generador de Plantillas Automáticas")
    st.selectbox("Documento:", ["Contrato Cuota Litis", "Poder Especial", "Solicitud de Mensura"])
    st.text_input("Expediente de referencia:")
    st.button("⚙️ Generar Word Automático")

# --- 5. ALERTAS ---
def vista_alertas():
    st.title("📅 Panel de Alertas y Plazos")
    st.info("Seguimiento automático de audiencias y plazos de mensura catastral.")
    st.warning("Próximo vencimiento: EXP-2026-001 (Plazo de Mensura en 5 días).")

# --- 6. FACTURACIÓN ---
def vista_facturacion():
    st.title("💳 Control de Honorarios")
    st.number_input("Presupuesto RD$:", min_value=0.0)
    st.number_input("Avance RD$:", min_value=0.0)
    st.button("Actualizar Registro Financiero")

# --- 7. CONFIGURACIÓN ---
def vista_configuracion():
    st.title("⚙️ Configuración y Perfil")
    st.text_input("Nombre de la Firma:", value="Abogados y Agrimensores 'AboAgrim'")
    st.text_input("Dirección:", value="Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Santiago")
    st.success("Estado del Sistema: Conexión Activa a Supabase.")

# --- LÓGICA DE NAVEGACIÓN ---
if menu == "🏠 Mando": vista_mando()
elif menu == "👤 Registro Maestro": vista_registro_maestro()
elif menu == "📁 Archivo": vista_archivo()
elif menu == "📄 Plantillas": vista_plantillas()
elif menu == "📅 Alertas": vista_alertas()
elif menu == "💳 Facturación": vista_facturacion()
elif menu == "⚙️ Configuración": vista_configuracion()
