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
    except Exception as e:
        st.error(f"Error técnico devuelto por la Base de Datos: {str(e)}")
        return False

def autenticar_usuario(email, password):
    try:
        res = db.auth.sign_in_with_password({"email": email, "password": password})
        return (True, res.user) if res.session else (False, None)
    except: return (False, None)
def registrar_nuevo_usuario(email, password):
    """Permite al administrador crear cuentas para el equipo."""
    try:
        res = db.auth.sign_up({"email": email, "password": password})
        return True if res.user else False
    except Exception as e:
        st.error(f"Error al crear usuario: {str(e)}")
        return False        

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
# 7. GESTIÓN DOCUMENTAL (STORAGE PARA LA BÓVEDA DIGITAL)
# ---------------------------------------------------------------------
def subir_documento(bucket, ruta_archivo, file_bytes):
    """
    Sube un archivo físico a la bóveda de Supabase Storage.
    """
    try:
        # CORRECCIÓN: Usamos 'path' para el nombre y 'file' para los datos
        db.storage.from_(bucket).upload(
            path=ruta_archivo, 
            file=file_bytes, 
            file_options={"upsert": "true"}
        )
        return True
    except Exception as e:
        st.error(f"Error de Storage: {str(e)}")
        return False
def listar_documentos(bucket, prefijo=""):
    """Lista los archivos dentro de una carpeta (expediente) en Supabase Storage."""
    try:
        respuesta = db.storage.from_(bucket).list(prefijo)
        return respuesta
    except Exception as e:
        st.error(f"Error al listar archivos: {str(e)}")
        return []

def obtener_url_descarga(bucket, ruta_archivo):
    """Genera el enlace público para descargar o ver el archivo."""
    try:
        return db.storage.from_(bucket).get_public_url(ruta_archivo)
    except:
        return ""
def descargar_documento_bytes(bucket, ruta_archivo):
    """Descarga los datos puros de un archivo para poder comprimirlo en un ZIP."""
    try:
        return db.storage.from_(bucket).download(ruta_archivo)
    except Exception as e:
        return None
def listar_modelos():
    """Trae la lista de plantillas .docx guardadas en el bucket."""
    try:
        res = db.storage.from_('plantillas').list()
        return [f['name'] for f in res if f['name'].endswith('.docx')]
    except:
        return []

def subir_a_expediente(file_data, file_name, carpeta_cliente):
    """Guarda el documento generado en la carpeta del cliente en el bucket."""
    path = f"{carpeta_cliente}/{file_name}"
    try:
        db.storage.from_('expedientes').upload(path, file_data, {"content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"})
        return True
    except:
        return False
