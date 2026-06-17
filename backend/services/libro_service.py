from pymongo.database import Database

from models.libro_model import Libro
from config import generar_id


def _serializar(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


class LibroService:

    def __init__(self, db: Database):
        self.db = db
        self.col = db[Libro.COLECCION]

    def crear(self, datos: dict) -> dict:
        libro = Libro(
            titulo=datos.get("titulo", ""),
            autor=datos.get("autor", {}),
            genero=datos.get("genero", ""),
            editorial=datos.get("editorial"),
            year=datos.get("anio"),
            idioma=datos.get("idioma", "es"),
            formato=datos.get("formato", "fisico"),
            descripcion=datos.get("descripcion"),
            disponible=datos.get("disponible", True),
        )

        errores = libro.validar()
        if errores:
            raise ValueError(errores)

        libro.libro_id = generar_id("LIB", "libros", self.db)
        doc = libro.to_dict()
        self.col.insert_one(doc)
        return _serializar(doc)

    def obtener_todos(self, skip: int = 0, limit: int = 100) -> list[dict]:
        docs = self.col.find({}, {"_id": 1, "libro_id": 1, "titulo": 1, "autor": 1,
                                   "genero": 1, "disponible": 1, "anio": 1})
        docs = docs.sort("fecha_registro", -1).skip(skip).limit(limit)
        return [_serializar(d) for d in docs]

    def obtener_por_id(self, libro_id: str) -> dict | None:
        doc = self.col.find_one({"libro_id": libro_id})
        return _serializar(doc) if doc else None

    def buscar(self, termino: str) -> list[dict]:
        regex = {"$regex": termino, "$options": "i"}
        docs = self.col.find({"$or": [{"titulo": regex}, {"autor.name": regex}]})
        return [_serializar(d) for d in docs]

    def obtener_disponibles(self) -> list[dict]:
        docs = self.col.find({"disponible": True})
        return [_serializar(d) for d in docs]

    def obtener_por_genero(self, genero: str) -> list[dict]:
        docs = self.col.find({"genero": genero.lower()})
        return [_serializar(d) for d in docs]

    def actualizar(self, libro_id: str, datos: dict) -> dict | None:
        campos_permitidos = {
            "titulo", "autor", "genero", "editorial",
            "anio", "idioma", "formato", "descripcion", "disponible"
        }
        actualizacion = {k: v for k, v in datos.items() if k in campos_permitidos}

        if not actualizacion:
            raise ValueError("No se proporcionaron campos validos para actualizar.")

        resultado = self.col.find_one_and_update(
            {"libro_id": libro_id},
            {"$set": actualizacion},
            return_document=True,
        )
        return _serializar(resultado) if resultado else None

    def cambiar_disponibilidad(self, libro_id: str, disponible: bool) -> dict | None:
        return self.actualizar(libro_id, {"disponible": disponible})

    def eliminar(self, libro_id: str) -> bool:
        resultado = self.col.delete_one({"libro_id": libro_id})
        return resultado.deleted_count > 0

    def contar_por_genero(self) -> list[dict]:
        pipeline = [
            {"$group": {"_id": "$genero", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
            {"$project": {"genero": "$_id", "total": 1, "_id": 0}},
        ]
        return list(self.col.aggregate(pipeline))
