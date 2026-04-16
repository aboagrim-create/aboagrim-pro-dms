# =====================================================================
# MOTOR DE BASE DE DATOS Y AUTOMATIZACIÓN (SUPABASE)
# Sistema: AboAgrim Pro DMS v17.1
# =====================================================================

import streamlit as st
from supabase import create_client, Client
import io

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
    # Definición de las 7 categorías de roles del sistema
    roles_permitidos = [
        "agrimensor", 
        "abogado", 
        "notario", 
        "representante", 
        "apoderado", 
        "reclamante", 
        "solicitante"
    ]
    
    # Crear un diccionario vacío con listas para cada rol
    diccionario_roles = {rol: [] for rol in roles_permitidos}
    
    try:
        # Consulta a la tabla personas en Supabase
        respuesta = db.table("personas").select("id, nombre_completo, rol").execute()
        
        # Clasificar cada persona en su lista correspondiente
        for persona in respuesta.data:
            rol_actual = persona.get('rol')
            nombre_actual = persona.get('nombre_completo')
            
            if rol_actual in diccionario_roles:
                diccionario_roles[rol_actual].append(nombre_actual)
                
    except Exception as e:
        # Falla silenciosa para evitar romper la interfaz si la tabla está vacía
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
        # Traer todos los expedientes ordenados por fecha de creación
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
# 5. MOTOR DE PLANTILLAS WORD (DOCXTPL)
# ---------------------------------------------------------------------
def procesar_plantilla_maestra(contexto, plantilla_bytes):
    """
    Recibe un diccionario con datos (contexto) y un archivo Word en bytes.
    Reemplaza las variables y devuelve un nuevo archivo Word listo para descargar.
    """
    try:
        from docxtpl import DocxTemplate
        
        # Cargar la plantilla desde la memoria (BytesIO)
        documento = DocxTemplate(io.BytesIO(plantilla_bytes))
        
        # Procesar e inyectar las variables
        documento.render(contexto)
        
        # Guardar el resultado en un nuevo espacio de memoria
        archivo_salida = io.BytesIO()
        documento.save(archivo_salida)
        archivo_salida.seek(0)
        
        return archivo_salida
        
    except Exception as e:
        return None
