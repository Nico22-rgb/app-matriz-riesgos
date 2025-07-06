import streamlit as st
import pandas as pd
import io
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configurar la página
st.set_page_config(page_title="Análisis de Riesgos", layout="centered")

# Título centrado
st.markdown(
    "<h1 style='text-align: center;'>Análisis de Riesgos - Área de Validaciones</h1>",
    unsafe_allow_html=True
)

# Cargar imagen
imagen = Image.open("altea.jpg")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(imagen, width=300)

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

        if etapas_seleccionadas:
            if st.button("Generar matriz de riesgo"):
                st.success(f"¡Matriz de riesgo generada con éxito!\nEtapas seleccionadas: {', '.join(etapas_seleccionadas)}")

                try:
                    # Leer archivo Excel sin encabezado automático
                    df = pd.read_excel(archivo, header=None)

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
                            bloques.append(df.iloc[inicio:fin])

                    tabla = pd.concat([encabezado] + bloques, ignore_index=True)

                    st.write("Por favor completa tu matriz de riesgo:")
                    tabla_editada = st.data_editor(tabla, use_container_width=True, num_rows="dynamic")

                    buffer = io.BytesIO()
                    tabla_editada.to_excel(buffer, index=False, header=False)
                    buffer.seek(0)
                    st.download_button(
                        label="📥 Descargar matriz de riesgo en Excel",
                        data=buffer,
                        file_name="matriz_riesgo.xlsx"
                    )

                    pdf_buffer = io.BytesIO()
                    c = canvas.Canvas(pdf_buffer, pagesize=letter)
                    width, height = letter
                    x = 50
                    y = height - 50

                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(x, y, "Matriz de Riesgo")
                    y -= 20

                    c.setFont("Helvetica-Bold", 10)
                    for col_num, value in enumerate(tabla_editada.columns):
                        c.drawString(x + col_num * 80, y, str(value))
                    y -= 15

                    c.setFont("Helvetica", 9)
                    for row in tabla_editada.itertuples(index=False):
                        for col_num, value in enumerate(row):
                            c.drawString(x + col_num * 80, y, str(value))
                        y -= 15
                        if y < 50:
                            c.showPage()
                            y = height - 50

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
