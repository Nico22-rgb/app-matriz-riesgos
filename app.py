import streamlit as st
import pandas as pd
import io
from PIL import Image
from openpyxl import load_workbook
from openpyxl.styles import Alignment

st.set_page_config(page_title="Análisis de Riesgos", layout="centered")

if 'edited_data_table' not in st.session_state:
    st.session_state.edited_data_table = pd.DataFrame()

st.markdown("<h1 style='text-align: center;'>Análisis de Riesgos - Área de Validaciones</h1>", unsafe_allow_html=True)

try:
    imagen = Image.open("altea.jpg")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(imagen, width=300)
except Exception as e:
    st.warning(f"No se pudo cargar la imagen del logo. Error: {e}")
    st.info("Asegúrate de tener conexión a internet para cargar la imagen de marcador de posición.")

st.markdown("<h5>Por favor sube el archivo de la base de datos de las matrices de riesgo</h5>", unsafe_allow_html=True)
archivo = st.file_uploader("", type=[".xlsx"])

if archivo:
    tipo_validacion = st.selectbox("Seleccione el tipo de validación a realizar", [
        "Validación de procesos", "Validación de campaña", "Validación de limpieza"
    ], index=None)

    etapas_seleccionadas = []
    sheet_to_use = None

    if tipo_validacion in ["Validación de procesos", "Validación de campaña"]:
        tipo_linea = st.selectbox("¿A qué línea de fabricación pertenece su producto?", [
            "Línea de medicamentos sólidos",
            "Línea de medicamentos líquidos y semisólidos"
        ], index=None)

        if tipo_linea == "Línea de medicamentos sólidos":
            sheet_to_use = "MR 1 sólidos"
            st.markdown("Seleccione las etapas que aplican al proceso:")
            etapas_posibles = [
                "Verificación de prerrequisitos de validación",
                "Pesaje/Dispensación de materias primas",
                "Pulverización",
                "Pelletización",
                "Granulacion",
                "Secado",
                "Compactación",
                "Mezcla (Lubricación)",
                "Encapsulado",
                "Compresión",
                "Recubrimiento",
                "Grageado",
                "Revisión",
                "Envase blíster",
                "Envase foil",
                "Envase frasco",
                "Envase sobre",
                "Envase tubo",
                "Empaque blíster",
                "Empaque manual foil",
                "Empaque frasco",
                "Empaque tubo",
                "Recogida de blísters",
                "Codificado manual"
            ]
            for etapa in etapas_posibles:
                if st.toggle(etapa):
                    etapas_seleccionadas.append(etapa)

        elif tipo_linea == "Línea de medicamentos líquidos y semisólidos":
            sheet_to_use = "MR 1 líquidos y semisólidos"
            st.markdown("Seleccione las etapas que aplican al proceso:")
            etapas_liquidas = [
                "Verificación de prerrequisitos de validación",
                "Pesaje/Dispensación de materias primas",
                "Disolución/Dispersión",
                "Homogenización",
                "Filtración",
                "Envase frascos",
                "Envase sobres",
                "Envase tubos",
                "Empaque manual frascos",
                "Empaque manual sobre",
                "Empaque tubos"
            ]
            for etapa in etapas_liquidas:
                if st.toggle(etapa):
                    etapas_seleccionadas.append(etapa)

    elif tipo_validacion == "Validación de limpieza":
        sheet_to_use = "MR 1 limpieza"
        st.markdown("Seleccione las etapas que aplican al proceso de limpieza:")
        etapas_limpieza = [
            "Verificación de prerrequisitos de validación",
            "Limpieza preliminar y desmonte del equipo (piezas móviles)",
            "Limpieza de piezas móviles y parte interna de los equipos",
            "Seguimiento al proceso de limpieza",
            "Uso, desmonte y prelavado de las mangas",
            "Verificación y limpieza de las mangas"
        ]
        for etapa in etapas_limpieza:
            if st.toggle(etapa):
                etapas_seleccionadas.append(etapa)

    if etapas_seleccionadas and sheet_to_use:
        if st.button("Generar matriz de riesgo"):
            st.success(f"¡Matriz de riesgo generada con éxito!\nEtapas seleccionadas: {', '.join(etapas_seleccionadas)}")
            try:
                df = pd.read_excel(archivo, sheet_name=sheet_to_use, header=None)

                rangos_por_hoja = {
                    "MR 1 sólidos": {
                        etapa: (i + 1, i + 2) for i, etapa in enumerate([
                            "Verificación de prerrequisitos de validación",
                            "Pesaje/Dispensación de materias primas",
                            "Pulverización",
                            "Pelletización",
                            "Granulacion",
                            "Secado",
                            "Compactación",
                            "Mezcla (Lubricación)",
                            "Encapsulado",
                            "Compresión",
                            "Recubrimiento",
                            "Grageado",
                            "Revisión",
                            "Envase blíster",
                            "Envase foil",
                            "Envase frasco",
                            "Envase sobre",
                            "Envase tubo",
                            "Empaque blíster",
                            "Empaque manual foil",
                            "Empaque frasco",
                            "Empaque tubo",
                            "Recogida de blísters",
                            "Codificado manual"
                        ])
                    },
                    "MR 1 líquidos y semisólidos": {
                        etapa: (i + 1, i + 2) for i, etapa in enumerate([
                            "Verificación de prerrequisitos de validación",
                            "Pesaje/Dispensación de materias primas",
                            "Disolución/Dispersión",
                            "Homogenización",
                            "Filtración",
                            "Envase frascos",
                            "Envase sobres",
                            "Envase tubos",
                            "Empaque manual frascos",
                            "Empaque manual sobre",
                            "Empaque tubos"
                        ])
                    },
                    "MR 1 limpieza": {
                        etapa: (i + 1, i + 2) for i, etapa in enumerate([
                            "Verificación de prerrequisitos de validación",
                            "Limpieza preliminar y desmonte del equipo (piezas móviles)",
                            "Limpieza de piezas móviles y parte interna de los equipos",
                            "Seguimiento al proceso de limpieza",
                            "Uso, desmonte y prelavado de las mangas",
                            "Verificación y limpieza de las mangas"
                        ])
                    }
                }

                rangos_para_hoja_actual = rangos_por_hoja.get(sheet_to_use, {})
                if not rangos_para_hoja_actual:
                    st.error(f"No se encontraron rangos definidos para la hoja '{sheet_to_use}'.")
                    st.stop()

                encabezado = df.iloc[[0]]
                bloques = []

                for etapa in etapas_seleccionadas:
                    if etapa in rangos_para_hoja_actual:
                        inicio, fin = rangos_para_hoja_actual[etapa]
                        bloques.append(df.iloc[inicio:fin])
                    else:
                        st.warning(f"La etapa '{etapa}' no tiene rangos definidos.")

                tabla = pd.concat([encabezado] + bloques, ignore_index=True)

                st.session_state.edited_data_table = st.data_editor(
                    tabla,
                    use_container_width=True,
                    num_rows="dynamic",
                    key="editor_riesgo"
                )

                buffer = io.BytesIO()
                st.session_state.edited_data_table.iloc[:, 0] = st.session_state.edited_data_table.iloc[:, 0].ffill()
                st.session_state.edited_data_table.to_excel(buffer, index=False, header=False)
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
                            ws.merge_cells(start_row=start_row, start_column=col_to_merge, end_row=row - 1, end_column=col_to_merge)
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


