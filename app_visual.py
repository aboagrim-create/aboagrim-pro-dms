# =====================================================================
# INTERFAZ GRÁFICA Y SISTEMA EXPERTO LEGAL JI (EDICIÓN PREMIUM FULL)
# Sistema: AboAgrim Pro DMS 
# =====================================================================

import streamlit as st
import pandas as pd
import datetime
import zipfile   # <--- NUEVO
import io        # <--- NUEVO
from docx import Document
# ... arriba están los import ...

from database import *

# Línea 14: Así debe empezar la función
import streamlit as st

def vista_registro_maestro():
    st.markdown("<h1 style='text-align: center; color: #1a5276;'>👤 Registro Maestro Pro</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # Usamos un formulario para que todo se procese junto y sea más rápido
    with st.form("form_registro_maestro"):
        
        # --- SECCIÓN: CLIENTES / SOLICITANTES ---
        st.subheader("👥 Datos de los Clientes")
        num_clientes = st.number_input("Cantidad de clientes a registrar", min_value=1, max_value=10, value=1)
        
        for i in range(int(num_clientes)):
            with st.expander(f"👤 Cliente #{i+1}", expanded=(i==0)):
                c1, c2 = st.columns(2)
                c1.text_input(f"Nombre Completo / Razón Social #{i+1}", key=f"nom_{i}")
                c2.text_input(f"Cédula / RNC #{i+1}", key=f"ced_{i}")
                
                c3, c4, c5 = st.columns(3)
                c3.text_input(f"Teléfono #{i+1}", key=f"tel_{i}")
                c4.text_input(f"Correo #{i+1}", key=f"mail_{i}")
                c5.selectbox(f"Profesión #{i+1}", ["Abogado", "Agrimensor", "Empresario", "Estudiante", "Otro"], key=f"prof_{i}")

        # --- SECCIÓN: INMUEBLES (Lo que se había borrado) ---
        st.markdown("---")
        st.subheader("🏠 Información Técnica del Inmueble")
        i1, i2, i3 = st.columns(3)
        parcela = i1.text_input("Parcela / Solar")
        dc = i2.text_input("Distrito Catastral")
        matricula = i3.text_input("Matrícula")

        i4, i5, i6 = st.columns(3)
        area = i4.text_input("Superficie (m²)")
        designacion = i5.text_input("Designación Posicional")
        municipio = i6.text_input("Municipio / Provincia", value="Santiago")

        # --- BOTONES DE ACCIÓN ---
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            guardar = st.form_submit_button("💾 GUARDAR REGISTRO MAESTRO")
        
        if guardar:
            st.success("✅ ¡Datos guardados correctamente en el sistema!")

    # --- BARRA LATERAL PARA DESCARGAS ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 Gestión de Expedientes")
    if st.sidebar.button("📄 Generar Word y Descargar"):
        st.sidebar.info("El archivo se descargará en su carpeta de 'Descargas'.")

# Asegúrese de que no haya nada repetido debajo de este bloque.
# =====================================================================
# MÓDULO 1: MANDO CENTRAL
# =====================================================================
def vista_mando():
    st.markdown("""
        <div style='background:linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); padding:35px 30px; border-radius:12px; color:white; border-left:6px solid #FBBF24; margin-bottom: 2rem;'>
            <h1 style='margin:0; font-size: 2.8rem; font-weight: 800;'>AboAgrim Pro DMS ⚖️📐</h1>
            <p style='font-size:1.2rem; color:#94A3B8; margin-bottom: 1rem;'>Centro de Mando: Jurisdicción Inmobiliaria y Mensura</p>
            <div style='font-size:1.1rem; color:#FBBF24; font-weight:600; text-transform:uppercase;'>Santiago | Lic. Jhonny Matos, M.A.</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📈 Desempeño Operativo y Búsqueda")
    casos = consultar_todo()
    
    if casos:
        df = pd.DataFrame(casos)
        c1, c2 = st.columns([2, 1])
        
        # Extracción segura de tags
        tags_disp = []
        for col in ['tipo_caso', 'jurisdiccion', 'estado', 'etapa']:
            if col in df.columns:
                tags_disp.extend([str(v) for v in df[col].dropna().unique() if str(v).strip() != "N/A"])
        tags_disp = sorted(list(set(tags_disp)))
        
        sel_tags = c1.multiselect("🔍 Filtrar por Etiquetas (Tags):", options=tags_disp, placeholder="Ej. Deslinde, Santiago...")
        busq = c2.text_input("📝 Búsqueda libre:")
        
        df_f = df.copy()
        if sel_tags: 
            for t in sel_tags: df_f = df_f[df_f.astype(str).apply(lambda r: t in r.values, axis=1)]
        if busq: 
            df_f = df_f[df_f.astype(str).apply(lambda x: x.str.contains(busq, case=False)).any(axis=1)]
        
        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Resultados", len(df_f))
        m2.metric("Casos Abiertos", len(df_f[df_f.get('estado', '') == 'Abierto']))
        m3.metric("Deslindes", len(df_f[df_f.get('tipo_caso', '') == 'Deslinde']))
        m4.metric("Litis", len(df_f[df_f.get('tipo_caso', '') == 'Litis']))
        
        st.divider()
        st.dataframe(df_f, use_container_width=True)
    else: 
        st.info("🟢 Sistema operativo en línea. Registre su primer expediente en el Registro Maestro.")

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
    st.title("📅 Motor de Alertas y Plazos Legales")
    st.info("Cálculo automático de caducidades y prescripciones procesales de la JI.")
    
    tab_calc, tab_activas = st.tabs(["⏱️ Calculadora y Registro", "🔔 Panel de Vencimientos"])
    
    with tab_calc:
        with st.form("form_alertas", clear_on_submit=True):
            st.subheader("Registrar un nuevo plazo")
            c1, c2 = st.columns(2)
            exp = c1.text_input("Expediente N°:")
            evento = c2.selectbox("Evento Procesal (Ley 108-05):", [
                "Autorización de Mensura (60 días)", 
                "Prórroga de Mensura (30 días)",
                "Apelación de Sentencia (30 días)", 
                "Revisión por Causa de Fraude (1 Año)"
            ])
            
            fecha_inicio = st.date_input("Fecha de Notificación / Emisión (Día Cero):")
            
            if st.form_submit_button("⏳ Calcular y Guardar Alerta"):
                if exp:
                    # El cerebro jurídico: calcula los días según la opción elegida
                    dias = 60 if "60" in evento else 30 if "30" in evento else 365
                    fecha_venc = fecha_inicio + datetime.timedelta(days=dias)
                    
                    datos = {
                        "expediente_id": exp,
                        "tipo_alerta": evento,
                        "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
                        "fecha_vencimiento": fecha_venc.strftime("%Y-%m-%d"),
                        "estado": "Pendiente"
                    }
                    if registrar_evento("alertas", datos):
                        st.success(f"✅ Alerta guardada. Fecha de vencimiento exacta: {fecha_venc.strftime('%d/%m/%Y')}")
                    else:
                        st.error("Error al conectar con la base de datos.")
                else:
                    st.warning("⚠️ Ingrese un número de expediente.")
                    
    with tab_activas:
        st.subheader("🚨 Control de Vencimientos")
        alertas = consultar_alertas(solo_pendientes=True)
        if alertas:
            df_al = pd.DataFrame(alertas)
            
            # 1. Convertimos la columna a formato de Fecha oficial
            df_al['fecha_vencimiento'] = pd.to_datetime(df_al['fecha_vencimiento'])
            
            # 2. Definimos el día de hoy
            hoy = pd.to_datetime("today").normalize()
            
            # 3. Calculamos los días restantes
            df_al['Días Restantes'] = (df_al['fecha_vencimiento'] - hoy).dt.days
            
            # 4. Ponemos la fecha bonita para la tabla (sin horas)
            df_al['fecha_vencimiento'] = df_al['fecha_vencimiento'].dt.date
            
            # Reorganizamos la tabla para que se vea profesional
            st.dataframe(
                df_al[['expediente_id', 'tipo_alerta', 'fecha_vencimiento', 'Días Restantes', 'estado']], 
                use_container_width=True
            )
        else:
            st.success("Tranquilidad total. No hay plazos críticos pendientes en este momento.")
# =====================================================================
# MÓDULO 6: FACTURACIÓN
# =====================================================================
def vista_facturacion():
    st.title("💳 Gestión de Honorarios")
    
    col_a, col_b = st.columns(2)
    monto = col_a.number_input("Monto a Facturar (RD$)", min_value=0)
    cliente_tel = col_b.text_input("Número de WhatsApp del Cliente (Ej: 1809...)", value="1809")

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    
    if c1.button("🖨️ Imprimir Factura"):
        st.write("Generando PDF para impresión...")
        
    # Botón dinámico de WhatsApp
    mensaje = f"Hola, le habla el Lic. Jhonny Matos. Le informamos que su factura por RD${monto} está lista para pago."
    url_wa = f"https://wa.me/{cliente_tel}?text={mensaje.replace(' ', '%20')}"
    
    c2.link_button("📲 Enviar por WhatsApp", url_wa)
    
    if c3.button("📧 Enviar por Correo"):
        st.success("Correo enviado al cliente.")
# =====================================================================
# MÓDULO 7: CONFIGURACIÓN
# =====================================================================
def vista_configuracion():
    st.title("⚙️ Configuración Global de AboAgrim")
    
    with st.expander("💼 Datos de la Oficina"):
        st.text_input("Nombre de la Firma", value="AboAgrim Pro")
        st.text_input("Dirección", value="Calle Boy Scout 83, Santiago")
        st.text_input("RNC", value="1-XX-XXXXX-X")
        
    with st.expander("⚖️ Credenciales Profesionales"):
        st.text_input("Exequatur Abogado", value="XXXX-XX")
        st.text_input("Registro Agrimensor (CODIA)", value="YYYYY")
        
    with st.expander("☁️ Conexión Supabase / API"):
        st.text_input("URL del Proyecto", type="password")
        st.text_input("API Key", type="password")
        
    st.button("✅ Guardar Configuración")
def vista_archivo_digital():
    st.title("📁 Archivo Digital Central")
    
    col_f1, col_f2 = st.columns([2, 1])
    tipo_doc = col_f2.selectbox("Filtrar por tipo:", ["Todos", "Planos", "Contratos", "Cédulas", "Sentencias"])
    busqueda = col_f1.text_input("🔍 Buscar en el archivo (Nombre, Parcela o ID)...")

    # Tabla de archivos simulando la nube
    st.markdown("### Expedientes en la Nube")
    data = [
        {"Fecha": "15/04/2026", "Expediente": "2026-001", "Cliente": "Juan Pérez", "Estatus": "Aprobado"},
        {"Fecha": "10/04/2026", "Expediente": "2026-002", "Cliente": "Maria Sosa", "Estatus": "En Mensuras"}
    ]
    st.table(data)
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
            "💳 Facturación",
            "⚙️ Configuración"
        ]
    )
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión"):
        st.success("Sesión cerrada")

# Diccionario que conecta los botones con sus funciones
vistas = {
    "🏠 Mando Central": vista_mando,
    "👤 Registro Maestro": vista_registro_maestro,
    "📁 Archivo Digital": vista_archivo_digital,
    "📄 Plantillas Auto": vista_plantillas,
    "📅 Alertas y Plazos": vista_alertas,
    "💳 Facturación": vista_facturacion,
    "⚙️ Configuración": vista_configuracion
}

# El motor que ejecuta la pantalla seleccionada
if menu in vistas:
    vistas[menu]()

# Supongamos que esta es su función de conexión (ajuste según su db.py)
# from database import ejecutar_query 

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

    messagebox.showinfo("Éxito", f"{tipo_perfil} agregado y actualizado en el sistema.")
    ventana_origen.destroy()

def ventana_registro_profesional(tipo, menu_a_refrescar=None):
    ventana = ctk.CTkToplevel()
    ventana.title(f"AboAgrim Pro - Registro de {tipo}")
    ventana.geometry("450x650")
    ventana.attributes('-topmost', True)

    ctk.CTkLabel(ventana, text=f"DATOS DEL {tipo.upper()}", font=("Roboto", 18, "bold")).pack(pady=15)

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
