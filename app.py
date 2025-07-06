import streamlit as st
import pandas as pd
import io
import base64
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

# Centrar la imagen
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(imagen, width=300)

# Subida de archivo
st.markdown(
    "<h5>Por favor sube el archivo de la base de datos de las matrices de riesgo</h5>",
    unsafe_allow_html=True
)
archivo = st.file_uploader("", type=[".xlsx"])

# Paso 1: si se sube el archivo
if archivo:
    tipo_validacion = st.selectbox("Seleccione el tipo de validación a realizar", [
        "Validación de procesos", "Validación de campaña", "Validación de limpieza"], index=None)

    if tipo_validacion in ["Validación de procesos", "Validación de campaña"]:
        tipo_linea = st.selectbox("¿A qué línea de fabricación pertenece su producto?", [
            "Línea de medicamentos sólidos",
            "Línea de medicamentos líquidos y semisólidos",
            "Línea de cosméticos"
        ], index=None)

        etapas_seleccionadas = []

        if tipo_linea == "Línea de medicamentos sólidos":
            st.markdown("### Seleccione las etapas que aplican al proceso:")

            etapa_dispensacion = st.toggle("Dispensación")
            etapa_compresion = st.toggle("Compresión")

            if etapa_dispensacion:
                etapas_seleccionadas.append("Dispensación")
            if etapa_compresion:
                etapas_seleccionadas.append("Compresión")

        elif tipo_linea == "Línea de medicamentos líquidos y semisólidos":
            st.markdown("### Seleccione las etapas que aplican al proceso:")

            etapa_fusion = st.toggle("Fusión")
            etapa_emulsion = st.toggle("Emulsión")

            if etapa_fusion:
                etapas_seleccionadas.append("Fusión")
            if etapa_emulsion:
                etapas_seleccionadas.append("Emulsión")

        elif tipo_linea == "Línea de cosméticos":
            st.markdown("### Seleccione las etapas que aplican al proceso:")

            etapa_mezcla = st.toggle("Mezcla")
            etapa_dispensado = st.toggle("Dispensado")

            if etapa_mezcla:
                etapas_seleccionadas.append("Mezcla")
            if etapa_dispensado:
                etapas_seleccionadas.append("Dispensado")

      # Mostrar botón solo si hay etapas seleccionadas
        if etapas_seleccionadas:
            if st.button("Generar matriz de riesgo"):
                st.success(f"¡Matriz de riesgo generada con éxito!\n\nEtapas seleccionadas: {', '.join(etapas_seleccionadas)}")

                # Leer Excel
                try:
                    df = pd.read_excel(archivo)

                    # Extraer fila 1 y filas 3-5, columnas A-F
                    encabezado = df.iloc[[0], 0:6]
                    contenido = df.iloc[2:5, 0:6]
                    tabla = pd.concat([encabezado, contenido], ignore_index=True)

                    st.write("Por favor completa tu matriz de riesgo:")
                    tabla_editada = st.data_editor(tabla, use_container_width=True, num_rows="dynamic")

                    # Descargar como Excel
                    buffer = io.BytesIO()
                    tabla_editada.to_excel(buffer, index=False, header=False)
                    buffer.seek(0)

                    st.download_button(
                        label="📥 Descargar matriz de riesgo en Excel",
                        data=buffer,
                        file_name="matriz_riesgo.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                except Exception as e:
                    st.error(f"Ocurrió un error al procesar el archivo: {e}")



