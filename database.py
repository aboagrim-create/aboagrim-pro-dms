import os
import streamlit as st
from supabase import create_client, Client
from docxtpl import DocxTemplate

# Asegúrese de que estas variables estén en sus Secrets de Streamlit o cámbielas por el texto directamente
url: str = st.secrets.get("SUPABASE_URL", "SU_URL_AQUI")
key: str = st.secrets.get("SUPABASE_KEY", "SU_KEY_AQUI")
supabase: Client = create_client(url, key)

def obtener_diccionario_maestro():
    """Trae las etiquetas desde la tabla variables_sistema"""
    try:
        query = supabase.table("variables_sistema").select("*").execute()
        return query.data
    except Exception as e:
        st.error(f"Error al leer diccionario: {e}")
        return []

def procesar_plantilla_maestra(datos, nombre_plantilla):
    """Crea el Word y lo guarda en la carpeta Expedientes"""
    try:
        ruta_plantilla = os.path.join("plantillas_maestras", nombre_plantilla)
        nombre_cli = datos.get('cliente_nombre', 'Nuevo_Expediente').replace(" ", "_")
        ruta_salida = f"Expedientes/{nombre_cli}"
        
        if not os.path.exists(ruta_salida):
            os.makedirs(ruta_salida)
            
        doc = DocxTemplate(ruta_plantilla)
        doc.render(datos)
        
        archivo_final = f"{ruta_salida}/GENERADO_{nombre_plantilla}"
        doc.save(archivo_final)
        return archivo_final
    except Exception as e:
        return f"Error técnico: {str(e)}"
