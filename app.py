import streamlit as st
import pandas as pd
import io
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import requests # Importar requests para descargar la imagen desde una URL

# Configurar la página
st.set_page_config(page_title="Análisis de Riesgos", layout="centered")

# Título centrado
st.markdown(
    "<h1 style='text-align: center;'>Análisis de Riesgos - Área de Validaciones</h1>",
    unsafe_allow_html=True
)

# Cargar imagen desde una URL (reemplazando la carga local de "altea.jpg")
# Se usa una imagen de marcador de posición para que la aplicación sea ejecutable sin un archivo local.
image_url = "https://placehold.co/300x100/A0A0A0/FFFFFF?text=Altea+Logo"
try:
    response = requests.get(image_url)
    imagen = Image.open(io.BytesIO(response.content))
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(imagen, width=300)
except Exception as e:
    st.warning(f"No se pudo cargar la imagen del logo. Error: {e}")
    st.info("Asegúrate de tener conexión a internet para cargar la imagen de marcador de posición.")


# Subida de archivo
st.markdown(
    "<h5>Por favor sube el archivo de la base de datos de las matrices de riesgo</h5>",
    unsafe_allow_html=True
)
archivo = st.file_uploader("", type=[".xlsx"])

# Paso 1: si se sube el archivo
if archivo:
    tipo_validacion = st.selectbox("Seleccione el tipo de validación a realizar", [
        "Validación de procesos", "Validación de campaña", "Validación de limpieza"
    ], index=None)

    if tipo_validacion in ["Validación de procesos", "Validación de campaña"]:
        tipo_linea = st.selectbox("¿A qué línea de fabricación pertenece su producto?", [
            "Línea de medicamentos sólidos",
            "Línea de medicamentos líquidos y semisólidos",
            "Línea de cosméticos"
        ], index=None)

        etapas_seleccionadas = []

        if tipo_linea == "Línea de medicamentos sólidos":
            st.markdown("Seleccione las etapas que aplican al proceso:")
            if st.toggle("Dispensación"):
                etapas_seleccionadas.append("Dispensación")
            if st.toggle("Compresión"):
                etapas_seleccionadas.append("Compresión")

        elif tipo_linea == "Línea de medicamentos líquidos y semisólidos":
            st.markdown("Seleccione las etapas que aplican al proceso:")
            if st.toggle("Fusión"):
                etapas_seleccionadas.append("Fusión")
            if st.toggle("Emulsión"):
                etapas_seleccionadas.append("Emulsión")

        elif tipo_linea == "Línea de cosméticos":
            st.markdown("Seleccione las etapas que aplican al proceso:")
            if st.toggle("Mezcla"):
                etapas_seleccionadas.append("Mezcla")
            if st.toggle("Dispensado"):
                etapas_seleccionadas.append("Dispensado")

        # Botón de generación de matriz
        if etapas_seleccionadas:
            if st.button("Generar matriz de riesgo"):
                st.success(f"¡Matriz de riesgo generada con éxito!\nEtapas seleccionadas: {', '.join(etapas_seleccionadas)}")

                try:
                    # Leer archivo Excel
                    df = pd.read_excel(archivo)

                    # Diccionario de rangos por etapa (índices base 0 de Pandas)
                    # NOTA IMPORTANTE:
                    # Si tu archivo de Excel tiene una fila de encabezado que ya se extrae con df.iloc[[0]],
                    # entonces la primera fila de datos en Excel (fila 2) corresponde al índice 1 en Pandas.
                    # El rango df.iloc[inicio:fin] es inclusivo en 'inicio' y exclusivo en 'fin'.
                    # Por ejemplo, (1, 6) significa índices de Pandas 1, 2, 3, 4, 5 (que son filas 2 a 6 de Excel).
                    # Por favor, ajusta estos rangos según la estructura exacta de tu Excel.
                    rangos_por_etapa = {
                        "Dispensación": (1, 6),   # filas 2 a 6 de Excel (índices Pandas 1 a 5)
                        "Compresión": (6, 11),    # filas 7 a 11 de Excel (índices Pandas 6 a 10)
                        "Fusión": (11, 16),       # filas 12 a 16 de Excel (índices Pandas 11 a 15)
                        "Emulsión": (16, 21),     # filas 17 a 21 de Excel (índices Pandas 16 a 20)
                        "Mezcla": (21, 26),       # filas 22 a 26 de Excel (índices Pandas 21 a 25)
                        "Dispensado": (26, 31)    # filas 27 a 31 de Excel (índices Pandas 26 a 30)
                    }

                    # Extraer encabezado (primera fila del Excel)
                    # Se asume que la primera fila del Excel es el encabezado que siempre debe incluirse.
                    encabezado = df.iloc[[0]]
                    bloques = []

                    for etapa in etapas_seleccionadas:
                        if etapa in rangos_por_etapa:
                            inicio, fin = rangos_por_etapa[etapa]
                            # Se seleccionan las filas correspondientes a la etapa
                            bloques.append(df.iloc[inicio:fin])

                    # Concatenar tabla final: encabezado + bloques de etapas seleccionadas
                    tabla = pd.concat([encabezado] + bloques, ignore_index=True)

                    # **DEBUGGING AID:** Mostrar la tabla extraída para verificar los rangos
                    st.write("Tabla extraída (verifica si los rangos son correctos):")
                    st.dataframe(tabla) # Usar st.dataframe para una mejor visualización

                    # Editor de tabla para que el usuario pueda completar la matriz
                    st.write("Por favor completa tu matriz de riesgo:")
                    tabla_editada = st.data_editor(tabla, use_container_width=True, num_rows="dynamic")

                    # Descargar Excel
                    buffer = io.BytesIO()
                    # Se guarda el DataFrame editado en un archivo Excel en memoria
                    # header=False para evitar escribir el índice del DataFrame como una fila de encabezado en el Excel
                    tabla_editada.to_excel(buffer, index=False, header=False)
                    buffer.seek(0) # Mover el puntero al inicio del buffer para la descarga
                    st.download_button(
                        label="📥 Descargar matriz de riesgo en Excel",
                        data=buffer,
                        file_name="matriz_riesgo.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" # MIME type para Excel
                    )

                    # Crear PDF
                    pdf_buffer = io.BytesIO()
                    c = canvas.Canvas(pdf_buffer, pagesize=letter)
                    width, height = letter
                    x_start = 50 # Posición inicial X para el texto
                    y_start = height - 50 # Posición inicial Y para el texto

                    # Título del PDF
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(x_start, y_start, "Matriz de Riesgo")
                    y_position = y_start - 20 # Espacio después del título

                    # Escribir encabezados de la tabla en el PDF
                    c.setFont("Helvetica-Bold", 10)
                    # Se itera sobre las columnas de la tabla editada para escribir los encabezados
                    for col_num, value in enumerate(tabla_editada.columns):
                        c.drawString(x_start + col_num * 80, y_position, str(value))
                    y_position -= 15 # Espacio después de los encabezados

                    # Escribir filas de datos en el PDF
                    c.setFont("Helvetica", 9)
                    # Se itera sobre cada fila del DataFrame editado
                    for row in tabla_editada.itertuples(index=False):
                        # Se itera sobre cada valor en la fila
                        for col_num, value in enumerate(row):
                            c.drawString(x_start + col_num * 80, y_position, str(value))
                        y_position -= 15 # Espacio después de cada fila
                        # Si la posición Y es muy baja, se crea una nueva página
                        if y_position < 50:
                            c.showPage()
                            y_position = height - 50 # Reiniciar posición Y para la nueva página

                    c.save() # Guardar el contenido del PDF
                    pdf_buffer.seek(0) # Mover el puntero al inicio del buffer para la descarga

                    st.download_button(
                        label="📄 Descargar matriz de riesgo en PDF",
                        data=pdf_buffer,
                        file_name="matriz_riesgo.pdf",
                        mime="application/pdf"
                    )

                except Exception as e:
                    st.error(f"Ocurrió un error al procesar el archivo: {e}")
