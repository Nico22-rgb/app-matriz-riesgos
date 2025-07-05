import streamlit as st
from PIL import Image

# Configurar la página
st.set_page_config(page_title="Análisis de Riesgos", layout="centered")

# Título centrado
st.markdown(
    """
    <h1 style='text-align: center; color: #2c3e50;'>Análisis de Riesgos - Área de Validaciones</h1>
    """,
    unsafe_allow_html=True
)

# Mostrar imagen
imagen = Image.open("altea.jpg")  # Cambia el nombre si tu imagen se llama diferente
st.image(imagen, width=250)







