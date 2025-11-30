import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input  # importante: ResNet50
from pathlib import Path

# ----------------------------------------------------------------------
# CARGAR MODELO Y CLASES
# ----------------------------------------------------------------------
modelo = load_model(
    r"C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\modelo_emociones_resnet50.keras"
)

nombres_clases = np.load(
    r"C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\label_names.npy"
).tolist()

print("CLASES DEL MODELO:", nombres_clases)

TAMANO_IMAGEN = 96
ANCHO_EMOJI = 120

clasificador_rostros = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

camara = None
camara_activa = False


# ----------------------------------------------------------------------
# CARGAR EMOJI
# ----------------------------------------------------------------------
def cargar_emoji(nombre_emocion):
    directorio = Path(
        r"C:\USB Santiago\Semestre 7 Tec\Inteligencia Artificial\Trabajos_Inteligencia_Artificial\Modulo 4\Reconocimiento_De_Emociones\Emojis"
    )
    nombre = nombre_emocion.lower()

    for ext in (".png", ".jpg", ".jpeg", ".bmp"):
        ruta = directorio / f"{nombre}{ext}"
        if ruta.exists():
            img = cv2.imread(str(ruta))
            return img
    return None


# ----------------------------------------------------------------------
# PREPROCESAR ROSTRO
# ----------------------------------------------------------------------
def preprocesar_rostro(rostro_bgr, tamano=224):
    rostro_red = cv2.resize(rostro_bgr, (tamano, tamano))
    rostro_rgb = cv2.cvtColor(rostro_red, cv2.COLOR_BGR2RGB).astype("float32")
    rostro_rgb = np.expand_dims(rostro_rgb, axis=0)
    return preprocess_input(rostro_rgb)


# ----------------------------------------------------------------------
# MOSTRAR IMAGEN
# ----------------------------------------------------------------------
def mostrar_imagen(imagen_bgr, emocion, prob):
    max_w, max_h = 820, 470
    h, w = imagen_bgr.shape[:2]
    escala = min(max_w / w, max_h / h, 1.8)

    if escala != 1.0:
        imagen_bgr = cv2.resize(imagen_bgr, (int(w * escala), int(h * escala)))

    img_rgb = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2RGB)
    tk_img = ImageTk.PhotoImage(Image.fromarray(img_rgb))

    label_imagen.config(image=tk_img)
    label_imagen.image = tk_img

    if emocion is None:
        label_resultado.config(text="No se detecta rostro")
    else:
        label_resultado.config(text=f"Emoción detectada: {emocion} ({prob*100:.2f}%)")


# ----------------------------------------------------------------------
# EMOJI CUADRADO
# ----------------------------------------------------------------------
def crear_panel_emoji(emoji, alto_total):
    panel = np.zeros((alto_total, ANCHO_EMOJI, 3), dtype=np.uint8)

    if emoji is None:
        return panel

    h, w = emoji.shape[:2]
    tam = max(h, w)
    cuadrado = np.ones((tam, tam, 3), np.uint8) * 255

    y0 = (tam - h) // 2
    x0 = (tam - w) // 2
    cuadrado[y0:y0 + h, x0:x0 + w] = emoji

    emoji_red = cv2.resize(cuadrado, (ANCHO_EMOJI, ANCHO_EMOJI))
    offset = (alto_total - ANCHO_EMOJI) // 2
    panel[offset:offset + ANCHO_EMOJI, :] = emoji_red

    return panel


# ----------------------------------------------------------------------
# PREDICCIÓN CON REGLAS (NEUTRAL POR DEFECTO, TRISTEZA SOLO SI ES CLARA)
# ----------------------------------------------------------------------
def predecir_emocion(rostro_bgr):
    """
    Usa las probabilidades originales del modelo y aplica reglas para:
    - Usar Neutral cuando el modelo está inseguro.
    - Aceptar Tristeza solo si es claramente dominante sobre Neutral,
      pero con condiciones un poco más suaves para que salga más.
    """
    entrada = preprocesar_rostro(rostro_bgr, TAMANO_IMAGEN)
    pred = modelo.predict(entrada, verbose=0)[0]  # vector de probabilidades softmax

    # Índices de cada emoción según nombres_clases
    idx_alegria  = nombres_clases.index("Alegria")
    idx_enojo    = nombres_clases.index("Enojo")
    idx_neutral  = nombres_clases.index("Neutral")
    idx_sorpresa = nombres_clases.index("Sorpresa")
    idx_tristeza = nombres_clases.index("Tristeza")

    # Probabilidades individuales
    p_alegria  = pred[idx_alegria]
    p_enojo    = pred[idx_enojo]
    p_neutral  = pred[idx_neutral]
    p_sorpresa = pred[idx_sorpresa]
    p_tristeza = pred[idx_tristeza]

    # Mejor emoción cruda
    idx_max = np.argmax(pred)
    p_max = pred[idx_max]

    # 1) Si el modelo está inseguro → Neutral
    umbral_confianza = 0.45  # si la mejor prob < 0.45, usamos Neutral
    if p_max < umbral_confianza:
        idx = idx_neutral
    else:
        # 2) Caso especial: Tristeza
        if idx_max == idx_tristeza:
            diferencia_tristeza_neutral = p_tristeza - p_neutral

            # 🔧 Condiciones un poco más suaves para tristeza
            # Antes: p_tristeza >= 0.55 y diff >= 0.15
            # Ahora: p_tristeza >= 0.50 y diff >= 0.10
            if p_tristeza >= 0.50 and diferencia_tristeza_neutral >= 0.10:
                idx = idx_tristeza
            else:
                idx = idx_neutral
        else:
            # 3) Para el resto de emociones respetamos el ganador
            idx = idx_max

    emocion = nombres_clases[idx]
    prob = float(pred[idx])

    # Debug opcional:
    # print("Pred:", pred, " ->", emocion, prob)

    return emocion, prob



# ----------------------------------------------------------------------
# PROCESAR FOTO DE CAMARA (SIN PADDING)
# ----------------------------------------------------------------------
def procesar_fotograma(frame):
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rostros = clasificador_rostros.detectMultiScale(gris, 1.3, 5)

    panel_vacio = np.zeros((frame.shape[0], ANCHO_EMOJI, 3), dtype=np.uint8)

    if len(rostros) == 0:
        return np.hstack([frame, panel_vacio]), None, 0.0

    x, y, w, h = rostros[0]
    rostro = frame[y:y + h, x:x + w]

    emocion, prob = predecir_emocion(rostro)

    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
    cv2.putText(frame, f"{emocion} ({prob*100:.1f}%)",
                (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    panel_emoji = crear_panel_emoji(cargar_emoji(emocion), frame.shape[0])
    return np.hstack([frame, panel_emoji]), emocion, prob


# ----------------------------------------------------------------------
# PROCESAR IMAGEN DESDE ARCHIVO (CON PADDING)
# ----------------------------------------------------------------------
def procesar_imagen_archivo(img):
    if max(img.shape[:2]) < 180:
        factor = 260 / max(img.shape[:2])
        img = cv2.resize(img, (int(img.shape[1] * factor), int(img.shape[0] * factor)))

    img = cv2.copyMakeBorder(
        img, 40, 40, 40, 40,
        cv2.BORDER_CONSTANT, value=(0, 0, 0)
    )

    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rostros = clasificador_rostros.detectMultiScale(gris, 1.1, 4)

    if len(rostros) == 0:
        rostro = img
        x = y = w = h = 0
    else:
        x, y, w, h = rostros[0]
        rostro = img[y:y + h, x:x + w]

    emocion, prob = predecir_emocion(rostro)

    if len(rostros) != 0:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
        cv2.putText(img, f"{emocion} ({prob*100:.1f}%)",
                    (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    panel_emoji = crear_panel_emoji(cargar_emoji(emocion), img.shape[0])
    return np.hstack([img, panel_emoji]), emocion, prob


# ----------------------------------------------------------------------
# CÁMARA
# ----------------------------------------------------------------------
def actualizar_camara():
    if not camara_activa or camara is None:
        return

    ret, frame = camara.read()
    if not ret:
        detener_camara()
        return

    resultado, emocion, prob = procesar_fotograma(frame)
    mostrar_imagen(resultado, emocion, prob)

    ventana.after(30, actualizar_camara)


def iniciar_camara():
    global camara, camara_activa
    detener_camara()

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        messagebox.showerror("Error", "No se pudo abrir la cámara.")
        return

    camara = cap
    camara_activa = True
    actualizar_camara()


def detener_camara():
    global camara, camara_activa
    camara_activa = False
    if camara is not None:
        camara.release()
        camara = None


# ----------------------------------------------------------------------
# CARGAR IMAGEN
# ----------------------------------------------------------------------
def cargar_imagen():
    detener_camara()

    ruta = filedialog.askopenfilename(
        filetypes=[("Imágenes", "*.jpg;*.jpeg;*.png")]
    )
    if not ruta:
        return

    img = cv2.imread(ruta)
    if img is None:
        messagebox.showerror("Error", "No se pudo cargar la imagen.")
        return

    resultado, emocion, prob = procesar_imagen_archivo(img)
    mostrar_imagen(resultado, emocion, prob)


# ----------------------------------------------------------------------
# INTERFAZ TKINTER
# ----------------------------------------------------------------------
def on_closing():
    detener_camara()
    ventana.destroy()


ventana = tk.Tk()
ventana.title("Reconocimiento de Emociones")
ventana.geometry("950x650")

frame_btn = tk.Frame(ventana)
frame_btn.pack(pady=10)

tk.Button(frame_btn, text="Cargar Imagen", command=cargar_imagen).grid(row=0, column=0, padx=5)
tk.Button(frame_btn, text="Iniciar Webcam", command=iniciar_camara).grid(row=0, column=1, padx=5)

label_imagen = tk.Label(ventana)
label_imagen.pack(pady=10)

label_resultado = tk.Label(ventana, font=("Helvetica", 14))
label_resultado.pack(pady=10)

ventana.protocol("WM_DELETE_WINDOW", on_closing)
ventana.mainloop()
