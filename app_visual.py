import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import pandas as pd
import io
from docxtpl import DocxTemplate

# ==========================================
# ⚙️ CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="AboAgrim Pro", layout="wide", page_icon="⚖️")

# Conexión a Supabase
try:
    url: str = st.secrets["supabase_url"]
    key: str = st.secrets["supabase_key"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Error de configuración de la Base de Datos. Verifique los 'secrets'.")

# Control de Sesión
if "admin_autenticado" not in st.session_state:
    st.session_state.admin_autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = "Invitado"
if "rol" not in st.session_state:
    st.session_state.rol = "Pasante"

# ==========================================
# 📂 MÓDULOS DEL SISTEMA (LAS PANTALLAS)
# ==========================================

def vista_registro_maestro():
    st.title("👤 Registro Maestro de Expedientes")
    st.subheader("Base de Datos Oficial | AboAgrim")
    
    tab1, tab2 = st.tabs(["➕ Nuevo Ingreso", "🔍 Ver/Editar Expedientes"])
    
    with tab1:
        with st.form("form_nuevo_caso", clear_on_submit=True):
            st.markdown("#### Datos Principales")
            c1, c2, c3 = st.columns([2, 3, 2])
            exp_n = c1.text_input("Número de Expediente:", placeholder="Ej: 2026-0001")
            prop_n = c2.text_input("Nombre del Cliente/Propietario:")
            ced_n = c3.text_input("Cédula/RNC:")
            
            st.markdown("#### Datos Técnicos e Inmobiliarios")
            c4, c5, c6 = st.columns(3)
            tipo_n = c4.selectbox("Tipo de Acto:", ["Mensura Catastral", "Deslinde", "Litis", "Condominio", "Saneamiento"])
            parc_n = c5.text_input("Parcela:")
            dc_n = c6.text_input("D.C.:")
            
            mun_n = st.text_input("Municipio y Provincia:")
            
            if st.form_submit_button("🚀 Registrar en Base de Datos"):
                if exp_n and prop_n:
                    try:
                        nueva_data = {
                            "expediente": exp_n,
                            "nombre_propietario": prop_n,
                            "cedula": ced_n,
                            "tipo_acto": tipo_n,
                            "parcela": parc_n,
                            "dc": dc_n,
                            "municipio": mun_n,
                            "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
                        }
                        supabase.table("expedientes_maestros").insert(nueva_data).execute()
                        st.success(f"✅ ¡Éxito! El expediente {exp_n} ha sido blindado en la nube.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error al conectar con la nube: {e}")
                else:
                    st.warning("⚠️ El número de expediente y nombre del propietario son obligatorios.")

    with tab2:
        st.markdown("#### Buscador de Expedientes")
        try:
            res = supabase.table("expedientes_maestros").select("*").order("fecha_creacion", desc=True).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                columnas = ["expediente", "nombre_propietario", "tipo_acto", "parcela", "dc", "fecha_creacion"]
                st.dataframe(df[columnas], use_container_width=True)
            else:
                st.info("No hay registros disponibles para mostrar.")
        except Exception as e:
            st.error(f"Error al cargar la tabla: {e}")

def vista_archivo_digital():
    st.title("📂 Archivo Digital Centralizado")
    st.subheader("Bóveda Documental de AboAgrim")
    
    try:
        res_e = supabase.table("expedientes_maestros").select("expediente, nombre_propietario").execute()
        list_e = [f"{e['expediente']} - {e['nombre_propietario']}" for e in res_e.data] if res_e.data else []
    except:
        list_e = []
        
    sel_exp = st.selectbox("Seleccione Expediente para ver sus documentos:", ["Ver Todos"] + list_e)
    st.divider()

    try:
        query = supabase.table("archivo_digital").select("*")
        if sel_exp != "Ver Todos":
            query = query.eq("codigo_expediente", sel_exp.split(" - ")[0])
        
        docs = query.execute()
        
        if docs.data:
            for d in docs.data:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    c1.markdown(f"📄 **{d['nombre_documento']}**")
                    c1.caption(f"Expediente Vinculado: {d.get('codigo_expediente', 'N/A')}")
                    c2.link_button("👁️ Abrir", d['url_enlace'], use_container_width=True)
        else:
            st.info("No se encontraron documentos vinculados para este filtro.")
    except Exception as e:
        st.error(f"Error al cargar archivos: {e}")

def vista_plantillas_auto():
    st.title("📄 Plantillas Automáticas")
    st.info("Módulo en construcción. Se activará próximamente.")

def vista_alertas_plazos():
    st.title("📅 Radar de Alertas JI")
    st.subheader("Control Normativo 2026")
    hoy = datetime.now().date()
    
    try:
        res = supabase.table("expedientes_maestros").select("*").execute()
        
        t1, t2 = st.tabs(["🛠️ Plazos de Mensura (60 días)", "⚖️ Audiencias y Apelaciones"])
        
        with t1:
            st.markdown("### Control de Trabajo de Campo")
            if res.data:
                for caso in res.data:
                    if caso.get('fecha_creacion'):
                        f_ini = datetime.strptime(caso['fecha_creacion'][:10], '%Y-%m-%d').date()
                        vencimiento = f_ini + timedelta(days=60)
                        dias_restantes = (vencimiento - hoy).days
                        
                        if dias_restantes <= 15:
                            st.error(f"🔴 **CRÍTICO:** Exp {caso['expediente']} - {caso['nombre_propietario']} vence en {dias_restantes} días.")
                        elif dias_restantes <= 30:
                            st.warning(f"🟡 **ATENCIÓN:** Exp {caso['expediente']} tiene {dias_restantes} días restantes.")
            else:
                st.info("No hay expedientes para evaluar en la base de datos.")
                
        with t2:
            st.markdown("### Próximas Audiencias")
            st.info("Módulo judicial activo. Sin vistas programadas en los próximos 7 días.")
    except Exception as e:
        st.error(f"Error de conexión: {e}")

def vista_facturacion():
    st.title("💵 Facturación y Honorarios")
    st.write("Módulo financiero en desarrollo.")

def vista_configuracion():
    st.title("⚙️ Configuración y Accesos")
    if st.session_state.admin_autenticado:
        st.success(f"Sesión activa: {st.session_state.rol}")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.admin_autenticado = False
            st.rerun()
    else:
        u = st.text_input("Usuario Master:")
        p = st.text_input("PIN:", type="password")
        if st.button("🔑 Entrar"):
            if u == "JhonnyMatos" and p == "1234":
                st.session_state.admin_autenticado = True
                st.session_state.rol = "Presidente Fundador"
                st.rerun()

# ==========================================
# 🚦 ENRUTADOR PRINCIPAL (MENÚ LATERAL)
# ==========================================
modulos = ["🏠 Mando Central", "👤 Registro Maestro", "📂 Archivo Digital", "📄 Plantillas Auto", "📅 Alertas y Plazos"]

if st.session_state.admin_autenticado:
    modulos.append("💵 Facturación")
    modulos.append("⚙️ Configuración")
else:
    modulos.append("⚙️ Configuración")

with st.sidebar:
    st.markdown(f"**Firmado como:** {st.session_state.usuario}")
    st.caption(f"**Nivel de Acceso:** {st.session_state.rol}")
    menu = st.radio("Ir a:", modulos, key="menu_lateral_maestro")

# Salto de pantallas según selección
if menu == "🏠 Mando Central":
    st.info("Bienvenido al Mando Central de AboAgrim Pro")
elif menu == "👤 Registro Maestro":
    vista_registro_maestro()
elif menu == "📂 Archivo Digital":
    vista_archivo_digital()
elif menu == "📄 Plantillas Auto":
    vista_plantillas_auto()
elif menu == "📅 Alertas y Plazos":
    vista_alertas_plazos()
elif menu == "💵 Facturación":
    vista_facturacion()
elif menu == "⚙️ Configuración":
    vista_configuracion()
