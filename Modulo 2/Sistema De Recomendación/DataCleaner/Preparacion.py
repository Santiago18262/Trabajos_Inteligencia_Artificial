
# ------------------------------------------------------------
# Importación de librerías necesarias
# ------------------------------------------------------------
import ast                    # Permite evaluar cadenas que contienen estructuras Python (listas, dicts, etc.)
import pandas as pd           # Librería para manipulación de datos en DataFrames


class MoviePreprocessor:
    """
    Clase que aplica las mismas transformaciones del script original,
    pero estructuradas en métodos reutilizables y más claros.

    Su objetivo es limpiar, transformar y preparar el dataset
    de películas para que sea utilizable en el modelo de recomendación.
    """

    # --------------------------------------------------------
    # Funciones auxiliares (estáticas)
    # --------------------------------------------------------

    @staticmethod
    def safe_literal_list(text):
        """
        Convierte una cadena con estructura tipo lista de diccionarios
        (por ejemplo: "[{'id': 28, 'name': 'Action'}, ...]") en una lista
        de nombres. Devuelve [] si hay error o valor nulo.
        """
        try:
            # Si el valor es NaN, devuelve lista vacía
            if pd.isna(text):
                return []
            # Convierte el texto a lista de Python usando ast.literal_eval
            data = ast.literal_eval(text)
            out = []
            # Extrae los valores de la clave 'name' de cada diccionario
            for it in data:
                name = it.get('name') if isinstance(it, dict) else None
                if name:
                    out.append(str(name))
            return out
        except Exception:
            # Si algo falla (por formato inválido, etc.), devuelve lista vacía
            return []

    @staticmethod
    def safe_literal_top3_cast(text):
        """
        Convierte el texto del reparto (cast) en una lista con
        los nombres de los tres primeros actores principales.
        Si hay error o valor nulo, devuelve [].
        """
        try:
            if pd.isna(text):
                return []
            data = ast.literal_eval(text)
            out = []
            # Recorre hasta 3 actores como máximo
            for i, it in enumerate(data):
                if i >= 3:
                    break
                name = it.get('name') if isinstance(it, dict) else None
                if name:
                    out.append(str(name))
            return out
        except Exception:
            return []

    @staticmethod
    def safe_literal_director(text):
        """
        Extrae el nombre del director desde la columna 'crew',
        buscando el diccionario cuyo 'job' sea 'Director'.
        Si hay error o valor nulo, devuelve [].
        """
        try:
            if pd.isna(text):
                return []
            data = ast.literal_eval(text)
            out = []
            # Busca en cada elemento del crew al director
            for it in data:
                if isinstance(it, dict) and it.get('job') == 'Director' and it.get('name'):
                    out.append(str(it['name']))
            return out
        except Exception:
            return []

    @staticmethod
    def collapse(L):
        """
        Elimina los espacios dentro de cada elemento de una lista.
        Ejemplo: ['Science Fiction'] -> ['ScienceFiction']
        """
        return [str(i).replace(" ", "") for i in L]

    @staticmethod
    def empty_row(r):
        """
        Determina si una fila del DataFrame está vacía después del preprocesamiento.
        Devuelve True si todas las listas (overview, genres, keywords, cast, crew)
        están vacías.
        """
        # Suma las longitudes de cada campo, si todo da 0 -> fila vacía
        return (len(r['overview']) + len(r['genres']) +
                len(r['keywords']) + len(r['cast']) + len(r['crew'])) == 0

    # --------------------------------------------------------
    # Método principal de limpieza y transformación
    # --------------------------------------------------------
    @classmethod
    def apply_all(cls, movies_df):
        """
        Ejecuta toda la secuencia de limpieza y transformación sobre
        el DataFrame original de películas.

        Devuelve:
          - movies_clean → DataFrame con las columnas originales limpias (listas).
          - new_df → DataFrame reducido con columnas ['movie_id', 'title', 'tags'].
        """
        # Crea una copia del DataFrame original para no modificarlo directamente
        movies = movies_df.copy()

        # Rellena los valores faltantes (NaN) en la columna 'overview' con cadena vacía
        movies['overview'] = movies['overview'].fillna('')

        # ----------------------------------------------------
        # Aplica las funciones de conversión seguras a cada columna
        # ----------------------------------------------------
        movies['genres']   = movies['genres'].apply(cls.safe_literal_list)
        movies['keywords'] = movies['keywords'].apply(cls.safe_literal_list)
        movies['cast']     = movies['cast'].apply(cls.safe_literal_top3_cast)
        movies['crew']     = movies['crew'].apply(cls.safe_literal_director)

        # Tokeniza la sinopsis (overview) dividiéndola por espacios
        movies['overview'] = movies['overview'].apply(lambda x: str(x).split())

        # ----------------------------------------------------
        # Normaliza los textos: elimina espacios dentro de las palabras
        # ----------------------------------------------------
        movies['cast']     = movies['cast'].apply(cls.collapse)
        movies['crew']     = movies['crew'].apply(cls.collapse)
        movies['genres']   = movies['genres'].apply(cls.collapse)
        movies['keywords'] = movies['keywords'].apply(cls.collapse)

        # ----------------------------------------------------
        # Filtra filas vacías para evitar vectores nulos
        # ----------------------------------------------------
        before = len(movies)  # Número de filas antes del filtrado
        movies = movies[~movies.apply(cls.empty_row, axis=1)].copy()  # Elimina las filas vacías
        after = len(movies)   # Número de filas después
        print(f"Filas totales: {before} | Filas útiles tras limpieza: {after}")

        # ----------------------------------------------------
        # Genera la columna 'tags' combinando todas las listas de información
        # ----------------------------------------------------
        movies['tags'] = (movies['overview'] + movies['genres'] +
                          movies['keywords'] + movies['cast'] + movies['crew'])

        # Crea un nuevo DataFrame con solo las columnas necesarias
        new = movies[['movie_id', 'title', 'tags']].copy()

        # Une los elementos de cada lista en una sola cadena separada por espacios
        new['tags'] = new['tags'].apply(lambda x: " ".join(x))

        # Devuelve ambos DataFrames: el completo y el simplificado
        return movies, new
