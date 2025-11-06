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
# Función auxiliar para generar los campos del formulario
# ------------------------------------------------------------
def input_field(var, meta):
    tipo = meta["tipo"]
    etiqueta = meta.get("etiqueta", var.replace("_", " ").capitalize())
    desc = meta.get("descripcion")

    # Campos según tipo de dato
    if tipo == "entero":
        val = st.number_input(
            etiqueta,
            min_value=meta.get("min", 0),
            max_value=meta.get("max", 100),
            value=meta.get("min", 0),
            step=1
        )
    elif tipo == "flotante":
        val = st.number_input(
            etiqueta,
            min_value=meta.get("min", 0.0),
            max_value=meta.get("max", 100.0),
            value=meta.get("min", 0.0),
            step=0.1,
            format="%.1f"
        )
    elif tipo == "texto":
        val = st.selectbox(etiqueta, meta.get("opciones", [""]))
    elif tipo == "booleano":
        val = st.checkbox(etiqueta, value=False)
    else:
        val = None

    # Mostrar descripción debajo
    if desc:
        st.caption(desc)
    return val

# ------------------------------------------------------------
# Agrupación visual de variables
# ------------------------------------------------------------
GRUPOS = {
    "Datos personales": [
        "edad", "sexo"
    ],
    "Síntomas": [
        # Respiratorios generales
        "fiebre_c", "tos", "duracion_tos_dias",
        "sibilancias", "disnea", "dolor_pecho", "fatiga",
        "cefalea", "mialgias", "odinofagia", "anosmia",

        # NUEVOS (resfriado/sinusitis/faringitis)
        "congestion_nasal", "rinorrea","exudado_amigdalino",
        "adenopatias_cervicales", "estornudos"
    ],
    "Signos y estudios": [
        "satO2", "crepitantes", "roncus", "sibilos_auscultacion",
        "rx_consolidacion", "pcr_alta", "leucocitosis"
    ],
    "Factores de riesgo": [
        "tabaquismo", "paquetes_por_dia", "anios_fumando",
        "exposicion_contaminantes", "alergias_atopia",
        "infeccion_respiratoria_reciente", "contacto_covid",
        "estacional_invierno"
    ]
}


# ------------------------------------------------------------
# Sección lateral (entrada de datos del paciente)
# ------------------------------------------------------------
with st.sidebar:
    st.header("Datos del paciente")
    hechos = {}

    # Recorre las variables agrupadas por categoría
    usados = set()
    for titulo, llaves in GRUPOS.items():
        st.subheader(titulo)
        for k in llaves:
            if k in VARIABLES:
                hechos[k] = input_field(k, VARIABLES[k])
                usados.add(k)

    # Si hay variables nuevas no incluidas en los grupos
    restantes = [k for k in VARIABLES.keys() if k not in usados]
    if restantes:
        st.subheader("Otros")
        for k in restantes:
            hechos[k] = input_field(k, VARIABLES[k])

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

        for dx, fc in orden:
            st.markdown(f"**{dx}** — probabilidad **{fc*100:.1f}%**")
            # st.progress(min(max(fc, 0.0), 1.0))  # Barra de progreso visual

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
                    st.markdown(f"- **Regla {n['regla']}** (fc={n['fc']}, lógica={n['logica']}): " + "; ".join(reqs))

    else:
        st.info("No se activó ninguna regla con los datos actuales. Intente completar más campos o síntomas del paciente.")

# ------------------------------------------------------------
# Columna 2: Visualización de las reglas de la base de conocimiento
# ------------------------------------------------------------
with col2:
    st.subheader("Reglas de la Base de Conocimiento")
    st.write(f"Total de reglas: **{len(REGLAS)}**")
    for r in REGLAS:
        with st.expander(f"{r['id']} → {r['entonces']} (fc={r['fc']})"):
            st.json(r)

# ------------------------------------------------------------
# Pie de página
# ------------------------------------------------------------
st.caption("Este prototipo tiene fines educativos y no sustituye una valoración médica profesional.")
