from datetime import datetime, timezone
from bson import ObjectId


MEMBRESIAS_VALIDAS = {"basica", "premium", "estudiante"}


class Usuario:

    COLECCION = "usuarios"

    def __init__(
        self,
        nombre: str,
        correo: str,
        membresia: str = "basica",
        historial: list = None,
        preferencias: list[str] = None,
        activo: bool = True,
        usuario_id: str = None,
        _id=None,
    ):
        self._id = _id or ObjectId()
        self.usuario_id = usuario_id
        self.nombre = nombre.strip()
        self.correo = correo.strip().lower()
        self.membresia = membresia.strip().lower() if membresia else "basica"
        self.historial = historial if historial is not None else []
        self.preferencias = [p.strip().lower() for p in preferencias] if preferencias else []
        self.activo = activo
        self.fecha_registro = datetime.now(timezone.utc)

    def validar(self) -> list[str]:
        errores = []
        if not self.nombre:
            errores.append("El campo 'nombre' es requerido.")
        if not self.correo:
            errores.append("El campo 'correo' es requerido.")
        elif "@" not in self.correo or "." not in self.correo.split("@")[-1]:
            errores.append("El formato del 'correo' no es valido.")
        if not self.membresia:
            errores.append("El campo 'membresia' es requerido.")
        elif self.membresia not in MEMBRESIAS_VALIDAS:
            errores.append(
                f"Membresia '{self.membresia}' no valida. Opciones: {sorted(MEMBRESIAS_VALIDAS)}"
            )
        if not isinstance(self.historial, list):
            errores.append("El campo 'historial' debe ser una lista.")
        if not isinstance(self.preferencias, list):
            errores.append("El campo 'preferencias' debe ser una lista.")
        return errores

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "usuario_id": self.usuario_id,
            "nombre": self.nombre,
            "correo": self.correo,
            "membresia": self.membresia,
            "historial": self.historial,
            "preferencias": self.preferencias,
            "activo": self.activo,
            "fecha_registro": self.fecha_registro,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Usuario":
        return cls(
            nombre=data.get("nombre", ""),
            correo=data.get("correo", ""),
            membresia=data.get("membresia", "basica"),
            historial=data.get("historial", []),
            preferencias=data.get("preferencias", []),
            activo=data.get("activo", True),
            usuario_id=data.get("usuario_id"),
            _id=data.get("_id"),
        )

    def __repr__(self):
        return f"<Usuario: {self.nombre} ({self.correo}) — {self.membresia}>"
