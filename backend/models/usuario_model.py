"""
usuario_model.py — Modelo de la colección 'usuarios'.

Colección: usuarios
Descripción: Representa un usuario registrado en la biblioteca.
"""

from datetime import datetime, timezone
from bson import ObjectId


# Tipos de membresía válidos
MEMBRESIAS_VALIDAS = {"basica", "premium", "estudiante"}


class Usuario:
    """
    Modelo para la colección 'usuarios'.

    Campos:
        nombre       (str)       — Nombre completo del usuario      [requerido]
        correo       (str)       — Correo electrónico (único)       [requerido]
        membresia    (str)       — 'basica' | 'premium' | 'estudiante' [requerido]
        historial    (list)      — Lista de ObjectId de préstamos   [auto=[]]
        preferencias (list[str]) — Géneros literarios preferidos    [auto=[]]
        activo       (bool)      — Si la cuenta está activa         [auto=True]
        fecha_registro (datetime)— Fecha de creación de la cuenta   [auto]
    """

    COLECCION = "usuarios"

    def __init__(
        self,
        nombre: str,
        correo: str,
        membresia: str = "basica",
        historial: list = None,
        preferencias: list[str] = None,
        activo: bool = True,
        _id=None,
    ):
        self._id = _id or ObjectId()
        self.nombre = nombre.strip()
        self.correo = correo.strip().lower()
        self.membresia = membresia.strip().lower() if membresia else "basica"
        # historial: lista de ObjectId apuntando a la colección 'prestamos'
        self.historial = historial if historial is not None else []
        # preferencias: lista de géneros literarios (strings)
        self.preferencias = [p.strip().lower() for p in preferencias] if preferencias else []
        self.activo = activo
        self.fecha_registro = datetime.now(timezone.utc)

    # ─── Validación ───────────────────────────────────────────────────────────

    def validar(self) -> list[str]:
        """
        Valida los campos del modelo.
        Retorna una lista de errores (vacía si todo es válido).
        """
        errores = []

        if not self.nombre:
            errores.append("El campo 'nombre' es requerido.")
        if not self.correo:
            errores.append("El campo 'correo' es requerido.")
        elif "@" not in self.correo or "." not in self.correo.split("@")[-1]:
            errores.append("El formato del 'correo' no es válido.")
        if not self.membresia:
            errores.append("El campo 'membresia' es requerido.")
        elif self.membresia not in MEMBRESIAS_VALIDAS:
            errores.append(
                f"Membresía '{self.membresia}' no válida. Opciones: {sorted(MEMBRESIAS_VALIDAS)}"
            )
        if not isinstance(self.historial, list):
            errores.append("El campo 'historial' debe ser una lista.")
        if not isinstance(self.preferencias, list):
            errores.append("El campo 'preferencias' debe ser una lista.")

        return errores

    # ─── Serialización ────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Convierte el modelo a un diccionario listo para insertar en MongoDB."""
        return {
            "_id": self._id,
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
        """Crea un objeto Usuario a partir de un diccionario (p. ej., desde MongoDB)."""
        return cls(
            nombre=data.get("nombre", ""),
            correo=data.get("correo", ""),
            membresia=data.get("membresia", "basica"),
            historial=data.get("historial", []),
            preferencias=data.get("preferencias", []),
            activo=data.get("activo", True),
            _id=data.get("_id"),
        )

    def __repr__(self):
        return f"<Usuario: {self.nombre} ({self.correo}) — {self.membresia}>"
