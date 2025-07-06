import streamlit as st
import pandas as pd
import io
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import load_workbook
from openpyxl.styles import Alignment
import requests # Asegurarse de que requests esté importado

st.set_page_config(page_title="Análisis de Riesgos", layout="centered")

st.markdown(
    "<h1 style='text-align: center;'>Análisis de Riesgos - Área de Validaciones</h1>",
    unsafe_allow_html=True
)


# Cargar imagen
try:
    imagen = Image.open("altea.jpg")
    col1, col2, col3 = st.columns([1, 2, 1])




    with col2:
        st.image(imagen, width=300)
except Exception as e:
    st.warning(f"Could not load the logo image. Error: {e}")
    st.info("Ensure you have an internet connection to load the placeholder image.")

# File upload section
st.markdown(
    "<h5>Por favor sube el archivo de la base de datos de las matrices de riesgo</h5>",
    unsafe_allow_html=True
)
archivo = st.file_uploader("", type=[".xlsx"])

# Step 1: If file is uploaded
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

        # Matrix generation button
        if etapas_seleccionadas:
            if st.button("Generar matriz de riesgo"):
                st.success(f"¡Matriz de riesgo generada con éxito!\nEtapas seleccionadas: {', '.join(etapas_seleccionadas)}")

                try:
                    # Read Excel file without automatic header, to control row extraction.
                    # df will now contain all Excel rows, starting from index 0.
                    df = pd.read_excel(archivo, header=None)

                    # Dictionary of ranges per stage (0-based Pandas indices)
                    # With `header=None` in `pd.read_excel`, Pandas index 0 corresponds to Excel row 1,
                    # index 1 to Excel row 2, and so on.
                    # The df.iloc[start:end] range is inclusive at 'start' and exclusive at 'end'.
                    # These ranges are based on the user's provided code in the query.
                    rangos_por_etapa = {
                        "Dispensación": (1, 6),
                        "Compresión": (6, 11),
                        "Fusión": (11, 16),
                        "Emulsión": (16, 21),
                        "Mezcla": (21, 26),
                        "Dispensado": (26, 31)
                    }

                    # Extract header (the first row of the Excel, which is now index 0 in df)
                    encabezado = df.iloc[[0]]
                    bloques = []

                    for etapa in etapas_seleccionadas:
                        if etapa in rangos_por_etapa:
                            inicio, fin = rangos_por_etapa[etapa]
                            # Select rows corresponding to the stage
                            bloque_actual = df.iloc[inicio:fin]
                            bloques.append(bloque_actual)

                    # Concatenate final table: header + selected stage blocks
                    tabla = pd.concat([encabezado] + bloques, ignore_index=True)

                    # Table editor for user to complete the risk matrix
                    st.write("Por favor completa tu matriz de riesgo:")
                    tabla_editada = st.data_editor(tabla, use_container_width=True, num_rows="dynamic")

                    # Save Excel with merged cells in the first column
                    buffer = io.BytesIO()

                    # IMPORTANT FIX: Fill NaN/None values in the first column with the previous valid value
                    # This ensures that openpyxl sees repeated values for merging.
                    tabla_editada.iloc[:, 0] = tabla_editada.iloc[:, 0].ffill()

                    tabla_editada.to_excel(buffer, index=False, header=False)
                    buffer.seek(0)

                    wb = load_workbook(buffer)
                    ws = wb.active

                    st.subheader("Información de Depuración para Fusión de Celdas:")
                    st.write(f"Filas totales en la hoja de cálculo: {ws.max_row}")
                    st.write(f"Columnas totales en la hoja de cálculo: {ws.max_column}")
                    st.write("Valores en la primera columna de la tabla editada (lo que openpyxl ve DESPUÉS de ffill):")
                    for r_idx in range(1, ws.max_row + 1):
                        st.write(f"Fila {r_idx}: '{ws.cell(row=r_idx, column=1).value}'")


                    # Logic to merge cells in the first column (col=1)
                    col_to_merge = 1  # First column in Excel (1-indexed)
                    current_value = ws.cell(row=1, column=col_to_merge).value
                    start_row = 1

                    st.write(f"Iniciando fusión de celdas en la columna {col_to_merge}")
                    st.write(f"Valor inicial (fila 1): '{current_value}'")
                    st.write(f"Fila de inicio de bloque: {start_row}")

                    for row in range(2, ws.max_row + 2):  # Up to one row past the end to ensure last block is merged
                        value = ws.cell(row=row, column=col_to_merge).value if row <= ws.max_row else None
                        st.write(f"Procesando fila {row}: Valor actual = '{value}', Valor anterior = '{current_value}'")
                        if value != current_value:
                            st.write(f"Valor cambiado en fila {row}. Bloque anterior de {start_row} a {row-1}.")
                            if row - start_row > 1:
                                st.write(f"Fusionando celdas de {start_row} a {row-1} en columna {col_to_merge}")
                                ws.merge_cells(start_row=start_row, start_column=col_to_merge,
                                               end_row=row - 1, end_column=col_to_merge)
                                ws.cell(row=start_row, column=col_to_merge).alignment = Alignment(horizontal="center", vertical="center")
                            else:
                                st.write(f"No se fusiona: bloque de una sola fila ({start_row}).")
                            current_value = value
                            start_row = row
                        else:
                            st.write(f"Valor igual: '{value}'. Continuar bloque.")

                    output = io.BytesIO()
                    wb.save(output)
                    output.seek(0)

                    st.download_button(
                        label="📥 Descargar matriz de riesgo en Excel",
                        data=output,
                        file_name="matriz_riesgo.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    # Create PDF
                    pdf_buffer = io.BytesIO()
                    c = canvas.Canvas(pdf_buffer, pagesize=letter)
                    width, height = letter
                    x_start = 50
                    y_start = height - 50

                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(x_start, y_start, "Matriz de Riesgo")
                    y_position = y_start - 20

                    c.setFont("Helvetica-Bold", 10)
                    for col_num, value in enumerate(tabla_editada.columns):
                        c.drawString(x_start + col_num * 80, y_position, str(value))
                    y_position -= 15

                    c.setFont("Helvetica", 9)
                    for row in tabla_editada.itertuples(index=False):
                        for col_num, value in enumerate(row):
                            c.drawString(x_start + col_num * 80, y_position, str(value))
                        y_position -= 15
                        if y_position < 50:
                            c.showPage()
                            y_position = height - 50

                    c.save()
                    pdf_buffer.seek(0)

                    st.download_button(
                        label="📄 Descargar matriz de riesgo en PDF",
                        data=pdf_buffer,
                        file_name="matriz_riesgo.pdf",
                        mime="application/pdf"
                    )

                except Exception as e:
                    st.error(f"Ocurrió un error al procesar el archivo: {e}")


