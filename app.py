import streamlit as st
from PIL import Image

# Configurar la página
st.set_page_config(page_title="Análisis de Riesgos", layout="centered")

# Título centrado
st.markdown(
    "<h1 style='text-align: center;'>Análisis de Riesgos - Área de Validaciones</h1>",
    unsafe_allow_html=True
)

# Cargar imagen
imagen = Image.open("altea.jpg")  # Reemplaza con el nombre correcto si es diferente

# Crear columnas para centrar la imagen
col1, col2, col3 = st.columns([1, 2, 1])  # col2 es más ancha (centro)
with col2:
    st.image(imagen, width=300)  # Puedes ajustar el ancho según necesites

# Subir el archivo
archivo = st.file_uploader("Sube el archivo de la base de datos 204", [".xlsx"])

if archivo:

    tipo_validacion = st.selectbox("¿Qué tipo de validación desea?", [
                                   "Validacion 1", "Validacion 2", "Validacion 3"], index=None)

    if tipo_validacion == "Validacion 1":
        tipo_linea = st.selectbox("¿Qué linea desea consultar?", [
                                  "Linea 1", "Linea 2", "Linea 3"], index=None)

        if tipo_linea == "Linea 1":
            etapas_seleccionadas = st.multiselect("Seleccione las etapas que apliquen", [
                                                  "Green", "Yellow", "Red", "Blue"])








