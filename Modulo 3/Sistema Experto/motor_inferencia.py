
"""
Este archivo es mediante el cual funciona el sistema experto.
Aquí se analizan los datos que ingresa el usuario (síntomas, signos, etc.)
y se comparan con las reglas de la base de conocimiento para llegar a
un posible diagnóstico y sus probabilidades.
"""

from typing import Dict, Any, List  # Solo sirve para aclarar el tipo de datos (diccionarios, listas, etc.)

# ============================================================
# FUNCIÓN QUE REVISA SI UNA CONDICIÓN SE CUMPLE
# ============================================================
# Esta función compara lo que dijo el usuario con lo que espera la regla.

def evaluar(valor_usuario, operador, valor_regla):
    """Compara el valor del usuario con el valor esperado según el operador."""
    if operador == "==": return valor_usuario == valor_regla     # Igual
    if operador == "!=": return valor_usuario != valor_regla     # Diferente
    if operador == ">=": return valor_usuario >= valor_regla     # Mayor o igual
    if operador == "<=": return valor_usuario <= valor_regla     # Menor o igual
    if operador == ">":  return valor_usuario > valor_regla      # Mayor que
    if operador == "<":  return valor_usuario < valor_regla      # Menor que
    if operador == "in": return valor_usuario in valor_regla     # Está dentro de una lista
    if operador == "contiene": return valor_regla in valor_usuario  # Contiene una palabra o valor
    return False  # Si no se reconoce el operador, se asume que no cumple

# ============================================================
# FUNCIÓN QUE CALCULA QUÉ TANTO SE CUMPLE UNA CONDICIÓN
# ============================================================

def grado_verdad(hechos: Dict[str, Any], condicion: Dict[str, Any]) -> float:
    """
    Calcula si una condición se cumple (1) o no (0).
    También puede usar un "peso" para darle más importancia.
    """
    variable = condicion["variable"]          # Nombre de la variable (ej. fiebre_c)
    operador = condicion["operador"]          # Operador lógico (==, >, etc.)
    valor = condicion["valor"]                # Valor que la regla espera (ej. fiebre_c > 38)
    peso = float(condicion.get("peso", 1.0))  # Importancia de la condición (por defecto vale 1)

    # Si el usuario no puso ese dato, no se puede evaluar
    if variable not in hechos:
        return 0.0

    # Trata de comparar; si algo sale mal, se considera que no cumple
    try:
        cumple = evaluar(hechos[variable], operador, valor)
    except Exception:
        cumple = False

    # Si cumple → devuelve 1, si no → 0, y lo multiplica por el peso
    return (1.0 if cumple else 0.0) * peso

# ============================================================
# FUNCIONES QUE COMBINAN RESULTADOS DE VARIAS CONDICIONES
# ============================================================

def agregar(valores: List[float], logica: str, pesos: List[float] | None = None) -> float:
    """
    Une los resultados de varias condiciones de una misma regla.
    Si la lógica es 'todas' (AND), se saca un promedio.
    Si la lógica es 'alguna' (OR), se toma el valor más alto.
    """
    if not valores:  # Si no hay condiciones, devuelve 0
        return 0.0

    modo = (logica or "todas").strip().lower()  # Se limpia el texto

    if modo in {"todas", "and", "y", "all"}:
        # Si todas deben cumplirse → promedio (con pesos si los hay)
        if pesos is None or not pesos:
            pesos = [1.0] * len(valores)
        total_pesos = sum(pesos) or 1.0
        return sum(valores) / total_pesos
    else:
        # Si basta con una (OR), se toma la que más cumple
        return max(valores)

def combinar(existente: float, nuevo: float) -> float:
    """
    Combina dos niveles de certeza para la misma enfermedad.
    Ejemplo: si una regla dice 0.7 y otra 0.5, se combinan sin pasarse de 1.
    """
    return 1.0 - (1.0 - existente) * (1.0 - nuevo)

# ============================================================
# ENCADENAMIENTO HACIA ADELANTE
# ============================================================
# Aquí se aplican todas las reglas para ver qué diagnósticos se cumplen
# con los datos que dio el usuario.

def encadenamiento_adelante(hechos: Dict[str, Any], reglas: List[Dict[str, Any]]):
    """
    Recorre todas las reglas, calcula cuánto se cumplen y genera:
      - los diagnósticos posibles,
      - las probabilidades,
      - las explicaciones y
      - las recomendaciones.
    """
    trazabilidad, puntajes, explicaciones, recomendaciones = [], {}, {}, {}

    # Se analizan todas las reglas una por una
    for regla in reglas:
        # Se calcula qué tanto se cumple cada condición
        grados = [grado_verdad(hechos, c) for c in regla["si"]]
        pesos = [float(c.get("peso", 1.0)) for c in regla["si"]]
        agregado = agregar(grados, regla.get("logica", "todas"), pesos)
        certeza_regla = agregado * float(regla.get("fc", 1.0))  # Se multiplica por su factor de certeza

        # Si la regla tuvo al menos algo de coincidencia
        if certeza_regla > 0:
            diagnostico = regla["entonces"]  # Ejemplo: "Neumonía"
            # Si ya había un valor previo, se combina con el nuevo
            puntajes[diagnostico] = combinar(puntajes.get(diagnostico, 0.0), certeza_regla)

            # Generar una explicación para el usuario
            condiciones_texto = []
            for c in regla["si"]:
                valor = hechos.get(c["variable"])
                try:
                    cumple = evaluar(valor, c["operador"], c["valor"])
                except Exception:
                    cumple = False
                texto = f"{c['variable'].replace('_',' ')}: {'✅' if cumple else '❌'} (valor: {valor}, espera: {c['operador']} {c['valor']}, peso={c.get('peso',1.0)})"
                condiciones_texto.append(texto)

            # Guarda la explicación completa de la regla
            frase = f"Regla {regla.get('id')}: " + "; ".join(condiciones_texto)
            explicaciones.setdefault(diagnostico, []).append(frase)

            # Si la regla tiene recomendaciones, se guardan
            if regla.get("recomendaciones"):
                recomendaciones.setdefault(diagnostico, [])
                for rec in regla["recomendaciones"]:
                    if rec not in recomendaciones[diagnostico]:
                        recomendaciones[diagnostico].append(rec)

            # Guarda un resumen de cómo se aplicó la regla (útil para depurar)
            trazabilidad.append({
                "regla_id": regla.get("id"),
                "diagnostico": diagnostico,
                "factor_certeza": round(certeza_regla, 3),
                "cobertura": round(agregado, 3),
            })

    # Devuelve todos los resultados al programa principal
    return trazabilidad, puntajes, explicaciones, recomendaciones

# ============================================================
# ENCADENAMIENTO HACIA ATRÁS
# ============================================================

def encadenamiento_atras(objetivo: str, reglas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Busca qué reglas terminan en el diagnóstico indicado.
    Devuelve qué condiciones se deben cumplir para confirmarlo.
    """
    requisitos = []
    for r in reglas:
        if r["entonces"] == objetivo:
            requisitos.append({
                "regla": r.get("id"),
                "logica": r.get("logica", "todas"),
                "fc": r.get("fc", 1.0),
                "condiciones": r["si"],
            })
    return requisitos
