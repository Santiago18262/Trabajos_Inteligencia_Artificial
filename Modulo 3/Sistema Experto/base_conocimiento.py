
"""
Base de Conocimiento (del Sistema Experto de diagnóstico de enfermedades respiratorias.
Contiene todas las variables de entrada y las reglas médicas.
Cada regla tiene un factor de certeza (fc) que representa la probabilidad del diagnóstico.
"""

from typing import List, Dict, Any  # Tipos para anotar listas/diccionarios y mayor claridad estática

# ============================================================
# VARIABLES DEL PACIENTE
# ============================================================

VARIABLES = {  # Diccionario maestro: define cada variable de entrada y sus metadatos para la validación
    "edad": {  # Edad del paciente
        "tipo": "entero", "min": 0, "max": 110,                 # Tipo entero con límites de validación
        "etiqueta": "Edad del paciente (años)",                 # Texto mostrado en la UI
        "descripcion": "Edad actual del paciente en años completos."  # Ayuda contextual
    },
    "sexo": {  # Sexo/género
        "tipo": "texto", "opciones": ["Femenino", "Masculino", "Otro"],  # Select de opciones
        "etiqueta": "Sexo del paciente",
        "descripcion": "Seleccione el sexo o género con el que el paciente se identifica."
    },
    "fiebre_c": {  # Temperatura en °C
        "tipo": "flotante", "min": 34.0, "max": 43.5,           # Rango razonable de temperatura humana
        "etiqueta": "Temperatura corporal (°C)",
        "descripcion": "Temperatura medida con termómetro. Fiebre es ≥ 38 °C."
    },
    "tos": {  # Tipo de tos
        "tipo": "texto", "opciones": ["No", "Seca", "Productiva"],  # Clasificación básica
        "etiqueta": "Tipo de tos",
        "descripcion": "Tos seca (sin flema) o productiva (con flema o moco)."
    },
    "duracion_tos_dias": {  # Días con tos
        "tipo": "entero", "min": 0, "max": 120,
        "etiqueta": "Duración de la tos (días)",
        "descripcion": "Número de días que el paciente ha tenido tos."
    },
    "disnea": {  # Falta de aire
        "tipo": "booleano",
        "etiqueta": "¿Presenta dificultad para respirar?",
        "descripcion": "Sensación de falta de aire o dificultad para respirar."
    },
    "sibilancias": {  # Sibilancias referidas por el paciente
        "tipo": "booleano",
        "etiqueta": "¿Tiene sibilancias?",
        "descripcion": "Silbidos o ruidos agudos al respirar, típicos del asma o EPOC."
    },
    "dolor_pecho": {  # Dolor torácico
        "tipo": "booleano",
        "etiqueta": "¿Siente dolor en el pecho?",
        "descripcion": "Dolor o molestia en el área torácica, que puede aumentar al respirar."
    },
    "fatiga": {  # Cansancio
        "tipo": "booleano",
        "etiqueta": "¿Siente cansancio o fatiga?",
        "descripcion": "Sensación de agotamiento físico o debilidad general."
    },
    "cefalea": {  # Dolor de cabeza
        "tipo": "booleano",
        "etiqueta": "¿Tiene dolor de cabeza?",
        "descripcion": "Presencia de dolor o presión en la cabeza (cefalea)."
    },
    "mialgias": {  # Dolores musculares
        "tipo": "booleano",
        "etiqueta": "¿Tiene dolores musculares?",
        "descripcion": "Dolor o molestia en los músculos, común en infecciones virales."
    },
    "odinofagia": {  # Dolor de garganta
        "tipo": "booleano",
        "etiqueta": "¿Tiene dolor de garganta?",
        "descripcion": "Dolor o ardor al tragar alimentos o líquidos."
    },
    "anosmia": {  # Pérdida de olfato
        "tipo": "booleano",
        "etiqueta": "¿Ha perdido el sentido del olfato?",
        "descripcion": "Pérdida total o parcial del sentido del olfato (común en COVID-19)."
    },
    "satO2": {  # Saturación de oxígeno
        "tipo": "entero", "min": 50, "max": 100,
        "etiqueta": "Saturación de oxígeno (%)",
        "descripcion": "Medida de oxígeno en sangre con oxímetro. Normal: ≥ 95%."
    },
    "crepitantes": {  # Hallazgo en auscultación
        "tipo": "booleano",
        "etiqueta": "¿Se escuchan crepitantes al auscultar?",
        "descripcion": "Ruidos tipo burbujeo en pulmones, típicos de neumonía o edema pulmonar."
    },
    "roncus": {  # Roncus en auscultación
        "tipo": "booleano",
        "etiqueta": "¿Se escuchan roncus?",
        "descripcion": "Ruidos graves o roncos durante la respiración (por secreciones)."
    },
    "sibilos_auscultacion": {  # Sibilos en auscultación
        "tipo": "booleano",
        "etiqueta": "¿Se escuchan sibilos en la auscultación?",
        "descripcion": "Silbidos detectados al escuchar los pulmones con estetoscopio."
    },
    "rx_consolidacion": {  # Hallazgo radiográfico
        "tipo": "booleano",
        "etiqueta": "¿La radiografía muestra consolidación pulmonar?",
        "descripcion": "Presencia de zonas blancas en la radiografía, típicas de neumonía."
    },
    "pcr_alta": {  # Proteína C reactiva elevada
        "tipo": "booleano",
        "etiqueta": "¿Proteína C reactiva elevada?",
        "descripcion": "Indicador de inflamación o infección sistémica en sangre."
    },
    "leucocitosis": {  # Leucocitos altos
        "tipo": "booleano",
        "etiqueta": "¿Leucocitos elevados (leucocitosis)?",
        "descripcion": "Aumento de glóbulos blancos, indicador de infección bacteriana."
    },

    "tabaquismo": {  # Estado de tabaquismo
        "tipo": "texto", "opciones": ["No", "Exfumador", "Actual"],  # Clasificación básica
        "etiqueta": "Tabaquismo",
        "descripcion": "Seleccione si el paciente fuma actualmente, fumó antes o nunca ha fumado."
    },
    "paquetes_por_dia": {  # Promedio de paquetes/día
        "tipo": "flotante", "min": 0.0, "max": 8.0,   # 1 paquete - 20 cig/día
        "etiqueta": "Promedio de paquetes por día",
        "descripcion": "Cada paquete equivale a 20 cigarrillos. Ej.: 0.5 = 10 cig/día; 1 = 1 paquete diario."
    },
    "anios_fumando": {  # Años totales fumando
        "tipo": "entero", "min": 0, "max": 95,
        "etiqueta": "Años fumando",
        "descripcion": "Número de años que el paciente ha fumado de forma regular (aproximado)."
    },

    "congestion_nasal": {  # Nariz tapada
        "tipo": "booleano",
        "etiqueta": "¿Tiene congestión nasal?",
        "descripcion": "Sensación de nariz tapada u obstruida."
    },
    "rinorrea": {  # Tipo de secreción
        "tipo": "texto", "opciones": ["No", "Clara", "Purulenta"],
        "etiqueta": "Tipo de secreción nasal (rinorrea)",
        "descripcion": "Secreción nasal acuosa (clara) o espesa/amarillenta (purulenta)."
    },
    "exudado_amigdalino": {  # Placas en amígdalas
        "tipo": "booleano",
        "etiqueta": "¿Exudado en amígdalas?",
        "descripcion": "Placas blanquecinas o exudado en las amígdalas, típico de faringitis bacteriana."
    },
    "adenopatias_cervicales": {  # Ganglios cervicales
        "tipo": "booleano",
        "etiqueta": "¿Ganglios del cuello inflamados/dolorosos?",
        "descripcion": "Agrandamiento de ganglios linfáticos cervicales (dolorosos a la palpación)."
    },
    "estornudos": {  # Estornudos frecuentes
        "tipo": "booleano",
        "etiqueta": "¿Estornudos frecuentes?",
        "descripcion": "Episodios repetitivos de estornudos, comunes en resfriado alérgico/viral."
    },

    "exposicion_contaminantes": {  # Irritantes ambientales
        "tipo": "booleano",
        "etiqueta": "¿Exposición a contaminantes o humo?",
        "descripcion": "Contacto frecuente con polvo, humo o sustancias irritantes."
    },
    "alergias_atopia": {  # Antecedentes alérgicos/atópicos
        "tipo": "booleano",
        "etiqueta": "¿Tiene alergias o atopia?",
        "descripcion": "Antecedentes de alergia, rinitis o dermatitis atópica."
    },
    "infeccion_respiratoria_reciente": {  # Infección reciente
        "tipo": "booleano",
        "etiqueta": "¿Tuvo infección respiratoria reciente?",
        "descripcion": "Resfriado o gripa reciente que pudo afectar vías respiratorias."
    },
    "contacto_covid": {  # Contacto con caso confirmado
        "tipo": "booleano",
        "etiqueta": "¿Tuvo contacto con un caso confirmado de COVID-19?",
        "descripcion": "Indique si ha estado cerca de una persona diagnosticada con COVID-19."
    },
    "estacional_invierno": {  # Estacionalidad
        "tipo": "booleano",
        "etiqueta": "¿Estamos en temporada invernal?",
        "descripcion": "Ayuda a valorar influenza u otras infecciones estacionales."
    },
}

# ============================================================
# REGLAS DE PRODUCCIÓN 
# ============================================================

REGLAS: List[Dict[str, Any]] = [  # Lista de reglas; cada regla contiene condiciones, conclusión, fc y recomendaciones

    # === ASMA ===
    # Tipo: Asma alérgica (atópica) con tos seca predominante — compatible con hiperreactividad bronquial
    {
        "id": "ASMA_1",
        "si": [
            {"variable": "sibilancias", "operador": "==", "valor": True},
            {"variable": "tos", "operador": "in", "valor": ["Seca"], "peso": 0.8},
            {"variable": "alergias_atopia", "operador": "==", "valor": True},
        ],
        "entonces": "Asma",
        "fc": 0.90,
        "recomendaciones": [
            "Realizar espirometría con broncodilatador",
            "Evitar alérgenos conocidos"
        ]
    },
    # Tipo: Asma con obstrucción demostrable en clínica / posible exacerbación (disnea + sibilos en auscultación)
    {
        "id": "ASMA_2",
        "si": [
            {"variable": "sibilancias", "operador": "==", "valor": True},
            {"variable": "disnea", "operador": "==", "valor": True},
            {"variable": "sibilos_auscultacion", "operador": "==", "valor": True, "peso": 0.9},
        ],
        "entonces": "Asma",
        "fc": 0.85,
        "recomendaciones": [
            "Espirometría de control",
            "Prueba de óxido nítrico exhalado si está disponible"
        ]
    },

    # === NEUMONÍA ===
    # Tipo: Neumonía adquirida en la comunidad (NAC) — sospecha clínica por fiebre alta, tos productiva y crepitantes
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
        "recomendaciones": [
            "Radiografía de tórax",
            "Oximetría de pulso",
            "Biometría hemática",
            "Iniciar antibiótico según guía local"
        ]
    },
    # Tipo: Neumonía adquirida en la comunidad confirmada por imagen — probable bacteriana (RX + leucocitosis)
    {
        "id": "NEUMONIA_2_RX",
        "si": [
            {"variable": "rx_consolidacion", "operador": "==", "valor": True},
            {"variable": "fiebre_c", "operador": ">=", "valor": 38.0, "peso": 0.8},
            {"variable": "leucocitosis", "operador": "==", "valor": True, "peso": 0.8},
        ],
        "entonces": "Neumonía",
        "fc": 0.95,
        "recomendaciones": [
            "Iniciar antibiótico empírico",
            "Control clínico en 48–72 horas"
        ]
    },

    # === BRONQUITIS AGUDA ===
    # Tipo: Bronquitis aguda postinfecciosa (viral probable) — curso < 3 semanas y sin consolidación
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
        "recomendaciones": [
            "Tratamiento sintomático (descanso e hidratación)",
            "Evitar el uso de antibióticos innecesarios"
        ]
    },
    # Tipo: Bronquitis aguda no complicada — sin fiebre alta ni signos de neumonía
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
        "recomendaciones": [
            "Analgésicos y antipiréticos si hay fiebre",
            "Revalorar si aparecen signos de neumonía"
        ]
    },

    # === EPOC ===
    # Tipo: EPOC por tabaquismo con alta carga (≥1 paquete/día) — síntomas obstructivos
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
        "fc": 0.78,
        "recomendaciones": [
            "Espirometría diagnóstica (FEV1/FVC)",
            "Abandono del tabaquismo",
            "Vacunas contra influenza y neumococo"
        ]
    },
    # Tipo: EPOC por exposición crónica (≥15 años) con carga moderada — síntomas obstructivos
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
        "recomendaciones": [
            "Espirometría diagnóstica (FEV1/FVC)",
            "Abandono del tabaquismo",
            "Vacunas contra influenza y neumococo"
        ]
    },

    # === COVID-19 ===
    # Tipo: COVID-19 con nexo epidemiológico — clínica compatible más contacto reciente
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
        "recomendaciones": [
            "Prueba diagnóstica (antígeno o PCR)",
            "Aislamiento domiciliario",
            "Monitoreo de saturación de oxígeno si hay factores de riesgo"
        ]
    },
    # Tipo: COVID-19 con anosmia predominante — cuadro compatible aun con fiebre baja
    {
        "id": "COVID_2_ANOSMIA",
        "si": [
            {"variable": "anosmia", "operador": "==", "valor": True},
            {"variable": "fiebre_c", "operador": ">=", "valor": 37.5, "peso": 0.6},
            {"variable": "odinofagia", "operador": "==", "valor": True, "peso": 0.6},
        ],
        "entonces": "COVID-19",
        "fc": 0.70,
        "recomendaciones": [
            "Realizar prueba de detección",
            "Aislamiento y vigilancia de síntomas"
        ]
    },

    # === INFLUENZA ===
    # Tipo: Influenza estacional — síndrome febril agudo con mialgias y cefalea en época invernal
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
        "recomendaciones": [
            "Prueba rápida de influenza",
            "Administrar antiviral si cumple criterios",
            "Reposo e hidratación adecuada"
        ]
    },

    # === RESFRIADO COMÚN ===
    # Tipo: Rinofaringitis aguda (resfriado) con rinorrea clara — leve y autolimitada
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
        "fc": 0.85,
        "recomendaciones": [
            "Hidratación y reposo",
            "Lavados nasales con solución salina",
            "Analgésicos/antipiréticos si es necesario"
        ]
    },
    # Tipo: Resfriado con estornudos predominantes — cuadro rinítico leve
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
        "fc": 0.80,
        "recomendaciones": [
            "Medidas sintomáticas",
            "Evitar antibióticos"
        ]
    },
    # Tipo: Resfriado clásico (tríada congestión + rinorrea clara + estornudos), sin fiebre alta ni consolidación
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
        "fc": 0.78,
        "recomendaciones": [
            "Hidratación y reposo",
            "Lavados nasales con solución salina",
            "Analgésicos/antipiréticos si es necesario"
        ]
    },

    # === FARINGITIS ===
    # Tipo: Faringitis viral — tos presente y sin fiebre alta; evitar antibióticos
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
        "fc": 0.55,
        "recomendaciones": [
            "Gárgaras con agua tibia y sal",
            "Analgésicos/antipiréticos",
            "Evitar antibióticos"
        ]
    },
    # Tipo: Faringitis bacteriana (probable estreptocócica; criterios tipo Centor)
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
        "fc": 0.90,
        "recomendaciones": [
            "Prueba rápida de estreptococo o cultivo faríngeo",
            "Antibiótico si la prueba es positiva (según guía local)",
            "Analgésicos/antipiréticos"
        ]
    },
]