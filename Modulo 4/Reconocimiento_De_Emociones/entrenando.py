import os
import time
from collections import Counter

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.models import load_model


# ---------------------------------------------------------------------
# 1. RUTAS DEL DATASET (AFFECTNET)
# ---------------------------------------------------------------------
ruta_train = r'C:\USB Santiago\AffectNet\train'
ruta_val   = r'C:\USB Santiago\AffectNet\val'

TAMANO_IMAGEN = 48       # Igual que tu script original, rápido
BATCH_SIZE = 32
EPOCHS_FASE1 = 12
EPOCHS_FASE2 = 10


# ---------------------------------------------------------------------
# 1.1 PREPROCESAMIENTO AVANZADO (MEJORADO)
# ---------------------------------------------------------------------
def custom_preprocess(img):
    """
    Mejor preprocesamiento:
    - normalización ResNet50
    """
    img = tf.cast(img, tf.float32)
    img = preprocess_input(img)
    return img


# ---------------------------------------------------------------------
# 2. DATA AUGMENTATION + GENERADORES
# ---------------------------------------------------------------------
datagen_train = ImageDataGenerator(
    preprocessing_function=custom_preprocess,
    rotation_range=25,
    width_shift_range=0.20,
    height_shift_range=0.20,
    zoom_range=0.20,
    horizontal_flip=True
)

datagen_val = ImageDataGenerator(
    preprocessing_function=custom_preprocess
)

train_gen = datagen_train.flow_from_directory(
    ruta_train,
    target_size=(TAMANO_IMAGEN, TAMANO_IMAGEN),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

val_gen = datagen_val.flow_from_directory(
    ruta_val,
    target_size=(TAMANO_IMAGEN, TAMANO_IMAGEN),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)


# ---------------------------------------------------------------------
# 3. INFO DE CLASES + PESOS AUTOMÁTICOS
# ---------------------------------------------------------------------
class_indices = train_gen.class_indices
lista_emociones = sorted(class_indices, key=lambda k: class_indices[k])

print("\nClases detectadas (índice -> nombre):")
for nombre, idx in class_indices.items():
    print(f"{idx}: {nombre}")

conteo_clases = Counter(train_gen.classes)
print("\nConteo por clase en TRAIN:")
for idx, cant in conteo_clases.items():
    print(f"{idx} ({lista_emociones[idx]}): {cant}")

y_train = train_gen.classes
clases_unicas = np.unique(y_train)

pesos = compute_class_weight(
    class_weight="balanced",
    classes=clases_unicas,
    y=y_train
)

class_weights_dict = {int(c): float(p) for c, p in zip(clases_unicas, pesos)}

print("\nPesos balanceados:")
print(class_weights_dict)


# ---------------------------------------------------------------------
# 4. MODELO BASE – RESNET50 (FASE 1)
# ---------------------------------------------------------------------
modelo_base = ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(TAMANO_IMAGEN, TAMANO_IMAGEN, 3)
)

for capa in modelo_base.layers:
    capa.trainable = False  # Fase 1

# CAPAS SUPERIORES PERSONALIZADAS
x = layers.GlobalAveragePooling2D()(modelo_base.output)
x = layers.Dense(256, activation='relu')(x)
x = layers.Dropout(0.5)(x)
salida = layers.Dense(len(lista_emociones), activation='softmax')(x)

modelo = models.Model(inputs=modelo_base.input, outputs=salida)

modelo.compile(
    optimizer=tf.keras.optimizers.Adam(1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("\nResumen del modelo:")
modelo.summary()


# ---------------------------------------------------------------------
# 5. CALLBACKS PARA ENTRENAMIENTO ESTABLE
# ---------------------------------------------------------------------
callbacks = [
    EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-7),
    ModelCheckpoint('mejor_modelo_resnet50.keras', monitor='val_accuracy', save_best_only=True)
]


# ---------------------------------------------------------------------
# 6. ENTRENAMIENTO FASE 1 (CAPAS CONGELADAS)
# ---------------------------------------------------------------------
print("\nEntrenando FASE 1...")
inicio = time.time()

modelo.fit(
    train_gen,
    epochs=EPOCHS_FASE1,
    validation_data=val_gen,
    class_weight=class_weights_dict,
    callbacks=callbacks
)


# ---------------------------------------------------------------------
# 7. FASE 2 – FINE-TUNING
# ---------------------------------------------------------------------
print("\nAplicando FINE-TUNING...")

modelo_base.trainable = True

# descongelar SOLAMENTE últimas 50 capas
for layer in modelo_base.layers[:-50]:
    layer.trainable = False

modelo.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

modelo.fit(
    train_gen,
    epochs=EPOCHS_FASE2,
    validation_data=val_gen,
    class_weight=class_weights_dict,
    callbacks=callbacks
)

print(f"\nTiempo total entrenamiento: {time.time() - inicio:.2f} segundos")


# ---------------------------------------------------------------------
# 8. EVALUACIÓN FINAL
# ---------------------------------------------------------------------
print("\nCargando mejor modelo...")
mejor_modelo = load_model("mejor_modelo_resnet50.keras")

val_gen.reset()
predicciones = mejor_modelo.predict(val_gen)
clases_pred = np.argmax(predicciones, axis=1)
clases_reales = val_gen.classes

print("\nMatriz de confusión:")
print(confusion_matrix(clases_reales, clases_pred))

print("\nReporte de clasificación:")
print(classification_report(clases_reales, clases_pred, target_names=lista_emociones))


# ---------------------------------------------------------------------
# 9. GUARDADO FINAL
# ---------------------------------------------------------------------
mejor_modelo.save("modelo_emociones_resnet50.keras")
np.save("label_names.npy", np.array(lista_emociones))

print("\n✅ Modelo final guardado como modelo_emociones_resnet50.keras")
print("✅ Clases guardadas como label_names.npy")
