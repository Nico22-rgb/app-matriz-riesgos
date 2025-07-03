import streamlit as st

st.title("Generador de Matriz de Riesgos")

st.write("### ¿Para qué tipo de validación desea hacer su análisis de riesgo?")
opcion = st.radio(
    "Seleccione una opción:",
    ("Validación de proceso o campaña", "Validación de limpieza")
)

st.write(f"Ha seleccionado: **{opcion}**")
