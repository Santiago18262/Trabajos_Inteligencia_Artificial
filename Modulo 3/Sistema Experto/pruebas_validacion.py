
"""
Pruebas de validación del Sistema Experto para diagnóstico de enfermedades respiratorias.
- Muestra las probabilidades por diagnóstico y el Top para cada caso.
- Incluye casos COMPLETOS, PARCIALES (aproximados) y NEGATIVOS.
"""

from typing import Dict, Any, List, Tuple  # Tipos para anotar funciones (opcional, mejora legibilidad)
from base_conocimiento import REGLAS      # Importa la Base de Conocimiento (lista de reglas)
from motor_inferencia import encadenamiento_adelante  # Importa el motor (encadenamiento hacia adelante)

# ============================================================================
# Helper de impresión
# ============================================================================
# Sección con funciones utilitarias para mostrar resultados de manera uniforme.

def mostrar_resultados(nombre: str, hechos: Dict[str, Any]):
    """
    Ejecuta el encadenamiento hacia adelante con los 'hechos' (caso de prueba),
    imprime los puntajes por diagnóstico, el TOP 1, una explicación y las recomendaciones.
    """
    trazas, puntajes, explicaciones, recomendaciones = encadenamiento_adelante(hechos, REGLAS)  # Ejecuta el motor con los hechos y reglas

    print("\n" + "="*70)         # Imprime una línea separadora superior
    print(f" Caso: {nombre}")    # Muestra el nombre del caso evaluado
    print("="*70)                # Imprime otra línea separadora

    if not puntajes:  # Si no hubo diagnósticos (ninguna regla aportó certeza)
        print("Sin diagnósticos (todas las reglas relevantes quedaron en 0 o no aplican).")  # Mensaje informativo
        return        # Termina la función, no hay nada que mostrar

    # Ordenar y mostrar todos los puntajes (descendente por probabilidad)
    orden = sorted(puntajes.items(), key=lambda kv: kv[1], reverse=True)  # Ordena (dx, score) de mayor a menor
    print("\nProbabilidades obtenidas:")                                   # Título de la sección de probabilidades
    for dx, sc in orden:                                                   # Recorre cada diagnóstico y su score
        print(f"  - {dx}: {sc*100:.1f}%")  # Imprime porcentaje con un decimal

    # Top 1 (diagnóstico con mayor puntaje)
    top_dx, top_sc = orden[0]                            # Toma el primer elemento (el de mayor score)
    print(f"\nTOP: {top_dx} — {top_sc*100:.1f}%")        # Muestra el diagnóstico TOP y su porcentaje

    # (Opcional) Muestra la primera explicación por diagnóstico, si el motor generó alguna
    if explicaciones:                                    # Verifica si hay explicaciones generadas
        print("\nExplicaciones generadas:")             # Encabezado de explicaciones
        for dx, frases in explicaciones.items():        # Recorre diagnóstico → lista de frases
            if frases:                                   # Si hay al menos una frase
                print(f"  {dx}: {frases[0]}")           # Muestra solo la primera explicación para no saturar

    # (Opcional) Muestra recomendaciones por diagnóstico (si existen)
    if recomendaciones:                                  # Verifica si hay recomendaciones
        print("\nRecomendaciones sugeridas:")           # Encabezado de recomendaciones
        for dx, recs in recomendaciones.items():        # Recorre diagnóstico → lista de recomendaciones
            print(f"  {dx}: {', '.join(recs)}")         # Imprime recomendaciones separadas por coma

    print("\n" + "-"*70)  # Línea separadora final del bloque del caso

# ============================================================================
# Casos COMPLETOS (diagnósticos principales)
# ============================================================================

def caso_neumonia_1():
    """Neumonía clínica típica (fiebre alta, tos productiva, disnea, crepitantes)."""
    return dict(
        edad=72, sexo="Femenino", fiebre_c=39.0, tos="Productiva", duracion_tos_dias=5,
        disnea=True, sibilancias=False, dolor_pecho=True, fatiga=True,
        cefalea=False, mialgias=False, odinofagia=False, anosmia=False,
        satO2=90, crepitantes=True, roncus=False, sibilos_auscultacion=False,
        rx_consolidacion=False, pcr_alta=True, leucocitosis=True,
        tabaquismo="Exfumador", paquetes_por_dia=0.5, anios_fumando=10,
        exposicion_contaminantes=False, alergias_atopia=False,
        infeccion_respiratoria_reciente=True, contacto_covid=False,
        estacional_invierno=False
    )

def caso_neumonia_2_rx():
    """Neumonía respaldada por imagen y laboratorios (consolidación + leucocitosis)."""
    return dict(
        edad=65, sexo="Masculino",
        fiebre_c=38.2, tos="Seca", duracion_tos_dias=2,
        disnea=False, sibilancias=False, dolor_pecho=False, fatiga=True,
        cefalea=False, mialgias=False, odinofagia=False, anosmia=False,
        satO2=95, crepitantes=False, roncus=False, sibilos_auscultacion=False,
        rx_consolidacion=True, pcr_alta=True, leucocitosis=True,
        tabaquismo="No", paquetes_por_dia=0.0, anios_fumando=0,
        exposicion_contaminantes=False, alergias_atopia=False,
        infeccion_respiratoria_reciente=False, contacto_covid=False,
        estacional_invierno=False
    )

def caso_asma_1():
    """Asma atópica (sibilancias + tos seca + alergias)."""
    return dict(
        edad=22, sexo="Masculino", fiebre_c=36.9, tos="Seca", duracion_tos_dias=10,
        disnea=False, sibilancias=True, dolor_pecho=False, fatiga=False,
        cefalea=False, mialgias=False, odinofagia=False, anosmia=False,
        satO2=97, crepitantes=False, roncus=False, sibilos_auscultacion=False,
        rx_consolidacion=False, pcr_alta=False, leucocitosis=False,
        tabaquismo="No", paquetes_por_dia=0.0, anios_fumando=0,
        exposicion_contaminantes=False, alergias_atopia=True,
        infeccion_respiratoria_reciente=False, contacto_covid=False,
        estacional_invierno=False
    )

def caso_asma_2():
    """Asma por esfuerzo (disnea + sibilancias + sibilos en auscultación)."""
    return dict(
        edad=28, sexo="Femenino",
        fiebre_c=36.7, tos="Seca", duracion_tos_dias=3,
        disnea=True, sibilancias=True, dolor_pecho=False, fatiga=False,
        cefalea=False, mialgias=False, odinofagia=False, anosmia=False,
        satO2=98, crepitantes=False, roncus=False, sibilos_auscultacion=True,
        rx_consolidacion=False, pcr_alta=False, leucocitosis=False,
        tabaquismo="No", paquetes_por_dia=0.0, anios_fumando=0,
        exposicion_contaminantes=True, alergias_atopia=False,
        infeccion_respiratoria_reciente=False, contacto_covid=False,
        estacional_invierno=False
    )

def caso_epoc_1():
    """EPOC por tabaquismo intenso (disnea + sibilancias)."""
    return dict(
        edad=65, sexo="Masculino",
        fiebre_c=36.8, tos="Seca", duracion_tos_dias=60,
        disnea=True, sibilancias=True, dolor_pecho=False, fatiga=True,
        cefalea=False, mialgias=False, odinofagia=False, anosmia=False,
        satO2=93, crepitantes=False, roncus=True, sibilos_auscultacion=True,
        rx_consolidacion=False, pcr_alta=False, leucocitosis=False,
        tabaquismo="Actual", paquetes_por_dia=1.2, anios_fumando=30,
        exposicion_contaminantes=True, alergias_atopia=False,
        infeccion_respiratoria_reciente=False, contacto_covid=False,
        estacional_invierno=False
    )

def caso_epoc_2():
    """EPOC moderado (evita activar asma clínica; sibilos de auscultación en False)."""
    return dict(
        edad=58, sexo="Masculino", fiebre_c=36.9, tos="Productiva", duracion_tos_dias=40,
        disnea=True, sibilancias=True, dolor_pecho=False, fatiga=True,
        cefalea=False, mialgias=False, odinofagia=False, anosmia=False,
        satO2=94, crepitantes=False, roncus=True,
        sibilos_auscultacion=False,  # clave para no activar ASMA_2
        rx_consolidacion=False, pcr_alta=False, leucocitosis=False,
        tabaquismo="Exfumador", paquetes_por_dia=0.6, anios_fumando=20,
        exposicion_contaminantes=True, alergias_atopia=False,
        infeccion_respiratoria_reciente=False, contacto_covid=False,
        estacional_invierno=False
    )

def caso_covid_1():
    """COVID-19 con nexo epidemiológico (fiebre + tos + fatiga + contacto)."""
    return dict(
        edad=35, sexo="Femenino",
        fiebre_c=38.0, tos="Seca", duracion_tos_dias=3,
        disnea=False, sibilancias=False, dolor_pecho=False, fatiga=True,
        cefalea=True, mialgias=True, odinofagia=False, anosmia=False,
        satO2=97, crepitantes=False, roncus=False, sibilos_auscultacion=False,
        rx_consolidacion=False, pcr_alta=False, leucocitosis=False,
        contacto_covid=True,
        tabaquismo="No", paquetes_por_dia=0.0, anios_fumando=0,
        exposicion_contaminantes=False, alergias_atopia=False,
        infeccion_respiratoria_reciente=True,
        estacional_invierno=False
    )

def caso_covid_2_anosmia():
    """COVID-19 con anosmia predominante (fiebre leve + odinofagia)."""
    return dict(
        edad=26, sexo="Masculino",
        fiebre_c=37.6, tos="No", duracion_tos_dias=0,
        disnea=False, sibilancias=False, dolor_pecho=False, fatiga=False,
        cefalea=False, mialgias=False, odinofagia=True, anosmia=True,
        satO2=98, crepitantes=False, roncus=False, sibilos_auscultacion=False,
        rx_consolidacion=False, pcr_alta=False, leucocitosis=False,
        contacto_covid=False,
        tabaquismo="No", paquetes_por_dia=0.0, anios_fumando=0,
        exposicion_contaminantes=False, alergias_atopia=False,
        infeccion_respiratoria_reciente=False,
        estacional_invierno=False
    )

def caso_influenza_1():
    """Influenza estacional (fiebre alta + mialgias + cefalea + invierno)."""
    return dict(
        edad=30, sexo="Femenino",
        fiebre_c=38.5, tos="Seca", duracion_tos_dias=2,
        disnea=False, sibilancias=False, dolor_pecho=False, fatiga=True,
        cefalea=True, mialgias=True, odinofagia=False, anosmia=False,
        satO2=98, crepitantes=False, roncus=False, sibilos_auscultacion=False,
        rx_consolidacion=False, pcr_alta=False, leucocitosis=False,
        contacto_covid=False,
        tabaquismo="No", paquetes_por_dia=0.0, anios_fumando=0,
        exposicion_contaminantes=False, alergias_atopia=False,
        infeccion_respiratoria_reciente=False,
        estacional_invierno=True
    )

def caso_resfriado_1():
    """Resfriado nasal típico (rinorrea clara + congestión + fiebre baja)."""
    return dict(
        edad=18, sexo="Masculino",
        fiebre_c=37.2, tos="Seca", duracion_tos_dias=1,
        disnea=False, sibilancias=False, dolor_pecho=False, fatiga=False,
        cefalea=False, mialgias=False, odinofagia=True, anosmia=False,
        satO2=99, crepitantes=False, roncus=False, sibilos_auscultacion=False,
        rx_consolidacion=False, pcr_alta=False, leucocitosis=False,
        rinorrea="Clara", congestion_nasal=True, estornudos=True,
        contacto_covid=False,
        tabaquismo="No", paquetes_por_dia=0.0, anios_fumando=0,
        exposicion_contaminantes=False, alergias_atopia=True,
        infeccion_respiratoria_reciente=False,
        estacional_invierno=False
    )

def caso_resfriado_2():
    """Resfriado leve sin tos (valida una variante de regla de resfriado)."""
    return dict(
        edad=22, sexo="Femenino",
        fiebre_c=37.0, tos="No", duracion_tos_dias=0,
        disnea=False, sibilancias=False, dolor_pecho=False, fatiga=False,
        cefalea=False, mialgias=False, odinofagia=False, anosmia=False,
        satO2=99, crepitantes=False, roncus=False, sibilos_auscultacion=False,
        rx_consolidacion=False, pcr_alta=False, leucocitosis=False,
        rinorrea="Clara", congestion_nasal=True, estornudos=True,
        contacto_covid=False,
        tabaquismo="No", paquetes_por_dia=0.0, anios_fumando=0,
        exposicion_contaminantes=False, alergias_atopia=True,
        infeccion_respiratoria_reciente=False,
        estacional_invierno=False
    )

def caso_resfriado_3():
    """Resfriado clásico (congestión + rinorrea clara + estornudos)."""
    return dict(
        edad=25, sexo="Masculino",
        fiebre_c=37.4, tos="Seca", duracion_tos_dias=2,
        disnea=False, sibilancias=False, dolor_pecho=False, fatiga=False,
        cefalea=False, mialgias=False, odinofagia=False, anosmia=False,
        satO2=99, crepitantes=False, roncus=False, sibilos_auscultacion=False,
        rx_consolidacion=False, pcr_alta=False, leucocitosis=False,
        rinorrea="Clara", congestion_nasal=True, estornudos=True,
        contacto_covid=False,
        tabaquismo="No", paquetes_por_dia=0.0, anios_fumando=0,
        exposicion_contaminantes=False, alergias_atopia=True,
        infeccion_respiratoria_reciente=False,
        estacional_invierno=False
    )

def caso_faringitis_viral():
    """Faringitis viral (sin tos para no activar bronquitis; rinorrea purulenta)."""
    return dict(
        edad=19, sexo="Femenino",
        fiebre_c=37.6, tos="No", duracion_tos_dias=2,
        disnea=False, sibilancias=False, dolor_pecho=False, fatiga=False,
        cefalea=False, mialgias=False, odinofagia=True, anosmia=False,
        satO2=99, crepitantes=False, roncus=False, sibilos_auscultacion=False,
        rx_consolidacion=False, pcr_alta=False, leucocitosis=False,
        rinorrea="Purulenta", congestion_nasal=False,
        contacto_covid=False,
        tabaquismo="No", paquetes_por_dia=0.0, anios_fumando=0,
        exposicion_contaminantes=False, alergias_atopia=False,
        infeccion_respiratoria_reciente=False,
        estacional_invierno=False
    )

def caso_faringitis_bacteriana():
    """Faringitis estreptocócica (Centor alto: odinofagia + exudado + adenopatías + fiebre, sin tos)."""
    return dict(
        edad=21, sexo="Masculino",
        fiebre_c=38.2, tos="No", duracion_tos_dias=1,
        disnea=False, sibilancias=False, dolor_pecho=False, fatiga=False,
        cefalea=False, mialgias=False, odinofagia=True, anosmia=False,
        satO2=99, crepitantes=False, roncus=False, sibilos_auscultacion=False,
        rx_consolidacion=False, pcr_alta=False, leucocitosis=False,
        exudado_amigdalino=True, adenopatias_cervicales=True,
        rinorrea="No", congestion_nasal=False,
        contacto_covid=False,
        tabaquismo="No", paquetes_por_dia=0.0, anios_fumando=0,
        exposicion_contaminantes=False, alergias_atopia=False,
        infeccion_respiratoria_reciente=False,
        estacional_invierno=False
    )

def caso_bronquitis_1():
    """Bronquitis aguda pos-IR, subaguda, sin consolidación (variante 1)."""
    return dict(
        edad=35, sexo="Masculino", fiebre_c=37.5,
        tos="Productiva", duracion_tos_dias=10,
        infeccion_respiratoria_reciente=True,
        rx_consolidacion=False,
        congestion_nasal=False, rinorrea="Purulenta",
        disnea=False, crepitantes=False
    )

def caso_bronquitis_2():
    """Bronquitis aguda leve: tos + fiebre baja + sin crepitantes (variante 2)."""
    return dict(
        edad=29, sexo="Femenino",
        fiebre_c=37.8, tos="Seca", duracion_tos_dias=5,
        crepitantes=False, rx_consolidacion=False,
        congestion_nasal=False
    )

# ============================================================================
# Casos PARCIALES (no se cumplen todas las condiciones; ahora dan aproximado)
# ============================================================================

def caso_neumonia_parcial():
    """NEUMONÍA_1 PARCIAL: falta 'crepitantes=True' → la regla aporta parcialmente."""
    return dict(
        edad=70, sexo="Femenino",
        fiebre_c=39.0, tos="Productiva", duracion_tos_dias=5,
        disnea=True, crepitantes=False,   # falta crepitantes
        sibilancias=False, dolor_pecho=True, fatiga=True,
        rx_consolidacion=False, leucocitosis=False, pcr_alta=False,
        roncus=False, sibilos_auscultacion=False,
        satO2=92, contacto_covid=False, infeccion_respiratoria_reciente=False
    )

def caso_asma_parcial():
    """ASMA_1 PARCIAL: falta 'alergias_atopia=True'."""
    return dict(
        edad=25, sexo="Masculino",
        tos="Seca", sibilancias=True, alergias_atopia=False,  # falta alergia
        disnea=False, sibilos_auscultacion=False, rx_consolidacion=False
    )

def caso_bronquitis_1_parcial_con_bronquitis_2_activa():
    """BRONQUITIS_1 PARCIAL (sin IR reciente), pero BRONQUITIS_2 sí aporta por fiebre baja + tos."""
    return dict(
        edad=33, sexo="Masculino",
        tos="Productiva", duracion_tos_dias=10,
        infeccion_respiratoria_reciente=False,   # falta para BRONQUITIS_1
        rx_consolidacion=False, crepitantes=False,
        fiebre_c=37.6, congestion_nasal=False    # activa BRONQUITIS_2
    )

def caso_covid_1_parcial_con_covid_2_activa():
    """COVID_1 PARCIAL (sin contacto), pero COVID_2 activa (anosmia + odinofagia)."""
    return dict(
        edad=29, sexo="Femenino",
        fiebre_c=37.6, tos="No", fatiga=False,
        contacto_covid=False,     # falta para COVID_1
        anosmia=True, odinofagia=True,            # activa COVID_2
        rx_consolidacion=False, leucocitosis=False, pcr_alta=False
    )

def caso_faringitis_bacteriana_parcial_con_viral_activa():
    """Faringitis bacteriana parcial (hay tos → rompe Centor), pero viral activa por patrón clínico."""
    return dict(
        edad=20, sexo="Femenino",
        fiebre_c=37.5, odinofagia=True, tos="Seca",   # rompe la bacteriana
        congestion_nasal=False, rinorrea="Purulenta", # activa la viral
        rx_consolidacion=False, leucocitosis=False
    )

# ============================================================================
# PRUEBAS NEGATIVAS — No deben arrojar diagnósticos
# ============================================================================

def caso_negativo_vacio():
    """Sin hechos: agregado=0 → sin diagnósticos."""
    return dict()

def caso_negativo_demografia_sola():
    """Solo demografía: ninguna regla se activa por edad/sexo únicamente."""
    return dict(
        edad=35,
        sexo="Masculino"
    )

def caso_negativo_categorias_fuera_de_opciones():
    """Categóricos fuera del catálogo; se evita activar reglas por mapeo exacto."""
    return dict(
        tos="Indefinida",
        rinorrea="Ninguna",
        tabaquismo="Desconocido",
        congestion_nasal=None,
        disnea=None, sibilancias=None
    )

def caso_negativo_minimos_inofensivos():
    """Valores inofensivos que no activan reglas (fiebre baja/ausente, sin RX/labs)."""
    return dict(
        tos="No",
        disnea=False,
        sibilancias=False,
        crepitantes=False,
        sibilos_auscultacion=False,
        alergias_atopia=False,
        contacto_covid=False,
        estacional_invierno=False
    )

def caso_negativo_labs_sueltos_inconclusos():
    """Labs sueltos no suficientes para activar neumonía con RX."""
    return dict(
        pcr_alta=True,
        leucocitosis=False,
        tos="No",
        disnea=False,
        sibilancias=False,
        congestion_nasal=False
    )

# ============================================================================
# Listas de pruebas a correr
# ============================================================================

PRUEBAS_COMPLETAS = [  # Casos que deberían activar con claridad diagnósticos principales
    ("Neumonía (clínica)", caso_neumonia_1),
    ("Neumonía (RX+labs)", caso_neumonia_2_rx),
    ("Asma_1", caso_asma_1),
    ("Asma_2", caso_asma_2),
    ("EPOC_1", caso_epoc_1),
    ("EPOC_2", caso_epoc_2),
    ("COVID_1", caso_covid_1),
    ("COVID_2_ANOSMIA", caso_covid_2_anosmia),
    ("Influenza_1", caso_influenza_1),
    ("Resfriado_1", caso_resfriado_1),
    ("Resfriado_2", caso_resfriado_2),
    ("Resfriado_3", caso_resfriado_3),
    ("Faringitis (viral)", caso_faringitis_viral),
    ("Faringitis (bacteriana)", caso_faringitis_bacteriana),
    ("Bronquitis_1", caso_bronquitis_1),
    ("Bronquitis_2", caso_bronquitis_2),
]

PRUEBAS_PARCIALES = [  # Casos incompletos: deberían dar aportes parciales/aproximados
    ("NEUMONÍA_1 parcial (sin crepitantes)", caso_neumonia_parcial),
    ("ASMA parcial (sin alergia ni esfuerzo)", caso_asma_parcial),
    ("BRONQUITIS_1 parcial, pero BRONQUITIS_2 activa", caso_bronquitis_1_parcial_con_bronquitis_2_activa),
    ("COVID_1 parcial, pero COVID_2 activa", caso_covid_1_parcial_con_covid_2_activa),
    ("Faringitis bacteriana parcial, viral activa", caso_faringitis_bacteriana_parcial_con_viral_activa),
]

PRUEBAS_NEGATIVAS = [  # Casos que no deberían clasificar en ningún diagnóstico
    ("NEGATIVO: vacío", caso_negativo_vacio),
    ("NEGATIVO: demografía sola", caso_negativo_demografia_sola),
    ("NEGATIVO: categorías fuera de opciones", caso_negativo_categorias_fuera_de_opciones),
    ("NEGATIVO: mínimos inofensivos", caso_negativo_minimos_inofensivos),
    ("NEGATIVO: labs sueltos inconclusos", caso_negativo_labs_sueltos_inconclusos),
]

# ============================================================================
# Ejecución
# ============================================================================

if __name__ == "__main__":  # Punto de entrada cuando se ejecuta el archivo directamente
    print("\n" + "#"*70)
    print("# PRUEBAS COMPLETAS")
    print("#"*70)
    for nombre, fabrica in PRUEBAS_COMPLETAS:  # Recorre los casos “completos”
        mostrar_resultados(nombre, fabrica())  # Genera hechos y muestra resultados

    print("\n" + "#"*70)
    print("# PRUEBAS PARCIALES (no se cumplen todas las condiciones; se muestra aproximado)")
    print("#"*70)
    for nombre, fabrica in PRUEBAS_PARCIALES:  # Recorre los casos “parciales”
        mostrar_resultados(nombre, fabrica())

    print("\n" + "#"*70)
    print("# PRUEBAS NEGATIVAS (no deben arrojar diagnósticos)")
    print("#"*70)
    for nombre, fabrica in PRUEBAS_NEGATIVAS:  # Recorre los casos “negativos”
        mostrar_resultados(nombre, fabrica())
