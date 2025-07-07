import streamlit as st
import pandas as pd
import io
from PIL import Image
from openpyxl import load_workbook
from openpyxl.styles import Alignment, PatternFill, Font
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter

# Configuración inicial de la página de Streamlit
st.set_page_config(page_title="Análisis de Riesgos", layout="centered")

# Inicializar el estado de la tabla editada solo si aún no existe en session_state
if 'edited_data_table' not in st.session_state:
    st.session_state.edited_data_table = pd.DataFrame()
if 'guardar_cambios' not in st.session_state:
    st.session_state.guardar_cambios = False

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
                        "Verificación de prerrequisitos de validación": (1, 2),
                        "Pesaje/Dispensación de materias primas": (2, 3),
                        "Pulverización": (3, 4),
                        "Pelletización": (4, 5),
                        "Granulacion": (5, 6),
                        "Secado": (6, 7),
                        "Compactación": (7, 8),
                        "Mezcla (Lubricación)": (8, 9),
                        "Encapsulado": (9, 10),
                        "Compresión": (10, 11),
                        "Recubrimiento": (11, 12),
                        "Grageado": (12, 13),
                        "Revisión": (13, 14),
                        "Envase blíster": (14, 15),
                        "Envase foil": (15, 16),
                        "Envase frasco": (16, 17),
                        "Envase sobre": (17, 18),
                        "Envase tubo": (18, 19),
                        "Empaque blíster": (19, 20),
                        "Empaque manual foil": (20, 21),
                        "Empaque frasco": (21, 22),
                        "Empaque tubo": (22, 23),
                        "Recogida de blísters": (23, 24),
                        "Codificado manual": (24, 25)
                    },
                    "MR 1 líquidos y semisólidos": {
                        "Verificación de prerrequisitos de validación": (1, 2),
                        "Pesaje/Dispensación de materias primas": (2, 3),
                        "Disolución/Dispersión": (3, 4),
                        "Homogenización": (4, 5),
                        "Filtración": (5, 6),
                        "Envase frascos": (6, 7),
                        "Envase sobres": (7, 8),
                        "Envase tubos": (8, 9),
                        "Empaque manual frascos": (9, 10),
                        "Empaque manual sobre": (10, 11),
                        "Empaque tubos": (11, 12)
                    },
                    "MR 1 limpieza": {
                        "Verificación de prerrequisitos de validación": (1, 2),
                        "Limpieza preliminar y desmonte del equipo (piezas móviles)": (2, 3),
                        "Limpieza de piezas móviles y parte interna de los equipos": (3, 4),
                        "Seguimiento al proceso de limpieza": (4, 5),
                        "Uso, desmonte y prelavado de las mangas": (5, 6),
                        "Verificación y limpieza de las mangas": (6, 7)
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
                st.session_state.edited_data_table = tabla.copy()

            except Exception as e:
                st.error(f"Ocurrió un error al procesar el archivo: {e}")

    if not st.session_state.edited_data_table.empty:
        st.markdown("### Por favor completa tu matriz de riesgo:")
        edited_table = st.data_editor(
            st.session_state.edited_data_table,
            use_container_width=True,
            num_rows="dynamic",
            key="editor_riesgo"
        )

        if st.button("Guardar cambios en la matriz"):
            st.session_state.edited_data_table = edited_table.copy()
            st.success("✅ Cambios guardados correctamente. Puedes descargar el archivo actualizado.")

        if st.session_state.edited_data_table is not None:
            buffer = io.BytesIO()
            st.session_state.edited_data_table.iloc[:, 0] = st.session_state.edited_data_table.iloc[:, 0].ffill()
            st.session_state.edited_data_table.to_excel(buffer, index=False, header=False)
            buffer.seek(0)

            wb = load_workbook(buffer)
            ws = wb.active

             # Aplicar formato a la fila 1 (encabezado)
            palegreen_fill = PatternFill(start_color="FFC0E080", end_color="FFC0E080", fill_type="solid")
            bold_font = Font(bold=True)
            center_alignment = Alignment(horizontal="center", vertical="center")
            for cell in ws[1]:
                cell.fill = palegreen_fill
                cell.font = bold_font
                cell.alignment = center_alignment

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


            for r_idx in range(2, ws.max_row + 1):
                ws[f"O{r_idx}"].value = f"=POWER((J{r_idx}*L{r_idx}*N{r_idx}),1/3)"
                ws[f"P{r_idx}"].value = f"=IF(O{r_idx}<1.33,\"Bajo\",IF(AND(O{r_idx}>=1.33,O{r_idx}<3),\"Moderado\",IF(AND(O{r_idx}>=3,O{r_idx}<4),\"Alto\",\"\")))"
                ws[f"Q{r_idx}"].value = f"=IF(P{r_idx}=\"Alto\",\"Sí\",\"No\")"

            rojo = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
            naranja = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
            verde = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
            amarillo = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

            ws.conditional_formatting.add("P2:P1048576", FormulaRule(formula=["P2=\"Alto\""], fill=rojo))
            ws.conditional_formatting.add("P2:P1048576", FormulaRule(formula=["P2=\"Moderado\""], fill=naranja))
            ws.conditional_formatting.add("P2:P1048576", FormulaRule(formula=["P2=\"Bajo\""], fill=verde))
            ws.conditional_formatting.add("Q2:Q1048576", FormulaRule(formula=["Q2=\"Sí\""], fill=amarillo))

            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        if cell.value is not None:
                            cell_value_str = str(cell.value)
                            if cell.data_type == 'f':
                                if column_letter in ['P', 'Q']:
                                    max_length = max(max_length, len("Moderado"))
                                else:
                                    max_length = max(max_length, len(cell_value_str))
                            else:
                                max_length = max(max_length, len(cell_value_str))
                    except Exception:
                        pass
                adjusted_width = (max_length + 3)
                ws.column_dimensions[column_letter].width = adjusted_width
            # Alinear todo el contenido del Excel al centro (horizontal y vertical)
            for row in ws.iter_rows():
                for cell in row:
                   # Alinear todo el contenido del Excel al centro y ajustar texto
                    for row in ws.iter_rows():
                        for cell in row:
                            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


            output = io.BytesIO()
            wb.save(output)
            output.seek(0)

            st.download_button(
                label="📥 Descargar matriz de riesgo en Excel",
                data=output,
                file_name="matriz_riesgo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("Por favor, sube un archivo Excel para comenzar.")
