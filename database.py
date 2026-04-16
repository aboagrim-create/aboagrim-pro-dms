# =====================================================================
# MOTOR DE BASE DE DATOS Y AUTENTICACIÓN (SUPABASE)
# Sistema: AboAgrim Pro DMS v18.0 (Edición Limpia)
# =====================================================================

import streamlit as st
from supabase import create_client, Client

# ---------------------------------------------------------------------
# 1. CONEXIÓN AL SERVIDOR EN LA NUBE
# ---------------------------------------------------------------------
@st.cache_resource
def get_supabase() -> Client:
    """
    Establece y mantiene la conexión segura con la base de datos Supabase
    utilizando las credenciales almacenadas en Streamlit Secrets.
    """
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    
    cliente_supabase = create_client(url, key)
    return cliente_supabase

# Inicializar la variable de base de datos
db = get_supabase()

# ---------------------------------------------------------------------
# 2. EXTRACCIÓN DE PERFILES PROFESIONALES
# ---------------------------------------------------------------------
def obtener_diccionario_maestro():
    """
    Recupera el listado completo de profesionales y clientes,
    organizándolos por su rol para poblar los menús desplegables.
    """
    roles_permitidos = [
        "agrimensor", 
        "abogado", 
        "notario", 
        "representante", 
        "apoderado", 
        "reclamante", 
        "solicitante"
    ]
    
    diccionario_roles = {rol: [] for rol in roles_permitidos}
    
    try:
        respuesta = db.table("personas").select("id, nombre_completo, rol").execute()
        
        for persona in respuesta.data:
            rol_actual = persona.get('rol')
            nombre_actual = persona.get('nombre_completo')
            
            if rol_actual in diccionario_roles:
                diccionario_roles[rol_actual].append(nombre_actual)
                
    except Exception as e:
        pass
        
    return diccionario_roles

# ---------------------------------------------------------------------
# 3. EXTRACCIÓN DE EXPEDIENTES (MANDO CENTRAL)
# ---------------------------------------------------------------------
def consultar_todo():
    """
    Descarga todos los casos registrados para alimentar el Dashboard
    y las tablas del Mando Central.
    """
    try:
        respuesta = db.table("casos").select("*").order("created_at", desc=True).execute()
        return respuesta.data
    except Exception as e:
        return []

# ---------------------------------------------------------------------
# 4. INSERCIÓN DE NUEVOS REGISTROS
# ---------------------------------------------------------------------
def registrar_evento(tabla, datos):
    """
    Función universal para insertar datos en cualquier tabla (casos, personas, etc.)
    Retorna True si el guardado fue exitoso, False si hubo error.
    """
    try:
        db.table(tabla).insert(datos).execute()
        return True
    except Exception as e:
        return False

# ---------------------------------------------------------------------
# 5. SISTEMA DE AUTENTICACIÓN (LOGIN)
# ---------------------------------------------------------------------
def autenticar_usuario(email, password):
    """
    Se comunica con el endpoint de Supabase Auth para verificar las credenciales.
    Retorna True y los datos del usuario si es exitoso, False si falla.
    """
    try:
        respuesta = db.auth.sign_in_with_password({"email": email, "password": password})
        if respuesta.session:
            return True, respuesta.user
        return False, None
    except Exception as e:
        return False, None
