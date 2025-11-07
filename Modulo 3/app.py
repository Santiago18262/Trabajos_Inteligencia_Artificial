# app.py
# -*- coding: utf-8 -*-
"""
Interfaz principal del Sistema Experto para diagnóstico de enfermedades respiratorias.
Ajuste: la UI se mantiene simple (sin switches). Internamente solo se consideran
los campos que el usuario realmente tocó. Los valores por defecto se ignoran.
"""

import streamlit as st
from base_conocimiento import REGLAS, VARIABLES
from motor_inferencia import encadenamiento_adelante, encadenamiento_atras_automatico

# ------------------------------------------------------------
# Configuración general de la página
# ------------------------------------------------------------
st.set_page_config(page_title="Sistema Experto Respiratorio", page_icon="", layout="wide")

# ------------------------------------------------------------
# Utilidades de estado: detectar si el usuario tocó un campo
# ------------------------------------------------------------
def _ensure_state(var: str):
    # Bandera de "tocado"
    if f"t_{var}" not in st.session_state:
        st.session_state[f"t_{var}"] = False

def _mark_touched(var: str):
    st.session_state[f"t_{var}"] = True

def _is_touched(var: str) -> bool:
    return bool(st.session_state.get(f"t_{var}", False))

# ------------------------------------------------------------
# Encabezado principal
# ------------------------------------------------------------
st.title("Sistema Experto — Diagnóstico de Enfermedades Respiratorias")
st.caption("Ingresa datos en el panel **>>** (arriba a la izquierda) para ingresar los datos y síntomas del paciente y pulsa "
           "**Calcular diagnóstico** para mostrar la probabilidades de cada una de las enfermedades.")

# ------------------------------------------------------------
# Campo de entrada con detección de interacción
# ------------------------------------------------------------
def input_field(var: str, meta: dict):
    """
    Dibuja el control según tipo, registra 'tocado' con on_change,
    y devuelve (valor, incluir?). Solo incluimos si el usuario tocó el control
    o si el valor es distinto al placeholder (en texto).
    """
    _ensure_state(var)

    tipo = meta["tipo"]
    etiqueta = meta.get("etiqueta", var.replace("_", " ").capitalize())
    desc = meta.get("descripcion")
    key = f"in_{var}"

    # BOOLEANO: checkbox. Unchecked por defecto NO entra hasta que lo toquen.
    if tipo == "booleano":
        val = st.checkbox(etiqueta, value=False, key=key, on_change=_mark_touched, args=(var,))
        if desc: st.caption(desc)
        incluir = _is_touched(var)  # solo si el usuario interactuó
        return (val if incluir else None), incluir

    # ENTERO
    if tipo == "entero":
        val = st.number_input(
            etiqueta,
            min_value=meta.get("min", 0),
            max_value=meta.get("max", 100),
            value=meta.get("min", 0),  # valor inicial "neutro"
            step=1,
            key=key,
            on_change=_mark_touched,
            args=(var,)
        )
        if desc: st.caption(desc)
        incluir = _is_touched(var)
        return (val if incluir else None), incluir

    # FLOTANTE
    if tipo == "flotante":
        val = st.number_input(
            etiqueta,
            min_value=meta.get("min", 0.0),
            max_value=meta.get("max", 100.0),
            value=meta.get("min", 0.0),  # valor inicial "neutro"
            step=0.1,
            format="%.1f",
            key=key,
            on_change=_mark_touched,
            args=(var,)
        )
        if desc: st.caption(desc)
        incluir = _is_touched(var)
        return (val if incluir else None), incluir

    # TEXTO: insertamos placeholder inicial que NO cuenta
    if tipo == "texto":
        opciones = meta.get("opciones", [])
        placeholder = "— (sin dato) —"
        if opciones:
            opciones_ui = [placeholder] + opciones  # placeholder en índice 0
            idx = st.selectbox(etiqueta, options=list(range(len(opciones_ui))),
                               format_func=lambda i: opciones_ui[i],
                               index=0,
                               key=key,
                               on_change=_mark_touched,
                               args=(var,))
            val = None if idx == 0 else opciones_ui[idx]
        else:
            # texto libre con placeholder visual
            val = st.text_input(etiqueta, value="", key=key, on_change=_mark_touched, args=(var,))
            if val == "":  # vacío no cuenta
                val = None
        if desc: st.caption(desc)
        incluir = (val is not None)
        return val, incluir

    # Fallback
    if desc: st.caption(desc)
    return None, False

# ------------------------------------------------------------
# Agrupación visual de variables
# ------------------------------------------------------------
GRUPOS = {
    "Datos personales": [
        "edad", "sexo"
    ],
    "Síntomas": [
        "fiebre_c", "tos", "duracion_tos_dias",
        "sibilancias", "disnea", "dolor_pecho", "fatiga",
        "cefalea", "mialgias", "odinofagia", "anosmia",
        "congestion_nasal", "rinorrea", "exudado_amigdalino",
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
    usados = set()

    for titulo, llaves in GRUPOS.items():
        st.subheader(titulo)
        for k in llaves:
            if k in VARIABLES:
                val, incluir = input_field(k, VARIABLES[k])
                if incluir:
                    hechos[k] = val
                usados.add(k)

    # Variables no agrupadas (si las hubiera)
    restantes = [k for k in VARIABLES.keys() if k not in usados]
    if restantes:
        st.subheader("Otros")
        for k in restantes:
            val, incluir = input_field(k, VARIABLES[k])
            if incluir:
                hechos[k] = val

# ------------------------------------------------------------
# Estructura visual en columnas
# ------------------------------------------------------------
col1, col2 = st.columns([1.3, 1])

# ------------------------------------------------------------
# Columna 1: Resultados del diagnóstico
# ------------------------------------------------------------
with col1:
    st.subheader("Presentación del diagnóstico")

    calcular = st.button("Calcular diagnóstico", type="primary")

    if calcular and hechos:
        trazas, puntajes, explicaciones, recomendaciones = encadenamiento_adelante(hechos, REGLAS)

        if puntajes:
            orden = sorted(puntajes.items(), key=lambda x: x[1], reverse=True)
            st.write("**Diagnósticos presuntivos (con probabilidad):**")
            for dx, fc in orden:
                st.markdown(f"**{dx}** — probabilidad **{fc*100:.1f}%**")

            st.divider()

            st.subheader("Recomendaciones iniciales")
            for dx, _ in orden[:3]:
                if recomendaciones.get(dx):
                    st.markdown(f"**{dx}:** " + "; ".join(recomendaciones[dx]))

            st.subheader("Explicación en lenguaje natural")
            for dx, _ in orden[:3]:
                if explicaciones.get(dx):
                    with st.expander(f"¿Por qué se diagnosticó {dx}?"):
                        for frase in explicaciones[dx]:
                            st.markdown("• " + frase)
        else:
            st.info("Con los datos proporcionados no se activó ninguna regla. Complete uno o más campos e intente nuevamente.")
    elif calcular and not hechos:
        st.info("No ingresaste ningún dato. Modifica al menos un campo y vuelve a calcular.")
    else:
        st.caption("Modifica uno o más campos en el panel lateral y pulsa **Calcular diagnóstico**.")

# ------------------------------------------------------------
# Columna 2: Visualización de las reglas de la base de conocimiento
# ------------------------------------------------------------
with col2:
    st.subheader("Reglas de la Base de Conocimiento")
    st.write(f"Total de reglas: **{len(REGLAS)}**")
    for r in REGLAS:
        with st.expander(f"{r['id']} → {r['entonces']} (fc={r.get('fc',1.0)})"):
            st.json(r)
