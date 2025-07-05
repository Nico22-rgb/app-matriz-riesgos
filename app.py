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
imagen = Image.open("logo.png")  # Reemplaza con el nombre correcto si es diferente

# Crear columnas para centrar la imagen
col1, col2, col3 = st.columns([1, 2, 1])  # col2 es más ancha (centro)
with col2:
    st.image(imagen, width=300)  # Puedes ajustar el ancho según necesites







