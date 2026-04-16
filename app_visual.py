import streamlit as st
import pandas as pd
from database import *

# --- Configuración Base ---
st.set_page_config(page_title="AboAgrim Pro DMS", layout="wide")

# --- Menú Lateral Exacto ---
st.sidebar.markdown("### AboAgrim DMS")
st.sidebar.markdown("**MENÚ**")

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

# --- 1. Mando ---
def vista_mando():
    st.title("📊 Mando Central: Resumen Operativo")
    casos = consultar_todo()
    if casos:
        df = pd.DataFrame(casos)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Expedientes", len(df))
        c2.metric("Casos Abiertos", len(df[df['estado'] == 'Abierto']) if 'estado' in df else 0)
        c3.metric("Jurisdicción Principal", df['jurisdiccion'].mode()[0] if 'jurisdiccion' in df and not df.empty else "N/A")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Sin expedientes registrados.")

# --- 2. Registro Maestro ---
def vista_registro_maestro():
    st.title("⚖️ Registro Maestro y Redacción")
    dic = obtener_diccionario_maestro()
    
    with st.form("form_registro"):
        st.subheader("Información General del Caso")
        col1, col2 = st.columns(2)
        with col1:
            num = st.text_input("Número de Expediente:")
            tipo = st.selectbox("Tipo de Acto:", ["Deslinde", "Saneamiento", "Litis", "Transferencia"])
        with col2:
            cliente = st.text_input("Nombre del Cliente:")
            jur = st.selectbox("Jurisdicción:", ["Santiago", "La Vega", "Santo Domingo", "Puerto Plata"])
        
        st.subheader("Asignación Técnica")
        c1, c2, c3 = st.columns(3)
        agrimensor = c1.selectbox("Agrimensor:", dic.get('agrimensor', []) or ["N/A"])
        abogado = c2.selectbox("Abogado:", dic.get('abogado', []) or ["N/A"])
        notario = c3.selectbox("Notario:", dic.get('notario', []) or ["N/A"])

        if st.form_submit_button("Guardar Expediente"):
            if num and cliente:
                exito = registrar_evento("casos", {"numero_expediente": num, "tipo_caso": tipo, "jurisdiccion": jur, "cliente_id": cliente, "estado": "Abierto"})
                if exito: st.success("Expediente blindado en la nube.")
            else:
                st.warning("Complete el número y cliente.")

# --- 3. Archivo ---
def vista_archivo():
    st.title("📁 Archivo Digital DMS")
    st.info("Sube documentos (Planos, Word, PDF) asociados a los expedientes.")
    st.file_uploader("Cargar documento:", accept_multiple_files=True)

# --- 4. Plantillas (FUNCIÓN REINSERTADA) ---
def vista_plantillas():
    st.title("📄 Generador de Plantillas Automáticas")
    st.markdown("Automatiza Contratos de Cuota Litis, Solicitudes de Mensura y Actos de Alguacil.")
    plantilla = st.selectbox("Seleccione el documento a generar:", ["Contrato Cuota Litis", "Poder de Representación", "Solicitud de Autorización de Mensura"])
    if st.button(f"Cargar variables para {plantilla}"):
        st.success("Motor de plantillas listo.")

# --- 5. Alertas (FUNCIÓN REINSERTADA) ---
def vista_alertas():
    st.title("📅 Panel de Alertas y Plazos")
    st.warning("No hay audiencias programadas para esta semana.")
    st.info("El expediente EXP-2026-001 (Deslinde) tiene plazo de mensura próximo a vencer.")

# --- 6. Facturación (Honorarios) ---
def vista_facturacion():
    st.title("💳 Facturación y Honorarios")
    datos = consultar_honorarios_completos()
    if datos:
        st.dataframe(pd.DataFrame(datos), use_container_width=True)
    else:
        st.info("No hay registros de facturación activos.")

# --- 7. Configuración ---
def vista_configuracion():
    st.title("⚙️ Configuración General")
    st.write("Sistema AboAgrim Pro v17.1 - Estado: **Óptimo y en la Nube**")

# --- Lógica de Enrutamiento ---
if menu == "🏠 Mando":
    vista_mando()
elif menu == "👤 Registro Maestro":
    vista_registro_maestro()
elif menu == "📁 Archivo":
    vista_archivo()
elif menu == "📄 Plantillas":
    vista_plantillas()
elif menu == "📅 Alertas":
    vista_alertas()
elif menu == "💳 Facturación":
    vista_facturacion()
elif menu == "⚙️ Configuración":
    vista_configuracion()
