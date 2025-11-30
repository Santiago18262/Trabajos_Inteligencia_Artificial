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

TAMANO_IMAGEN   = 96   # Tamaño reducido para acelerar el entrenamiento
TAMANO_LOTE     = 32   # Cantidad de imágenes por lote (batch)
EPOCAS_FASE1    = 20   # Épocas entrenando solo las capas finales
EPOCAS_FASE2    = 15   # Épocas de ajuste fino (fine-tuning)

# ---------------------------------------------------------------------
# 1.1 PREPROCESAMIENTO
# ---------------------------------------------------------------------
def preprocesamiento_personalizado(imagen):
    imagen = tf.cast(imagen, tf.float32)    # Convierte la imagen a números decimales
    imagen = preprocess_input(imagen)       # Ajusta colores al formato específico de ResNet
    return imagen

# ---------------------------------------------------------------------
# 2. AUMENTO DE DATOS (Generación de variantes)
# ---------------------------------------------------------------------
generador_aumento_entrenamiento = ImageDataGenerator(
    preprocessing_function=preprocesamiento_personalizado,
    rotation_range=25,        # Rota la imagen aleatoriamente
    width_shift_range=0.20,   # Mueve la imagen horizontalmente
    height_shift_range=0.20,  # Mueve la imagen verticalmente
    zoom_range=0.20,          # Acerca o aleja la imagen
    horizontal_flip=True      # Invierte la imagen horizontalmente (espejo)
)

# Para prueba NO aumentamos datos, solo aplicamos el preprocesamiento base
generador_aumento_prueba = ImageDataGenerator(
    preprocessing_function=preprocesamiento_personalizado
)

# Carga imágenes de entrenamiento
generador_entrenamiento = generador_aumento_entrenamiento.flow_from_directory(
    ruta_entrenamiento,
    target_size=(TAMANO_IMAGEN, TAMANO_IMAGEN),
    batch_size=TAMANO_LOTE,
    class_mode='categorical',
    shuffle=True # Mezcla los datos aleatoriamente
)

# Carga imágenes de prueba
generador_prueba = generador_aumento_prueba.flow_from_directory(
    ruta_prueba,
    target_size=(TAMANO_IMAGEN, TAMANO_IMAGEN),
    batch_size=TAMANO_LOTE,
    class_mode='categorical',
    shuffle=False # Mantiene el orden fijo para evaluar correctamente
)

# ---------------------------------------------------------------------
# 3. INFO DE CLASES + PESOS AUTOMÁTICOS + AJUSTE MANUAL
# ---------------------------------------------------------------------
indices_clases = generador_entrenamiento.class_indices
lista_emociones = sorted(indices_clases, key=lambda k: indices_clases[k])

print("\nClases detectadas:")
for nombre, indice in indices_clases.items():
    print(f"{indice}: {nombre}")

conteo_clases = Counter(generador_entrenamiento.classes)
print("\nConteo en Entrenamiento:")
for indice, cantidad in conteo_clases.items():
    print(f"{lista_emociones[indice]}: {cantidad}")

# Calcula pesos base para equilibrar clases desproporcionadas
pesos_base = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(generador_entrenamiento.classes),
    y=generador_entrenamiento.classes
)
pesos_clase_diccionario = {i: float(pesos_base[i]) for i in range(len(pesos_base))}

# Obtiene índices numéricos de cada emoción
indice_alegria  = lista_emociones.index("Alegria")
indice_enojo    = lista_emociones.index("Enojo")
indice_neutral  = lista_emociones.index("Neutral")
indice_tristeza = lista_emociones.index("Tristeza")
indice_sorpresa = lista_emociones.index("Sorpresa")

# Ajuste manual de prioridades (basado en tu análisis previo)
pesos_clase_diccionario[indice_alegria]  *= 1.20   # Aumenta prioridad de Alegría
pesos_clase_diccionario[indice_enojo]    *= 1.30   # Refuerza aprendizaje de Enojo
pesos_clase_diccionario[indice_neutral]  *= 1.70   # Aumenta mucho Neutral (suele ser difícil)
pesos_clase_diccionario[indice_tristeza] *= 0.80   # Reduce prioridad de Tristeza
pesos_clase_diccionario[indice_sorpresa] *= 1.10   # Refuerza levemente Sorpresa

print("\nPesos finales usados:")
for i, peso in pesos_clase_diccionario.items():
    print(f"{i} ({lista_emociones[i]}): {peso:.3f}")

# ---------------------------------------------------------------------
# 4. MODELO BASE: RESNET50
# ---------------------------------------------------------------------
# Carga ResNet50 pre-entrenada con ImageNet, sin la capa de salida original
modelo_base = ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(TAMANO_IMAGEN, TAMANO_IMAGEN, 3)
)

# Congela TODAS las capas de ResNet para no alterar lo aprendido
for capa in modelo_base.layers:
    capa.trainable = False  

# CAPAS FINALES (Tu red personalizada)
x = layers.GlobalAveragePooling2D()(modelo_base.output) # Aplana los datos
x = layers.Dense(256, activation='relu')(x)             # Capa densa intermedia
x = layers.Dropout(0.5)(x)                              # Apaga 50% de neuronas (evita sobreajuste)
salida = layers.Dense(len(lista_emociones), activation='softmax')(x) # Capa final de predicción

modelo = models.Model(modelo_base.input, salida)

# Compila el modelo
modelo.compile(
    optimizer=tf.keras.optimizers.Adam(1e-4), # Tasa de aprendizaje moderada
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("\nResumen del modelo:")
modelo.summary()

# ---------------------------------------------------------------------
# 5. CALLBACKS (Herramientas de control)
# ---------------------------------------------------------------------
callbacks = [
    EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True), # Detiene si no mejora en 5 épocas
    ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-7), # Reduce velocidad si se estanca
    ModelCheckpoint("mejor_resnet50.keras", monitor="val_accuracy", save_best_only=True) # Guarda solo el mejor modelo
]

# ---------------------------------------------------------------------
# 6. FASE 1 – ENTRENAMIENTO (Transfer Learning)
# ---------------------------------------------------------------------
print("\nEntrenando FASE 1...")
modelo.fit(
    generador_entrenamiento,
    validation_data=generador_prueba,
    epochs=EPOCAS_FASE1,
    class_weight=pesos_clase_diccionario, # Aplica los pesos calculados
    callbacks=callbacks
)

# ---------------------------------------------------------------------
# 7. FASE 2 – AJUSTE FINO (Fine Tuning)
# ---------------------------------------------------------------------
print("\nIniciando Ajuste Fino (Fine-Tuning)...")

modelo_base.trainable = True # Habilita el entrenamiento del modelo base
# Vuelve a congelar todo EXCEPTO las últimas 50 capas
for capa in modelo_base.layers[:-50]:
    capa.trainable = False

# Recompila con una tasa de aprendizaje MUY baja para cambios sutiles
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
# 8. EVALUACIÓN FINAL
# ---------------------------------------------------------------------
print("\nCargando el mejor modelo guardado...")
mejor_modelo = load_model("mejor_resnet50.keras") # Carga la mejor versión obtenida

generador_prueba.reset()
predicciones = mejor_modelo.predict(generador_prueba)
clases_predichas = np.argmax(predicciones, axis=1) # Obtiene el índice de la clase más probable
clases_reales = generador_prueba.classes           # Etiquetas reales

print("\nMatriz de confusión:")
print(confusion_matrix(clases_reales, clases_predichas))

print("\nReporte de clasificación:")
print(classification_report(clases_reales, clases_predichas, target_names=lista_emociones))

# ---------------------------------------------------------------------
# 9. GUARDAR MODELO Y ETIQUETAS
# ---------------------------------------------------------------------
mejor_modelo.save("modelo_emociones_resnet50.keras")  # Guarda el archivo final del modelo
np.save("label_names.npy", np.array(lista_emociones)) # Guarda los nombres de las clases

print("\nModelo guardado exitosamente como modelo_emociones_resnet50.keras")
print("Clases guardadas como label_names.npy")