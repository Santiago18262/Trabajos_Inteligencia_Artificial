# evaluar_modelo.py

import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import confusion_matrix, classification_report

# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

# Ruta a tu modelo .keras
RUTA_MODELO = r"C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\modelos\modelo_emociones_resnet50.keras"

# Ruta al directorio de TEST (carpeta con subcarpetas por emoción)
RUTA_TEST = r"C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\datasets\dataset(AffectNet)\test"

# Tamaño de imagen que usaste al entrenar
TAMANO_IMAGEN = (96, 96)  # <-- cambia a (224, 224) si tu ResNet trabajó a 224x224

# Modo de color que usaste al entrenar
COLOR_MODO = "rgb"  # <-- pon "rgb" si entrenaste en color

# Batch size (no afecta el resultado, solo la velocidad)
BATCH_SIZE = 32

# Si usaste preprocess_input (ResNet50, VGG16, etc.), deberías usarlo aquí también.
# Descomenta estas líneas y úsalo en el ImageDataGenerator en lugar de rescale.
from tensorflow.keras.applications.resnet50 import preprocess_input
USAR_PREPROCESS_INPUT = True  # pon False si SOLO usaste rescale=1./255

# ============================================================
# 2. CARGAR MODELO
# ============================================================

print("Cargando modelo desde:", RUTA_MODELO)
modelo = load_model(RUTA_MODELO)
print("Modelo cargado correctamente.\n")

# ============================================================
# 3. GENERADOR DE TEST (SIN SHUFFLE)
# ============================================================

if USAR_PREPROCESS_INPUT:
    test_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input
    )
else:
    test_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0
    )

test_generator = test_datagen.flow_from_directory(
    RUTA_TEST,
    target_size=TAMANO_IMAGEN,
    color_mode=COLOR_MODO,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False  # MUY IMPORTANTE para que y_true coincida con las predicciones
)

# Guardamos el mapeo índice -> etiqueta
class_indices = test_generator.class_indices
# Ordered by index (0,1,2,...)
labels = [None] * len(class_indices)
for nombre_clase, idx in class_indices.items():
    labels[idx] = nombre_clase

print("\nClases detectadas (en orden de índice):")
for i, nombre in enumerate(labels):
    print(f"{i}: {nombre}")

# ============================================================
# 4. PREDICCIONES
# ============================================================

print("\nGenerando predicciones sobre el conjunto de prueba...")
predicciones = modelo.predict(test_generator, verbose=1)

# y_pred: clase predicha (argmax)
y_pred = np.argmax(predicciones, axis=1)

# y_true: clases reales del generador
y_true = test_generator.classes

# ============================================================
# 5. MATRIZ DE CONFUSIÓN Y REPORTE
# ============================================================

from sklearn.metrics import confusion_matrix, classification_report

print("\nMatriz de Confusión:")
mat_conf = confusion_matrix(y_true, y_pred)
print(mat_conf)

print("\nReporte de clasificación:")
print(classification_report(y_true, y_pred, target_names=labels))

# ============================================================
# 6. (OPCIONAL) MOSTRAR MATRIZ DE CONFUSIÓN BONITA
# ============================================================
# Descomenta esta parte si quieres ver la matriz como imagen de calor


import matplotlib.pyplot as plt # Libreria para graficas
import seaborn as sns # Libreria para graficas avanzadas

plt.figure(figsize=(8, 6))
sns.heatmap(mat_conf, annot=True, fmt="d", xticklabels=labels, yticklabels=labels)
plt.xlabel("Predicción")
plt.ylabel("Real")
plt.title("Matriz de Confusión")
plt.tight_layout()
plt.show()

