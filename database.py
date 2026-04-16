# =====================================================================
# MOTOR DE BASE DE DATOS Y AUTENTICACIÓN (SUPABASE)
# Sistema: AboAgrim Pro DMS v18.0
# =====================================================================

import streamlit as st
from supabase import create_client, Client

# ---------------------------------------------------------------------
# 1. CONEXIÓN AL SERVIDOR EN LA NUBE
# ---------------------------------------------------------------------
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

db = get_supabase()

# ---------------------------------------------------------------------
# 2. EXTRACCIÓN DE PERFILES PROFESIONALES
# ---------------------------------------------------------------------
def obtener_diccionario_maestro():
    roles = ["agrimensor", "abogado", "notario", "representante", "apoderado", "reclamante", "solicitante"]
    dic = {rol: [] for rol in roles}
    try:
        respuesta = db.table("personas").select("id, nombre_completo, rol").execute()
        for p in respuesta.data:
            rol_actual = p.get('rol')
            if rol_actual in dic:
                dic[rol_actual].append(p.get('nombre_completo'))
    except Exception:
        pass
    return dic

# ---------------------------------------------------------------------
# 3. EXTRACCIÓN DE EXPEDIENTES (Arreglado para recibir búsquedas)
# ---------------------------------------------------------------------
def consultar_todo(busqueda=""):
    """
    Descarga todos los casos registrados. 
    Ahora acepta un parámetro de 'busqueda' para que no dé error en el Archivo Digital.
    """
    try:
        respuesta = db.table("casos").select("*").order("created_at", desc=True).execute()
        datos = respuesta.data
        
        # Si la interfaz envía un texto de búsqueda, filtramos los resultados
        if busqueda:
            datos_filtrados = []
            for caso in datos:
                # Busca coincidencias en cualquier parte del caso
                if busqueda.lower() in str(caso).lower():
                    datos_filtrados.append(caso)
            return datos_filtrados
            
        return datos
    except Exception:
        return []

# ---------------------------------------------------------------------
# 4. INSERCIÓN DE NUEVOS REGISTROS
# ---------------------------------------------------------------------
def registrar_evento(tabla, datos):
    try:
        db.table(tabla).insert(datos).execute()
        return True
    except Exception:
        return False

# ---------------------------------------------------------------------
# 5. SISTEMA DE AUTENTICACIÓN (LOGIN)
# ---------------------------------------------------------------------
def autenticar_usuario(email, password):
    try:
        respuesta = db.auth.sign_in_with_password({"email": email, "password": password})
        if respuesta.session:
            return True, respuesta.user
        return False, None
    except Exception:
        return False, None

# =====================================================================
# 6. FUNCIONES RESTAURADAS PARA INTERFAZ AVANZADA (Plantillas, Alertas, Facturas)
# =====================================================================

def consultar_plantillas():
    """Recupera la lista de plantillas disponibles."""
    try:
        respuesta = db.table("plantillas").select("*").execute()
        return respuesta.data
    except Exception:
        return [] # Retorna lista vacía si falla para no romper la interfaz

def consultar_alertas(solo_pendientes=False):
    """
    Recupera las alertas.
    Acepta el parámetro 'solo_pendientes' que requiere la interfaz.
    """
    try:
        consulta = db.table("alertas").select("*")
        if solo_pendientes:
            consulta = consulta.eq("estado", "Pendiente")
        respuesta = consulta.execute()
        return respuesta.data
    except Exception:
        return []

def consultar_facturas():
    """Recupera el historial de facturación y pagos."""
    try:
        respuesta = db.table("pagos").select("*").execute()
        return respuesta.data
    except Exception:
        return []
