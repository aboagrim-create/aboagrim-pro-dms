import streamlit as st
from supabase import create_client, Client
import io

# --- Conexión Blindada a Supabase ---
@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

db = get_supabase()

def obtener_diccionario_maestro():
    """Recupera todos los perfiles profesionales y técnicos."""
    roles = ["agrimensor", "abogado", "notario", "representante", "apoderado", "reclamante", "solicitante"]
    dic = {rol: [] for rol in roles}
    try:
        res = db.table("personas").select("id, nombre_completo, rol").execute()
        for p in res.data:
            if p['rol'] in dic: dic[p['rol']].append(p['nombre_completo'])
    except: pass
    return dic

def consultar_expedientes():
    """Trae la data completa para el Mando Central."""
    try:
        res = db.table("casos").select("*").order("created_at", desc=True).execute()
        return res.data
    except: return []

def consultar_honorarios():
    """Trae los estados de cuenta y cobros."""
    try:
        res = db.table("honorarios").select("*, casos(numero_expediente)").execute()
        return res.data
    except: return []

def registrar_evento(tabla, datos):
    """Función universal de inserción (Upsert)."""
    try:
        db.table(tabla).insert(datos).execute()
        return True
    except Exception as e:
        st.error(f"Error en registro: {e}")
        return False

def generar_word_pro(contexto, plantilla_bytes):
    """Motor de redacción automatizada."""
    try:
        from docxtpl import DocxTemplate
        doc = DocxTemplate(io.BytesIO(plantilla_bytes))
        doc.render(contexto)
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        return output
    except: return None
