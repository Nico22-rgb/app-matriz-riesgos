import streamlit as st
import pandas as pd
import io
import base64
from PIL import Image
from openpyxl import load_workbook
from openpyxl.styles import Alignment, PatternFill, Font
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter

# Configuración de página
st.set_page_config(page_title="Análisis de Riesgos", layout="centered")

# Imagen y título inicial
st.markdown("<h1 style='text-align: center;'>Análisis de Riesgos - Área de Validaciones</h1>", unsafe_allow_html=True)

def mostrar_logo_adaptable(path_png_transparente):
    try:
        with open(path_png_transparente, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()

        st.markdown(f"""
        <style>
            .logo-container {{
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            body[data-theme="dark"] .logo-container {{
                background-color: #0e1117;
            }}
            body[data-theme="light"] .logo-container {{
                background-color: #f0f2f6;
            }}
            .logo-container img {{
                width: 300px;
            }}
        </style>
        <div class="logo-container">
            <img src="data:image/png;base64,{encoded}" alt="Logo Altea" />
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"No se pudo cargar el logo. Error: {e}")
        st.info("Verifica que el archivo exista y esté en formato PNG transparente.")

# Muestra el logo adaptativo
mostrar_logo_adaptable("altea.png")

# ======== Autenticación ========
CONTRASENA = "Motasyjacobo22"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("## 🔐 Ingreso restringido")
    contrasena = st.text_input("Ingrese la contraseña para continuar:", type="password")
    if contrasena == CONTRASENA:
        st.session_state.autenticado = True
        st.success("✅ Acceso concedido.")
    else:
        if contrasena != "":
            st.error("❌ Contraseña incorrecta.")
        st.stop()  # Detiene la ejecución hasta que se autentique correctamente

# ======== Carga de archivo y selección de opciones ========
st.markdown("<h5>Por favor sube el archivo de la base de datos de las matrices de riesgo</h5>", unsafe_allow_html=True)
archivo = st.file_uploader("", type=["xlsx"])

# Inicializar variable para controlar si la matriz fue generada
if "matriz_generada" not in st.session_state:
    st.session_state.matriz_generada = False

# Función para cargar datos con caché
@st.cache_data
def load_excel(file, sheet_name):
    return pd.read_excel(file, sheet_name=sheet_name, header=None)

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
            st.session_state.matriz_generada = True
            st.success(f"¡Matriz de riesgo generada con éxito!\nEtapas seleccionadas: {', '.join(etapas_seleccionadas)}")
            try:
                df = load_excel(archivo, sheet_to_use)

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
                    st.session_state.matriz_generada = False
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
                st.session_state.matriz_generada = False
                st.stop()

    # ======== Edición de la tabla (solo si la matriz fue generada) ========
    if st.session_state.get("matriz_generada", False) and "edited_data_table" in st.session_state and not st.session_state.edited_data_table.empty:
        # Contenedor para la tabla
        with st.container():
            st.markdown("### Por favor completa tu matriz de riesgo:")
            # Mostrar feedback si se editó la tabla
            if st.session_state.get("editor_riesgo", {}).get("edited_rows"):
                st.info("Cambios en la tabla guardados automáticamente.")
            
            # Configuración de columnas para validación de datos
            column_config = {
                9: st.column_config.NumberColumn("Severidad", min_value=1, max_value=4, step=1),  # Columna J
                11: st.column_config.NumberColumn("Ocurrencia", min_value=1, max_value=4, step=1),  # Columna L
                13: st.column_config.NumberColumn("Detección", min_value=1, max_value=4, step=1)  # Columna N
            }
            
            # Mostrar la tabla interactiva
            edited_table = st.data_editor(
                st.session_state.edited_data_table,
                use_container_width=True,
                num_rows="dynamic",
                column_config=column_config,
                key="editor_riesgo"
            )

            # Actualizar session_state con los cambios
            st.session_state.edited_data_table = edited_table.copy()

            # JavaScript para mantener el scroll en la tabla
            st.markdown("""
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    const tableContainer = document.querySelector('.element-container');
                    if (tableContainer) {
                        tableContainer.scrollIntoView({ behavior: 'smooth' });
                    }
                });
            </script>
            """, unsafe_allow_html=True)

        # Botón para descargar el Excel
        if st.button("📥 Generar y descargar matriz de riesgo en Excel"):
            buffer = io.BytesIO()
            st.session_state.edited_data_table.iloc[:, 0] = st.session_state.edited_data_table.iloc[:, 0].ffill()
            st.session_state.edited_data_table.to_excel(buffer, index=False, header=False)
            buffer.seek(0)

            wb = load_workbook(buffer)
            ws = wb.active

            # Aplicar formato a la fila 1 (encabezado)
            palegreen_fill = PatternFill(start_color="C0E080", end_color="C0E080", fill_type="solid")
            bold_font = Font(bold=True)
            center_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            for cell in ws[1]:
                cell.fill = palegreen_fill
                cell.font = bold_font
                cell.alignment = center_alignment

            # Combinar celdas automáticamente en columnas A (1), C (3), D (4)
            columnas_a_combinar = [1, 3, 4]
            for col_to_merge in columnas_a_combinar:
                current_value = None
                start_row = 2
                for row in range(2, ws.max_row + 1):
                    value = ws.cell(row=row, column=col_to_merge).value
                    value = str(value).strip() if value is not None else ""
                    if row == 2:
                        current_value = value
                        continue
                    if value != current_value or row == ws.max_row:
                        if row - start_row > 1 or (row == ws.max_row and value == current_value):
                            end_row = row if value != current_value else row + 1
                            ws.merge_cells(
                                start_row=start_row,
                                start_column=col_to_merge,
                                end_row=end_row - 1,
                                end_column=col_to_merge
                            )
                            ws.cell(row=start_row, column=col_to_merge).alignment = Alignment(
                                horizontal="center", vertical="center", wrap_text=True
                            )
                        current_value = value
                        start_row = row

            # Aplicar fórmulas en columnas O, P, Q
            for r_idx in range(2, ws.max_row + 1):
                ws[f"O{r_idx}"].value = f"=POWER((J{r_idx}*L{r_idx}*N{r_idx}),1/3)"
                ws[f"P{r_idx}"].value = f'=IF(O{r_idx}<1.33,"Bajo",IF(O{r_idx}<3,"Moderado","Alto"))'
                ws[f"Q{r_idx}"].value = f'=IF(P{r_idx}="Alto","Alta",IF(P{r_idx}="Moderado","Media","Baja"))'

            # Aplicar formato condicional
            rojo = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
            naranja = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
            verde = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")

            ws.conditional_formatting.add("P2:P" + str(ws.max_row), FormulaRule(formula=['P2="Alto"'], fill=rojo))
            ws.conditional_formatting.add("P2:P" + str(ws.max_row), FormulaRule(formula=['P2="Moderado"'], fill=naranja))
            ws.conditional_formatting.add("P2:P" + str(ws.max_row), FormulaRule(formula=['P2="Bajo"'], fill=verde))
            ws.conditional_formatting.add("Q2:Q" + str(ws.max_row), FormulaRule(formula=['Q2="Alta"'], fill=rojo))
            ws.conditional_formatting.add("Q2:Q" + str(ws.max_row), FormulaRule(formula=['Q2="Media"'], fill=naranja))
            ws.conditional_formatting.add("Q2:Q" + str(ws.max_row), FormulaRule(formula=['Q2="Baja"'], fill=verde))

            # Ajustar ancho de columnas
            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        if cell.value is not None:
                            cell_value_str = str(cell.value)
                            max_length = max(max_length, len(cell_value_str))
                    except Exception:
                        pass
                adjusted_width = max_length + 3
                ws.column_dimensions[column_letter].width = adjusted_width

            # Alinear todo el contenido al centro
            for row in ws.iter_rows():
                for cell in row:
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            # Guardar el archivo Excel
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
