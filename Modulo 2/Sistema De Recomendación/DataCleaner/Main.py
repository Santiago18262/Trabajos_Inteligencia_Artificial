
# ------------------------------------------------------------
# Importaciones
# ------------------------------------------------------------
import pandas as pd  # (Opcional) Librería útil si más adelante se agregan validaciones o análisis
from Constructor import ModelBuilder  # Importa la clase principal que construye el modelo de recomendación

# ------------------------------------------------------------
# Función principal del script
# ------------------------------------------------------------
def main():
    """
    Función principal del programa.
    Se encarga de crear una instancia de la clase ModelBuilder y
    ejecutar el proceso completo de construcción y guardado de los modelos (.pkl).
    """
    # Crea una instancia del constructor del modelo
    builder = ModelBuilder()

    # Llama al método que ejecuta todo el pipeline:
    #  - Carga de datos
    #  - Limpieza y preprocesamiento
    #  - Vectorización
    #  - Cálculo de similitud
    #  - Guardado de archivos
    builder.build_and_save()

# ------------------------------------------------------------
# Punto de entrada del script
# ------------------------------------------------------------
# Esta condición asegura que el código dentro se ejecute solo cuando
# este archivo se ejecute directamente (no cuando se importe desde otro módulo).
if __name__ == "__main__":
    main()  # Ejecuta la función principal
