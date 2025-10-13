
# Importamos librerías necesarias para manejo de rutas y salida del programa
import os      # Permite trabajar con directorios y rutas de archivos del sistema
import sys     # Permite terminar el programa o acceder a argumentos del sistema


class PathResolver:
    """
    Clase encargada de resolver y gestionar todas las rutas necesarias
    para el sistema de recomendación de películas.

    - Identifica el directorio base donde se ejecuta el código.
    - Crea (si no existe) la carpeta 'model' para guardar archivos .pkl.
    - Busca las rutas relativas de los datasets (movies y credits).
    - Muestra mensajes informativos sobre las rutas detectadas.
    """

    def __init__(self):
        # Obtiene el directorio actual de trabajo (donde se ejecuta el script)
        self.CWD = os.getcwd()

        # ---- 0) Diagnóstico de rutas ----
        # Imprime el directorio actual para depuración
        print(f"Directorio de trabajo actual (cwd): {self.CWD}")

        try:
            # Obtiene el directorio base donde está ubicado este archivo (.py)
            self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            # Si ocurre un error (por ejemplo, en un entorno interactivo),
            # usa el directorio actual de trabajo como base
            self.BASE_DIR = self.CWD

        # Define la carpeta 'model' dentro del directorio base
        self.MODEL_DIR = os.path.join(self.BASE_DIR, "model")

        # Crea la carpeta 'model' si no existe
        os.makedirs(self.MODEL_DIR, exist_ok=True)

        # Define las rutas completas para los archivos pickle del modelo
        self.movie_list_pkl = os.path.join(self.MODEL_DIR, "movie_list.pkl")
        self.similarity_pkl = os.path.join(self.MODEL_DIR, "similarity.pkl")

        # Muestra en consola la ruta donde se guardarán los modelos
        print(f"Carpeta 'model': {self.MODEL_DIR}")

        # ---- 1) Rutas a datasets (sin usar rutas absolutas) ----
        # Define el directorio donde deberían estar los datasets
        datasets_dir = os.path.join(self.BASE_DIR, "datasets")

        # Define las rutas esperadas de los archivos CSV
        movies_path = os.path.join(datasets_dir, "tmdb_5000_movies.csv")
        credits_path = os.path.join(datasets_dir, "tmdb_5000_credits.csv")

        # Verifica si ambos archivos existen en la ruta esperada
        if not (os.path.exists(movies_path) and os.path.exists(credits_path)):
            # Si no existen, intenta buscar un nivel arriba (por si se ejecuta desde otra carpeta)
            alt_dir = os.path.join(self.BASE_DIR, "..", "datasets")

            # Crea las rutas alternativas (nivel superior)
            alt_movies = os.path.join(alt_dir, "tmdb_5000_movies.csv")
            alt_credits = os.path.join(alt_dir, "tmdb_5000_credits.csv")

            # Si los archivos existen en el nivel superior, usa esas rutas
            if os.path.exists(alt_movies) and os.path.exists(alt_credits):
                movies_path, credits_path = alt_movies, alt_credits
            else:
                # Si no se encuentran en ninguna de las ubicaciones esperadas,
                # muestra mensaje de error y termina el programa
                print("\n❌ No se encontraron los archivos CSV.")
                print("Se buscaron en:\n", datasets_dir, "\n", alt_dir)
                sys.exit(1)  # Sale del programa con código de error

        # Si todo está correcto, muestra la carpeta de donde se usarán los datasets
        print(f"📂 Usando datasets desde: {os.path.dirname(movies_path)}")

        # Guarda las rutas finales como atributos de la instancia
        self.movies_path = movies_path
        self.credits_path = credits_path

    def paths(self):
        """
        Devuelve las rutas en el mismo orden lógico usado por el script original:
        1. movie_list_pkl   → archivo .pkl con la lista de películas procesadas.
        2. similarity_pkl   → archivo .pkl con la matriz de similitudes.
        3. movies_path      → ruta del dataset tmdb_5000_movies.csv.
        4. credits_path     → ruta del dataset tmdb_5000_credits.csv.
        """
        # Retorna las cuatro rutas como tupla en el orden establecido
        return self.movie_list_pkl, self.similarity_pkl, self.movies_path, self.credits_path
