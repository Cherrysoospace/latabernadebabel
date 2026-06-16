"""
autor_model.py — Modelo de la colección 'autores'.

Colección: autores
Descripción: Almacena la información biográfica y bibliográfica
             de los autores cuyos libros están en la biblioteca.
"""

from datetime import datetime, timezone
from bson import ObjectId


class Autor:
    """
    Modelo para la colección 'autores'.

    Campos:
        nombre        (str)       — Nombre completo del autor            [requerido]
        biografia     (str)       — Texto biográfico del autor           [opcional]
        nacionalidad  (str)       — País o región de origen              [opcional]
        obras         (list[str]) — Lista de títulos de sus obras        [auto=[]]
        premios       (list[str]) — Lista de premios o reconocimientos   [auto=[]]
        fecha_registro (datetime) — Fecha de ingreso al sistema          [auto]
    """

    COLECCION = "autores"

    BIOGRAFIA_MAX_CHARS = 2000

    def __init__(
        self,
        nombre: str,
        biografia: str = None,
        nacionalidad: str = None,
        obras: list[str] = None,
        premios: list[str] = None,
        _id=None,
    ):
        self._id = _id or ObjectId()
        self.nombre = nombre.strip()
        self.biografia = biografia.strip() if biografia else None
        self.nacionalidad = nacionalidad.strip() if nacionalidad else None
        # obras: lista de títulos de libros (strings)
        self.obras = [o.strip() for o in obras if o.strip()] if obras else []
        # premios: lista de nombres de galardones o reconocimientos
        self.premios = [p.strip() for p in premios if p.strip()] if premios else []
        self.fecha_registro = datetime.now(timezone.utc)

    # ─── Lógica de negocio ────────────────────────────────────────────────────

    def agregar_obra(self, titulo: str) -> None:
        """Agrega una obra a la lista si no existe ya."""
        titulo = titulo.strip()
        if titulo and titulo not in self.obras:
            self.obras.append(titulo)

    def agregar_premio(self, premio: str) -> None:
        """Agrega un premio a la lista si no existe ya."""
        premio = premio.strip()
        if premio and premio not in self.premios:
            self.premios.append(premio)

    # ─── Validación ───────────────────────────────────────────────────────────

    def validar(self) -> list[str]:
        """
        Valida los campos del modelo.
        Retorna una lista de errores (vacía si todo es válido).
        """
        errores = []

        if not self.nombre:
            errores.append("El campo 'nombre' es requerido.")
        if self.biografia and len(self.biografia) > self.BIOGRAFIA_MAX_CHARS:
            errores.append(
                f"La 'biografia' no puede superar {self.BIOGRAFIA_MAX_CHARS} caracteres."
            )
        if not isinstance(self.obras, list):
            errores.append("El campo 'obras' debe ser una lista de strings.")
        if not isinstance(self.premios, list):
            errores.append("El campo 'premios' debe ser una lista de strings.")

        return errores

    # ─── Serialización ────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Convierte el modelo a un diccionario listo para insertar en MongoDB."""
        return {
            "_id": self._id,
            "nombre": self.nombre,
            "biografia": self.biografia,
            "nacionalidad": self.nacionalidad,
            "obras": self.obras,
            "premios": self.premios,
            "fecha_registro": self.fecha_registro,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Autor":
        """Crea un objeto Autor a partir de un diccionario (p. ej., desde MongoDB)."""
        return cls(
            nombre=data.get("nombre", ""),
            biografia=data.get("biografia"),
            nacionalidad=data.get("nacionalidad"),
            obras=data.get("obras", []),
            premios=data.get("premios", []),
            _id=data.get("_id"),
        )

    def __repr__(self):
        return f"<Autor: {self.nombre} ({self.nacionalidad}) — {len(self.obras)} obra(s)>"
