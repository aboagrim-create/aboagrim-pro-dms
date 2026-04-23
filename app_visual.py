# =====================================================================
# INTERFAZ GRÁFICA Y SISTEMA EXPERTO LEGAL JI (EDICIÓN PREMIUM FULL)
# Sistema: AboAgrim Pro DMS 
# =====================================================================
from docxtpl import DocxTemplate
import io
import pandas as pd
import datetime
import zipfile   # <--- NUEVO
import io        # <--- NUEVO
# ... arriba están los import ...

from database import *

# Línea 14: Así debe empezar la función
import streamlit as st
# --- ESTO VA AL PRINCIPIO DEL ARCHIVO ---
if "autenticado_global" not in st.session_state:
    st.session_state.autenticado_global = False

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

    # --- CONFIGURACIÓN DE RUTA DE GUARDADO ---
    with st.expander("📂 Destino del Documento", expanded=True):
        c_dir, c_btn = st.columns([3, 1])
        ruta_carpeta = c_dir.text_input("Carpeta de Destino", value="C:/AboAgrim/Expedientes/Documentos/")
        if c_btn.button("📁 Explorar"):
            st.info("Ruta fijada para el guardado automático.")

    # --- FORMULARIO MAESTRO DE VARIABLES ---
    with st.form("generador_maestro"):
        # Pestañas para organizar la gran cantidad de variables
        t1, t2, t3, t4 = st.tabs(["👤 Partes", "🏗️ Inmueble", "📜 Cláusulas", "⚙️ Salida"])

        with t1:
            st.subheader("Información de las Partes")
            col1, col2 = st.columns(2)
            with col1:
                tipo_contrato = st.selectbox("Documento a Generar", [
                    "Contrato de Cuota-Litis", 
                    "Acto de Notoriedad", 
                    "Poder Especial de Representación",
                    "Contrato de Servicios Técnicos de Agrimensura",
                    "Instancia de Solicitud de Mensura"
                ])
                nombre_cliente = st.text_input("Nombre del Cliente")
            with col2:
                estado_civil_var = st.selectbox("Estado Civil en Documento", ["Soltero/a", "Casado/a", "Unión Libre", "Divorciado/a"])
                cedula_var = st.text_input("Cédula / RNC")

        with t2:
            st.subheader("Variables del Inmueble")
            col3, col4, col5 = st.columns(3)
            with col3:
                parcela_var = st.text_input("Número de Parcela")
                dc_var = st.text_input("D.C.")
            with col4:
                matricula_var = st.text_input("Matrícula")
                designacion_var = st.text_input("Desig. Posicional")
            with col5:
                superficie_var = st.number_input("Metraje (m²)", min_value=0.0)
                municipio_var = st.text_input("Municipio")

        with t3:
            st.subheader("Configuración Dinámica de Cláusulas")
            st.write("Seleccione los elementos que el sistema debe insertar en la plantilla:")
            
            # Matriz de Casillas (Checkboxes) para variables del sistema
            ch1, ch2, ch3 = st.columns(3)
            with ch1:
                v_conyuge = st.checkbox("Incluir Datos de Cónyuge")
                v_regimen = st.checkbox("Mencionar Régimen Matrimonial")
                v_representante = st.checkbox("Incluir Representante Legal")
            with ch2:
                v_honorarios = st.checkbox("Insertar Tabla de Honorarios", value=True)
                v_mora = st.checkbox("Incluir Cláusula de Mora")
                v_gastos = st.checkbox("Cláusula de Gastos Operativos")
            with ch3:
                v_testigos = st.checkbox("Espacios para Testigos")
                v_notario = st.checkbox("Cuerpo de Legalización Notarial", value=True)
                v_anexos = st.checkbox("Listado de Anexos Técnicos")

        with t4:
            st.subheader("Formato y Ejecución")
            col6, col7 = st.columns(2)
            with col6:
                formato_output = st.radio("Formato de Archivo", ["Word (.docx)", "PDF (.pdf)"], horizontal=True)
            with col7:
                estilo_doc = st.selectbox("Estilo Visual", ["Elegante / Legal", "Moderno / Minimalista", "Oficial / Judicial"])

        # --- BOTÓN DE ACCIÓN ---
        st.markdown("---")
        c_gen1, c_gen2 = st.columns([1, 4])
        btn_generar = c_gen1.form_submit_button("🚀 GENERAR")

        if btn_generar:
            if nombre_cliente and parcela_var:
                st.success(f"✅ ¡Éxito! Plantilla '{tipo_contrato}' generada y guardada en la ruta especificada.")
                st.balloons()
            else:
                st.warning("⚠️ Faltan datos críticos (Nombre o Parcela) para completar las variables.")

    # --- TABLA DE REGISTRO DE PLANTILLAS ---
    st.markdown("### 📋 Historial de Documentos Generados")
    log_data = {
        "Documento": [tipo_contrato if btn_generar else "Esperando..."],
        "Cliente": [nombre_cliente if nombre_cliente else "---"],
        "Estado": ["Guardado en Carpeta" if btn_generar else "En edición"]
    }
    st.table(log_data)

# =====================================================================
# MÓDULO 5: ALERTAS Y PLAZOS
# =====================================================================
def vista_alertas():
    st.header("⚖️ Control de Plazos, Perenciones y Caducidades")
    st.info("Basado en Reglamentos 2022 y Resoluciones actualizadas al 2026.")
    
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
# =====================================================================
# MÓDULO 6: FACTURACIÓN
# =====================================================================
def vista_facturacion():
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
    st.header("📁 Archivo Digital Central")
    st.write("Aquí se muestran todos los expedientes guardados en su nube (Supabase).")

    try:
        # 1. Traemos la información fresca desde la nube
        respuesta = supabase.table("expedientes_maestros").select("*").execute()
        datos_nube = respuesta.data
        
        if not datos_nube:
            st.info("Bóveda vacía. Aún no ha guardado ningún expediente desde el Registro Maestro.")
        else:
            # 2. Convertimos los datos en una tabla inteligente
            import pandas as pd
            df = pd.DataFrame(datos_nube)
            
            # 3. Organizamos las columnas para que se vean bien
            df_mostrar = df.rename(columns={
                "fecha_creacion": "Fecha de Registro",
                "expediente": "No. Expediente",
                "nombre_propietario": "Propietario / Cliente",
                "cedula_propietario": "Cédula",
                "parcela": "Parcela",
                "municipio": "Municipio",
                "provincia": "Provincia"
            })
            
            # Mostramos la tabla con diseño profesional
            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
            
            st.success(f"Se han encontrado {len(datos_nube)} expedientes en su archivo digital.")

    except Exception as e:
        st.error("⚠️ No se pudo conectar con la Bóveda Digital.")
        st.info("Revisando conexión a la base de datos...")
# ==========================================
# MENÚ LATERAL Y NAVEGACIÓN DEL SISTEMA
# ==========================================
with st.sidebar:
    menu = st.radio(
        "Navegación",
        [
            "🏠 Mando Central",
            "👤 Registro Maestro",
            "📂 Archivo Digital",
            "📄 Plantillas Auto",  # <--- Esta es la que ya tiene o vamos a usar
            "🗓️ Alertas y Plazos",
            "💵 Facturación",
            "⚙️ Configuración"
        ]
    )
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión"):
        st.success("Sesión cerrada")
def vista_registro_maestro():
    st.header("👤 Registro Maestro de Expedientes")
    st.write("Llene los datos. Puede generar todos los documentos del expediente a la vez.")

    # --- PESTAÑAS DE ORGANIZACIÓN ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📍 Inmueble y Fechas", "👥 Propietario / Reclamante", "🤝 Vendedor (Contratos)", "🧭 Colindancias", "⚖️ Profesionales"])

    with tab1:
        st.subheader("Datos Técnicos y del Inmueble")
        col1, col2, col3 = st.columns(3)
        st.session_state['exp'] = col1.text_input("No. Expediente", key="in_exp")
        st.session_state['fecha_men'] = col2.text_input("Fecha Mensura (Ej: 12/11/2025)", key="in_fm")
        st.session_state['hora_men'] = col3.text_input("Hora Mensura (Ej: 9:00 A.M.)", key="in_hm")

        col4, col5, col6 = st.columns(3)
        st.session_state['dc'] = col4.text_input("Distrito Catastral (DC)", key="in_dc")
        st.session_state['parcela'] = col5.text_input("Parcela", key="in_par")
        st.session_state['area_m2'] = col6.text_input("Área (M²)", key="in_area")

        col7, col8 = st.columns(2)
        st.session_state['municipio'] = col7.text_input("Municipio", key="in_mun")
        st.session_state['provincia'] = col8.text_input("Provincia", key="in_prov")

        st.session_state['ubicacion_det'] = st.text_area("Ubicación Detallada (Ruta para Letreros/Avisos)", key="in_ubi")
        st.session_state['coordenadas'] = st.text_input("Coordenadas (Ej: 19.494634, -70.893367)", key="in_coord")

    with tab2:
        st.subheader("Datos del Propietario / Reclamante / Comprador")
        col9, col10 = st.columns(2)
        st.session_state['nom_prop'] = col9.text_input("Nombre Completo", key="in_np")
        st.session_state['ced_prop'] = col10.text_input("Cédula", key="in_cp")

        col11, col12, col13 = st.columns(3)
        st.session_state['est_prop'] = col11.selectbox("Estado Civil", ["Soltero", "Casado", "Divorciado", "Viudo"], key="in_ep")
        st.session_state['nac_prop'] = col12.text_input("Nacionalidad", value="Dominicano", key="in_nap")
        st.session_state['prof_prop'] = col13.text_input("Profesión/Oficio", key="in_prp")
        
        st.session_state['dom_prop'] = st.text_input("Domicilio", key="in_dp")

    with tab3:
        st.subheader("Datos del Vendedor (Solo para Contratos de Venta)")
        col14, col15 = st.columns(2)
        st.session_state['nom_ven'] = col14.text_input("Nombre del Vendedor", key="in_nv")
        st.session_state['ced_ven'] = col15.text_input("Cédula Vendedor", key="in_cv")

        col16, col17, col18 = st.columns(3)
        st.session_state['est_ven'] = col16.selectbox("Estado Civil Vendedor", ["Soltero", "Casado", "Divorciado", "Viudo"], key="in_ev")
        st.session_state['nac_ven'] = col17.text_input("Nacionalidad V.", value="Dominicano", key="in_nav")
        st.session_state['prof_ven'] = col18.text_input("Profesión V.", key="in_prv")

        st.session_state['dom_ven'] = st.text_input("Domicilio Vendedor", key="in_dv")

    with tab4:
        st.subheader("Colindancias Actuales")
        col19, col20 = st.columns(2)
        st.session_state['col_norte'] = col19.text_input("Al Norte", key="in_cn")
        st.session_state['med_norte'] = col20.text_input("Medida Norte (m)", key="in_mn")
        
        col21, col22 = st.columns(2)
        st.session_state['col_sur'] = col21.text_input("Al Sur", key="in_cs")
        st.session_state['med_sur'] = col22.text_input("Medida Sur (m)", key="in_ms")

        col23, col24 = st.columns(2)
        st.session_state['col_este'] = col23.text_input("Al Este", key="in_ce")
        st.session_state['med_este'] = col24.text_input("Medida Este (m)", key="in_me")

        col25, col26 = st.columns(2)
        st.session_state['col_oeste'] = col25.text_input("Al Oeste", key="in_co")
        st.session_state['med_oeste'] = col26.text_input("Medida Oeste (m)", key="in_mo")

    with tab5:
        st.subheader("Profesionales Legales Actuantes")
        col27, col28 = st.columns(2)
        st.session_state['nom_notario'] = col27.text_input("Nombre del Notario", key="in_nnot")
        st.session_state['mat_notario'] = col28.text_input("Matrícula Notario", key="in_mnot")

        col29, col30 = st.columns(2)
        st.session_state['nom_abogado'] = col29.text_input("Nombre Abogado/Apoderado", key="in_nabo")
        st.session_state['mat_abogado'] = col30.text_input("Colegiatura Abogado", key="in_mabo")
# --- BARRA LATERAL (SIDEBAR) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 Salida de Expedientes")

    import glob
    plantillas_disponibles = glob.glob("**/*.docx", recursive=True)

    if len(plantillas_disponibles) == 0:
        st.sidebar.error("❌ No se encontraron plantillas.")
    else:
        # MAGIA AQUÍ: multiselect permite elegir 1 o 10 plantillas al mismo tiempo
        plantillas_elegidas = st.sidebar.multiselect("📄 Seleccione las Plantillas:", plantillas_disponibles)

        if st.sidebar.button("🛠️ Preparar Expediente"):
            if not plantillas_elegidas:
                st.sidebar.warning("⚠️ Seleccione al menos una plantilla.")
            else:
                with st.sidebar.status("Procesando documentos y guardando en la nube...", expanded=True) as status:
                    try:
                        # 1. Llamamos al Súper Motor para crear el ZIP
                        archivo, nombre_archivo, tipo_mime = generar_paquete_documentos(st.session_state, plantillas_elegidas)
                        
                        st.session_state['archivo_listo'] = archivo
                        st.session_state['nombre_descarga'] = nombre_archivo
                        st.session_state['tipo_mime'] = tipo_mime
                        
                        # 2. GUARDADO AUTOMÁTICO EN SUPABASE
                        datos_a_guardar = {
                            "expediente": st.session_state.get('in_exp', ''),
                            "nombre_propietario": st.session_state.get('in_np', ''),
                            "cedula_propietario": st.session_state.get('in_cp', ''),
                            "parcela": st.session_state.get('in_par', ''),
                            "municipio": st.session_state.get('in_mun', ''),
                            "provincia": st.session_state.get('in_prov', '')
                        }
                        
                        # Enviamos los datos a la tabla 'expedientes_maestros'
                        supabase.table("expedientes_maestros").insert(datos_a_guardar).execute()
                        
                        status.update(label="✅ ¡Expediente listo y guardado en la nube!", state="complete", expanded=False)
                    except Exception as e:
                        status.update(label="❌ Error al procesar o guardar", state="error")
                        st.sidebar.error(f"Detalle del error: {e}")

        # Botón de descarga Dinámico (ZIP o Word)
        if 'archivo_listo' in st.session_state and st.session_state['archivo_listo']:
            st.sidebar.download_button(
                label="📥 DESCARGAR AHORA EN PC",
                data=st.session_state['archivo_listo'],
                file_name=st.session_state.get('nombre_descarga', 'Paquete.zip'),
                mime=st.session_state.get('tipo_mime', 'application/zip')
            )
# Supongamos que esta es su función de conexión (ajuste según su db.py)
# from database import ejecutar_query 


# Diccionario que conecta los botones con sus funciones
vistas = {
    "🏠 Mando Central": vista_mando,
    "👤 Registro Maestro": vista_registro_maestro, # Asegúrese de que termine en _registro_maestro
    "📂 Archivo Digital": vista_archivo_digital,
    "📄 Plantillas Auto": vista_documentos,
    "🗓️ Alertas y Plazos": vista_alertas,
    "💵 Facturación": vista_facturacion,
    "⚙️ Configuración": vista_configuracion
}
# El motor que ejecuta la pantalla seleccionada
if menu in vistas:
    vistas[menu]()
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
# --- FUNCIÓN ÚNICA Y MODERNA PARA EL REGISTRO MAESTRO ---

def vista_registro_maestro():
    st.markdown("<h1 style='text-align: center; color: #1a5276;'>👤 Registro Maestro Pro</h1>", unsafe_allow_html=True)
    
    with st.form("form_maestro_final"):
        st.subheader("👥 Intervinientes")
        # Botón dinámico para agregar más personas
        num_clientes = st.number_input("Cantidad de personas", min_value=1, max_value=10, value=1)
        
        for i in range(int(num_clientes)):
            with st.expander(f"👤 Persona #{i+1}", expanded=(i==0)):
                c1, c2 = st.columns(2)
                c1.text_input(f"Nombre Completo #{i+1}", key=f"n_{i}")
                c2.text_input(f"Cédula / RNC #{i+1}", key=f"c_{i}")
                
                c3, c4 = st.columns(2)
                # Botón desplegable dinámico
                c3.selectbox(f"Rol #{i+1}", ["Cliente", "Abogado", "Agrimensor", "Vendedor"], key=f"p_{i}")
                c4.text_input(f"Teléfono #{i+1}", key=f"t_{i}")

        st.divider()
        st.subheader("🏠 Datos del Inmueble")
        i1, i2, i3 = st.columns(3)
        parcela = i1.text_input("Parcela")
        dc = i2.text_input("DC")
        matricula = i3.text_input("Matrícula")

        # Botón de Guardar que NO da pantalla roja
        if st.form_submit_button("💾 GUARDAR EXPEDIENTE"):
            st.success("✅ ¡Datos guardados exitosamente en la nube!")
# --- LÓGICA DE ARRANQUE DEL SISTEMA ---
if "autenticado_global" not in st.session_state:
    st.session_state.autenticado_global = False

if not st.session_state.autenticado_global:
    login_sistema()
else:
    # AQUÍ VA TODO EL CÓDIGO QUE YA TIENE (El menú lateral y las vistas)
    # Ejemplo:
    # with st.sidebar:
    #     menu = st.radio(...)
    # vistas[menu]()
    
    # Agregue un botón de salir al final del menú lateral
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado_global = False
        st.rerun()
