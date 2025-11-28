import os

# Define el directorio principal donde están las carpetas de emociones
directorio = r'C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\dataset2\train'  # Cambia esto por el path de tu dataset

# Define las extensiones de las imágenes que deseas contar
extensiones_imagenes = ('.jpg', '.jpeg', '.png', '.bmp')

# Inicializa un diccionario para almacenar el conteo de imágenes por emoción
conteo_emociones = {}

# Recorre las subcarpetas (emociones)
for carpeta in os.listdir(directorio):
    ruta_carpeta = os.path.join(directorio, carpeta)
    
    # Asegúrate de que es una carpeta
    if os.path.isdir(ruta_carpeta):
        # Inicializa el contador para esa emoción
        conteo_emociones[carpeta] = 0
        
        # Recorre las imágenes dentro de esa carpeta
        for archivo in os.listdir(ruta_carpeta):
            if archivo.lower().endswith(extensiones_imagenes):
                conteo_emociones[carpeta] += 1

# Muestra el conteo de imágenes por emoción
for emocion, cantidad in conteo_emociones.items():
    print(f'Número de imágenes para la emoción {emocion}: {cantidad}')


import numpy as np
labels = np.load("label_names.npy")
print(labels)
