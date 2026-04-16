import sqlite3
import os
import json
from datetime import datetime
import sqlite3

from database import obtener_diccionario_maestro
def obtener_diccionario_maestro(db_name="aboagrim.db"):
    """
    Recupera las listas de profesionales y roles para poblar 
    los menús desplegables en el Registro Maestro y formularios.
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
        conn = sqlite3.connect(db_name)
        # Permite acceder a las columnas por su nombre
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        # Lógica para extraer los datos de tu base de datos SQLite.
        # Ajusta el nombre de la tabla ('contactos' o 'personas') según tu esquema.
        # Este es un ejemplo asumiendo una tabla unificada con una columna 'rol':
        
        for rol in diccionario_maestro.keys():
            try:
                # Se busca en la base de datos por el rol específico
                cursor.execute("SELECT id, nombre_completo FROM personas WHERE rol = ?", (rol,))
                resultados = cursor.fetchall()
                diccionario_maestro[rol] = [dict(row) for row in resultados]
            except sqlite3.OperationalError:
                # Si la tabla o columna aún no existe, evita que el sistema colapse
                pass 
                
        conn.close()
        return diccionario_maestro
        
    except Exception as e:
        print(f"Error crítico al conectar con la base de datos: {e}")
        return diccionario_maestro # Retorna vacío pero no rompe la app

# --- INFRAESTRUCTURA ---
CARPETA_RAIZ = "Expedientes_AboAgrim"
PLANTILLAS_DIR = "plantillas_maestras"

def obtener_conexion():
    conn = sqlite3.connect('aboagrim.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_sistema():
    if not os.path.exists(CARPETA_RAIZ): os.makedirs(CARPETA_RAIZ)
    if not os.path.exists(PLANTILLAS_DIR): os.makedirs(PLANTILLAS_DIR)
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # 1. Tabla de Expedientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expedientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_nombre TEXT, cedula_rnc TEXT, telefono TEXT,
            monto REAL DEFAULT 0, pagado REAL DEFAULT 0, estado TEXT DEFAULT 'Investigación',
            actuacion TEXT, fecha_apertura TEXT, requisitos TEXT, notas TEXT,
            ruta_carpeta TEXT, referencia TEXT, area_m2 REAL DEFAULT 0, jurisdiccion TEXT,
            inmuebles_json TEXT, apoderados_json TEXT, profesionales_json TEXT,
            fecha_modificacion TEXT, plantillas_asignadas TEXT
        )
    """)

    # 2. Tabla de Plantillas Maestras
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plantillas_db (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_mostrar TEXT, archivo_word TEXT, carpeta_destino_sugerida TEXT,
            tramite_asociado TEXT, tipo_plantilla TEXT
        )
    """)
    
    # 3. Tabla de Alertas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas_db (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expediente_id INTEGER, tipo_alerta TEXT, fecha_vencimiento TEXT,
            descripcion TEXT, estado TEXT DEFAULT 'Pendiente'
        )
    """)

    # 4. Tabla de Facturación
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facturas_db (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expediente_id INTEGER,
            ncf TEXT,
            fecha_emision TEXT,
            concepto TEXT,
            subtotal REAL,
            itbis REAL,
            total REAL,
            estado TEXT DEFAULT 'Pendiente',
            monto_pagado REAL DEFAULT 0,
            historial_pagos TEXT DEFAULT '[]'
        )
    """)
    
    # Auto-Reparación de Columnas
    cursor.execute("PRAGMA table_info(expedientes)")
    cols_e = [c[1] for c in cursor.fetchall()]
    for col in ["inmuebles_json", "apoderados_json", "profesionales_json", "referencia", "jurisdiccion", "fecha_modificacion", "plantillas_asignadas"]:
        if col not in cols_e: cursor.execute(f"ALTER TABLE expedientes ADD COLUMN {col} TEXT")
            
    cursor.execute("PRAGMA table_info(plantillas_db)")
    cols_p = [c[1] for c in cursor.fetchall()]
    for col in ["tramite_asociado", "tipo_plantilla"]:
        if col not in cols_p: cursor.execute(f"ALTER TABLE plantillas_db ADD COLUMN {col} TEXT DEFAULT 'General'")
            
    cursor.execute("PRAGMA table_info(facturas_db)")
    cols_f = [c[1] for c in cursor.fetchall()]
    if "monto_pagado" not in cols_f: cursor.execute("ALTER TABLE facturas_db ADD COLUMN monto_pagado REAL DEFAULT 0")
    if "historial_pagos" not in cols_f: cursor.execute("ALTER TABLE facturas_db ADD COLUMN historial_pagos TEXT DEFAULT '[]'")
            
    conn.commit()
    conn.close()

# --- FUNCIÓN DE UPSERT (AUTO-DESCUBRIMIENTO) ---
def auto_registrar_plantilla(nombre_archivo):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM plantillas_db WHERE archivo_word = ?", (nombre_archivo,))
    if not cursor.fetchone():
        nombre_bonito = nombre_archivo.replace(".docx", "").replace("_", " ")
        cursor.execute("""
            INSERT INTO plantillas_db (nombre_mostrar, archivo_word, carpeta_destino_sugerida, tramite_asociado, tipo_plantilla)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre_bonito, nombre_archivo, "4_Contratos_Legales", "General (Aplica a todo)", "Instancia JI"))
        conn.commit()
    conn.close()

# --- FUNCIONES DE FACTURACIÓN Y PAGOS ---
def upsert_factura(id_f, exp_id, ncf, fecha, concepto, subtotal, itbis, total, estado='Pendiente'):
    conn = obtener_conexion()
    cursor = conn.cursor()
    if id_f:
        cursor.execute("UPDATE facturas_db SET expediente_id=?, ncf=?, fecha_emision=?, concepto=?, subtotal=?, itbis=?, total=?, estado=? WHERE id=?", 
                       (exp_id, ncf, fecha, concepto, subtotal, itbis, total, estado, id_f))
    else:
        cursor.execute("INSERT INTO facturas_db (expediente_id, ncf, fecha_emision, concepto, subtotal, itbis, total, estado, monto_pagado, historial_pagos) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, '[]')", 
                       (exp_id, ncf, fecha, concepto, subtotal, itbis, total, estado))
    conn.commit()
    conn.close()

def consultar_facturas():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.*, e.cliente_nombre, e.cedula_rnc, e.actuacion 
        FROM facturas_db f 
        LEFT JOIN expedientes e ON f.expediente_id = e.id
        ORDER BY f.id DESC
    """)
    res = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return res

def registrar_abono_factura(id_f, monto_abono, forma_pago, etapa_pago):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT total, monto_pagado, historial_pagos FROM facturas_db WHERE id=?", (id_f,))
    row = cursor.fetchone()
    if row:
        total = float(row['total'])
        monto_pagado = float(row['monto_pagado'] or 0.0)
        historial = json.loads(row['historial_pagos'] or '[]')
        
        historial.append({
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "monto": monto_abono,
            "forma": forma_pago,
            "etapa": etapa_pago
        })
        
        nuevo_pagado = monto_pagado + monto_abono
        nuevo_estado = "Pagada" if nuevo_pagado >= total else "Pago Parcial"
        
        cursor.execute("UPDATE facturas_db SET monto_pagado=?, historial_pagos=?, estado=? WHERE id=?", 
                       (nuevo_pagado, json.dumps(historial), nuevo_estado, id_f))
        conn.commit()
    conn.close()

def borrar_factura(id_f):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM facturas_db WHERE id = ?", (id_f,))
    conn.commit()
    conn.close()

# --- FUNCIONES DE ALERTAS ---
def upsert_alerta(id_a, exp_id, tipo, fecha, desc, estado='Pendiente'):
    conn = obtener_conexion()
    cursor = conn.cursor()
    if id_a: cursor.execute("UPDATE alertas_db SET expediente_id=?, tipo_alerta=?, fecha_vencimiento=?, descripcion=?, estado=? WHERE id=?", (exp_id, tipo, fecha, desc, estado, id_a))
    else: cursor.execute("INSERT INTO alertas_db (expediente_id, tipo_alerta, fecha_vencimiento, descripcion, estado) VALUES (?, ?, ?, ?, ?)", (exp_id, tipo, fecha, desc, estado))
    conn.commit()
    conn.close()

def consultar_alertas(solo_pendientes=True):
    conn = obtener_conexion()
    cursor = conn.cursor()
    query = "SELECT a.*, e.cliente_nombre, e.actuacion FROM alertas_db a LEFT JOIN expedientes e ON a.expediente_id = e.id"
    if solo_pendientes: query += " WHERE a.estado = 'Pendiente'"
    query += " ORDER BY a.fecha_vencimiento ASC"
    cursor.execute(query)
    res = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return res

def borrar_alerta(id_a):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM alertas_db WHERE id = ?", (id_a,))
    conn.commit()
    conn.close()

# --- FUNCIONES DE PLANTILLAS Y EXPEDIENTES ---
def upsert_plantilla(id_p, nombre, archivo, carpeta, tramite, tipo):
    conn = obtener_conexion()
    cursor = conn.cursor()
    if id_p: cursor.execute("UPDATE plantillas_db SET nombre_mostrar=?, archivo_word=?, carpeta_destino_sugerida=?, tramite_asociado=?, tipo_plantilla=? WHERE id=?", (nombre, archivo, carpeta, tramite, tipo, id_p))
    else: cursor.execute("INSERT INTO plantillas_db (nombre_mostrar, archivo_word, carpeta_destino_sugerida, tramite_asociado, tipo_plantilla) VALUES (?, ?, ?, ?, ?)", (nombre, archivo, carpeta, tramite, tipo))
    conn.commit()
    conn.close()

def borrar_plantilla(id_p):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM plantillas_db WHERE id = ?", (id_p,))
    conn.commit()
    conn.close()

def consultar_plantillas():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plantillas_db ORDER BY tipo_plantilla, nombre_mostrar")
    res = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return res

def actualizar_plantillas_cliente(id_e, plantillas_json):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE expedientes SET plantillas_asignadas=? WHERE id=?", (plantillas_json, id_e))
    conn.commit()
    conn.close()

def guardar_expediente_elite(d):
    nombre_folder = d['n'].replace(" ", "_").replace(".", "")
    ruta_maestra = os.path.join(CARPETA_RAIZ, f"{nombre_folder}_{d['c']}")
    if not os.path.exists(ruta_maestra):
        os.makedirs(ruta_maestra)
        for sub in ["1_Identidad", "2_Titulos_Certificaciones", "3_Planos_Gabinete", "4_Contratos_Legales", "5_Correspondencia_JI"]: os.makedirs(os.path.join(ruta_maestra, sub))
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expedientes (cliente_nombre, cedula_rnc, telefono, monto, pagado, actuacion, fecha_apertura, ruta_carpeta, estado, referencia, requisitos, jurisdiccion, inmuebles_json, apoderados_json, profesionales_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (d['n'], d['c'], d['t'], d['m'], d['pg'], d['act'], d['f'], ruta_maestra, 'Investigación', d['ref'], d['req'], d['jur'], d['inm'], d['apo'], d['prof']))
    conn.commit()
    conn.close()

def actualizar_expediente_estado(id_e, nuevo_estado, nuevo_pagado):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE expedientes SET estado=?, pagado=?, fecha_modificacion=? WHERE id=?", (nuevo_estado, nuevo_pagado, datetime.now().strftime("%d/%m/%Y %H:%M"), id_e))
    conn.commit()
    conn.close()

def consultar_todo(busqueda=None):
    conn = obtener_conexion()
    cursor = conn.cursor()
    if busqueda: cursor.execute("SELECT * FROM expedientes WHERE cliente_nombre LIKE ? OR referencia LIKE ?", (f"%{busqueda}%", f"%{busqueda}%"))
    else: cursor.execute("SELECT * FROM expedientes ORDER BY id DESC")
    res = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return res

def obtener_por_id(id_e):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expedientes WHERE id = ?", (id_e,))
    fila = cursor.fetchone()
    conn.close()
    return dict(fila) if fila else None

def borrar_expediente(id_e):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expedientes WHERE id = ?", (id_e,))
    conn.commit()
    conn.close()

inicializar_sistema()
