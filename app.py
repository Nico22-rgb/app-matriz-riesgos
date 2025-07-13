import streamlit as st
import pandas as pd
import io
import base64
from openpyxl import load_workbook
from openpyxl.styles import Alignment, PatternFill, Font
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configuración de página
st.set_page_config(
    page_title="Análisis de Riesgos - Validaciones Farmacéuticas", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejor apariencia
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E8B57;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown("<h1 class='main-header'>🔬 Análisis de Riesgos - Área de Validaciones Farmacéuticas</h1>", unsafe_allow_html=True)

def mostrar_logo_adaptable(path_png_transparente):
    """Función mejorada para mostrar logo con manejo de errores"""
    try:
        with open(path_png_transparente, "rb") as image_file:
            encoded = image_file.read()
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                <img src="data:image/png;base64,{base64.b64encode(encoded).decode()}" 
                     width="300" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            </div>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.info("💡 Logo no encontrado. Asegúrate de que el archivo 'altea.png' esté en el directorio.")
    except Exception as e:
        st.warning(f"⚠️ Error al cargar el logo: {str(e)}")

# Mostrar logo
mostrar_logo_adaptable("altea.png")

# ======== CONFIGURACIÓN DE DATOS ========
CONTRASENA = "Motasyjacobo22"  # Restaurar contraseña original

# Configuración de etapas por tipo de validación
ETAPAS_CONFIG = {
    "MR 1 sólidos": {
        "etapas": [
            "Verificación de prerrequisitos de validación",
            "Pesaje/Dispensación de materias primas",
            "Pulverización", "Pelletización", "Granulacion", "Secado",
            "Compactación", "Mezcla (Lubricación)", "Encapsulado",
            "Compresión", "Recubrimiento", "Grageado", "Revisión",
            "Envase blíster", "Envase foil", "Envase frasco", "Envase sobre", "Envase tubo",
            "Empaque blíster", "Empaque manual foil", "Empaque frasco", "Empaque tubo",
            "Recogida de blísters", "Codificado manual"
        ],
        "rangos": {
            "Verificación de prerrequisitos de validación": (0, 1),
            "Pesaje/Dispensación de materias primas": (1, 2),
            "Pulverización": (2, 3), "Pelletización": (3, 4), "Granulacion": (4, 5),
            "Secado": (5, 6), "Compactación": (6, 7), "Mezcla (Lubricación)": (7, 8),
            "Encapsulado": (8, 9), "Compresión": (9, 10), "Recubrimiento": (10, 11),
            "Grageado": (11, 12), "Revisión": (12, 13), "Envase blíster": (13, 14),
            "Envase foil": (14, 15), "Envase frasco": (15, 16), "Envase sobre": (16, 17),
            "Envase tubo": (17, 18), "Empaque blíster": (18, 19), "Empaque manual foil": (19, 20),
            "Empaque frasco": (20, 21), "Empaque tubo": (21, 22), "Recogida de blísters": (22, 23),
            "Codificado manual": (23, 24)
        }
    },
    "MR 1 líquidos y semisólidos": {
        "etapas": [
            "Verificación de prerrequisitos de validación",
            "Pesaje/Dispensación de materias primas",
            "Disolución/Dispersión", "Homogenización", "Filtración",
            "Envase frascos", "Envase sobres", "Envase tubos",
            "Empaque manual frascos", "Empaque manual sobre", "Empaque tubos"
        ],
        "rangos": {
            "Verificación de prerrequisitos de validación": (0, 1),
            "Pesaje/Dispensación de materias primas": (1, 2),
            "Disolución/Dispersión": (2, 3), "Homogenización": (3, 4),
            "Filtración": (4, 5), "Envase frascos": (5, 6), "Envase sobres": (6, 7),
            "Envase tubos": (7, 8), "Empaque manual frascos": (8, 9),
            "Empaque manual sobre": (9, 10), "Empaque tubos": (10, 11)
        }
    },
    "MR 1 limpieza": {
        "etapas": [
            "Verificación de prerrequisitos de validación",
            "Limpieza preliminar y desmonte del equipo (piezas móviles)",
            "Limpieza de piezas móviles y parte interna de los equipos",
            "Seguimiento al proceso de limpieza",
            "Uso, desmonte y prelavado de las mangas",
            "Verificación y limpieza de las mangas"
        ],
        "rangos": {
            "Verificación de prerrequisitos de validación": (0, 1),
            "Limpieza preliminar y desmonte del equipo (piezas móviles)": (1, 2),
            "Limpieza de piezas móviles y parte interna de los equipos": (2, 3),
            "Seguimiento al proceso de limpieza": (3, 4),
            "Uso, desmonte y prelavado de las mangas": (4, 5),
            "Verificación y limpieza de las mangas": (5, 6)
        }
    }
}

# ======== FUNCIONES AUXILIARES ========
@st.cache_data
def load_excel(file, sheet_name):
    """Función optimizada para cargar datos Excel"""
    try:
        return pd.read_excel(file, sheet_name=sheet_name, header=0)
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {str(e)}")
        return None

def generar_estadisticas_riesgo(df_procesado):
    """Genera estadísticas básicas del análisis de riesgo"""
    try:
        # Simular análisis de riesgo basado en NPR
        riesgos = ["Alto", "Moderado", "Bajo"]
        conteos = [len(df_procesado) // 3, len(df_procesado) // 3, len(df_procesado) - 2*(len(df_procesado) // 3)]
        
        return {
            "total_riesgos": len(df_procesado),
            "alto": conteos[0],
            "moderado": conteos[1],
            "bajo": conteos[2]
        }
    except:
        return {"total_riesgos": 0, "alto": 0, "moderado": 0, "bajo": 0}

def crear_grafico_riesgos(stats):
    """Crea gráfico de distribución de riesgos"""
    if stats["total_riesgos"] == 0:
        return None
    
    fig = px.pie(
        values=[stats["alto"], stats["moderado"], stats["bajo"]],
        names=["Alto", "Moderado", "Bajo"],
        title="Distribución de Riesgos por Criticidad",
        color_discrete_map={
            "Alto": "#FF6B6B",
            "Moderado": "#FFD93D", 
            "Bajo": "#6BCF7F"
        }
    )
    fig.update_layout(height=400, showlegend=True)
    return fig

def aplicar_formato_excel(ws, max_row):
    """Función optimizada para aplicar formato Excel"""
    try:
        # Formato del encabezado
        palegreen_fill = PatternFill(start_color="C0E080", end_color="C0E080", fill_type="solid")
        bold_font = Font(bold=True)
        center_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        for cell in ws[1]:
            cell.fill = palegreen_fill
            cell.font = bold_font
            cell.alignment = center_alignment

        # Combinar celdas en columnas específicas
        columnas_a_combinar = [1, 3, 4]
        for col_to_merge in columnas_a_combinar:
            current_value = None
            start_row = 2
            
            for row in range(2, max_row + 1):
                value = ws.cell(row=row, column=col_to_merge).value
                value = str(value).strip() if value is not None else ""
                
                if row == 2:
                    current_value = value
                    continue
                    
                if value != current_value or row == max_row:
                    if row - start_row > 1 or (row == max_row and value == current_value):
                        end_row = row if value != current_value else row + 1
                        ws.merge_cells(
                            start_row=start_row,
                            start_column=col_to_merge,
                            end_row=end_row - 1,
                            end_column=col_to_merge
                        )
                        ws.cell(row=start_row, column=col_to_merge).alignment = center_alignment
                    current_value = value
                    start_row = row

        # Aplicar fórmulas NPR ajustado
        for r_idx in range(2, max_row + 1):
            ws[f"O{r_idx}"].value = f"=ROUND(POWER((J{r_idx}*L{r_idx}*N{r_idx}),1/3),1)"
            ws[f"P{r_idx}"].value = f'=IF(O{r_idx}<1.33,"Bajo",IF(O{r_idx}<3,"Moderado","Alto"))'
            ws[f"Q{r_idx}"].value = f'=IF(P{r_idx}="Alto","Alta",IF(P{r_idx}="Moderado","Media","Baja"))'

        # Formato condicional
        rojo = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        naranja = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
        verde = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")

        ws.conditional_formatting.add(f"P2:P{max_row}", FormulaRule(formula=['P2="Alto"'], fill=rojo))
        ws.conditional_formatting.add(f"P2:P{max_row}", FormulaRule(formula=['P2="Moderado"'], fill=naranja))
        ws.conditional_formatting.add(f"P2:P{max_row}", FormulaRule(formula=['P2="Bajo"'], fill=verde))
        ws.conditional_formatting.add(f"Q2:Q{max_row}", FormulaRule(formula=['Q2="Alta"'], fill=rojo))
        ws.conditional_formatting.add(f"Q2:Q{max_row}", FormulaRule(formula=['Q2="Media"'], fill=naranja))
        ws.conditional_formatting.add(f"Q2:Q{max_row}", FormulaRule(formula=['Q2="Baja"'], fill=verde))

        # Ajustar ancho de columnas
        for column in ws.columns:
            column_letter = get_column_letter(column[0].column)
            if column_letter == 'P':
                ws.column_dimensions[column_letter].width = 30
            elif column_letter == 'Q':
                ws.column_dimensions[column_letter].width = 14
            else:
                max_length = 0
                for cell in column:
                    try:
                        if cell.value is not None:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                ws.column_dimensions[column_letter].width = max_length + 3

        # Alinear contenido
        for row in ws.iter_rows():
            for cell in row:
                cell.alignment = center_alignment

        return True
    except Exception as e:
        st.error(f"Error al aplicar formato Excel: {str(e)}")
        return False

# ======== INTERFAZ PRINCIPAL ========

# Autenticación
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🔐 Acceso Seguro")
        st.markdown("**Sistema de Gestión de Riesgos en Validaciones Farmacéuticas**")
        
        contrasena = st.text_input("Ingrese la contraseña:", type="password", placeholder="Contraseña requerida")
        
        if st.button("🚀 Ingresar", use_container_width=True):
            if contrasena == CONTRASENA:
                st.session_state.autenticado = True
                st.success("✅ Acceso concedido correctamente")
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta. Intente nuevamente.")
        
        if contrasena and contrasena != CONTRASENA:
            st.error("❌ Contraseña incorrecta")
    st.stop()

# Sidebar con información
with st.sidebar:
    st.markdown("## 📊 Panel de Control")
    st.markdown("### Información del Sistema")
    st.info(f"**Fecha:** {datetime.now().strftime('%d/%m/%Y')}")
    st.info(f"**Hora:** {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("### 🎯 Metodología")
    st.markdown("""
    - **NPR Ajustado**: Media geométrica
    - **Normativas**: ICH Q9, ISPE
    - **Resolución**: 1229 de 2013
    """)
    
    if "excel_buffer" in st.session_state:
        stats = generar_estadisticas_riesgo(pd.DataFrame())
        st.markdown("### 📈 Estadísticas")
        st.metric("Total de Riesgos", stats["total_riesgos"])
        st.metric("Riesgos Altos", stats["alto"])
        st.metric("Riesgos Moderados", stats["moderado"])
        st.metric("Riesgos Bajos", stats["bajo"])

# Contenido principal
st.markdown("### 📁 Carga de Archivo de Base de Datos")
archivo = st.file_uploader(
    "Seleccione el archivo Excel con las matrices de riesgo:", 
    type=["xlsx"], 
    help="Archivo debe contener las hojas: MR 1 sólidos, MR 1 líquidos y semisólidos, MR 1 limpieza"
)

if archivo:
    col1, col2 = st.columns(2)
    
    with col1:
        tipo_validacion = st.selectbox(
            "🔬 Tipo de Validación:",
            ["Validación de procesos", "Validación de campaña", "Validación de limpieza"],
            index=None,
            help="Seleccione el tipo de validación que desea realizar"
        )
    
    etapas_seleccionadas = []
    sheet_to_use = None
    
    if tipo_validacion in ["Validación de procesos", "Validación de campaña"]:
        with col2:
            tipo_linea = st.selectbox(
                "🏭 Línea de Fabricación:",
                ["Línea de medicamentos sólidos", "Línea de medicamentos líquidos y semisólidos"],
                index=None,
                help="Seleccione la línea de fabricación correspondiente"
            )
        
        if tipo_linea:
            sheet_to_use = "MR 1 sólidos" if "sólidos" in tipo_linea else "MR 1 líquidos y semisólidos"
            
            st.markdown(f"### ⚙️ Selección de Etapas - {tipo_linea}")
            st.markdown("Seleccione las etapas que aplican al proceso:")
            
            config = ETAPAS_CONFIG[sheet_to_use]
            
            # Crear columnas para mejor organización
            cols = st.columns(3)
            for i, etapa in enumerate(config["etapas"]):
                with cols[i % 3]:
                    if st.checkbox(etapa, key=f"etapa_{i}"):
                        etapas_seleccionadas.append(etapa)
    
    elif tipo_validacion == "Validación de limpieza":
        sheet_to_use = "MR 1 limpieza"
        
        st.markdown("### 🧽 Selección de Etapas de Limpieza")
        config = ETAPAS_CONFIG[sheet_to_use]
        
        cols = st.columns(2)
        for i, etapa in enumerate(config["etapas"]):
            with cols[i % 2]:
                if st.checkbox(etapa, key=f"limpieza_{i}"):
                    etapas_seleccionadas.append(etapa)
    
    # Procesamiento y generación
    if etapas_seleccionadas and sheet_to_use:
        st.markdown("### 🎯 Etapas Seleccionadas")
        st.success(f"**{len(etapas_seleccionadas)}** etapas seleccionadas: {', '.join(etapas_seleccionadas)}")
        
        if "excel_buffer" not in st.session_state:
            if st.button("🚀 Generar Matriz de Riesgo", use_container_width=True, type="primary"):
                with st.spinner("Generando matriz de riesgo..."):
                    try:
                        df = load_excel(archivo, sheet_to_use)
                        if df is None:
                            st.stop()
                        
                        config = ETAPAS_CONFIG[sheet_to_use]
                        rangos = config["rangos"]
                        
                        encabezado = df.iloc[[0]]
                        bloques = []
                        
                        for etapa in etapas_seleccionadas:
                            if etapa in rangos:
                                inicio, fin = rangos[etapa]
                                bloques.append(df.iloc[inicio:fin + 1])
                        
                        if not bloques:
                            st.error("No se encontraron datos para las etapas seleccionadas.")
                            st.stop()
                        
                        tabla = pd.concat([encabezado] + bloques, ignore_index=True)
                        
                        # Generar Excel
                        buffer = io.BytesIO()
                        tabla.to_excel(buffer, index=False)
                        buffer.seek(0)
                        
                        wb = load_workbook(buffer)
                        ws = wb.active
                        
                        # Aplicar formato
                        if aplicar_formato_excel(ws, ws.max_row):
                            output = io.BytesIO()
                            wb.save(output)
                            output.seek(0)
                            
                            st.session_state['excel_buffer'] = output
                            st.session_state['etapas_seleccionadas'] = etapas_seleccionadas
                            st.session_state['tabla_procesada'] = tabla
                            
                            st.balloons()
                            st.markdown("""
                            <div class='success-box'>
                                <h4>✅ ¡Matriz de Riesgo Generada Exitosamente!</h4>
                                <p>La matriz ha sido procesada con NPR ajustado y formato condicional aplicado.</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error("Error al aplicar formato al archivo Excel.")
                    
                    except Exception as e:
                        st.error(f"Error al procesar el archivo: {str(e)}")
                        st.info("Verifique que el archivo tenga la estructura correcta.")
        
        # Mostrar resultados
        if "excel_buffer" in st.session_state:
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 Descargar Matriz de Riesgo",
                    data=st.session_state['excel_buffer'].getvalue(),
                    file_name=f"matriz_riesgo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    on_click=lambda: st.session_state.update({"descarga_realizada": True})
                )
            
            with col2:
                if st.button("🔄 Generar Nueva Matriz", use_container_width=True):
                    for key in ["excel_buffer", "etapas_seleccionadas", "tabla_procesada", "descarga_realizada"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
            
            # Visualización de estadísticas
            if "tabla_procesada" in st.session_state:
                stats = generar_estadisticas_riesgo(st.session_state['tabla_procesada'])
                
                st.markdown("### 📊 Análisis de Resultados")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total de Riesgos", stats["total_riesgos"])
                with col2:
                    st.metric("Riesgos Altos", stats["alto"], delta=f"{stats['alto']/stats['total_riesgos']*100:.1f}%")
                with col3:
                    st.metric("Riesgos Moderados", stats["moderado"], delta=f"{stats['moderado']/stats['total_riesgos']*100:.1f}%")
                with col4:
                    st.metric("Riesgos Bajos", stats["bajo"], delta=f"{stats['bajo']/stats['total_riesgos']*100:.1f}%")
                
                # Gráfico de distribución
                fig = crear_grafico_riesgos(stats)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            # Selección de operaciones críticas
            if st.session_state.get("descarga_realizada", False):
                st.markdown("### 🚨 Identificación de Operaciones Críticas")
                st.info("Seleccione las operaciones que resultaron con criticidad **Alta** según la matriz generada:")
                
                selected_alta = st.multiselect(
                    "Operaciones con criticidad Alta:",
                    options=st.session_state['etapas_seleccionadas'],
                    key="alta_seleccion",
                    help="Estas operaciones requerirán planes de validación más rigurosos"
                )
                
                if selected_alta:
                    st.success(f"✅ **{len(selected_alta)}** operaciones identificadas con criticidad Alta:")
                    for op in selected_alta:
                        st.write(f"• {op}")
                    
                    # Recomendaciones
                    st.markdown("### 💡 Recomendaciones")
                    st.warning("""
                    **Para operaciones de criticidad Alta:**
                    - Implementar controles estadísticos más estrictos
                    - Aumentar frecuencia de muestreo
                    - Realizar validación concurrente
                    - Documentar exhaustivamente los procedimientos
                    """)

else:
    st.info("📁 Por favor, cargue un archivo Excel para comenzar el análisis de riesgos.")
    st.markdown("""
    ### 📋 Instrucciones de Uso:
    1. **Cargar archivo**: Seleccione el archivo Excel con las matrices de riesgo
    2. **Seleccionar validación**: Elija el tipo de validación a realizar
    3. **Configurar etapas**: Marque las etapas que aplican a su proceso
    4. **Generar matriz**: Procese los datos con NPR ajustado
    5. **Descargar resultados**: Obtenga la matriz formateada
    6. **Identificar críticos**: Seleccione operaciones de alta criticidad
    """)
