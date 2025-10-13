
# ------------------------------------------------------------
# Importación de librerías necesarias
# ------------------------------------------------------------
import os                           # Para manejo de rutas y tamaños de archivos
import pickle                       # Para guardar y cargar objetos serializados (.pkl)
import pandas as pd                 # Para manipulación de datos en estructuras tipo DataFrame
from sklearn.feature_extraction.text import CountVectorizer  # Convierte texto a vectores numéricos
from sklearn.metrics.pairwise import cosine_similarity       # Calcula similitud entre vectores

# ------------------------------------------------------------
# Importación de módulos personalizados del proyecto
# ------------------------------------------------------------
from Config_paths import PathResolver         # Gestiona rutas de archivos y directorios
from Preparacion import MoviePreprocessor     # Encapsula la limpieza y preparación de datos


class ModelBuilder:
    """
    Clase que ejecuta el pipeline completo de construcción del modelo de recomendación.
    
    Mantiene la misma lógica, pasos y mensajes impresos que el script original,
    pero de manera modular y estructurada en una clase.
    """

    def __init__(self):
        # Crea una instancia de PathResolver para obtener las rutas necesarias
        self.resolver = PathResolver()

        # Desempaqueta las rutas devueltas por el método paths():
        # - movie_list_pkl: ruta donde se guardará el archivo .pkl de películas
        # - similarity_pkl: ruta donde se guardará el archivo .pkl de similitud
        # - movies_path: ruta del CSV de películas (tmdb_5000_movies.csv)
        # - credits_path: ruta del CSV de créditos (tmdb_5000_credits.csv)
        (self.movie_list_pkl,
         self.similarity_pkl,
         self.movies_path,
         self.credits_path) = self.resolver.paths()


    def build_and_save(self):
        """
        Ejecuta paso a paso la construcción del modelo:
        1. Carga los datasets.
        2. Realiza el merge entre movies y credits.
        3. Aplica limpieza y transformación con MoviePreprocessor.
        4. Vectoriza los textos y calcula la matriz de similitud.
        5. Guarda los resultados en archivos .pkl.
        """

        # --------------------------------------------------------
        # 1) Cargar CSVs originales (películas y créditos)
        # --------------------------------------------------------
        movies = pd.read_csv(self.movies_path)   # Carga el dataset principal de películas
        credits = pd.read_csv(self.credits_path) # Carga el dataset de créditos
        print("Películas:", movies.shape, " | Créditos:", credits.shape)  # Imprime tamaño de ambos

        # --------------------------------------------------------
        # 2) Merge entre ambos datasets por la columna 'title'
        # --------------------------------------------------------
        movies = movies.merge(credits, on='title', how='inner')  # Une ambos datasets
        # Selecciona solo las columnas relevantes para el modelo
        movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']].copy()

        # --------------------------------------------------------
        # 3) Limpieza y transformación de datos
        # --------------------------------------------------------
        # Aplica la preparación definida en MoviePreprocessor (procesa campos de texto, listas, etc.)
        # Devuelve dos DataFrames: uno limpio (movies_clean) y otro reducido (new) con 'tags' combinadas
        movies_clean, new = MoviePreprocessor.apply_all(movies)

        # --------------------------------------------------------
        # 4) Vectorización y cálculo de similitud
        # --------------------------------------------------------
        # Convierte los textos en vectores numéricos de conteo de palabras
        cv = CountVectorizer(max_features=5000, stop_words='english')
        vector = cv.fit_transform(new['tags']).toarray()  # Matriz de características

        # Calcula la similitud entre las películas usando la similitud del coseno
        similarity = cosine_similarity(vector)
        print("Vector shape:", vector.shape, " | Similarity shape:", similarity.shape)

        # --------------------------------------------------------
        # 5) Guardado de modelos en archivos pickle
        # --------------------------------------------------------
        # Guarda el DataFrame reducido (new) con movie_id, title y tags
        with open(self.movie_list_pkl, 'wb') as f:
            pickle.dump(new, f)
        # Muestra confirmación con el tamaño del archivo
        print(f"✔ Guardado: {self.movie_list_pkl} ({os.path.getsize(self.movie_list_pkl)} bytes)")

        # Guarda la matriz de similitud para uso en la app Streamlit
        with open(self.similarity_pkl, 'wb') as f:
            pickle.dump(similarity, f)
        print(f"✔ Guardado: {self.similarity_pkl} ({os.path.getsize(self.similarity_pkl)} bytes)")

        # --------------------------------------------------------
        # 6) Mensaje final de éxito
        # --------------------------------------------------------
        print("\n✅ Archivos generados correctamente.")
        print("Importante: en tu app lee usando la MISMA ruta absoluta mostrada arriba.")
