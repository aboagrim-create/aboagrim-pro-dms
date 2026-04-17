import streamlit as st
from supabase import create_client, Client

# --- ESCUDO PROTECTOR PARA EVITAR PANTALLAS ROJAS ---
class DiccionarioSeguro(dict):
    def __missing__(self, key):
        return "N/A"

# --- CONEXIÓN PRINCIPAL ---
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

db = get_supabase()

# --- FUNCIONES DE CONSULTA ---
def obtener_diccionario_maestro():
    roles = ["agrimensor", "abogado", "notario", "representante", "apoderado", "reclamante", "solicitante"]
    dic = {rol: [] for rol in roles}
    try:
        res = db.table("personas").select("nombre_completo, rol").execute()
        for p in res.data:
            r = p.get('rol')
            if r in dic: dic[r].append(p.get('nombre_completo'))
    except: pass
    return dic

def consultar_todo(busqueda=""):
    try:
        res = db.table("casos").select("*").order("created_at", desc=True).execute()
        datos = [DiccionarioSeguro(d) for d in res.data]
        if busqueda:
            datos = [d for d in datos if busqueda.lower() in str(d).lower()]
        return datos
    except: return []

def registrar_evento(tabla, datos):
    try:
        db.table(tabla).insert(datos).execute()
        return True
    except: return False

def autenticar_usuario(email, password):
    try:
        res = db.auth.sign_in_with_password({"email": email, "password": password})
        return (True, res.user) if res.session else (False, None)
    except: return (False, None)

# --- FUNCIONES DE APOYO PARA MÓDULOS ---
def consultar_plantillas():
    try: return [DiccionarioSeguro(d) for d in db.table("plantillas").select("*").execute().data]
    except: return []

def consultar_alertas(solo_pendientes=False):
    try:
        q = db.table("alertas").select("*")
        if solo_pendientes: q = q.eq("estado", "Pendiente")
        return [DiccionarioSeguro(d) for d in q.execute().data]
    except: return []

def consultar_facturas():
    try: return [DiccionarioSeguro(d) for d in db.table("pagos").select("*").execute().data]
    except: return []
# ---------------------------------------------------------------------
# 7. GESTIÓN DOCUMENTAL (STORAGE)
# ---------------------------------------------------------------------
def subir_documento(bucket, ruta_archivo, file_bytes):
    """
    Sube un archivo físico a la bóveda de Supabase Storage.
    """
    try:
        # El parámetro file_options define el tipo de contenido automáticamente
        db.storage.from_(bucket).upload(
            file=ruta_archivo, 
            data=file_bytes, 
            file_options={"upsert": "true"}
        )
        return True
    except Exception as e:
        st.error(f"Error de Storage: {str(e)}")
        return False
