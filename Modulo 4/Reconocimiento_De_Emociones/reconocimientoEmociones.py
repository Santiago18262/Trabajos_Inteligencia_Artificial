import cv2      # Visión por computadora
import os       # Manejo de rutas
from pathlib import Path
import numpy as np

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.vgg16 import preprocess_input


# ----------------------------------------------------------------------
# FUNCIÓN PARA CARGAR EMOJI SEGÚN LA EMOCIÓN
# ----------------------------------------------------------------------
def cargar_emoji(nombre_emocion):
    """
    Carga la imagen del emoji correspondiente desde la carpeta 'Emojis'
    ubicada junto al script.
    """
    directorio_base = Path(__file__).parent
    directorio_emojis = directorio_base / 'Emojis'

    if not directorio_emojis.exists():
        return None

    extensiones = ['.jpeg', '.jpg', '.png', '.bmp']
    nombre_archivo = nombre_emocion.lower()

    # Buscar archivo con el mismo nombre (sin importar la extensión)
    for archivo in directorio_emojis.iterdir():
        if archivo.is_file() and archivo.stem.lower() == nombre_archivo:
            imagen = cv2.imread(str(archivo))
            if imagen is not None:
                return imagen

    # Intentar buscar con extensiones comunes
    for ext in extensiones:
        candidato = directorio_emojis / f"{nombre_archivo}{ext}"
        if candidato.exists():
            imagen = cv2.imread(str(candidato))
            if imagen is not None:
                return imagen

    return None


# ----------------------------------------------------------------------
# PREPROCESAMIENTO PARA LA CNN (VGG16)
# ----------------------------------------------------------------------
def preprocesar_rostro(rostro_bgr, tamano=224):
    """
    Prepara el rostro para la CNN:
    - Redimensiona
    - Convierte a RGB
    - Normaliza con preprocess_input de VGG16
    - Agrega dimensión batch
    """
    rostro_redimensionado = cv2.resize(rostro_bgr, (tamano, tamano), interpolation=cv2.INTER_CUBIC)
    rostro_rgb = cv2.cvtColor(rostro_redimensionado, cv2.COLOR_BGR2RGB)
    rostro_rgb = np.array(rostro_rgb, dtype="float32")
    rostro_rgb = np.expand_dims(rostro_rgb, axis=0)
    rostro_rgb = preprocess_input(rostro_rgb)
    return rostro_rgb


# ----------------------------------------------------------------------
# CARGAR MODELO Y NOMBRES DE CLASES
# ----------------------------------------------------------------------
modelo = load_model("modelo_emociones_vgg16.h5")
nombres_clases = np.load("label_names.npy").tolist()

print("Emociones detectables:", nombres_clases)

TAMANO_IMAGEN = 224


# ----------------------------------------------------------------------
# INICIAR CÁMARA Y CLASIFICADOR DE ROSTROS
# ----------------------------------------------------------------------
camara = cv2.VideoCapture(0, cv2.CAP_DSHOW)

clasificador_rostros = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)


# ----------------------------------------------------------------------
# BUCLE PRINCIPAL
# ----------------------------------------------------------------------
while True:
    leido, fotograma = camara.read()
    if not leido:
        break

    fotograma_gris = cv2.cvtColor(fotograma, cv2.COLOR_BGR2GRAY)
    fotograma_aux = fotograma.copy()

    # Panel a la derecha donde se colocará el emoji
    panel_vacio = np.zeros((fotograma.shape[0], 300, 3), dtype=np.uint8)
    fotograma_completo = cv2.hconcat([fotograma, panel_vacio])

    rostros = clasificador_rostros.detectMultiScale(fotograma_gris, 1.3, 5)

    for (x, y, w, h) in rostros:
        rostro_color = fotograma_aux[y:y+h, x:x+w]

        # Preprocesar para la CNN
        rostro_procesado = preprocesar_rostro(rostro_color, TAMANO_IMAGEN)

        # Predicción
        predicciones = modelo.predict(rostro_procesado, verbose=0)
        indice = np.argmax(predicciones)
        emocion = nombres_clases[indice]
        probabilidad = predicciones[0][indice]

        # ------- DEPURACIÓN EN CONSOLA -------
        print("Probabilidades:", predicciones[0])
        for i, nombre in enumerate(nombres_clases):
            print(f"{nombre}: {predicciones[0][i]*100:.2f}%")
        print(f"Predicción final: {emocion} ({probabilidad*100:.2f}%)")
        print("----------------------------------------------")
        # ---------------------------------------

        # Dibujar rectángulo y texto
        texto = f"{emocion} ({probabilidad*100:.1f}%)"
        cv2.putText(fotograma, texto, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.rectangle(fotograma, (x, y), (x + w, y + h),
                      (0, 255, 0), 2)

        # Cargar emoji
        emoji = cargar_emoji(emocion)

        if emoji is not None:
            emoji_redimensionado = cv2.resize(emoji, (300, fotograma.shape[0]), interpolation=cv2.INTER_CUBIC)
        else:
            emoji_redimensionado = panel_vacio.copy()

        fotograma_completo = cv2.hconcat([fotograma, emoji_redimensionado])

    cv2.imshow('Reconocimiento de emociones (VGG16)', fotograma_completo)

    tecla = cv2.waitKey(1)
    if tecla == 27:  # ESC
        break

camara.release()
cv2.destroyAllWindows()
