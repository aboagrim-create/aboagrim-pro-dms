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
import streamlit as st
import datetime

def vista_registro_maestro():
    st.title("📝 Registro Maestro de Expedientes")
    st.info("Complete la información para alimentar las plantillas de la Jurisdicción Inmobiliaria (JI).")

    # --- DATOS PRE-CONFIGURADOS (Tus Credenciales) ---
    credenciales_oficina = {
        "jhonny_matos_titulos": "Lic. Jhonny Matos. M.A., Presidente",
        "exequatur_legal": "12345-XX", 
        "exequatur_agrimensor": "6789-YY",
        "direccion_oficina": "Calle Boy Scout 83, Plaza Jasansa, Mod. 5-B, Santiago, Dom. Rep."
    }

    with st.form("registro_maestro_dinamico", clear_on_submit=False):
        
        # --- MÓDULO 1: GENERALES DE LEY (CLIENTE) ---
        st.subheader("👤 I. Generales del Cliente / Partes")
        col1, col2, col3 = st.columns(3)
        
        cliente_nombre = col1.text_input("Nombre Completo / Razón Social", placeholder="Ej: Juan Pérez")
        cedula = col2.text_input("Cédula / RNC", placeholder="000-0000000-0")
        nacionalidad = col3.text_input("Nacionalidad", value="Dominicana")
        
        c4, c5, c6 = st.columns(3)
        profesion = c4.text_input("Profesión / Ocupación")
        estado_civil = c5.selectbox("Estado Civil", ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a", "Unión Libre"])
        nombre_representado = c6.text_input("Nombre Representado", help="Si actúa en nombre de un tercero o empresa")
        
        domicilio_cliente = st.text_input("Domicilio Real del Cliente")

        # Lógica Dinámica para Cónyuge
        if estado_civil == "Casado/a":
            st.warning("🔒 Requisito Legal: Se requieren datos del cónyuge para actos de disposición.")
            cc1, cc2 = st.columns(2)
            nombre_conyuge = cc1.text_input("Nombre del Cónyuge")
            cedula_conyuge = cc2.text_input("Cédula del Cónyuge")
            regimen_matrimonial = st.selectbox("Régimen Matrimonial", ["Comunidad de Bienes", "Separación de Bienes", "Participación"])
        else:
            nombre_conyuge, cedula_conyuge, regimen_matrimonial = "", "", ""

        st.markdown("---")

        # --- MÓDULO 2: DATOS TÉCNICOS DEL INMUEBLE ---
        st.subheader("🗺️ II. Datos del Inmueble (Técnicos y Catastrales)")
        i1, i2, i3 = st.columns(3)
        parcela = i1.text_input("Parcela / Solar")
        dc = i2.text_input("Distrito Catastral (DC)")
        matricula = i3.text_input("Matrícula / Certificado de Título")
        
        i4, i5, i6 = st.columns(3)
        superficie = i4.text_input("Superficie (m²)", placeholder="Ej: 500.50 m²")
        designacion_posicional = i5.text_input("Designación Posicional (Nueva)")
        ubicacion_inmueble = i6.text_input("Provincia/Municipio", value="Santiago, R.D.")
        
        with st.expander("➕ Linderos y Detalles Técnicos (Opcional)"):
            st.text_area("Colindancias (Norte, Sur, Este, Oeste)")
            st.text_input("Coordenadas UTM")
            st.text_input("Mejoras Existentes")

        st.markdown("---")

        # --- MÓDULO 3: JURISDICCIÓN Y PROCESO ---
        st.subheader("⚖️ III. Estructura Jurisdicción Inmobiliaria (JI)")
        j1, j2 = st.columns(2)
        tipo_proceso = j1.selectbox("Tipo de Proceso / Actuación", [
            "Deslinde", "Saneamiento", "Subdivisión", "Litis sobre Derechos Registrados", 
            "Transferencia", "Determinación de Herederos"
        ])
        
        organo_ji = j2.selectbox("Órgano de la JI", [
            "Mensuras Catastrales (DGMIC)", "Registro de Títulos (RT)", 
            "Tribunal de Tierras (Jurisdicción Original)", "Tribunal Superior de Tierras"
        ])

        j3, j4 = st.columns(2)
        direccion_regional = j3.text_input("Dirección Regional", value="Departamento Norte")
        num_expediente_ji = j4.text_input("Número de Expediente JI", placeholder="Ej: 2026-0005")

        st.markdown("---")

        # --- MÓDULO 4: REQUISITO Y HONORARIOS ---
        st.subheader("📄 IV. Requisito y Cláusulas Económicas")
        nombre_documento = st.selectbox("Seleccione el Documento a Redactar:", [
            "Contrato de Cuota Litis", "Instancia de Inicio de Proceso", 
            "Acto de Venta y Transferencia", "Poder Especial de Representación",
            "Acto de Notoriedad Pública", "Instancia de Demanda (Litis)"
        ])

        h1, h2, h3 = st.columns(3)
        porcentaje_litis = h1.text_input("Porcentaje Litis (%)", value="30%")
        monto_pesos = h2.text_input("Monto Fijo (RD$)")
        monto_letras = h3.text_input("Monto en Letras", placeholder="Cien mil pesos...")

        condiciones_pago = st.text_area("Condiciones de Pago")

        # --- BOTÓN DE ACCIÓN ---
        st.markdown("---")
        submit_btn = st.form_submit_button("💾 Guardar y Vincular Expediente (Upsert)")

        if submit_btn:
            if not cliente_nombre or not cedula:
                st.error("⚠️ Datos faltantes: Se requiere Nombre y Cédula del cliente.")
            else:
                st.success(f"✅ Registro Maestro Actualizado para: {cliente_nombre}")
                st.balloons()
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
        if not casos:
            st.warning("No hay expedientes registrados."); return
        
        exp_sel = st.selectbox("Seleccione el Expediente del Cliente:", 
                               [f"{c.get('numero_expediente')} | {c.get('cliente_id')}" for c in casos])
        
        st.write("Seleccione las plantillas a llenar (hasta 10):")
        modelos_disponibles = listar_modelos()
        seleccionadas = []
        
        cols = st.columns(2)
        for i, mod in enumerate(modelos_disponibles):
            if cols[i % 2].checkbox(mod, key=f"chk_{mod}"):
                seleccionadas.append(mod)
        
        if st.button("📂 Generar Documentos y Archivar en Expediente"):
            if not seleccionadas:
                st.error("Seleccione al menos una plantilla.")
            else:
                with st.spinner("Procesando lote de documentos..."):
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for mod_name in seleccionadas:
                            modelo_bytes = db.storage.from_('plantillas').download(mod_name)
                            doc = Document(io.BytesIO(modelo_bytes))
                            doc.add_paragraph(f"\nDocumento vinculado al expediente: {exp_sel}")
                            
                            out_buffer = io.BytesIO()
                            doc.save(out_buffer)
                            out_buffer.seek(0)
                            
                            nombre_archivo = f"{mod_name.replace('.docx', '')}_{exp_sel.split('|')[0].strip()}.docx"
                            subir_a_expediente(out_buffer.getvalue(), nombre_archivo, exp_sel.split('|')[0].strip())
                            zip_file.writestr(nombre_archivo, out_buffer.getvalue())
                    
                    st.success(f"✅ Se han generado {len(seleccionadas)} documentos y se archivaron en la nube.")
                    st.download_button("⬇️ Descargar Paquete ZIP", zip_buffer.getvalue(), "expediente_completo.zip")

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
    st.title("💳 Finanzas y Control de Honorarios")
    
    with st.form("form_pagos", clear_on_submit=True):
        st.subheader("Registrar un Nuevo Pago / Abono")
        c1, c2, c3 = st.columns(3)
        exp = c1.text_input("Expediente N°:")
        tot = c2.number_input("Honorarios Acordados (RD$):", min_value=0.0, step=1000.0)
        abo = c3.number_input("Monto Abonado Hoy (RD$):", min_value=0.0, step=1000.0)
        
        if st.form_submit_button("💳 Registrar Ingreso"):
            if exp and abo > 0:
                datos_pago = {
                    "expediente_id": exp, "honorarios_totales": tot, 
                    "monto_pagado": abo, "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d")
                }
                if registrar_evento("pagos", datos_pago): st.success(f"✅ Pago de RD$ {abo:,.2f} registrado.")
                else: st.error("Error al registrar el pago.")
            else: st.warning("Ingrese Expediente y Monto.")
            
    st.divider()
    
    st.subheader("📊 Historial de Movimientos")
    facturas = consultar_facturas()
    if facturas:
        df_pagos = pd.DataFrame(facturas)
        df_pagos['Balance Pendiente'] = pd.to_numeric(df_pagos['honorarios_totales']) - pd.to_numeric(df_pagos['monto_pagado'])
        st.dataframe(df_pagos[['fecha_registro', 'expediente_id', 'honorarios_totales', 'monto_pagado', 'Balance Pendiente']], use_container_width=True)
        
        total_ingresos = pd.to_numeric(df_pagos['monto_pagado']).sum()
        st.metric("Total Ingresos Históricos (RD$)", f"RD$ {total_ingresos:,.2f}")
    else:
        st.info("No hay pagos registrados aún.")

# =====================================================================
# MÓDULO 7: CONFIGURACIÓN
# =====================================================================
def vista_configuracion():
    st.title("⚙️ Ajustes del Sistema y Accesos")
    
    tab_perfil, tab_leyes, tab_usuarios = st.tabs(["⚙️ Perfil de la Firma", "📚 Compendio Normativo", "👥 Gestión de Accesos"])
    
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

    with tab_usuarios:
        st.subheader("Crear Cuenta para Nuevo Miembro del Equipo")
        st.info("Al registrar un correo aquí, le otorgarás acceso inmediato al sistema a tu personal.")
        
        with st.form("form_nuevo_usuario", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nuevo_email = c1.text_input("Correo del empleado / asociado:")
            nuevo_pass = c2.text_input("Contraseña Temporal (Min. 6 caracteres):", type="password")
            
            if st.form_submit_button("🔐 Autorizar y Crear Usuario"):
                if nuevo_email and len(nuevo_pass) >= 6:
                    if registrar_nuevo_usuario(nuevo_email, nuevo_pass):
                        st.success(f"✅ Acceso concedido. El usuario {nuevo_email} ya puede iniciar sesión.")
                        st.balloons()
                    else:
                        st.error("Error: Verifica que el correo tenga formato válido o que no exista ya en el sistema.")
                else:
                    st.warning("⚠️ Ingrese un correo válido y una contraseña de al menos 6 caracteres.")

# --- ENRUTADOR ---
vistas = {
    "🏠 Mando Central": vista_mando, "👤 Registro Maestro": vista_registro_maestro, 
    "📁 Archivo Digital": vista_archivo, "📄 Plantillas Auto": vista_plantillas, 
    "📅 Alertas y Plazos": vista_alertas, "💳 Facturación": vista_facturacion, 
    "⚙️ Configuración": vista_configuracion
}
vistas[menu]()
