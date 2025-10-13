
import re, threading  # re: expresiones regulares; threading: ejecutar carga del modelo en segundo plano
from pathlib import Path  # Manejo de rutas de archivos de forma multiplataforma
import tkinter as tk  # Tkinter base
from tkinter import filedialog, messagebox  # Diálogos para abrir archivos y mostrar mensajes
from DeteccionDeSpam import EmailSpamClassifier  # backend  # Importa el clasificador del backend
from Config_regex import URL_RE, ADJUNTO_RE, EXT_PELIGROSAS, EXT_COMUNES, es_email_valido  # Carga regex/sets/validador

# ======= Colores UI =======  # Paleta de colores para la interfaz
COLOR_BG = "#9ebbc0"  # Color de fondo general
COLOR_INPUT = "#dfdede"  # Color de fondo para entradas de texto
COLOR_TEXT = "#111827"  # Color de texto principal

# ======= Ventana principal =======  # Configuración de la ventana raíz
root = tk.Tk()  # Crea la ventana principal
root.title("Detector de Spam")  # Título de la ventana
root.geometry("500x550")  # Tamaño inicial de la ventana
root.configure(bg=COLOR_BG)  # Aplica color de fondo

status_var = tk.StringVar(value="Modelo: cargando…")  # Variable de estado para mostrar progreso de modelo
clf = None  # se asignará al cargar modelo  # Inicializa el clasificador como None (se cargará asincrónico)

# ======= Layout principal =======  # Contenedor superior para todo el contenido
main = tk.Frame(root, bg=COLOR_BG)  # Frame principal con mismo fondo
main.pack(padx=12, pady=12, fill="both", expand=True)  # Empaqueta con padding y permite expansión

# --- Formulario ---  # Sección con entradas de remitente y asunto
form = tk.Frame(main, bg=COLOR_BG)  # Contenedor del formulario
form.pack(fill="x", pady=(0, 8))  # Ocupa ancho completo con margen inferior

tk.Label(form, text="Remitente:", bg=COLOR_BG, fg=COLOR_TEXT).grid(row=0, column=0, sticky="e", padx=6, pady=6)  # Etiqueta Remitente
entry_remitente = tk.Entry(form, bg=COLOR_INPUT, fg=COLOR_TEXT, insertbackground=COLOR_TEXT)  # Campo de entrada de remitente
entry_remitente.grid(row=0, column=1, sticky="we", padx=6, pady=6)  # Ubica el Entry en la grilla y permite expandirse horizontalmente

tk.Label(form, text="Asunto:", bg=COLOR_BG, fg=COLOR_TEXT).grid(row=1, column=0, sticky="e", padx=6, pady=6)  # Etiqueta Asunto
entry_asunto = tk.Entry(form, bg=COLOR_INPUT, fg=COLOR_TEXT)  # Campo de entrada de asunto
entry_asunto.grid(row=1, column=1, sticky="we", padx=6, pady=6)  # Posiciona y permite expandirse en X

form.grid_columnconfigure(1, weight=1)  # La columna 1 (con los Entry) se expande para ocupar espacio

# --- Contenido ---  # Área de texto para el cuerpo del mensaje
tk.Label(main, text="Contenido del mensaje:", bg=COLOR_BG, fg=COLOR_TEXT).pack(anchor="w")  # Etiqueta para el Text
text_contenido = tk.Text(main, height=10, bg=COLOR_INPUT, fg=COLOR_TEXT)  # Cuadro de texto multilínea para contenido
text_contenido.pack(fill="both", expand=True, pady=(0, 8))  # Se expande y añade margen inferior

# --- Botones ---  # Barra de botones de acciones
btns = tk.Frame(main, bg=COLOR_BG)  # Contenedor de botones
btns.pack(fill="x", pady=(0, 8))  # Ocupa ancho completo con margen inferior
btn_analizar = tk.Button(btns, text="Analizar", bg="#d1d5db")  # Botón para ejecutar análisis
btn_analizar.pack(side="left", padx=4)  # Ubica el botón a la izquierda con padding
btn_abrir = tk.Button(btns, text="Abrir archivo (.txt/.eml)", bg="#d1d5db")  # Botón para abrir archivo
btn_abrir.pack(side="left", padx=4)  # Coloca a la izquierda con separación
btn_limpiar = tk.Button(btns, text="Limpiar", bg="#d1d5db")  # Botón para limpiar campos/salida
btn_limpiar.pack(side="left", padx=4)  # Posiciona a la izquierda con padding

tk.Label(main, textvariable=status_var, bg=COLOR_BG).pack(anchor="w", pady=(0, 6))  # Muestra estado del modelo (StringVar)

# --- Resultados ---  # Área de salida del análisis
tk.Label(main, text="Resultados del análisis:", bg=COLOR_BG, fg=COLOR_TEXT).pack(anchor="w")  # Título de sección resultados
out = tk.Text(main, height=10, state="disabled", bg=COLOR_INPUT, fg=COLOR_TEXT)  # Text para mostrar resultados (solo lectura)
out.pack(fill="both", expand=True)  # Se expande para ocupar espacio disponible

# ======= Funciones UI =======  # Lógica asociada a la interfaz
def analizar():  # Función que se ejecuta al presionar "Analizar"
    if clf is None:  # Si el modelo aún no está cargado
        messagebox.showinfo("Espérame tantito", "El modelo sigue cargando.")  # Aviso al usuario
        return  # Evita continuar

    remitente = entry_remitente.get().strip()  # Obtiene remitente y elimina espacios
    if not es_email_valido(remitente):  # Valida formato mínimo del email
        messagebox.showwarning("Remitente inválido", "Ingresa un correo válido (debe contener '@' y '.').")  # Advertencia
        entry_remitente.focus_set()  # Enfoca el campo
        entry_remitente.select_range(0, 'end')  # Selecciona todo para reescritura rápida
        return  # No continúa si es inválido

    asunto = entry_asunto.get().strip()  # Obtiene asunto
    contenido = text_contenido.get("1.0", "end").strip()  # Obtiene contenido del Text

    enlaces = URL_RE.findall(contenido or "")  # Busca URLs en el contenido usando regex

    # Extrae adjuntos mencionados  # Itera coincidencias y extrae nombre/extensión
    adjuntos = []
    for m in ADJUNTO_RE.finditer(contenido or ""):
        nombre = m.group("name").strip()  # Nombre completo del archivo
        ext = m.group("ext").lower()  # Extensión en minúscula
        adjuntos.append((nombre, ext))  # Agrega tupla (nombre, ext)

    adj_peligrosos = [n for (n, ext) in adjuntos if ext in EXT_PELIGROSAS]  # Filtra adjuntos peligrosos por extensión
    adj_listables = [n for (n, ext) in adjuntos if ext in (EXT_PELIGROSAS | EXT_COMUNES)]  # Adjuntos a listar (comunes+peligrosos)

    # Si tanto el asunto como el contenido del correo están vacíos,asigna "(sin contenido)" como resultado.
    # De lo contrario, llama al método 'clasificar_correo_ext' del clasificador 'clf' para determinar si el correo es SPAM o HAM, y convierte el resultado a mayúsculas.
    clasificacion = "(sin contenido)" if (not asunto and not contenido) else clf.clasificar_correo_ext(
        remitente, asunto, contenido, enlaces, adjuntos).upper()

    # Si el correo no tiene asunto ni contenido, la confianza se establece en 0.0 (ya que no hay información para evaluar).
    # De lo contrario, se obtiene la probabilidad de que el correo sea SPAM utilizando el método 'prob_spam_correo_ext' del clasificador.
    confianza = 0.0 if (not asunto and not contenido) else clf.prob_spam_correo_ext(
        remitente, asunto, contenido, enlaces, adjuntos)

    out.config(state="normal")  # Habilita edición para escribir resultados
    out.delete("1.0", "end")  # Limpia salida previa
    out.insert("end", "=== Características extraídas ===\n")  # Encabezado
    out.insert("end", f"Remitente: {remitente or '(vacío)'}\n")  # Muestra remitente
    out.insert("end", f"Asunto: {asunto or '(vacío)'}\n")  # Muestra asunto
    out.insert("end", f"Enlaces ({len(enlaces)}):\n")  # Muestra cantidad de URLs encontradas
    for u in enlaces:  # Lista cada URL
        out.insert("end", f"  - {u}\n")  # Escribe URL

    if adj_listables:  # Si hay adjuntos a listar
        out.insert("end", f"Adjuntos mencionados ({len(adj_listables)}):\n")  # Encabezado de adjuntos
        for n in adj_listables:  # Lista cada adjunto
            out.insert("end", f"  - {n}\n")  # Escribe nombre
    else:
        out.insert("end", "Adjuntos mencionados: ninguno\n")  # Indica ausencia de adjuntos

    out.insert("end", "\n=== Clasificación ===\n")  # Encabezado de clasificación
    out.insert("end", f"Resultado: {clasificacion}\n")  # Muestra etiqueta (SPAM/HAM o sin contenido)
    out.insert("end", f"Confianza SPAM (mensaje): {confianza:.2%}\n")  # Muestra probabilidad en porcentaje

    if adj_peligrosos:  # Si hubo adjuntos peligrosos
        out.insert("end", "\n⚠ Adjuntos potencialmente peligrosos detectados.\n")  # Anota advertencia en el reporte
        messagebox.showwarning("Advertencia", "Se detectaron adjuntos potencialmente peligrosos.")  # Popup de advertencia
    out.config(state="disabled")  # Vuelve a modo solo lectura

def abrir_archivo():  # Función para cargar contenido desde archivo .txt/.eml
    f = filedialog.askopenfilename(filetypes=[("Texto/EML", "*.txt *.eml"), ("Todos", "*.*")])  # Diálogo de selección
    if not f:  # Si el usuario cancela
        return  # Sale
    txt = Path(f).read_text(encoding="utf-8", errors="ignore")  # Lee el archivo como texto
    m = re.search(r"^(From|Remitente)\s*:\s*(.+)$", txt, re.IGNORECASE | re.MULTILINE)  # Busca línea de remitente
    if m:  # Si encontró remitente
        entry_remitente.delete(0, "end")  # Limpia campo
        entry_remitente.insert(0, m.group(2).strip())  # Inserta remitente encontrado
    m = re.search(r"^(Subject|Asunto)\s*:\s*(.+)$", txt, re.IGNORECASE | re.MULTILINE)  # Busca línea de asunto
    if m:  # Si encontró asunto
        entry_asunto.delete(0, "end")  # Limpia campo
        entry_asunto.insert(0, m.group(2).strip())  # Inserta asunto encontrado
    partes = re.split(r"\r?\n\r?\n", txt, maxsplit=1)  # Separa encabezados y cuerpo por línea en blanco
    cuerpo = partes[1] if len(partes) == 2 else txt  # Toma el cuerpo si existe; si no, todo el texto
    text_contenido.delete("1.0", "end")  # Limpia el Text
    text_contenido.insert("1.0", cuerpo.strip())  # Inserta el cuerpo del mensaje

def limpiar():  # Limpia todos los campos y la salida
    entry_remitente.delete(0, "end")  # Limpia remitente
    entry_asunto.delete(0, "end")  # Limpia asunto
    text_contenido.delete("1.0", "end")  # Limpia contenido
    out.config(state="normal")  # Habilita para borrar
    out.delete("1.0", "end")  # Limpia resultados
    out.config(state="disabled")  # Vuelve a solo lectura

def validar_remitente_evento(_evt=None):  # Validación al perder foco en el campo remitente
    r = entry_remitente.get().strip()  # Obtiene texto actual
    if r and not es_email_valido(r):  # Si hay texto pero formato no válido
        messagebox.showwarning("Remitente inválido", "Ingresa un correo válido (debe contener '@' y '.').")  # Advierte
        entry_remitente.focus_set()  # Regresa el foco al campo
        entry_remitente.select_range(0, 'end')  # Selecciona todo el texto

entry_remitente.bind("<FocusOut>", validar_remitente_evento)  # Vincula la validación al evento de perder foco

btn_analizar.config(command=analizar)  # Asigna función analizar al botón
btn_abrir.config(command=abrir_archivo)  # Asigna función abrir_archivo al botón
btn_limpiar.config(command=limpiar)  # Asigna función limpiar al botón

# ======= Carga del modelo (hilo en segundo plano) =======  # Evita bloquear la UI mientras se carga el modelo
def cargar_modelo():  # Función que inicializa el clasificador
    global clf  # Usará la variable global clf
    status_var.set("Modelo: Cargando…")  # Actualiza estado en la UI
    try:
        base = Path(__file__).resolve().parent  # Directorio del archivo actual
        csv_default = base / "datasets" / "spam_ham_dataset2.csv"  # Ruta por defecto del CSV
        clf = EmailSpamClassifier(csv_path=csv_default)  # Crea el clasificador con ruta al CSV
        status_var.set("Modelo: Listo ✅")  # Actualiza estado a listo
    except Exception as e:  # Si falla la carga del CSV, usa fallback
        clf = EmailSpamClassifier(csv_path="__FALTA__")  # Inicializa con dataset mínimo interno
        status_var.set("Modelo: fallback ⚠ (sin CSV)")  # Indica modo fallback en la UI
        messagebox.showwarning("Aviso", f"No se cargó el CSV real.\nUsando dataset mínimo.\n\n{e}")  # Muestra advertencia

threading.Thread(target=cargar_modelo, daemon=True).start()  # Lanza la carga en hilo daemon para no bloquear la UI

root.mainloop()  # Inicia el loop de eventos de Tkinter (mantiene la app abierta y responsiva)
