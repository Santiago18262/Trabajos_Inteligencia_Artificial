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
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.models import load_model

# ---------------------------------------------------------------------
# 1. RUTA DONDE ESTÁ EL DATASET FER2013 EN CARPETAS
# ---------------------------------------------------------------------
ruta_datos = r'C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\dataset\train'

TAMANO_IMAGEN = 48       # tamaño original del dataset FER2013 (más rápido de entrenar)
BATCH_SIZE = 32
EPOCHS_FASE1 = 15        # más épocas, pero con EarlyStopping
EPOCHS_FASE2 = 15
VALID_SPLIT = 0.2        # 20% validación

# ---------------------------------------------------------------------
# 1.1 FUNCIÓN DE PREPROCESAMIENTO AVANZADO
#     (simula poca luz, variaciones de contraste, ruido, etc.)
# ---------------------------------------------------------------------
def custom_preprocess(img):
    """
    img llega en rango [0, 255] y en RGB.
    Simulamos:
    - cambios de iluminación (más oscuro/más claro)
    - cambios de contraste
    - ruido gaussiano (como cámara en poca luz)
    y al final aplicamos el preprocess_input de VGG16.
    """
    img = tf.cast(img, tf.float32)

    # Cambios de iluminación global
    factor_luz = tf.random.uniform([], 0.5, 1.5)  # 0.5 = más oscuro, 1.5 = más claro
    img = img * factor_luz

    # Contraste aleatorio
    img = tf.image.random_contrast(img, 0.8, 1.2)

    # Ruido gaussiano suave
    ruido = tf.random.normal(tf.shape(img), mean=0.0, stddev=10.0)
    img = img + ruido

    # Clampeamos a rango válido
    img = tf.clip_by_value(img, 0.0, 255.0)

    # Preprocesamiento estándar de VGG16
    img = preprocess_input(img)

    return img

# ---------------------------------------------------------------------
# 2. DATA AUGMENTATION + GENERADORES (SIN CARGAR TODO EN RAM)
# ---------------------------------------------------------------------
datagen_entrenamiento = ImageDataGenerator(
    preprocessing_function=custom_preprocess,  # usamos nuestra función
    rotation_range=25,
    width_shift_range=0.15,
    height_shift_range=0.15,
    zoom_range=0.15,
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
class_indices = train_gen.class_indices
lista_emociones = sorted(class_indices, key=lambda k: class_indices[k])
cantidad_clases = len(lista_emociones)

print("\nClases detectadas (índice -> nombre):")
for nombre, idx in class_indices.items():
    print(f"{idx}: {nombre}")

# Imprimir conteo por clase usando el generador de entrenamiento
conteo_clases = Counter(train_gen.classes)
print("\nConteo por clase (índice -> cantidad) en TRAIN:")
for idx, cant in conteo_clases.items():
    print(f"{idx} ({lista_emociones[idx]}): {cant}")

# ---------------------------------------------------------------------
# 3.1 CÁLCULO DE PESOS DE CLASE AUTOMÁTICO (PARA MANEJAR DESBALANCE)
# ---------------------------------------------------------------------
y_train = train_gen.classes
clases_unicas = np.unique(y_train)

pesos = compute_class_weight(
    class_weight='balanced',
    classes=clases_unicas,
    y=y_train
)

class_weights_dict = {int(clase): float(peso) for clase, peso in zip(clases_unicas, pesos)}

print("\nPesos de clase calculados automáticamente:")
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
# 5. CALLBACKS PARA MEJOR ENTRENAMIENTO
# ---------------------------------------------------------------------
callbacks = [
    EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=2,
        min_lr=1e-7
    ),
    ModelCheckpoint(
        'mejor_modelo_vgg16.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
]

# ---------------------------------------------------------------------
# 6. ENTRENAMIENTO FASE 1 (CAPAS CONGELADAS)
# ---------------------------------------------------------------------
print("\nEntrenando modelo (FASE 1 - capas congeladas)...")
inicio_tiempo = time.time()

historial_1 = modelo.fit(
    train_gen,
    epochs=EPOCHS_FASE1,
    validation_data=val_gen,
    class_weight=class_weights_dict,
    callbacks=callbacks
)

# ---------------------------------------------------------------------
# 7. FASE 2 - FINE TUNING (DESCONGELAR PARTE DE VGG16)
# ---------------------------------------------------------------------
print("\nAplicando Fine-Tuning (descongelando parte de VGG16)...")

# Descongelar las últimas N capas de VGG16 de forma más controlada
num_capas_descongelar = 15  # puedes probar 10, 15, 20
descongelar_desde = len(modelo_base.layers) - num_capas_descongelar

for i, capa in enumerate(modelo_base.layers):
    if i >= descongelar_desde:
        capa.trainable = True
    else:
        capa.trainable = False

modelo.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),  # LR más bajo para fine-tuning
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

historial_2 = modelo.fit(
    train_gen,
    epochs=EPOCHS_FASE2,
    validation_data=val_gen,
    class_weight=class_weights_dict,
    callbacks=callbacks
)

tiempo_total = time.time() - inicio_tiempo
print(f"\nEntrenamiento completado en {tiempo_total:.2f} segundos.")

# ---------------------------------------------------------------------
# 8. CARGAR EL MEJOR MODELO (GUARDADO POR ModelCheckpoint)
# ---------------------------------------------------------------------
print("\nCargando el mejor modelo guardado (según val_accuracy)...")
mejor_modelo = load_model('mejor_modelo_vgg16.h5')

# ---------------------------------------------------------------------
# 9. EVALUACIÓN DETALLADA (MATRIZ DE CONFUSIÓN + REPORTE)
# ---------------------------------------------------------------------
print("\nGenerando predicciones en el conjunto de validación...")

val_gen.reset()
predicciones_val = mejor_modelo.predict(val_gen)
clases_predichas = np.argmax(predicciones_val, axis=1)

# Etiquetas reales del generador
clases_reales = val_gen.classes

print("\nMatriz de confusión:")
print(confusion_matrix(clases_reales, clases_predichas))

print("\nReporte detallado de clasificación:")
print(classification_report(clases_reales, clases_predichas, target_names=lista_emociones))

# ---------------------------------------------------------------------
# 10. GUARDAR MODELO FINAL Y CLASES (PARA EL SCRIPT DE LA CÁMARA)
# ---------------------------------------------------------------------
mejor_modelo.save("modelo_emociones_vgg16.h5")  # sobrescribimos con el mejor
np.save("label_names.npy", np.array(lista_emociones))

print("\n✅ Mejor modelo guardado como modelo_emociones_vgg16.h5")
print("✅ Clases guardadas como label_names.npy")
