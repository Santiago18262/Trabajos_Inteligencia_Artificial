import os, re, unicodedata
from pathlib import Path
import numpy as np, pandas as pd, nltk
from sklearn.feature_extraction.text import TfidfVectorizer

from Config_regex import URL_RE, ADJUNTO_RE, EXT_PELIGROSAS, EXT_COMUNES

def quitar_acentos(t: str) -> str:
    t = unicodedata.normalize('NFKD', t)
    return t.encode('ascii', 'ignore').decode('utf-8')

def limpiar_texto(t: str) -> str:
    t = (t or "").lower().strip()
    t = quitar_acentos(t)
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def dominio_de_email(remitente: str) -> str:
    r = (remitente or "").strip().lower()
    if "@" in r:
        return r.split("@", 1)[-1]
    return ""

def tokens_dominio(dom: str) -> list[str]:
    """
    Convierte un dominio 'sub.dom.tld' en tokens útiles:
    from_dom_dom, from_sub_sub, from_tld_tld
    """
    if not dom:
        return []
    dom = dom.replace("-", " ")
    partes = dom.split(".")
    toks = []
    if len(partes) >= 1:
        toks.append(f"from_dom_{limpiar_texto(partes[-2] if len(partes)>=2 else partes[0])}")
    if len(partes) >= 2:
        toks.append(f"from_tld_{limpiar_texto(partes[-1])}")
    if len(partes) >= 3:
        toks.append(f"from_sub_{limpiar_texto(partes[0])}")
    return toks

def extraer_enlaces(texto: str) -> list[str]:
    return URL_RE.findall(texto or "")

def tokens_enlace(url: str) -> list[str]:
    """
    A partir de una URL genera tokens de dominio/tld generales.
    """
    toks = ["has_url"]
    try:
        # Extraer dominio de forma simple
        m = re.search(r"https?://([^/\s:]+)", url, re.I)
        if not m:
            return toks
        host = m.group(1).lower()
        host = host.replace("www.", "")
        partes = host.split(".")
        if len(partes) >= 1:
            toks.append(f"url_dom_{limpiar_texto(partes[-2] if len(partes)>=2 else partes[0])}")
        if len(partes) >= 2:
            toks.append(f"url_tld_{limpiar_texto(partes[-1])}")
        if len(partes) >= 3:
            toks.append(f"url_sub_{limpiar_texto(partes[0])}")
    except Exception:
        pass
    return toks

def extraer_adjuntos(texto: str) -> list[tuple[str,str]]:
    adjuntos = []
    for m in ADJUNTO_RE.finditer(texto or ""):
        nombre = (m.group("name") or "").strip()
        ext = (m.group("ext") or "").lower().strip()
        if nombre and ext:
            adjuntos.append((nombre, ext))
    return adjuntos

def tokens_adjuntos(adjuntos: list[tuple[str,str]]) -> list[str]:
    toks = []
    if adjuntos:
        toks.append("has_attachment")
    for nombre, ext in adjuntos:
        # extensión
        toks.append(f"att_ext_{ext}")
        if ext in EXT_PELIGROSAS:
            toks.append("att_ext_dangerous")
        # palabras del nombre (separar por no-alfa)
        base = limpiar_texto(re.sub(r"\.[a-z0-9]{1,6}$", "", nombre, flags=re.I))
        if base:
            for w in base.split():
                # evita palabras demasiado cortas
                if len(w) >= 3:
                    toks.append(f"att_name_{w}")
    return toks


class EmailSpamClassifier:
    """
    Clasificador Naive Bayes multinomial sobre TF-IDF.
    Ahora incorpora tokens de:
      - remitente (dominio, tld, subdominio)
      - asunto
      - contenido
      - enlaces (dominio, tld, subdominio, has_url)
      - adjuntos (has_attachment, att_ext_*, att_ext_dangerous, att_name_*)
    """

    def __init__(self, csv_path=None):
        # Recursos NLTK (idempotente)
        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords")
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")

        self.precision = 0.0
        self.recall_spam = 0.0

        # Ruta por defecto
        if csv_path is None:
            try:
                base = Path(__file__).resolve().parent
            except NameError:
                base = Path(os.getcwd())
            csv_path = base / "datasets" / "spam_ham_dataset2.csv"

        self.csv_path = Path(csv_path)

        # Cargar dataset o fallback
        if self.csv_path.exists():
            df = pd.read_csv(self.csv_path)
        else:
            df = pd.DataFrame({
                "remitente": [
                    "promos@casino-oro.fun",
                    "maria.garcia@empresa.com",
                    "soporte@seguridadbancaria-alerta.com",
                    "contabilidad@empresa.com",
                ],
                "asunto": [
                    "100 tiradas gratis sin depósito",
                    "Reunión semanal del equipo",
                    "Verifica tu cuenta urgente",
                    "Reporte mensual",
                ],
                "mensaje": [
                    "Regístrate y gana premios al instante. premios.bat",  # añadimos .bat aquí
                    "Nos vemos mañana 10:00 sala de juntas. reporte.pdf",
                    "Detectamos actividad inusual. Confirma tus datos. verificar-cuenta.cmd",
                    "Envío el reporte mensual consolidado. balance.xlsx",
                ],
                "enlaces": [
                    "https://casino-oro.fun/oferta",
                    "",
                    "https://seguridadbancaria-alerta.com/verificar-cuenta",
                    "",
                ],
                "etiqueta": ["spam", "ham", "spam", "ham"],
            })

        if "etiqueta" not in df.columns:
            raise ValueError("El CSV debe contener la columna 'etiqueta' con valores 'spam' o 'ham'.")

        df["remitente"] = df.get("remitente", "").astype(str)
        df["asunto"]    = df.get("asunto", "").astype(str)
        df["mensaje"]   = df.get("mensaje", "").astype(str)
        df["enlaces"]   = df.get("enlaces", "").astype(str)
        df["etiqueta"]  = df["etiqueta"].astype(str).str.lower().str.strip()

        # Construcción de CORPUS enriquecido por fila
        rows = []
        for _, r in df.iterrows():
            remitente = r["remitente"]
            asunto = r["asunto"]
            mensaje = r["mensaje"]
            enlaces_col = r["enlaces"]

            # Enlaces: usar columna si viene, si no, extraer del mensaje
            enlaces_list = []
            if isinstance(enlaces_col, str) and enlaces_col.strip():
                # dividir por espacios si trae varias
                enlaces_list = [u for u in enlaces_col.split() if u.strip()]
            # extraer también del cuerpo por si hay más
            enlaces_list = list(set(enlaces_list + extraer_enlaces(mensaje)))

            # Adjuntos: extraer desde el cuerpo
            adjuntos = extraer_adjuntos(mensaje)

            # Armar texto enriquecido
            enriched = self._make_feature_text(remitente, asunto, mensaje, enlaces_list, adjuntos)
            rows.append(enriched)

        df["mensaje_limpio"] = rows
        self.df = df

        # Vectorización TF-IDF
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        X = self.vectorizer.fit_transform(self.df["mensaje_limpio"])
        self.palabras = self.vectorizer.get_feature_names_out()

        # Priors
        spam = self.df[self.df["etiqueta"] == "spam"]
        ham  = self.df[self.df["etiqueta"] == "ham"]
        n = len(self.df) or 1
        self.P_spam = len(spam) / n
        self.P_no_spam = len(ham) / n

        # Vectores por clase
        X_spam = self.vectorizer.transform(spam["mensaje_limpio"]) if len(spam) else X[:0]
        X_ham  = self.vectorizer.transform(ham["mensaje_limpio"])  if len(ham)  else X[:0]

        alpha = 1.0
        s_spam = np.sum(X_spam.toarray(), axis=0) if X_spam.shape[0] else np.zeros(len(self.palabras))
        s_ham  = np.sum(X_ham.toarray(),  axis=0) if X_ham.shape[0]  else np.zeros(len(self.palabras))

        denom_spam = (np.sum(s_spam) + alpha * len(self.palabras)) or 1.0
        denom_ham  = (np.sum(s_ham)  + alpha * len(self.palabras)) or 1.0
        self.P_feat_spam = (s_spam + alpha) / denom_spam
        self.P_feat_ham  = (s_ham  + alpha) / denom_ham

        # Métricas rápidas
        try:
            self.df["prediccion"] = self.df["mensaje_limpio"].apply(self.clasificar_texto)
            self.precision = float(np.mean(self.df["prediccion"] == self.df["etiqueta"]))
            denom = self.df["etiqueta"].value_counts().get("spam", 1)
            self.recall_spam = float(
                np.sum((self.df["prediccion"] == "spam") & (self.df["etiqueta"] == "spam")) / denom
            )
        except Exception:
            pass

    # ============ FEATURE TEXT =============
    def _make_feature_text(self, remitente: str, asunto: str, contenido: str,
                           enlaces: list[str] | None, adjuntos: list[tuple[str,str]] | None) -> str:
        parts: list[str] = []

        # Texto base (limpio)
        parts.append(limpiar_texto(asunto))
        parts.append(limpiar_texto(contenido))

        # Dominio remitente → tokens
        dom = dominio_de_email(remitente)
        parts += tokens_dominio(dom)

        # Enlaces → tokens
        if enlaces:
            for u in enlaces:
                parts += tokens_enlace(u)
        else:
            # intento de extracción si no vienen
            for u in extraer_enlaces(contenido):
                parts += tokens_enlace(u)

        # Adjuntos → tokens
        if adjuntos is None:
            adjuntos = extraer_adjuntos(contenido)
        parts += tokens_adjuntos(adjuntos)

        # Unir todo
        return " ".join([p for p in parts if p])

    # ============ NÚCLEO BAYES ============
    def _log_post(self, txt_clean: str):
        v = self.vectorizer.transform([txt_clean]).toarray()[0]
        eps = 1e-12
        ls = np.log(self.P_spam + eps)    + np.sum(np.log(self.P_feat_spam + eps) * v)
        lh = np.log(self.P_no_spam + eps) + np.sum(np.log(self.P_feat_ham  + eps) * v)
        return ls, lh

    def clasificar_texto(self, txt: str) -> str:
        t = limpiar_texto(txt)
        ls, lh = self._log_post(t)
        return "spam" if ls > lh else "ham"

    def prob_spam_texto(self, txt: str) -> float:
        t = limpiar_texto(txt)
        ls, lh = self._log_post(t)
        d = lh - ls
        return float(1.0 / (1.0 + np.exp(d)))

    # ============ API PARA CORREO ============
    def clasificar_correo(self, remitente: str, asunto: str, contenido: str) -> str:
        """
        Compatibilidad retro: extrae enlaces/adjuntos automáticamente del contenido.
        """
        enriched = self._make_feature_text(remitente, asunto, contenido, None, None)
        ls, lh = self._log_post(enriched)
        return "spam" if ls > lh else "ham"

    def prob_spam_correo(self, remitente: str, asunto: str, contenido: str) -> float:
        enriched = self._make_feature_text(remitente, asunto, contenido, None, None)
        ls, lh = self._log_post(enriched)
        d = lh - ls
        return float(1.0 / (1.0 + np.exp(d)))

    # Versión extendida (puedes pasar enlaces y adjuntos ya extraídos desde la UI)
    def clasificar_correo_ext(self, remitente: str, asunto: str, contenido: str,
                              enlaces: list[str] | None = None,
                              adjuntos: list[tuple[str,str]] | None = None) -> str:
        enriched = self._make_feature_text(remitente, asunto, contenido, enlaces, adjuntos)
        ls, lh = self._log_post(enriched)
        return "spam" if ls > lh else "ham"

    def prob_spam_correo_ext(self, remitente: str, asunto: str, contenido: str,
                             enlaces: list[str] | None = None,
                             adjuntos: list[tuple[str,str]] | None = None) -> float:
        enriched = self._make_feature_text(remitente, asunto, contenido, enlaces, adjuntos)
        ls, lh = self._log_post(enriched)
        d = lh - ls
        return float(1.0 / (1.0 + np.exp(d)))
