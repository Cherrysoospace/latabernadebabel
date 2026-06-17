from pymongo.database import Database

from models.usuario_model import Usuario
from config import generar_id


def _serializar(doc: dict) -> dict:
    if doc:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
    return doc


class UsuarioService:

    def __init__(self, db: Database):
        self.db = db
        self.col = db[Usuario.COLECCION]

    def crear(self, datos: dict) -> dict:
        correo = datos.get("correo", "").strip().lower()
        if self.col.find_one({"correo": correo}):
            raise ValueError(f"Ya existe un usuario con el correo '{correo}'.")

        usuario = Usuario(
            nombre=datos.get("nombre", ""),
            correo=correo,
            membresia=datos.get("membresia", "basica"),
            historial=datos.get("historial", []),
            preferencias=datos.get("preferencias", []),
            activo=datos.get("activo", True),
        )

        errores = usuario.validar()
        if errores:
            raise ValueError(errores)

        usuario.usuario_id = generar_id("USR", "usuarios", self.db)
        doc = usuario.to_dict()
        self.col.insert_one(doc)
        return _serializar(doc)

    def obtener_todos(self, skip: int = 0, limit: int = 20) -> list[dict]:
        docs = self.col.find({}, {"_id": 1, "usuario_id": 1, "nombre": 1, "correo": 1,
                                   "membresia": 1, "activo": 1, "fecha_registro": 1})
        docs = docs.sort("fecha_registro", -1).skip(skip).limit(limit)
        return [_serializar(d) for d in docs]

    def obtener_por_id(self, usuario_id: str) -> dict | None:
        doc = self.col.find_one({"usuario_id": usuario_id})
        return _serializar(doc) if doc else None

    def obtener_por_correo(self, correo: str) -> dict | None:
        doc = self.col.find_one({"correo": correo.strip().lower()})
        return _serializar(doc) if doc else None

    def obtener_por_membresia(self, membresia: str) -> list[dict]:
        docs = self.col.find({"membresia": membresia.lower()})
        return [_serializar(d) for d in docs]

    def obtener_activos(self) -> list[dict]:
        docs = self.col.find({"activo": True},
                              {"usuario_id": 1, "nombre": 1, "correo": 1, "membresia": 1})
        return [_serializar(d) for d in docs]

    def actualizar(self, usuario_id: str, datos: dict) -> dict | None:
        campos_permitidos = {"nombre", "correo", "membresia", "preferencias", "activo"}
        actualizacion = {k: v for k, v in datos.items() if k in campos_permitidos}

        if not actualizacion:
            raise ValueError("No se proporcionaron campos validos para actualizar.")

        resultado = self.col.find_one_and_update(
            {"usuario_id": usuario_id},
            {"$set": actualizacion},
            return_document=True,
        )
        return _serializar(resultado) if resultado else None

    def agregar_prestamo_al_historial(self, usuario_id: str, prestamo_id: str) -> bool:
        resultado = self.col.update_one(
            {"usuario_id": usuario_id},
            {"$addToSet": {"historial": prestamo_id}},
        )
        return resultado.modified_count > 0

    def eliminar(self, usuario_id: str) -> bool:
        resultado = self.col.delete_one({"usuario_id": usuario_id})
        return resultado.deleted_count > 0

    def desactivar(self, usuario_id: str) -> dict | None:
        return self.actualizar(usuario_id, {"activo": False})

    def contar_por_membresia(self) -> list[dict]:
        pipeline = [
            {"$group": {"_id": "$membresia", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
            {"$project": {"membresia": "$_id", "total": 1, "_id": 0}},
        ]
        return list(self.col.aggregate(pipeline))
