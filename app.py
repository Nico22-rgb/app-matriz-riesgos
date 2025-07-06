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

    # Paso 2: si selecciona tipo de validación
    if tipo_validacion:
        tipo_linea = st.selectbox("¿Para qué línea de fabricación desea hacer su análisis de riesgo?", [
            "Línea de medicamentos sólidos", "Línea de medicamentos líquidos y semisólidos", "Línea de cosméticos"], index=None)

        # Paso 3: mostrar etapas SOLO si aplica
        if tipo_validacion in ["Validación de procesos", "Validación de campaña"] and tipo_linea:
            st.markdown("### Seleccione las etapas que aplican al proceso:")

            etapa_green = st.toggle("Green")
            etapa_yellow = st.toggle("Yellow")
            etapa_red = st.toggle("Red")
            etapa_blue = st.toggle("Blue")

            etapas_seleccionadas = []
            if etapa_green:
                etapas_seleccionadas.append("Green")
            if etapa_yellow:
                etapas_seleccionadas.append("Yellow")
            if etapa_red:
                etapas_seleccionadas.append("Red")
            if etapa_blue:
                etapas_seleccionadas.append("Blue")


