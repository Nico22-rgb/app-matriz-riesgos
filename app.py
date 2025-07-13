import streamlit as st
import pandas as pd
import io
import base64
from PIL import Image
import numpy as np
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
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <img src="data:image/png;base64,{base64.b64encode(encoded).decode()}" width="300">
            </div>
            """,
            unsafe_allow_html=True
        )
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
        if "excel_buffer" not in st.session_state:
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

                    # Animación de globos
                    st.balloons()

                    st.success("¡Matriz de riesgo generada con éxito!")

                except Exception as e:
                    st.error(f"Ocurrió un error al procesar el archivo: {e}")

        # Mostrar botón de descarga solo si la matriz fue generada
        if "excel_buffer" in st.session_state:
            st.download_button(
                label="Descargar matriz de riesgo 📥",
                data=st.session_state['excel_buffer'].getvalue(),
                file_name="matriz_riesgo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                on_click=lambda: st.session_state.update({"descarga_realizada": True})
            )
            
            # Mostrar multiselect solo después de descargar
            if st.session_state.get("descarga_realizada", False):
                st.markdown("<h5>De acuerdo con la matriz de riesgo generada, seleccione las etapas que involucran operaciones con criticidad alta:</h5>", unsafe_allow_html=True)
                selected_alta = st.multiselect(
                    "Seleccione las etapas que involucran operaciones con criticidad alta:",
                    options=st.session_state['etapas_seleccionadas'],
                    key="alta_seleccion"
                )

                if selected_alta:
                    operaciones_texto = ', '.join(selected_alta)
                    st.info(f"Las etapas que involucran operaciones críticas son: {operaciones_texto}")

                    if st.button("Generar matriz de priorización del riesgo"):
                        st.session_state['mostrar_matriz'] = True
                        # Mostrar imagen con zonas clicables solo si se activó el botón

# Mostrar imagen con zonas clicables solo si se activó el botón
if st.session_state.get('mostrar_matriz', False):
    def mostrar_imagen_con_zonas(path_png_transparente):
        try:
            with open(path_png_transparente, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode()
            
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <img src="data:image/png;base64,{encoded}" width="800">
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Error al cargar la imagen: {e}")

    mostrar_imagen_con_zonas("Matriz de priorizacion de riesgos.png")
   
   st.markdown('**"Ubica en la matriz el nivel de riesgo asociado a tu operación/etapa para saber si es necesario implementar controles adicionales durante la validación."**')

    # Inicializar estado para Área Roja
    if "area_roja_consultada" not in st.session_state:
        st.session_state['area_roja_consultada'] = False

    # Expander para áreas
    with st.expander("🟢 Área Verde"):
        st.write("No es necesario implementar controles adicionales en esta operación-etapa para demostrar que la verificación a ser efectuada es lo suficientemente robusta para dar un concepto final Se recomienda monitoreo rutinario.")
    
    with st.expander("🟡 Área Amarilla"):
        st.write("Considera implementar acciones o controles adicionales durante los seguimientos de validación para demostrar que la verificación a ser efectuada es lo suficientemente robusta para dar un concepto final.")
    
    # Expander para Área Roja con seguimiento de interacción
    with st.expander("🔴 Área Roja"):
        st.write("Es necesario implementar acciones o controles adicionales durante los seguimientos de validación para garantizar que la verificación a ser efectuada es lo suficientemente robusta para dar un concepto final.")
        # Actualizar estado solo si no se ha consultado antes (evitar reinicio)
        if not st.session_state.get('area_roja_consultada', False):
            st.session_state['area_roja_consultada'] = True
            st.rerun()  # Forzar recarga para reflejar el cambio

    # Mostrar Plan de Muestreo solo después de interactuar con Área Roja
    if st.session_state.get('area_roja_consultada', False):
        # Título centrado con margen inferior
        st.markdown("""
            <h3 style='text-align: center; color: #2c3e50; margin-bottom: 30px;'>Plan de Muestreo</h3>
        """, unsafe_allow_html=True)

        # Contenedor con imagen y texto separados con espacio
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: center; gap: 30px; margin-bottom: 35px;">
                <img src="data:image/png;base64,{base64.b64encode(open('muestreo.png', 'rb').read()).decode()}" 
                     style="width: 130px; height: auto; border-radius: 5px;" />
                <p style="text-align: justify; max-width: 600px;">
                    La elaboración de esta propuesta de plan de muestreo está basada en la fórmula para el cálculo del tamaño de muestra 
                    para poblaciones de tamaño finito del capítulo <b><1010></b> de la Farmacopea de los Estados Unidos de América, y en 
                    las recomendaciones del procedimiento estándar de operación <b>PSO-VAL-007</b> sobre el muestreo y análisis de datos en la 
                    validación de procesos de manufactura en Altea Farmacéutica S.A.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Espacio adicional antes del siguiente componente
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        # Formulario en una fila
        with st.expander("Por favor diligencia los campos correspondientes basado en la matriz de riesgo obtenida para el proceso ", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                etapa = st.selectbox("Etapa", ["Verificación", "Pesaje", "Limpieza", "Mezcla"])
            with col2:
                operacion = st.selectbox("Operación", ["Prueba 1", "Prueba 2", "Inspección"])
            with col3:
                atributo = st.selectbox("Atributo", ["Dimensión", "Peso", "Pureza"])

            col4, col5 = st.columns(2)
            with col4:
                criticidad = st.select_slider("Nivel de Criticidad", options=["Bajo", "Moderado", "Alto"])
            with col5:
                aql = st.number_input("Nivel de AQL (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)

