import cv2
import os
import numpy as np
import time
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator

#---------------------------------------------------------------------
# RUTA DONDE ESTÁN LAS CARPETAS DE EMOCIONES
#---------------------------------------------------------------------
ruta_datos = r'C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\Data'
lista_emociones = sorted(os.listdir(ruta_datos))
print("Emociones detectadas:", lista_emociones)

TAMANO_IMAGEN = 224  # Tamaño requerido por VGG16

datos_imagenes = []
lista_etiquetas = []

print("Cargando imágenes...")

#---------------------------------------------------------------------
# CARGA DE IMÁGENES Y ETIQUETAS
#---------------------------------------------------------------------
for indice_etiqueta, emocion in enumerate(lista_emociones):
    ruta_emocion = os.path.join(ruta_datos, emocion)

    for nombre_archivo in os.listdir(ruta_emocion):
        ruta_archivo = os.path.join(ruta_emocion, nombre_archivo)

        imagen = cv2.imread(ruta_archivo)
        if imagen is None:
            continue

        imagen = cv2.resize(imagen, (TAMANO_IMAGEN, TAMANO_IMAGEN))
        imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

        datos_imagenes.append(imagen)
        lista_etiquetas.append(indice_etiqueta)

datos_imagenes = np.array(datos_imagenes, dtype="float32")
lista_etiquetas = np.array(lista_etiquetas)

#---------------------------------------------------------------------
# DEPURACIÓN DE CLASES
#---------------------------------------------------------------------
print("Total de imágenes cargadas:", len(datos_imagenes))
print("Conteo por clase:", Counter(lista_etiquetas))
print("Orden de emociones:", lista_emociones)

#---------------------------------------------------------------------
# PREPROCESAMIENTO VGG16
#---------------------------------------------------------------------
datos_imagenes = preprocess_input(datos_imagenes)

cantidad_clases = len(lista_emociones)
etiquetas_onehot = to_categorical(lista_etiquetas, num_classes=cantidad_clases)

# División de datos
X_entrenamiento, X_validacion, y_entrenamiento, y_validacion = train_test_split(
    datos_imagenes, etiquetas_onehot, test_size=0.2, random_state=42, stratify=lista_etiquetas
)

#---------------------------------------------------------------------
# DATA AUGMENTATION
#---------------------------------------------------------------------
augmentador = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True
)
augmentador.fit(X_entrenamiento)

#---------------------------------------------------------------------
# MODELO BASE VGG16 (FASE 1: CAPAS CONGELADAS)
#---------------------------------------------------------------------
modelo_base = VGG16(
    weights='imagenet',
    include_top=False,
    input_shape=(TAMANO_IMAGEN, TAMANO_IMAGEN, 3)
)

# Congelar TODAS las capas de VGG16 en la fase 1
for capa in modelo_base.layers:
    capa.trainable = False

# CAPAS FINALES
entrada_red = modelo_base.output
entrada_red = layers.Flatten()(entrada_red)
entrada_red = layers.Dense(256, activation='relu')(entrada_red)
entrada_red = layers.Dropout(0.5)(entrada_red)
salida_red = layers.Dense(cantidad_clases, activation='softmax')(entrada_red)

modelo = models.Model(inputs=modelo_base.input, outputs=salida_red)

modelo.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print(modelo.summary())

#---------------------------------------------------------------------
# ENTRENAMIENTO FASE 1 (CAPAS CONGELADAS)
#---------------------------------------------------------------------
print("\nEntrenando modelo (FASE 1 - capas congeladas)...")
inicio_tiempo = time.time()

historial_1 = modelo.fit(
    augmentador.flow(X_entrenamiento, y_entrenamiento, batch_size=32),
    epochs=5,
    validation_data=(X_validacion, y_validacion)
)

#---------------------------------------------------------------------
# FASE 2 - FINE TUNING (DESCONGELAR ÚLTIMAS 10 CAPAS)
#---------------------------------------------------------------------
print("\nAplicando Fine-Tuning (descongelando últimas 10 capas)...")

for capa in modelo_base.layers[-10:]:
    capa.trainable = True

modelo.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

historial_2 = modelo.fit(
    augmentador.flow(X_entrenamiento, y_entrenamiento, batch_size=32),
    epochs=5,
    validation_data=(X_validacion, y_validacion)
)

tiempo_total = time.time() - inicio_tiempo
print(f"\nEntrenamiento completado en {tiempo_total:.2f} segundos.")

#---------------------------------------------------------------------
# EVALUACIÓN DETALLADA
#---------------------------------------------------------------------
predicciones_val = modelo.predict(X_validacion)
clases_reales = np.argmax(y_validacion, axis=1)
clases_predichas = np.argmax(predicciones_val, axis=1)

print("\nMatriz de confusión:")
print(confusion_matrix(clases_reales, clases_predichas))

print("\nReporte detallado de clasificación:")
print(classification_report(clases_reales, clases_predichas, target_names=lista_emociones))

#---------------------------------------------------------------------
# GUARDAR MODELO Y CLASES
#---------------------------------------------------------------------
modelo.save("modelo_emociones_vgg16.h5")
np.save("nombres_clases.npy", np.array(lista_emociones))

print("\nModelo guardado como modelo_emociones_vgg16.h5")
print("Clases guardadas como nombres_clases.npy")
  