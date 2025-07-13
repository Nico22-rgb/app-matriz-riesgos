import streamlit as st
import pandas as pd
import io
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
            encoded = image_file.read()
        st.image(encoded, use_column_width=True)
    except Exception as e:
        st.warning(f"No se pudo cargar el logo. Error: {e}")
        st.info("Verifica que el archivo exista y esté en formato PNG transparente.")

# Muestra el logo adaptativo
mostrar_logo_adaptable("altea.png")

# ======== Autenticación ========
CONTRASENA = "M"

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

# Función para cargar datos con caché
@st.cache_data
def load_excel(file, sheet_name):
    return pd.read_excel(file, sheet_name=sheet_name, header=0)  # Usar la primera fila como encabezado

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
        if st.button("Generar matriz de riesgo con Excel"):
            try:
                df = load_excel(archivo, sheet_to_use)

                rangos_por_hoja = {
                    "MR 1 sólidos": {
                        "Verificación de prerrequisitos de validación": (0, 1),
                        "Pesaje/Dispensación de materias primas": (1, 2),
                        "Pulverización": (2, 3),
                        "Pelletización": (3, 4),
                        "Granulacion": (4, 5),
                        "Secado": (5, 6),
                        "Compactación": (6, 7),
                        "Mezcla (Lubricación)": (7, 8),
                        "Encapsulado": (8, 9),
                        "Compresión": (9, 10),
                        "Recubrimiento": (10, 11),
                        "Grageado": (11, 12),
                        "Revisión": (12, 13),
                        "Envase blíster": (13, 14),
                        "Envase foil": (14, 15),
                        "Envase frasco": (15, 16),
                        "Envase sobre": (16, 17),
                        "Envase tubo": (17, 18),
                        "Empaque blíster": (18, 19),
                        "Empaque manual foil": (19, 20),
                        "Empaque frasco": (20, 21),
                        "Empaque tubo": (21, 22),
                        "Recogida de blísters": (22, 23),
                        "Codificado manual": (23, 24)
                    },
                    "MR 1 líquidos y semisólidos": {
                        "Verificación de prerrequisitos de validación": (0, 1),
                        "Pesaje/Dispensación de materias primas": (1, 2),
                        "Disolución/Dispersión": (2, 3),
                        "Homogenización": (3, 4),
                        "Filtración": (4, 5),
                        "Envase frascos": (5, 6),
                        "Envase sobres": (6, 7),
                        "Envase tubos": (7, 8),
                        "Empaque manual frascos": (8, 9),
                        "Empaque manual sobre": (9, 10),
                        "Empaque tubos": (10, 11)
                    },
                    "MR 1 limpieza": {
                        "Verificación de prerrequisitos de validación": (0, 1),
                        "Limpieza preliminar y desmonte del equipo (piezas móviles)": (1, 2),
                        "Limpieza de piezas móviles y parte interna de los equipos": (2, 3),
                        "Seguimiento al proceso de limpieza": (3, 4),
                        "Uso, desmonte y prelavado de las mangas": (4, 5),
                        "Verificación y limpieza de las mangas": (5, 6)
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
                        bloques.append(df.iloc[inicio:fin + 1])  # +1 para incluir el rango completo
                    else:
                        st.warning(f"La etapa '{etapa}' no tiene rangos definidos.")

                tabla = pd.concat([encabezado] + bloques, ignore_index=True)
                buffer = io.BytesIO()
                tabla.to_excel(buffer, index=False)
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

                # Aplicar fórmulas en columnas O (15), P (16), Q (17) basadas en J (10), L (12), N (14)
                for r_idx in range(2, ws.max_row + 1):
                    ws[f"O{r_idx}"].value = f"=ROUND(POWER((J{r_idx}*L{r_idx}*N{r_idx}),1/3),1)"  # Redondear a 1 decimal
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
                    column_letter = get_column_letter(column[0].column)
                    if column_letter == 'P':
                        ws.column_dimensions[column_letter].width = 30  # Aproximadamente 214 píxeles
                    elif column_letter == 'Q':
                        ws.column_dimensions[column_letter].width = 14  # Aproximadamente 99 píxeles
                    else:
                        max_length = 0
                        for cell in column:
                            try:
                                if cell.value is not None:
                                    cell_value_str = str(cell.value)
                                    max_length = max(max_length, len(cell_value_str))
                            except Exception:
                                pass
                        ws.column_dimensions[column_letter].width = max_length + 3

                # Alinear todo el contenido al centro
                for row in ws.iter_rows():
                    for cell in row:
                        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

                # Guardar el archivo Excel en la sesión
                output = io.BytesIO()
                wb.save(output)
                output.seek(0)
                st.session_state['excel_buffer'] = output
                st.session_state['etapas_seleccionadas'] = etapas_seleccionadas  # Guardar etapas seleccionadas

                # Animación de confeti estática
                st.markdown(
                    """
                    <style>
                    .confetti-container {
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        pointer-events: none;
                        z-index: 1000;
                        display: none;
                    }
                    .confetti {
                        position: absolute;
                        width: 10px;
                        height: 10px;
                        background: hsl(var(--hue), 70%, 50%);
                        border-radius: 50%;
                        animation: fall 2s linear forwards;
                    }
                    @keyframes fall {
                        0% { transform: translateY(-100vh); opacity: 1; }
                        100% { transform: translateY(100vh); opacity: 0; }
                    }
                    .confetti:nth-child(2n) { --hue: 120; }
                    .confetti:nth-child(3n) { --hue: 240; }
                    .confetti:nth-child(4n) { --hue: 60; }
                    </style>
                    <div class="confetti-container" id="confetti-container"></div>
                    <script>
                    function createConfetti() {
                        const container = document.getElementById('confetti-container');
                        container.innerHTML = '';
                        for (let i = 0; i < 50; i++) {
                            const confetti = document.createElement('div');
                            confetti.className = 'confetti';
                            confetti.style.left = Math.random() * 100 + 'vw';
                            confetti.style.animationDelay = (Math.random() * 0.5) + 's';
                            confetti.style.setProperty('--hue', Math.random() * 360);
                            container.appendChild(confetti);
                        }
                        container.style.display = 'block';
                        setTimeout(() => {
                            container.style.display = 'none';
                        }, 2000);
                    }
                    document.querySelector('button').onclick = createConfetti;
                    </script>
                    """,
                    unsafe_allow_html=True
                )

                st.success("¡Matriz de riesgo generada con éxito!")

                # Botón de descarga
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                        <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(st.session_state['excel_buffer'].read()).decode()}" download="matriz_riesgo.xlsx">
                            <button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Descargar matriz de riesgo 📥</button>
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Selección de operaciones con criticidad Alta
                st.markdown("**De acuerdo con la matriz de riesgo generada, seleccione las operaciones con criticidad Alta:**")
                selected_alta = st.multiselect(
                    "Seleccione las operaciones:",
                    options=etapas_seleccionadas,
                    key="alta_seleccion"
                )
                if selected_alta:
                    st.write(f"Operaciones seleccionadas con criticidad Alta: {', '.join(selected_alta)}")

            except Exception as e:
                st.error(f"Ocurrió un error al procesar el archivo: {e}")

else:
    st.info("Por favor, sube un archivo Excel para comenzar.")
