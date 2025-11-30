import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input  # Importante: Preprocesamiento de ResNet50
from pathlib import Path

# ----------------------------------------------------------------------
# CARGAR MODELO Y CLASES
# ----------------------------------------------------------------------
# Carga el modelo entrenado desde la ruta especificada
modelo = load_model(
    r"C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\modelos\modelo_emociones_resnet50.keras"
)

# Carga la lista de nombres de emociones guardada
nombres_clases = np.load(
    r"C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\modelos\label_names.npy"
).tolist()

print("CLASES DEL MODELO:", nombres_clases)

TAMANO_IMAGEN = 96   # Tamaño esperado por la red neuronal
ANCHO_EMOJI = 120    # Ancho del panel lateral para mostrar emojis

# Carga el detector de rostros pre-entrenado de OpenCV (Haar Cascade)
clasificador_rostros = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)


# ----------------------------------------------------------------------
# CARGAR EMOJI
# ----------------------------------------------------------------------
def cargar_emoji(nombre_emocion):
    # Define la carpeta donde están las imágenes de emojis
    directorio = Path(
        r"C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\Emojis"
    )
    nombre = nombre_emocion.lower() # Convierte el nombre a minúsculas

    # Busca la imagen con diferentes extensiones posibles
    for ext in (".png", ".jpg", ".jpeg", ".bmp"):
        ruta = directorio / f"{nombre}{ext}"
        if ruta.exists():
            img = cv2.imread(str(ruta)) # Lee la imagen si existe
            return img
    return None # Retorna vacío si no encuentra nada

# ----------------------------------------------------------------------
# PREPROCESAR ROSTRO
# ----------------------------------------------------------------------
def preprocesar_rostro(rostro_bgr, tamano=224):
    rostro_red = cv2.resize(rostro_bgr, (tamano, tamano)) # Ajusta tamaño
    rostro_rgb = cv2.cvtColor(rostro_red, cv2.COLOR_BGR2RGB).astype("float32") # Convierte a RGB y decimales
    rostro_rgb = np.expand_dims(rostro_rgb, axis=0) # Agrega dimensión de lote (1, 96, 96, 3)
    return preprocess_input(rostro_rgb) # Aplica normalización de ResNet

# ----------------------------------------------------------------------
# EMOJI CUADRADO
# ----------------------------------------------------------------------
def crear_panel_emoji(emoji, alto_total):
    # Crea un panel negro vacío del alto de la imagen principal
    panel = np.zeros((alto_total, ANCHO_EMOJI, 3), dtype=np.uint8)

    if emoji is None:
        return panel # Si no hay emoji, devuelve panel negro

    h, w = emoji.shape[:2]
    tam = max(h, w)
    # Crea un cuadrado blanco para centrar el emoji (evita deformación)
    cuadrado = np.ones((tam, tam, 3), np.uint8) * 255

    y0 = (tam - h) // 2
    x0 = (tam - w) // 2
    cuadrado[y0:y0 + h, x0:x0 + w] = emoji # Pega el emoji en el centro

    # Redimensiona el cuadrado al ancho deseado
    emoji_red = cv2.resize(cuadrado, (ANCHO_EMOJI, ANCHO_EMOJI))
    
    # Centra verticalmente el emoji en el panel negro
    offset = (alto_total - ANCHO_EMOJI) // 2
    panel[offset:offset + ANCHO_EMOJI, :] = emoji_red

    return panel

# ----------------------------------------------------------------------
# PREDICCIÓN CON REGLAS (NEUTRAL POR DEFECTO)
# ----------------------------------------------------------------------
def predecir_emocion(rostro_bgr):
    """
    Predice la emoción y aplica filtros para evitar cambios bruscos o errores.
    Prioriza 'Neutral' si la confianza es baja.
    """
    entrada = preprocesar_rostro(rostro_bgr, TAMANO_IMAGEN)
    pred = modelo.predict(entrada, verbose=0)[0]  # Obtiene probabilidades del modelo

    # Índices de cada emoción en la lista de clases
    idx_alegria  = nombres_clases.index("Alegria")
    idx_enojo    = nombres_clases.index("Enojo")
    idx_neutral  = nombres_clases.index("Neutral")
    idx_sorpresa = nombres_clases.index("Sorpresa")
    idx_tristeza = nombres_clases.index("Tristeza")

    # Extrae probabilidades individuales
    p_alegria  = pred[idx_alegria]
    p_enojo    = pred[idx_enojo]
    p_neutral  = pred[idx_neutral]
    p_sorpresa = pred[idx_sorpresa]
    p_tristeza = pred[idx_tristeza]

    # Encuentra la emoción con mayor probabilidad bruta
    idx_max = np.argmax(pred)
    p_max = pred[idx_max]

    # 1) Si la confianza máxima es baja, asumimos Neutral
    umbral_confianza = 0.45  # Menos de 45% de seguridad = Neutral
    if p_max < umbral_confianza:
        idx = idx_neutral
    else:
        # 2) Regla especial para Tristeza (suele confundirse con Neutral)
        if idx_max == idx_tristeza:
            diferencia_tristeza_neutral = p_tristeza - p_neutral

            # Solo aceptamos tristeza si supera a neutral por un margen decente
            if p_tristeza >= 0.50 and diferencia_tristeza_neutral >= 0.10:
                idx = idx_tristeza
            else:
                idx = idx_neutral # Si es dudoso, mejor decir Neutral
        else:
            # 3) Para el resto (Alegría, Enojo, Sorpresa), confiamos en el modelo
            idx = idx_max

    emocion = nombres_clases[idx] # Nombre final
    prob = float(pred[idx])       # Probabilidad final

    return emocion, prob

# ----------------------------------------------------------------------
# PROCESAR FOTO DE CAMARA (SIN PADDING EXTRA)
# ----------------------------------------------------------------------
def procesar_fotograma(frame):
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Pasa a escala de grises
    rostros = clasificador_rostros.detectMultiScale(gris, 1.3, 5) # Detecta caras

    # Panel vacío por si no hay caras
    panel_vacio = np.zeros((frame.shape[0], ANCHO_EMOJI, 3), dtype=np.uint8)

    if len(rostros) == 0:
        return np.hstack([frame, panel_vacio]), None, 0.0 # Devuelve imagen sin cambios

    x, y, w, h = rostros[0] # Toma el primer rostro encontrado
    rostro = frame[y:y + h, x:x + w] # Recorta la cara

    emocion, prob = predecir_emocion(rostro) # Predice la emoción

    # Dibuja rectángulo y texto sobre la cara original
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
    cv2.putText(frame, f"{emocion} ({prob*100:.1f}%)",
                (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Crea el panel con el emoji correspondiente y lo pega al lado
    panel_emoji = crear_panel_emoji(cargar_emoji(emocion), frame.shape[0])
    return np.hstack([frame, panel_emoji]), emocion, prob

# ----------------------------------------------------------------------
# PROCESAR IMAGEN DESDE ARCHIVO (CON MARCO NEGRO / PADDING)
# ----------------------------------------------------------------------
def procesar_imagen_archivo(img):
    # Si la imagen es muy pequeña, la agranda para facilitar la detección
    if max(img.shape[:2]) < 180:
        factor = 260 / max(img.shape[:2])
        img = cv2.resize(img, (int(img.shape[1] * factor), int(img.shape[0] * factor)))

    # Agrega un marco negro alrededor para que detecte caras en los bordes
    img = cv2.copyMakeBorder(
        img, 40, 40, 40, 40,
        cv2.BORDER_CONSTANT, value=(0, 0, 0)
    )

    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rostros = clasificador_rostros.detectMultiScale(gris, 1.1, 4)

    # Si no detecta nada, usa toda la imagen como "rostro"
    if len(rostros) == 0:
        rostro = img
        x = y = w = h = 0
    else:
        x, y, w, h = rostros[0]
        rostro = img[y:y + h, x:x + w]

    emocion, prob = predecir_emocion(rostro)

    # Dibuja si encontró rostro con detector
    if len(rostros) != 0:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
        cv2.putText(img, f"{emocion} ({prob*100:.1f}%)",
                    (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Agrega el panel lateral con el emoji
    panel_emoji = crear_panel_emoji(cargar_emoji(emocion), img.shape[0])
    return np.hstack([img, panel_emoji]), emocion, prob