from datetime import datetime, timezone, timedelta
from bson import ObjectId


ESTADOS_VALIDOS = {"activo", "devuelto", "vencido"}

DURACION_POR_MEMBRESIA = {
    "basica": 14,
    "estudiante": 21,
    "premium": 30,
}


class Prestamo:

    COLECCION = "prestamos"

    def __init__(
        self,
        usuario_id: str,
        libro_id: str,
        fecha_fin: datetime,
        fecha_inicio: datetime = None,
        estado: str = "activo",
        fecha_devolucion: datetime = None,
        prestamo_id: str = None,
        _id=None,
    ):
        self._id = _id or ObjectId()
        self.prestamo_id = prestamo_id
        self.usuario_id = usuario_id
        self.libro_id = libro_id
        self.fecha_inicio = fecha_inicio or datetime.now(timezone.utc)
        self.fecha_fin = fecha_fin
        self.estado = estado.lower() if estado else "activo"
        self.fecha_devolucion = fecha_devolucion

    @classmethod
    def crear_con_duracion(
        cls,
        usuario_id: str,
        libro_id: str,
        dias: int = 14,
    ) -> "Prestamo":
        ahora = datetime.now(timezone.utc)
        fecha_fin = ahora + timedelta(days=dias)
        return cls(
            usuario_id=usuario_id,
            libro_id=libro_id,
            fecha_inicio=ahora,
            fecha_fin=fecha_fin,
        )

    def esta_vencido(self) -> bool:
        ahora = datetime.now(timezone.utc)
        fecha_fin = self.fecha_fin
        if fecha_fin.tzinfo is None:
            fecha_fin = fecha_fin.replace(tzinfo=timezone.utc)
        return self.estado == "activo" and ahora > fecha_fin

    def devolver(self) -> None:
        self.estado = "devuelto"
        self.fecha_devolucion = datetime.now(timezone.utc)

    def validar(self) -> list[str]:
        errores = []
        if not self.usuario_id:
            errores.append("El campo 'usuario_id' es requerido.")
        if not self.libro_id:
            errores.append("El campo 'libro_id' es requerido.")
        if not self.fecha_fin:
            errores.append("El campo 'fecha_fin' es requerido.")
        elif isinstance(self.fecha_fin, datetime):
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
                f"Estado '{self.estado}' no valido. Opciones: {sorted(ESTADOS_VALIDOS)}"
            )
        return errores

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "prestamo_id": self.prestamo_id,
            "usuario_id": self.usuario_id,
            "libro_id": self.libro_id,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "estado": self.estado,
            "fecha_devolucion": self.fecha_devolucion,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Prestamo":
        return cls(
            usuario_id=data.get("usuario_id"),
            libro_id=data.get("libro_id"),
            fecha_inicio=data.get("fecha_inicio"),
            fecha_fin=data.get("fecha_fin"),
            estado=data.get("estado", "activo"),
            fecha_devolucion=data.get("fecha_devolucion"),
            prestamo_id=data.get("prestamo_id"),
            _id=data.get("_id"),
        )

    def __repr__(self):
        return (
            f"<Prestamo: usuario={self.usuario_id} libro={self.libro_id} "
            f"estado={self.estado} vence={self.fecha_fin.date()}>"
        )
