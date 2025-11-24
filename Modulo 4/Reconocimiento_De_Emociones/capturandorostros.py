import cv2
import os
import imutils

# ---------------------------------------------------------
# SELECCIONA LA EMOCIÓN A CAPTURAR
# ---------------------------------------------------------
# nombre_emocion = 'Enojo'
nombre_emocion = 'Felicidad'
# nombre_emocion = 'Sorpresa'
# nombre_emocion = 'Tristeza'

ruta_datos = 'C:\\USB Santiago\\Semestre 7 Tec\\Inteligencia Artificial\\Trabajos_Inteligencia_Artificial\\Modulo 4\\Reconocimiento_De_Emociones\\Data'
ruta_emocion = ruta_datos + '/' + nombre_emocion

# ---------------------------------------------------------
# CREAR CARPETA SI NO EXISTE
# ---------------------------------------------------------
if not os.path.exists(ruta_emocion):
    print('Carpeta creada:', ruta_emocion)
    os.makedirs(ruta_emocion)

# ---------------------------------------------------------
# INICIAR CÁMARA Y CLASIFICADOR
# ---------------------------------------------------------
captura = cv2.VideoCapture(0, cv2.CAP_DSHOW)
clasificador_rostro = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

contador = 0
modo_captura = False   # 🔥 NO inicia capturando

# ---------------------------------------------------------
# BUCLE PRINCIPAL
# ---------------------------------------------------------
while True:
    correcto, fotograma = captura.read()
    if not correcto:
        break

    fotograma = imutils.resize(fotograma, width=640)
    fotograma_gris = cv2.cvtColor(fotograma, cv2.COLOR_BGR2GRAY)
    fotograma_aux = fotograma.copy()

    rostros = clasificador_rostro.detectMultiScale(fotograma_gris, 1.3, 5)

    for (x, y, ancho, alto) in rostros:

        # Márgenes para capturar más área alrededor del rostro
        margen_x = int(0.15 * ancho)
        margen_y = int(0.25 * alto)

        x1 = max(0, x - margen_x)
        y1 = max(0, y - margen_y)
        x2 = min(fotograma.shape[1], x + ancho + margen_x)
        y2 = min(fotograma.shape[0], y + alto + margen_y)

        # Dibujar rectángulo verde
        cv2.rectangle(fotograma, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Guardar la imagen del rostro
        if modo_captura:
            rostro = fotograma_aux[y1:y2, x1:x2]
            rostro = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(ruta_emocion + f'/rostro_{contador}.jpg', rostro)
            contador += 1

    # ---------------------------------------------------------
    # TEXTOS DE INTERFAZ
    # ---------------------------------------------------------
    cv2.putText(fotograma, "Presiona 'c' para comenzar a capturar",
                (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    color_estado = (0, 255, 0) if modo_captura else (0, 0, 255)
    cv2.putText(fotograma, f"Capturando: {'SI' if modo_captura else 'NO'}",
                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_estado, 2)

    cv2.imshow('Captura de rostros', fotograma)

    tecla = cv2.waitKey(1)

    if tecla == ord('c'):
        modo_captura = True

    if tecla == 27 or contador >= 200:  # ESC o ya juntaste 200 imágenes
        break

# ---------------------------------------------------------
# FINALIZAR
# ---------------------------------------------------------
captura.release()
cv2.destroyAllWindows()
