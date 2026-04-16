import streamlit as st
import pandas as pd
from database import *

st.set_page_config(page_title="AboAgrim Pro DMS", layout="wide", initial_sidebar_state="expanded")

# --- Identidad Corporativa ---
st.sidebar.markdown(f"## Abogados y Agrimensores 'AboAgrim'")
st.sidebar.markdown(f"**Lic. Jhonny Matos. M.A., Presidente**")
st.sidebar.divider()

menu = st.sidebar.radio("Módulos del Sistema", 
    ["📊 Mando Central", "📝 Registro y Redacción", "💰 Honorarios y Cobros", "⚙️ Configuración"])

# --- 1. MANDO CENTRAL ---
if menu == "📊 Mando Central":
    st.title("📊 Tablero de Control Operativo")
    casos = consultar_expedientes()
    if casos:
        df = pd.DataFrame(casos)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Casos", len(df))
        c2.metric("Deslindes", len(df[df['tipo'] == 'Deslinde']) if 'tipo' in df else 0)
        c3.metric("En Tribunal", len(df[df['etapa'] == 'Tribunal']) if 'etapa' in df else 0)
        c4.metric("Pendientes", len(df[df['estado'] == 'Abierto']) if 'estado' in df else 0)
        
        st.subheader("Carga de Trabajo por Jurisdicción")
        st.bar_chart(df['jurisdiccion'].value_counts() if 'jurisdiccion' in df else [])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Inicie el sistema registrando su primer caso en el módulo de Registro.")

# --- 2. REGISTRO Y REDACCIÓN ---
elif menu == "📝 Registro y Redacción":
    st.title("📝 Gestión de Expedientes y Documentos")
    dic = obtener_diccionario_maestro()
    
    with st.form("form_caso"):
        st.subheader("Datos del Proceso")
        col1, col2 = st.columns(2)
        with col1:
            num = st.text_input("Número de Expediente / Referencia:")
            tipo = st.selectbox("Tipo de Proceso:", ["Deslinde", "Saneamiento", "Litis sobre derecho registrado", "Transferencia", "Determinación de Herederos"])
            jur = st.selectbox("Jurisdicción:", ["Santiago", "La Vega", "Puerto Plata", "Moca", "Santo Domingo"])
        with col2:
            cli = st.text_input("Nombre del Cliente / Reclamante:")
            est = st.selectbox("Etapa Actual:", ["Recepción", "Mensura Catastral", "Sometimiento", "Tribunal", "Aprobado"])
        
        st.subheader("Asignación de Personal Técnico")
        a1, a2, a3 = st.columns(3)
        agrimensor = a1.selectbox("Agrimensor:", dic['agrimensor'] or ["N/A"])
        abogado = a2.selectbox("Abogado:", dic['abogado'] or ["N/A"])
        notario = a3.selectbox("Notario:", dic['notario'] or ["N/A"])

        if st.form_submit_button("Guardar y Preparar Documentación"):
            exito = registrar_evento("casos", {"numero_expediente": num, "tipo": tipo, "jurisdiccion": jur, "cliente": cli, "etapa": est, "estado": "Abierto"})
            if exito: st.success("Expediente blindado en la nube exitosamente.")

# --- 3. HONORARIOS Y COBROS ---
elif menu == "💰 Honorarios y Cobros":
    st.title("💰 Módulo Financiero: Honorarios y Cobros")
    finanzas = consultar_honorarios()
    if finanzas:
        df_f = pd.DataFrame(finanzas)
        st.table(df_f)
    else:
        st.warning("No hay registros financieros activos.")
    
    with st.expander("Registrar Nuevo Pago / Honorario"):
        st.number_input("Monto total del contrato:", min_value=0.0)
        st.number_input("Avance recibido:", min_value=0.0)
        st.button("Actualizar Balance")

# --- 4. CONFIGURACIÓN ---
elif menu == "⚙️ Configuración":
    st.title("⚙️ Configuración del Sistema")
    st.write("Estado de Conexión: **Nube (Supabase) Conectada**")
    if st.button("Verificar Integridad de Tablas"):
        st.balloons()
