import sqlite3
import os

DB_NAME = "aboagrim.db"

def get_db_connection():
    """Establece la conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def obtener_diccionario_maestro():
    """
    Recupera las listas de profesionales y roles para poblar 
    los menús desplegables en el Registro Maestro y formularios.
    Incluye todos los roles técnicos solicitados.
    """
    diccionario_maestro = {
        "agrimensor": [],
        "abogado": [],
        "notario": [],
        "representante": [],
        "apoderado": [],
        "reclamante": [],
        "solicitante": []
    }
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Extraemos los registros para cada rol
        for rol in diccionario_maestro.keys():
            try:
                cursor.execute("SELECT id, nombre_completo FROM personas WHERE rol = ?", (rol,))
                resultados = cursor.fetchall()
                diccionario_maestro[rol] = [dict(row) for row in resultados]
            except sqlite3.OperationalError:
                # Si la tabla aún no se ha creado, pasamos silenciosamente para no colapsar la app
                pass 
                
        conn.close()
        return diccionario_maestro
        
    except Exception as e:
        print(f"Error crítico al conectar con la base de datos: {e}")
        return diccionario_maestro

def ejecutar_ddl():
    """Ejecuta el archivo ddl.sql para asegurar que las tablas existan."""
    if os.path.exists('ddl.sql'):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            with open('ddl.sql', 'r', encoding='utf-8') as f:
                sql_script = f.read()
            cursor.executescript(sql_script)
            conn.commit()
            conn.close()
            print("Base de datos estructurada correctamente.")
        except Exception as e:
            print(f"Error al ejecutar DDL: {e}")
