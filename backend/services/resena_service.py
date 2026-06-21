from datetime import datetime, timezone
from pymongo.database import Database

from models.resena_model import Resena
from models.libro_model import Libro
from models.usuario_model import Usuario
from config import generar_id


def _serializar(doc: dict) -> dict:
    if doc:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
    return doc


class ResenaService:

    def __init__(self, db: Database):
        self.db = db
        self.col = db[Resena.COLECCION]
        self.col_libros = db[Libro.COLECCION]
        self.col_usuarios = db[Usuario.COLECCION]

    def _actualizar_estadisticas_libro(self, libro_id: str):
        pipeline = [
            {"$match": {"libro.libro_id": libro_id}},
            {"$group": {
                "_id": "$libro.libro_id",
                "promedio": {"$avg": "$calificacion"},
                "total": {"$sum": 1},
            }},
        ]
        resultado = list(self.col.aggregate(pipeline))
        if resultado:
            stats = {
                "promedioCalificacion": round(resultado[0]["promedio"], 1),
                "totalResenas": resultado[0]["total"],
            }
        else:
            stats = {"promedioCalificacion": 0, "totalResenas": 0}
        self.col_libros.update_one(
            {"libro_id": libro_id},
            {"$set": {"estadisticas": stats}}
        )

    def crear(self, datos: dict) -> dict:
        usuario_id = datos.get("usuario_id", "")
        libro_id = datos.get("libro_id", "")

        libro_doc = self.col_libros.find_one({"libro_id": libro_id})
        if not libro_doc:
            raise ValueError("El libro especificado no existe.")

        usuario_doc = self.col_usuarios.find_one({"usuario_id": usuario_id})
        if not usuario_doc:
            raise ValueError("El usuario especificado no existe.")
        if not usuario_doc.get("activo", False):
            raise ValueError("La cuenta del usuario no esta activa.")

        if self.col.find_one({"usuario.usuario_id": usuario_id, "libro.libro_id": libro_id}):
            raise ValueError("Este usuario ya tiene una resena para este libro.")

        usuario_ref = {
            "usuario_id": usuario_doc["usuario_id"],
            "nombre": usuario_doc["nombre"],
            "correo": usuario_doc["correo"],
        }
        libro_ref = {
            "libro_id": libro_doc["libro_id"],
            "titulo": libro_doc["titulo"],
        }

        resena = Resena(
            usuario=usuario_ref,
            libro=libro_ref,
            calificacion=datos.get("calificacion"),
            comentario=datos.get("comentario"),
        )

        errores = resena.validar()
        if errores:
            raise ValueError(errores)

        resena.resena_id = generar_id("RES", "resenas", self.db)
        doc = resena.to_dict()
        self.col.insert_one(doc)
        self._actualizar_estadisticas_libro(libro_id)
        return _serializar(doc)

    def obtener_todos(self, skip: int = 0, limit: int = 20) -> dict:
        filtro = {}
        total = self.col.count_documents(filtro)
        docs = self.col.find(filtro).sort("resena_id", 1).skip(skip).limit(limit)
        return {
            "items": [_serializar(d) for d in docs],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    def obtener_por_id(self, resena_id: str) -> dict | None:
        doc = self.col.find_one({"resena_id": resena_id})
        return _serializar(doc) if doc else None

    def obtener_por_libro(self, libro_id: str) -> list[dict]:
        docs = self.col.find({"libro.libro_id": libro_id}).sort("fecha", -1)
        return [_serializar(d) for d in docs]

    def obtener_por_usuario(self, usuario_id: str) -> list[dict]:
        docs = self.col.find({"usuario.usuario_id": usuario_id}).sort("fecha", -1)
        return [_serializar(d) for d in docs]

    def obtener_por_calificacion_minima(self, minimo: int) -> list[dict]:
        if not (1 <= int(minimo) <= 5):
            raise ValueError("La calificacion minima debe estar entre 1 y 5.")
        docs = self.col.find({"calificacion": {"$gte": int(minimo)}}).sort("calificacion", -1)
        return [_serializar(d) for d in docs]

    def actualizar(self, resena_id: str, datos: dict) -> dict | None:
        campos_permitidos = {"calificacion", "comentario"}
        actualizacion = {k: v for k, v in datos.items() if k in campos_permitidos}

        if not actualizacion:
            raise ValueError("Se debe proporcionar 'calificacion' o 'comentario' para actualizar.")

        if "calificacion" in actualizacion:
            cal = int(actualizacion["calificacion"])
            if not (1 <= cal <= 5):
                raise ValueError("La calificacion debe estar entre 1 y 5.")
            actualizacion["calificacion"] = cal

        actualizacion["editada"] = True
        actualizacion["fecha_edicion"] = datetime.now(timezone.utc)

        resultado = self.col.find_one_and_update(
            {"resena_id": resena_id},
            {"$set": actualizacion},
            return_document=True,
        )
        if resultado:
            self._actualizar_estadisticas_libro(resultado["libro"]["libro_id"])
        return _serializar(resultado) if resultado else None

    def eliminar(self, resena_id: str) -> bool:
        resena = self.col.find_one({"resena_id": resena_id})
        if not resena:
            return False
        libro_id = resena["libro"]["libro_id"]
        resultado = self.col.delete_one({"resena_id": resena_id})
        if resultado.deleted_count:
            self._actualizar_estadisticas_libro(libro_id)
        return resultado.deleted_count > 0

    def promedio_calificacion_libro(self, libro_id: str) -> dict:
        pipeline = [
            {"$match": {"libro.libro_id": libro_id}},
            {"$group": {
                "_id": "$libro.libro_id",
                "promedio": {"$avg": "$calificacion"},
                "total_resenas": {"$sum": 1},
            }},
            {"$project": {
                "libro_id": "$_id",
                "promedio": {"$round": ["$promedio", 2]},
                "total_resenas": 1,
                "_id": 0,
            }},
        ]
        resultado = list(self.col.aggregate(pipeline))
        if resultado:
            return resultado[0]
        return {"libro_id": libro_id, "promedio": None, "total_resenas": 0}

    def libros_mejor_calificados(self, top: int = 5) -> list[dict]:
        pipeline = [
            {"$group": {
                "_id": "$libro.libro_id",
                "promedio": {"$avg": "$calificacion"},
                "total_resenas": {"$sum": 1},
            }},
            {"$sort": {"promedio": -1, "total_resenas": -1}},
            {"$limit": top},
            {"$project": {
                "libro_id": "$_id",
                "promedio": {"$round": ["$promedio", 2]},
                "total_resenas": 1,
                "_id": 0,
            }},
        ]
        return list(self.col.aggregate(pipeline))
