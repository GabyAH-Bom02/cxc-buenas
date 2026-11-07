import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="CXC Seguras", page_icon="💼", layout="centered")

# Inicializar Base de Datos en la sesión
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=[
        "Proyecto", "Monto Total", "Anticipo", "Fecha 1", "Fecha 2", "Fecha 3", "Fecha 4", "Fecha 5"
    ])

if 'terminos_aceptados' not in st.session_state:
    st.session_state.terminos_aceptados = False

if 'codigo_ingresado' not in st.session_state:
    st.session_state.codigo_ingresado = False

# Título Principal
st.title("🔒 CXC Seguras")
st.subheader("Sistema de Cobranza y Gestión de Cartera")

# --- PASO 1: TÉRMINOS Y CONDICIONES ---
if not st.session_state.terminos_aceptados:
    st.markdown("### Aviso de Privacidad y Términos")
    st.info("""
    **Cobranzas Seguras MX, S.A.** con domicilio en Av. Cerro de la Campana 102, Col. Los Pirules, Estado de México, 
    es responsable del tratamiento de sus datos personales (facturas, montos de proyectos, nombres de clientes).
    """)
    
    acepto = st.checkbox("He leído y acepto el aviso de privacidad y términos y condiciones.")
    
    if st.button("Continuar"):
        if acepto:
            st.session_state.terminos_aceptados = True
            st.rerun()
        else:
            st.error("Debes aceptar los términos y condiciones para continuar.")

# --- PASO 2: INGRESO DE CÓDIGO DE ACCESO ---
elif not st.session_state.codigo_ingresado:
    st.markdown("### Identificación de Usuario")
    codigo = st.text_input("Ingresa tu código de acceso de 4 dígitos:", type="password")
    
    if st.button("Validar Código"):
        if codigo in ["0444", "0004", "1111"]:
            st.session_state.codigo_ingresado = True
            st.session_state.rol = codigo
            st.rerun()
        else:
            st.error("Código incorrecto. Intenta de nuevo (Ej. Jefe: 0444, Operación: 0004)")

# --- PASO 3: PANEL SEGÚN EL ROL ---
else:
    rol = st.session_state.rol
    
    if rol == "0444":
        st.success("👤 Sesión Iniciada: **Jefe / Líder**")
        st.markdown("### Registrar Nuevo Proyecto / Factura")
        
        with st.form("form_proyecto"):
            proyecto = st.text_input("Nombre del Proyecto / Empresa")
            monto_total = st.number_input("Monto Total ($)", min_value=0.0, step=100.0)
            anticipo = st.number_input("Anticipo ($)", min_value=0.0, step=100.0)
            
            num_fechas = st.selectbox("Número de fechas de cobro (máx. 5):", [1, 2, 3, 4, 5])
            
            fechas = []
            for i in range(num_fechas):
                f = st.date_input(f"Fecha de cobro {i+1}")
                fechas.append(str(f))
            
            # Completar hasta 5 elementos para la tabla
            while len(fechas) < 5:
                fechas.append("")
                
            enviar = st.form_submit_button("Guardar en Base de Datos")
            
            if enviar:
                if proyecto.strip() == "":
                    st.warning("Por favor ingresa el nombre del proyecto.")
                else:
                    nuevo_registro = {
                        "Proyecto": proyecto,
                        "Monto Total": monto_total,
                        "Anticipo": anticipo,
                        "Fecha 1": fechas[0],
                        "Fecha 2": fechas[1],
                        "Fecha 3": fechas[2],
                        "Fecha 4": fechas[3],
                        "Fecha 5": fechas[4]
                    }
                    st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([nuevo_registro])], ignore_index=True)
                    st.success(f"¡Proyecto '{proyecto}' guardado con éxito!")

        st.markdown("---")
        st.markdown("### Proyectos Registrados Actuales")
        st.dataframe(st.session_state.db)

    elif rol == "0004":
        st.success("👤 Sesión Iniciada: **Personal Operativo / Descarga**")
        st.markdown("### Descargar Base de Datos")
        
        if len(st.session_state.db) > 0:
            csv = st.session_state.db.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Base de Datos en CSV (Compatible con Excel/Sheets)",
                data=csv,
                file_name="base_datos_cxc_seguras.csv",
                mime="text/csv",
            )
            st.dataframe(st.session_state.db)
        else:
            st.info("Aún no hay registros guardados por el jefe.")

    elif rol == "1111":
        st.success("👤 Sesión Iniciada: **Vista Ejecutiva / Semaforización**")
        st.markdown("### Control de Cobranza y Semáforo (Fecha actual: 6 Nov 2026)")
        
        if len(st.session_state.db) > 0:
            hoy = datetime.strptime("2026-11-06", "%Y-%m-%d").date()
            
            datos_semaforo = []
            for index, row in st.session_state.db.iterrows():
                for i in range(1, 6):
                    f_str = row[f"Fecha {i}"]
                    if f_str != "":
                        f_date = datetime.strptime(f_str, "%Y-%m-%d").date()
                        estado = "🟢 Ya se puede cobrar" if f_date <= hoy else "🔴 Aún no"
                        datos_semaforo.append({
                            "Proyecto": row["Proyecto"],
                            "Monto Total": row["Monto Total"],
                            "Cuota Fecha": f_str,
                            "Estado": estado
                        })
            
            df_sem = pd.DataFrame(datos_semaforo)
            st.dataframe(df_sem, use_container_width=True)
        else:
            st.info("No hay datos para mostrar en el semáforo.")

    if st.button("Cerrar Sesión"):
        st.session_state.codigo_ingresado = False
        st.rerun()
