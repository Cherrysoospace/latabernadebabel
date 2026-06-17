from datetime import datetime, timezone
from bson import ObjectId


class Autor:

    COLECCION = "autores"
    BIOGRAFIA_MAX_CHARS = 2000

    def __init__(
        self,
        nombre: str,
        biografia: str = None,
        nacionalidad: str = None,
        obras: list[str] = None,
        premios: list[str] = None,
        autor_id: str = None,
        _id=None,
    ):
        self._id = _id or ObjectId()
        self.autor_id = autor_id
        self.nombre = nombre.strip()
        self.biografia = biografia.strip() if biografia else None
        self.nacionalidad = nacionalidad.strip() if nacionalidad else None
        self.obras = [o.strip() for o in obras if o.strip()] if obras else []
        self.premios = [p.strip() for p in premios if p.strip()] if premios else []
        self.fecha_registro = datetime.now(timezone.utc)

    def agregar_obra(self, titulo: str) -> None:
        titulo = titulo.strip()
        if titulo and titulo not in self.obras:
            self.obras.append(titulo)

    def agregar_premio(self, premio: str) -> None:
        premio = premio.strip()
        if premio and premio not in self.premios:
            self.premios.append(premio)

    def validar(self) -> list[str]:
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

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "autor_id": self.autor_id,
            "nombre": self.nombre,
            "biografia": self.biografia,
            "nacionalidad": self.nacionalidad,
            "obras": self.obras,
            "premios": self.premios,
            "fecha_registro": self.fecha_registro,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Autor":
        return cls(
            nombre=data.get("nombre", ""),
            biografia=data.get("biografia"),
            nacionalidad=data.get("nacionalidad"),
            obras=data.get("obras", []),
            premios=data.get("premios", []),
            autor_id=data.get("autor_id"),
            _id=data.get("_id"),
        )

    def __repr__(self):
        return f"<Autor: {self.nombre} ({self.nacionalidad}) — {len(self.obras)} obra(s)>"
