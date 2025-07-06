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
col1, col2, col3 = st.columns([1, 2, 1])  # col2 es más ancha (centro)
with col2:
    st.image(imagen, width=300)  
    
# Mostrar el texto en grande
st.markdown(
    "<h4> Por favor sube el archivo de la base de datos de las matrices de riesgo</h4>",
    unsafe_allow_html=True
)
# Subir el archivo
archivo = st.file_uploader("", [".xlsx"])

if archivo:

    tipo_validacion = st.selectbox("Selccione el tipo de validación a realizar", [
                                   "Validación de procesos", "Validacion de campaña", "Validacion de limpieza"], index=None)

    if tipo_validacion == "Validación de procesos":
        tipo_linea = st.selectbox("¿Para que línea de fabricación desea hacer su análisis de riesgo??", [
                                  "Linea de medicamentos sólidos", "Linea de medicamentos líquidos y semisólidos", "Linea de cosméticos"], index=None)

 if tipo_validacion == "Validación de campaña":
        tipo_linea = st.selectbox("¿Para que línea de fabricación desea hacer su análisis de riesgo??", [
                                  "Linea de medicamentos sólidos", "Linea de medicamentos líquidos y semisólidos", "Linea de cosméticos"], index=None)

 if tipo_validacion == "Validación de limpieza":
        tipo_linea = st.selectbox("¿Para que línea de fabricación desea hacer su análisis de riesgo??", [
                                  "Linea de medicamentos sólidos", "Linea de medicamentos líquidos y semisólidos", "Linea de cosméticos"], index=None)

            if tipo_linea == "Linea de medicamentos sólidos":
            etapas_seleccionadas = st.multiselect("Seleccione las etapas que aplican al proceso de manufactura/envase/empaque de su producto", [
                                                  "Green", "Yellow", "Red", "Blue"])








