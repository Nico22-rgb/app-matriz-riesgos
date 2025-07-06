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

    tipo_validacion = st.selectbox("Seleccione el tipo de validación a realizar", [
        "Validación de procesos", "Validación de campaña", "Validación de limpieza"], index=None)

    if tipo_validacion == "Validación de procesos":
        tipo_linea = st.selectbox("¿Para qué línea de fabricación desea hacer su análisis de riesgo?", [
            "Línea de medicamentos sólidos", "Línea de medicamentos líquidos y semisólidos", "Línea de cosméticos"])

    elif tipo_validacion == "Validación de campaña":
        tipo_linea = st.selectbox("¿Para qué línea de fabricación desea hacer su análisis de riesgo?", [
            "Línea de medicamentos sólidos", "Línea de medicamentos líquidos y semisólidos", "Línea de cosméticos"])

    elif tipo_validacion == "Validación de limpieza":
        tipo_linea = st.selectbox("¿Para qué línea de fabricación desea hacer su análisis de riesgo?", [
            "Línea de medicamentos sólidos", "Línea de medicamentos líquidos y semisólidos", "Línea de cosméticos"])

    # Bloque común a cualquier tipo de validación
if tipo_linea == "Línea de medicamentos sólidos":
    st.markdown("### Seleccione las etapas que aplican al proceso:")

    etapa_green = st.toggle("Green")
    etapa_yellow = st.toggle("Yellow")
    etapa_red = st.toggle("Red")
    etapa_blue = st.toggle("Blue")

    # Guardar las etapas seleccionadas en una lista
    etapas_seleccionadas = []
    if etapa_green:
        etapas_seleccionadas.append("Green")
    if etapa_yellow:
        etapas_seleccionadas.append("Yellow")
    if etapa_red:
        etapas_seleccionadas.append("Red")
    if etapa_blue:
        etapas_seleccionadas.append("Blue")





