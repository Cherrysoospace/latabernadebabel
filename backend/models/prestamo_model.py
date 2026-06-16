"""
prestamo_model.py — Modelo de la colección 'prestamos'.

Colección: prestamos
Descripción: Registra el préstamo de un libro a un usuario,
             incluyendo fechas y estado del préstamo.
"""

from datetime import datetime, timezone, timedelta
from bson import ObjectId


# Estados válidos del préstamo
ESTADOS_VALIDOS = {"activo", "devuelto", "vencido"}

# Duración por defecto del préstamo (días) según tipo de membresía
DURACION_POR_MEMBRESIA = {
    "basica": 14,       # 2 semanas
    "estudiante": 21,   # 3 semanas
    "premium": 30,      # 1 mes
}


class Prestamo:
    """
    Modelo para la colección 'prestamos'.

    Campos:
        usuario_id   (ObjectId)  — ID del usuario que realiza el préstamo  [requerido]
        libro_id     (ObjectId)  — ID del libro prestado                   [requerido]
        fecha_inicio (datetime)  — Fecha de inicio del préstamo            [auto=ahora]
        fecha_fin    (datetime)  — Fecha límite de devolución              [requerido]
        estado       (str)       — 'activo' | 'devuelto' | 'vencido'       [auto='activo']
        fecha_devolucion (datetime) — Fecha real de devolución             [opcional]
    """

    COLECCION = "prestamos"

    def __init__(
        self,
        usuario_id: ObjectId,
        libro_id: ObjectId,
        fecha_fin: datetime,
        fecha_inicio: datetime = None,
        estado: str = "activo",
        fecha_devolucion: datetime = None,
        _id=None,
    ):
        self._id = _id or ObjectId()
        # Asegurar que los IDs sean ObjectId
        self.usuario_id = ObjectId(usuario_id) if not isinstance(usuario_id, ObjectId) else usuario_id
        self.libro_id = ObjectId(libro_id) if not isinstance(libro_id, ObjectId) else libro_id
        self.fecha_inicio = fecha_inicio or datetime.now(timezone.utc)
        self.fecha_fin = fecha_fin
        self.estado = estado.lower() if estado else "activo"
        self.fecha_devolucion = fecha_devolucion  # None hasta que se devuelva

    # ─── Método de fábrica ────────────────────────────────────────────────────

    @classmethod
    def crear_con_duracion(
        cls,
        usuario_id: ObjectId,
        libro_id: ObjectId,
        dias: int = 14,
    ) -> "Prestamo":
        """
        Crea un préstamo calculando la fecha_fin a partir de los días dados.
        Útil para crear préstamos con la duración según el tipo de membresía.
        """
        ahora = datetime.now(timezone.utc)
        fecha_fin = ahora + timedelta(days=dias)
        return cls(
            usuario_id=usuario_id,
            libro_id=libro_id,
            fecha_inicio=ahora,
            fecha_fin=fecha_fin,
        )

    # ─── Lógica de negocio ────────────────────────────────────────────────────

    def esta_vencido(self) -> bool:
        """Retorna True si el préstamo ha pasado su fecha límite sin ser devuelto."""
        ahora = datetime.now(timezone.utc)
        fecha_fin = self.fecha_fin
        # Normalizar a aware datetime si es naive
        if fecha_fin.tzinfo is None:
            fecha_fin = fecha_fin.replace(tzinfo=timezone.utc)
        return self.estado == "activo" and ahora > fecha_fin

    def devolver(self) -> None:
        """Marca el préstamo como devuelto y registra la fecha real."""
        self.estado = "devuelto"
        self.fecha_devolucion = datetime.now(timezone.utc)

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
        if not self.fecha_fin:
            errores.append("El campo 'fecha_fin' es requerido.")
        elif isinstance(self.fecha_fin, datetime):
            # Normalizar para comparar
            fin = self.fecha_fin
            if fin.tzinfo is None:
                fin = fin.replace(tzinfo=timezone.utc)
            inicio = self.fecha_inicio
            if inicio.tzinfo is None:
                inicio = inicio.replace(tzinfo=timezone.utc)
            if fin <= inicio:
                errores.append("La 'fecha_fin' debe ser posterior a 'fecha_inicio'.")
        if self.estado not in ESTADOS_VALIDOS:
            errores.append(
                f"Estado '{self.estado}' no válido. Opciones: {sorted(ESTADOS_VALIDOS)}"
            )

        return errores

    # ─── Serialización ────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Convierte el modelo a un diccionario listo para insertar en MongoDB."""
        return {
            "_id": self._id,
            "usuario_id": self.usuario_id,
            "libro_id": self.libro_id,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "estado": self.estado,
            "fecha_devolucion": self.fecha_devolucion,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Prestamo":
        """Crea un objeto Prestamo a partir de un diccionario (p. ej., desde MongoDB)."""
        return cls(
            usuario_id=data.get("usuario_id"),
            libro_id=data.get("libro_id"),
            fecha_inicio=data.get("fecha_inicio"),
            fecha_fin=data.get("fecha_fin"),
            estado=data.get("estado", "activo"),
            fecha_devolucion=data.get("fecha_devolucion"),
            _id=data.get("_id"),
        )

    def __repr__(self):
        return (
            f"<Prestamo: usuario={self.usuario_id} libro={self.libro_id} "
            f"estado={self.estado} vence={self.fecha_fin.date()}>"
        )
