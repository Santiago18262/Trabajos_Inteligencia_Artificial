# entrenar_fer2013_generators.py
import os
import time
from collections import Counter

import numpy as np  # Esta librería es para manejo de arreglos
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight  # Para calcular pesos de clase

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ---------------------------------------------------------------------
# 1. RUTA DONDE ESTÁ EL DATASET FER2013 EN CARPETAS
# ---------------------------------------------------------------------
ruta_datos = r'C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\dataset\train'

# TAMANO_IMAGEN = 224   # tamaño requerido por VGG16 en teoría
TAMANO_IMAGEN = 48      # tamaño original del dataset FER2013 (más rápido de entrenar)
BATCH_SIZE = 32         # tamaño de lote para los generadores
EPOCHS_FASE1 = 3
EPOCHS_FASE2 = 3
VALID_SPLIT = 0.2       # 20% validación

# ---------------------------------------------------------------------
# 2. DATA AUGMENTATION + GENERADORES (SIN CARGAR TODO EN RAM)
# ---------------------------------------------------------------------
# preprocess_input de VGG16 se aplica dentro del generador
datagen_entrenamiento = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True,
    validation_split=VALID_SPLIT
)

# Generador de entrenamiento
train_gen = datagen_entrenamiento.flow_from_directory(
    ruta_datos,
    target_size=(TAMANO_IMAGEN, TAMANO_IMAGEN),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

# Generador de validación (IMPORTANTE: shuffle=False para matriz de confusión)
val_gen = datagen_entrenamiento.flow_from_directory(
    ruta_datos,
    target_size=(TAMANO_IMAGEN, TAMANO_IMAGEN),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

# ---------------------------------------------------------------------
# 3. INFO DE CLASES
# ---------------------------------------------------------------------
# class_indices es un diccionario {nombre_clase: índice}
class_indices = train_gen.class_indices
# Lo convertimos en lista ordenada por índice: [ "Angry", "Disgust", ... ]
lista_emociones = sorted(class_indices, key=lambda k: class_indices[k])
cantidad_clases = len(lista_emociones)

print("Emociones detectadas en el dataset:", lista_emociones)
print("Total imágenes entrenamiento:", train_gen.samples)
print("Total imágenes validación:", val_gen.samples)

# Imprimir conteo por clase usando el generador de entrenamiento
conteo_clases = Counter(train_gen.classes)
print("\nConteo por clase (índice -> cantidad) en TRAIN:")
for idx, cant in conteo_clases.items():
    print(f"{idx} ({lista_emociones[idx]}): {cant}")

print("\nOrden de emociones (índice -> nombre):")
for idx, emo in enumerate(lista_emociones):
    print(f"{idx}: {emo}")

# ---------------------------------------------------------------------
# 3.1 CÁLCULO DE PESOS DE CLASE (PARA MANEJAR DESBALANCE)
# ---------------------------------------------------------------------
# Esto hace que todas las clases "pesen" similar en el loss,
# aunque haya menos imágenes de disgust/sad/etc.
class_weights = compute_class_weight(
    class_weight="balanced",
    classes=np.unique(train_gen.classes),
    y=train_gen.classes
)

# Lo pasamos a diccionario {índice_clase: peso}
class_weights_dict = {i: float(class_weights[i]) for i in range(len(class_weights))}
print("\nPesos de clase calculados (class_weight='balanced'):")
for idx, peso in class_weights_dict.items():
    print(f"Clase {idx} ({lista_emociones[idx]}): {peso:.3f}")

# ---------------------------------------------------------------------
# 4. MODELO BASE VGG16 (FASE 1: CAPAS CONGELADAS)
# ---------------------------------------------------------------------
modelo_base = VGG16(
    weights='imagenet',
    include_top=False,
    input_shape=(TAMANO_IMAGEN, TAMANO_IMAGEN, 3)
)

# Congelar TODAS las capas de VGG16 en la fase 1
for capa in modelo_base.layers:
    capa.trainable = False

# CAPAS FINALES PERSONALIZADAS
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

print("\nResumen del modelo:")
modelo.summary()

# ---------------------------------------------------------------------
# 5. ENTRENAMIENTO FASE 1 (CAPAS CONGELADAS)
# ---------------------------------------------------------------------
print("\nEntrenando modelo (FASE 1 - capas congeladas)...")
inicio_tiempo = time.time()

historial_1 = modelo.fit(
    train_gen,
    epochs=EPOCHS_FASE1,
    validation_data=val_gen,
    class_weight=class_weights_dict  # <-- USAMOS PESOS DE CLASE
)

# ---------------------------------------------------------------------
# 6. FASE 2 - FINE TUNING (DESCONGELAR ÚLTIMAS 10 CAPAS)
# ---------------------------------------------------------------------
print("\nAplicando Fine-Tuning (descongelando últimas 10 capas)...")

for capa in modelo_base.layers[-10:]:
    capa.trainable = True

modelo.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

historial_2 = modelo.fit(
    train_gen,
    epochs=EPOCHS_FASE2,
    validation_data=val_gen,
    class_weight=class_weights_dict  # <-- TAMBIÉN AQUÍ
)

tiempo_total = time.time() - inicio_tiempo
print(f"\nEntrenamiento completado en {tiempo_total:.2f} segundos.")

# ---------------------------------------------------------------------
# 7. EVALUACIÓN DETALLADA (MATRIZ DE CONFUSIÓN + REPORTE)
# ---------------------------------------------------------------------
print("\nGenerando predicciones en el conjunto de validación...")

# Reiniciamos el generador para recorrer todas las imágenes en orden
val_gen.reset()
predicciones_val = modelo.predict(val_gen)
clases_predichas = np.argmax(predicciones_val, axis=1)

# Etiquetas reales del generador
clases_reales = val_gen.classes

print("\nMatriz de confusión:")
print(confusion_matrix(clases_reales, clases_predichas))

print("\nReporte detallado de clasificación:")
print(classification_report(clases_reales, clases_predichas, target_names=lista_emociones))

# ---------------------------------------------------------------------
# 8. GUARDAR MODELO Y CLASES (PARA EL SCRIPT DE LA CÁMARA)
# ---------------------------------------------------------------------
modelo.save("modelo_emociones_vgg16.h5")
np.save("label_names.npy", np.array(lista_emociones))

print("\n✅ Modelo guardado como modelo_emociones_vgg16.h5")  # .h5 guarda arquitectura + pesos
print("✅ Clases guardadas como label_names.npy")            # .npy guarda el arreglo de nombres
