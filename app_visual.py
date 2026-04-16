import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AboAgrim Pro DMS", layout="wide")

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.markdown(f"## AboAgrim Pro")
st.sidebar.markdown(f"Lic. Jhonny Matos. M.A., Presidente")
st.sidebar.divider()

# Menú de navegación
menu = st.sidebar.radio(
    "Módulos del Sistema",
    ["Mando Central", "Registro Catastral & Legal", "Archivo Digital DMS", "Configuración de Firma"]
)

# --- IMPORTACIÓN DE DATOS SIMULADOS (PARA EL EJEMPLO) ---
def get_casos_ejemplo():
    data = {
        'Número': ['2023-01', '2023-02', '2023-03'],
        'Cliente': ['Cliente A', 'Cliente B', 'Cliente C'],
        'Tipo': ['Deslinde', 'Saneamiento', 'Litis'],
        'Jurisdicción': ['Distrito Nacional', 'Santiago', 'Santo Domingo'],
        'Estado': ['Abierto', 'Cerrado', 'Abierto']
    }
    return pd.DataFrame(data)

def get_litigios_ejemplo():
    data = {
        'Número': ['2023-L01', '2023-L02'],
        'Cliente': ['Cliente D', 'Cliente E'],
        'Tipo': ['Reclamación de Linderos', 'Servidumbre'],
        'Jurisdicción': ['La Vega', 'San Cristóbal'],
        'Estado': ['Abierto', 'Abierto']
    }
    return pd.DataFrame(data)

# --- FUNCIONES DE VISTA (LAS VISTAS DESEADAS) ---
def vista_mando_central():
    st.title("Mando Central: Resumen Operativo")
    
    st.subheader("Expedientes Catastrales (Deslindes, etc.)")
    df_casos = get_casos_ejemplo()
    st.dataframe(df_casos, use_container_width=True)

    st.divider()
    
    st.subheader("Litigios y Litis")
    df_litigios = get_litigios_ejemplo()
    st.dataframe(df_litigios, use_container_width=True)

def vista_registro_catastral_legal():
    st.title("Módulo de Registro Catastral y Legal")
    st.info("Formulario para registro de nuevos expedientes.")
    # Implementación del formulario aquí...

def vista_archivo_digital_dms():
    st.title("Módulo de Archivo Digital DMS")
    st.info("Búsqueda y gestión de documentos digitales.")
    # Implementación del archivo aquí...

def vista_configuracion_firma():
    st.title("Módulo de Configuración de Firma")
    st.info("Ajustes generales y perfiles de firma.")
    # Implementación de configuración aquí...

# --- LÓGICA DE NAVEGACIÓN (CONECTANDO EL MENÚ A LAS VISTAS) ---
if menu == "Mando Central":
    vista_mando_central()
elif menu == "Registro Catastral & Legal":
    vista_registro_catastral_legal()
elif menu == "Archivo Digital DMS":
    vista_archivo_digital_dms()
elif menu == "Configuración de Firma":
    vista_configuracion_firma()
