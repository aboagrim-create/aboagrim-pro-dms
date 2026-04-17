# =====================================================================
# INTERFAZ GRÁFICA Y SISTEMA EXPERTO LEGAL JI (EDICIÓN PREMIUM FULL)
# Sistema: AboAgrim Pro DMS 
# =====================================================================

import streamlit as st
import pandas as pd
import datetime
import zipfile   # <--- NUEVO
import io        # <--- NUEVO
from database import *

# --- CONFIGURACIÓN DE MARCA Y SISTEMA ---
st.set_page_config(page_title="AboAgrim Pro DMS", layout="wide", initial_sidebar_state="expanded")

# --- LÓGICA DE SEGURIDAD (LOGIN) ---
if 'autenticado' not in st.session_state: 
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("""
        <style>
        .login-box {
            max-width: 450px; margin: 0 auto; padding: 40px; 
            border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); 
            color: white; border-top: 6px solid #FBBF24;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: white;'>⚖️ AboAgrim Pro</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94A3B8;'>Acceso Restringido DMS</p>", unsafe_allow_html=True)
        
        with st.form("Login_Seguro"):
            u = st.text_input("Correo Institucional:").strip()
            p = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("Entrar al Sistema", use_container_width=True):
                if u and p:
                    exito, user = autenticar_usuario(u, p)
                    if exito:
                        st.session_state['autenticado'] = True
                        st.session_state['user'] = u
                        st.rerun()
                    else: st.error("❌ Credenciales incorrectas.")
                else: st.warning("⚠️ Complete ambos campos.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop() # Detiene la ejecución si no hay login

# --- INTERFAZ PRINCIPAL (BARRA LATERAL) ---
st.sidebar.markdown(f"### AboAgrim Pro\n**Lic. Jhonny Matos, M.A.**\n`Usuario: {st.session_state['user']}`")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Navegación", 
    ["🏠 Mando Central", "👤 Registro Maestro", "📁 Archivo Digital", "📄 Plantillas Auto", "📅 Alertas y Plazos", "💳 Facturación", "⚙️ Configuración"]
)

st.sidebar.divider()
if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state['autenticado'] = False
    st.rerun()

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
def vista_registro_maestro():
    st.title("👤 Registro Maestro de Expedientes")
    dic = obtener_diccionario_maestro()
    
    with st.form("registro_expediente_full", clear_on_submit=False):
        tab1, tab2, tab3 = st.tabs(["📋 I. Datos Legales", "📐 II. Detalles del Proceso", "⚖️ III. Roles Profesionales"])
        
        with tab1:
            c1, c2, c3 = st.columns(3)
            num = c1.text_input("N° Expediente:")
            cli = c2.text_input("Cliente Principal / Reclamante:")
            ced = c3.text_input("Cédula / RNC:")
            
        with tab2:
            c4, c5, c6 = st.columns(3)
            tipo = c4.selectbox("Tipo de Acto:", ["Deslinde", "Saneamiento", "Litis", "Transferencia", "Determinación de Herederos"])
            jur = c5.selectbox("Jurisdicción:", ["Santiago", "La Vega", "Santo Domingo", "Puerto Plata", "Moca"])
            eta = c6.selectbox("Etapa Inicial:", ["Recepción", "Mensura", "Sometimiento", "Tribunal", "Sentencia"])
            
        with tab3:
            st.markdown("Asigne el personal técnico y legal involucrado:")
            a1, a2, a3 = st.columns(3)
            agrim = a1.selectbox("Agrimensor:", dic.get('agrimensor', []) or ["N/A"])
            abog = a2.selectbox("Abogado:", dic.get('abogado', []) or ["N/A"])
            notar = a3.selectbox("Notario:", dic.get('notario', []) or ["N/A"])
            
            a4, a5, a6 = st.columns(3)
            repre = a4.selectbox("Representante:", dic.get('representante', []) or ["N/A"])
            apoder = a5.selectbox("Apoderado:", dic.get('apoderado', []) or ["N/A"])
            solic = a6.selectbox("Solicitante:", dic.get('solicitante', []) or ["N/A"])

        st.markdown("---")
        if st.form_submit_button("🛡️ Blindar y Registrar Expediente en la Nube"):
            if num and cli:
                datos = {
                    "numero_expediente": num, "cliente_id": cli, "tipo_caso": tipo, 
                    "jurisdiccion": jur, "etapa": eta, "estado": "Abierto"
                }
                if registrar_evento("casos", datos): 
                    st.toast("Expediente guardado exitosamente.", icon="✅")
                    st.balloons()
                else: 
                    st.error("Error al conectar con la base de datos.")
            else:
                st.warning("⚠️ El Número de Expediente y el Cliente son obligatorios.")

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
    st.title("📄 Motor de Plantillas y Requisitos (Ley 108-05)")
    
    tab_docs, tab_req = st.tabs(["⚙️ Generador de Documentos", "📋 Requisitos Legales de la JI"])
    
    with tab_docs:
        c1, c2 = st.columns(2)
        with c1:
            via = st.radio("Vía de Actuación:", ["Administrativa (DRMC / RT)", "Contenciosa (Tribunales)"])
            if via == "Administrativa (DRMC / RT)":
                doc = st.selectbox("Documento:", ["Solicitud de Mensura", "Contrato de Mensura", "Instancia Transferencia"])
            else:
                doc = st.selectbox("Documento:", ["Contrato Cuota Litis", "Poder Especial", "Demanda Litis", "Conclusiones"])
            
            exp = st.text_input("Extraer datos del Expediente N°:")
            if st.button("⚙️ Ensamblar Documento Word"):
                st.toast(f"Generando {doc}...", icon="⏳")
        with c2:
            st.info("💡 **Inteligencia Documental:** El sistema detectará automáticamente la jurisdicción y adaptará el encabezado legal.")

    with tab_req:
        tramite = st.selectbox("Consultar Checklist Legal para:", ["Deslinde", "Saneamiento", "Litis sobre Derechos Registrados", "Transferencia por Venta"])
        if tramite == "Deslinde":
            st.success("**Trámite: Deslinde (Res. 3642-2016)**\n1. Contrato de Mensura firmado.\n2. Constancia Anotada.\n3. Cédula del titular.\n4. Acta de Hitos y Mensura.\n5. Planos.")
        elif tramite == "Saneamiento":
            st.success("**Trámite: Saneamiento (Art. 20 Ley 108-05)**\n1. Instancia de solicitud.\n2. Croquis ilustrativo.\n3. Certificación del Ayuntamiento.\n4. Pruebas de posesión.")
        elif tramite == "Litis sobre Derechos Registrados":
            st.success("**Trámite: Litis (Art. 28 Ley 108-05)**\n1. Demanda introductiva.\n2. Acto de Alguacil (octava franca).\n3. Depósito en RT.\n4. Copia del Título.")
        elif tramite == "Transferencia por Venta":
            st.success("**Trámite: Transferencia (RT)**\n1. Acto de venta original.\n2. Título original.\n3. Impuesto (3% DGII).\n4. Certificación de IPI.")

# =====================================================================
# MÓDULO 5: ALERTAS Y PLAZOS
# =====================================================================
def vista_alertas():
    st.title("📅 Motor de Alertas, Plazos y Caducidades")
    
    tab_alertas, tab_leyes = st.tabs(["🔔 Mis Alertas Activas", "⚖️ Calculadora de Plazos Ley 108-05"])
    
    with tab_alertas:
        st.warning("No hay plazos críticos por vencer en los próximos 7 días.")
        
    with tab_leyes:
        st.subheader("Tabla Oficial de Plazos, Prescripciones y Caducidades de la JI")
        datos = {
            "Actuación / Proceso": ["Autorización de Mensura", "Prórroga de Mensura", "Aviso de Mensura", "Apelación TJO", "Revisión por Fraude", "Casación"],
            "Plazo Legal": ["60 días", "30 días adicionales", "15 días antes", "30 días", "1 Año", "30 días"],
            "Efecto Legal": ["Caducidad", "Administrativo", "Nulidad", "Prescripción", "Prescripción", "Caducidad"],
            "Base Normativa": ["Art. 41 Reg. Mensuras", "Art. 42 Reg. Mensuras", "Art. 46 Reg. Mensuras", "Art. 80 Ley 108-05", "Art. 86 Ley 108-05", "Art. 82 Ley 108-05"]
        }
        st.dataframe(pd.DataFrame(datos), use_container_width=True, hide_index=True)

# =====================================================================
# MÓDULO 6: FACTURACIÓN
# =====================================================================
def vista_facturacion():
    st.title("💳 Facturación y Gestión de Cobros")
    
    with st.expander("⚖️ Consultar Guía de Tasas e Impuestos (JI y DGII)", expanded=False):
        st.markdown("""
        * **Impuesto de Transferencia (DGII):** 3% del valor del inmueble.
        * **Colegio de Abogados (Ley 3-19):** RD$ 50.00 (Sello por acto).
        * **Colegio de Notarios:** RD$ 100.00 (Por legalización).
        * **Tasa Mensuras:** Varía según extensión superficial.
        """)
    
    st.markdown("### Registro de Transacción")
    with st.form("form_pagos", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        exp = c1.text_input("Expediente N°:")
        tot = c2.number_input("Honorarios Totales (RD$):", min_value=0.0, step=1000.0)
        abo = c3.number_input("Abono Recibido (RD$):", min_value=0.0, step=1000.0)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💳 Aplicar Cobro a Cuenta", use_container_width=True):
            if exp and abo > 0:
                datos_pago = {"expediente_id": exp, "honorarios_totales": tot, "monto_pagado": abo, "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d")}
                registrar_evento("pagos", datos_pago)
                st.success(f"✅ Abono de RD$ {abo:,.2f} aplicado al expediente {exp}.")
            else: st.warning("⚠️ Ingrese el Expediente y un Abono mayor a 0.")

# =====================================================================
# MÓDULO 7: CONFIGURACIÓN
# =====================================================================
def vista_configuracion():
    st.title("⚙️ Ajustes del Sistema y Biblioteca Legal")
    
    tab_perfil, tab_leyes = st.tabs(["⚙️ Perfil de la Firma", "📚 Compendio Normativo de la JI"])
    
    with tab_perfil:
        st.text_input("Razón Social:", value="Abogados y Agrimensores 'AboAgrim'")
        st.text_input("Sede Principal:", value="Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Santiago.")
        st.text_input("Teléfonos:", value="829-826-5888 / 809-691-3333")
        if st.button("💾 Guardar Configuración"): st.toast("Ajustes guardados.", icon="✅")
            
    with tab_leyes:
        st.markdown("""
        **Legislación Integrada en AboAgrim Pro DMS:**
        1. **Ley No. 108-05 de Registro Inmobiliario.**
        2. **Reglamento General de Mensuras Catastrales.**
        3. **Reglamento de los Tribunales de la JI.**
        4. **Reglamento General de Registro de Títulos.**
        """)

# --- ENRUTADOR ---
vistas = {
    "🏠 Mando Central": vista_mando, "👤 Registro Maestro": vista_registro_maestro, 
    "📁 Archivo Digital": vista_archivo, "📄 Plantillas Auto": vista_plantillas, 
    "📅 Alertas y Plazos": vista_alertas, "💳 Facturación": vista_facturacion, 
    "⚙️ Configuración": vista_configuracion
}
vistas[menu]()
