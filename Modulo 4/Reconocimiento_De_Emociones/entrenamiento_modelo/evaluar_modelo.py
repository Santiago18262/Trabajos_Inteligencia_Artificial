import os  # Permite al código navegar por las carpetas para buscar las fotos
import numpy as np  # Necesario para convertir las imágenes en números que la IA entienda

from tensorflow.keras.models import load_model  # Abre el archivo .keras guardado para usarlo
from tensorflow.keras.preprocessing.image import ImageDataGenerator  # Carga las imágenes de prueba y ajusta sus valores 

from sklearn.metrics import confusion_matrix, classification_report  # Herramientas estadísticas para calificar qué tan bien funciona tu modelo

# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

# Ruta de tu modelo entrenado
RUTA_MODELO = r"C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\modelos\modelo_emociones_resnet50.keras"

# Ruta de las imágenes de prueba
RUTA_TEST = r"C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\datasets\dataset(AffectNet)\test"

TAMANO_IMAGEN = (96, 96)  # Debe ser igual al tamaño usado en entrenamiento
COLOR_MODO = "rgb"        # Modo de color (3 canales)
BATCH_SIZE = 32           # Imágenes procesadas por lote

# Importar preprocesamiento específico de ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
USAR_PREPROCESS_INPUT = True  # True para usar la función de ResNet, False para rescale normal

# ============================================================
# 2. CARGAR MODELO
# ============================================================

print("Cargando modelo desde:", RUTA_MODELO)
modelo = load_model(RUTA_MODELO) # Carga la arquitectura y pesos en memoria
print("Modelo cargado correctamente.\n")

# ============================================================
# 3. GENERADOR DE TEST (SIN SHUFFLE)
# ============================================================

if USAR_PREPROCESS_INPUT:
    test_datagen = ImageDataGenerator(preprocessing_function=preprocess_input) # Preprocesamiento avanzado
else:
    test_datagen = ImageDataGenerator(rescale=1.0 / 255.0) # Normalización simple (0 a 1)

test_generator = test_datagen.flow_from_directory(
    RUTA_TEST,
    target_size=TAMANO_IMAGEN, # Redimensiona las fotos
    color_mode=COLOR_MODO,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False  # No desordenar para poder comparar
)

# Guardar nombres de las clases
class_indices = test_generator.class_indices
labels = [None] * len(class_indices) # Crear lista vacía
for nombre_clase, idx in class_indices.items():
    labels[idx] = nombre_clase # Asignar nombre al índice correcto

print("\nClases detectadas (en orden de índice):")
for i, nombre in enumerate(labels):
    print(f"{i}: {nombre}")

# ============================================================
# 4. PREDICCIONES
# ============================================================

print("\nGenerando predicciones sobre el conjunto de prueba...")
predicciones = modelo.predict(test_generator, verbose=1) # El modelo predice probabilidades

y_pred = np.argmax(predicciones, axis=1) # Obtiene el índice de la clase más probable
y_true = test_generator.classes          # Obtiene las etiquetas reales (correctas)

# ============================================================
# 5. MATRIZ DE CONFUSIÓN Y REPORTE
# ============================================================

print("\nMatriz de Confusión:")
mat_conf = confusion_matrix(y_true, y_pred) # Cruza datos reales vs predichos
print(mat_conf)

print("\nReporte de clasificación:")
print(classification_report(y_true, y_pred, target_names=labels)) # Muestra precisión, recall y F1

# ============================================================
# 6. MOSTRAR MATRIZ DE CONFUSIÓN (GRÁFICA)
# ============================================================

import matplotlib.pyplot as plt 
import seaborn as sns 

plt.figure(figsize=(8, 6)) # Tamaño de la figura
sns.heatmap(mat_conf, annot=True, fmt="d", xticklabels=labels, yticklabels=labels, cmap="Blues") # Mapa con tonalidades azules
plt.xlabel("Predicción")
plt.ylabel("Real")
plt.title("Matriz de Confusión")
plt.tight_layout() # Ajusta márgenes
plt.show() # Muestra la ventana