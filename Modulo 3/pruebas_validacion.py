# pruebas_validacion.py
# -*- coding: utf-8 -*-
"""
Pruebas de validación del Sistema Experto para diagnóstico de enfermedades respiratorias.

Este archivo permite comprobar que las reglas definidas en la base de conocimiento
funcionan correctamente al aplicarse a distintos casos clínicos simulados.
"""

from base_conocimiento import REGLAS
from motor_inferencia import encadenamiento_adelante

# ============================================================
# CASO DE PRUEBA: NEUMONÍA
# ============================================================

def caso_neumonia():
    """
    Caso clínico representativo de neumonía.
    Paciente con fiebre alta, tos productiva, disnea y crepitantes.
    """
    return dict(
        edad=72, sexo="Femenino", fiebre_c=39.0, tos="Productiva", duracion_tos_dias=5,
        disnea=True, sibilancias=False, dolor_pecho=True, fatiga=True,
        cefalea=False, mialgias=False, odinofagia=False, anosmia=False,
        satO2=90, crepitantes=True, roncus=False, sibilos_auscultacion=False,
        rx_consolidacion=True, pcr_alta=True, leucocitosis=True,
        tabaquismo="Exfumador", exposicion_contaminantes=False, alergias_atopia=False,
        infeccion_respiratoria_reciente=True, contacto_covid=False,
        anos_tabaquismo_pa=15, estacional_invierno=False
    )

# ============================================================
# CASO DE PRUEBA: ASMA
# ============================================================

def caso_asma():
    """
    Caso clínico representativo de asma bronquial.
    Paciente joven con tos seca, disnea y antecedentes de alergia.
    """
    return dict(
        edad=22, sexo="Masculino", fiebre_c=36.9, tos="Seca", duracion_tos_dias=10,
        disnea=True, sibilancias=True, dolor_pecho=False, fatiga=False,
        cefalea=False, mialgias=False, odinofagia=False, anosmia=False,
        satO2=97, crepitantes=False, roncus=True, sibilos_auscultacion=True,
        rx_consolidacion=False, pcr_alta=False, leucocitosis=False,
        tabaquismo="No", exposicion_contaminantes=False, alergias_atopia=True,
        infeccion_respiratoria_reciente=False, contacto_covid=False,
        anos_tabaquismo_pa=0, estacional_invierno=False
    )

# ============================================================
# EJECUCIÓN DE PRUEBAS
# ============================================================

if __name__ == "__main__":
    for nombre, caso in [("Neumonía", caso_neumonia()), ("Asma", caso_asma())]:
        trazas, puntajes, explicaciones, recomendaciones = encadenamiento_adelante(caso, REGLAS)

        print("\n===========================================")
        print(f" Diagnóstico simulado: {nombre}")
        print("===========================================")

        # Mostrar resultados de probabilidad de diagnóstico
        print("\nProbabilidades obtenidas:")
        for k, v in puntajes.items():
            print(f"  - {k}: {v*100:.1f}%")

        # Mostrar explicación de cómo se llegó al diagnóstico
        print("\nExplicaciones generadas:")
        for dx, frases in explicaciones.items():
            print(f"  {dx}: {frases[0] if frases else 'Sin explicación disponible'}")

        # Mostrar recomendaciones médicas asociadas
        if recomendaciones:
            print("\nRecomendaciones sugeridas:")
            for dx, recs in recomendaciones.items():
                print(f"  {dx}: {', '.join(recs)}")

        print("\n-------------------------------------------")
