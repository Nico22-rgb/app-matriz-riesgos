import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Ejemplo extracciónn Excel", layout="centered")
st.title("Ejemplo: Mostrar fragmento de Excel editable")

# Simular un archivo Excel si el usuario no sube uno
def crear_excel_ejemplo():
    data = [
        ["Nombre", "Cargo", "Área", "Riesgo 1", "Riesgo 2", "Riesgo 3"],
        ["Juan Pérez", "Operario", "Sólidos", "Alto", "Medio", "Bajo"],
        ["Ana Gómez", "Técnico", "Líquidos", "Bajo", "Bajo", "Alto"],
        ["Luis Torres", "Inspector", "Cosméticos", "Medio", "Alto", "Bajo"],
        ["Laura Díaz", "Supervisor", "Sólidos", "Alto", "Alto", "Alto"],
        ["Marta López", "Jefe de área", "Líquidos", "Bajo", "Medio", "Alto"]
    ]
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, header=False)
    buffer.seek(0)
    return buffer

# Subida de archivo
archivo = st.file_uploader("ejemplo_matriz_riesgos", type=[".xlsx"])

# Usar archivo real o generar uno
if archivo is None:
    st.info("No subiste un archivo, usando uno de ejemplo...")
    archivo = crear_excel_ejemplo()

try:
    df = pd.read_excel(archivo, header=None)

    # Extraer fila 1 y filas 3-5, columnas A-F (0:6)
    encabezado = df.iloc[[0], 0:6]
    contenido = df.iloc[2:5, 0:6]
    tabla = pd.concat([encabezado, contenido], ignore_index=True)

    st.markdown("### Vista editable del fragmentoO del archivo:")
    tabla_editada = st.data_editor(tabla, use_container_width=True, num_rows="dynamic")

except Exception as e:
    st.error(f"Ocurrió un error al procesar el archivo: {e}")

