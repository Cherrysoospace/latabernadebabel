"""
prestamo_service.py — Lógica de negocio para la colección 'prestamos'.

Responsabilidades:
    - Operaciones CRUD sobre la colección 'prestamos'.
    - Lógica de préstamo: verificar disponibilidad, calcular duración por membresía.
    - Lógica de devolución: marcar libro como disponible y cerrar el préstamo.
    - Actualización automática de préstamos vencidos.
    - Validación de modelo antes de persistir.
"""

from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.database import Database

from models.prestamo_model import Prestamo, DURACION_POR_MEMBRESIA
from models.libro_model import Libro
from models.usuario_model import Usuario


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _to_object_id(id_str: str) -> ObjectId:
    """Convierte un string a ObjectId. Lanza ValueError si es inválido."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise ValueError(f"ID inválido: '{id_str}'")


def _serializar(doc: dict) -> dict:
    """Convierte ObjectId a string para que Flask pueda serializar a JSON."""
    if doc:
        for campo in ("_id", "usuario_id", "libro_id"):
            if campo in doc and isinstance(doc[campo], ObjectId):
                doc[campo] = str(doc[campo])
    return doc


# ─── Service ──────────────────────────────────────────────────────────────────

class PrestamoService:
    """
    Capa de servicio para la colección 'prestamos'.
    Recibe la instancia de base de datos (db) inyectada desde la app Flask.
    Coordina cambios en las colecciones 'libros' y 'usuarios' cuando es necesario.
    """

    def __init__(self, db: Database):
        self.col = db[Prestamo.COLECCION]
        self.col_libros = db[Libro.COLECCION]
        self.col_usuarios = db[Usuario.COLECCION]

    # ── CREATE ────────────────────────────────────────────────────────────────

    def crear(self, datos: dict) -> dict:
        """
        Registra un nuevo préstamo aplicando las reglas de negocio:
            1. Verifica que el libro exista y esté disponible.
            2. Verifica que el usuario exista y esté activo.
            3. Calcula la duración según la membresía del usuario.
            4. Marca el libro como no disponible.
            5. Agrega el préstamo al historial del usuario.

        Args:
            datos: Debe contener 'usuario_id' y 'libro_id'.
                   Opcionalmente 'dias' para sobreescribir la duración.

        Returns:
            El documento del préstamo insertado.

        Raises:
            ValueError: Si no se cumplen las reglas de negocio.
        """
        usuario_oid = _to_object_id(datos.get("usuario_id", ""))
        libro_oid = _to_object_id(datos.get("libro_id", ""))

        # 1. Verificar libro
        libro = self.col_libros.find_one({"_id": libro_oid})
        if not libro:
            raise ValueError("El libro especificado no existe.")
        if not libro.get("disponible", False):
            raise ValueError(f"El libro '{libro.get('titulo')}' no está disponible.")

        # 2. Verificar usuario
        usuario = self.col_usuarios.find_one({"_id": usuario_oid})
        if not usuario:
            raise ValueError("El usuario especificado no existe.")
        if not usuario.get("activo", False):
            raise ValueError("La cuenta del usuario no está activa.")

        # 3. Calcular duración
        membresia = usuario.get("membresia", "basica")
        dias = datos.get("dias") or DURACION_POR_MEMBRESIA.get(membresia, 14)

        # 4. Crear el préstamo
        prestamo = Prestamo.crear_con_duracion(
            usuario_id=usuario_oid,
            libro_id=libro_oid,
            dias=int(dias),
        )

        errores = prestamo.validar()
        if errores:
            raise ValueError(errores)

        doc = prestamo.to_dict()
        self.col.insert_one(doc)

        # 5. Marcar libro como no disponible
        self.col_libros.update_one({"_id": libro_oid}, {"$set": {"disponible": False}})

        # 6. Agregar al historial del usuario (sin duplicados)
        self.col_usuarios.update_one(
            {"_id": usuario_oid},
            {"$addToSet": {"historial": prestamo._id}},
        )

        return _serializar(doc)

    # ── READ ──────────────────────────────────────────────────────────────────

    def obtener_todos(self, skip: int = 0, limit: int = 20) -> list[dict]:
        """Retorna una lista paginada de todos los préstamos."""
        docs = self.col.find({}).skip(skip).limit(limit)
        return [_serializar(d) for d in docs]

    def obtener_por_id(self, prestamo_id: str) -> dict | None:
        """Retorna un préstamo completo por su _id."""
        oid = _to_object_id(prestamo_id)
        doc = self.col.find_one({"_id": oid})
        return _serializar(doc) if doc else None

    def obtener_por_usuario(self, usuario_id: str) -> list[dict]:
        """Retorna todos los préstamos de un usuario específico."""
        oid = _to_object_id(usuario_id)
        docs = self.col.find({"usuario_id": oid})
        return [_serializar(d) for d in docs]

    def obtener_activos(self) -> list[dict]:
        """Retorna todos los préstamos con estado 'activo'."""
        docs = self.col.find({"estado": "activo"})
        return [_serializar(d) for d in docs]

    def obtener_vencidos(self) -> list[dict]:
        """
        Retorna préstamos activos cuya fecha_fin ya pasó.
        También los marca como 'vencido' en la base de datos.
        """
        ahora = datetime.now(timezone.utc)
        filtro = {"estado": "activo", "fecha_fin": {"$lt": ahora}}

        # Actualizar estado en la BD antes de retornarlos
        self.col.update_many(filtro, {"$set": {"estado": "vencido"}})

        docs = self.col.find({"estado": "vencido"})
        return [_serializar(d) for d in docs]

    # ── UPDATE / DEVOLUCIÓN ───────────────────────────────────────────────────

    def devolver(self, prestamo_id: str) -> dict | None:
        """
        Procesa la devolución de un préstamo:
            1. Cambia el estado a 'devuelto'.
            2. Registra la fecha real de devolución.
            3. Marca el libro como disponible nuevamente.

        Returns:
            El documento del préstamo actualizado.

        Raises:
            ValueError: Si el préstamo no existe o ya fue devuelto.
        """
        oid = _to_object_id(prestamo_id)
        prestamo = self.col.find_one({"_id": oid})

        if not prestamo:
            raise ValueError("El préstamo especificado no existe.")
        if prestamo.get("estado") == "devuelto":
            raise ValueError("Este préstamo ya fue devuelto.")

        ahora = datetime.now(timezone.utc)

        # 1. Actualizar préstamo
        resultado = self.col.find_one_and_update(
            {"_id": oid},
            {"$set": {"estado": "devuelto", "fecha_devolucion": ahora}},
            return_document=True,
        )

        # 2. Marcar libro como disponible
        self.col_libros.update_one(
            {"_id": prestamo["libro_id"]},
            {"$set": {"disponible": True}},
        )

        return _serializar(resultado) if resultado else None

    def actualizar_estado(self, prestamo_id: str, estado: str) -> dict | None:
        """
        Actualiza manualmente el estado de un préstamo.
        Estados válidos: 'activo', 'devuelto', 'vencido'.
        """
        estados_validos = {"activo", "devuelto", "vencido"}
        if estado not in estados_validos:
            raise ValueError(f"Estado no válido. Opciones: {sorted(estados_validos)}")

        oid = _to_object_id(prestamo_id)
        resultado = self.col.find_one_and_update(
            {"_id": oid},
            {"$set": {"estado": estado}},
            return_document=True,
        )
        return _serializar(resultado) if resultado else None

    # ── DELETE ────────────────────────────────────────────────────────────────

    def eliminar(self, prestamo_id: str) -> bool:
        """
        Elimina un préstamo por su _id.

        Returns:
            True si se eliminó, False si no se encontró.
        """
        oid = _to_object_id(prestamo_id)
        resultado = self.col.delete_one({"_id": oid})
        return resultado.deleted_count > 0

    # ── ESTADÍSTICAS ──────────────────────────────────────────────────────────

    def contar_por_estado(self) -> list[dict]:
        """
        Agrega y cuenta préstamos agrupados por estado.
        """
        pipeline = [
            {"$group": {"_id": "$estado", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
            {"$project": {"estado": "$_id", "total": 1, "_id": 0}},
        ]
        return list(self.col.aggregate(pipeline))

    def usuarios_con_mas_prestamos(self, top: int = 5) -> list[dict]:
        """
        Retorna los 'top' usuarios con más préstamos registrados.
        """
        pipeline = [
            {"$group": {"_id": "$usuario_id", "total_prestamos": {"$sum": 1}}},
            {"$sort": {"total_prestamos": -1}},
            {"$limit": top},
            {"$project": {"usuario_id": "$_id", "total_prestamos": 1, "_id": 0}},
        ]
        resultados = list(self.col.aggregate(pipeline))
        # Serializar los ObjectId de usuario_id
        for r in resultados:
            if isinstance(r.get("usuario_id"), ObjectId):
                r["usuario_id"] = str(r["usuario_id"])
        return resultados
