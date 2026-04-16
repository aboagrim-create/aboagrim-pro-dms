import sqlite3
import os

DB_NAME = "aboagrim.db"

def get_db_connection():
    """Establece la conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def obtener_diccionario_maestro():
    """Recupera las listas de profesionales para los menús desplegables."""
    diccionario_maestro = {
        "agrimensor": [], "abogado": [], "notario": [],
        "representante": [], "apoderado": [], "reclamante": [], "solicitante": []
    }
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for rol in diccionario_maestro.keys():
            try:
                cursor.execute("SELECT id, nombre_completo FROM personas WHERE rol = ?", (rol,))
                diccionario_maestro[rol] = [dict(row) for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                pass 
        conn.close()
        return diccionario_maestro
    except Exception:
        return diccionario_maestro

def consultar_todo():
    """
    Recupera todos los expedientes para armar las gráficas 
    y métricas del Mando Central.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Seleccionamos todos los casos para el DataFrame de pandas
        cursor.execute("SELECT * FROM casos")
        resultados = cursor.fetchall()
        conn.close()
        # Convertimos a una lista de diccionarios para que Streamlit/Pandas lo lea bien
        return [dict(row) for row in resultados]
    except Exception as e:
        print(f"Error consultando casos: {e}")
        return []

def ejecutar_ddl():
    """Ejecuta el archivo ddl.sql para asegurar la estructura de tablas."""
    if os.path.exists('ddl.sql'):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            with open('ddl.sql', 'r', encoding='utf-8') as f:
                cursor.executescript(f.read())
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error al ejecutar DDL: {e}")
def procesar_plantilla_maestra(contexto, ruta_plantilla, ruta_salida):
    """
    Automatiza la generación de documentos legales (Contratos, Solicitud de Mensura, etc.)
    fusionando los datos del sistema con plantillas de Word.
    """
    try:
        from docxtpl import DocxTemplate
        doc = DocxTemplate(ruta_plantilla)
        doc.render(contexto)
        doc.save(ruta_salida)
        return True
    except ImportError:
        print("Librería docxtpl no instalada en el entorno.")
        return False
    except Exception as e:
        print(f"Error procesando el documento legal: {e}")
        return False
