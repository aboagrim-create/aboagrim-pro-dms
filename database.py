import streamlit as st
from supabase import create_client, Client
import io

# --- Conexión a la Nube (Supabase) ---
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

def obtener_diccionario_maestro():
    """Extrae profesionales directamente desde Supabase."""
    roles = ["agrimensor", "abogado", "notario", "representante", "apoderado", "reclamante", "solicitante"]
    diccionario = {rol: [] for rol in roles}
    try:
        respuesta = supabase.table("personas").select("id, nombre_completo, rol").execute()
        for persona in respuesta.data:
            rol = persona.get("rol")
            if rol in diccionario:
                diccionario[rol].append(persona)
    except Exception as e:
        print(f"Error conectando a Supabase: {e}")
    return diccionario

def consultar_todo():
    """Trae todos los expedientes desde la nube para las métricas."""
    try:
        respuesta = supabase.table("casos").select("*").order("fecha_apertura", desc=True).execute()
        return respuesta.data
    except Exception as e:
        print(f"Error consultando casos en Supabase: {e}")
        return []

def procesar_plantilla_maestra(contexto, archivo_plantilla_bytes):
    """
    Procesa plantillas en memoria sin depender del disco duro local,
    preparado para funcionar en Streamlit Cloud.
    """
    try:
        from docxtpl import DocxTemplate
        doc = DocxTemplate(io.BytesIO(archivo_plantilla_bytes))
        doc.render(contexto)
        
        salida_bytes = io.BytesIO()
        doc.save(salida_bytes)
        salida_bytes.seek(0)
        return salida_bytes
    except Exception as e:
        print(f"Error en plantilla: {e}")
        return None
