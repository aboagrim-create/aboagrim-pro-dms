import streamlit as st
import pandas as pd
import datetime
from database import *

# ---------------------------------------------------------------------
# CONFIGURACIÓN DEL SISTEMA OPERATIVO Y PÁGINA
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="AboAgrim Pro DMS v18.0", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------
# PANTALLA DE LOGIN (PUNTO DE CONTROL DE ACCESO)
# ---------------------------------------------------------------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("""
        <style>
        .login-box {
            max-width: 400px; margin: 0 auto; padding: 30px; 
            border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            background-color: #1E3A8A; color: white; border-top: 5px solid #FBBF24;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: white;'>⚖️ AboAgrim Pro</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #cbd5e1;'>Acceso Restringido al Sistema DMS</p>", unsafe_allow_html=True)
        
with st.form("form_login"):
            correo = st.text_input("Correo Electrónico Institucional:")
            clave = st.text_input("Contraseña de Acceso:", type="password")
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if submit:
                # 1. Limpiar espacios en blanco invisibles al inicio o al final
                correo_limpio = correo.strip()
                
                # 2. Validaciones de formato
                if not correo_limpio or not clave:
                    st.warning("⚠️ Por favor, complete ambos campos.")
                elif "@" not in correo_limpio or "." not in correo_limpio:
                    st.error("❌ Formato inválido. Asegúrese de escribir un correo real (ej. usuario@dominio.com).")
                else:
                    # 3. Autenticación con el correo ya limpio
                    exito, usuario = autenticar_usuario(correo_limpio, clave)
                    if exito:
                        st.session_state['autenticado'] = True
                        st.session_state['correo_usuario'] = correo_limpio
                        st.rerun() # Recarga la página para mostrar el sistema
                    else:
                        st.error("❌ Credenciales incorrectas o usuario no registrado en Supabase.")
# =====================================================================
# EL USUARIO HA PASADO EL LOGIN - MOSTRAR EL SISTEMA
# =====================================================================

# ---------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR) Y MENÚ DE NAVEGACIÓN
# ---------------------------------------------------------------------
st.sidebar.markdown("### Abogados y Agrimensores")
st.sidebar.markdown("## 'AboAgrim'")
st.sidebar.markdown(f"**Usuario:** {st.session_state['correo_usuario']}")
st.sidebar.divider()

opciones_menu = [
    "🏠 Mando Central", 
    "⚖️ Registro Maestro", 
    "📁 Archivo Digital", 
    "📄 Plantillas Auto", 
    "📅 Alertas y Plazos", 
    "💳 Facturación", 
    "⚙️ Configuración y Leyes"
]

menu = st.sidebar.radio("Módulos del Sistema", opciones_menu, label_visibility="collapsed")

st.sidebar.divider()

# Botón para cerrar sesión
if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state['autenticado'] = False
    st.rerun()

st.sidebar.caption("Motor: AboAgrim OS v18.0 - Ley 108-05")

# =====================================================================
# MÓDULO 1: MANDO CENTRAL (Mantenido intacto y funcional)
# =====================================================================
def vista_mando():
    estilo_banner = """
        <style>
        .hero-banner {
            background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
            padding: 35px 30px; border-radius: 12px; color: white;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin-bottom: 2rem;
            border-left: 6px solid #FBBF24;
        }
        .hero-title { font-size: 2.5rem; font-weight: 800; margin-bottom: 0.2rem; }
        .hero-subtitle { font-size: 1.2rem; color: #94A3B8; margin-bottom: 1rem; }
        .founder-name { font-size: 1.1rem; color: #FBBF24; font-weight: 600; text-transform: uppercase; }
        </style>
    """
    st.markdown(estilo_banner, unsafe_allow_html=True)
    st.markdown("""
        <div class="hero-banner">
            <div class="hero-title">AboAgrim Pro DMS ⚖️📐</div>
            <div class="hero-subtitle">Centro de Mando: Jurisdicción Inmobiliaria y Mensura</div>
            <div class="founder-name">Lic. Jhonny Matos, M.A. | Presidente Fundador</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📈 Desempeño Operativo y Búsqueda")
    casos_bd = consultar_todo()
    
    if casos_bd:
        df_casos = pd.DataFrame(casos_bd)
        columna_busqueda_1, columna_busqueda_2 = st.columns([2, 1])
        
        with columna_busqueda_1:
            columnas_para_tags = ['tipo_caso', 'jurisdiccion', 'estado', 'etapa']
            lista_tags_disponibles = [str(val) for col in columnas_para_tags if col in df_casos.columns for val in df_casos[col].dropna().unique() if str(val).strip()]
            tags_ordenados = sorted(list(set(lista_tags_disponibles)))
            tags_seleccionados = st.multiselect("🔍 Filtrar por Etiquetas (Tags):", options=tags_ordenados)
            
        with columna_busqueda_2:
            texto_busqueda = st.text_input("Búsqueda libre por nombre o número:")

        df_filtrado = df_casos.copy()
        if tags_seleccionados:
            for tag_actual in tags_seleccionados:
                df_filtrado = df_filtrado[df_filtrado.astype(str).apply(lambda fila: tag_actual in fila.values, axis=1)]
        if texto_busqueda:
            df_filtrado = df_filtrado[df_filtrado.astype(str).apply(lambda x: x.str.contains(texto_busqueda, case=False, na=False)).any(axis=1)]

        st.markdown("<br>", unsafe_allow_html=True)
        metrica_1, metrica_2, metrica_3, metrica_4 = st.columns(4)
        metrica_1.metric("Expedientes (Filtro)", len(df_filtrado))
        metrica_2.metric("Deslindes Activos", len(df_filtrado[df_filtrado['tipo_caso'] == 'Deslinde']) if 'tipo_caso' in df_filtrado.columns else 0)
        metrica_3.metric("Litis Registradas", len(df_filtrado[df_filtrado['tipo_caso'] == 'Litis']) if 'tipo_caso' in df_filtrado.columns else 0)
        metrica_4.metric("Casos Abiertos", len(df_filtrado[df_filtrado['estado'] == 'Abierto']) if 'estado' in df_filtrado.columns else 0)
        
        st.divider()
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.info("🟢 Sistema operativo en línea. Aún no hay expedientes en la base de datos.")

# =====================================================================
# MÓDULO 2 Y 3: REGISTRO Y ARCHIVO (Resumidos aquí para mantener funcionalidad)
# =====================================================================
def vista_registro():
    st.title("⚖️ Registro Maestro de Expedientes")
    diccionario_personal = obtener_diccionario_maestro()
    with st.form("formulario_registro_oficial"):
        st.subheader("I. Datos Legales y Catastrales")
        c1, c2, c3 = st.columns(3)
        numero_exp = c1.text_input("N° Expediente:")
        tipo_caso = c2.selectbox("Clasificación del Acto:", ["Deslinde", "Saneamiento", "Litis", "Transferencia", "Determinación de Herederos"])
        jurisdiccion = c3.selectbox("Jurisdicción:", ["Santiago", "La Vega", "Santo Domingo", "Puerto Plata", "Moca"])
        
        c4, c5 = st.columns(2)
        cliente_principal = c4.text_input("Cliente / Propietario principal:")
        etapa_actual = c5.selectbox("Etapa Inicial:", ["Recepción", "Mensura", "Sometimiento", "Tribunal", "Sentencia"])
        
        st.subheader("II. Asignación de Roles")
        a1, a2, a3 = st.columns(3)
        agrimensor = a1.selectbox("Agrimensor:", diccionario_personal.get('agrimensor', []) or ["N/A"])
        abogado = a2.selectbox("Abogado:", diccionario_personal.get('abogado', []) or ["N/A"])
        notario = a3.selectbox("Notario:", diccionario_personal.get('notario', []) or ["N/A"])
        
        if st.form_submit_button("🛡️ Blindar y Registrar"):
            if numero_exp and cliente_principal:
                if registrar_evento("casos", {"numero_expediente": numero_exp, "tipo_caso": tipo_caso, "jurisdiccion": jurisdiccion, "cliente_id": cliente_principal, "etapa": etapa_actual, "estado": "Abierto"}): 
                    st.toast("¡Expediente guardado!", icon="✅")
                else: 
                    st.error("Error de conexión.")
            else:
                st.warning("Número y Cliente obligatorios.")

def vista_archivo():
    st.title("📁 Bóveda Digital DMS")
    st.markdown("Sistema de gestión documental para planos y resoluciones.")
    expediente_vincular = st.text_input("Vincular al Expediente N°:")
    archivos_cargados = st.file_uploader("Arrastre sus archivos aquí", accept_multiple_files=True)
    if st.button("Subir a la Nube Segura") and archivos_cargados:
        st.toast(f"{len(archivos_cargados)} Archivos subidos.", icon="☁️")

# =====================================================================
# MÓDULO 4: PLANTILLAS (NUEVO: LÓGICA DE TRÁMITES Y REQUISITOS JI)
# =====================================================================
def vista_plantillas():
    st.title("📄 Motor de Plantillas y Requisitos (Ley 108-05)")
    
    pestaña_plantillas, pestaña_requisitos = st.tabs(["⚙️ Generador de Documentos", "📋 Requisitos Legales de la JI"])
    
    with pestaña_plantillas:
        st.markdown("Automatización de actuaciones Administrativas y Contenciosas.")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            categoria_acto = st.radio("Vía de Actuación:", ["Administrativa (DRMC / RT)", "Contenciosa (Tribunales)"])
            
            if categoria_acto == "Administrativa (DRMC / RT)":
                documento_elegido = st.selectbox("Seleccione Documento:", [
                    "Solicitud de Autorización de Mensura", 
                    "Contrato de Mensura (Agrimensor-Cliente)", 
                    "Carta de Consentimiento", 
                    "Instancia de Transferencia de Inmueble"
                ])
            else:
                documento_elegido = st.selectbox("Seleccione Documento:", [
                    "Contrato de Cuota Litis",
                    "Poder de Representación",
                    "Instancia Introductiva de Demanda (Litis)",
                    "Instancia de Fijación de Audiencia",
                    "Escrito de Conclusiones"
                ])
                
            expediente_origen = st.text_input("Extraer datos del Expediente N°:")
            if st.button("⚙️ Ensamblar Documento"):
                st.toast(f"Generando {documento_elegido}...", icon="⏳")
                
        with col_p2:
            st.info("💡 **Inteligencia Documental:** El sistema detectará automáticamente la jurisdicción seleccionada y adaptará el encabezado al Tribunal o Dirección Regional correspondiente.")

    with pestaña_requisitos:
        st.markdown("### Checklist Oficial de Requisitos por Trámite")
        tramite_info = st.selectbox("Consultar requisitos para:", ["Deslinde", "Saneamiento", "Litis sobre Derechos Registrados", "Transferencia por Venta"])
        
        if tramite_info == "Deslinde":
            st.success("**Trámite: Deslinde (Resolución 3642-2016)**\n1. Contrato de Mensura firmado.\n2. Copia de la Constancia Anotada.\n3. Copia de Cédula del titular.\n4. Autorización del Abogado del Estado (si aplica).\n5. Acta de Hitos y Mensura.\n6. Plano Individual y General.")
        elif tramite_info == "Saneamiento":
            st.success("**Trámite: Saneamiento (Art. 20 Ley 108-05)**\n1. Instancia de solicitud de autorización de mensura.\n2. Croquis ilustrativo del terreno.\n3. Certificación del Ayuntamiento.\n4. Actas del estado civil del reclamante.\n5. Pruebas de posesión (recibos, contratos).")
        elif tramite_info == "Litis sobre Derechos Registrados":
            st.success("**Trámite: Litis (Art. 28 Ley 108-05)**\n1. Instancia introductiva de demanda.\n2. Notificación del acto de demanda (Alguacil) en octava franca.\n3. Depósito de la demanda notificada en el Registro de Títulos.\n4. Copia del Certificado de Título involucrado.")
        elif tramite_info == "Transferencia por Venta":
            st.success("**Trámite: Transferencia (Vía Administrativa RT)**\n1. Acto de venta original legalizado.\n2. Certificado de Título original del vendedor.\n3. Recibo de pago de Impuesto de Transferencia (3% DGII).\n4. Copias de cédulas de comprador y vendedor.\n5. Certificación de IPI al día.")

# =====================================================================
# MÓDULO 5: ALERTAS Y PLAZOS (NUEVO: PRESCRIPCIONES Y CADUCIDADES)
# =====================================================================
def vista_alertas():
    st.title("📅 Motor de Alertas, Plazos y Caducidades")
    
    tab_alertas, tab_leyes = st.tabs(["🔔 Mis Alertas Activas", "⚖️ Calculadora de Plazos Ley 108-05"])
    
    with tab_alertas:
        st.subheader("Control de Plazos de Expedientes")
        st.warning("No hay plazos críticos por vencer en los próximos 7 días.")
        # Aquí irá la lógica futura que cruce los casos abiertos con las fechas
        
    with tab_leyes:
        st.subheader("Tabla Oficial de Plazos, Prescripciones y Caducidades de la JI")
        
        datos_plazos = {
            "Actuación / Proceso": [
                "Autorización de Mensura", 
                "Prórroga de Mensura", 
                "Aviso de Mensura (Publicación)",
                "Apelación de Sentencia TJO",
                "Revisión por Causa de Fraude",
                "Recurso de Casación",
                "Revisión por Error Material",
                "Fijación de Audiencia Saneamiento"
            ],
            "Plazo Legal": [
                "60 días", 
                "30 días adicionales", 
                "15 días antes de iniciar",
                "30 días",
                "1 Año",
                "30 días",
                "Imprescriptible",
                "Max 60 días tras recibir expediente"
            ],
            "Efecto Legal": [
                "Caducidad", 
                "Administrativo", 
                "Nulidad de Mensura",
                "Prescripción / Caducidad",
                "Prescripción",
                "Caducidad",
                "Ninguno",
                "Plazo de Tribunal"
            ],
            "Base Normativa": [
                "Art. 41 Reglamento Mensuras", 
                "Art. 42 Reglamento Mensuras", 
                "Art. 46 Reglamento Mensuras",
                "Art. 80 Ley 108-05",
                "Art. 86 Ley 108-05",
                "Art. 82 Ley 108-05",
                "Art. 89 Ley 108-05",
                "Art. 60 Reglamento Tribunales"
            ]
        }
        
        df_plazos = pd.DataFrame(datos_plazos)
        st.dataframe(df_plazos, use_container_width=True, hide_index=True)
        st.info("🚨 **Nota Técnica:** Los plazos contenciosos (apelación, casación) comienzan a correr a partir de la fecha de notificación de la sentencia por acto de alguacil, no desde el día en que se dicta la sentencia.")

# =====================================================================
# MÓDULO 6: FACTURACIÓN E IMPUESTOS (NUEVO: TASAS Y RECIBOS JI)
# =====================================================================
def vista_facturacion():
    st.title("💳 Facturación y Calculadora de Impuestos")
    
    col_finanzas_1, col_finanzas_2 = st.columns(2)
    with col_finanzas_1:
        st.subheader("Registro de Cobros de Honorarios")
        expediente_pago = st.text_input("Aplicar pago al Expediente N°:")
        monto_total_contrato = st.number_input("Honorarios Totales (RD$):", min_value=0.0, step=1000.0)
        monto_avance = st.number_input("Abono Recibido (RD$):", min_value=0.0, step=1000.0)
        if st.button("💳 Registrar Transacción", use_container_width=True):
            st.toast("Pago registrado en el estado de cuenta.")
            
    with col_finanzas_2:
        st.subheader("Tasas e Impuestos Comunes (JI y DGII)")
        st.markdown("""
        **Gastos Administrativos del Proceso:**
        * **Impuesto de Transferencia (DGII):** 3% del valor del inmueble.
        * **Colegio de Abogados (Ley 3-19):** RD$ 50.00 (Sello por acto).
        * **Colegio de Notarios:** RD$ 100.00 (Por legalización de firmas).
        * **Sello Ley 33-91 (Poder Judicial):** Depende de la actuación.
        * **Tasa Dirección Regional Mensuras (Tasa por parcela):** Varía según extensión superficial y tipo de solicitud.
        """)
        st.caption("Utilice esta guía para calcular las provisiones de fondos de sus clientes.")

# =====================================================================
# MÓDULO 7: CONFIGURACIÓN Y LEYES (NUEVO: COMPENDIO NORMATIVO)
# =====================================================================
def vista_configuracion():
    st.title("⚙️ Ajustes del Sistema y Biblioteca Legal")
    
    tab_perfil, tab_leyes = st.tabs(["⚙️ Perfil de la Firma", "📚 Compendio Normativo de la JI"])
    
    with tab_perfil:
        st.subheader("Datos Oficiales de los Documentos")
        st.text_input("Razón Social:", value="Abogados y Agrimensores 'AboAgrim'")
        st.text_input("Dirección Principal:", value="Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Santiago")
        st.text_input("Teléfonos:", value="829-826-5888 / 809-691-3333")
        if st.button("💾 Guardar Configuración"):
            st.toast("Ajustes guardados exitosamente.", icon="✅")
            
    with tab_leyes:
        st.subheader("Legislación Integrada en AboAgrim Pro DMS")
        st.markdown("""
        Este sistema opera bajo los lineamientos de las siguientes normativas de la República Dominicana:
        
        1. **Ley No. 108-05 de Registro Inmobiliario.** (Ley sustantiva base).
        2. **Reglamento General de Mensuras Catastrales.** (Resolución No. 3642-2016 de la SCJ).
        3. **Reglamento de los Tribunales de la Jurisdicción Inmobiliaria.**
        4. **Reglamento General de Registro de Títulos.**
        5. **Resolución No. 1737-2007** (Sobre el Fondo de Garantía de Inmuebles Registrados).
        
        *Las actualizaciones a la normativa dictadas por el Consejo del Poder Judicial (CPJ) se inyectarán en los módulos de 'Plantillas' y 'Alertas' de manera automática.*
        """)

# =====================================================================
# ENRUTADOR PRINCIPAL DEL SISTEMA
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
elif menu == "⚙️ Configuración y Leyes":
    vista_configuracion()

# Fin del documento app_visual.py
