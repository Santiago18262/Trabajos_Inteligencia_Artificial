
"""
Interfaz principal del Sistema Experto para diagnóstico de enfermedades respiratorias.
"""

import streamlit as st                               # Importa Streamlit para construir la interfaz web
from base_conocimiento import REGLAS, VARIABLES      # Importa reglas y definición de variables de la BC
from motor_inferencia import (                        # Importa motores de inferencia
    encadenamiento_adelante)

# ------------------------------------------------------------
# Configuración general de la página
# ------------------------------------------------------------
st.set_page_config(                                   # Configura metadatos de la app
    page_title="Sistema Experto Respiratorio",        # Título de la pestaña del navegador
    page_icon="",                                     # Ícono de la página (vacío = ícono por defecto)
    layout="wide"                                     # Usa layout ancho (full width)
)

# ------------------------------------------------------------
# Utilidades de estado: detectar si el usuario tocó un campo
# ------------------------------------------------------------
def _ensure_state(var: str):
    """Asegura que exista la bandera 'tocado' para la variable dada en session_state."""
    if f"t_{var}" not in st.session_state:            # Si no existe la clave de 'tocado' para var
        st.session_state[f"t_{var}"] = False          # Inicialízala en False

def _mark_touched(var: str):
    """Marca una variable como 'tocada' (el usuario interactuó)."""
    st.session_state[f"t_{var}"] = True               # Cambia la bandera a True

def _is_touched(var: str) -> bool:
    """Retorna True si la variable fue 'tocada' por el usuario."""
    return bool(st.session_state.get(f"t_{var}", False))  # Lee la bandera con valor por defecto False

# ------------------------------------------------------------
# Encabezado principal
# ------------------------------------------------------------
st.title("Sistema Experto — Diagnóstico de Enfermedades Respiratorias")  # Título grande en la UI
st.caption(                                                               # Subtítulo/ayuda bajo el título
    "Ingresa datos en el panel **>>** (arriba a la izquierda) para ingresar los datos y síntomas del paciente y pulsa "
    "**Calcular diagnóstico** para mostrar la probabilidades de cada una de las enfermedades."
)

# ------------------------------------------------------------
# Campo de entrada con detección de interacción
# ------------------------------------------------------------
def input_field(var: str, meta: dict):
    """
    Dibuja el control según tipo, registra 'tocado' con on_change,
    y devuelve (valor, incluir?). Solo incluimos si el usuario tocó el control
    o si el valor es distinto al placeholder (en texto).
    """
    _ensure_state(var)                                 # Asegura que exista la bandera de 'tocado' para var

    tipo = meta["tipo"]                                # Tipo de dato (booleano, entero, flotante, texto)
    etiqueta = meta.get("etiqueta",                    # Etiqueta del control (fallback: nombre bonito)
                        var.replace("_", " ").capitalize())
    desc = meta.get("descripcion")                     # Descripción opcional para mostrar como caption
    key = f"in_{var}"                                  # Clave única del control en Streamlit

    # BOOLEANO: checkbox. Unchecked por defecto NO entra hasta que lo toquen.
    if tipo == "booleano":
        val = st.checkbox(                             # Renderiza un checkbox
            etiqueta,
            value=False,                               # Por defecto desmarcado
            key=key,                                   # Clave del widget
            on_change=_mark_touched,                   # Marca como tocado cuando cambie
            args=(var,)                                # Pasa el nombre de la variable a _mark_touched
        )
        if desc: st.caption(desc)                      # Muestra descripción si existe
        incluir = _is_touched(var)                     # Solo incluir si el usuario interactuó
        return (val if incluir else None), incluir     # Devuelve valor real solo si incluir=True

    # ENTERO
    if tipo == "entero":
        val = st.number_input(                         # Renderiza un input numérico (entero)
            etiqueta,
            min_value=meta.get("min", 0),              # Mínimo permitido (default 0)
            max_value=meta.get("max", 100),            # Máximo permitido (default 100)
            value=meta.get("min", 0),                  # Valor inicial 'neutro' (para no contar si no lo tocan)
            step=1,                                    # Incremento de 1 en 1
            key=key,                                   # Clave del widget
            on_change=_mark_touched,                   # Marca como tocado al cambiar
            args=(var,)                                # Pasa el nombre de la variable
        )
        if desc: st.caption(desc)                      # Muestra descripción si existe
        incluir = _is_touched(var)                     # Incluye solo si fue tocado
        return (val if incluir else None), incluir     # Devuelve valor condicionado por incluir

    # FLOTANTE
    if tipo == "flotante":
        val = st.number_input(                         # Renderiza un input numérico (float)
            etiqueta,
            min_value=meta.get("min", 0.0),            # Mínimo permitido (default 0.0)
            max_value=meta.get("max", 100.0),          # Máximo permitido (default 100.0)
            value=meta.get("min", 0.0),                # Valor inicial 'neutro'
            step=0.1,                                  # Paso de 0.1
            format="%.1f",                             # Formato de visualización con 1 decimal
            key=key,                                   # Clave del widget
            on_change=_mark_touched,                   # Marca como tocado al cambiar
            args=(var,)                                # Pasa el nombre de la variable
        )
        if desc: st.caption(desc)                      # Muestra descripción si existe
        incluir = _is_touched(var)                     # Incluye solo si fue tocado
        return (val if incluir else None), incluir     # Devuelve valor condicionado por incluir

    # TEXTO: insertamos placeholder inicial que NO cuenta
    if tipo == "texto":
        opciones = meta.get("opciones", [])            # Lista de opciones (si es un select) o vacío
        placeholder = "— (sin dato) —"                 # Placeholder visible para "no seleccionado"
        if opciones:
            opciones_ui = [placeholder] + opciones     # Inserta placeholder al inicio de la lista
            idx = st.selectbox(                        # Renderiza un combo/select
                etiqueta,
                options=list(range(len(opciones_ui))), # Índices como opciones internas
                format_func=lambda i: opciones_ui[i],  # Muestra el texto correspondiente
                index=0,                               # Selecciona por defecto el placeholder
                key=key,                               # Clave del widget
                on_change=_mark_touched,               # Marca como tocado al cambiar
                args=(var,)                            # Pasa el nombre de la variable
            )
            val = None if idx == 0 else opciones_ui[idx]  # Si está en placeholder => None; si no, valor real
        else:
            # texto libre con placeholder visual
            val = st.text_input(                       # Renderiza un input de texto libre
                etiqueta,
                value="",                              # Vacío por defecto
                key=key,                               # Clave del widget
                on_change=_mark_touched,               # Marca como tocado al cambiar
                args=(var,)                            # Pasa el nombre de la variable
            )
            if val == "":                              # Si quedó vacío, no cuenta
                val = None
        if desc: st.caption(desc)                      # Muestra descripción si existe
        incluir = (val is not None)                    # Incluye si el valor no es None (i.e., no placeholder/ vacío)
        return val, incluir                            # Devuelve valor y bandera incluir

    # Fallback
    if desc: st.caption(desc)                          # Si no coincide con tipos conocidos, solo muestra descripción
    return None, False                                 # No incluir por defecto

# ------------------------------------------------------------
# Agrupación visual de variables
# ------------------------------------------------------------
GRUPOS = {                                             # Define grupos lógicos para la UI lateral
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
with st.sidebar:                                      # Inicia el panel lateral
    st.header("Datos del paciente")                   # Encabezado del panel
    hechos = {}                                       # Diccionario de hechos (solo campos incluidos)
    usados = set()                                    # Conjunto para rastrear variables mostradas

    for titulo, llaves in GRUPOS.items():             # Itera por grupos definidos
        st.subheader(titulo)                          # Subtítulo del grupo
        for k in llaves:                              # Itera por cada variable del grupo
            if k in VARIABLES:                        # Verifica que la var exista en la BC
                val, incluir = input_field(k, VARIABLES[k])  # Dibuja control y obtiene valor/incluir
                if incluir:                           # Si debe incluirse
                    hechos[k] = val                   # Agrega a hechos (evidencias)
                usados.add(k)                         # Marca variable como usada en la UI

    # Variables no agrupadas (si las hubiera)
    restantes = [k for k in VARIABLES.keys() if k not in usados]  # Calcula variables que no están en GRUPOS
    if restantes:                                      # Si existen variables restantes
        st.subheader("Otros")                          # Muestra otro subgrupo
        for k in restantes:                            # Itera sobre ellas
            val, incluir = input_field(k, VARIABLES[k])# Dibuja control
            if incluir:                                # Si se debe incluir
                hechos[k] = val                        # Agrega a hechos

# ------------------------------------------------------------
# Estructura visual en columnas
# ------------------------------------------------------------
col1, col2 = st.columns([1.3, 1])                    # Crea dos columnas (col1 más ancha que col2)

# ------------------------------------------------------------
# Columna 1: Resultados del diagnóstico
# ------------------------------------------------------------
with col1:                                            # Comienza contenido en la primera columna
    st.subheader("Presentación del diagnóstico")      # Título de sección

    calcular = st.button("Calcular diagnóstico", type="primary")  # Botón principal de acción

    if calcular and hechos:                            # Si se presionó y hay hechos capturados
        trazas, puntajes, explicaciones, recomendaciones = encadenamiento_adelante(  # Llama motor forward chaining
            hechos,
            REGLAS
        )

        if puntajes:                                   # Si hay puntajes (diagnósticos evaluados)
            orden = sorted(                            # Ordena diagnósticos por probabilidad descendente
                puntajes.items(),
                key=lambda x: x[1],
                reverse=True
            )
            st.write("**Diagnósticos presuntivos (con probabilidad):**")  # Título de lista
            for dx, fc in orden:                       # Itera por diagnósticos ordenados
                st.markdown(f"**{dx}** — probabilidad **{fc*100:.1f}%**")  # Muestra cada dx con % formato

            st.divider()                               # Separador visual

            st.subheader("Recomendaciones iniciales")  # Subtítulo de recomendaciones
            for dx, _ in orden[:3]:                    # Toma top-3 diagnósticos
                if recomendaciones.get(dx):            # Si hay recomendaciones para ese dx
                    st.markdown(f"**{dx}:** " + "; ".join(recomendaciones[dx]))  # Lista unida por '; '

            st.subheader("Explicación en lenguaje natural")  # Subtítulo de explicaciones
            for dx, _ in orden[:3]:                    # Para top-3 diagnósticos
                if explicaciones.get(dx):              # Si hay explicación
                    with st.expander(f"¿Por qué se diagnosticó {dx}?"):  # Expander por dx
                        for frase in explicaciones[dx]: # Itera por frases explicativas
                            st.markdown("• " + frase)   # Muestra cada razón como viñeta

        else:                                          # Si no se activaron reglas
            st.info("Con los datos proporcionados no se activó ninguna regla. Complete uno o más campos e intente nuevamente.")  # Mensaje informativo

    elif calcular and not hechos:                      # Si se presionó pero no hay hechos
        st.info("No ingresaste ningún dato. Modifica al menos un campo y vuelve a calcular.")  # Pide ingresar algo

    else:                                              # Si aún no se presiona el botón
        st.caption("Modifica uno o más campos en el panel lateral y pulsa **Calcular diagnóstico**.")  # Instrucción breve

# ------------------------------------------------------------
# Columna 2: Visualización de las reglas de la base de conocimiento
# ------------------------------------------------------------
with col2:                                            # Comienza contenido en la segunda columna
    st.subheader("Reglas de la Base de Conocimiento") # Título de sección
    st.write(f"Total de reglas: **{len(REGLAS)}**")    # Muestra el número total de reglas cargadas
    for r in REGLAS:                                   # Itera por cada regla
        with st.expander(f"{r['id']} → {r['entonces']} (fc={r.get('fc',1.0)})"):  # Expander por regla con id, conclusión y fc
            st.json(r)                                 # Muestra la regla completa en formato JSON (legible)
