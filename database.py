import streamlit as st
from supabase import create_client, Client
import io
import datetime

# --- Conexión Blindada a Supabase ---
@st.cache_resource
def get_supabase() -> Client:
    """Inicializa el cliente de Supabase usando secretos de Streamlit."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

db = get_supabase()

# --- Funciones de Consulta (SELECT) ---
def obtener_diccionario_maestro():
    """Recupera la lista completa de profesionales categorizados por rol."""
    roles = ["agrimensor", "abogado", "notario", "representante", "apoderado", "reclamante", "solicitante"]
    dic = {rol: [] for rol in roles}
    try:
        res = db.table("personas").select("id, nombre_completo, rol").execute()
        for p in res.data:
            rol_actual = p.get('rol')
            if rol_actual in dic:
                dic[rol_actual].append(p['nombre_completo'])
    except Exception as e:
        st.error(f"Error de conexión: {e}")
    return dic

def consultar_todo():
    """Trae la base de datos completa de expedientes ordenados por fecha."""
    try:
        res = db.table("casos").select("*").order("fecha_apertura", desc=True).execute()
        return res.data
    except:
        return []

def consultar_honorarios_completos():
    """Consulta detallada de estados financieros de los casos."""
    try:
        res = db.table("honorarios").select("*, casos(numero_expediente, cliente)").execute()
        return res.data
    except:
        return []

# --- Funciones de Acción (INSERT / UPDATE) ---
def registrar_evento(tabla, datos):
    """Inserta registros en cualquier tabla de la base de datos."""
    try:
        db.table(tabla).insert(datos).execute()
        return True
    except Exception as e:
        st.error(f"Error al insertar en {tabla}: {e}")
        return False

def actualizar_etapa_caso(id_caso, nueva_etapa):
    """Actualiza la etapa procesal de un expediente."""
    try:
        db.table("casos").update({"etapa": nueva_etapa}).eq("id", id_caso).execute()
        return True
    except:
        return False

# --- Motor de Documentos (DOCXTPL) ---
def generar_documento_legal(contexto, plantilla_bytes):
    """Genera un archivo Word a partir de una plantilla cargada."""
    try:
        from docxtpl import DocxTemplate
        doc = DocxTemplate(io.BytesIO(plantilla_bytes))
        doc.render(contexto)
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        return output
    except Exception as e:
        st.error(f"Error en generación de Word: {e}")
        return None
