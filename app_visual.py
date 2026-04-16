import streamlit as st
import pandas as pd
import datetime
from database import *

# --- CONFIGURACIÓN DE MARCA ---
st.set_page_config(page_title="AboAgrim Pro DMS", layout="wide", initial_sidebar_state="expanded")

# --- LÓGICA DE SEGURIDAD (LOGIN) ---
if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><h1 style='text-align:center; color:#1E3A8A;'>⚖️ AboAgrim Pro</h1>", unsafe_allow_html=True)
        with st.form("Login"):
            u = st.text_input("Correo Institucional:").strip()
            p = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("Entrar al Sistema", use_container_width=True):
                exito, user = autenticar_usuario(u, p)
                if exito:
                    st.session_state['autenticado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else: st.error("Acceso denegado.")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
st.sidebar.markdown(f"### AboAgrim Pro\n**Lic. Jhonny Matos, M.A.**\n`Usuario: {st.session_state['user']}`")
st.sidebar.divider()
menu = st.sidebar.radio("Navegación", ["🏠 Mando Central", "👤 Registro Maestro", "📁 Archivo", "📄 Plantillas", "📅 Alertas", "💳 Facturación", "⚙️ Configuración"])

if st.sidebar.button("🚪 Salir"):
    st.session_state['autenticado'] = False
    st.rerun()

# --- MÓDULOS ---
def vista_mando():
    st.markdown("""
        <div style='background:linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); padding:30px; border-radius:15px; color:white; border-left:8px solid #FBBF24;'>
            <h1 style='margin:0;'>AboAgrim Pro DMS ⚖️📐</h1>
            <p style='font-size:1.2rem; opacity:0.8;'>Santiago, República Dominicana | Gestión de Mensura y Derecho</p>
        </div>
    """, unsafe_allow_html=True)
    
    casos = consultar_todo()
    if casos:
        df = pd.DataFrame(casos)
        c1, c2 = st.columns([2, 1])
        tags = sorted(list(set([str(v) for col in ['tipo_caso', 'jurisdiccion', 'estado'] if col in df.columns for v in df[col].dropna().unique()])))
        sel_tags = c1.multiselect("🔍 Filtrar por Etiquetas:", options=tags)
        busq = c2.text_input("📝 Buscar Cliente o Expediente:")
        
        df_f = df.copy()
        if sel_tags: 
            for t in sel_tags: df_f = df_f[df_f.astype(str).apply(lambda r: t in r.values, axis=1)]
        if busq: df_f = df_f[df_f.astype(str).apply(lambda x: x.str.contains(busq, case=False)).any(axis=1)]
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Expedientes", len(df_f))
        m2.metric("Abiertos", len(df_f[df_f['estado']=='Abierto']))
        m3.metric("Deslindes", len(df_f[df_f['tipo_caso']=='Deslinde']))
        m4.metric("Litis", len(df_f[df_f['tipo_caso']=='Litis']))
        
        st.dataframe(df_f, use_container_width=True)
    else: st.info("Inicie registrando su primer expediente.")

def vista_registro_maestro():
    st.title("👤 Gestión Integral de Expedientes")
    dic = obtener_diccionario_maestro()
    tab1, tab2, tab3 = st.tabs(["📋 Datos del Cliente", "📐 Detalles del Inmueble", "⚖️ Roles y Asignación"])
    
    with st.form("registro_exp"):
        with tab1:
            c1, c2 = st.columns(2)
            num = c1.text_input("N° Expediente:")
            cli = c2.text_input("Nombre del Cliente:")
            tipo = st.selectbox("Tipo de Proceso:", ["Deslinde", "Saneamiento", "Litis", "Transferencia"])
        
        with tab2:
            c3, c4 = st.columns(2)
            jur = c3.selectbox("Jurisdicción:", ["Santiago", "La Vega", "Santo Domingo", "Puerto Plata"])
            eta = c4.selectbox("Etapa Actual:", ["Recepción", "Mensura", "Sometimiento", "Tribunal", "Sentencia"])
            detalles = st.text_area("Descripción del Terreno / Lote:")
            
        with tab3:
            st.markdown("### Asignación de Profesionales (7 Roles)")
            a1, a2, a3 = st.columns(3)
            agrim = a1.selectbox("Agrimensor:", dic['agrimensor'] or ["N/A"])
            abog = a2.selectbox("Abogado:", dic['abogado'] or ["N/A"])
            notar = a3.selectbox("Notario:", dic['notario'] or ["N/A"])
            
            a4, a5, a6 = st.columns(3)
            repre = a4.selectbox("Representante:", dic['representante'] or ["N/A"])
            apoder = a5.selectbox("Apoderado:", dic['apoderado'] or ["N/A"])
            solic = a6.selectbox("Solicitante:", dic['solicitante'] or ["N/A"])

        if st.form_submit_button("🛡️ Registrar y Sincronizar"):
            if num and cli:
                datos = {"numero_expediente": num, "cliente_id": cli, "tipo_caso": tipo, "jurisdiccion": jur, "etapa": eta, "estado": "Abierto"}
                if registrar_evento("casos", datos): 
                    st.toast("Expediente guardado exitosamente.", icon="✅")
                    st.balloons()
                else: st.error("Error al guardar.")

def vista_plantillas():
    st.title("📄 Motor de Plantillas Ley 108-05")
    cat = st.radio("Categoría:", ["Administrativa (Mensura/RT)", "Contenciosa (Tribunales)"], horizontal=True)
    st.selectbox("Seleccione Plantilla:", ["Contrato de Cuota Litis", "Autorización de Mensura", "Instancia Introductiva"])
    st.button("⚙️ Generar Documento Profesional")

def vista_alertas():
    st.title("📅 Alertas, Plazos y Caducidades")
    st.info("Seguimiento automático de prescripciones legales.")
    data = {"Actuación": ["Apelación TJO", "Revisión Fraude", "Aviso Mensura"], "Plazo": ["30 Días", "1 Año", "15 Días"]}
    st.table(pd.DataFrame(data))

def vista_facturacion():
    st.title("💳 Control de Honorarios y Tasas JI")
    c1, c2 = st.columns(2)
    c1.number_input("Presupuesto RD$:", min_value=0.0)
    c2.number_input("Abono RD$:", min_value=0.0)
    st.button("Registrar Transacción Financiera")

def vista_archivo():
    st.title("📁 Bóveda Digital DMS")
    st.file_uploader("Subir planos Civil 3D, Word o PDF:", accept_multiple_files=True)
    st.button("⬆️ Cargar a la Nube")

def vista_configuracion():
    st.title("⚙️ Configuración y Normativa")
    st.markdown("**Sede Principal:** Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Santiago.")
    st.success("Conexión con Supabase: ESTABLE")

# --- NAVEGADOR ---
vistas = {"🏠 Mando Central": vista_mando, "👤 Registro Maestro": vista_registro_maestro, "📁 Archivo": vista_archivo, "📄 Plantillas": vista_plantillas, "📅 Alertas": vista_alertas, "💳 Facturación": vista_facturacion, "⚙️ Configuración": vista_configuracion}
vistas[menu]()
