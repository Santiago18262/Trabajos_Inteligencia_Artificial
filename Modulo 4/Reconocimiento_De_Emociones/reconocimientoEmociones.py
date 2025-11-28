import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.vgg16 import preprocess_input
from pathlib import Path

# ----------------------------------------------------------------------
# CARGAR MODELO Y CLASES
# ----------------------------------------------------------------------
modelo = load_model("modelo_emociones_vgg16.h5")
nombres_clases = np.load("label_names.npy").tolist()

TAMANO_IMAGEN = 48          # o 224, según como entrenaste
ANCHO_EMOJI = 120           # tamaño del emoji (cuadrado)

clasificador_rostros = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

camara = None
camara_activa = False

# ----------------------------------------------------------------------
# CARGAR EMOJI SEGÚN EMOCIÓN
# ----------------------------------------------------------------------
def cargar_emoji(nombre_emocion):
    directorio_base = Path(__file__).parent
    directorio_emojis = directorio_base / "Emojis"

    if not directorio_emojis.exists():
        return None

    nombre = nombre_emocion.lower()
    extensiones = [".png", ".jpg", ".jpeg", ".bmp"]

    for ext in extensiones:
        archivo = directorio_emojis / f"{nombre}{ext}"
        if archivo.exists():
            img = cv2.imread(str(archivo))
            if img is not None:
                return img
    return None

# ----------------------------------------------------------------------
# PREPROCESAR ROSTRO PARA LA CNN
# ----------------------------------------------------------------------
def preprocesar_rostro(rostro_bgr, tamano=224):
    rostro_redimensionado = cv2.resize(rostro_bgr, (tamano, tamano),
                                       interpolation=cv2.INTER_CUBIC)
    rostro_rgb = cv2.cvtColor(rostro_redimensionado, cv2.COLOR_BGR2RGB)
    rostro_rgb = rostro_rgb.astype("float32")
    rostro_rgb = np.expand_dims(rostro_rgb, axis=0)
    return preprocess_input(rostro_rgb)

# ----------------------------------------------------------------------
# MOSTRAR IMAGEN EN TKINTER (CON ESCALADO)
# ----------------------------------------------------------------------
def mostrar_imagen(imagen_bgr, emocion, probabilidad):
    # Escala controlada para que se vea bien en la ventana
    max_w, max_h = 820, 470
    h, w = imagen_bgr.shape[:2]
    escala = min(max_w / w, max_h / h, 1.8)

    if escala != 1.0:
        nuevo_w = int(w * escala)
        nuevo_h = int(h * escala)
        imagen_bgr = cv2.resize(imagen_bgr, (nuevo_w, nuevo_h),
                                interpolation=cv2.INTER_AREA)

    imagen_rgb = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2RGB)
    imagen_pil = Image.fromarray(imagen_rgb)
    imagen_tk = ImageTk.PhotoImage(imagen_pil)

    label_imagen.config(image=imagen_tk)
    label_imagen.image = imagen_tk

    if emocion is None:
        label_resultado.config(text="No se detecta rostro")
    else:
        label_resultado.config(
            text=f"Emoción detectada: {emocion} ({probabilidad*100:.2f}%)"
        )

# ----------------------------------------------------------------------
# FUNCIÓN AUXILIAR: CREAR PANEL CON EMOJI CUADRADO
# ----------------------------------------------------------------------
def crear_panel_emoji(emoji_original, alto_panel):
    panel_vacio = np.zeros((alto_panel, ANCHO_EMOJI, 3), dtype=np.uint8)

    if emoji_original is None:
        return panel_vacio

    # Hacer el emoji cuadrado
    alto, ancho = emoji_original.shape[:2]
    tam = max(alto, ancho)
    cuadrado = np.ones((tam, tam, 3), dtype=np.uint8) * 255  # fondo blanco

    y_offset = (tam - alto) // 2
    x_offset = (tam - ancho) // 2
    cuadrado[y_offset:y_offset+alto, x_offset:x_offset+ancho] = emoji_original

    # Redimensionar a ANCHO_EMOJI x ANCHO_EMOJI
    emoji_red = cv2.resize(
        cuadrado,
        (ANCHO_EMOJI, ANCHO_EMOJI),
        interpolation=cv2.INTER_CUBIC
    )

    panel = panel_vacio.copy()
    offset = (alto_panel - ANCHO_EMOJI) // 2
    panel[offset:offset+ANCHO_EMOJI, :] = emoji_red

    return panel

# ----------------------------------------------------------------------
# PROCESAR FOTOGRAMA DE CÁMARA (SIN PADDING)
# ----------------------------------------------------------------------
def procesar_fotograma(fotograma):
    """
    Aquí ya NO agregamos marco/padding para alejar la imagen.
    Trabajamos directo con el frame de la cámara.
    """

    gris = cv2.cvtColor(fotograma, cv2.COLOR_BGR2GRAY)
    rostros = clasificador_rostros.detectMultiScale(
        gris, scaleFactor=1.3, minNeighbors=5
    )

    panel_vacio = np.zeros((fotograma.shape[0], ANCHO_EMOJI, 3), dtype=np.uint8)

    if len(rostros) == 0:
        return np.hstack([fotograma, panel_vacio]), None, 0.0

    (x, y, w, h) = rostros[0]
    rostro = fotograma[y:y+h, x:x+w]

    pred = modelo.predict(preprocesar_rostro(rostro, TAMANO_IMAGEN), verbose=0)
    idx = int(np.argmax(pred))
    emocion = nombres_clases[idx]
    prob = float(pred[0][idx])

    # Marco + texto (verde)
    cv2.rectangle(fotograma, (x, y), (x+w, y+h), (0, 255, 0), 3)
    cv2.putText(
        fotograma,
        f"{emocion} ({prob*100:.1f}%)",
        (x, y - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    # Emoji cuadrado
    emoji = cargar_emoji(emocion)
    panel_emoji = crear_panel_emoji(emoji, fotograma.shape[0])

    return np.hstack([fotograma, panel_emoji]), emocion, prob

# ----------------------------------------------------------------------
# PROCESAR IMAGEN DESDE ARCHIVO (CON PADDING Y ESCALADO)
# ----------------------------------------------------------------------
def procesar_imagen_archivo(img):
    # Si es pequeña (FER2013 ~48x48), escalarla primero
    if max(img.shape[:2]) < 180:
        factor = 260 / max(img.shape[:2])
        img = cv2.resize(
            img,
            (int(img.shape[1] * factor), int(img.shape[0] * factor)),
            interpolation=cv2.INTER_CUBIC
        )

    # Padding para que el marco no se corte (solo en IMÁGENES DE ARCHIVO)
    padding = 40
    img = cv2.copyMakeBorder(
        img, padding, padding, padding, padding,
        cv2.BORDER_CONSTANT, value=(0, 0, 0)   # padding negro
    )

    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rostros = clasificador_rostros.detectMultiScale(
        gris, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30)
    )

    panel_vacio = np.zeros((img.shape[0], ANCHO_EMOJI, 3), dtype=np.uint8)

    # Si no detecta rostro, usar toda la imagen
    if len(rostros) == 0:
        rostro = img
    else:
        (x, y, w, h) = rostros[0]
        rostro = img[y:y+h, x:x+w]

    pred = modelo.predict(preprocesar_rostro(rostro, TAMANO_IMAGEN), verbose=0)
    idx = int(np.argmax(pred))
    emocion = nombres_clases[idx]
    prob = float(pred[0][idx])

    # Marco + texto solo si hubo detección
    if len(rostros) != 0:
        (x, y, w, h) = rostros[0]
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
        cv2.putText(
            img,
            f"{emocion} ({prob*100:.1f}%)",
            (x, y - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    # Emoji cuadrado
    emoji = cargar_emoji(emocion)
    panel_emoji = crear_panel_emoji(emoji, img.shape[0])

    return np.hstack([img, panel_emoji]), emocion, prob

# ----------------------------------------------------------------------
# MANEJO DE CÁMARA
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
# CARGAR IMAGEN DESDE ARCHIVO
# ----------------------------------------------------------------------
def cargar_imagen():
    detener_camara()

    ruta = filedialog.askopenfilename(
        title="Selecciona una imagen",
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
# CIERRE LIMPIO
# ----------------------------------------------------------------------
def on_closing():
    detener_camara()
    ventana.destroy()

# ----------------------------------------------------------------------
# INTERFAZ TKINTER
# ----------------------------------------------------------------------
ventana = tk.Tk()
ventana.title("Reconocimiento de Emociones")
ventana.geometry("950x650")

frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=10)

btn_img = tk.Button(frame_botones, text="Cargar Imagen", command=cargar_imagen)
btn_img.grid(row=0, column=0, padx=5)

btn_cam = tk.Button(frame_botones, text="Iniciar Webcam", command=iniciar_camara)
btn_cam.grid(row=0, column=1, padx=5)

label_imagen = tk.Label(ventana)
label_imagen.pack(pady=10)

label_resultado = tk.Label(ventana, font=("Helvetica", 14))
label_resultado.pack(pady=10)

ventana.protocol("WM_DELETE_WINDOW", on_closing)
ventana.mainloop()
