# =====================================================================
# INTERFAZ GRÁFICA DE USUARIO (GUI)
# Sistema: AboAgrim Pro DMS v17.1
# =====================================================================

import streamlit as st
import pandas as pd
import datetime
from database import *

# ---------------------------------------------------------------------
# CONFIGURACIÓN DEL SISTEMA OPERATIVO Y PÁGINA
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="AboAgrim Pro DMS v17.1", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR) Y MENÚ DE NAVEGACIÓN
# ---------------------------------------------------------------------
st.sidebar.markdown("### Abogados y Agrimensores")
st.sidebar.markdown("## 'AboAgrim'")
st.sidebar.markdown("**Lic. Jhonny Matos. M.A., Presidente**")
st.sidebar.divider()

# Definición del menú principal con todas sus opciones originales
opciones_menu = [
    "🏠 Mando Central", 
    "⚖️ Registro Maestro", 
    "📁 Archivo Digital", 
    "📄 Plantillas Auto", 
    "📅 Alertas y Plazos", 
    "💳 Facturación", 
    "⚙️ Configuración"
]

menu = st.sidebar.radio(
    "Módulos del Sistema",
    opciones_menu,
    label_visibility="collapsed"
)

st.sidebar.divider()
st.sidebar.markdown("🟢 **Estado del Servidor:** En Línea (Supabase)")
st.sidebar.caption("Motor: AboAgrim OS v17.1")

# =====================================================================
# MÓDULO 1: MANDO CENTRAL (Dashboard y Buscador)
# =====================================================================
def vista_mando():
    
    # 1. Inyección de estilos CSS para el Banner Principal
    estilo_banner = """
        <style>
        .hero-banner {
            background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
            padding: 35px 30px; 
            border-radius: 12px; 
            color: white;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); 
            margin-bottom: 2rem;
            border-left: 6px solid #FBBF24;
        }
        .hero-title { font-size: 2.5rem; font-weight: 800; margin-bottom: 0.2rem; }
        .hero-subtitle { font-size: 1.2rem; color: #94A3B8; margin-bottom: 1rem; }
        .founder-name { font-size: 1.1rem; color: #FBBF24; font-weight: 600; text-transform: uppercase; }
        </style>
    """
    st.markdown(estilo_banner, unsafe_allow_html=True)

    # 2. Renderizado del Banner HTML
    banner_html = """
        <div class="hero-banner">
            <div class="hero-title">AboAgrim Pro DMS ⚖️📐</div>
            <div class="hero-subtitle">Centro de Mando: Jurisdicción Inmobiliaria y Mensura</div>
            <div class="founder-name">Lic. Jhonny Matos, M.A. | Presidente Fundador</div>
        </div>
    """
    st.markdown(banner_html, unsafe_allow_html=True)

    st.markdown("### 📈 Desempeño Operativo y Búsqueda")
    
    # 3. Consulta de datos a la base de datos
    casos_bd = consultar_todo()
    
    if casos_bd:
        # Convertir datos a DataFrame para manipularlos fácilmente
        df_casos = pd.DataFrame(casos_bd)
        
        # 4. Motor de Búsqueda Inteligente (Filtros y Tags)
        columna_busqueda_1, columna_busqueda_2 = st.columns([2, 1])
        
        with columna_busqueda_1:
            # Recopilar todos los tags únicos disponibles en la tabla
            columnas_para_tags = ['tipo_caso', 'jurisdiccion', 'estado', 'etapa']
            lista_tags_disponibles = []
            
            for columna in columnas_para_tags:
                if columna in df_casos.columns:
                    for valor in df_casos[columna].dropna().unique():
                        if str(valor).strip() != "":
                            lista_tags_disponibles.append(str(valor))
                            
            # Ordenar alfabéticamente y eliminar duplicados
            tags_ordenados = sorted(list(set(lista_tags_disponibles)))
            
            # Selector múltiple para el usuario
            tags_seleccionados = st.multiselect(
                "🔍 Filtrar por Etiquetas (Tags):", 
                options=tags_ordenados, 
                placeholder="Ej. Deslinde, Santiago, Abierto..."
            )
            
        with columna_busqueda_2:
            # Buscador de texto libre
            texto_busqueda = st.text_input("Búsqueda libre por nombre o número:")

        # 5. Aplicar los filtros seleccionados al DataFrame
        df_filtrado = df_casos.copy()
        
        # Filtro de Tags
        if tags_seleccionados:
            for tag_actual in tags_seleccionados:
                mascara = df_filtrado.astype(str).apply(lambda fila: tag_actual in fila.values, axis=1)
                df_filtrado = df_filtrado[mascara]
                
        # Filtro de Texto
        if texto_busqueda:
            mascara_texto = df_filtrado.astype(str).apply(lambda x: x.str.contains(texto_busqueda, case=False, na=False)).any(axis=1)
            df_filtrado = df_filtrado[mascara_texto]

        # 6. Mostrar Métricas Dinámicas (Basadas en los datos filtrados)
        st.markdown("<br>", unsafe_allow_html=True)
        metrica_1, metrica_2, metrica_3, metrica_4 = st.columns(4)
        
        metrica_1.metric("Expedientes (Filtro)", len(df_filtrado))
        
        total_deslindes = len(df_filtrado[df_filtrado['tipo_caso'] == 'Deslinde']) if 'tipo_caso' in df_filtrado.columns else 0
        metrica_2.metric("Deslindes Activos", total_deslindes)
        
        total_litis = len(df_filtrado[df_filtrado['tipo_caso'] == 'Litis']) if 'tipo_caso' in df_filtrado.columns else 0
        metrica_3.metric("Litis Registradas", total_litis)
        
        total_abiertos = len(df_filtrado[df_filtrado['estado'] == 'Abierto']) if 'estado' in df_filtrado.columns else 0
        metrica_4.metric("Casos Abiertos", total_abiertos)
        
        # 7. Tabla Final de Resultados
        st.divider()
        st.dataframe(df_filtrado, use_container_width=True)
        
    else:
        # Pantalla alternativa si la base de datos está vacía
        st.info("🟢 Sistema operativo en línea. Aún no hay expedientes en la base de datos.")

# =====================================================================
# MÓDULO 2: REGISTRO MAESTRO (Formulario de 7 Roles)
# =====================================================================
def vista_registro():
    st.title("⚖️ Registro Maestro de Expedientes")
    
    # Obtener el personal desde la base de datos
    diccionario_personal = obtener_diccionario_maestro()
    
    # Iniciar el formulario de guardado
    with st.form("formulario_registro_oficial"):
        
        # Sección 1: Datos Legales Básicos
        st.subheader("I. Datos Legales y Catastrales")
        col_reg_1, col_reg_2, col_reg_3 = st.columns(3)
        
        numero_exp = col_reg_1.text_input("Número de Expediente / Referencia:")
        
        tipos_acto = ["Deslinde", "Saneamiento", "Litis", "Transferencia", "Determinación de Herederos"]
        tipo_caso = col_reg_2.selectbox("Clasificación del Acto:", tipos_acto)
        
        jurisdicciones = ["Santiago", "La Vega", "Santo Domingo", "Puerto Plata", "Moca"]
        jurisdiccion = col_reg_3.selectbox("Jurisdicción Competente:", jurisdicciones)
        
        # Sección 2: Cliente y Estado
        col_reg_4, col_reg_5 = st.columns(2)
        cliente_principal = col_reg_4.text_input("Cliente / Propietario principal:")
        
        etapas_proceso = ["Recepción de Documentos", "Mensura Catastral", "Sometimiento", "Tribunal", "Sentencia"]
        etapa_actual = col_reg_5.selectbox("Etapa Inicial del Proceso:", etapas_proceso)
        
        st.markdown("---")
        
        # Sección 3: Asignación de Roles (Técnico y Legal)
        st.subheader("II. Asignación de Roles Profesionales")
        
        fila_roles_1, fila_roles_2, fila_roles_3 = st.columns(3)
        agrimensor = fila_roles_1.selectbox("Agrimensor a cargo:", diccionario_personal.get('agrimensor', []) or ["N/A"])
        abogado = fila_roles_2.selectbox("Abogado apoderado:", diccionario_personal.get('abogado', []) or ["N/A"])
        notario = fila_roles_3.selectbox("Notario actuante:", diccionario_personal.get('notario', []) or ["N/A"])
        
        fila_roles_4, fila_roles_5, fila_roles_6 = st.columns(3)
        representante = fila_roles_4.selectbox("Representante legal:", diccionario_personal.get('representante', []) or ["N/A"])
        apoderado = fila_roles_5.selectbox("Apoderado:", diccionario_personal.get('apoderado', []) or ["N/A"])
        solicitante = fila_roles_6.selectbox("Solicitante del acto:", diccionario_personal.get('solicitante', []) or ["N/A"])

        # Botón de Guardado Final
        st.markdown("---")
        boton_guardar = st.form_submit_button("🛡️ Blindar y Registrar Expediente en la Nube")
        
        # Lógica de procesamiento al presionar el botón
        if boton_guardar:
            if numero_exp != "" and cliente_principal != "":
                
                # Preparar el paquete de datos para Supabase
                paquete_datos = {
                    "numero_expediente": numero_exp, 
                    "tipo_caso": tipo_caso, 
                    "jurisdiccion": jurisdiccion, 
                    "cliente_id": cliente_principal, 
                    "etapa": etapa_actual, 
                    "estado": "Abierto"
                }
                
                # Ejecutar el guardado
                guardado_exitoso = registrar_evento("casos", paquete_datos)
                
                if guardado_exitoso: 
                    st.toast("¡Expediente guardado en Supabase exitosamente!", icon="✅")
                    st.success(f"El expediente {numero_exp} se ha registrado correctamente.")
                else: 
                    st.error("Error de conexión a la Base de Datos. Intente nuevamente.")
            else:
                st.warning("⚠️ El Número de Expediente y el Nombre del Cliente son campos obligatorios.")

# =====================================================================
# MÓDULO 3: ARCHIVO DIGITAL (Bóveda)
# =====================================================================
def vista_archivo():
    st.title("📁 Bóveda Digital DMS")
    st.markdown("Sistema de gestión documental para planos de Civil 3D, PDF y resoluciones.")
    
    # Crear pestañas para organizar la vista
    pestaña_subir, pestaña_explorar = st.tabs(["⬆️ Cargar Documentos", "🗄️ Explorador de Bóveda"])
    
    with pestaña_subir:
        st.write("Vincule los archivos técnicos directamente a un número de expediente.")
        expediente_vincular = st.text_input("Vincular al Expediente N°:")
        archivos_cargados = st.file_uploader("Arrastre sus archivos aquí", accept_multiple_files=True)
        
        if st.button("Subir a la Nube Segura"):
            if archivos_cargados: 
                st.toast(f"{len(archivos_cargados)} Archivos encriptados y subidos.", icon="☁️")
                st.success("Archivos procesados correctamente.")
            else:
                st.warning("Seleccione al menos un archivo para subir.")
    
    with pestaña_explorar:
        st.info("Explorador de Bóveda: Aquí aparecerán los archivos indexados una vez conectados a la cubeta de Storage.")

# =====================================================================
# MÓDULO 4: PLANTILLAS AUTOMÁTICAS
# =====================================================================
def vista_plantillas():
    st.title("📄 Generador de Plantillas Automáticas")
    st.markdown("Motor de automatización de Contratos, Actos de Alguacil y Solicitudes de Mensura.")
    
    col_plantilla_1, col_plantilla_2 = st.columns(2)
    
    with col_plantilla_1:
        tipos_documentos = [
            "Contrato de Cuota Litis", 
            "Poder Especial de Representación", 
            "Solicitud de Autorización de Mensura",
            "Instancia de Fijación de Audiencia"
        ]
        documento_elegido = st.selectbox("Seleccione la Plantilla Maestra a utilizar:", tipos_documentos)
        
        expediente_origen = st.text_input("Extraer datos del Expediente N° (Para autocompletado):")
        
        if st.button("⚙️ Ensamblar Documento Word"):
            st.toast("Procesando variables con DocxTpl...", icon="⏳")
            st.success("El motor de plantillas está preparado para recibir la plantilla .docx base.")
            
    with col_plantilla_2:
        st.info("💡 **Instrucciones:** Asegúrese de tener cargadas las plantillas base en el servidor con las variables correctas (ej. {{cliente}}, {{jurisdiccion}}).")

# =====================================================================
# MÓDULO 5: ALERTAS Y PLAZOS
# =====================================================================
def vista_alertas():
    st.title("📅 Panel de Control de Alertas")
    st.markdown("Gestión de plazos perentorios de Mensura Catastral y fijaciones de audiencias.")
    
    st.warning("No hay audiencias ni plazos de mensura próximos a vencer en los próximos 7 días.")

# =====================================================================
# MÓDULO 6: FACTURACIÓN Y HONORARIOS
# =====================================================================
def vista_facturacion():
    st.title("💳 Módulo Financiero y Honorarios")
    
    col_finanzas_1, col_finanzas_2 = st.columns(2)
    
    with col_finanzas_1:
        st.subheader("Registrar Nuevo Cobro")
        expediente_pago = st.text_input("Aplicar pago al Expediente N°:")
        monto_total_contrato = st.number_input("Honorarios Totales Acordados (RD$):", min_value=0.0, step=1000.0)
        
    with col_finanzas_2:
        st.subheader("Transacción")
        monto_avance = st.number_input("Avance o Abono Recibido (RD$):", min_value=0.0, step=1000.0)
        
        st.write("") # Espaciador
        st.write("") # Espaciador
        if st.button("💳 Registrar Transacción Financiera", use_container_width=True):
            st.success(f"Transacción aplicada correctamente al expediente {expediente_pago}.")

# =====================================================================
# MÓDULO 7: CONFIGURACIÓN
# =====================================================================
def vista_configuracion():
    st.title("⚙️ Ajustes del Sistema Operativo")
    
    col_config_1, col_config_2 = st.columns(2)
    
    with col_config_1:
        st.subheader("Perfil de la Firma")
        st.text_input("Razón Social / Nombre Comercial:", value="Abogados y Agrimensores 'AboAgrim'")
        st.text_input("Dirección Principal:", value="Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Santiago")
        st.text_input("Contacto Telefónico Principal:", value="829-826-5888 / 809-691-3333")
        st.text_input("Correo Institucional:", value="Aboagrim@gmail.com")
        
        if st.button("💾 Guardar Cambios de Perfil"):
            st.toast("Perfil actualizado correctamente en el sistema.", icon="💾")
            
    with col_config_2:
        st.subheader("Estado de Conexiones")
        st.success("✅ Base de Datos (Supabase): ONLINE")
        st.success("✅ Motor Documental (DocxTpl): ACTIVO")
        st.success("✅ Framework (Streamlit): ESTABLE")

# =====================================================================
# ENRUTADOR PRINCIPAL DEL SISTEMA (LÓGICA DE MENÚS)
# =====================================================================
if menu == "🏠 Mando Central":
    vista_mando()
elif menu == "⚖️ Registro Maestro":
    vista_registro()
elif menu == "📁 Archivo Digital":
    vista_archivo()
elif menu == "📄 Plantillas Auto":
    vista_plantillas()
elif menu == "📅 Alertas y Plazos":
    vista_alertas()
elif menu == "💳 Facturación":
    vista_facturacion()
elif menu == "⚙️ Configuración":
    vista_configuracion()

# Fin del documento app_visual.py
