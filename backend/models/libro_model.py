"""
libro_model.py — Modelo de la colección 'libros'.

Colección: libros
Descripción: Representa un libro disponible en la biblioteca.
"""

from datetime import datetime, timezone
from bson import ObjectId


# Formatos válidos de libro
FORMATOS_VALIDOS = {"fisico", "digital", "audiolibro"}

# Géneros válidos (ampliable)
GENEROS_VALIDOS = {
    "ficcion", "no ficcion", "ciencia ficcion", "fantasia", "terror",
    "romance", "misterio", "thriller", "biografia", "historia",
    "ciencia", "tecnologia", "filosofia", "poesia", "infantil",
    "juvenil", "autoayuda", "arte", "economia", "derecho", "otro"
}

# Idiomas admitidos (código ISO 639-1)
IDIOMAS_VALIDOS = {
    "es": "Español",
    "en": "Inglés",
    "fr": "Francés",
    "pt": "Portugués",
    "de": "Alemán",
    "it": "Italiano",
    "zh": "Chino",
    "ja": "Japonés",
    "ru": "Ruso",
    "ar": "Árabe",
}


class Libro:
    """
    Modelo para la colección 'libros'.

    Campos:
        titulo      (str)      — Título del libro                  [requerido]
        autor       (str)      — Nombre del autor                  [requerido]
        genero      (str)      — Género literario                   [requerido]
        editorial   (str)      — Casa editorial                     [opcional]
        anio        (int)      — Año de publicación (≥ 1000)        [opcional]
        idioma      (str)      — Código ISO 639-1 del idioma        [opcional]
        formato     (str)      — 'fisico' | 'digital' | 'audiolibro' [opcional]
        descripcion (str)      — Sinopsis o descripción del libro   [opcional]
        fecha_registro (datetime) — Fecha de ingreso al catálogo   [auto]
        disponible  (bool)     — Si el libro está disponible        [auto=True]
    """

    COLECCION = "libros"

    def __init__(
        self,
        titulo: str,
        autor: str,
        genero: str,
        editorial: str = None,
        year: int = None,
        idioma: str = "es",
        formato: str = "fisico",
        descripcion: str = None,
        disponible: bool = True,
        _id=None,
    ):
        self._id = _id or ObjectId()
        self.titulo = titulo.strip()
        self.autor = autor.strip()
        self.genero = genero.strip().lower()
        self.editorial = editorial.strip() if editorial else None
        self.anio = year
        self.idioma = idioma.lower() if idioma else "es"
        self.formato = formato.lower() if formato else "fisico"
        self.descripcion = descripcion.strip() if descripcion else None
        self.disponible = disponible
        self.fecha_registro = datetime.now(timezone.utc)

    # ─── Validación ───────────────────────────────────────────────────────────

    def validar(self) -> list[str]:
        """
        Valida los campos del modelo.
        Retorna una lista de errores (vacía si todo es válido).
        """
        errores = []

        if not self.titulo:
            errores.append("El campo 'titulo' es requerido.")
        if not self.autor:
            errores.append("El campo 'autor' es requerido.")
        if not self.genero:
            errores.append("El campo 'genero' es requerido.")
        if self.genero and self.genero not in GENEROS_VALIDOS:
            errores.append(
                f"Género '{self.genero}' no válido. Opciones: {sorted(GENEROS_VALIDOS)}"
            )
        if self.anio is not None:
            if not isinstance(self.anio, int) or self.anio < 1000 or self.anio > datetime.now().year + 1:
                errores.append(f"El año debe ser un entero entre 1000 y {datetime.now().year + 1}.")
        if self.idioma and self.idioma not in IDIOMAS_VALIDOS:
            errores.append(
                f"Idioma '{self.idioma}' no válido. Opciones: {list(IDIOMAS_VALIDOS.keys())}"
            )
        if self.formato and self.formato not in FORMATOS_VALIDOS:
            errores.append(
                f"Formato '{self.formato}' no válido. Opciones: {sorted(FORMATOS_VALIDOS)}"
            )

        return errores

    # ─── Serialización ────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Convierte el modelo a un diccionario listo para insertar en MongoDB."""
        return {
            "_id": self._id,
            "titulo": self.titulo,
            "autor": self.autor,
            "genero": self.genero,
            "editorial": self.editorial,
            "anio": self.anio,
            "idioma": self.idioma,
            "formato": self.formato,
            "descripcion": self.descripcion,
            "disponible": self.disponible,
            "fecha_registro": self.fecha_registro,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Libro":
        """Crea un objeto Libro a partir de un diccionario (p. ej., desde MongoDB)."""
        return cls(
            titulo=data.get("titulo", ""),
            autor=data.get("autor", ""),
            genero=data.get("genero", ""),
            editorial=data.get("editorial"),
            year=data.get("anio"),
            idioma=data.get("idioma", "es"),
            formato=data.get("formato", "fisico"),
            descripcion=data.get("descripcion"),
            disponible=data.get("disponible", True),
            _id=data.get("_id"),
        )

    def __repr__(self):
        return f"<Libro: '{self.titulo}' — {self.autor} ({self.anio})>"
