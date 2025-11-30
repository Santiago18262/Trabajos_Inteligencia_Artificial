import os  # Librería para navegar por carpetas y archivos del sistema
import numpy as np  # Librería matemática para manejar arrays y cargar archivos .npy
import keras # O import tensorflow.keras as keras

# Ruta del dataset de entrenamiento (usamos r'' para evitar errores con los backslash)
directorio = r'C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\datasets\dataset(AffectNet)\train'

# Tupla con los formatos de imagen que vamos a aceptar y contar
extensiones_imagenes = ('.jpg', '.jpeg', '.png', '.bmp')

# Diccionario vacío para ir guardando "Emoción": cantidad
conteo_emociones = {}

# Itera sobre cada carpeta (que representa una emoción) en el directorio principal
for carpeta in os.listdir(directorio):
    ruta_carpeta = os.path.join(directorio, carpeta)  # Crea la ruta completa uniendo directorio + nombre carpeta
    
    # Verifica si lo encontrado es realmente una carpeta y no un archivo suelto
    if os.path.isdir(ruta_carpeta):
        conteo_emociones[carpeta] = 0  # Inicializa el contador de esta emoción en 0
        
        # Itera sobre cada archivo dentro de la carpeta de la emoción actual
        for archivo in os.listdir(ruta_carpeta):
            if archivo.lower().endswith(extensiones_imagenes):  # Verifica si el archivo es una imagen válida
                conteo_emociones[carpeta] += 1  # Si es imagen, suma 1 al contador

# Itera sobre el diccionario final para mostrar los resultados
for emocion, cantidad in conteo_emociones.items():
    print(f'Número de imágenes para la emoción {emocion}: {cantidad}')  # Imprime el total por clase


# ---------------------------------------------------------
#  Verificación de etiquetas de emociones
# ---------------------------------------------------------

# Carga el archivo que contiene los nombres de las clases guardadas
label_names = np.load(r'C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\modelos\label_names.npy')

print("\nLabel names:", label_names)  # Muestra en consola la lista de etiquetas cargadas

# ---------------------------------------------------------
#  Verificación de modelo
# ---------------------------------------------------------

# 1. Cargar el modelo
modelo = keras.saving.load_model(r'C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\modelos\modelo_emociones_resnet50.keras')

# 2. Ver la arquitectura en texto (capas y número de parámetros)
modelo.summary()

# Ver los pesos de todas las capas
for capa in modelo.layers:
    pesos = capa.get_weights()
    print(f"Capa: {capa.name}")
    print(pesos) # Esto imprimirá arrays de numpy con los números