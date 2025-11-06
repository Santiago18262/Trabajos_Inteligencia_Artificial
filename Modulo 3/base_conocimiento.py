# base_conocimiento.py
# -*- coding: utf-8 -*-
"""
Base de Conocimiento (BC) del Sistema Experto de diagnóstico de enfermedades respiratorias.
Contiene todas las variables de entrada y las reglas médicas en español.
Cada regla tiene un factor de certeza (fc) que representa la probabilidad del diagnóstico.
"""

from typing import List, Dict, Any

# ============================================================
# VARIABLES DEL PACIENTE
# ============================================================

VARIABLES = {
    "edad": {
        "tipo": "entero", "min": 0, "max": 110,
        "etiqueta": "Edad del paciente (años)",
        "descripcion": "Edad actual del paciente en años completos."
    },
    "sexo": {
        "tipo": "texto", "opciones": ["Femenino", "Masculino", "Otro"],
        "etiqueta": "Sexo del paciente",
        "descripcion": "Seleccione el sexo o género con el que el paciente se identifica."
    },
    "fiebre_c": {
        "tipo": "flotante", "min": 34.0, "max": 43.5,
        "etiqueta": "Temperatura corporal (°C)",
        "descripcion": "Temperatura medida con termómetro. Fiebre es ≥ 38 °C."
    },
    "tos": {
        "tipo": "texto", "opciones": ["No", "Seca", "Productiva"],
        "etiqueta": "Tipo de tos",
        "descripcion": "Tos seca (sin flema) o productiva (con flema o moco)."
    },
    "duracion_tos_dias": {
        "tipo": "entero", "min": 0, "max": 120,
        "etiqueta": "Duración de la tos (días)",
        "descripcion": "Número de días que el paciente ha tenido tos."
    },
    "disnea": {
        "tipo": "booleano",
        "etiqueta": "¿Presenta dificultad para respirar?",
        "descripcion": "Sensación de falta de aire o dificultad para respirar."
    },
    "sibilancias": {
        "tipo": "booleano",
        "etiqueta": "¿Tiene sibilancias?",
        "descripcion": "Silbidos o ruidos agudos al respirar, típicos del asma o EPOC."
    },
    "dolor_pecho": {
        "tipo": "booleano",
        "etiqueta": "¿Siente dolor en el pecho?",
        "descripcion": "Dolor o molestia en el área torácica, que puede aumentar al respirar."
    },
    "fatiga": {
        "tipo": "booleano",
        "etiqueta": "¿Siente cansancio o fatiga?",
        "descripcion": "Sensación de agotamiento físico o debilidad general."
    },
    "cefalea": {
        "tipo": "booleano",
        "etiqueta": "¿Tiene dolor de cabeza?",
        "descripcion": "Presencia de dolor o presión en la cabeza (cefalea)."
    },
    "mialgias": {
        "tipo": "booleano",
        "etiqueta": "¿Tiene dolores musculares?",
        "descripcion": "Dolor o molestia en los músculos, común en infecciones virales."
    },
    "odinofagia": {
        "tipo": "booleano",
        "etiqueta": "¿Tiene dolor de garganta?",
        "descripcion": "Dolor o ardor al tragar alimentos o líquidos."
    },
    "anosmia": {
        "tipo": "booleano",
        "etiqueta": "¿Ha perdido el sentido del olfato?",
        "descripcion": "Pérdida total o parcial del sentido del olfato (común en COVID-19)."
    },
    "satO2": {
        "tipo": "entero", "min": 50, "max": 100,
        "etiqueta": "Saturación de oxígeno (%)",
        "descripcion": "Medida de oxígeno en sangre con oxímetro. Normal: ≥ 95%."
    },
    "crepitantes": {
        "tipo": "booleano",
        "etiqueta": "¿Se escuchan crepitantes al auscultar?",
        "descripcion": "Ruidos tipo burbujeo en pulmones, típicos de neumonía o edema pulmonar."
    },
    "roncus": {
        "tipo": "booleano",
        "etiqueta": "¿Se escuchan roncus?",
        "descripcion": "Ruidos graves o roncos durante la respiración (por secreciones)."
    },
    "sibilos_auscultacion": {
        "tipo": "booleano",
        "etiqueta": "¿Se escuchan sibilos en la auscultación?",
        "descripcion": "Silbidos detectados al escuchar los pulmones con estetoscopio."
    },
    "rx_consolidacion": {
        "tipo": "booleano",
        "etiqueta": "¿La radiografía muestra consolidación pulmonar?",
        "descripcion": "Presencia de zonas blancas en la radiografía, típicas de neumonía."
    },
    "pcr_alta": {
        "tipo": "booleano",
        "etiqueta": "¿Proteína C reactiva elevada?",
        "descripcion": "Indicador de inflamación o infección sistémica en sangre."
    },
    "leucocitosis": {
        "tipo": "booleano",
        "etiqueta": "¿Leucocitos elevados (leucocitosis)?",
        "descripcion": "Aumento de glóbulos blancos, indicador de infección bacteriana."
    },

    # -------- Tabaquismo (actualizado) --------
    "tabaquismo": {
        "tipo": "texto", "opciones": ["No", "Exfumador", "Actual"],
        "etiqueta": "Tabaquismo",
        "descripcion": "Seleccione si el paciente fuma actualmente, fumó antes o nunca ha fumado."
    },
    "paquetes_por_dia": {
        "tipo": "flotante", "min": 0.0, "max": 8.0,
        "etiqueta": "Promedio de paquetes por día",
        "descripcion": "Cada paquete equivale a 20 cigarrillos. Ej.: 0.5 = 10 cig/día; 1 = 1 paquete diario."
    },
    "anios_fumando": {
        "tipo": "entero", "min": 0, "max": 95,
        "etiqueta": "Años fumando",
        "descripcion": "Número de años que el paciente ha fumado de forma regular (aproximado)."
    },

    # -------- SÍNTOMAS / SIGNOS nasofaríngeos (Resfriado, Faringitis) --------
    "congestion_nasal": {
        "tipo": "booleano",
        "etiqueta": "¿Tiene congestión nasal?",
        "descripcion": "Sensación de nariz tapada u obstruida."
    },
    "rinorrea": {
        "tipo": "texto", "opciones": ["No", "Clara", "Purulenta"],
        "etiqueta": "Tipo de secreción nasal (rinorrea)",
        "descripcion": "Secreción nasal acuosa (clara) o espesa/amarillenta (purulenta)."
    },
    # (Eliminadas: dolor_facial, halitosis)
    "exudado_amigdalino": {
        "tipo": "booleano",
        "etiqueta": "¿Exudado en amígdalas?",
        "descripcion": "Placas blanquecinas o exudado en las amígdalas, típico de faringitis bacteriana."
    },
    "adenopatias_cervicales": {
        "tipo": "booleano",
        "etiqueta": "¿Ganglios del cuello inflamados/dolorosos?",
        "descripcion": "Agrandamiento de ganglios linfáticos cervicales (dolorosos a la palpación)."
    },
    "estornudos": {
        "tipo": "booleano",
        "etiqueta": "¿Estornudos frecuentes?",
        "descripcion": "Episodios repetitivos de estornudos, comunes en resfriado alérgico/viral."
    },

    "exposicion_contaminantes": {
        "tipo": "booleano",
        "etiqueta": "¿Exposición a contaminantes o humo?",
        "descripcion": "Contacto frecuente con polvo, humo o sustancias irritantes."
    },
    "alergias_atopia": {
        "tipo": "booleano",
        "etiqueta": "¿Tiene alergias o atopia?",
        "descripcion": "Antecedentes de alergia, rinitis o dermatitis atópica."
    },
    "infeccion_respiratoria_reciente": {
        "tipo": "booleano",
        "etiqueta": "¿Tuvo infección respiratoria reciente?",
        "descripcion": "Resfriado o gripa reciente que pudo afectar vías respiratorias."
    },
    "contacto_covid": {
        "tipo": "booleano",
        "etiqueta": "¿Tuvo contacto con un caso confirmado de COVID-19?",
        "descripcion": "Indique si ha estado cerca de una persona diagnosticada con COVID-19."
    },
    "estacional_invierno": {
        "tipo": "booleano",
        "etiqueta": "¿Estamos en temporada invernal?",
        "descripcion": "Ayuda a valorar influenza u otras infecciones estacionales."
    },
}

# ============================================================
# REGLAS DE PRODUCCIÓN (SI... ENTONCES)
# ============================================================

REGLAS: List[Dict[str, Any]] = [

    # === ASMA ===
    # Interpretación médica: El sistema infiere Asma si detecta silbidos al respirar + tos seca + alergia conocida.
    # (Escenario típico de asma alérgica).
    {
        "id": "ASMA_1",
        "si": [
            {"variable": "sibilancias", "operador": "==", "valor": True},
            {"variable": "tos", "operador": "in", "valor": ["Seca"], "peso": 0.8},
            {"variable": "alergias_atopia", "operador": "==", "valor": True},
        ],
        "entonces": "Asma",
        "fc": 0.90,
        "logica": "todas",
        "recomendaciones": [
            "Realizar espirometría con broncodilatador",
            "Evitar alérgenos conocidos",
            "Usar beta-agonista de acción corta si es necesario"
        ]
    },
    # Interpretación médica: Asma por esfuerzo: disnea + sibilancias audibles + sibilos en auscultación.
    # (Escenario típico inducido por ejercicio o irritantes).
    {
        "id": "ASMA_2",
        "si": [
            {"variable": "sibilancias", "operador": "==", "valor": True},
            {"variable": "disnea", "operador": "==", "valor": True},
            {"variable": "sibilos_auscultacion", "operador": "==", "valor": True, "peso": 0.9},
        ],
        "entonces": "Asma",
        "fc": 0.80,
        "logica": "todas",
        "recomendaciones": [
            "Espirometría de control",
            "Prueba de óxido nítrico exhalado si está disponible"
        ]
    },

    # === NEUMONÍA ===
    # Interpretación médica: Fiebre alta + tos productiva + disnea + crepitantes.
    # (Escenario clínico típico de neumonía).
    {
        "id": "NEUMONIA_1",
        "si": [
            {"variable": "fiebre_c", "operador": ">=", "valor": 38.5},
            {"variable": "tos", "operador": "==", "valor": "Productiva"},
            {"variable": "disnea", "operador": "==", "valor": True},
            {"variable": "crepitantes", "operador": "==", "valor": True},
        ],
        "entonces": "Neumonía",
        "fc": 0.85,
        "logica": "todas",
        "recomendaciones": [
            "Radiografía de tórax",
            "Oximetría de pulso",
            "Biometría hemática",
            "Iniciar antibiótico según guía local"
        ]
    },
    # Interpretación médica: Hallazgo radiográfico consistente + fiebre y leucocitosis.
    # (Escenario de confirmación por imagen).
    {
        "id": "NEUMONIA_2_RX",
        "si": [
            {"variable": "rx_consolidacion", "operador": "==", "valor": True},
            {"variable": "fiebre_c", "operador": ">=", "valor": 38.0, "peso": 0.8},
            {"variable": "leucocitosis", "operador": "==", "valor": True, "peso": 0.8},
        ],
        "entonces": "Neumonía",
        "fc": 0.90,
        "logica": "todas",
        "recomendaciones": [
            "Iniciar antibiótico empírico",
            "Control clínico en 48–72 horas"
        ]
    },

    # === BRONQUITIS AGUDA ===
    # Interpretación médica: Tos subaguda post-IR, sin consolidación, con pocos síntomas nasales.
    {
        "id": "BRONQUITIS_1",
        "si": [
            {"variable": "tos", "operador": "in", "valor": ["Seca", "Productiva"]},
            {"variable": "infeccion_respiratoria_reciente", "operador": "==", "valor": True},
            {"variable": "duracion_tos_dias", "operador": "<=", "valor": 21},
            {"variable": "rx_consolidacion", "operador": "==", "valor": False},
            {"variable": "congestion_nasal", "operador": "==", "valor": False, "peso": 0.8},
            {"variable": "rinorrea", "operador": "!=", "valor": "Clara", "peso": 0.8}
        ],
        "entonces": "Bronquitis aguda",
        "fc": 0.65,
        "logica": "todas",
        "recomendaciones": [
            "Tratamiento sintomático (descanso e hidratación)",
            "Evitar el uso de antibióticos innecesarios"
        ]
    },
    # Interpretación médica: Tos + fiebre baja + sin crepitantes, con escasa congestión nasal.
    {
        "id": "BRONQUITIS_2",
        "si": [
            {"variable": "tos", "operador": "in", "valor": ["Seca", "Productiva"]},
            {"variable": "fiebre_c", "operador": "<", "valor": 38.0},
            {"variable": "crepitantes", "operador": "==", "valor": False},
            {"variable": "congestion_nasal", "operador": "==", "valor": False, "peso": 0.7}
        ],
        "entonces": "Bronquitis aguda",
        "fc": 0.55,
        "logica": "todas",
        "recomendaciones": [
            "Analgésicos y antipiréticos si hay fiebre",
            "Revalorar si aparecen signos de neumonía"
        ]
    },

    # === EPOC (con paquetes_por_dia y anios_fumando) ===
    # Interpretación médica: ≥40 años + fumador/exfumador + consumo alto (≥1 paquete/día) + disnea y sibilancias.
    {
        "id": "EPOC_1",
        "si": [
            {"variable": "edad", "operador": ">=", "valor": 40},
            {"variable": "tabaquismo", "operador": "in", "valor": ["Exfumador", "Actual"]},
            {"variable": "paquetes_por_dia", "operador": ">=", "valor": 1.0},
            {"variable": "disnea", "operador": "==", "valor": True},
            {"variable": "sibilancias", "operador": "==", "valor": True},
        ],
        "entonces": "EPOC",
        "fc": 0.80,
        "logica": "todas",
        "recomendaciones": [
            "Espirometría diagnóstica (FEV1/FVC)",
            "Abandono del tabaquismo",
            "Vacunas contra influenza y neumococo"
        ]
    },
    # Interpretación médica: Exposición prolongada (≥15 años) + consumo moderado (≥0.5 paquetes/día) + síntomas respiratorios.
    {
        "id": "EPOC_2",
        "si": [
            {"variable": "edad", "operador": ">=", "valor": 40},
            {"variable": "tabaquismo", "operador": "in", "valor": ["Exfumador", "Actual"]},
            {"variable": "anios_fumando", "operador": ">=", "valor": 15, "peso": 0.9},
            {"variable": "paquetes_por_dia", "operador": ">=", "valor": 0.5, "peso": 0.9},
            {"variable": "disnea", "operador": "==", "valor": True},
            {"variable": "sibilancias", "operador": "==", "valor": True},
        ],
        "entonces": "EPOC",
        "fc": 0.75,
        "logica": "todas",
        "recomendaciones": [
            "Espirometría diagnóstica (FEV1/FVC)",
            "Abandono del tabaquismo",
            "Vacunas contra influenza y neumococo"
        ]
    },

    # === COVID-19 ===
    # Interpretación médica: Fiebre + tos + fatiga + contacto confirmado.
    {
        "id": "COVID_1",
        "si": [
            {"variable": "fiebre_c", "operador": ">=", "valor": 37.8},
            {"variable": "tos", "operador": "in", "valor": ["Seca", "Productiva"]},
            {"variable": "fatiga", "operador": "==", "valor": True},
            {"variable": "contacto_covid", "operador": "==", "valor": True, "peso": 0.9},
        ],
        "entonces": "COVID-19",
        "fc": 0.80,
        "logica": "todas",
        "recomendaciones": [
            "Prueba diagnóstica (antígeno o PCR)",
            "Aislamiento domiciliario",
            "Monitoreo de saturación de oxígeno si hay factores de riesgo"
        ]
    },
    # Interpretación médica: Anosmia + fiebre leve + odinofagia.
    {
        "id": "COVID_2_ANOSMIA",
        "si": [
            {"variable": "anosmia", "operador": "==", "valor": True},
            {"variable": "fiebre_c", "operador": ">=", "valor": 37.5, "peso": 0.6},
            {"variable": "odinofagia", "operador": "==", "valor": True, "peso": 0.6},
        ],
        "entonces": "COVID-19",
        "fc": 0.70,
        "logica": "todas",
        "recomendaciones": [
            "Realizar prueba de detección",
            "Aislamiento y vigilancia de síntomas"
        ]
    },

    # === INFLUENZA ===
    # Interpretación médica: Fiebre alta + mialgias + cefalea + invierno.
    {
        "id": "INFLUENZA_1",
        "si": [
            {"variable": "fiebre_c", "operador": ">=", "valor": 38.0},
            {"variable": "mialgias", "operador": "==", "valor": True},
            {"variable": "cefalea", "operador": "==", "valor": True},
            {"variable": "estacional_invierno", "operador": "==", "valor": True},
        ],
        "entonces": "Influenza",
        "fc": 0.75,
        "logica": "todas",
        "recomendaciones": [
            "Prueba rápida de influenza",
            "Administrar antiviral si cumple criterios",
            "Reposo e hidratación adecuada"
        ]
    },

    # === RESFRIADO COMÚN ===
    # (Viral leve; patrón nasal dominante)
    {
        "id": "RESFRIADO_1",
        "si": [
            {"variable": "rinorrea", "operador": "==", "valor": "Clara"},
            {"variable": "congestion_nasal", "operador": "==", "valor": True},
            {"variable": "odinofagia", "operador": "==", "valor": True, "peso": 0.6},
            {"variable": "fiebre_c", "operador": "<", "valor": 38.0},
            {"variable": "rx_consolidacion", "operador": "==", "valor": False}
        ],
        "entonces": "Resfriado común",
        "fc": 0.85,   # ↑ antes 0.80
        "logica": "todas",
        "recomendaciones": [
            "Hidratación y reposo",
            "Lavados nasales con solución salina",
            "Analgésicos/antipiréticos si es necesario"
        ]
    },
    {
        "id": "RESFRIADO_2",
        "si": [
            {"variable": "estornudos", "operador": "==", "valor": True},
            {"variable": "rinorrea", "operador": "==", "valor": "Clara"},
            {"variable": "congestion_nasal", "operador": "==", "valor": True},
            {"variable": "tos", "operador": "in", "valor": ["No", "Seca"], "peso": 0.5},
            {"variable": "fiebre_c", "operador": "<", "valor": 38.0}
        ],
        "entonces": "Resfriado común",
        "fc": 0.80,   # ↑ antes 0.75
        "logica": "todas",
        "recomendaciones": [
            "Medidas sintomáticas",
            "Evitar antibióticos"
        ]
    },
    {
        "id": "RESFRIADO_3",
        "si": [
            {"variable": "congestion_nasal", "operador": "==", "valor": True},
            {"variable": "rinorrea", "operador": "==", "valor": "Clara"},
            {"variable": "estornudos", "operador": "==", "valor": True},
            {"variable": "fiebre_c", "operador": "<", "valor": 38.0},
            {"variable": "rx_consolidacion", "operador": "==", "valor": False}
        ],
        "entonces": "Resfriado común",
        "fc": 0.82,   # ↑ antes 0.78
        "logica": "todas",
        "recomendaciones": [
            "Hidratación y reposo",
            "Lavados nasales con solución salina",
            "Analgésicos/antipiréticos si es necesario"
        ]
    },

    # === FARINGITIS ===
    # Faringitis viral: odinofagia + tos; ↓ peso si hay patrón nasal claro (congestión + rinorrea clara)
    {
        "id": "FARINGITIS_1_VIRAL",
        "si": [
            {"variable": "odinofagia", "operador": "==", "valor": True},
            {"variable": "tos", "operador": "in", "valor": ["Seca", "Productiva"]},
            {"variable": "fiebre_c", "operador": "<", "valor": 38.0},
            {"variable": "congestion_nasal", "operador": "==", "valor": False, "peso": 0.7},
            {"variable": "rinorrea", "operador": "!=", "valor": "Clara", "peso": 0.7}
        ],
        "entonces": "Faringitis (viral)",
        "fc": 0.55,   # ↓ antes 0.60
        "logica": "todas",
        "recomendaciones": [
            "Gárgaras con agua tibia y sal",
            "Analgésicos/antipiréticos",
            "Evitar antibióticos"
        ]
    },
    # Interpretación médica: Faringitis estreptocócica: odinofagia intensa + exudado + adenopatías + fiebre ≥ 38 °C + sin tos.
    {
        "id": "FARINGITIS_2_BACTERIANA",
        "si": [
            {"variable": "odinofagia", "operador": "==", "valor": True},
            {"variable": "exudado_amigdalino", "operador": "==", "valor": True},
            {"variable": "adenopatias_cervicales", "operador": "==", "valor": True},
            {"variable": "fiebre_c", "operador": ">=", "valor": 38.0},
            {"variable": "tos", "operador": "==", "valor": "No", "peso": 0.8}
        ],
        "entonces": "Faringitis (bacteriana)",
        "fc": 0.85,
        "logica": "todas",
        "recomendaciones": [
            "Prueba rápida de estreptococo o cultivo faríngeo",
            "Antibiótico si la prueba es positiva (según guía local)",
            "Analgésicos/antipiréticos"
        ]
    },
]
