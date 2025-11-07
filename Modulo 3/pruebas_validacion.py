# pruebas_validacion.py
# -*- coding: utf-8 -*-
"""
Pruebas de validación del Sistema Experto para diagnóstico de enfermedades respiratorias.
Muestra las probabilidades por diagnóstico y el Top para cada caso.
Incluye casos completos y casos PARCIALES (no se cumplen todas las condiciones).
"""

from typing import Dict, Any, List, Tuple
from base_conocimiento import REGLAS
from motor_inferencia import encadenamiento_adelante

# ============================================================================
# Helpers de impresión
# ============================================================================

def mostrar_resultados(nombre: str, hechos: Dict[str, Any]):
    trazas, puntajes, explicaciones, recomendaciones = encadenamiento_adelante(hechos, REGLAS)

    print("\n" + "="*60)
    print(f" Caso: {nombre}")
    print("="*60)

    if not puntajes:
        print("Sin diagnósticos (todas las reglas relevantes quedaron en 0 o no aplican).")
        return

    # Ordenar y mostrar todos los puntajes
    orden = sorted(puntajes.items(), key=lambda kv: kv[1], reverse=True)
    print("\nProbabilidades obtenidas:")
    for dx, sc in orden:
        print(f"  - {dx}: {sc*100:.1f}%")

    # Top 1
    top_dx, top_sc = orden[0]
    print(f"\nTOP: {top_dx} — {top_sc*100:.1f}%")

    # (Opcional) Primera explicación por diagnóstico, si existe
    if explicaciones:
        print("\nExplicaciones generadas:")
        for dx, frases in explicaciones.items():
            if frases:
                print(f"  {dx}: {frases[0]}")

    # (Opcional) Recomendaciones
    if recomendaciones:
        print("\nRecomendaciones sugeridas:")
        for dx, recs in recomendaciones.items():
            print(f"  {dx}: {', '.join(recs)}")

    print("\n" + "-"*60)

# ============================================================================
# Casos COMPLETOS (diagnósticos principales)
# ============================================================================

def caso_neumonia_1():
    """Neumonía clínica típica."""
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
    """Neumonía por imagen + labs (evitando disparar neumonía clínica completa)."""
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
    """Asma (tos seca + alergia + sibilancias)."""
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
    """EPOC típico, fumador intenso con disnea + sibilancias."""
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
    """EPOC moderado (evita activar ASMA_2 apagando sibilos en auscultación)."""
    return dict(
        edad=58, sexo="Masculino", fiebre_c=36.9, tos="Productiva", duracion_tos_dias=40,
        disnea=True, sibilancias=True, dolor_pecho=False, fatiga=True,
        cefalea=False, mialgias=False, odinofagia=False, anosmia=False,
        satO2=94, crepitantes=False, roncus=True,
        sibilos_auscultacion=False,  # clave
        rx_consolidacion=False, pcr_alta=False, leucocitosis=False,
        tabaquismo="Exfumador", paquetes_por_dia=0.6, anios_fumando=20,
        exposicion_contaminantes=True, alergias_atopia=False,
        infeccion_respiratoria_reciente=False, contacto_covid=False,
        estacional_invierno=False
    )

def caso_covid_1():
    """COVID-19 (fiebre + tos + fatiga + contacto)."""
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
    """COVID-19 olfativo (anosmia + fiebre leve + odinofagia)."""
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
    """Influenza (fiebre alta + mialgias + cefalea + invierno)."""
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
    """Resfriado leve con tos ausente (validando otra regla)."""
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
    """Resfriado nasal claro (tercera variante de reglas)."""
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
    """Faringitis viral (sin tos para no activar bronquitis)."""
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
    """Faringitis estreptocócica (Centor alto)."""
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
    """Bronquitis aguda pos-IR, subaguda, sin consolidación."""
    return dict(
        edad=35, sexo="Masculino", fiebre_c=37.5,
        tos="Productiva", duracion_tos_dias=10,
        infeccion_respiratoria_reciente=True,
        rx_consolidacion=False,
        congestion_nasal=False, rinorrea="Purulenta",
        disnea=False, crepitantes=False
    )

def caso_bronquitis_2():
    """Bronquitis aguda leve: tos + fiebre baja + sin crepitantes."""
    return dict(
        edad=29, sexo="Femenino",
        fiebre_c=37.8, tos="Seca", duracion_tos_dias=5,
        crepitantes=False, rx_consolidacion=False,
        congestion_nasal=False
    )

# ============================================================================
# Casos PARCIALES (no se cumplen todas las condiciones)
# ============================================================================

def caso_neumonia_parcial():
    """
    NEUMONÍA_1 PARCIAL: falta 'crepitantes=True' → esa regla aporta 0.
    También evitamos NEUMONÍA_2_RX (sin consolidación ni leucocitosis).
    """
    return dict(
        edad=70, sexo="Femenino",
        fiebre_c=39.0, tos="Productiva", duracion_tos_dias=5,
        disnea=True, crepitantes=False,   # <-- falta crepitantes
        sibilancias=False, dolor_pecho=True, fatiga=True,
        rx_consolidacion=False, leucocitosis=False, pcr_alta=False,
        roncus=False, sibilos_auscultacion=False,
        satO2=92, contacto_covid=False, infeccion_respiratoria_reciente=False
    )

def caso_asma_parcial():
    """
    ASMA_1 PARCIAL: falta 'alergias_atopia=True' → ASMA_1=0.
    Evitamos ASMA_2: sin disnea ni sibilos en auscultación.
    """
    return dict(
        edad=25, sexo="Masculino",
        tos="Seca", sibilancias=True, alergias_atopia=False,  # <-- falta alergia
        disnea=False, sibilos_auscultacion=False, rx_consolidacion=False
    )

def caso_bronquitis_1_parcial_con_bronquitis_2_activa():
    """
    BRONQUITIS_1 PARCIAL: falta 'infeccion_respiratoria_reciente=True' → BRONQUITIS_1=0.
    PERO se cumplen condiciones de BRONQUITIS_2 → hay aporte por la otra regla.
    """
    return dict(
        edad=33, sexo="Masculino",
        tos="Productiva", duracion_tos_dias=10,
        infeccion_respiratoria_reciente=False,   # <-- falta para BRONQUITIS_1
        rx_consolidacion=False, crepitantes=False,
        fiebre_c=37.6, congestion_nasal=False    # activa BRONQUITIS_2
    )

def caso_covid_1_parcial_con_covid_2_activa():
    """
    COVID_1 PARCIAL: 'contacto_covid=False' → COVID_1=0.
    PERO activamos COVID_2 (anosmia + fiebre leve + odinofagia).
    """
    return dict(
        edad=29, sexo="Femenino",
        fiebre_c=37.6, tos="No", fatiga=False,
        contacto_covid=False,     # <-- falta para COVID_1
        anosmia=True, odinofagia=True,            # activa COVID_2
        rx_consolidacion=False, leucocitosis=False, pcr_alta=False
    )

def caso_faringitis_bacteriana_parcial_con_viral_activa():
    """
    FARINGITIS BACTERIANA PARCIAL: 'tos' debe ser 'No'; aquí 'Seca' → regla=0.
    PERO activamos FARINGITIS VIRAL (odinofagia, fiebre <38, patrón nasal no claro).
    """
    return dict(
        edad=20, sexo="Femenino",
        fiebre_c=37.5, odinofagia=True, tos="Seca",   # <-- rompe la bacteriana
        congestion_nasal=False, rinorrea="Purulenta", # activa la viral
        rx_consolidacion=False, leucocitosis=False
    )

# ============================================================================
# Listas de pruebas a correr
# ============================================================================

PRUEBAS_COMPLETAS = [
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

PRUEBAS_PARCIALES = [
    ("NEUMONÍA_1 parcial (sin crepitantes)", caso_neumonia_parcial),
    ("ASMA parcial (sin alergia ni esfuerzo)", caso_asma_parcial),
    ("BRONQUITIS_1 parcial, pero BRONQUITIS_2 activa", caso_bronquitis_1_parcial_con_bronquitis_2_activa),
    ("COVID_1 parcial, pero COVID_2 activa", caso_covid_1_parcial_con_covid_2_activa),
    ("Faringitis bacteriana parcial, viral activa", caso_faringitis_bacteriana_parcial_con_viral_activa),
]

# ============================================================================
# Ejecución
# ============================================================================

if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# PRUEBAS COMPLETAS")
    print("#"*60)
    for nombre, fabrica in PRUEBAS_COMPLETAS:
        mostrar_resultados(nombre, fabrica())

    print("\n" + "#"*60)
    print("# PRUEBAS PARCIALES (no se cumplen todas las condiciones)")
    print("#"*60)
    for nombre, fabrica in PRUEBAS_PARCIALES:
        mostrar_resultados(nombre, fabrica())
