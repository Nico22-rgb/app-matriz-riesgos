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
imagen = Image.open("altea.jpg") 

# Crear columnas para centrar la imagen
col1, col2, col3 = st.columns([1, 2, 1])  
with col2:
    st.image(imagen, width=300)  
    
# Texto
st.markdown(
    "<h4>📎 Por favor sube el archivo de la base de datos de las matrices de riesgo</h4>",
    unsafe_allow_html=True
)

# Subida de archivo
archivo = st.file_uploader("", type=[".xlsx"])

# Paso 1: si se sube el archivo
if archivo:
    tipo_validacion = st.selectbox("Seleccione el tipo de validación a realizar", [
        "Validación de procesos", "Validación de campaña", "Validación de limpieza"], index=None)

    if tipo_validacion == "Validacion de procesos":
        tipo_linea = st.selectbox("¿A qué linea de fabricación pertenece su producto?", [
                                  "Linea de medicamentos sólidos", "Linea de medicamentos líquidos y semisólidos", "Linea de cosméticos"], index=None)

        if tipo_linea == "Linea de medicamentos sólidos":
            etapas_seleccionadas = st.multiselect("Seleccione las etapas que apliquen", [
                                                  "Green", "Yellow", "Red", "Blue"])




