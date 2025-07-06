import streamlit as st
import pandas as pd
import io
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import load_workbook
from openpyxl.styles import Alignment
import requests

# Configuración inicial de la página de Streamlit
st.set_page_config(page_title="Análisis de Riesgos", layout="centered")

# Título principal de la aplicación
st.markdown(
    "<h1 style='text-align: center;'>Análisis de Riesgos - Área de Validaciones</h1>",
    unsafe_allow_html=True
)
try:
    imagen = Image.open("altea.jpg")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(imagen, width=300)
except Exception as e:
    st.warning(f"No se pudo cargar la imagen del logo. Error: {e}")
    st.info("Asegúrate de tener conexión a internet para cargar la imagen de marcador de posición.")


# Sección para subir el archivo de la base de datos de las matrices de riesgo
st.markdown(
    "<h5>Por favor sube el archivo de la base de datos de las matrices de riesgo</h5>",
    unsafe_allow_html=True
)
archivo = st.file_uploader("", type=[".xlsx"])

# Lógica principal de la aplicación si se ha subido un archivo
if archivo:
    # Selección del tipo de validación a realizar
    tipo_validacion = st.selectbox("Seleccione el tipo de validación a realizar", [
        "Validación de procesos", "Validación de campaña", "Validación de limpieza"
    ], index=None)

    # Lógica condicional basada en el tipo de validación
    if tipo_validacion in ["Validación de procesos", "Validación de campaña"]:
        # Selección de la línea de fabricación del producto
        tipo_linea = st.selectbox("¿A qué línea de fabricación pertenece su producto?", [
            "Línea de medicamentos sólidos",
            "Línea de medicamentos líquidos y semisólidos",
            "Línea de cosméticos"
        ], index=None)

        etapas_seleccionadas = []

        # Selección de etapas específicas según la línea de fabricación
        if tipo_linea == "Línea de medicamentos sólidos":
            st.markdown("Seleccione las etapas que aplican al proceso:")
            if st.toggle("Dispensación"):
                etapas_seleccionadas.append("Dispensación")
            if st.toggle("Compresión"):
                etapas_seleccionadas.append("Compresión")
            if st.toggle("Fusión"):
                etapas_seleccionadas.append("Fusión")

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

        # Botón para generar la matriz de riesgo si hay etapas seleccionadas
        if etapas_seleccionadas:
            if st.button("Generar matriz de riesgo"):
                st.success(f"¡Matriz de riesgo generada con éxito!\nEtapas seleccionadas: {', '.join(etapas_seleccionadas)}")

                try:
                    # Lectura del archivo Excel sin considerar encabezados automáticamente
                    # Esto permite un control preciso de las filas por índice.
                    df = pd.read_excel(archivo, header=None)

                    # Definición de los rangos de filas para cada etapa en el Excel original
                    # Los índices son base 0 para Pandas, donde la fila 1 de Excel es el índice 0.
                    rangos_por_etapa = {
                        "Dispensación": (1, 6),
                        "Compresión": (6, 11),
                        "Fusión": (11, 16),
                        "Emulsión": (16, 21),
                        "Mezcla": (21, 26),
                        "Dispensado": (26, 31)
                    }

                    # Extracción del encabezado (primera fila del Excel)
                    encabezado = df.iloc[[0]]
                    bloques = []

                    # Extracción de los bloques de datos correspondientes a las etapas seleccionadas
                    for etapa in etapas_seleccionadas:
                        if etapa in rangos_por_etapa:
                            inicio, fin = rangos_por_etapa[etapa]
                            bloque_actual = df.iloc[inicio:fin]
                            bloques.append(bloque_actual)

                    # Concatenación del encabezado y los bloques de etapas para formar la tabla final
                    tabla = pd.concat([encabezado] + bloques, ignore_index=True)

                    # Editor de datos de Streamlit para que el usuario complete la matriz
                    st.write("Por favor completa tu matriz de riesgo:")
                    tabla_editada = st.data_editor(tabla, use_container_width=True, num_rows="dynamic")

                    # Preparación del buffer para guardar el archivo Excel
                    buffer = io.BytesIO()

                    # Rellenar valores nulos en TODAS las columnas con el valor anterior no nulo
                    # Esto es crucial para que la combinación de celdas funcione correctamente en Excel para todas las columnas.
                    tabla_editada = tabla_editada.ffill()

                    # Guardar el DataFrame editado en el buffer como un archivo Excel
                    # Se especifica index=False y header=False para evitar escribir índices y encabezados automáticos.
                    tabla_editada.to_excel(buffer, index=False, header=False)
                    buffer.seek(0)

                    # Cargar el libro de trabajo de Excel desde el buffer con openpyxl
                    wb = load_workbook(buffer)
                    ws = wb.active

                    # Lógica para combinar celdas en TODAS las columnas
                    # Itera sobre cada columna en la hoja de cálculo
                    for col in range(1, ws.max_column + 1):
                        current_value = ws.cell(row=1, column=col).value
                        start_row = 1

                        # Itera sobre cada fila para identificar bloques de valores idénticos
                        for row in range(2, ws.max_row + 2):
                            value = ws.cell(row=row, column=col).value if row <= ws.max_row else None
                            if value != current_value:
                                # Si el valor cambia y hay más de una fila en el bloque, combinar celdas
                                if row - start_row > 1:
                                    ws.merge_cells(start_row=start_row, start_column=col,
                                                   end_row=row - 1, end_column=col)
                                    # Centrar el contenido de la celda combinada
                                    ws.cell(row=start_row, column=col).alignment = Alignment(horizontal="center", vertical="center")
                                current_value = value
                                start_row = row

                    # Guardar el libro de trabajo modificado (con celdas combinadas) en un nuevo buffer
                    output = io.BytesIO()
                    wb.save(output)
                    output.seek(0)

                    # Botón para descargar el archivo Excel con las celdas combinadas
                    st.download_button(
                        label="📥 Descargar matriz de riesgo en Excel",
                        data=output,
                        file_name="matriz_riesgo.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                except Exception as e:
                    st.error(f"Ocurrió un error al procesar el archivo: {e}")
