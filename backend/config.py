"""
config.py — Configuración central de la aplicación Flask.
Carga las variables de entorno y establece la conexión con MongoDB.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Cargar variables del archivo .env
load_dotenv()


class Config:
    """Configuración base de la aplicación."""

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "clave_por_defecto_insegura")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    PORT = int(os.getenv("FLASK_PORT", 5000))

    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = os.getenv("DB_NAME", "biblioteca_db")


def get_db():
    """
    Crea y retorna la instancia de la base de datos MongoDB.
    Lanza una excepción si no se puede conectar.
    """
    try:
        client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        # Verificar la conexión
        client.admin.command("ping")
        db = client[Config.DB_NAME]
        print(f"✅ Conectado a MongoDB — Base de datos: '{Config.DB_NAME}'")
        return db
    except ConnectionFailure as e:
        print(f"❌ Error de conexión a MongoDB: {e}")
        raise
