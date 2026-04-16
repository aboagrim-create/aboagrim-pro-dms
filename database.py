import sqlite3
import os

DB_NAME = "aboagrim.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def ejecutar_ddl():
    """Asegura que todas las tablas existan al iniciar."""
    if os.path.exists('ddl.sql'):
        try:
            conn = get_db_connection()
            with open('ddl.sql', 'r', encoding='utf-8') as f:
                conn.cursor().executescript(f.read())
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error en DDL: {e}")

def obtener_diccionario_maestro():
    """Extrae abogados, agrimensores y técnicos para los menús."""
    roles = ["agrimensor", "abogado", "notario", "representante", "apoderado", "reclamante", "solicitante"]
    diccionario = {rol: [] for rol in roles}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for rol in roles:
            cursor.execute("SELECT id, nombre_completo FROM personas WHERE rol = ?", (rol,))
            diccionario[rol] = [dict(row) for row in cursor.fetchall()]
        conn.close()
    except Exception:
        pass
    return diccionario

def consultar_todo():
    """Trae todos los expedientes para las gráficas del Mando Central."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM casos ORDER BY fecha_apertura DESC")
        res = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return res
    except Exception:
        return []

def guardar_persona(nombre, rol, id_doc=""):
    """Registra nuevos profesionales o clientes."""
    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO personas (nombre_completo, rol, identificacion) VALUES (?, ?, ?)", (nombre, rol, id_doc))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def procesar_plantilla_maestra(contexto, ruta_plantilla, ruta_salida):
    """Genera el contrato o solicitud en Word automáticamente."""
    try:
        from docxtpl import DocxTemplate
        if not os.path.exists(ruta_plantilla): return False
        doc = DocxTemplate(ruta_plantilla)
        doc.render(contexto)
        doc.save(ruta_salida)
        return True
    except Exception:
        return False
