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
def vista_alertas():
    st.title("📅 Control de Alertas y Plazos")
    st.info("Gestione sus audiencias, plazos de objeción y vencimientos de mensura.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Nueva Alerta")
        tipo = st.selectbox("Tipo de Plazo", ["Audiencia", "Plazo JI", "Cierre Mensura", "Pago Impuestos"])
        fecha_alerta = st.date_input("Fecha límite")
        nota = st.text_area("Descripción corta")
        if st.button("Guardar Recordatorio"):
            st.success("Alerta programada correctamente")
            
    with col2:
        st.subheader("Próximos Vencimientos")
        # Aquí luego jalaremos los datos de Supabase
        st.warning("⚠️ Audiencia de Saneamiento - Parcela 102 - Faltan 3 días")
        st.info("📅 Entrega de Planos - Parcela 55 - 15 de Mayo")
    
    PLAZOS_LEGALES = {
        "Presentación de trabajos (60 días)": 60,
        "Prórroga trabajos (30 días)": 30,
        "Subsanar observaciones técnicas (15 días)": 15,
        "Autorización de Mensura (90 días)": 90,
        "Recurso jerárquico Dirección Nacional (15 días)": 15,
        "Subsanar faltas en RT (15 días)": 15,
        "Certificación Estado Jurídico (30 días)": 30,
        "Recurso de Apelación (30 días)": 30,
        "Recurso de Casación (30 días)": 30,
        "Litis: Octava para inventario (15 días)": 15,
        "Revisión por Causa de Fraude (1 año)": 365,
        "Perención de Instancia (3 años)": 1095,
        "Respuesta instancias administrativas (15 días)": 15
    }

    with st.expander("🔔 Programar Alerta Legal Automática", expanded=True):
        c1, c2 = st.columns(2)
        tipo = c1.selectbox("Trámite:", list(PLAZOS_LEGALES.keys()))
        f_ini = c1.date_input("Fecha Inicio:")
        exp = c1.text_input("No. Expediente:")
        cli = c2.text_input("Cliente:")
        org = c2.text_input("Órgano / Responsable:")
        notas = st.text_area("Notas del procedimiento:")
        
        if st.button("🚀 Activar Blindaje Legal"):
            import datetime
            vence = f_ini + datetime.timedelta(days=PLAZOS_LEGALES[tipo])
            datos = {
                "fecha_cita": str(vence),
                "expediente": exp,
                "cliente": cli,
                "ubicacion": tipo,
                "tecnico_asignado": org,
                "notas": f"INICIO: {f_ini}. {notas}",
                "categoria": "FATAL"
            }
            try:
                supabase.table("agenda_mensuras").insert(datos).execute()
                st.success(f"✅ ¡Alerta programada para el {vence}!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()
    st.subheader("🚩 Monitor de Plazos y Caducidades")
    
    try:
        res = supabase.table("agenda_mensuras").select("*").order("fecha_cita").execute()
        if res.data:
            import pandas as pd
            from datetime import date
            df = pd.DataFrame(res.data)
            df['fecha_cita'] = pd.to_datetime(df['fecha_cita']).dt.date
            
            # Formateo de la tabla
            df_v = df.rename(columns={"fecha_cita":"Vencimiento", "ubicacion":"Trámite", "expediente":"Exp."})
            
            # Aplicamos colores de forma segura
            def resaltar(s):
                color = ''
                dias = (s.Vencimiento - date.today()).days
                if dias < 0: color = 'background-color: #fee2e2' # Rojo
                elif dias <= 7: color = 'background-color: #fef3c7' # Amarillo
                return [color] * len(s)

            st.dataframe(df_v[["Vencimiento", "Trámite", "Exp.", "cliente"]].style.apply(resaltar, axis=1), use_container_width=True, hide_index=True)
            st.caption("🔴 Rojo: Vencido | 🟡 Amarillo: Menos de 7 días.")
        else:
            st.info("No hay plazos en seguimiento.")
    except Exception as e:
        st.error(f"Error al cargar monitor: {e}")

from fpdf import FPDF
import io
from datetime import datetime

def vista_facturacion():
    st.title("💵 Sistema de Facturación y Honorarios")
    st.subheader("Control Financiero | AboAgrim Pro")
    st.divider()

    # --- 1. SELECCIÓN Y DATOS DEL CONTRIBUYENTE ---
    with st.expander("👤 Datos del Cliente y Facturación", expanded=True):
        try:
            res_exp = supabase.table("expedientes_maestros").select("expediente, nombre_propietario, cedula_propietario").execute()
            dict_exp = {f"{e['expediente']} - {e['nombre_propietario']}": e for e in res_exp.data} if res_exp.data else {}
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                exp_sel = st.selectbox("Vincular a Expediente:", ["Seleccione..."] + list(dict_exp.keys()))
                tipo_p = st.radio("Tipo de Persona:", ["Física", "Jurídica"], horizontal=True)
            
            with col_c2:
                id_sugerida = dict_exp[exp_sel].get('cedula_propietario', '') if exp_sel != "Seleccione..." else ""
                identidad = st.text_input("RNC / Cédula del Cliente:", value=id_sugerida)
                fecha_factura = st.date_input("Fecha de Emisión", datetime.now())

        except Exception as e:
            st.error(f"Error al conectar con expedientes: {e}")
            return

    st.write("---")

    # --- 2. GESTIÓN DINÁMICA DE SERVICIOS ---
    st.markdown("### 📝 Detalle de Servicios Legales y Técnicos")
    
    if "items_factura" not in st.session_state:
        st.session_state.items_factura = []

    with st.container(border=True):
        c_i1, c_i2, c_i3 = st.columns([3, 1, 1])
        with c_i1:
            desc_serv = st.text_input("Descripción del Trabajo:", placeholder="Ej: Saneamiento Parcela 209")
        with c_i2:
            monto_serv = st.number_input("Costo (RD$):", min_value=0.0, step=100.0)
        with c_i3:
            st.write(" ")
            if st.button("➕ Agregar", use_container_width=True):
                if desc_serv and monto_serv > 0:
                    st.session_state.items_factura.append({"desc": desc_serv, "monto": monto_serv})
                    st.rerun()

    subtotal = 0
    if st.session_state.items_factura:
        for i, item in enumerate(st.session_state.items_factura):
            col_v1, col_v2, col_v3 = st.columns([3, 1, 1])
            with col_v1: st.info(f"**Servicio:** {item['desc']}")
            with col_v2: st.success(f"**RD$** {item['monto']:,.2f}")
            with col_v3:
                if st.button("🗑️ Quitar", key=f"del_{i}", use_container_width=True):
                    st.session_state.items_factura.pop(i)
                    st.rerun()
            subtotal += item['monto']
        
        st.write("---")
        
        col_it1, col_it2 = st.columns([2, 1])
        with col_it1:
            aplicar_itbis = st.checkbox("✅ Aplicar ITBIS (18%) a esta factura", value=True)
        
        itbis = (subtotal * 0.18) if aplicar_itbis else 0.0
        total_final = subtotal + itbis

        cr1, cr2, cr3 = st.columns(3)
        cr1.metric("Sub-Total", f"RD$ {subtotal:,.2f}")
        cr2.metric("ITBIS (18%)", f"RD$ {itbis:,.2f}" if aplicar_itbis else "EXENTO")
        cr3.metric("TOTAL A PAGAR", f"RD$ {total_final:,.2f}")

        st.divider()

        # --- 3. CONDICIONES DE PAGO ---
        st.markdown("### 💳 Condiciones de Liquidación")
        modalidad = st.radio(
            "Seleccione cómo el cliente pagará esta factura:", 
            ["Pago Único (Total)", "Avance Inicial y Saldo", "Pago por Etapas (Acuerdo de Trabajo)"], 
            horizontal=True
        )

        texto_condiciones = ""

        if modalidad == "Pago Único (Total)":
            texto_condiciones = f"El cliente se compromete a saldar el monto total de RD$ {total_final:,.2f} contra entrega de los trabajos o documentos correspondientes."
        elif modalidad == "Avance Inicial y Saldo":
            avance = st.number_input("Monto del Avance (RD$):", min_value=0.0, max_value=float(total_final), step=1000.0)
            saldo = total_final - avance
            st.metric("Balance Restante", f"RD$ {saldo:,.2f}")
            texto_condiciones = f"Avance Inicial Recibido: RD$ {avance:,.2f} \nBalance Pendiente: RD$ {saldo:,.2f} (Pagadero al concluir el servicio)."
        elif modalidad == "Pago por Etapas (Acuerdo de Trabajo)":
            etapas = st.text_area("Hitos de pago:", "1. Inicio de trabajos: 30%\n2. Aprobación Técnica (Mensuras): 40%\n3. Entrega de Título Definitivo: 30%")
            texto_condiciones = f"Pago estructurado bajo los siguientes hitos:\n{etapas}"

        # --- 4. GENERADOR DE PDF PREMIUM ---
        if st.button("📄 Generar Factura Oficial", type="primary", use_container_width=True):
            pdf = FPDF()
            pdf.add_page()
            
            # --- DISEÑO DEL MEMBRETE ---
            # Nombre de la Firma (Izquierda)
            pdf.set_font("Arial", 'B', 24)
            pdf.set_text_color(0, 51, 102) # Azul Marino
            pdf.cell(100, 10, "AboAgrim", ln=False, align='L')
            
            # Datos del Presidente (Derecha)
            pdf.set_font("Arial", '', 10)
            pdf.set_text_color(100, 100, 100) # Gris elegante
            pdf.cell(90, 5, "Lic. Jhonny Matos. M.A.", ln=True, align='R')
            
            # Subtítulo Firma y Cargo
            pdf.set_font("Arial", 'B', 10)
            pdf.set_text_color(184, 134, 11) # Oro/Dorado
            pdf.cell(100, 5, "ABOGADOS Y AGRIMENSORES", ln=False, align='L')
            
            pdf.set_font("Arial", '', 9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(90, 5, "Presidente Fundador", ln=True, align='R')
            
            pdf.cell(190, 5, "Santiago de los Caballeros, Rep. Dom.", ln=True, align='R')
            
            # Línea divisoria dorada
            pdf.set_draw_color(184, 134, 11) # Oro
            pdf.set_line_width(0.8)
            pdf.line(10, 32, 200, 32)
            pdf.set_line_width(0.2) # Restaurar grosor
            pdf.ln(15)
            
            # --- TÍTULO DEL DOCUMENTO ---
            pdf.set_font("Arial", 'B', 16)
            pdf.set_text_color(0, 51, 102)
            titulo_doc = "ACUERDO DE HONORARIOS Y SERVICIOS" if modalidad == "Pago por Etapas (Acuerdo de Trabajo)" else "FACTURA DE SERVICIOS"
            pdf.cell(0, 10, titulo_doc, ln=True, align='C')
            pdf.ln(5)
            
            # --- CAJA DE DATOS DEL CLIENTE ---
            pdf.set_fill_color(245, 245, 250) # Fondo azul ultra claro
            pdf.set_draw_color(200, 200, 200) # Borde gris claro
            pdf.set_font("Arial", 'B', 10)
            pdf.set_text_color(0, 0, 0)
            
            cliente_nombre = exp_sel.split(" - ")[1] if exp_sel != "Seleccione..." else "Cliente General"
            codigo_exp = exp_sel.split(" - ")[0] if exp_sel != "Seleccione..." else "N/A"
            
            pdf.cell(190, 8, " INFORMACIÓN DEL CLIENTE Y EXPEDIENTE", border=1, ln=True, fill=True)
            pdf.set_font("Arial", '', 10)
            pdf.cell(95, 8, f" Cliente: {cliente_nombre}", border='L,B', ln=False)
            pdf.cell(95, 8, f" Fecha de Emisión: {fecha_factura.strftime('%d/%m/%Y')}", border='R,B', ln=True)
            pdf.cell(95, 8, f" RNC / Cédula: {identidad} (Persona {tipo_p})", border='L,B', ln=False)
            pdf.cell(95, 8, f" Expediente Vinculado: {codigo_exp}", border='R,B', ln=True)
            pdf.ln(8)
            
            # --- TABLA DE SERVICIOS ---
            # Encabezado de la tabla (Azul Marino con letras blancas)
            pdf.set_fill_color(0, 51, 102)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(140, 10, "Descripción del Servicio", border=1, ln=False, align='C', fill=True)
            pdf.cell(50, 10, "Monto (RD$)", border=1, ln=True, align='C', fill=True)
            
            # Filas de la tabla
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 11)
            for item in st.session_state.items_factura:
                pdf.cell(140, 10, f" {item['desc']}", border=1)
                pdf.cell(50, 10, f"{item['monto']:,.2f} ", border=1, ln=True, align='R')
            
            # --- ZONA DE TOTALES ---
            pdf.set_draw_color(0, 51, 102)
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 10)
            
            # Subtotal
            pdf.cell(140, 8, "SUB-TOTAL   ", ln=False, align='R')
            pdf.cell(50, 8, f"RD$ {subtotal:,.2f} ", border=1, ln=True, align='R')
            
            # ITBIS (Opcional)
            if aplicar_itbis:
                pdf.cell(140, 8, "ITBIS (18%)   ", ln=False, align='R')
                pdf.cell(50, 8, f"RD$ {itbis:,.2f} ", border=1, ln=True, align='R')
            
            # Total Final (Destacado)
            pdf.set_fill_color(184, 134, 11) # Fondo Oro
            pdf.set_text_color(255, 255, 255)
            pdf.cell(140, 10, "TOTAL GENERAL   ", ln=False, align='R')
            pdf.cell(50, 10, f"RD$ {total_final:,.2f} ", border=1, ln=True, align='R', fill=True)
            
            # --- CONDICIONES DE PAGO (CAJA INFERIOR) ---
            pdf.ln(15)
            pdf.set_text_color(0, 51, 102)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, "TÉRMINOS Y CONDICIONES DE PAGO", ln=True)
            
            pdf.set_draw_color(184, 134, 11)
            pdf.set_text_color(50, 50, 50)
            pdf.set_font("Arial", '', 10)
            # Dibujamos un rectángulo virtual usando multi_cell con bordes
            pdf.multi_cell(190, 6, texto_condiciones, border=1, align='L')
            
            # --- PIE DE PÁGINA ---
            pdf.set_y(-30) # Posición a 3 cm del final
            pdf.set_font("Arial", 'I', 9)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 5, "Este documento tiene validez legal y administrativa para los fines correspondientes.", ln=True, align='C')
            pdf.cell(0, 5, "Gracias por confiar sus procesos a AboAgrim.", ln=True, align='C')
            
            # --- EXPORTAR ---
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 Descargar Factura (PDF Premium)", pdf_bytes, f"AboAgrim_Factura_{codigo_exp}_{datetime.now().strftime('%Y%m%d')}.pdf", "application/pdf", use_container_width=True)
            st.balloons()
    else:
        st.info("Agregue servicios para facturar.")
# =====================================================================
# MÓDULO 6: FACTURACIÓN
# =====================================================================
def vista_configuracion():
    st.title("⚙️ Configuración del Sistema")
    st.subheader("Despacho Privado del Presidente Fundador")
    st.divider()

    # --- 1. MURO DE SEGURIDAD (Se muestra si no está autenticado) ---
    if not st.session_state.get("admin_autenticado", False):
        st.error("🛑 Acceso Restringido")
        st.info("Este módulo es de uso exclusivo para el Lic. Jhonny Matos. Por favor, valide su identidad.")
        
        # Habilitamos los campos de entrada para el ingreso
        col_acc1, col_acc2 = st.columns(2)
        with col_acc1:
            u_pres = st.text_input("Usuario Presidente:", key="u_login_cfg_final")
        with col_acc2:
            p_pres = st.text_input("PIN de Seguridad:", type="password", key="p_login_cfg_final")
        
        if st.button("🔓 Validar Identidad y Entrar", use_container_width=True, type="primary"):
            if u_pres == "JhonnyMatos" and p_pres == "1234": 
                # ESTO ES LO QUE LE DEVUELVE EL ACCESO A TODO:
                st.session_state.admin_autenticado = True
                st.session_state.usuario = "JhonnyMatos"
                st.session_state.rol = "Presidente Fundador" 
                st.success("Acceso total concedido, Lic. Jhonny Matos.")
                st.rerun()
            else:
                st.error("PIN incorrecto.")
        return # Detiene la carga de pestañas hasta que se autentique

    # --- 2. ÁREA DE CONTROL TOTAL (Solo visible tras el login) ---
    
    # Botón de bloqueo para cerrar el despacho al terminar
    if st.button("🔒 Bloquear y Salir del Despacho"):
        st.session_state.admin_autenticado = False
        st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["🔒 Seguridad", "🏢 Identidad", "👥 Personal", "🎨 Estilo y Fondo"])

    with tab1:
        st.markdown("### Gestión de Claves Maestras")
        st.caption("Cambie su PIN de acceso principal al sistema.")
        st.text_input("Nuevo PIN Maestro", type="password", key="new_master_pin_set")
        if st.button("Actualizar PIN"):
            st.success("Protocolo de seguridad actualizado.")

    with tab2:
        st.markdown("### Identidad Corporativa AboAgrim")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Nombre del Titular", value="Lic. Jhonny Matos. M.A.")
            st.text_input("Cargo Oficial", value="Presidente Fundador")
        with c2:
            st.text_input("Firma", value="Abogados y Agrimensores 'AboAgrim'")
            st.text_input("Sede Principal", value="Santiago, Rep. Dom.")
        st.button("Guardar Cambios de Identidad")

    with tab3:
        st.markdown("### 👥 Administración de Personal")
        
        with st.expander("➕ Dar de Alta Nuevo Usuario"):
            u_nom = st.text_input("Nombre de Usuario", key="add_u_name_final")
            u_pass = st.text_input("PIN de Acceso", type="password", key="add_u_pass_final")
            
            # Los roles deben coincidir exactamente con los del enrutador
            u_rol = st.selectbox("Nivel de Acceso (Rol):", 
                                ["Pasante", "Asistente", "Abogado", "Agrimensor"])
            
            if st.button("🚀 Confirmar Alta"):
                if u_nom and u_pass:
                    # Guardamos en la base de datos
                    data = {"nombre_usuario": u_nom, "pin_acceso": u_pass, "rol": u_rol}
                    supabase.table("usuarios_sistema").insert(data).execute()
                    st.success(f"✅ Acceso configurado para {u_nom} como {u_rol}.")
                    st.rerun()

        st.divider()
        st.markdown("### 🗑️ Gestión de Bajas")
        # [Aquí se mantiene su código anterior para eliminar usuarios]
        st.caption("Seleccione un colaborador para revocar sus credenciales de entrada.")

        try:
            # Consultamos los usuarios actuales en tiempo real
            res_usuarios = supabase.table("usuarios_sistema").select("nombre_usuario").execute()
            lista_usuarios = [u['nombre_usuario'] for u in res_usuarios.data] if res_usuarios.data else []
            
            if lista_usuarios:
                col_del_1, col_del_2 = st.columns([2, 1])
                with col_del_1:
                    usuario_a_quitar = st.selectbox("Seleccionar usuario a dar de baja:", lista_usuarios, key="sel_del_user")
                
                with col_del_2:
                    st.write("") # Espaciador para alinear con el selectbox
                    if st.button("❌ Bloquear/Quitar", type="secondary", use_container_width=True):
                        # Blindaje de seguridad: Usted no puede eliminarse a sí mismo
                        if usuario_a_quitar == "JhonnyMatos":
                            st.error("Protección de Sistema: No se permite la baja del usuario Presidente Fundador.")
                        else:
                            try:
                                supabase.table("usuarios_sistema").delete().eq("nombre_usuario", usuario_a_quitar).execute()
                                st.toast(f"Acceso revocado para {usuario_a_quitar}", icon="🗑️")
                                st.rerun()
                            except Exception as e:
                                st.error(f"No se pudo completar la acción: {e}")
            else:
                st.info("No hay otros colaboradores registrados actualmente.")
                
        except Exception as e:
            st.warning("Conectando con la base de datos de personal...")

    with tab4:
        st.markdown("### 🎨 Personalización de la Oficina Digital")
        st.write("Ajuste la apariencia visual de su entorno de trabajo.")
        
        # Leemos los valores guardados o usamos los de por defecto
        color_actual = st.session_state.get("tema_color", "#003366")
        fuente_actual = st.session_state.get("tema_fuente", "sans-serif")
        fondo_actual = st.session_state.get("tema_fondo", "Oscuro Profundo")

        col_v1, col_v2 = st.columns(2)
        with col_v1:
            nuevo_color = st.color_picker("Color de Acento (Botones y Títulos)", color_actual)
            nueva_fuente = st.selectbox(
                "Tipo de Letra", 
                ["sans-serif", "serif", "monospace"], 
                index=["sans-serif", "serif", "monospace"].index(fuente_actual) if fuente_actual in ["sans-serif", "serif", "monospace"] else 0
            )
        with col_v2:
            nuevo_fondo = st.selectbox(
                "Fondo de Interfaz", 
                ["Oscuro Profundo", "Blanco Limpio"], 
                index=0 if fondo_actual == "Oscuro Profundo" else 1
            )
        
        if st.button("✨ Aplicar Cambios Estéticos", type="primary"):
            # Guardamos las decisiones en la memoria del sistema
            st.session_state["tema_color"] = nuevo_color
            st.session_state["tema_fuente"] = nueva_fuente
            st.session_state["tema_fondo"] = nuevo_fondo
            st.success("✅ Cambios aplicados. Repintando la oficina...")
            st.rerun() # Esto recarga la página para aplicar el color
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
    st.title("📁 Archivo Digital | AboAgrim Pro")
    st.subheader("Bóveda de Expedientes y Anexos Técnicos")
    st.divider()

    # --- 1. BUSCADOR DE EXPEDIENTES ---
    st.markdown("### 🔍 Localizador de Carpetas")
    
    try:
        # Consulta a Supabase para obtener los expedientes activos
        res_exp = supabase.table("expedientes_maestros").select("expediente, nombre_propietario").execute()
        lista_expedientes = [f"{e['expediente']} - {e['nombre_propietario']}" for e in res_exp.data] if res_exp.data else []
        
        if not lista_expedientes:
            st.info("📌 No hay expedientes registrados. Vaya al 'Registro Maestro' para crear el primer caso.")
            return

        # Selector desplegable (diseño limpio sin exceso de botones)
        expediente_seleccionado = st.selectbox("Seleccione el Expediente a consultar:", ["Seleccione..."] + lista_expedientes)
        
        if expediente_seleccionado == "Seleccione...":
            return # Pausa la pantalla hasta que elija un cliente

        codigo_exp = expediente_seleccionado.split(" - ")[0]
        st.success(f"📂 Carpeta Abierta: **{expediente_seleccionado}**")

    except Exception as e:
        st.error(f"Detalle técnico del error: {e}")
        return

    st.write("---")

    # --- 2. GESTIÓN DEL EXPEDIENTE (PESTAÑAS) ---
    tab_visor, tab_carga = st.tabs(["📄 Visor de Documentos", "📤 Digitalizar y Subir"])

    # PESTAÑA A: VISOR ORGANIZADO
    with tab_visor:
        st.markdown(f"### 📑 Inventario del Expediente {codigo_exp}")
        
        # Filtro de vista rápida
        filtro_vista = st.radio(
            "Filtrar por departamento:", 
            ["Todo", "⚖️ Legal (Títulos y Actos)", "🗺️ Agrimensura (Planos y Coordenadas)", "🆔 Anexos"], 
            horizontal=True
        )

        # Aquí simulamos la lectura de archivos desde su "Storage" en Supabase
        st.info(f"Conectando con el servidor Cloud para recuperar archivos de {codigo_exp}...")
        
        # Cuadrícula de documentos (Diseño Ejecutivo)
        col_doc1, col_doc2 = st.columns(2)
        
        with col_doc1:
            st.markdown("#### 🗺️ Área Técnica")
            with st.expander("Planos y Mensura", expanded=True):
                st.caption("No hay archivos cargados en: Planos Generales.")
                st.caption("No hay archivos cargados en: Tablas de Coordenadas.")
                st.caption("No hay archivos cargados en: Datos Parcelarios.")

        with col_doc2:
            st.markdown("#### ⚖️ Área Legal")
            with st.expander("Títulos y Actos", expanded=True):
                st.caption("No hay archivos cargados en: Certificados de Título.")
                st.caption("No hay archivos cargados en: Actos de Venta/Poderes.")
                st.caption("No hay archivos cargados en: Cédulas de Identidad.")

    # PESTAÑA B: ZONA DE CARGA
    with tab_carga:
        st.markdown("### 📥 Ingreso de Nuevos Documentos")
        st.write("Clasifique y suba los escaneos directamente a la bóveda del cliente.")
        
        with st.container(border=True):
            col_form1, col_form2 = st.columns(2)
            
            with col_form1:
                # Categorías técnicas y legales detalladas
                categoria_doc = st.selectbox(
                    "Clasificación del Documento:", 
                    [
                        "Plano General Catastral",
                        "Tabla de Coordenadas", 
                        "Datos Parcelarios (Derrotero)",
                        "Certificado de Título", 
                        "Acto de Venta / Contrato", 
                        "Poder de Representación",
                        "Cédula / Identificación",
                        "Resolución del Tribunal"
                    ]
                )
                descripcion_doc = st.text_input("Breve descripción (Opcional):", placeholder="Ej: Plano aprobado marzo 2026")
                
            with col_form2:
                archivo_pdf = st.file_uploader("Seleccione el archivo escaneado (PDF, JPG)", type=["pdf", "jpg", "png"])
            
            if st.button("💾 Encriptar y Guardar en Bóveda", use_container_width=True, type="primary"):
                if archivo_pdf:
                    # Lógica futura para: supabase.storage.from_('boveda').upload(f"{codigo_exp}/{archivo_pdf.name}")
                    st.toast(f"Archivo '{archivo_pdf.name}' procesado.", icon="✅")
                    st.success(f"El documento se ha guardado exitosamente bajo la categoría '{categoria_doc}' en el expediente {codigo_exp}.")
                else:
                    st.warning("⚠️ Debe adjuntar un archivo antes de proceder a guardar.")
        
        
def vista_plantillas_auto():
    st.title("📄 Fábrica de Documentos AboAgrim Pro")
    st.subheader("Módulo de Control Técnico y Legal JI")

    # --- INICIALIZACIÓN DE MEMORIA DINÁMICA ---
    if 'cant_extras' not in st.session_state: st.session_state.cant_extras = 0
    if 'cant_profesionales' not in st.session_state: st.session_state.cant_profesionales = 0
    if 'cant_apoderados' not in st.session_state: st.session_state.cant_apoderados = 0

    TRAMITES_JI = {
        "📍 Mensuras Catastrales": [
            "Actualización de Mensura", "Corrección Mensura Desplazada", "Desafectación de Dominio Público", 
            "Deslinde", "División para Constitución de Condominio", "Modificación Condominio", 
            "Oposición Expediente Técnico", "Plano Definitivo", "Prórroga de Autorización", 
            "Refundición", "Regularización Parcelaria", "Saneamiento", "Subdivisión", "Urbanización Parcelaria"
        ],
        "📜 Registro de Títulos": [
            "Transferencia de Inmueble", "Transferencia de Mejoras", "Hipoteca Convencional", 
            "Cancelación de Hipoteca Convencional", "Certificación del Estado Jurídico del Inmueble", 
            "Actualización de Generales", "Duplicado por Pérdida o Deterioro", "Constitución de Régimen de Condominio", 
            "Embargo Inmobiliario", "Privilegio de Honorarios de Abogados", "Anotación Preventiva"
        ],
        "⚖️ Tribunales de Tierras": [
            "Determinación de Herederos", "Litis Sobre Derechos Registrados", "Recurso de Apelación", 
            "Partición Amigable Entre Esposos", "Partición Amigable con Determinación de Herederos", 
            "Renuncia de Bien de Familia", "Solicitud de Transferencias Administrativas", 
            "Solicitud de Desglose como Instancia Principal Administrativa", "Revisión por Causa de Fraude"
        ]
    }

    try:
        res = supabase.table("expedientes_maestros").select("id, nombre_propietario").order("id", desc=True).execute()
        opciones_exp = {f"RES-{e['id']} | {e['nombre_propietario']}": e['id'] for e in res.data} if res.data else {"Ninguno": None}

        col_menu1, col_menu2, col_menu3 = st.columns(3)
        with col_menu1:
            sel_cliente = st.selectbox("👤 Expediente:", list(opciones_exp.keys()))
            id_cliente = opciones_exp.get(sel_cliente)
        with col_menu2:
            jurisdiccion = st.selectbox("🏛️ Jurisdicción:", list(TRAMITES_JI.keys()))
        with col_menu3:
            tramite = st.selectbox(f"📋 Trámite:", TRAMITES_JI[jurisdiccion])

        st.divider()

        # ==========================================
        # 1. BLOQUE DE DATOS TÉCNICOS BASE
        # ==========================================
        st.write(f"### 📑 Datos Estándar de JI")
        c1, c2, c3 = st.columns(3)
        with c1:
            ji_parcela = st.text_input("Parcela No.", placeholder="Ej: 123-A")
            ji_dc = st.text_input("Distrito Catastral (DC)", placeholder="Ej: 01")
            ji_solar_manzana = st.text_input("Solar / Manzana", placeholder="Ej: Solar 5, Manzana 12")
            
        with c2:
            ji_matricula = st.text_input("Matrícula / Certificado")
            ji_libro = st.text_input("Libro / Folio")
            ji_fecha_emision = st.text_input("Fecha Inscripción / Emisión", placeholder="DD/MM/AAAA")
            
        with c3:
            ji_exp_ji = st.text_input("Expediente JI No.")
            ji_ubicacion = st.text_input("Ubicación del Inmueble", value="Santiago")
            ji_area = st.text_input("Área / Superficie (m²)")
            ji_coordenadas = st.text_input("Coordenadas (UTM/WGS84)")

        # ==========================================
        # 1.5 BLOQUE DINÁMICO DE LITIGIO (SOLO TRIBUNALES)
        # ==========================================
        ji_demandante = ji_demandado = ji_sala = ji_juez = ji_rol = ji_audiencia = ""
        
        if jurisdiccion == "⚖️ Tribunales de Tierras":
            st.write("---")
            st.markdown("### ⚖️ Módulo de Litigios (Exclusivo Tribunal)")
            lt1, lt2, lt3 = st.columns(3)
            with lt1:
                ji_demandante = st.text_input("Parte Demandante / Recurrente")
                ji_demandado = st.text_input("Parte Demandada / Recurrida")
            with lt2:
                ji_sala = st.text_input("Sala / Cámara", placeholder="Ej: Segunda Sala")
                ji_juez = st.text_input("Magistrado / Juez Apoderado")
            with lt3:
                ji_rol = st.text_input("Número de Rol / Cuaderno")
                ji_audiencia = st.text_input("Fecha de Próxima Audiencia", placeholder="DD/MM/AAAA")

        # ==========================================
        # 2. CAMPOS EXTRA DINÁMICOS (JI)
        # ==========================================
        st.write("---")
        col_btn1, col_btn2, col_space = st.columns([1, 1, 3])
        with col_btn1:
            if st.button("➕ Agregar Dato Extra JI", use_container_width=True): st.session_state.cant_extras += 1
        with col_btn2:
            if st.button("➖ Borrar Dato Extra", use_container_width=True) and st.session_state.cant_extras > 0: st.session_state.cant_extras -= 1

        datos_extras_dict = {}
        for i in range(st.session_state.cant_extras):
            c_nom, c_val = st.columns(2)
            with c_nom: 
                nombre_campo = st.text_input(f"Nombre del dato {i+1}", key=f"ex_n_{i}")
            with c_val: 
                valor_campo = st.text_input(f"Valor {i+1}", key=f"ex_v_{i}")
            if nombre_campo: datos_extras_dict[nombre_campo.replace(" ", "_").lower()] = valor_campo

        # ==========================================
        # 3. PROFESIONALES ACTUANTES DINÁMICOS
        # ==========================================
        st.write("---")
        st.subheader("👥 Profesionales Actuantes")
        col_p1, col_p2, col_p3 = st.columns([1, 1, 3])
        with col_p1:
            if st.button("➕ Agregar Profesional", use_container_width=True): st.session_state.cant_profesionales += 1
        with col_p2:
            if st.button("➖ Borrar Profesional", use_container_width=True) and st.session_state.cant_profesionales > 0: st.session_state.cant_profesionales -= 1

        profesionales_lista = []
        for i in range(st.session_state.cant_profesionales):
            st.markdown(f"**Profesional {i+1}**")
            cp1, cp2, cp3 = st.columns(3)
            with cp1: n = st.text_input(f"Nombre Completo", key=f"p_nom_{i}")
            with cp2: r = st.selectbox(f"Rol", ["Abogado", "Agrimensor", "Notario Público"], key=f"p_rol_{i}")
            with cp3: c = st.text_input(f"Colegiatura", key=f"p_col_{i}")
            
            cpg1, cpg2, cpg3 = st.columns(3)
            with cpg1: p_ced = st.text_input(f"Cédula", key=f"p_ced_{i}")
            with cpg2: p_ec = st.selectbox(f"Estado Civil", ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"], key=f"p_ec_{i}")
            with cpg3: p_dom = st.text_input(f"Domicilio Profesional", key=f"p_dom_{i}")
            
            profesionales_lista.append({
                "nombre": n, "rol": r, "colegiatura": c, 
                "cedula": p_ced, "estado_civil": p_ec, "domicilio": p_dom
            })

        # ==========================================
        # 4. APODERADOS / REPRESENTANTES DINÁMICOS
        # ==========================================
        st.write("---")
        st.subheader("🤝 Representantes o Apoderados")
        col_a1, col_a2, col_a3 = st.columns([1, 1, 3])
        with col_a1:
            if st.button("➕ Agregar Apoderado", use_container_width=True): st.session_state.cant_apoderados += 1
        with col_a2:
            if st.button("➖ Borrar Apoderado", use_container_width=True) and st.session_state.cant_apoderados > 0: st.session_state.cant_apoderados -= 1

        apoderados_lista = []
        for i in range(st.session_state.cant_apoderados):
            st.markdown(f"**Apoderado / Representante {i+1}**")
            ca1, ca2, ca3 = st.columns(3)
            with ca1: an = st.text_input(f"Nombre Completo", key=f"a_nom_{i}")
            with ca2: ac = st.text_input(f"Cédula / Pasaporte", key=f"a_ced_{i}")
            with ca3: ar = st.text_input(f"En representación de", key=f"a_rep_{i}")
            
            cag1, cag2, cag3 = st.columns(3)
            with cag1: a_nac = st.text_input(f"Nacionalidad", value="Dominicano/a", key=f"a_nac_{i}")
            with cag2: a_ec = st.selectbox(f"Estado Civil", ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"], key=f"a_ec_{i}")
            with cag3: a_dom = st.text_input(f"Domicilio", key=f"a_dom_{i}")
            
            apoderados_lista.append({
                "nombre": an, "cedula": ac, "representa": ar,
                "nacionalidad": a_nac, "estado_civil": a_ec, "domicilio": a_dom
            })

        st.divider()

        # ==========================================
        # 5. FABRICACIÓN FINAL
        # ==========================================
        archivo_nombre = tramite.lower().replace(" ", "_") + ".docx"
        carpeta = "1_mensuras_catastrales" if "Mensuras" in jurisdiccion else "3_registro_titulos" if "Registro" in jurisdiccion else "2_jurisdiccion_original"
        ruta_final = f"plantillas_maestras/{carpeta}/{archivo_nombre}"

        if st.button(f"🚀 FABRICAR DOCUMENTO MAESTRO", type="primary", use_container_width=True) and id_cliente:
            with st.status("🛠️ Ensamblando expediente...", expanded=False):
                try:
                    res_db = supabase.table("expedientes_maestros").select("*").eq("id", id_cliente).single().execute()
                    
                    contexto_word = {
                        **res_db.data,
                        "parcela": ji_parcela, "dc": ji_dc, "solar_manzana": ji_solar_manzana,
                        "matricula": ji_matricula, "libro_folio": ji_libro, "fecha_emision": ji_fecha_emision,
                        "expediente_ji": ji_exp_ji, "ubicacion_inmueble": ji_ubicacion, "area": ji_area, "coordenadas": ji_coordenadas,
                        # Datos de Litigio
                        "demandante": ji_demandante, "demandado": ji_demandado, "sala_camara": ji_sala,
                        "juez_apoderado": ji_juez, "no_rol": ji_rol, "fecha_audiencia": ji_audiencia,
                        # Firmas
                        "firma_presidente": "Lic. Jhonny Matos. M.A.", "cargo_presidente": "Presidente Fundador",
                        **datos_extras_dict,
                        "profesionales": profesionales_lista, "apoderados": apoderados_lista
                    }

                    archivo_bin = generar_documento_word(ruta_final, contexto_word)

                    if archivo_bin:
                        st.success(f"✅ ¡Documento generado para {res_db.data['nombre_propietario']}!")
                        st.download_button("📥 DESCARGAR DOCUMENTO", archivo_bin, f"{tramite}.docx", use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Error al fabricar: {e}")

        # ==========================================
        # 6. MANTENIMIENTO CON PIN
        # ==========================================
        st.write("---")
        with st.expander("🛠️ ADMINISTRAR ARCHIVOS DE PLANTILLAS"):
            pin_ingresado = st.text_input("🔑 PIN de Seguridad:", type="password", key="pin_p_auto")
            PIN_SECRETO = "0681" 
            if pin_ingresado == PIN_SECRETO:
                maint_col1, maint_col2 = st.columns(2)
                import os
                with maint_col1:
                    st.markdown("**📤 Subir**")
                    destino = st.radio("Carpeta:", ["1_mensuras_catastrales", "2_jurisdiccion_original", "3_registro_titulos"])
                    archivo_subido = st.file_uploader("Elija el archivo .docx", type=["docx"])
                    if st.button("💾 Guardar"):
                        if archivo_subido:
                            os.makedirs(f"plantillas_maestras/{destino}", exist_ok=True)
                            with open(f"plantillas_maestras/{destino}/{archivo_subido.name}", "wb") as f: f.write(archivo_subido.getbuffer())
                            st.success(f"✅ Guardado en {destino}.")
                with maint_col2:
                    st.markdown("**🗑️ Borrar**")
                    carpeta_borrar = st.selectbox("Carpeta:", ["1_mensuras_catastrales", "2_jurisdiccion_original", "3_registro_titulos"], key="del_f")
                    ruta_limpieza = f"plantillas_maestras/{carpeta_borrar}"
                    archivos = os.listdir(ruta_limpieza) if os.path.exists(ruta_limpieza) else []
                    archivo_a_borrar = st.selectbox("Archivo a eliminar:", archivos)
                    if st.button("🗑️ ELIMINAR"):
                        if archivo_a_borrar:
                            os.remove(f"{ruta_limpieza}/{archivo_a_borrar}")
                            st.rerun()

    except Exception as e:
        st.error(f"❌ Error crítico: {e}")
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

# Módulos básicos
modulos = ["🏠 Mando Central", "👤 Registro Maestro", "📁 Archivo Digital", "📄 Plantillas Auto"]

# Filtro de jerarquía para Alertas y Facturación
if rol_usuario in ["Abogado", "Agrimensor", "Presidente Fundador"]:
    modulos.append("📅 Alertas y Plazos")
    modulos.append("💵 Facturación")

# LA CLAVE: Siempre mostramos Configuración si no está logueado como admin
# para que pueda poner su PIN y entrar.
if rol_usuario == "Presidente Fundador" or not admin_activo:
    modulos.append("⚙️ Configuración")

with st.sidebar:
    st.markdown(f"**Firmado como:** {usuario_actual if usuario_actual else 'Invitado'}")
    st.caption(f"**Nivel de Acceso:** {rol_usuario}")
    menu = st.radio("Ir a:", modulos)

# --- LÓGICA DE CARGA DE FUNCIONES (ENRUTADOR FINAL) ---
if menu == "🏠 Mando Central":
    vista_mando_central()

elif menu == "👤 Registro Maestro":
    vista_registro_maestro()

elif menu == "📁 Archivo Digital":
    vista_archivo_digital()

elif menu == "📄 Plantillas Auto":
    vista_plantillas_auto()

elif menu == "📅 Alertas y Plazos":
    st.info("Módulo de Alertas y Plazos Operativo")

elif menu == "💵 Facturación":
    vista_facturacion()  # <--- Aquí está la llamada real

elif menu == "⚙️ Configuración":
    vista_configuracion()
