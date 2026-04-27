# =====================================================================
# INTERFAZ GRÁFICA Y SISTEMA EXPERTO LEGAL JI (EDICIÓN PREMIUM FULL)
# Sistema: AboAgrim Pro DMS 
# =====================================================================
import streamlit as st
import zipfile
import io
from docxtpl import DocxTemplate
# ... arriba están los import ...
# =========================================================
# MOTOR DE ESTILOS VISUALES (Se ejecuta siempre al inicio)
# =========================================================
if "tema_color" in st.session_state:
    # Definimos si el fondo es oscuro o claro
    bg_color = "#0e1117" if st.session_state["tema_fondo"] == "Oscuro Profundo" else "#ffffff"
    text_color = "#ffffff" if st.session_state["tema_fondo"] == "Oscuro Profundo" else "#000000"
    
    # Inyectamos el diseño personalizado en toda la aplicación
    custom_css = f"""
    <style>
        /* Cambiar color de fondo principal y texto */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
            font-family: {st.session_state['tema_fuente']} !important;
        }}
        /* Cambiar el color de todos los Títulos */
        h1, h2, h3, h4, h5, h6 {{
            color: {st.session_state['tema_color']} !important;
            font-family: {st.session_state['tema_fuente']} !important;
        }}
        /* Cambiar el color de los botones principales */
        .stButton>button[kind="primary"] {{
            background-color: {st.session_state['tema_color']};
            border-color: {st.session_state['tema_color']};
            color: white;
        }}
        /* Cambiar el color del texto en los inputs si el fondo es blanco */
        .stTextInput>div>div>input {{
            color: {text_color};
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
# ==========================================
# MOTOR DE GENERACIÓN DE DOCUMENTOS WORD
# ==========================================
def generar_documento_word(nombre_plantilla, diccionario_datos):

    
    ruta_plantilla = nombre_plantilla
    
    try:
        doc = DocxTemplate(ruta_plantilla)
        doc.render(diccionario_datos)
        
        archivo_salida = io.BytesIO()
        doc.save(archivo_salida)
        archivo_salida.seek(0)
        
        return archivo_salida
    except Exception as e:
        st.error(f"Error al generar {nombre_plantilla}: {e}")
        return None


if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

from supabase import create_client, Client

# --- CONEXIÓN A SUPABASE (CEREBRO DIGITAL) ---
url_supabase = "https://wqcpbxrltttfnusdrawq.supabase.co"
clave_supabase = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndxY3BieHJsdHR0Zm51c2RyYXdxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYyMTI2NjEsImV4cCI6MjA5MTc4ODY2MX0.uD7v_-rY0b4dJGRSeF1mtDeftNzopFNnyyx7IEhPKPs"

try:
    supabase: Client = create_client(url_supabase, clave_supabase)
except Exception as e:
    pass

from google.oauth2 import service_account
from googleapiclient.discovery import build

def crear_oficina_virtual(nombre_cliente, id_expediente, id_maestra):
    try:
        # Cargamos los secretos que pegamos en Streamlit
        info_llave = st.secrets["google_drive"]
        creds = service_account.Credentials.from_service_account_info(info_llave)
        drive_service = build('drive', 'v3', credentials=creds)

        nombre_carpeta = f"EXP-{id_expediente} | {nombre_cliente}"

        # 1. Crear Carpeta Principal
        meta_principal = {
            'name': nombre_carpeta,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [id_maestra]
        }
        archivo = drive_service.files().create(body=meta_principal, fields='id, webViewLink').execute()
        folder_id = archivo.get('id')
        link_web = archivo.get('webViewLink')

        # 2. Crear las 3 Subcarpetas (Orden Diamante)
        subcarpetas = ["01_DOCUMENTOS_LEGALES", "02_PLANOS_Y_TECNICO", "03_RECIBOS_Y_PAGOS"]
        for sub in subcarpetas:
            meta_sub = {'name': sub, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [folder_id]}
            drive_service.files().create(body=meta_sub).execute()

        return link_web
    except Exception as e:
        st.error(f"Error en Drive: {e}")
        return None
def generar_paquete_documentos(datos_formulario, rutas_plantillas):
    import io
    import zipfile
    import os
    from docxtpl import DocxTemplate
    
    # 1. El Mega Diccionario (Atrapa todo lo de la pantalla)
    contexto = dict(datos_formulario)
    contexto['profesional'] = "Lic. Jhonny Matos. M.A."
    contexto['cargo'] = "Presidente fundador AboAgrim"
    
    # 2. Si solo es un archivo, lo procesamos normal
    if len(rutas_plantillas) == 1:
        doc = DocxTemplate(rutas_plantillas[0])
        doc.render(contexto)
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer, f"Expediente_{contexto.get('nom_prop', 'AboAgrim')}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    # 3. Si son VARIOS archivos, creamos un archivo .ZIP con todos adentro
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for ruta in rutas_plantillas:
            doc = DocxTemplate(ruta)
            doc.render(contexto)
            
            temp_buffer = io.BytesIO()
            doc.save(temp_buffer)
            
            # Nombre del archivo procesado
            nombre_archivo = f"Listo_{os.path.basename(ruta)}"
            zip_file.writestr(nombre_archivo, temp_buffer.getvalue())
            
    zip_buffer.seek(0)
    return zip_buffer, f"Paquete_Expediente_{contexto.get('nom_prop', 'AboAgrim')}.zip", "application/zip"
# Asegúrese de que no haya nada repetido debajo de este bloque.
# =====================================================================
# MÓDULO 1: MANDO CENTRAL
# =====================================================================
def vista_mando():
    # Mantenemos su diseño elegante intacto
    st.markdown("""
        <div style='background:linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); padding:35px 30px; border-radius:12px; color:white; border-left:6px solid #FBBF24; margin-bottom: 20px;'>
            <h1 style='margin:0; font-size: 2.8rem; font-weight: 800;'>AboAgrim Pro DMS ⚖️</h1>
            <p style='font-size:1.2rem; color:#94A3B8; margin-bottom: 1rem;'>Centro de Mando: Jurisdicción Inmobiliaria y Mensura</p>
            <div style='font-size:1.1rem; color:#FBBF24; font-weight:600; text-transform:uppercase;'>Santiago | Lic. Jhonny Matos, M.A.</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📈 Desempeño Operativo en la Nube")

    try:
        # 1. Consultar datos reales de la nube Supabase
        respuesta = supabase.table("expedientes_maestros").select("*").execute()
        datos = respuesta.data
        total_expedientes = len(datos)

        # 2. Mostrar Indicadores Rápidos (Métricas reales)
        col1, col2, col3 = st.columns(3)
        col1.metric("Expedientes Totales", total_expedientes)
        col2.metric("Mensuras Pendientes", "Próximamente")
        col3.metric("Estado del Sistema", "En Línea ☁️")

        st.divider()

        # 3. Mostrar los últimos movimientos reales
        st.subheader("📝 Últimos Movimientos")
        
        if total_expedientes == 0:
            st.info("Aún no hay expedientes en la base de datos. ¡Empiece hoy mismo en el Registro Maestro!")
        else:
            import pandas as pd
            df = pd.DataFrame(datos)
            
            # Ordenamos para mostrar los más recientes arriba
            df_recientes = df.sort_values(by="fecha_creacion", ascending=False).head(5)
            
            # Limpiamos las columnas para la vista rápida
            df_vista = df_recientes.rename(columns={
                "expediente": "No. Exp",
                "nombre_propietario": "Propietario",
                "municipio": "Ubicación"
            })
            
            st.table(df_vista[["No. Exp", "Propietario", "Ubicación"]])
            st.caption("Mostrando los últimos 5 expedientes registrados en su archivo digital.")

    except Exception as e:
        st.error("⚠️ Error al conectar el Mando Central con la Bóveda Digital.")
# =====================================================================
# MÓDULO 2: REGISTRO MAESTRO (CON PESTAÑAS Y 7 ROLES)
# =====================================================================
import streamlit as st
import datetime


# =====================================================================
# MÓDULO 3: ARCHIVO DIGITAL (BÓVEDA, EXPLORADOR Y DESCARGA ZIP)
# =====================================================================
def vista_archivo():
    st.title("📁 Bóveda Digital DMS")
    tab1, tab2 = st.tabs(["⬆️ Cargar Documentos", "🗄️ Explorador de Bóveda"])
    
    with tab1:
        st.markdown("Vincule planos de Civil 3D (DWG), PDFs, o sentencias a un expediente.")
        exp = st.text_input("Vincular al Expediente N° (Ej. EXP-001):", key="upload_exp")
        archivos = st.file_uploader("Arrastre sus archivos aquí:", accept_multiple_files=True)
        
        if st.button("⬆️ Subir a la Nube Segura"):
            if exp.strip() != "" and archivos:
                with st.spinner("Encriptando y subiendo archivos a la Bóveda..."):
                    for archivo in archivos:
                        file_bytes = archivo.read()
                        ruta_segura = f"{exp.strip()}/{archivo.name}"
                        exito = subir_documento("expedientes", ruta_segura, file_bytes)
                        if exito:
                            st.success(f"✅ {archivo.name} guardado en {exp}.")
                    st.toast("Transferencia completada.", icon="☁️")
            else:
                st.warning("⚠️ Debe indicar el N° de Expediente y seleccionar al menos un archivo.")
                
    with tab2:
        st.markdown("### 🔍 Buscar Documentos por Expediente")
        exp_busqueda = st.text_input("Ingrese el N° de Expediente a consultar:", key="search_exp")
        
        if st.button("🗂️ Buscar Archivos"):
            if exp_busqueda.strip():
                archivos_encontrados = listar_documentos("expedientes", exp_busqueda.strip())
                
                if archivos_encontrados and len(archivos_encontrados) > 0:
                    st.success(f"Archivos encontrados para el expediente {exp_busqueda}:")
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # 1. Mostramos la lista normal
                    for arch in archivos_encontrados:
                        nombre_archivo = arch.get('name')
                        if nombre_archivo and nombre_archivo != '.emptyFolderPlaceholder':
                            ruta_completa = f"{exp_busqueda.strip()}/{nombre_archivo}"
                            url_descarga = obtener_url_descarga("expedientes", ruta_completa)
                            
                            col1, col2 = st.columns([3, 1])
                            col1.markdown(f"📄 **{nombre_archivo}**")
                            col2.markdown(f"<a href='{url_descarga}' target='_blank'><button style='width:100%; padding:5px; border-radius:5px; background-color:#1E3A8A; color:white; border:none; cursor:pointer;'>⬇️ Ver Individual</button></a>", unsafe_allow_html=True)
                            st.divider()
                    
                    # 2. Lógica para crear el archivo ZIP en memoria
                    st.markdown("### 📦 Descarga Masiva")
                    with st.spinner("Empaquetando expediente completo..."):
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                            for arch in archivos_encontrados:
                                nombre_archivo = arch.get('name')
                                if nombre_archivo and nombre_archivo != '.emptyFolderPlaceholder':
                                    ruta_completa = f"{exp_busqueda.strip()}/{nombre_archivo}"
                                    # Descargamos los bytes de cada archivo
                                    file_bytes = descargar_documento_bytes("expedientes", ruta_completa)
                                    if file_bytes:
                                        # Lo metemos dentro del ZIP
                                        zip_file.writestr(nombre_archivo, file_bytes)
                        
                        # 3. Botón nativo de Streamlit para descargar el ZIP a la PC
                        st.download_button(
                            label=f"📦 Descargar Expediente {exp_busqueda.strip()} Completo (.ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name=f"Expediente_{exp_busqueda.strip()}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                else:
                    st.info("No se encontraron documentos en esta carpeta o el expediente no existe.")
            else:
                st.warning("⚠️ Por favor, ingrese un número de expediente.")

# =====================================================================
# MÓDULO 4: PLANTILLAS Y LEY 108-05
# =====================================================================
def vista_plantillas():
    st.title("📄 Generador de Plantillas Automatizado")
    st.markdown("### *AboAgrim Pro: Documentación Dinámica*")


# =====================================================================
# MÓDULO 5: ALERTAS Y PLAZOS
# =====================================================================
from datetime import datetime, timedelta

def vista_alertas_plazos():
    st.title("⚖️ Centro de Mando Normativo (JI)")
    st.subheader("Control Integral de Plazos | AboAgrim Pro")
    st.write("---")

    try:
        res = supabase.table("expedientes_maestros").select("expediente, nombre_propietario, tipo_acto, f_audiencia, fecha_creacion, jurisdiccion").execute()
        
        if not res.data:
            st.success("✨ El radar está despejado. No hay expedientes activos para monitorear en este momento.")
            return

        hoy = datetime.now().date()
        
        # --- 1. DASHBOARD DE MÉTRICAS (LO NUEVO Y MODERNO) ---
        total_casos = len(res.data)
        alertas_rojas = 0
        
        # Cálculo rápido de urgencias para el Dashboard
        for c in res.data:
            if c.get('f_audiencia'):
                f_aud = datetime.strptime(c['f_audiencia'], '%Y-%m-%d').date()
                if (f_aud - hoy).days <= 7: alertas_rojas += 1
            if c.get('fecha_creacion'):
                f_ini = datetime.strptime(c['fecha_creacion'][:10], '%Y-%m-%d').date()
                if (f_ini + timedelta(days=60) - hoy).days <= 15: alertas_rojas += 1

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(label="Expedientes en Radar", value=total_casos, delta="Activos", delta_color="normal")
        with col_m2:
            st.metric(label="Alertas Críticas", value=alertas_rojas, delta="- Requieren Atención" if alertas_rojas > 0 else "Todo en orden", delta_color="inverse" if alertas_rojas > 0 else "normal")
        with col_m3:
            st.metric(label="Normativa Activa", value="Ley 108-05", delta="Reglamentos Vigentes")

        st.write("---")
        
        # --- 2. PESTAÑAS REDISEÑADAS ---
        tab_tecnico, tab_judicial, tab_admin = st.tabs([
            "🛠️ Área Técnica (Mensuras)", 
            "⚖️ Área Judicial (Tribunales)", 
            "📝 Área Administrativa (Registro)"
        ])

        with tab_tecnico:
            st.markdown("### 📐 Vigencia de Autorizaciones")
            st.caption("Barra de estado para el plazo fatal de 60 días (Reglamento General de Mensuras).")
            
            casos_tecnicos = 0
            for caso in res.data:
                if caso.get('fecha_creacion'):
                    casos_tecnicos += 1
                    f_ini = datetime.strptime(caso['fecha_creacion'][:10], '%Y-%m-%d').date()
                    vencimiento_aut = f_ini + timedelta(days=60)
                    dias_restantes = (vencimiento_aut - hoy).days
                    
                    # Cálculo para la barra de progreso (0 a 100)
                    progreso = max(0, min(100, int((dias_restantes / 60) * 100)))
                    
                    with st.expander(f"📌 Expediente: {caso['expediente']} | Cliente: {caso['nombre_propietario']}", expanded=(dias_restantes <= 15)):
                        st.markdown(f"**Fecha de Inicio:** {f_ini.strftime('%d/%m/%Y')} ➔ **Vence:** {vencimiento_aut.strftime('%d/%m/%Y')}")
                        
                        if dias_restantes < 0:
                            st.error(f"❌ Autorización Vencida hace {abs(dias_restantes)} días.")
                            st.progress(0)
                        elif dias_restantes <= 15:
                            st.error(f"🔴 CRÍTICO: Quedan {dias_restantes} días para depositar.")
                            st.progress(progreso)
                        else:
                            st.success(f"🟢 Plazo holgado. Quedan {dias_restantes} días.")
                            st.progress(progreso)
                            
            if casos_tecnicos == 0:
                st.info("No hay fechas de creación registradas para calcular plazos técnicos.")

        with tab_judicial:
            st.markdown("### 🏛️ Calendario de Audiencias")
            
            for caso in res.data:
                if caso.get('f_audiencia'):
                    f_aud = datetime.strptime(caso['f_audiencia'], '%Y-%m-%d').date()
                    dias_aud = (f_aud - hoy).days
                    
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        c1.markdown(f"**⚖️ {caso.get('jurisdiccion', 'Jurisdicción Inmobiliaria')}**")
                        c1.write(f"**Exp:** {caso['expediente']} | **Propietario:** {caso['nombre_propietario']}")
                        
                        if dias_aud < 0:
                            c2.error(f"Pasada hace {abs(dias_aud)} días")
                        elif dias_aud == 0:
                            c2.error("🚨 AUDIENCIA HOY")
                        elif dias_aud <= 7:
                            c2.warning(f"En {dias_aud} días")
                        else:
                            c2.success(f"Próxima en {dias_aud} días")
                            
            st.info("💡 **Recordatorio de Apelación:** 30 días a partir de la notificación de la sentencia en Jurisdicción Original.")

        with tab_admin:
            st.markdown("### 📜 Recursos y Registro de Títulos")
            st.caption("Plazos legales estandarizados para consulta rápida.")
            
            c_adm1, c_adm2 = st.columns(2)
            with c_adm1:
                with st.container(border=True):
                    st.markdown("#### ⏳ Reconsideración")
                    st.write("**Plazo:** 15 días hábiles.")
                    st.caption("Se interpone ante el mismo órgano que dictó el acto objetado.")
            with c_adm2:
                with st.container(border=True):
                    st.markdown("#### ⚖️ Recurso Jerárquico")
                    st.write("**Plazo:** 30 días.")
                    st.caption("A partir de la respuesta del recurso de reconsideración.")
                    
            with st.container(border=True):
                st.markdown("#### 📄 Certificaciones")
                st.write("• **Estado Jurídico / Cargas y Gravámenes:** Vigencia de 30 días desde su emisión.")

    except Exception as e:
        st.error(f"Error de conexión con el radar: {e}")
            

from fpdf import FPDF
import io
from datetime import datetime

def vista_facturacion():
    st.title("💵 Facturación y Alertas de Cobro")
    st.subheader("Control de Honorarios | AboAgrim Pro")
    st.divider()

    tab_nueva, tab_alertas = st.tabs(["📄 Emitir Factura", "🚨 Alertas de Cobro"])

    with tab_nueva:
        try:
            res_exp = supabase.table("expedientes_maestros").select("expediente, nombre_propietario").execute()
            dict_exp = {f"{e['expediente']} - {e['nombre_propietario']}": e for e in res_exp.data} if res_exp.data else {}
            
            exp_sel = st.selectbox("Vincular a Expediente:", ["Seleccione..."] + list(dict_exp.keys()))
            if exp_sel == "Seleccione...": 
                st.info("Seleccione un expediente para comenzar.")
                return
            
            codigo_vincular = exp_sel.split(" - ")[0]
            nombre_cli = exp_sel.split(" - ")[1]
            fecha_f = st.date_input("Fecha de Emisión", datetime.now())
            
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            return

        st.write("---")
        
        # --- GESTIÓN DE ITEMS ---
        if "items_factura" not in st.session_state: st.session_state.items_factura = []

        with st.container(border=True):
            c_i1, c_i2, c_i3 = st.columns([3, 1, 1])
            desc_s = c_i1.text_input("Descripción:")
            monto_s = c_i2.number_input("Costo (RD$):", min_value=0.0, step=500.0)
            if c_i3.button("➕ Añadir", use_container_width=True):
                if desc_s and monto_s > 0:
                    st.session_state.items_factura.append({"desc": desc_s, "monto": monto_s})
                    st.rerun()

        subtotal = sum(item['monto'] for item in st.session_state.items_factura)
        
        if st.session_state.items_factura:
            for i, item in enumerate(st.session_state.items_factura):
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(f"• {item['desc']}")
                col2.write(f"RD$ {item['monto']:,.2f}")
                if col3.button("🗑️", key=f"del_{i}"):
                    st.session_state.items_factura.pop(i)
                    st.rerun()

            st.write("---")
            
            # --- INTERRUPTOR DE ITBIS (LO QUE USTED SOLICITÓ) ---
            col_opt1, col_opt2 = st.columns([2, 1])
            with col_opt1:
                con_itbis = st.toggle("Deslice para Aplicar ITBIS (18%)", value=True)
            
            itbis = (subtotal * 0.18) if con_itbis else 0.0
            total_f = subtotal + itbis

            cr1, cr2, cr3 = st.columns(3)
            cr1.metric("Sub-Total", f"RD$ {subtotal:,.2f}")
            cr2.metric("ITBIS", f"RD$ {itbis:,.2f}" if con_itbis else "EXENTO")
            cr3.metric("TOTAL", f"RD$ {total_f:,.2f}")

            # --- GUARDADO ---
            if st.button("💾 Emitir, Guardar y Descargar PDF", type="primary", use_container_width=True):
                try:
                    # Usamos 'codigo_expediente' para evitar el error de columna
                    datos_f = {
                        "codigo_expediente": codigo_vincular, 
                        "monto_total": total_f,
                        "estado": "Pendiente",
                        "fecha_emision": str(fecha_f)
                    }
                    supabase.table("facturas").insert(datos_f).execute()
                    st.success("✅ Guardado exitosamente en la base de datos.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error técnico al guardar: {e}")

    with tab_alertas:
        st.markdown("### ⚠️ Facturas Pendientes de Cobro")
        try:
            res = supabase.table("facturas").select("*").eq("estado", "Pendiente").execute()
            if res.data:
                for f in res.data:
                    # Protección contra fechas vacías
                    f_str = f.get('fecha_emision')
                    dias_txt = "Fecha no registrada"
                    if f_str:
                        f_emision = datetime.strptime(f_str, '%Y-%m-%d').date()
                        dias = (datetime.now().date() - f_emision).days
                        dias_txt = f"Emitida hace {dias} días"
                    
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.error(f"🔴 **Caso: {f.get('codigo_expediente', 'N/A')}**")
                        c1.caption(dias_txt)
                        c2.write(f"**RD$ {f.get('monto_total', 0):,.2f}**")
                        if c3.button("💰 Cobrado", key=f"p_{f['id']}"):
                            supabase.table("facturas").update({"estado": "Pagado"}).eq("id", f['id']).execute()
                            st.rerun()
            else:
                st.success("✅ Cartera al día.")
        except Exception as e:
            st.error(f"Error al cargar alertas: {e}")
# =====================================================================
# MÓDULO 6: FACTURACIÓN
# =====================================================================
from fpdf import FPDF
import io
from datetime import datetime

from fpdf import FPDF
import io
from datetime import datetime

def vista_configuracion():
    st.title("⚙️ Configuración y Alta Gerencia")
    st.subheader("Control de Accesos e Identidad | AboAgrim Pro")
    st.divider()

    if st.session_state.get("admin_autenticado", False):
        tab_accesos, tab_membrete, tab_sistema = st.tabs(["👥 Gestión de Accesos", "🎨 Identidad Visual", "💻 Sistema"])

        # --- 1. GESTIÓN DE ACCESOS (AÑADIR/BORRAR) ---
        with tab_accesos:
            st.markdown("### 👥 Control de Personal")
            
            # Formulario para nuevo acceso
            with st.expander("➕ Registrar Nuevo Miembro del Equipo", expanded=False):
                c1, c2, c3 = st.columns(3)
                nuevo_u = c1.text_input("Usuario:")
                nuevo_p = c2.text_input("PIN (4 dígitos):", type="password", max_chars=4)
                nuevo_r = c3.selectbox("Rol:", ["Abogado", "Agrimensor", "Pasante"])
                
                if st.button("Guardar Nuevo Acceso", type="primary"):
                    if nuevo_u and nuevo_p:
                        try:
                            supabase.table("usuarios").insert({
                                "nombre_usuario": nuevo_u, 
                                "pin_acceso": nuevo_p, 
                                "rol": nuevo_r
                            }).execute()
                            st.success(f"✅ {nuevo_u} ha sido autorizado como {nuevo_r}.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: El usuario ya existe o hubo un fallo en la nube.")

            st.write("---")
            st.markdown("#### Usuarios con Acceso Actual")
            try:
                res_u = supabase.table("usuarios").select("*").execute()
                for user in res_u.data:
                    col_user, col_rol, col_btn = st.columns([2, 2, 1])
                    col_user.write(f"👤 **{user['nombre_usuario']}**")
                    col_rol.caption(f"Rango: {user['rol']}")
                    # Evitar que el Presidente se borre a sí mismo por error
                    if user['nombre_usuario'] != "JhonnyMatos":
                        if col_btn.button("Eliminar", key=f"del_{user['id']}", type="secondary"):
                            supabase.table("usuarios").delete().eq("id", user['id']).execute()
                            st.rerun()
            except:
                st.info("No hay usuarios adicionales registrados.")

        # --- 2. IDENTIDAD VISUAL (LETRAS, COLORES, FONDOS) ---
        with tab_membrete:
            st.markdown("### 🎨 Personalización de Membretes e Interfaz")
            st.caption("Ajuste los colores y tipografías que el sistema usará en PDF y pantallas.")
            
            try:
                # Recuperar ajustes actuales
                conf_res = supabase.table("configuracion_visual").select("*").eq("id", 1).single().execute()
                c_act = conf_res.data

                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    new_color_p = st.color_picker("Color Primario (Azul AboAgrim)", c_act['color_primario'])
                    new_color_s = st.color_picker("Color Secundario (Oro/Detalles)", c_act['color_secundario'])
                with col_p2:
                    new_font = st.selectbox("Fuente Institucional:", 
                                         ["Arial", "Helvetica", "Times New Roman", "Courier", "Verdana"],
                                         index=["Arial", "Helvetica", "Times New Roman", "Courier", "Verdana"].index(c_act['fuente_familia']))
                    new_bg = st.color_picker("Fondo de Encabezados PDF:", c_act['fondo_cabecera'])

                if st.button("💾 Aplicar Identidad Visual", use_container_width=True, type="primary"):
                    supabase.table("configuracion_visual").update({
                        "color_primario": new_color_p,
                        "color_secundario": new_color_s,
                        "fuente_familia": new_font,
                        "fondo_cabecera": new_bg
                    }).eq("id", 1).execute()
                    st.success("🎨 Identidad corporativa actualizada. Los nuevos PDF usarán este estilo.")
                    st.balloons()
            except:
                st.error("Configure la tabla 'configuracion_visual' en Supabase para usar esta función.")

        # --- 3. SISTEMA ---
        with tab_sistema:
            st.markdown("### 🚪 Salida Segura")
            if st.button("Bloquear Centro de Mando", use_container_width=True):
                st.session_state.admin_autenticado = False
                st.session_state.rol = "Pasante"
                st.rerun()

    else:
        # Pantalla de acceso original con validación dinámica contra la tabla usuarios
        st.markdown("### 🔒 Validación de Identidad Administrativa")
        with st.container(border=True):
            u_pres = st.text_input("Usuario Master:")
            p_pres = st.text_input("PIN:", type="password")
            if st.button("Entrar", use_container_width=True, type="primary"):
                res_val = supabase.table("usuarios").select("*").eq("nombre_usuario", u_pres).eq("pin_acceso", p_pres).execute()
                if res_val.data:
                    st.session_state.admin_autenticado = True
                    st.session_state.usuario = u_pres
                    st.session_state.rol = res_val.data[0]['rol']
                    st.rerun()
                else:
                    st.error("Credenciales no autorizadas.")
            # Nota: Esto se complementa con CSS personalizado en el inicio del script
        # Aquí va la función de agregar/borrar usuarios...
def login_sistema():
    st.markdown("""
        <style>
        .login-box {
            background-color: #f0f2f6;
            padding: 30px;
            border-radius: 15px;
            border: 2px solid #1E3A8A;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.image("https://vuestra-url-logo.com/logo.png", width=200) # Si tiene logo
        st.header("🔐 Acceso AboAgrim Pro")
        
        u_ingreso = st.text_input("Nombre de Usuario:")
        p_ingreso = st.text_input("PIN de Seguridad:", type="password", max_chars=4)
        
        if st.button("Ingresar al Sistema", use_container_width=True):
            # Buscamos en la tabla de usuarios que ya creamos en Supabase
            res = supabase.table("usuarios_sistema").select("*").eq("nombre_usuario", u_ingreso).eq("pin_acceso", p_ingreso).eq("estado", "Activo").execute()
            
            if res.data:
                st.session_state.autenticado_global = True
                st.session_state.usuario_actual = u_ingreso
                st.success(f"Bienvenido, {u_ingreso}")
                st.rerun()
            else:
                st.error("Usuario o PIN incorrectos, o cuenta inactiva.")
def vista_documentos():
    st.header("📄 Generador de Documentos y Actas")
    st.info("Seleccione un expediente y una plantilla para generar el documento automáticamente.")

    # 1. Buscamos los expedientes activos para rellenar datos
    try:
        res_exp = supabase.table("agenda_mensuras").select("expediente, cliente, notas").execute()
        expedientes = [e['expediente'] for e in res_exp.data] if res_exp.data else []
    except:
        expedientes = []

    if not expedientes:
        st.warning("No hay expedientes registrados para generar documentos.")
        return

    col1, col2 = st.columns(2)
    with col1:
        exp_sel = st.selectbox("Seleccione el Expediente:", expedientes)
        tipo_doc = st.selectbox("Tipo de Documento:", [
            "Acta de Hito y Colindancia", 
            "Contrato de Cuota Litis", 
            "Instancia de Solicitud de Mensura"
        ])
    
    # 2. Buscamos los datos específicos del cliente seleccionado
    datos_cliente = next((item for item in res_exp.data if item["expediente"] == exp_sel), None)

    if datos_cliente:
        st.subheader("📝 Editor de Documento")
        
        # Plantilla básica
        cuerpo = f"""ACTA DE HITO Y COLINDANCIA
            
En el municipio de Santiago de los Caballeros, República Dominicana.
En relación al expediente No. {datos_cliente['expediente']}, propiedad de {datos_cliente['cliente']}.

Por medio de la presente, AboAgrim, representada por el Lic. Jhonny Matos, M.A., hace constar que..."""
        
        texto_final = st.text_area("Contenido del Documento:", cuerpo, height=350)

# --- BLOQUE DE BOTONES FINAL (Péguelo aquí) ---
        st.markdown("---")
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            # Este botón descarga el acta a su computadora
            st.download_button(
                label="💾 Descargar Acta (.txt)",
                data=texto_final,
                file_name=f"Acta_{exp_sel}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        with col_btn2:
            # Este botón abre el panel de impresión profesional
            if st.button("🖨️ IMPRIMIR DOCUMENTO", use_container_width=True):
                doc_html = f"""
                <div style="font-family: 'Times New Roman', serif; padding: 50px; line-height: 1.6; background-color: white; color: black;">
                    <h2 style="text-align: center; color: #1E3A8A;">ABOAGRIM</h2>
                    <p style="text-align: center; font-weight: bold;">SERVICIOS LEGALES Y CATASTRALES</p>
                    <p style="text-align: center; font-size: 12px;">Lic. Jhonny Matos, M.A. | Santiago, R.D.</p>
                    <hr style="border: 1px solid black;">
                    <div style="white-space: pre-wrap; margin-top: 30px; font-size: 15px; text-align: justify;">{texto_final}</div>
                </div>
                <script>setTimeout(function(){{ window.print(); }}, 500);</script>
                """
                st.components.v1.html(doc_html, height=600, scrolling=True)
def vista_archivo_digital():
    st.title("📂 Archivo Digital Centralizado")
    st.subheader("Gestión Documental | AboAgrim Pro")
    st.divider()

    tab_explorar, tab_subir = st.tabs(["🔍 Explorar Expedientes", "📤 Vincular Nuevo Documento"])

    # --- 1. EXPLORAR ARCHIVOS ---
    with tab_explorar:
        st.markdown("### 🗄️ Bóveda de Documentos")
        
        # Selector de expediente para filtrar
        try:
            res_exp = supabase.table("expedientes_maestros").select("expediente, nombre_propietario").execute()
            list_exp = [f"{e['expediente']} - {e['nombre_propietario']}" for e in res_exp.data] if res_exp.data else []
            
            exp_busqueda = st.selectbox("Filtrar por Expediente:", ["Todos"] + list_exp)
            st.write("---")

            query = supabase.table("archivo_digital").select("*")
            if exp_busqueda != "Todos":
                query = query.eq("codigo_expediente", exp_busqueda.split(" - ")[0])
            
            documentos = query.execute()

            if documentos.data:
                for doc in documentos.data:
                    with st.container(border=True):
                        col_icon, col_info, col_btn = st.columns([1, 4, 2])
                        col_icon.markdown("### 📄")
                        col_info.markdown(f"**{doc['nombre_documento']}**")
                        col_info.caption(f"Categoría: {doc['categoria']} | Exp: {doc['codigo_expediente']}")
                        
                        # Botón para abrir el archivo (redirige al link de Drive o Nube)
                        col_btn.link_button("👁️ Ver Documento", doc['url_enlace'], use_container_width=True)
                        if col_btn.button("🗑️ Eliminar", key=f"del_doc_{doc['id']}", use_container_width=True):
                            supabase.table("archivo_digital").delete().eq("id", doc['id']).execute()
                            st.rerun()
            else:
                st.info("No se han encontrado documentos vinculados a este criterio.")

        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")

    # --- 2. VINCULAR NUEVOS DOCUMENTOS ---
    with tab_subir:
        st.markdown("### 📤 Registro de Nueva Documentación")
        st.write("Vincule archivos alojados en su Google Drive o servidor al expediente correspondiente.")
        
        with st.container(border=True):
            exp_vincular = st.selectbox("Seleccionar Expediente destino:", list_exp if list_exp else ["Sin expedientes"])
            nombre_doc = st.text_input("Nombre del Documento:", placeholder="Ej: Plano de Mensura Aprobado")
            
            c1, c2 = st.columns(2)
            cat_doc = c1.selectbox("Categoría Legal/Técnica:", ["Plano de Mensura", "Sentencia Judicial", "Acto de Alguacil", "Contrato de Cuota Litis", "Certificación IPI", "Otro"])
            url_doc = c2.text_input("Enlace del Archivo (URL):", placeholder="Pegue el link de Google Drive aquí")

            if st.button("🚀 Registrar en Archivo Digital", type="primary", use_container_width=True):
                if nombre_doc and url_doc and exp_vincular != "Sin expedientes":
                    try:
                        nuevo_registro = {
                            "codigo_expediente": exp_vincular.split(" - ")[0],
                            "nombre_documento": nombre_doc,
                            "categoria": cat_doc,
                            "url_enlace": url_doc
                        }
                        supabase.table("archivo_digital").insert(nuevo_registro).execute()
                        st.success("✅ Documento vinculado exitosamente.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error al registrar: {e}")
                else:
                    st.warning("Por favor, complete todos los campos obligatorios.")
        
        
import io
from docxtpl import DocxTemplate

import io
from docxtpl import DocxTemplate
from datetime import datetime

# ==========================================
# 📄 MÓDULO DE PLANTILLAS AUTOMÁTICAS
# ==========================================
def vista_plantillas_auto():
    st.title("📄 Generador Automático de Documentos")
    st.subheader("Redacción Asistida | AboAgrim Pro")
    st.divider()

    try:
        res = supabase.table("expedientes_maestros").select("*").execute()
        if not res.data:
            st.warning("⚠️ No hay expedientes en el Registro Maestro.")
            return

        dict_exp = {f"EXP: {e['expediente']} - {e['nombre_propietario']}": e for e in res.data}
        seleccion = st.selectbox("🔍 Seleccione el expediente:", ["Seleccione..."] + list(dict_exp.keys()))
        
        if seleccion != "Seleccione...":
            caso = dict_exp[seleccion]
            tipo_doc = st.selectbox("📝 Tipo de Documento:", [
                "Instancia de Solicitud de Mensura",
                "Contrato de Cuota Litis",
                "Acto de Alguacil"
            ])

            if st.button("🚀 Generar y Descargar Word", type="primary", use_container_width=True):
                with st.spinner("Vinculando datos..."):
                    try:
                        mapa = {
                            "Instancia de Solicitud de Mensura": "plantilla_mensura.docx",
                            "Contrato de Cuota Litis": "plantilla_cuota_litis.docx",
                            "Acto de Alguacil": "plantilla_alguacil.docx"
                        }
                        nombre_base = mapa.get(tipo_doc)
                        doc = DocxTemplate(nombre_base)
                        
                        contexto = {
                            'nombre_cliente': caso.get('nombre_propietario', '__________'),
                            'cedula_cliente': caso.get('cedula', '__________'),
                            'parcela': caso.get('parcela', '__________'),
                            'dc': caso.get('dc', '__________'),
                            'fecha_hoy': datetime.now().strftime("%d de %B del %Y")
                        }
                        
                        doc.render(contexto)
                        buffer = io.BytesIO()
                        doc.save(buffer)
                        buffer.seek(0)
                        
                        st.download_button(
                            label="📥 Descargar Documento Listo",
                            data=buffer,
                            file_name=f"{caso['expediente']}_{tipo_doc.replace(' ', '_')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    except FileNotFoundError:
                        st.error(f"❌ Falta el archivo `{nombre_base}` en GitHub.")
                    except Exception as e:
                        st.error(f"Error: {e}")
    except Exception as e:
        st.error(f"Error de conexión: {e}")

# ==========================================
# 🚦 ENRUTADOR Y MENÚ (EL GATILLO)
# ==========================================

# Definimos los módulos con los emojis exactos
modulos = [
    "🏠 Mando Central", 
    "👤 Registro Maestro", 
    "📂 Archivo Digital", 
    "📄 Plantillas Auto", 
    "📅 Alertas y Plazos"
]

if st.session_state.get("admin_autenticado", False):
    modulos.append("💵 Facturación")

if not st.session_state.get("admin_autenticado", False) or st.session_state.get("rol") == "Presidente Fundador":
    modulos.append("⚙️ Configuración")
# ... (esto es lo que ya tiene arriba)
    modulos.append("⚙️ Configuración")

# --- INSERTE ESTO AQUÍ ---
with st.sidebar:
    st.markdown(f"**Firmado como:** {st.session_state.get('usuario', 'Invitado')}")
    menu = st.radio("Ir a:", modulos)
# -------------------------

# Lógica de salto (esto es lo que ya tiene en la línea 916)
if menu == "🏠 Mando Central":

# Lógica de salto (Enrutador)
if menu == "🏠 Mando Central":
    st.info("Bienvenido al Mando Central de AboAgrim Pro")
elif menu == "👤 Registro Maestro":
    vista_registro_maestro()
elif menu == "📂 Archivo Digital":
    vista_archivo_digital()
elif menu == "📄 Plantillas Auto":
    vista_plantillas_auto() # <--- ¡Aquí es donde se activa!
elif menu == "📅 Alertas y Plazos":
    vista_alertas_plazos()
elif menu == "💵 Facturación":
    vista_facturacion()
elif menu == "⚙️ Configuración":
    vista_configuracion()
# Aquí sigue def generar_documento_word(nombre_plantilla, diccionario_datos):

# Aquí sigue def generar_documento_word(nombre_plantilla, diccionario_datos):
# Aquí debajo empieza su def generar_documento_word...

def generar_documento_word(nombre_plantilla, diccionario_datos):
    """
    Toma una plantilla de la carpeta 'plantillas_maestras' y la llena con los datos.
    Devuelve un objeto de memoria (BytesIO) listo para descargar o subir a Drive.
    """
    # 1. Ruta exacta de tu plantilla
    ruta_plantilla = f"plantillas_maestras/{nombre_plantilla}"
    
    try:
        # 2. Cargar el documento con docxtpl
        doc = DocxTemplate(ruta_plantilla)
        
        # 3. Inyectar el diccionario de variables (El que viene de Supabase o session_state)
        doc.render(diccionario_datos)
        
        # 4. Guardar en memoria (sin crear archivos basura en tu disco duro)
        archivo_salida = io.BytesIO()
        doc.save(archivo_salida)
        archivo_salida.seek(0)
        
        return archivo_salida
    except Exception as e:
        st.error(f"Error al generar {nombre_plantilla}: {e}")
        return None
def guardar_y_actualizar(tipo_perfil, datos, ventana_origen, menu_desplegable=None):
    """Guarda en la base de datos y refresca el menú desplegable."""
    
    # 1. Lógica de inserción (Ejemplo SQL)
    # query = f"INSERT INTO {tipo_perfil} (nombre, cedula, profesion, ...) VALUES (...)"
    # ejecutar_query(query)
    
    print(f"Datos guardados en la nube para {tipo_perfil}: {datos}")
    
    # 2. Refrescar el Menú Desplegable si existe
    if menu_desplegable:
    
        nueva_lista = ["Seleccione..."] + ["Juan Pérez", "Lic. Matos", "Nuevo Registro..."] # Ejemplo
        menu_desplegable.configure(values=nueva_lista)
        menu_desplegable.set(datos["Nombre Completo"]) # Selecciona el recién creado

def ventana_registro_profesional(tipo, menu_a_refrescar=None):
    ventana = ctk.CTkToplevel()
    ventana.title(f"AboAgrim Pro - Registro de {tipo}")
    ventana.geometry("450x650")
    ventana.attributes('-topmost', True)

    # Contenedor con scroll para que sea moderno si hay muchos campos
    scroll_frame = ctk.CTkScrollableFrame(ventana, width=400, height=450)
    scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

    campos = ["Nombre Completo", "Cédula / RNC", "Dirección", "Teléfono", "Correo", "Profesión"]
    entradas = {}

    for campo in campos:
        ctk.CTkLabel(scroll_frame, text=campo, font=("Roboto", 12, "bold")).pack(anchor="w", padx=10)
        entry = ctk.CTkEntry(scroll_frame, placeholder_text=f"Escriba {campo.lower()}...", width=320)
        entry.pack(pady=(0, 15), padx=10)
        entradas[campo] = entry

    # Botón dinámico
    btn_guardar = ctk.CTkButton(
        ventana, 
        text=f"CONFIRMAR REGISTRO", 
        fg_color="#1a5276", # Azul profesional
        hover_color="#21618c",
        height=45,
        command=lambda: guardar_y_actualizar(
            tipo, 
            {k: v.get() for k, v in entradas.items()}, 
            ventana, 
            menu_a_refrescar
        )
    )
    btn_guardar.pack(pady=20)


# =======================================================
# 1. DISEÑO DE LA PANTALLA DE PLANTILLAS
# =======================================================

def crear_carpeta_expediente(nombre_cliente, id_expediente):
    # 1. Definimos el nombre de la carpeta principal
    nombre_carpeta = f"EXP_{id_expediente}_{nombre_cliente}"
    
    # 2. Lógica para crear carpeta en Google Drive (usando service account o OAuth)
    # (Aquí va la conexión técnica con Google)
    folder_metadata = {
        'name': nombre_carpeta,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': ['ID_DE_SU_CARPETA_MAESTRA_ABOAGRIM'] # Su carpeta raíz
    }
    
    # El sistema crea la carpeta y nos devuelve un Link
    # drive_service.files().create(body=folder_metadata).execute()
    
    link_drive = f"https://drive.google.com/drive/folders/ID_GENERADO"
    return link_drive
import googleapiclient.discovery
def vista_mando_central():
    st.title("🏠 Mando Central | AboAgrim Pro")
    st.markdown("**Bienvenido al panel de control principal, Lic. Jhonny Matos.**")
    st.divider()

    # --- 1. MÉTRICAS PRINCIPALES (KPIs) ---
    st.subheader("📊 Resumen de Operaciones")
    m1, m2, m3, m4 = st.columns(4)
    
    # Intentamos obtener el total real de expedientes desde Supabase
    total_expedientes = 0
    try:
        res = supabase.table("expedientes_maestros").select("id", count="exact").execute()
        total_expedientes = res.count if res.count else 0
    except Exception:
        pass

    with m1:
        st.metric(label="Expedientes Totales", value=total_expedientes, delta="Registrados")
    with m2:
        st.metric(label="Mensuras Catastrales", value="Activas") 
    with m3:
        st.metric(label="Registro de Títulos", value="Activos")
    with m4:
        st.metric(label="Tribunales de Tierras", value="En Litigio")

    st.write("---")

    # --- 2. ACCESOS RÁPIDOS Y ÚLTIMOS REGISTROS ---
    c_izq, c_der = st.columns([2, 1])
    
    with c_izq:
        st.subheader("🕒 Últimos Expedientes Registrados")
        try:
            # Pedimos solo 'id' y 'nombre_propietario' para asegurar compatibilidad
            res_ultimos = supabase.table("expedientes_maestros").select("id, nombre_propietario").order("id", desc=True).limit(5).execute()
            
            if res_ultimos.data:
                # Mostramos una tabla profesional y limpia
                st.dataframe(
                    res_ultimos.data, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "id": "ID del Expediente",
                        "nombre_propietario": "Cliente / Razón Social"
                    }
                )
            else:
                st.info("Aún no hay expedientes registrados en el sistema.")
        except Exception as e:
            # Si hay un error, ahora lo veremos en rojo para saber qué es
            st.error(f"Error al leer la base de datos: {e}")

    with c_der:
        st.subheader("⚡ Estado del Sistema")
        st.success("🟢 Conexión a Servidor: Óptima")
        st.success("🟢 Motor de Plantillas: Activo")
        st.success("🟢 Base de Datos: Sincronizada")
        st.write("")
        st.info("📌 Recuerde: Mantener su Archivo Digital actualizado garantiza la agilidad de los procesos en la Jurisdicción Inmobiliaria de Santiago y el resto del país.")
def vista_registro_maestro():
    st.title("👤 Registro Maestro de Expedientes")
    st.subheader("Control de Casos Legales y Técnicos | AboAgrim")
    st.divider()

    # --- 1. DATOS GENERALES DEL CLIENTE ---
    with st.expander("📝 Información Básica del Propietario/Cliente", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre_cliente = st.text_input("Nombre Completo / Razón Social:")
            identificacion = st.text_input("Cédula o RNC:", placeholder="001-0000000-0")
        with col2:
            telefono = st.text_input("Teléfono de Contacto:")
            domicilio = st.text_area("Dirección / Domicilio:", height=68)

    # --- 2. DEPARTAMENTO DE AGRIMENSURA (DATOS TÉCNICOS) ---
    st.markdown("### 🗺️ Módulo de Agrimensura y Catastro")
    with st.container(border=True):
        at1, at2, at3 = st.columns(3)
        with at1:
            parcela = st.text_input("Número de Parcela:", placeholder="Ej: 209-B")
            distrito = st.text_input("Distrito Catastral:")
        with at2:
            municipio = st.text_input("Municipio:", value="Santiago")
            provincia = st.text_input("Provincia:", value="Santiago")
        with at3:
            superficie = st.text_input("Superficie (m²):")
            estatus_t = st.selectbox("Estatus Técnico:", ["Saneamiento", "Deslinde", "Subdivisión", "Refundición"])

        # CAMPOS DE COORDENADAS (LO QUE SE HABÍA BORRADO)
        st.write("**📍 Ubicación Georreferenciada (UTM/WGS84)**")
        c_coord1, c_coord2, c_coord3 = st.columns(3)
        with c_coord1:
            coord_east = st.text_input("Coordenada Este (X):")
        with c_coord2:
            coord_north = st.text_input("Coordenada Norte (Y):")
        with c_coord3:
            puntos_gps = st.text_input("Puntos de Control / Vértices:")

    # --- 3. DEPARTAMENTO LEGAL (LITIS Y TRIBUNALES) ---
    st.markdown("### ⚖️ Módulo Jurídico y Litigios")
    with st.container(border=True):
        jurisdiccion = st.selectbox("Jurisdicción:", ["Inmobiliaria", "Civil y Comercial", "Laboral", "Penal"])
        
        jl1, jl2 = st.columns(2)
        with jl1:
            tribunal = st.text_input("Tribunal / Corte:", placeholder="Ej: Tribunal de Tierras de Jurisdicción Original")
            sala = st.text_input("Sala / Cámara:")
            juez = st.text_input("Magistrado / Juez Apoderado:")
        with jl2:
            no_rol = st.text_input("Número de Rol / Cuaderno:")
            f_audiencia = st.date_input("Fecha de Próxima Audiencia")
            etapa_procesal = st.selectbox("Etapa del Proceso:", ["Inicio", "Instrucción", "Fallo Pendiente", "Sentencia", "Recurso"])

    # --- 4. ACCIÓN DE GUARDADO ---
    st.divider()
    if st.button("🚀 REGISTRAR EXPEDIENTE MAESTRO", type="primary", use_container_width=True):
        if nombre_cliente and parcela:
            # Generamos código único
            codigo_generado = f"AA-{datetime.now().strftime('%y%m%d%H%M')}"
            
            data_insert = {
                "expediente": codigo_generado,
                "nombre_propietario": nombre_cliente,
                "cedula_propietario": identificacion,
                "parcela": parcela,
                "municipio": municipio,
                "provincia": provincia,
                "estatus": estatus_t,
                "jurisdiccion": jurisdiccion,
                "fecha_creacion": str(datetime.now())
            }
            
            try:
                supabase.table("expedientes_maestros").insert(data_insert).execute()
                st.success(f"✅ Expediente {codigo_generado} creado exitosamente para {nombre_cliente}.")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar en la nube: {e}")
        else:
            st.warning("⚠️ El nombre del cliente y el número de parcela son obligatorios.")
# =========================================================
# ENRUTADOR SEGURO - RECUPERACIÓN DE MANDO
# =========================================================

# Recuperamos datos de sesión
usuario_actual = st.session_state.get("usuario", "")
admin_activo = st.session_state.get("admin_autenticado", False)

# RESCATE AUTOMÁTICO: Si es usted, el sistema le otorga su rango de inmediato
if usuario_actual == "JhonnyMatos":
    st.session_state["rol"] = "Presidente Fundador"

rol_usuario = st.session_state.get("rol", "Pasante")

# --- MÓDULOS DEL SISTEMA ---
modulos = [
    "🏠 Mando Central", 
    "👤 Registro Maestro", 
    "📂 Archivo Digital", 
    "📄 Plantillas Auto", 
    "📅 Alertas y Plazos"
]

# Filtro de jerarquía para módulos financieros
if rol_usuario in ["Abogado", "Agrimensor", "Presidente Fundador"]:
    modulos.append("💵 Facturación")

# La configuración siempre visible para loguearse, o si es el presdente
if rol_usuario == "Presidente Fundador" or not admin_activo:
    modulos.append("⚙️ Configuración")

# Renderizado de la barra lateral
with st.sidebar:
    st.markdown(f"**Firmado como:** {usuario_actual if usuario_actual else 'Invitado'}")
    st.caption(f"**Nivel de Acceso:** {rol_usuario}")
    menu = st.radio("Ir a:", modulos)

# ==========================================
# 🚦 ENRUTADOR PRINCIPAL DEL SISTEMA
# ==========================================

if menu == "🏠 Mando Central":
    st.info("Bienvenido al Mando Central de AboAgrim Pro")
    # Si tiene la función de mando central, quite el "#" de la línea de abajo:
    # vista_mando_central()

elif menu == "👤 Registro Maestro":
    vista_registro_maestro()

elif menu == "📂 Archivo Digital":
    vista_archivo_digital()

elif menu == "📄 Plantillas Auto":
    # Borre el st.info que había antes y deje solo esta línea:
    vista_plantillas_auto()

elif menu == "📅 Alertas y Plazos":
    vista_alertas_plazos()

elif menu == "💵 Facturación":
    vista_facturacion()

elif menu == "⚙️ Configuración":
    vista_configuracion()
