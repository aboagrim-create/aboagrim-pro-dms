import streamlit as st
from supabase import create_client, Client
import json
from datetime import datetime

# Conexión Segura con los Secretos que usted guardó
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

PLANTILLAS_DIR = "plantillas_maestras"

def guardar_expediente_elite(d):
    data = {
        "cliente_nombre": d['n'], "cedula_rnc": d['c'], "telefono": d['t'],
        "monto": d['m'], "pagado": d['pg'], "actuacion": d['act'],
        "fecha_apertura": d['f'], "jurisdiccion": d['jur'],
        "inmuebles_json": d['inm'], "apoderados_json": d['apo'],
        "profesionales_json": d['prof'], "estado": "Investigación",
        "ruta_carpeta": f"Expedientes/{d['n']}"
    }
    return supabase.table("expedientes").insert(data).execute()

def consultar_todo(busqueda=""):
    query = supabase.table("expedientes").select("*").order("id", desc=True)
    if busqueda:
        query = query.ilike("cliente_nombre", f"%{busqueda}%")
    res = query.execute()
    return res.data

def obtener_por_id(id_exp):
    res = supabase.table("expedientes").select("*").eq("id", id_exp).single().execute()
    return res.data

def actualizar_expediente_estado(id_exp, n_estado, n_pago):
    supabase.table("expedientes").update({"estado": n_estado, "pagado": n_pago}).eq("id", id_exp).execute()

def borrar_expediente(id_exp):
    supabase.table("expedientes").delete().eq("id", id_exp).execute()

def consultar_facturas():
    res = supabase.table("facturas").select("*, expedientes(cliente_nombre, cedula_rnc, actuacion)").order("id", desc=True).execute()
    final_data = []
    for r in res.data:
        if r.get('expedientes'):
            r['cliente_nombre'] = r['expedientes']['cliente_nombre']
            r['cedula_rnc'] = r['expedientes']['cedula_rnc']
            r['actuacion'] = r['expedientes']['actuacion']
        final_data.append(r)
    return final_data

def upsert_factura(id_f, exp_id, ncf, fecha, concepto, sub, itbis, total, estado):
    data = {"expediente_id": exp_id, "ncf": ncf, "fecha_emision": fecha, "concepto": concepto, "subtotal": sub, "itbis": itbis, "total": total, "estado": estado}
    if id_f: supabase.table("facturas").update(data).eq("id", id_f).execute()
    else: supabase.table("facturas").insert(data).execute()

def registrar_abono_factura(id_f, monto_abono, forma, etapa):
    factura = supabase.table("facturas").select("*").eq("id", id_f).single().execute().data
    historial = json.loads(factura.get('historial_pagos') or '[]')
    historial.append({"fecha": datetime.now().strftime("%d/%m/%Y"), "monto": monto_abono, "forma": forma, "etapa": etapa})
    total_pagado = sum(p['monto'] for p in historial)
    nuevo_estado = "Pagada" if total_pagado >= factura['total'] else "Pago Parcial"
    supabase.table("facturas").update({"monto_pagado": total_pagado, "historial_pagos": json.dumps(historial), "estado": nuevo_estado}).eq("id", id_f).execute()

def borrar_factura(id_f):
    supabase.table("facturas").delete().eq("id", id_f).execute()

def consultar_alertas(solo_pendientes=True):
    query = supabase.table("alertas").select("*, expedientes(cliente_nombre)")
    if solo_pendientes: query = query.eq("estado", "Pendiente")
    res = query.order("fecha_vencimiento").execute()
    for r in res.data:
        if r.get('expedientes'): r['cliente_nombre'] = r['expedientes']['cliente_nombre']
    return res.data

def upsert_alerta(id_a, exp_id, tipo, fecha, desc, estado="Pendiente"):
    data = {"expediente_id": exp_id, "tipo_alerta": tipo, "fecha_vencimiento": fecha, "descripcion": desc, "estado": estado}
    if id_a: supabase.table("alertas").update(data).eq("id", id_a).execute()
    else: supabase.table("alertas").insert(data).execute()

def consultar_plantillas():
    return supabase.table("plantillas").select("*").execute().data

def auto_registrar_plantilla(nombre_archivo):
    existe = supabase.table("plantillas").select("*").eq("archivo_word", nombre_archivo).execute()
    if not existe.data:
        supabase.table("plantillas").insert({"nombre_mostrar": nombre_archivo.replace(".docx", ""), "archivo_word": nombre_archivo, "carpeta_destino_sugerida": "General"}).execute()

def borrar_plantilla(id_p):
    supabase.table("plantillas").delete().eq("id", id_p).execute()
# Pégalo al final de database.py
def obtener_diccionario_maestro():
    """Trae todas las variables (etiquetas) desde Supabase"""
    try:
        query = supabase.table("variables_sistema").select("*").execute()
        return query.data
    except Exception as e:
        st.error(f"Error al conectar con el diccionario: {e}")
        return []
# Agregue esto al final de database.py
from docxtpl import DocxTemplate
import os

def procesar_plantilla_maestra(datos, nombre_plantilla):
    """Genera el Word y lo guarda en la carpeta del cliente"""
    try:
        # 1. Ruta de la plantilla y carpeta de salida
        ruta_plantilla = os.path.join("plantillas_maestras", nombre_plantilla)
        carpeta_cliente = f"Expedientes/{datos['cliente_nombre']}"
        
        if not os.path.exists(carpeta_cliente):
            os.makedirs(carpeta_cliente)
            
        # 2. Cargar y procesar
        doc = DocxTemplate(ruta_plantilla)
        doc.render(datos) # Aquí se llenan etiquetas como {{ parcela }} [cite: 27]
        
        # 3. Guardar archivo final
        ruta_final = os.path.join(carpeta_cliente, f"GENERADO_{nombre_plantilla}")
        doc.save(ruta_final)
        return ruta_final
    except Exception as e:
        return f"Error: {e}"
