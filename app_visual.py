import streamlit as st
import pandas as pd
from database import obtener_diccionario_maestro, consultar_todo

# --- Configuración Base ---
st.set_page_config(page_title="AboAgrim Pro DMS", layout="wide")

# --- Encabezado Corporativo Oficial ---
st.sidebar.markdown("### Abogados y Agrimensores 'AboAgrim'")
st.sidebar.markdown("**Lic. Jhonny Matos. M.A., Presidente**")
st.sidebar.divider()

# --- Menú Lateral ---
menu = st.sidebar.radio(
    "Navegación",
    ["🏠 Mando", "👤 Registro Maestro", "⚙️ Configuración"]
)

# --- Vistas del Sistema ---
def vista_mando():
    st.title("🏠 Mando Central de Operaciones ☁️")
    datos = consultar_todo()
    
    if datos:
        df = pd.DataFrame(datos)
        col1, col2, col3 = st.columns(3)
        col1.metric("Expedientes en la Nube", len(df))
        col2.metric("Casos Abiertos", len(df[df['estado'] == 'Abierto']) if 'estado' in df.columns else 0)
        col3.metric("Jurisdicción Frecuente", df['jurisdiccion'].mode()[0] if 'jurisdiccion' in df.columns and not df.empty else "N/A")
        
        st.subheader("Registro de Base de Datos")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No se encontraron expedientes en Supabase. Verifique la conexión o registre un nuevo caso.")

def vista_registro():
    st.title("👤 Registro Maestro y Redacción")
    st.markdown("Seleccione el personal técnico y legal:")
    
    diccionario = obtener_diccionario_maestro()
    
    with st.expander("Desplegar Formulario de Asignación", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Agrimensor:", [p['nombre_completo'] for p in diccionario.get('agrimensor', [])] or ["Sin registros en la nube"])
            st.selectbox("Abogado:", [p['nombre_completo'] for p in diccionario.get('abogado', [])] or ["Sin registros en la nube"])
            st.selectbox("Notario:", [p['nombre_completo'] for p in diccionario.get('notario', [])] or ["Sin registros en la nube"])
            st.selectbox("Representante:", [p['nombre_completo'] for p in diccionario.get('representante', [])] or ["Sin registros en la nube"])
            
        with col2:
            st.selectbox("Apoderado:", [p['nombre_completo'] for p in diccionario.get('apoderado', [])] or ["Sin registros en la nube"])
            st.selectbox("Reclamante:", [p['nombre_completo'] for p in diccionario.get('reclamante', [])] or ["Sin registros en la nube"])
            st.selectbox("Solicitante:", [p['nombre_completo'] for p in diccionario.get('solicitante', [])] or ["Sin registros en la nube"])

    st.markdown("---")
    st.subheader("Bóveda de Documentos")
    st.file_uploader("Subir plantilla o documento de prueba al sistema", type=["docx", "pdf"])

def vista_configuracion():
    st.title("⚙️ Configuración del Sistema")
    st.success("Conexión activa mediante Streamlit Secrets y Supabase.")

# --- Lógica de Enrutamiento ---
if menu == "🏠 Mando":
    vista_mando()
elif menu == "👤 Registro Maestro":
    vista_registro()
elif menu == "⚙️ Configuración":
    vista_configuracion()
