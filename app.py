import streamlit as st
import pandas as pd
import io
from PIL import Image
from openpyxl import load_workbook
from openpyxl.styles import Alignment, PatternFill
from openpyxl.formatting.rule import FormulaRule
import requests # Se mantiene requests para la imagen de placeholder

# Configuración inicial de la página de Streamlit
st.set_page_config(page_title="Análisis de Riesgos", layout="centered")

# Inicializar st.session_state para la tabla editada si no existe
# Esto asegura que los cambios del usuario persistan a través de las re-ejecuciones de la app.
if 'edited_data_table' not in st.session_state:
    st.session_state.edited_data_table = pd.DataFrame()
# La variable 'guardar_cambios' no es necesaria con la implementación actual de st.data_editor
# if 'guardar_cambios' not in st.session_state:
#     st.session_state.guardar_cambios = False

# Título principal de la aplicación
st.markdown("<h1 style='text-align: center;'>Análisis de Riesgos - Área de Validaciones</h1>", unsafe_allow_html=True)

# Carga y visualización de la imagen del logo
# Se utiliza una URL de marcador de posición para asegurar la ejecución sin archivos locales.
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

# Sección para subir el archivo de la base de datos de las matrices de riesgo
st.markdown("<h5>Por favor sube el archivo de la base de datos de las matrices de riesgo</h5>", unsafe_allow_html=True)
archivo = st.file_uploader("", type=[".xlsx"])

# Lógica principal de la aplicación si se ha subido un archivo
if archivo:
    # Selección del tipo de validación a realizar
    # Se añade una 'key' para asegurar que el estado de este widget se maneje correctamente
    tipo_validacion = st.selectbox("Seleccione el tipo de validación a realizar", [
        "Validación de procesos", "Validación de campaña", "Validación de limpieza"
    ], index=None, key="tipo_validacion_select")

    etapas_seleccionadas = []
    sheet_to_use = None # Variable para almacenar el nombre de la hoja a usar

    # Lógica para determinar las etapas y la hoja según el tipo de validación y línea
    if tipo_validacion in ["Validación de procesos", "Validación de campaña"]:
        # Selección de la línea de fabricación del producto
        # Se añade una 'key' para asegurar que el estado de este widget se maneje correctamente
        tipo_linea = st.selectbox("¿A qué línea de fabricación pertenece su producto?", [
            "Línea de medicamentos sólidos",
            "Línea de medicamentos líquidos y semisólidos"
        ], index=None, key="tipo_linea_select")

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
                # Se añade una 'key' única para cada toggle para manejar su estado
                if st.toggle(etapa, key=f"toggle_solidos_{etapa}"):
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
                # Se añade una 'key' única para cada toggle para manejar su estado
                if st.toggle(etapa, key=f"toggle_liquidos_{etapa}"):
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
            # Se añade una 'key' única para cada toggle para manejar su estado
            if st.toggle(etapa, key=f"toggle_limpieza_{etapa}"):
                etapas_seleccionadas.append(etapa)

    # Botón para generar la matriz de riesgo
    # Este botón siempre regenerará la tabla y la guardará en session_state
    if st.button("Generar matriz de riesgo"):
        if not etapas_seleccionadas or not sheet_to_use:
            st.warning("Por favor, selecciona al menos una etapa y un tipo de validación/línea de fabricación.")
        else:
            st.success(f"¡Matriz de riesgo generada con éxito!\nEtapas seleccionadas: {', '.join(etapas_seleccionadas)}")
            try:
                # Lectura del archivo Excel desde la hoja determinada, sin encabezados automáticos
                df = pd.read_excel(archivo, sheet_name=sheet_to_use, header=None)

                # Definición de los rangos de filas para cada etapa, organizados por nombre de hoja.
                # ¡IMPORTANTE!: Ajusta estos rangos según la estructura EXACTA de tu Excel.
                # Los índices son base 0 para Pandas, donde la fila 1 de Excel es el índice 0.
                rangos_por_hoja = {
                    "MR 1 sólidos": {
                        "Verificación de prerrequisitos de validación": (1, 2), # Fila 2 de Excel
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

                # Seleccionar el diccionario de rangos correcto para la hoja actual
                rangos_para_hoja_actual = rangos_por_hoja.get(sheet_to_use, {})
                if not rangos_para_hoja_actual:
                    st.error(f"No se encontraron rangos definidos para la hoja '{sheet_to_use}'. Por favor, verifica la configuración.")
                    st.session_state.edited_data_table = pd.DataFrame() # Limpiar tabla en caso de error
                    st.stop()

                encabezado = df.iloc[[0]]
                bloques = []

                for etapa in etapas_seleccionadas:
                    if etapa in rangos_para_hoja_actual:
                        inicio, fin = rangos_para_hoja_actual[etapa]
                        bloque_actual = df.iloc[inicio:fin]
                        bloques.append(bloque_actual)
                    else:
                        st.warning(f"La etapa '{etapa}' no tiene rangos definidos para la hoja '{sheet_to_use}'.")

                tabla_generada_excel = pd.concat([encabezado] + bloques, ignore_index=True)
                st.session_state.edited_data_table = tabla_generada_excel # Guardar la tabla generada en session_state

            except Exception as e:
                st.error(f"Ocurrió un error al procesar el archivo: {e}")
                st.session_state.edited_data_table = pd.DataFrame() # Limpiar en caso de error

    # Mostrar el editor de datos si la tabla en session_state no está vacía
    if not st.session_state.edited_data_table.empty:
        st.markdown("### Por favor completa tu matriz de riesgo:")
        # El st.data_editor se inicializa con el DataFrame de session_state.
        # Cualquier edición del usuario se guarda automáticamente de vuelta en st.session_state.edited_data_table
        # gracias a la asignación directa y la 'key' única.
        st.session_state.edited_data_table = st.data_editor(st.session_state.edited_data_table,
                                                            use_container_width=True,
                                                            num_rows="dynamic",
                                                            key="risk_matrix_editor") # Usar una key fija para persistencia

        # Usar el DataFrame de session_state para todas las operaciones subsiguientes (descargas)
        tabla_final_para_descarga = st.session_state.edited_data_table

        # --- LÓGICA PARA PRESERVAR FÓRMULAS ---
        # Define las columnas que deben contener fórmulas y su plantilla
        # El formato es: {Índice de Columna en Excel (1-basado): "Plantilla de Fórmula"}
        # O (columna 15): =POWER((J2*L2*N2),1/3)
        # P (columna 16) y Q (columna 17): =IF(O2<1.33,"Bajo",IF(AND(O2>=1.33,O2<2.67),"Moderado",IF(AND(O2>=2.67,O2<4),"Alto")))
        formula_columns_info = {
            15: "=POWER((J{row}*L{row}*N{row}),1/3)",
            16: "=IF(O{row}<1.33,\"Bajo\",IF(AND(O{row}>=1.33,O{row}<2.67),\"Moderado\",IF(AND(O{row}>=2.67,O{row}<4),\"Alto\",\"\")))",
            17: "=IF(P{row}=\"Alto\",\"Sí\",\"No\")" # Corregido: La fórmula de Q depende de P
        }
        # --- FIN DE LA LÓGICA PARA PRESERVAR FÓRMULAS ---

        buffer = io.BytesIO()
        # Rellenar valores nulos en la PRIMERA columna con el valor anterior no nulo
        tabla_final_para_descarga.iloc[:, 0] = tabla_final_para_descarga.iloc[:, 0].ffill()
        tabla_final_para_descarga.to_excel(buffer, index=False, header=False)
        buffer.seek(0)

        wb = load_workbook(buffer)
        ws = wb.active

        # Lógica para combinar celdas SOLO en la PRIMERA columna
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

        # Re-insertar fórmulas en las columnas definidas
        # Se itera sobre las filas de datos (desde la fila 2 de Excel, después del encabezado)
        for r_idx in range(2, ws.max_row + 1):
            for col_idx, formula_template in formula_columns_info.items():
                # Formatear la cadena de la fórmula con el número de fila actual
                formula_string = formula_template.format(row=r_idx)
                # Establecer la fórmula en la celda correspondiente
                ws.cell(row=r_idx, column=col_idx).value = formula_string

        # <<< FORMATO CONDICIONAL >>>
        rojo = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        naranja = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
        verde = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        amarillo = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

        # Aplicar formato condicional a la columna P (índice 16)
        # Rango completo de la columna P desde la fila 2
        ws.conditional_formatting.add(f"P2:P{ws.max_row}", FormulaRule(formula=['P2="Alto"'], fill=rojo))
        ws.conditional_formatting.add(f"P2:P{ws.max_row}", FormulaRule(formula=['P2="Moderado"'], fill=naranja))
        ws.conditional_formatting.add(f"P2:P{ws.max_row}", FormulaRule(formula=['P2="Bajo"'], fill=verde))

        # Aplicar formato condicional a la columna Q (índice 17)
        # Rango completo de la columna Q desde la fila 2
        ws.conditional_formatting.add(f"Q2:Q{ws.max_row}", FormulaRule(formula=['Q2="Sí"'], fill=amarillo))
        # <<< FIN FORMATO >>>

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

  
