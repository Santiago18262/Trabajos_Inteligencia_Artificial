# aplicacion.py
# -*- coding: utf-8 -*-
"""
Interfaz principal del Sistema Experto para diagnóstico de enfermedades respiratorias.
Incluye campos descriptivos para que el usuario entienda cada dato ingresado.
"""

import streamlit as st
from base_conocimiento import REGLAS, VARIABLES
from motor_inferencia import encadenamiento_adelante, encadenamiento_atras_automatico

# ------------------------------------------------------------
# Configuración general de la página
# ------------------------------------------------------------
st.set_page_config(page_title="Sistema Experto Respiratorio", page_icon="🩺", layout="wide")

# ------------------------------------------------------------
# Encabezado principal
# ------------------------------------------------------------
st.title("🩺 Sistema Experto — Diagnóstico de Enfermedades Respiratorias")
st.caption("Basado en reglas tipo 'SI... ENTONCES' con factores de certeza y explicaciones en lenguaje natural.")

# ------------------------------------------------------------
# Sección lateral (entrada de datos del paciente)
# ------------------------------------------------------------
with st.sidebar:
    st.header("Datos del paciente")
    hechos = {}

    # Recorre todas las variables definidas en la base de conocimiento
    for variable, meta in VARIABLES.items():
        tipo = meta["tipo"]
        etiqueta = meta.get("etiqueta", variable.replace("_", " ").capitalize())

        # Campos según tipo de dato
        if tipo == "entero":
            hechos[variable] = st.number_input(
                etiqueta,
                min_value=meta.get("min", 0),
                max_value=meta.get("max", 100),
                value=meta.get("min", 0),
                step=1
            )
        elif tipo == "flotante":
            hechos[variable] = st.number_input(
                etiqueta,
                min_value=meta.get("min", 0.0),
                max_value=meta.get("max", 100.0),
                value=meta.get("min", 0.0),
                step=0.1,
                format="%.1f"
            )
        elif tipo == "texto":
            hechos[variable] = st.selectbox(etiqueta, meta.get("opciones", [""]))
        elif tipo == "booleano":
            hechos[variable] = st.checkbox(etiqueta, value=False)

        # Mostrar descripción breve debajo del campo
        if "descripcion" in meta:
            st.caption(meta["descripcion"])

# ------------------------------------------------------------
# Estructura visual en columnas
# ------------------------------------------------------------
col1, col2 = st.columns([1.3, 1])

# ------------------------------------------------------------
# Columna 1: Resultados del diagnóstico
# ------------------------------------------------------------
with col1:
    st.subheader("Presentación del diagnóstico")

    trazas, puntajes, explicaciones, recomendaciones = encadenamiento_adelante(hechos, REGLAS)

    if puntajes:
        # Ordenar los diagnósticos de mayor a menor probabilidad
        orden = sorted(puntajes.items(), key=lambda x: x[1], reverse=True)
        st.write("**Diagnósticos presuntivos (con probabilidad):**")

        for dx, cf in orden:
            st.markdown(f"- **{dx}** — probabilidad **{cf*100:.1f}%**")

        st.divider()

        # ------------------------------------------------------------
        # Recomendaciones médicas sugeridas
        # ------------------------------------------------------------
        st.subheader("Recomendaciones iniciales")
        for dx, _ in orden[:3]:
            if recomendaciones.get(dx):
                st.markdown(f"**{dx}:** " + "; ".join(recomendaciones[dx]))

        # ------------------------------------------------------------
        # Explicación de cómo se llegó al diagnóstico
        # ------------------------------------------------------------
        st.subheader("Explicación en lenguaje natural")
        for dx, _ in orden[:3]:
            if explicaciones.get(dx):
                with st.expander(f"¿Por qué se diagnosticó {dx}?"):
                    for frase in explicaciones[dx]:
                        st.markdown("• " + frase)

        # ------------------------------------------------------------
        # Encadenamiento hacia atrás automático (requisitos faltantes)
        # ------------------------------------------------------------
        st.subheader("Encadenamiento hacia atrás automático")
        faltantes = encadenamiento_atras_automatico(puntajes, REGLAS, top_n=3)
        for dx, necesidades in faltantes.items():
            with st.expander(f"Para confirmar **{dx}**, revise también:"):
                for n in necesidades:
                    reqs = [f"{c['variable'].replace('_', ' ')} {c['operador']} {c['valor']}" for c in n["condiciones"]]
                    st.markdown(f"- **Regla {n['regla']}** (CF={n['cf']}, lógica={n['logica']}): " + "; ".join(reqs))

    else:
        st.info("No se activó ninguna regla con los datos actuales. Intente completar más campos o síntomas del paciente.")

# ------------------------------------------------------------
# Columna 2: Visualización de las reglas de la base de conocimiento
# ------------------------------------------------------------
with col2:
    st.subheader("Reglas de la Base de Conocimiento")
    st.write(f"Total de reglas: **{len(REGLAS)}**")
    for r in REGLAS:
        with st.expander(f"{r['id']} → {r['entonces']} (CF={r['cf']})"):
            st.json(r)

# ------------------------------------------------------------
# Pie de página
# ------------------------------------------------------------
st.caption("Este prototipo tiene fines educativos y no sustituye una valoración médica profesional.")
