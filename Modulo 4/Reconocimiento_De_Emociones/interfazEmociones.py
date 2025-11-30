import tkinter as tk  # Para crear la interfaz 
from tkinter import filedialog, messagebox # Para abrir archivos y mostrar alertas
from PIL import Image, ImageTk # Para manejar imágenes en la interfaz
import cv2 # OpenCV para video e imágenes

# Importamos solo la lógica desde el otro archivo
from procesamientoEmociones import procesar_fotograma, procesar_imagen_archivo

# Variables globales de control de la cámara
camara = None
camara_activa = False

# ----------------------------------------------------------------------
# MOSTRAR IMAGEN EN TKINTER
# ----------------------------------------------------------------------
def mostrar_imagen(imagen_bgr, emocion, prob):
    max_w, max_h = 820, 470 # Dimensiones máximas permitidas en pantalla
    h, w = imagen_bgr.shape[:2] # Obtiene alto y ancho original
    
    # Calcula la escala para ajustar la imagen sin deformarla
    escala = min(max_w / w, max_h / h, 1.8)

    if escala != 1.0:
        # Redimensiona la imagen si es necesario
        imagen_bgr = cv2.resize(imagen_bgr, (int(w * escala), int(h * escala)))

    # Convierte de BGR (OpenCV) a RGB (Compatible con Tkinter)
    img_rgb = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2RGB)
    tk_img = ImageTk.PhotoImage(Image.fromarray(img_rgb)) # Crea objeto de imagen Tk

    label_imagen.config(image=tk_img) # Actualiza la etiqueta con la nueva foto
    label_imagen.image = tk_img       # Guarda una referencia para evitar que se borre

    if emocion is None:
        label_resultado.config(text="No se detecta rostro") # Texto si no hay cara
    else:
        # Muestra emoción y porcentaje de certeza
        label_resultado.config(text=f"Emoción detectada: {emocion} ({prob*100:.2f}%)")

# ----------------------------------------------------------------------
# CÁMARA
# ----------------------------------------------------------------------
def actualizar_camara():
    global camara, camara_activa

    if not camara_activa or camara is None:
        return # Sale si la cámara está apagada

    ret, frame = camara.read() # Lee un fotograma de la webcam
    if not ret:
        detener_camara() # Si falla, apaga todo
        return

    # Envía el fotograma a procesar (detectar cara y emoción)
    resultado, emocion, prob = procesar_fotograma(frame)
    mostrar_imagen(resultado, emocion, prob) # Muestra el resultado en pantalla

    ventana.after(30, actualizar_camara) # Se vuelve a llamar a sí misma en 30ms (bucle)

def iniciar_camara():
    global camara, camara_activa
    detener_camara() # Asegura que no haya otra cámara abierta antes

    # Abre la cámara (índice 0). CAP_DSHOW optimiza el inicio en Windows
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        messagebox.showerror("Error", "No se pudo abrir la cámara.") # Alerta de error
        return

    camara = cap
    camara_activa = True
    actualizar_camara() # Inicia el bucle de lectura

def detener_camara():
    global camara, camara_activa
    camara_activa = False # Baja la bandera de actividad
    if camara is not None:
        camara.release() # Libera el recurso de hardware
        camara = None

# ----------------------------------------------------------------------
# CARGAR IMAGEN DESDE ARCHIVO
# ----------------------------------------------------------------------
def cargar_imagen():
    detener_camara() # Apaga la cámara para ver la foto estática

    # Abre explorador de archivos para elegir imagen
    ruta = filedialog.askopenfilename(
        filetypes=[("Imágenes", "*.jpg;*.jpeg;*.png")]
    )
    if not ruta:
        return # Si cancela, no hace nada

    img = cv2.imread(ruta) # Lee la imagen con OpenCV
    if img is None:
        messagebox.showerror("Error", "No se pudo cargar la imagen.")
        return

    # Procesa la imagen estática
    resultado, emocion, prob = procesar_imagen_archivo(img)
    mostrar_imagen(resultado, emocion, prob) # Muestra resultado


# ----------------------------------------------------------------------
# INTERFAZ TKINTER
# ----------------------------------------------------------------------
def on_closing():
    detener_camara() # Libera cámara antes de salir
    ventana.destroy() # Cierra la ventana

ventana = tk.Tk() # Crea ventana principal
ventana.title("Reconocimiento de Emociones") # Título
ventana.geometry("950x650") # Tamaño inicial

frame_btn = tk.Frame(ventana) # Contenedor para botones
frame_btn.pack(pady=10) # Espacio vertical

# Botones de control
tk.Button(frame_btn, text="Cargar Imagen", command=cargar_imagen).grid(row=0, column=0, padx=5)
tk.Button(frame_btn, text="Iniciar Webcam", command=iniciar_camara).grid(row=0, column=1, padx=5)

label_imagen = tk.Label(ventana) # Etiqueta donde se verá la imagen/video
label_imagen.pack(pady=10)

label_resultado = tk.Label(ventana, font=("Helvetica", 14)) # Etiqueta de texto (Emoción)
label_resultado.pack(pady=10)

ventana.protocol("WM_DELETE_WINDOW", on_closing) # Acción al cerrar con la X
ventana.mainloop() # Inicia el bucle principal de la interfaz