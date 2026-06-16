"""
app.py — Punto de entrada principal de la aplicación Flask.
Registra los blueprints de cada colección y configura CORS.
"""

from flask import Flask
from flask_cors import CORS
from config import Config, get_db

# ── Blueprints ────────────────────────────────────────────────────────────────
from routes.libro_routes    import libro_bp
from routes.usuario_routes  import usuario_bp
from routes.prestamo_routes import prestamo_bp
from routes.resena_routes   import resena_bp
from routes.autor_routes    import autor_bp


def create_app():
    """Factory function que crea y configura la app Flask."""

    app = Flask(__name__)
    app.config.from_object(Config)

    # Habilitar CORS para el frontend Vanilla JS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Inicializar la base de datos y guardarla en el contexto de la app
    app.db = get_db()

    # ── Registro de Blueprints ────────────────────────────────────────────────
    app.register_blueprint(libro_bp,    url_prefix="/api/libros")
    app.register_blueprint(usuario_bp,  url_prefix="/api/usuarios")
    app.register_blueprint(prestamo_bp, url_prefix="/api/prestamos")
    app.register_blueprint(resena_bp,   url_prefix="/api/resenas")
    app.register_blueprint(autor_bp,    url_prefix="/api/autores")

    # ── Ruta de salud ─────────────────────────────────────────────────────────
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return {"status": "ok", "message": "Biblioteca API corriendo ✅"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.DEBUG,
    )

