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
# 1. RUTAS DE TU DATASET (Train / Test)
# ---------------------------------------------------------------------
ruta_train = r'C:\USB Santiago\dataset2\Train'
ruta_test  = r'C:\USB Santiago\dataset2\Test'

TAMANO_IMAGEN = 112      # <<< SUBIMOS A 112x112 PARA MÁS DETALLE
BATCH_SIZE = 32
EPOCHS_FASE1 = 12
EPOCHS_FASE2 = 10

# ---------------------------------------------------------------------
# 1.1 PREPROCESAMIENTO
# ---------------------------------------------------------------------
def custom_preprocess(img):
    img = tf.cast(img, tf.float32)
    img = preprocess_input(img)   # normalización ResNet50
    return img

# ---------------------------------------------------------------------
# 2. DATA AUGMENTATION
# ---------------------------------------------------------------------
datagen_train = ImageDataGenerator(
    preprocessing_function=custom_preprocess,
    rotation_range=25,
    width_shift_range=0.20,
    height_shift_range=0.20,
    zoom_range=0.20,
    horizontal_flip=True
)

datagen_test = ImageDataGenerator(
    preprocessing_function=custom_preprocess
)

train_gen = datagen_train.flow_from_directory(
    ruta_train,
    target_size=(TAMANO_IMAGEN, TAMANO_IMAGEN),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

test_gen = datagen_test.flow_from_directory(
    ruta_test,
    target_size=(TAMANO_IMAGEN, TAMANO_IMAGEN),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

# ---------------------------------------------------------------------
# 3. INFO DE CLASES + PESOS AUTOMÁTICOS + AJUSTE
# ---------------------------------------------------------------------
class_indices = train_gen.class_indices
lista_emociones = sorted(class_indices, key=lambda k: class_indices[k])

print("\nClases detectadas:")
for name, idx in class_indices.items():
    print(f"{idx}: {name}")

conteo = Counter(train_gen.classes)
print("\nConteo en Train:")
for idx, cant in conteo.items():
    print(f"{lista_emociones[idx]}: {cant}")

# Pesos base balanceados
pesos_base = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_gen.classes),
    y=train_gen.classes
)
class_weights_dict = {i: float(pesos_base[i]) for i in range(len(pesos_base))}

# Ajuste manual según tu matriz:
# Alegria y Enojo estaban "dominando"
# Neutral y Tristeza tenían bajo recall → los potenciamos
idx_alegria  = lista_emociones.index("Alegria")
idx_enojo    = lista_emociones.index("Enojo")
idx_neutral  = lista_emociones.index("Neutral")
idx_tristeza = lista_emociones.index("Tristeza")

class_weights_dict[idx_alegria]  *= 0.9
class_weights_dict[idx_enojo]    *= 0.95
class_weights_dict[idx_neutral]  *= 1.2
class_weights_dict[idx_tristeza] *= 1.25

print("\nPesos finales usados:")
for i, w in class_weights_dict.items():
    print(f"{i} ({lista_emociones[i]}): {w:.3f}")

# ---------------------------------------------------------------------
# 4. MODELO BASE: RESNET50
# ---------------------------------------------------------------------
modelo_base = ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(TAMANO_IMAGEN, TAMANO_IMAGEN, 3)
)

for layer in modelo_base.layers:
    layer.trainable = False  # fase 1 congelada

# CAPAS FINALES
x = layers.GlobalAveragePooling2D()(modelo_base.output)
x = layers.Dense(256, activation='relu')(x)
x = layers.Dropout(0.5)(x)
salida = layers.Dense(len(lista_emociones), activation='softmax')(x)

modelo = models.Model(modelo_base.input, salida)

modelo.compile(
    optimizer=tf.keras.optimizers.Adam(1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("\nResumen del modelo:")
modelo.summary()

# ---------------------------------------------------------------------
# 5. CALLBACKS
# ---------------------------------------------------------------------
callbacks = [
    EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
    ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-7),
    ModelCheckpoint("mejor_resnet50.keras", monitor="val_accuracy", save_best_only=True)
]

# ---------------------------------------------------------------------
# 6. FASE 1 – ENTRENAMIENTO
# ---------------------------------------------------------------------
print("\nEntrenando FASE 1...")
modelo.fit(
    train_gen,
    validation_data=test_gen,
    epochs=EPOCHS_FASE1,
    class_weight=class_weights_dict,
    callbacks=callbacks
)

# ---------------------------------------------------------------------
# 7. FASE 2 – FINE TUNING (MÁS CAPAS)
# ---------------------------------------------------------------------
print("\nFine-Tuning...")

modelo_base.trainable = True
# descongelamos más capas (últimas 80) para que se adapte mejor
for layer in modelo_base.layers[:-80]:
    layer.trainable = False

modelo.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

modelo.fit(
    train_gen,
    validation_data=test_gen,
    epochs=EPOCHS_FASE2,
    class_weight=class_weights_dict,
    callbacks=callbacks
)

# ---------------------------------------------------------------------
# 8. EVALUACIÓN
# ---------------------------------------------------------------------
print("\nCargando mejor modelo...")
mejor = load_model("mejor_resnet50.keras")

test_gen.reset()
pred = mejor.predict(test_gen)
pred_clases = np.argmax(pred, axis=1)
real_clases = test_gen.classes

print("\nMatriz de confusión:")
print(confusion_matrix(real_clases, pred_clases))

print("\nReporte de clasificación:")
print(classification_report(real_clases, pred_clases, target_names=lista_emociones))

# ---------------------------------------------------------------------
# 9. GUARDAR MODELO Y CLASES
# ---------------------------------------------------------------------
mejor.save("modelo_emociones_resnet50.keras")
np.save("label_names.npy", np.array(lista_emociones))

print("\n✅ Modelo guardado como modelo_emociones_resnet50.keras")
print("✨ Clases guardadas como label_names.npy")
