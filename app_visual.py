import streamlit as st
import pandas as pd
from database import *

# --- Configuración de Interfaz ---
st.set_page_config(page_title="AboAgrim Pro DMS", layout="wide")

# --- Identidad Corporativa ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
st.sidebar.markdown("## Abogados y Agrimensores 'AboAgrim'")
st.sidebar.markdown("**Lic. Jhonny Matos. M.A., Presidente**")
st.sidebar.divider()

# Menú de Navegación
menu = st.sidebar.radio(
    "Módulos del Sistema",
    ["📊 Mando Central", "📝 Registro Catastral & Legal", "💰 Honorarios y Cobros", "📂 Archivo Digital DMS", "⚙️ Configuración"]
)

# --- 1. MANDO CENTRAL (Dashboard) ---
def vista_mando_central():
    st.title("📊 Mando Central: Resumen Operativo")
    casos = consultar_todo()
    
    if casos:
        df = pd.DataFrame(casos)
        # Métricas principales
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Expedientes", len(df))
        m2.metric("Deslindes", len(df[df['tipo_caso'] == 'Deslinde']) if 'tipo_caso' in df else 0)
        m3.metric("Litis", len(df[df['tipo_caso'] == 'Litis sobre derecho registrado']) if 'tipo_caso' in df else 0)
        m4.metric("Casos Abiertos", len(df[df['estado'] == 'Abierto']) if 'estado' in df else 0)

        col_izq, col_der = st.columns([2, 1])
        with col_izq:
            st.subheader("Buscador Global de Expedientes")
            busqueda = st.text_input("Filtrar por Cliente o Número:")
            if busqueda:
                df = df[df.astype(str).apply(lambda x: busqueda.lower() in x.str.lower().values, axis=1)]
            st.dataframe(df, use_container_width=True)
            
        with col_der:
            st.subheader("Distribución por Jurisdicción")
            if 'jurisdiccion' in df:
                st.bar_chart(df['jurisdiccion'].value_counts())
    else:
        st.info("Inicie registrando casos en el módulo de Registro.")

# --- 2. REGISTRO CATASTRAL & LEGAL ---
def vista_registro():
    st.title("📝 Registro Catastral y Legal")
    dic = obtener_diccionario_maestro()
    
    with st.form("form_registro_completo"):
        st.subheader("Información General del Caso")
        c1, c2, c3 = st.columns(3)
        numero = c1.text_input("Número de Expediente:")
        tipo = c2.selectbox("Tipo de Acto:", ["Deslinde", "Saneamiento", "Litis", "Transferencia", "Subdivisión"])
        jurisdiccion = c3.selectbox("Jurisdicción:", ["Santiago", "La Vega", "Santo Domingo", "Puerto Plata", "Moca"])
        
        st.subheader("Partes Interesadas")
        f1, f2 = st.columns(2)
        cliente = f1.text_input("Nombre del Cliente / Reclamante:")
        cedula = f2.text_input("Cédula / RNC:")
        
        st.subheader("Asignación de Personal Técnico")
        a1, a2, a3 = st.columns(3)
        agrimensor = a1.selectbox("Agrimensor:", dic['agrimensor'] or ["N/A"])
        abogado = a2.selectbox("Abogado:", dic['abogado'] or ["N/A"])
        notario = a3.selectbox("Notario:", dic['notario'] or ["N/A"])

        if st.form_submit_button("✅ Blindar y Guardar Expediente"):
            datos = {
                "numero_expediente": numero,
                "tipo_caso": tipo,
                "jurisdiccion": jurisdiccion,
                "cliente": cliente,
                "estado": "Abierto",
                "etapa": "Recepción"
            }
            if registrar_evento("casos", datos):
                st.success("Expediente registrado exitosamente en Supabase.")

# --- 3. HONORARIOS Y COBROS ---
def vista_honorarios():
    st.title("💰 Gestión Financiera de Honorarios")
    datos_fin = consultar_honorarios_completos()
    if datos_fin:
        df_fin = pd.DataFrame(datos_fin)
        st.dataframe(df_fin, use_container_width=True)
    else:
        st.warning("No hay registros financieros activos.")

# --- 4. ARCHIVO DIGITAL DMS ---
def vista_archivo():
    st.title("📂 Archivo Digital DMS")
    st.info("Gestión de archivos en la nube (Planos, Word, PDF).")
    uploaded_file = st.file_uploader("Subir documento técnico:", type=["docx", "pdf", "dwg"])
    if uploaded_file:
        st.success("Archivo preparado para carga.")

# --- Lógica de Enrutamiento Final ---
if menu == "📊 Mando Central":
    vista_mando_central()
elif menu == "📝 Registro Catastral & Legal":
    vista_registro()
elif menu == "💰 Honorarios y Cobros":
    vista_honorarios()
elif menu == "📂 Archivo Digital DMS":
    vista_archivo()
elif menu == "⚙️ Configuración":
    st.title("⚙️ Configuración General")
    st.write("Sistema AboAgrim Pro v17.1 - Estado: **Óptimo**")
import streamlit as st
from supabase import create_client, Client
import io

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

db = get_supabase()

def obtener_diccionario_maestro():
    roles = ["agrimensor", "abogado", "notario", "representante", "apoderado", "reclamante", "solicitante"]
    dic = {rol: [] for rol in roles}
    try:
        res = db.table("personas").select("id, nombre_completo, rol").execute()
        for p in res.data:
            rol_actual = p.get('rol')
            if rol_actual in dic:
                dic[rol_actual].append(p['nombre_completo'])
    except Exception:
        pass # Falla silenciosamente si la tabla no existe, sin romper la interfaz
    return dic

def consultar_todo():
    try:
        res = db.table("casos").select("*").order("fecha_apertura", desc=True).execute()
        return res.data
    except Exception:
        return []

def consultar_honorarios_completos():
    try:
        res = db.table("honorarios").select("*").execute()
        return res.data
    except Exception:
        return []

def registrar_evento(tabla, datos):
    try:
        db.table(tabla).insert(datos).execute()
        return True
    except Exception:
        return False

def procesar_plantilla_maestra(contexto, plantilla_bytes):
    try:
        from docxtpl import DocxTemplate
        doc = DocxTemplate(io.BytesIO(plantilla_bytes))
        doc.render(contexto)
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        return output
    except Exception:
        return None
