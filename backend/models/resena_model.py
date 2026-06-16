"""
resena_model.py — Modelo de la colección 'resenas'.

Colección: resenas
Descripción: Almacena la reseña que un usuario realiza sobre un libro,
             incluyendo calificación numérica y comentario de texto.
"""

from datetime import datetime, timezone
from bson import ObjectId


class Resena:
    """
    Modelo para la colección 'resenas'.

    Campos:
        usuario_id   (ObjectId) — ID del usuario que escribe la reseña  [requerido]
        libro_id     (ObjectId) — ID del libro reseñado                 [requerido]
        calificacion (int)      — Puntuación del 1 al 5                 [requerido]
        comentario   (str)      — Texto de la reseña                    [opcional]
        fecha        (datetime) — Fecha de publicación de la reseña     [auto]
        editada      (bool)     — Si la reseña fue modificada           [auto=False]
        fecha_edicion (datetime)— Fecha de la última edición            [opcional]
    """

    COLECCION = "resenas"

    CALIFICACION_MIN = 1
    CALIFICACION_MAX = 5
    COMENTARIO_MAX_CHARS = 1000

    def __init__(
        self,
        usuario_id: ObjectId,
        libro_id: ObjectId,
        calificacion: int,
        comentario: str = None,
        fecha: datetime = None,
        editada: bool = False,
        fecha_edicion: datetime = None,
        _id=None,
    ):
        self._id = _id or ObjectId()
        # Asegurar que los IDs sean ObjectId
        self.usuario_id = ObjectId(usuario_id) if not isinstance(usuario_id, ObjectId) else usuario_id
        self.libro_id = ObjectId(libro_id) if not isinstance(libro_id, ObjectId) else libro_id
        self.calificacion = int(calificacion) if calificacion is not None else None
        self.comentario = comentario.strip() if comentario else None
        self.fecha = fecha or datetime.now(timezone.utc)
        self.editada = editada
        self.fecha_edicion = fecha_edicion

    # ─── Lógica de negocio ────────────────────────────────────────────────────

    def editar(self, nueva_calificacion: int = None, nuevo_comentario: str = None) -> None:
        """
        Actualiza la calificación o el comentario de la reseña
        y registra la fecha de edición.
        """
        if nueva_calificacion is not None:
            self.calificacion = int(nueva_calificacion)
        if nuevo_comentario is not None:
            self.comentario = nuevo_comentario.strip()
        self.editada = True
        self.fecha_edicion = datetime.now(timezone.utc)

    # ─── Validación ───────────────────────────────────────────────────────────

    def validar(self) -> list[str]:
        """
        Valida los campos del modelo.
        Retorna una lista de errores (vacía si todo es válido).
        """
        errores = []

        if not self.usuario_id:
            errores.append("El campo 'usuario_id' es requerido.")
        if not self.libro_id:
            errores.append("El campo 'libro_id' es requerido.")
        if self.calificacion is None:
            errores.append("El campo 'calificacion' es requerido.")
        elif not isinstance(self.calificacion, int) or not (
            self.CALIFICACION_MIN <= self.calificacion <= self.CALIFICACION_MAX
        ):
            errores.append(
                f"La 'calificacion' debe ser un entero entre "
                f"{self.CALIFICACION_MIN} y {self.CALIFICACION_MAX}."
            )
        if self.comentario and len(self.comentario) > self.COMENTARIO_MAX_CHARS:
            errores.append(
                f"El 'comentario' no puede superar {self.COMENTARIO_MAX_CHARS} caracteres."
            )

        return errores

    # ─── Serialización ────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Convierte el modelo a un diccionario listo para insertar en MongoDB."""
        return {
            "_id": self._id,
            "usuario_id": self.usuario_id,
            "libro_id": self.libro_id,
            "calificacion": self.calificacion,
            "comentario": self.comentario,
            "fecha": self.fecha,
            "editada": self.editada,
            "fecha_edicion": self.fecha_edicion,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Resena":
        """Crea un objeto Resena a partir de un diccionario (p. ej., desde MongoDB)."""
        return cls(
            usuario_id=data.get("usuario_id"),
            libro_id=data.get("libro_id"),
            calificacion=data.get("calificacion"),
            comentario=data.get("comentario"),
            fecha=data.get("fecha"),
            editada=data.get("editada", False),
            fecha_edicion=data.get("fecha_edicion"),
            _id=data.get("_id"),
        )

    def __repr__(self):
        return (
            f"<Resena: libro={self.libro_id} usuario={self.usuario_id} "
            f"calificacion={self.calificacion}/5>"
        )
