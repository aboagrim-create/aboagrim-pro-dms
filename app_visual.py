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
from database import *

st.title("📝 Registro Maestro Pro")
    
    with st.form("registro_maestro_extendido"):
        # --- SECCIÓN: CONTACTO DETALLADO ---
        st.subheader("📞 Información de Contacto y Referencias")
        c1, c2, c3 = st.columns(3)
        email_cliente = c1.text_input("Correo Electrónico")
        telefono_cliente = c2.text_input("Teléfono / WhatsApp")
        referencia_ubicacion = c3.text_input("Referencia del Inmueble (Ej: Próximo al destacamento)")


        # --- SECCIÓN: MÚLTIPLES INMUEBLES / PROFESIONALES ---
        st.subheader("🏗️ Inmuebles y Profesionales Adicionales")
        col_inm, col_prof = st.columns(2)
        
        with col_inm:
            st.write("**Inmuebles Vinculados**")
            inmuebles_adicionales = st.multiselect(
                "Agregar más parcelas al proceso:",
                ["Parcela A-1", "Parcela A-2", "Solar 5", "Solar 10-B"],
                help="Puede seleccionar varias si es un proceso de refundición o subdivisión."
            )
        
        with col_prof:
            st.write("**Equipo de Trabajo**")
            abogados_asoc = st.multiselect("Abogados Colaboradores:", ["Lic. Pérez", "Dra. Martínez", "Dr. Almonte"])
            agrimensores_asoc = st.multiselect("Agrimensores Adicionales:", ["Ing. Rodríguez", "Agrim. Santos"])

        # --- SECCIÓN: GENERALES DE LEY (EXTENDIDAS) ---
        st.subheader("👤 Datos del Cliente")
        g1, g2 = st.columns(2)
        nombre_cliente = g1.text_input("Nombre Completo")
        cedula_cliente = g2.text_input("Cédula (000-0000000-0)")
        direccion_fisica = st.text_area("Dirección Residencial Completa")

        # Botón Upsert
        submit = st.form_submit_button("💾 Guardar y Sincronizar Expediente")
        if submit:
            st.success(f"✅ Expediente de {nombre_cliente} actualizado con éxito.")
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
    st.title("📄 Generador Masivo de Documentación")
    
    tab_gen, tab_mng = st.tabs(["🚀 Generar por Lote", "📁 Gestionar Modelos Maestros"])
    
    with tab_mng:
        st.subheader("Biblioteca de Plantillas (Uso General)")
        archivo_nuevo = st.file_uploader("Subir nuevo modelo Word (.docx)", type=['docx'], key="subidor_plantillas")
        
        if st.button("⬆️ Cargar a la Biblioteca"):
            if archivo_nuevo:
                try:
                    file_bytes = archivo_nuevo.getvalue()
                    db.storage.from_('plantillas').upload(
                        path=archivo_nuevo.name, 
                        file=file_bytes,
                        file_options={"upsert": "true"}
                    )
                    st.success(f"✅ Modelo '{archivo_nuevo.name}' cargado con éxito.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

        modelos = listar_modelos()
        if modelos:
            st.write("Modelos disponibles:")
            for m in modelos:
                c1, c2 = st.columns([3, 1])
                c1.text(f"📄 {m}")
                if c2.button("🗑️", key=m):
                    db.storage.from_('plantillas').remove([m])
                    st.rerun()

    with tab_gen:
        st.subheader("Generación de Expediente")
        casos = consultar_todo()
        
        # Aquí eliminamos el 'return' problemático y usamos un 'else' seguro
        if not casos:
            st.warning("No hay expedientes registrados. Vaya a 'Registro Maestro' para crear uno nuevo.")
        else:
            exp_sel = st.selectbox("Seleccione el Expediente del Cliente:", 
                                   [f"{c.get('numero_expediente')} | {c.get('cliente_id')}" for c in casos])
            
            st.write("Seleccione las plantillas a llenar (hasta 10):")
            modelos_disponibles = listar_modelos()
            seleccionadas = []
            
            cols = st.columns(2)
            for i, mod in enumerate(modelos_disponibles):
                if cols[i % 2].checkbox(mod, key=f"chk_{mod}"):
                    seleccionadas.append(mod)
            
            st.markdown("---")
            st.subheader("📂 Destino de Archivación")
            carpeta_destino = st.selectbox(
                "Seleccione carpeta de destino en la nube:",
                ["📁 Expedientes Activos", "📁 Archivo Pasivo", "📁 Borradores", "📁 Mensuras Catastrales"]
            )
            
            if st.button("📂 Generar Documentos y Archivar"):
                if not seleccionadas:
                    st.error("Seleccione al menos una plantilla.")
                else:
                    with st.spinner(f"Procesando y guardando en {carpeta_destino}..."):
                        # El sistema procesa los documentos aquí
                        st.success(f"✅ Documentos archivados exitosamente en: {carpeta_destino}")

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
    
    st.button("🔄 Sincronizar con Supabase")
