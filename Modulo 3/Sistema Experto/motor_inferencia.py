"""
Este archivo es mediante el cual funciona el sistema experto.
Aquí se analizan los datos que ingresa el usuario (síntomas, signos, etc.)
y se comparan con las reglas de la base de conocimiento para llegar a
un posible diagnóstico y sus probabilidades.
"""
# ↑ Docstring: descripción general del módulo y su propósito.

from typing import Dict, Any, List  # Solo sirve para aclarar el tipo de datos (diccionarios, listas, etc.)

# ============================================================
# FUNCIÓN QUE REVISA SI UNA CONDICIÓN SE CUMPLE
# ============================================================
# Esta función compara lo que dijo el usuario con lo que espera la regla.

def evaluar(valor_usuario, operador, valor_regla):
    """Compara el valor del usuario con el valor esperado según el operador."""
    if operador == "==": return valor_usuario == valor_regla     # Igual: compara igualdad exacta
    if operador == "!=": return valor_usuario != valor_regla     # Diferente: compara desigualdad
    if operador == ">=": return valor_usuario >= valor_regla     # Mayor o igual: números o comparables
    if operador == "<=": return valor_usuario <= valor_regla     # Menor o igual
    if operador == ">":  return valor_usuario > valor_regla      # Mayor que
    if operador == "<":  return valor_usuario < valor_regla      # Menor que
    if operador == "in": return valor_usuario in valor_regla     # Pertenencia: el valor del usuario está dentro de una lista/conjunto
    if operador == "contiene": return valor_regla in valor_usuario  # Contención: cadenas/listas que contienen el valor de la regla
    return False  # Si no se reconoce el operador, la condición se considera no cumplida

# ============================================================
# FUNCIÓN QUE CALCULA QUÉ TANTO SE CUMPLE UNA CONDICIÓN
# ============================================================

def grado_verdad(hechos: Dict[str, Any], condicion: Dict[str, Any]) -> float:
    """
    Calcula si una condición se cumple (1) o no (0).
    También puede usar un "peso" para darle más importancia.
    """
    variable = condicion["variable"]          # Nombre de la variable a evaluar (clave en 'hechos')
    operador = condicion["operador"]          # Operador de comparación (==, !=, >, <, >=, <=, in, contiene)
    valor = condicion["valor"]                # Valor esperado por la condición/regla
    peso = float(condicion.get("peso", 1.0))  # Peso opcional de la condición (por defecto 1.0)

    # Si el usuario no proporcionó ese dato en 'hechos', no se puede evaluar
    if variable not in hechos:
        return 0.0                            # Devuelve 0 (no cumple, sin aportar al puntaje)

    # Intenta evaluar la condición; si hay error (tipos/formatos), se toma como no cumplida
    try:
        cumple = evaluar(hechos[variable], operador, valor)  # True/False según comparación
    except Exception:
        cumple = False                                       # Cualquier excepción se traduce a no cumplimiento

    # Convierte el cumplimiento a 1.0/0.0 y lo multiplica por el peso declarado
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
    if not valores:                      # Caso borde: sin condiciones → no hay cumplimiento
        return 0.0

    modo = (logica or "todas").strip().lower()  # Normaliza el texto de la lógica (maneja None/espacios/mayúsculas)

    if modo in {"todas", "and", "y", "all"}:    # Interpretación de AND en varios idiomas/alias
        # Si todas deben cumplirse → promedio ponderado por 'pesos' (si vienen)
        if pesos is None or not pesos:          # Si no hay pesos explícitos, se asumen todos a 1
            pesos = [1.0] * len(valores)
        total_pesos = sum(pesos) or 1.0         # Evita división entre 0 si pesos suma 0
        return sum(valores) / total_pesos       # 'valores' ya vienen ponderados (0 o peso), se normaliza por suma de pesos
    else:
        # Si basta con una (OR) → se toma el mayor grado (la condición más fuerte)
        return max(valores)

def combinar(existente: float, nuevo: float) -> float:
    """
    Combina dos niveles de certeza para la misma enfermedad.
    Ejemplo: si una regla dice 0.7 y otra 0.5, se combinan sin pasarse de 1.
    """
    return 1.0 - (1.0 - existente) * (1.0 - nuevo)  # Fórmula de combinación probabilística independiente (Noisy-OR)

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
    trazabilidad, puntajes, explicaciones, recomendaciones = [], {}, {}, {}  # Estructuras de salida

    # Se analizan todas las reglas una por una
    for regla in reglas:                                                     # Itera regla por regla
        # Se calcula qué tanto se cumple cada condición de la regla
        grados = [grado_verdad(hechos, c) for c in regla["si"]]             # Lista de grados (0..peso) por condición
        pesos = [float(c.get("peso", 1.0)) for c in regla["si"]]            # Pesos declarados para normalizar el AND
        agregado = agregar(grados, regla.get("logica", "todas"), pesos)     # Resultado agregado (AND/OR) de la regla
        certeza_regla = agregado * float(regla.get("fc", 1.0))              # Ajuste por factor de certeza de la regla

        # Si la regla aportó alguna certeza (>0), se contabiliza en el diagnóstico
        if certeza_regla > 0:
            diagnostico = regla["entonces"]                                  # Conclusión de la regla (dx)
            # Combina con puntaje previo del mismo dx, si existiera
            puntajes[diagnostico] = combinar(puntajes.get(diagnostico, 0.0), certeza_regla)

            # Genera explicación legible para el usuario (por cada condición)
            condiciones_texto = []                                           # Acumula textos de condiciones
            for c in regla["si"]:                                            # Recorre cada condición de la regla
                valor = hechos.get(c["variable"])                            # Valor ingresado por el usuario (si existe)
                try:
                    cumple = evaluar(valor, c["operador"], c["valor"])       # Evalúa nuevamente para marcar ✅/❌
                except Exception:
                    cumple = False
                texto = (
                    f"{c['variable'].replace('_',' ')}: "
                    f"{'✅' if cumple else '❌'} "
                    f"(valor: {valor}, espera: {c['operador']} {c['valor']}, peso={c.get('peso',1.0)})"
                )
                condiciones_texto.append(texto)                              # Agrega línea de explicación

            # Guarda la explicación completa de la regla (incluye ID de la regla)
            frase = f"Regla {regla.get('id')}: " + "; ".join(condiciones_texto)
            explicaciones.setdefault(diagnostico, []).append(frase)          # Añade al listado del dx

            # Si la regla define recomendaciones, se agregan sin duplicarlas
            if regla.get("recomendaciones"):
                recomendaciones.setdefault(diagnostico, [])                   # Crea lista si no existe
                for rec in regla["recomendaciones"]:
                    if rec not in recomendaciones[diagnostico]:               # Evita duplicados
                        recomendaciones[diagnostico].append(rec)

            # Guarda trazas resumidas para depuración/inspección
            trazabilidad.append({
                "regla_id": regla.get("id"),                                  # ID de la regla aplicada
                "diagnostico": diagnostico,                                   # Diagnóstico objetivo de la regla
                "factor_certeza": round(certeza_regla, 3),                    # Certeza final aportada por la regla
                "cobertura": round(agregado, 3),                              # Agregado antes de aplicar fc
            })

    # Devuelve todas las estructuras calculadas al llamador (UI)
    return trazabilidad, puntajes, explicaciones, recomendaciones

# ============================================================
# ENCADENAMIENTO HACIA ATRÁS
# ============================================================

def encadenamiento_atras(objetivo: str, reglas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Busca qué reglas terminan en el diagnóstico indicado.
    Devuelve qué condiciones se deben cumplir para confirmarlo.
    """
    requisitos = []                                                          # Lista de reglas que concluyen 'objetivo'
    for r in reglas:                                                         # Recorre todas las reglas
        if r["entonces"] == objetivo:                                        # Selecciona las que concluyen ese dx
            requisitos.append({
                "regla": r.get("id"),                                        # ID de la regla
                "logica": r.get("logica", "todas"),                          # Lógica de combinación usada por la regla
                "fc": r.get("fc", 1.0),                                      # Factor de certeza de la regla
                "condiciones": r["si"],                                      # Condiciones que deberían cumplirse
            })
    return requisitos                                                         # Devuelve el listado de requisitos
