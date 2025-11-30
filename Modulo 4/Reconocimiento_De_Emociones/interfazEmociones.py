# interfaz_emociones.py

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2

# Importamos SOLO la lógica desde el otro archivo
from procesamientoEmociones import procesar_fotograma, procesar_imagen_archivo

# Variables de cámara
camara = None
camara_activa = False


# ----------------------------------------------------------------------
# MOSTRAR IMAGEN EN TKINTER
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
# CÁMARA
# ----------------------------------------------------------------------
def actualizar_camara():
    global camara, camara_activa

    if not camara_activa or camara is None:
        return

    ret, frame = camara.read()
    if not ret:
        detener_camara()
        return

    # Procesamos el fotograma con la lógica importada
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
        filetypes=[("Imágenes", "*.jpg;*.jpeg;*.png")]
    )
    if not ruta:
        return

    img = cv2.imread(ruta)
    if img is None:
        messagebox.showerror("Error", "No se pudo cargar la imagen.")
        return

    # Procesamos la imagen con la lógica importada
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
