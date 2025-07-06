import streamlit as st
import pandas as pd
import io
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import load_workbook
from openpyxl.styles import Alignment
import requests

# Configuración inicial
st.set_page_config(page_title="Análisis de Riesgos", layout="centered")

st.markdown(
    "<h1 style='text-align: center;'>Análisis de Riesgos - Área de Validaciones</h1>",
    unsafe_allow_html=True
)

# Imagen
try:
    imagen = Image.open("altea.jpg")
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

if archivo:
    tipo_validacion = st.selectbox("Seleccione el tipo de validación a realizar", [
        "Validación de procesos", "Validación de campaña", "Validación de limpieza"
    ], index=None)

    if tipo_validacion in ["Validación de procesos", "Validación de campaña"]:
        tipo_linea = st.selectbox("¿A qué línea de fabricación pertenece su producto?", [
            "Línea de medicamentos sólidos",
            "Línea de medicamentos líquidos y semisólidos",
        ], index=None)

        etapas_seleccionadas = []
        sheet_to_use = None

        if tipo_linea == "Línea de medicamentos sólidos":
            sheet_to_use = "MR 1 sólidos"
            st.markdown("Seleccione las etapas que aplican al proceso:")
            if st.toggle("Dispensación"):
                etapas_seleccionadas.append("Dispensación")
            if st.toggle("Compresión"):
                etapas_seleccionadas.append("Compresión")
            if st.toggle("Fusión"):
                etapas_seleccionadas.append("Fusión")

        elif tipo_linea == "Línea de medicamentos líquidos y semisólidos":
            sheet_to_use = "MR 1 líquidos y semisólidos"
            st.markdown("Seleccione las etapas que aplican al proceso:")
            if st.toggle("Fusión"):
                etapas_seleccionadas.append("Fusión")
            if st.toggle("Emulsión"):
                etapas_seleccionadas.append("Emulsión")

        if etapas_seleccionadas:
            if st.button("Generar matriz de riesgo"):
                st.success(f"¡Matriz de riesgo generada con éxito!\nEtapas seleccionadas: {', '.join(etapas_seleccionadas)}")

                try:
                    df = pd.read_excel(archivo, sheet_name=sheet_to_use, header=None)

                    rangos_por_etapa = {
                        "Dispensación": (1, 6),
                        "Compresión": (6, 11),
                        "Fusión": (11, 16),
                        "Emulsión": (16, 21),
                        "Mezcla": (21, 26),
                        "Dispensado": (26, 31)
                    }

                    encabezado = df.iloc[[0]]
                    bloques = []

                    for etapa in etapas_seleccionadas:
                        if etapa in rangos_por_etapa:
                            inicio, fin = rangos_por_etapa[etapa]
                            bloque_actual = df.iloc[inicio:fin]
                            bloques.append(bloque_actual)

                    tabla = pd.concat([encabezado] + bloques, ignore_index=True)

                    st.write("Por favor completa tu matriz de riesgo:")
                    tabla_editada = st.data_editor(tabla, use_container_width=True, num_rows="dynamic")

                    # Guardar a Excel con celdas combinadas en la primera columna
                    buffer = io.BytesIO()
                    tabla_editada.iloc[:, 0] = tabla_editada.iloc[:, 0].ffill()
                    tabla_editada.to_excel(buffer, index=False, header=False)
                    buffer.seek(0)

                    wb = load_workbook(buffer)
                    ws = wb.active

                    col_to_merge = 1
                    current_value = ws.cell(row=1, column=col_to_merge).value
                    start_row = 1

                    for row in range(2, ws.max_row + 2):
                        value = ws.cell(row=row, column=col_to_merge).value if row <= ws.max_row else None
                        if value != current_value:
                            if row - start_row > 1:
                                ws.merge_cells(start_row=start_row, start_column=col_to_merge,
                                               end_row=row - 1, end_column=col_to_merge)
                                ws.cell(row=start_row, column=col_to_merge).alignment = Alignment(horizontal="center", vertical="center")
                            current_value = value
                            start_row = row

                    output = io.BytesIO()
                    wb.save(output)
                    output.seek(0)

                    st.download_button(
                        label="📥 Descargar matriz de riesgo en Excel",
                        data=output,
                        file_name="matriz_riesgo.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                except Exception as e:
                    st.error(f"Ocurrió un error al procesar el archivo: {e}")
