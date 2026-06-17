from datetime import datetime, timezone
from bson import ObjectId


FORMATOS_VALIDOS = {"fisico", "digital", "audiolibro"}

GENEROS_VALIDOS = {
    "ficcion", "no ficcion", "ciencia ficcion", "fantasia", "terror",
    "romance", "misterio", "thriller", "biografia", "historia",
    "ciencia", "tecnologia", "filosofia", "poesia", "infantil",
    "juvenil", "autoayuda", "arte", "economia", "derecho", "otro"
}

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

    COLECCION = "libros"

    def __init__(
        self,
        titulo: str,
        autor: dict,
        genero: str,
        editorial: str = None,
        year: int = None,
        idioma: str = "es",
        formato: str = "fisico",
        descripcion: str = None,
        disponible: bool = True,
        estadisticas: dict = None,
        libro_id: str = None,
        _id=None,
    ):
        self._id = _id or ObjectId()
        self.libro_id = libro_id
        self.titulo = titulo.strip()
        self.autor = autor
        self.genero = genero.strip().lower()
        self.editorial = editorial.strip() if editorial else None
        self.anio = year
        self.idioma = idioma.lower() if idioma else "es"
        self.formato = formato.lower() if formato else "fisico"
        self.descripcion = descripcion.strip() if descripcion else None
        self.disponible = disponible
        self.estadisticas = estadisticas or {"promedioCalificacion": 0, "totalResenas": 0}
        self.fecha_registro = datetime.now(timezone.utc)

    def validar(self) -> list[str]:
        errores = []
        if not self.titulo:
            errores.append("El campo 'titulo' es requerido.")
        if not isinstance(self.autor, dict):
            errores.append("El campo 'autor' debe ser un objeto con 'autor_id', 'name' y 'nacionalidad'.")
        else:
            if not self.autor.get("autor_id"):
                errores.append("El campo 'autor.autor_id' es requerido.")
            if not self.autor.get("name"):
                errores.append("El campo 'autor.name' es requerido.")
        if not self.genero:
            errores.append("El campo 'genero' es requerido.")
        if self.genero and self.genero not in GENEROS_VALIDOS:
            errores.append(
                f"Genero '{self.genero}' no valido. Opciones: {sorted(GENEROS_VALIDOS)}"
            )
        if self.anio is not None:
            if not isinstance(self.anio, int) or self.anio < 1000 or self.anio > datetime.now().year + 1:
                errores.append(f"El anio debe ser un entero entre 1000 y {datetime.now().year + 1}.")
        if self.idioma and self.idioma not in IDIOMAS_VALIDOS:
            errores.append(
                f"Idioma '{self.idioma}' no valido. Opciones: {list(IDIOMAS_VALIDOS.keys())}"
            )
        if self.formato and self.formato not in FORMATOS_VALIDOS:
            errores.append(
                f"Formato '{self.formato}' no valido. Opciones: {sorted(FORMATOS_VALIDOS)}"
            )
        return errores

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "libro_id": self.libro_id,
            "titulo": self.titulo,
            "autor": self.autor,
            "genero": self.genero,
            "editorial": self.editorial,
            "anio": self.anio,
            "idioma": self.idioma,
            "formato": self.formato,
            "descripcion": self.descripcion,
            "disponible": self.disponible,
            "estadisticas": self.estadisticas,
            "fecha_registro": self.fecha_registro,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Libro":
        return cls(
            titulo=data.get("titulo", ""),
            autor=data.get("autor", {}),
            genero=data.get("genero", ""),
            editorial=data.get("editorial"),
            year=data.get("anio"),
            idioma=data.get("idioma", "es"),
            formato=data.get("formato", "fisico"),
            descripcion=data.get("descripcion"),
            disponible=data.get("disponible", True),
            estadisticas=data.get("estadisticas"),
            libro_id=data.get("libro_id"),
            _id=data.get("_id"),
        )

    def __repr__(self):
        nombre_autor = self.autor.get("name", str(self.autor)) if isinstance(self.autor, dict) else self.autor
        return f"<Libro: '{self.titulo}' — {nombre_autor} ({self.anio})>"
