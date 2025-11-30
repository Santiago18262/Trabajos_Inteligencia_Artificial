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
ruta_entrenamiento = r'C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\modelos\dataset(AffectNet)\train'
ruta_prueba        = r'C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\modelos\dataset2(AffectNet)\test'

TAMANO_IMAGEN   = 96      # para que sea mas rapido el entrenamiento
TAMANO_LOTE     = 32   # tamaño de lote
EPOCAS_FASE1    = 20 
EPOCAS_FASE2    = 15  

# ---------------------------------------------------------------------
# 1.1 PREPROCESAMIENTO
# ---------------------------------------------------------------------
def preprocesamiento_personalizado(imagen):
    imagen = tf.cast(imagen, tf.float32)
    imagen = preprocess_input(imagen)   # normalización ResNet50
    return imagen

# ---------------------------------------------------------------------
# 2. DATA AUGMENTATION
# ---------------------------------------------------------------------
generador_aumento_entrenamiento = ImageDataGenerator(
    preprocessing_function=preprocesamiento_personalizado,
    rotation_range=25,
    width_shift_range=0.20,
    height_shift_range=0.20,
    zoom_range=0.20,
    horizontal_flip=True
)

generador_aumento_prueba = ImageDataGenerator(
    preprocessing_function=preprocesamiento_personalizado
)

generador_entrenamiento = generador_aumento_entrenamiento.flow_from_directory(
    ruta_entrenamiento,
    target_size=(TAMANO_IMAGEN, TAMANO_IMAGEN),
    batch_size=TAMANO_LOTE,
    class_mode='categorical',
    shuffle=True
)

generador_prueba = generador_aumento_prueba.flow_from_directory(
    ruta_prueba,
    target_size=(TAMANO_IMAGEN, TAMANO_IMAGEN),
    batch_size=TAMANO_LOTE,
    class_mode='categorical',
    shuffle=False
)

# ---------------------------------------------------------------------
# 3. INFO DE CLASES + PESOS AUTOMÁTICOS + AJUSTE
# ---------------------------------------------------------------------
indices_clases = generador_entrenamiento.class_indices
lista_emociones = sorted(indices_clases, key=lambda k: indices_clases[k])

print("\nClases detectadas:")
for nombre, indice in indices_clases.items():
    print(f"{indice}: {nombre}")

conteo_clases = Counter(generador_entrenamiento.classes)
print("\nConteo en Train:")
for indice, cantidad in conteo_clases.items():
    print(f"{lista_emociones[indice]}: {cantidad}")

# Pesos base balanceados
pesos_base = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(generador_entrenamiento.classes),
    y=generador_entrenamiento.classes
)
pesos_clase_diccionario = {i: float(pesos_base[i]) for i in range(len(pesos_base))}

# Ajuste manual según tu matriz:
# Alegria y Enojo estaban "dominando"
# Neutral y Tristeza tenían bajo recall → los potenciamos
indice_alegria  = lista_emociones.index("Alegria")
indice_enojo    = lista_emociones.index("Enojo")
indice_neutral  = lista_emociones.index("Neutral")
indice_tristeza = lista_emociones.index("Tristeza")
indice_sorpresa = lista_emociones.index("Sorpresa")

# Ajuste más equilibrado de pesos
pesos_clase_diccionario[indice_alegria]  *= 1.20   # casi neutro se cambio de 0.95 a 1.10 
pesos_clase_diccionario[indice_enojo]    *= 1.30   # reforzamos enojo 
pesos_clase_diccionario[indice_neutral]  *= 1.70   # ligero ajuste se cambio de 1.05 a 1.10
pesos_clase_diccionario[indice_tristeza] *= 0.80   # ya no tan castigado
pesos_clase_diccionario[indice_sorpresa] *= 1.10   # reforzada, pero no exagerada de 1.20 a

print("\nPesos finales usados:")
for i, peso in pesos_clase_diccionario.items():
    print(f"{i} ({lista_emociones[i]}): {peso:.3f}")

# ---------------------------------------------------------------------
# 4. MODELO BASE: RESNET50
# ---------------------------------------------------------------------
modelo_base = ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(TAMANO_IMAGEN, TAMANO_IMAGEN, 3)
)

for capa in modelo_base.layers:
    capa.trainable = False  # fase 1 congelada

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
    generador_entrenamiento,
    validation_data=generador_prueba,
    epochs=EPOCAS_FASE1,
    class_weight=pesos_clase_diccionario,
    callbacks=callbacks
)

# ---------------------------------------------------------------------
# 7. FASE 2 – FINE TUNING (MÁS CAPAS)
# ---------------------------------------------------------------------
print("\nFine-Tuning...")

modelo_base.trainable = True
# descongelamos más capas (últimas 50) para que se adapte mejor
for capa in modelo_base.layers[:-50]:
    capa.trainable = False

modelo.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

modelo.fit(
    generador_entrenamiento,
    validation_data=generador_prueba,
    epochs=EPOCAS_FASE2,
    class_weight=pesos_clase_diccionario,
    callbacks=callbacks
)

# ---------------------------------------------------------------------
# 8. EVALUACIÓN
# ---------------------------------------------------------------------
print("\nCargando mejor modelo...")
mejor_modelo = load_model("mejor_resnet50.keras")

generador_prueba.reset()
predicciones = mejor_modelo.predict(generador_prueba)
clases_predichas = np.argmax(predicciones, axis=1)
clases_reales = generador_prueba.classes

print("\nMatriz de confusión:")
print(confusion_matrix(clases_reales, clases_predichas))

print("\nReporte de clasificación:")
print(classification_report(clases_reales, clases_predichas, target_names=lista_emociones))

# ---------------------------------------------------------------------
# 9. GUARDAR MODELO Y CLASES
# ---------------------------------------------------------------------
mejor_modelo.save("modelo_emociones_resnet50.keras")
np.save("label_names.npy", np.array(lista_emociones))

print("\n✅ Modelo guardado como modelo_emociones_resnet50.keras")
print("✨ Clases guardadas como label_names.npy")
