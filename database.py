import streamlit as st
from supabase import create_client, Client
import io

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

db = get_supabase()

def obtener_diccionario_maestro():
    """Recupera abogados, agrimensores y técnicos para los menús."""
    roles = ["agrimensor", "abogado", "notario", "representante", "apoderado", "reclamante", "solicitante"]
    dic = {rol: [] for rol in roles}
    try:
        res = db.table("personas").select("id, nombre_completo, rol").execute()
        for p in res.data:
            rol_actual = p.get('rol')
            if rol_actual in dic:
                dic[rol_actual].append(p['nombre_completo'])
    except Exception:
        pass
    return dic

def consultar_todo():
    """Trae todos los expedientes desde la nube."""
    try:
        res = db.table("casos").select("*").order("created_at", desc=True).execute()
        return res.data
    except Exception:
        return []

def registrar_evento(tabla, datos):
    """Inserta registros (casos, personas o pagos) en Supabase."""
    try:
        db.table(tabla).insert(datos).execute()
        return True
    except Exception:
        return False

def procesar_plantilla_maestra(contexto, plantilla_bytes):
    """Motor de redacción automática en memoria."""
    try:
        from docxtpl import DocxTemplate
        doc = DocxTemplate(io.BytesIO(plantilla_bytes))
        doc.render(contexto)
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        return output
    except Exception:
        return None
