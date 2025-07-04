import streamlit as st

# Subir el archivo
archivo = st.file_uploader("Sube el archivo de la base de datos", [".xlsx"])

if archivo:

    tipo_validacion = st.selectbox("¿Qué tipo de validación desea?", [
                                   "Validacion 1", "Validacion 2", "Validacion 3"], index=None)

    if tipo_validacion == "Validacion 1":
        tipo_linea = st.selectbox("¿Qué linea desea consultar?", [
                                  "Linea 1", "Linea 2", "Linea 3"], index=None)

        if tipo_linea == "Linea 1":
            etapas_seleccionadas = st.multiselect("Seleccione las etapas que apliquen", [
                                                  "Green", "Yellow", "Red", "Blue"])
