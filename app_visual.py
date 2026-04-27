# =====================================================================
# INTERFAZ GRÁFICA Y SISTEMA EXPERTO LEGAL JI (EDICIÓN PREMIUM FULL)
# Sistema: AboAgrim Pro DMS 
# =====================================================================
import streamlit as st
import zipfile
import io
from docxtpl import DocxTemplate
# ... arriba están los import ...
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

def vista_facturacion():
    from datetime import datetime 
    
    st.title("💵 Gestión de Facturación y Honorarios")
    
    # 1. Indicadores Financieros
    c1, c2, c3 = st.columns(3)
    c1.metric("Pendiente por Cobrar", "RD$ 45,000", "+5%")
    c2.metric("Cobrado este mes", "RD$ 120,000")
    c3.metric("Gastos Operativos", "RD$ 12,500")

    st.markdown("---")

    # 2. Lógica de Búsqueda Automática
    try:
        res = supabase.table("registro_maestro").select("nombre_completo, cedula, direccion").execute()
        clientes_db = res.data
    except Exception:
        clientes_db = []

    col_form, col_tabla = st.columns([1, 1.2], gap="large") 

    with col_form:
        st.subheader("📝 Nuevo Registro de Cobro")
        
        nombres_clientes = [c['nombre_completo'] for c in clientes_db]
        cliente_seleccionado = st.selectbox("🔍 Buscar Cliente", ["-- Seleccione un cliente --"] + nombres_clientes)
        
        val_cedula, val_direccion, val_nombre = "", "", ""
        if cliente_seleccionado != "-- Seleccione un cliente --":
            datos = next((c for c in clientes_db if c['nombre_completo'] == cliente_seleccionado), None)
            if datos:
                val_nombre = datos['nombre_completo']
                val_cedula = datos.get('cedula', '')
                val_direccion = datos.get('direccion', '')
        
        with st.form("form_crear_factura"):
            nombre_final = st.text_input("Nombre del Cliente", value=val_nombre)
            
            c_ced, c_dir = st.columns(2)
            cedula_fact = c_ced.text_input("Cédula / RNC", value=val_cedula)
            direccion_fact = c_dir.text_input("Dirección", value=val_direccion)
            
            concepto_fact = st.text_input("Concepto (Ej. Saneamiento Parcela 12)")
            
            # --- NUEVA CASILLA: MONTO TOTAL VS PAGO ACTUAL ---
            c_total, c_actual = st.columns(2)
            monto_total_contrato = c_total.number_input("Monto Total Contrato (RD$)", min_value=0.0, step=5000.0)
            monto_pago_actual = c_actual.number_input("Monto Pago Actual (RD$)", min_value=0.0, step=1000.0)
            
            # --- PAGOS POR ETAPAS ---
            etapa_pago = st.selectbox("Etapa del Proceso", [
                "Pago Único", "Avance Inicial", "Etapa de Campo", "Sometimiento JI", "Aprobación / Entrega"
            ])
            
            estado_fact = st.selectbox("Estado del Pago Actual", ["Pendiente", "Pagado", "Abono"])
            
            st.markdown("---")
            b1, b2 = st.columns(2)
            btn_guardar = b1.form_submit_button("💾 Guardar en Nube")
            btn_enviar = b2.form_submit_button("📤 Generar Factura")

        # --- LÓGICA DE GUARDADO ---
        if btn_guardar:
            nueva_factura = {
                "cliente": nombre_final,
                "monto_pago": monto_pago_actual,
                "monto_total": monto_total_contrato,
                "estado": estado_fact,
                "concepto": f"{concepto_fact} ({etapa_pago})",
                "fecha": datetime.now().isoformat()
            }
            try:
                supabase.table("facturas").insert(nueva_factura).execute()
                st.success(f"✅ Cobro de {nombre_final} registrado.")
            except Exception as e:
                st.error(f"Error: {e}")
        
        # --- DISEÑO PREMIUM CON DESGLOSE DE MONTOS ---
        if btn_enviar:
            if nombre_final and monto_pago_actual > 0:
                fecha_hoy = datetime.now().strftime("%d/%m/%Y")
                num_recibo = datetime.now().strftime("ABG-%y%m%d%H%M")
                pendiente = monto_total_contrato - monto_pago_actual if monto_total_contrato > 0 else 0
                
                recibo_html = f"""
                <html>
                <head><meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f6f9; padding: 20px; }}
                    .container {{ max-width: 700px; margin: auto; background: #fff; padding: 40px; border-radius: 10px; border-top: 10px solid #0a2540; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
                    .header {{ display: flex; justify-content: space-between; margin-bottom: 30px; border-bottom: 2px solid #eee; padding-bottom: 20px; }}
                    .logo h1 {{ color: #0a2540; margin: 0; }}
                    .details {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    .details td {{ padding: 10px; border-bottom: 1px solid #eee; }}
                    .details td:first-child {{ font-weight: bold; color: #555; }}
                    .monto-box {{ margin-top: 30px; padding: 20px; background: #f8fcf9; border-radius: 8px; text-align: right; }}
                    .total-line {{ font-size: 22px; color: #2e8540; font-weight: bold; }}
                    .footer {{ text-align: center; margin-top: 50px; font-size: 12px; color: #888; }}
                </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <div class="logo"><h1>⚖️ AboAgrim</h1><p>Lic. Jhonny Matos. M.A.</p></div>
                            <div style="text-align: right;"><strong>Recibo No:</strong> {num_recibo}<br><strong>Fecha:</strong> {fecha_hoy}</div>
                        </div>
                        <h2 style="text-align: center; color: #0a2540;">RECIBO DE PAGO</h2>
                        <table class="details">
                            <tr><td>Cliente:</td><td>{nombre_final}</td></tr>
                            <tr><td>RNC/Cédula:</td><td>{cedula_fact}</td></tr>
                            <tr><td>Concepto:</td><td>{concepto_fact}</td></tr>
                            <tr><td>Etapa del Proceso:</td><td>{etapa_pago}</td></tr>
                        </table>
                        <div class="monto-box">
                            <p>Monto Total del Trabajo: RD$ {monto_total_contrato:,.2f}</p>
                            <p class="total-line">PAGO RECIBIDO HOY: RD$ {monto_pago_actual:,.2f}</p>
                            <hr>
                            <p style="color: #c0392b;">Balance Pendiente: RD$ {pendiente:,.2f}</p>
                        </div>
                        <div class="footer">
                            <div style="width: 200px; border-top: 1px solid #000; margin: 40px auto 10px auto;"></div>
                            Firma Autorizada - AboAgrim Pro DMS
                        </div>
                    </div>
                </body>
                </html>
                """
                st.download_button("⬇️ Descargar Recibo Detallado", recibo_html, file_name=f"Recibo_{nombre_final}.html", mime="text/html")

    with col_tabla:
        st.subheader("📋 Historial de Pagos")
        try:
            res_fact = supabase.table("facturas").select("cliente, monto_pago, monto_total, estado, fecha").order("fecha", desc=True).execute()
            st.dataframe(res_fact.data, use_container_width=True)
        except:
            st.info("Conecte la tabla 'facturas' en Supabase para ver el historial real.")
# =====================================================================
# MÓDULO 6: FACTURACIÓN
# =====================================================================
def vista_configuracion():
    st.title("⚙️ Configuración del Sistema")
    
    with st.expander("🏢 Datos de la Firma AboAgrim"):
        st.text_input("Nombre de la Oficina", value="Abogados y Agrimensores 'AboAgrim'")
        st.text_input("Dirección en Santiago", value="Calle Principal, Santiago, Rep. Dom.")
        st.text_input("Teléfono de Contacto", value="809-XXX-XXXX")
        
    with st.expander("💾 Conexión de Base de Datos"):
        st.success("Conexión con Supabase: ACTIVA")
        st.code("Host: database.supabase.co")
        
    if st.button("Guardar Cambios"):
        st.success("Configuración actualizada")
    # --- BLOQUE DE SEGURIDAD ---
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.header("🔒 Acceso Restringido - Facturación")
        pin = st.text_input("Ingrese su PIN de Seguridad:", type="password", key="pin_fact")
        if st.button("Validar Acceso"):
            if pin == "1234": # <--- Licenciado, aquí pone su clave
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("PIN Incorrecto.")
        return 

    # --- TODO SU CONTENIDO NUEVO (FUSIONADO) ---
    st.header("💰 Gestión de Honorarios y Facturación")
    
    # Mantenemos sus mensajes automáticos
    MENSAJES_PRO = {
        "Anticipo": "Hola, le saludo de AboAgrim. Confirmamos el recibo de su anticipo.",
        "Saldo": "Saludos, su expediente está listo. Favor pasar a liquidar el saldo.",
        "Recordatorio": "Buen día, le recordamos que tiene un pago pendiente.",
        "Mensura Programada": "Hola, su mensura ha sido agendada. Favor estar presente."
    }

    with st.expander("➕ Registrar y Despachar Factura", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            exp_fact = st.text_input("No. de Expediente:")
            cli_fact = st.text_input("Nombre del Cliente:")
            tel_cli = st.text_input("WhatsApp (Ej: 1809...):")
            monto_t = st.number_input("Monto Total (RD$):", min_value=0.0)
        with col2:
            monto_a = st.number_input("Monto Recibido (RD$):", min_value=0.0)
            concepto = st.text_input("Concepto:")
            msg_tipo = st.selectbox("Mensaje WhatsApp:", list(MENSAJES_PRO.keys()))
            
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        
        if c1.button("💾 Guardar en Nube"):
            estado = "Saldado" if monto_a >= monto_t else "Pendiente"
            try:
                supabase.table("facturacion").insert({
                    "expediente_id": exp_fact, "cliente": cli_fact,
                    "monto_total": monto_t, "monto_abonado": monto_a,
                    "concepto": concepto, "estado_pago": estado
                }).execute()
                st.success("✅ ¡Registrado en Supabase!")
            except Exception as e:
                st.error(f"Error: {e}")

        if c2.button("📲 Enviar WhatsApp"):
            if tel_cli:
                msg = f"{MENSAJES_PRO[msg_tipo]} *Detalle:* {concepto}. *Monto:* RD${monto_a}".replace(" ", "%20")
                st.markdown(f'<a href="https://wa.me/{tel_cli}?text={msg}" target="_blank"><button style="background-color:#25D366;color:white;border:none;padding:10px;border-radius:5px;width:100%;">Abrir WhatsApp</button></a>', unsafe_allow_html=True)
            else: st.warning("Falta teléfono.")

        if c3.button("🖨️ Imprimir Recibo"):
            factura_html = f"<h3>RECIBO ABOAGRIM</h3><p><b>Cliente:</b> {cli_fact}<br><b>Monto:</b> RD${monto_a}</p><script>window.print();</script>"
            st.components.v1.html(factura_html, height=200)

    if st.button("🔒 Cerrar Caja Fuerte"):
        st.session_state.autenticado = False
        st.rerun()
    # (Aquí sigue el código de la tabla que ya teníamos para mostrar los datos de Supabase)
# =====================================================================
# MÓDULO 7: CONFIGURACIÓN
# =====================================================================
def vista_configuracion():
    # --- 1. BLOQUEO DE ADMINISTRADOR ÚNICO ---
    if "admin_autenticado" not in st.session_state:
        st.session_state.admin_autenticado = False

    if not st.session_state.admin_autenticado:
        st.header("🔒 Área Exclusiva del Propietario")
        st.info("Solo el Lic. Jhonny Matos puede gestionar esta sección.")
        
        u_admin = st.text_input("Usuario Maestro:", key="admin_user")
        p_admin = st.text_input("PIN Maestro:", type="password", key="admin_pin")
        
        if st.button("Validar Identidad de Propietario"):
            # Validamos que sea USTED y que coincida con la base de datos
            res = supabase.table("usuarios_sistema").select("*").eq("nombre_usuario", u_admin).eq("pin_acceso", p_admin).execute()
            
            if res.data and u_admin == "JhonnyMatos":
                st.session_state.admin_autenticado = True
                st.success("Identidad confirmada. Bienvenido, Licenciado.")
                st.rerun()
            else:
                st.error("Acceso denegado. Esta sección es solo para el administrador principal.")
        return

    # --- 2. PANEL DE CONTROL (Si ya es usted) ---
    st.divider()
    st.subheader("📥 Respaldo y Protección de Datos")
    st.info("Descargue una copia de seguridad completa (Excel) de su base de datos a su computadora.")

    if st.button("🚀 Generar Respaldo Maestro"):
        try:
            import pandas as pd
            from io import BytesIO
            from datetime import date

            # 1. Extraer datos de Supabase
            df_ingresos = pd.DataFrame(supabase.table("facturacion").select("*").execute().data)
            df_agenda = pd.DataFrame(supabase.table("agenda_mensuras").select("*").execute().data)
            df_usuarios = pd.DataFrame(supabase.table("usuarios_sistema").select("*").execute().data)
            
            # 2. Preparar el archivo Excel en memoria
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_ingresos.to_excel(writer, sheet_name='Facturacion', index=False)
                df_agenda.to_excel(writer, sheet_name='Agenda_Plazos', index=False)
                df_usuarios.to_excel(writer, sheet_name='Usuarios', index=False)
            
            # 3. Crear el botón de descarga real
            st.download_button(
                label="💾 Guardar Archivo en PC",
                data=output.getvalue(),
                file_name=f"Respaldo_AboAgrim_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("✅ Archivo generado. Presione el botón de arriba para guardarlo.")
        except Exception as e:
            st.error(f"Hubo un problema al recopilar los datos: {e}")
    st.header("⚙️ Panel de Control Maestro")
    
    tab1, tab2 = st.tabs(["👥 Gestión de Accesos", "🎨 Diseño y Estilo"])

    with tab1:
        st.subheader("Control de Colaboradores")
        with st.expander("➕ Dar Acceso a Nuevo Usuario"):
            nuevo_u = st.text_input("Nombre:")
            nuevo_p = st.text_input("PIN (4 dígitos):", type="password", max_chars=4)
            if st.button("Crear Acceso"):
                try:
                    supabase.table("usuarios_sistema").insert({"nombre_usuario": nuevo_u, "pin_acceso": nuevo_p}).execute()
                    st.success(f"Acceso creado para {nuevo_u}")
                except: st.error("El usuario ya existe.")
        
        # Lista para quitar accesos
        usuarios = supabase.table("usuarios_sistema").select("*").execute()
        for u in usuarios.data:
            c1, c2 = st.columns([3, 1])
            c1.write(f"👤 **{u['nombre_usuario']}** - {u['estado']}")
            label = "Bloquear" if u['estado'] == 'Activo' else "Activar"
            est = 'Inactivo' if u['estado'] == 'Activo' else 'Activo'
            if c2.button(label, key=f"u_{u['id']}"):
                supabase.table("usuarios_sistema").update({"estado": est}).eq("id", u['id']).execute()
                st.rerun()

    with tab2:
        st.subheader("Personalización de AboAgrim Pro")
        color_p = st.color_picker("Color de la Firma:", "#1E3A8A")
        if st.button("Guardar Cambios de Diseño"):
            st.markdown(f"<style>h1, h2, h3 {{ color: {color_p} !important; }} .stButton>button {{ background-color: {color_p} !important; }}</style>", unsafe_allow_html=True)
            st.success("Diseño actualizado.")

    if st.button("🔒 Salir de Modo Maestro"):
        st.session_state.admin_autenticado = False
        st.rerun()

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
    st.title("📂 Archivo Digital de Expedientes")
    
    # --- Estilo de Tarjetas Premium ---
    st.markdown("""
        <style>
        .card {
            border: 1px solid #e6e9ef;
            padding: 1.5rem;
            border-radius: 12px;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
        }
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }
        </style>
    """, unsafe_allow_html=True)

    # 1. Métricas (KPIs)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Expedientes", "1,240", "↑ 12")
    m2.metric("Aprobados", "850", "72%")
    m3.metric("En Proceso", "125", "-4")
    m4.metric("Digital", "98%", "🔥")

    st.divider()

    # 2. Lógica de Datos (Traer de Supabase)
    try:
        # Buscamos en su tabla maestra
        res = supabase.table("registro_maestro").select("*").limit(10).execute()
        expedientes = res.data
    except:
        expedientes = [] # Fallback por si la tabla está vacía

    # 3. Buscador
    query = st.text_input("🔍 Buscar expediente por nombre o parcela...")

    # 4. Generación de Tarjetas
    for exp in expedientes:
        nombre = exp.get('nombre_completo', 'Sin Nombre')
        id_exp = exp.get('id', '000')
        tipo = exp.get('tipo_proceso', 'Legal/Técnico')
        estado = exp.get('estado', 'Activo')
        
        # Filtro de búsqueda simple
        if query.lower() in nombre.lower():
            with st.container():
                # Diseño de la Tarjeta con HTML
                color_estado = "#d4edda" if estado == "Completado" else "#fff3cd"
                texto_estado = "#155724" if estado == "Completado" else "#856404"
                
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #0a2540; font-weight: bold; font-size: 18px;">👤 {nombre}</span>
                        <span class="status-badge" style="background-color: {color_estado}; color: {texto_estado};">
                            {estado}
                        </span>
                    </div>
                    <p style="color: #666; margin: 10px 0;">📂 <b>Tipo:</b> {tipo} | 🆔 <b>ID:</b> {id_exp}</p>
                </div>
                """, unsafe_allow_html=True)

                # Botones de Acción
                col1, col2, col3 = st.columns([1, 1, 2])
                
                if col1.button(f"📄 Ver Documentos", key=f"doc_{id_exp}"):
                    st.session_state.expediente_ver = nombre
                    st.toast(f"Cargando archivos de {nombre}...")
                
                if col2.button(f"✏️ Editar", key=f"edit_{id_exp}"):
                    st.info("Función de edición en desarrollo")

                # Visualizador de archivos (Solo aparece si se hace clic)
                if st.session_state.get('expediente_ver') == nombre:
                    with st.expander(f"📂 Carpeta Digital: {nombre}", expanded=True):
                        st.write("---")
                        # Aquí conectaríamos con su Google Drive
                        st.markdown("### 📥 Archivos Disponibles")
                        col_a, col_b = st.columns(2)
                        col_a.link_button("📜 Título de Propiedad.pdf", "https://google.com")
                        col_b.link_button("🗺️ Plano Catastral.pdf", "https://google.com")
                        if st.button("Cerrar Carpeta"):
                            st.session_state.expediente_ver = None
                            st.rerun()

    # Botón para agregar nuevo
    st.markdown("---")
    if st.button("➕ Digitalizar Nuevo Expediente", use_container_width=True):
        st.success("Abriendo escáner y carga de archivos...")

# --- 🔐 CANDADO DE SEGURIDAD PRINCIPAL ---
if not st.session_state.get("autenticado_global", False):
    login_sistema()
    st.stop()  # 🛑 Esto oculta todo el menú y el sistema si no hay PIN
# ==========================================
# MENÚ LATERAL Y NAVEGACIÓN DEL SISTEMA
# ==========================================
with st.sidebar:
    menu = st.radio(
        "Navegación",
        [
            "🏠 Mando Central",
            "👤 Registro Maestro",
            "📁 Archivo Digital",
            "📄 Plantillas Auto",
            "📅 Alertas y Plazos",
            "💵 Facturación",
            "⚙️ Configuración"
        ]
    )
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado_global = False
        st.rerun()
        
        
def vista_plantillas_auto():
    st.title("📄 Fábrica de Documentos AboAgrim Pro")
    st.subheader("Módulo de Control Técnico y Legal JI")

    # --- INICIALIZACIÓN DE MEMORIA DINÁMICA ---
    if 'cant_extras' not in st.session_state: st.session_state.cant_extras = 0
    if 'cant_profesionales' not in st.session_state: st.session_state.cant_profesionales = 0
    if 'cant_apoderados' not in st.session_state: st.session_state.cant_apoderados = 0

    # ==========================================
    # EL DICCIONARIO MAESTRO JI (COMPLETO)
    # ==========================================
    TRAMITES_JI = {
        "📍 Mensuras Catastrales": [
            "Actualización de Mensura", "Corrección Mensura Desplazada", 
            "Depósito de Documentos Físicos", "Desafectación de Dominio Público", 
            "Deslinde", "División para Constitución de Condominio", 
            "Modificación Condominio", "Oposición Expediente Técnico", 
            "Plano Definitivo", "Prórroga de Autorización", 
            "Recurso Jerárquico", "Refundición", 
            "Regularización Parcelaria", "Saneamiento", 
            "Solicitud de Autorización", "Solicitud de Reconsideración", 
            "Subdivisión", "Urbanización Parcelaria"
        ],
        "📜 Registro de Títulos": [
            "Transferencia de Inmueble", "Transferencia de Mejoras",
            "Hipoteca Convencional", "Hipoteca Judicial", "Hipoteca Legal de la Mujer Casada",
            "Cancelación de Hipoteca Convencional", "Cancelación de Hipoteca Judicial",
            "Certificación del Estado Jurídico del Inmueble", "Certificación con Reserva de Prioridad",
            "Actualización de Generales", "Duplicado por Pérdida o Deterioro", 
            "Constitución de Régimen de Condominio", "Corrección de Certificado de Título",
            "Embargo Inmobiliario", "Cancelación de Embargo Inmobiliario",
            "Constitución de Bien de Familia", "Cancelación de Bien de Familia",
            "Privilegio de Honorarios de Abogados", "Cancelación de Privilegio de Honorarios",
            "Adjudicación", "Anotación Preventiva"
        ],
        "⚖️ Tribunales de Tierras": [
            "Determinación de Herederos", "Litis Sobre Derechos Registrados", 
            "Certificaciones", "Recurso de Apelación", 
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
        # 3. PROFESIONALES ACTUANTES DINÁMICOS (CON GENERALES)
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
            st.write("") 

        # ==========================================
        # 4. APODERADOS / REPRESENTANTES DINÁMICOS (CON GENERALES)
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
            st.write("") 

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
                        "parcela": ji_parcela,
                        "dc": ji_dc,
                        "solar_manzana": ji_solar_manzana,
                        "matricula": ji_matricula,
                        "libro_folio": ji_libro,
                        "fecha_emision": ji_fecha_emision,
                        "expediente_ji": ji_exp_ji,
                        "ubicacion_inmueble": ji_ubicacion,
                        "area": ji_area,
                        "coordenadas": ji_coordenadas,
                        "firma_presidente": "Lic. Jhonny Matos. M.A.",
                        "cargo_presidente": "Presidente Fundador",
                        **datos_extras_dict,
                        "profesionales": profesionales_lista,
                        "apoderados": apoderados_lista
                    }

                    archivo_bin = generar_documento_word(ruta_final, contexto_word)

                    if archivo_bin:
                        st.success(f"✅ ¡Documento generado para {res_db.data['nombre_propietario']}!")
                        st.download_button("📥 DESCARGAR DOCUMENTO", archivo_bin, f"{tramite}.docx", use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Error al fabricar: {e}")

        # ==========================================
        # 6. MÓDULO DE MANTENIMIENTO (CON PIN)
        # ==========================================
        st.write("---")
        with st.expander("🛠️ ADMINISTRAR ARCHIVOS DE PLANTILLAS"):
            pin_ingresado = st.text_input("🔑 PIN de Seguridad:", type="password")
            PIN_SECRETO = "1234" # Cambie esto por su PIN real
            
            if pin_ingresado == PIN_SECRETO:
                maint_col1, maint_col2 = st.columns(2)
                import os
                with maint_col1:
                    st.markdown("**📤 Subir o Actualizar**")
                    destino = st.radio("Carpeta:", ["1_mensuras_catastrales", "2_jurisdiccion_original", "3_registro_titulos"])
                    archivo_subido = st.file_uploader("Elija el archivo .docx", type=["docx"])
                    if st.button("💾 Guardar"):
                        if archivo_subido:
                            os.makedirs(f"plantillas_maestras/{destino}", exist_ok=True)
                            with open(f"plantillas_maestras/{destino}/{archivo_subido.name}", "wb") as f:
                                f.write(archivo_subido.getbuffer())
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
                            st.error(f"🗑️ Eliminado.")
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

def vista_registro_maestro():
    st.title("👤 Registro Maestro de Expedientes")
    st.write("Complete los datos del propietario para abrir el expediente.")

    # Formulario simple y efectivo
    with st.container():
        in_np = st.text_input("Nombre del Propietario", key="reg_np_final")
        in_cp = st.text_input("Cédula / Pasaporte", key="reg_cp_final")
        in_exp = st.text_input("Número de Expediente (Opcional)", key="reg_exp_final")

    st.divider()

    if st.button("💾 GUARDAR EXPEDIENTE", type="primary", use_container_width=True):
        if in_np:
            try:
                # Guardamos en su base de datos de Supabase
                datos = {
                    "nombre_propietario": in_np, 
                    "cedula_propietario": in_cp, 
                    "expediente": in_exp
                }
                supabase.table("expedientes_maestros").insert(datos).execute()
                st.success(f"✅ ¡Éxito! El expediente de {in_np} ha sido registrado.")
            except Exception as e:
                st.error(f"❌ Error al conectar con la base de datos: {e}")
        else:
            st.warning("⚠️ El nombre del propietario es obligatorio para el registro.")

# ==========================================
# MOTOR DE NAVEGACIÓN (ESTO CIERRA EL ARCHIVO)
# ==========================================
vistas = {
    "🏠 Mando Central": vista_mando,
    "👤 Registro Maestro": vista_registro_maestro,
    "📁 Archivo Digital": vista_archivo_digital,
    "📄 Plantillas Auto": vista_plantillas_auto,
    "📅 Alertas y Plazos": vista_alertas,
    "💵 Facturación": vista_facturacion,
    "⚙️ Configuración": vista_configuracion
}

if menu in vistas:
    vistas[menu]()
else:
    st.error(f"Error: La sección '{menu}' no existe en el diccionario.")
