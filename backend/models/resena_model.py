from datetime import datetime, timezone
from bson import ObjectId


class Resena:

    COLECCION = "resenas"
    CALIFICACION_MIN = 1
    CALIFICACION_MAX = 5
    COMENTARIO_MAX_CHARS = 1000

    def __init__(
        self,
        usuario: dict,
        libro: dict,
        calificacion: int,
        comentario: str = None,
        fecha: datetime = None,
        editada: bool = False,
        fecha_edicion: datetime = None,
        resena_id: str = None,
        _id=None,
    ):
        self._id = _id or ObjectId()
        self.resena_id = resena_id
        self.usuario = usuario
        self.libro = libro
        self.calificacion = int(calificacion) if calificacion is not None else None
        self.comentario = comentario.strip() if comentario else None
        self.fecha = fecha or datetime.now(timezone.utc)
        self.editada = editada
        self.fecha_edicion = fecha_edicion

    def editar(self, nueva_calificacion: int = None, nuevo_comentario: str = None) -> None:
        if nueva_calificacion is not None:
            self.calificacion = int(nueva_calificacion)
        if nuevo_comentario is not None:
            self.comentario = nuevo_comentario.strip()
        self.editada = True
        self.fecha_edicion = datetime.now(timezone.utc)

    def validar(self) -> list[str]:
        errores = []
        if not isinstance(self.usuario, dict) or not self.usuario.get("usuario_id"):
            errores.append("El campo 'usuario' debe ser un objeto con 'usuario_id'.")
        if not isinstance(self.libro, dict) or not self.libro.get("libro_id"):
            errores.append("El campo 'libro' debe ser un objeto con 'libro_id'.")
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

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "resena_id": self.resena_id,
            "usuario": self.usuario,
            "libro": self.libro,
            "calificacion": self.calificacion,
            "comentario": self.comentario,
            "fecha": self.fecha,
            "editada": self.editada,
            "fecha_edicion": self.fecha_edicion,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Resena":
        return cls(
            usuario=data.get("usuario", {}),
            libro=data.get("libro", {}),
            calificacion=data.get("calificacion"),
            comentario=data.get("comentario"),
            fecha=data.get("fecha"),
            editada=data.get("editada", False),
            fecha_edicion=data.get("fecha_edicion"),
            resena_id=data.get("resena_id"),
            _id=data.get("_id"),
        )

    def __repr__(self):
        return (
            f"<Resena: libro={self.libro.get('libro_id')} "
            f"usuario={self.usuario.get('usuario_id')} "
            f"calificacion={self.calificacion}/5>"
        )
