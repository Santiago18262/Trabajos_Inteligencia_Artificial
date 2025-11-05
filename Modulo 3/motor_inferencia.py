# motor_inferencia.py
# -*- coding: utf-8 -*-
"""
Motor de inferencia del Sistema Experto de diagnóstico respiratorio.
Realiza el razonamiento lógico aplicando las reglas de la base de conocimiento
a los datos ingresados por el usuario (hechos).

Incluye:
- Encadenamiento hacia adelante (para calcular diagnósticos)
- Encadenamiento hacia atrás (para verificar qué faltaría confirmar)
"""

from typing import Dict, Any, List

# ============================================================
# FUNCIÓN DE EVALUACIÓN DE CONDICIONES
# ============================================================
# Compara el valor ingresado por el usuario con el valor esperado en la regla.
# Usa los operadores lógicos definidos (==, >, <, in, etc.)

def evaluar(valor_usuario, operador, valor_regla):
    if operador == "==": return valor_usuario == valor_regla
    if operador == "!=": return valor_usuario != valor_regla
    if operador == ">=": return valor_usuario >= valor_regla
    if operador == "<=": return valor_usuario <= valor_regla
    if operador == ">":  return valor_usuario > valor_regla
    if operador == "<":  return valor_usuario < valor_regla
    if operador == "in": return valor_usuario in valor_regla
    if operador == "contiene": return valor_regla in valor_usuario
    return False

# ============================================================
# FUNCIÓN PARA OBTENER EL GRADO DE CUMPLIMIENTO DE UNA CONDICIÓN
# ============================================================

def grado_verdad(hechos: Dict[str, Any], condicion: Dict[str, Any]) -> float:
    variable = condicion["variable"]
    operador = condicion["operador"]
    valor = condicion["valor"]
    peso = float(condicion.get("peso", 1.0))  # ponderación opcional

    # Si el dato no fue ingresado, no se puede evaluar
    if variable not in hechos:
        return 0.0

    try:
        cumple = evaluar(hechos[variable], operador, valor)
    except Exception:
        cumple = False

    # Si cumple → 1.0 (verdadero), si no → 0.0 (falso)
    return (1.0 if cumple else 0.0) * peso

# ============================================================
# FUNCIONES DE AGREGACIÓN Y COMBINACIÓN DE REGLAS
# ============================================================

def agregar(valores: List[float], logica: str) -> float:
    """Si la lógica es 'todas', toma el mínimo; si es 'alguna', el máximo."""
    return min(valores) if logica == "todas" else max(valores)

def combinar(existente: float, nuevo: float) -> float:
    """Combina factores de certeza múltiples de la misma enfermedad."""
    return 1.0 - (1.0 - existente) * (1.0 - nuevo)

# ============================================================
# ENCADENAMIENTO HACIA ADELANTE
# ============================================================
# Toma los hechos (síntomas ingresados) y aplica todas las reglas posibles
# para generar nuevos diagnósticos con su nivel de probabilidad.

def encadenamiento_adelante(hechos: Dict[str, Any], reglas: List[Dict[str, Any]]):
    trazabilidad, puntajes, explicaciones, recomendaciones = [], {}, {}, {}

    for regla in reglas:
        grados = [grado_verdad(hechos, c) for c in regla["si"]]
        agregado = agregar(grados, regla.get("logica", "todas"))
        certeza_regla = agregado * float(regla.get("cf", 1.0))

        if certeza_regla > 0:
            diagnostico = regla["entonces"]
            puntajes[diagnostico] = combinar(puntajes.get(diagnostico, 0.0), certeza_regla)

            # Construir texto explicativo
            condiciones_texto = []
            for c in regla["si"]:
                valor = hechos.get(c["variable"])
                cumple = evaluar(valor, c["operador"], c["valor"])
                texto = f"{c['variable'].replace('_',' ')}: {'✔️' if cumple else '⛔'} (valor: {valor}, espera: {c['operador']} {c['valor']})"
                condiciones_texto.append(texto)

            frase = f"Regla {regla.get('id')}: " + "; ".join(condiciones_texto)
            explicaciones.setdefault(diagnostico, []).append(frase)

            # Guardar recomendaciones asociadas
            if regla.get("recomendaciones"):
                recomendaciones.setdefault(diagnostico, [])
                for rec in regla["recomendaciones"]:
                    if rec not in recomendaciones[diagnostico]:
                        recomendaciones[diagnostico].append(rec)

            trazabilidad.append({
                "regla_id": regla.get("id"),
                "diagnostico": diagnostico,
                "factor_certeza": round(certeza_regla, 3),
            })

    return trazabilidad, puntajes, explicaciones, recomendaciones

# ============================================================
# ENCADENAMIENTO HACIA ATRÁS (REQUISITOS DE CONFIRMACIÓN)
# ============================================================
# Sirve para saber qué condiciones son necesarias para confirmar un diagnóstico
# (se usa automáticamente para los diagnósticos más probables).

def encadenamiento_atras(objetivo: str, reglas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    requisitos = []
    for r in reglas:
        if r["entonces"] == objetivo:
            requisitos.append({
                "regla": r.get("id"),
                "logica": r.get("logica", "todas"),
                "cf": r.get("cf", 1.0),
                "condiciones": r["si"],
            })
    return requisitos

def encadenamiento_atras_automatico(puntajes: Dict[str, float], reglas: List[Dict[str, Any]], top_n: int = 3):
    """Aplica encadenamiento hacia atrás automático para los diagnósticos más probables."""
    orden = sorted(puntajes.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return {dx: encadenamiento_atras(dx, reglas) for dx, _ in orden}
