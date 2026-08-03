from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

from .extensions import db


def _configurar_logging(app: Flask) -> None:
    """Configura un archivo de logs con rotación básica."""
    ruta_log = Path(app.instance_path) / "cuida_mayores.log"

    manejador_existente = any(
        isinstance(handler, RotatingFileHandler)
        and Path(handler.baseFilename) == ruta_log
        for handler in app.logger.handlers
    )

    if not manejador_existente:
        manejador = RotatingFileHandler(
            ruta_log,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        manejador.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(module)s | %(message)s"
            )
        )
        manejador.setLevel(logging.INFO)
        app.logger.addHandler(manejador)

    app.logger.setLevel(logging.INFO)


def create_app(test_config: dict | None = None) -> Flask:
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="dev-cambiar-en-produccion",
        SQLALCHEMY_DATABASE_URI="sqlite:///cuida_mayores.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    _configurar_logging(app)
    db.init_app(app)

    from .cuidadores import bp as cuidadores_bp

    app.register_blueprint(cuidadores_bp)

    @app.route("/", methods=["GET"])
    def inicio():
        """Muestra el dashboard principal."""
        try:
            total = db.session.scalar(
                db.select(db.func.count(Cuidador.id))
            ) or 0
            aprobados = db.session.scalar(
                db.select(db.func.count(Cuidador.id)).where(
                    Cuidador.estado_validacion == "Aprobado"
                )
            ) or 0
            pendientes = db.session.scalar(
                db.select(db.func.count(Cuidador.id)).where(
                    Cuidador.estado_validacion == "Pendiente"
                )
            ) or 0
            disponibles = db.session.scalar(
                db.select(db.func.count(Cuidador.id)).where(
                    Cuidador.disponible.is_(True)
                )
            ) or 0

        except Exception as error:
            app.logger.exception(
                "Error al calcular los indicadores del dashboard: %s",
                error,
            )
            total = 0
            aprobados = 0
            pendientes = 0
            disponibles = 0

        return render_template(
            "inicio.html",
            total=total,
            aprobados=aprobados,
            pendientes=pendientes,
            disponibles=disponibles,
        )

    @app.errorhandler(404)
    def no_encontrado(_error):
        """Muestra una página personalizada para recursos inexistentes."""
        return render_template("404.html"), 404

    @app.errorhandler(Exception)
    def error_no_controlado(error):
        """Registra excepciones no controladas y devuelve un error 500."""
        if isinstance(error, HTTPException):
            return error

        db.session.rollback()
        app.logger.error(
            "Excepción global no controlada: %s",
            error,
            exc_info=(type(error), error, error.__traceback__),
        )

        return render_template("500.html"), 500

    with app.app_context():
        db.create_all()

    app.logger.info("Aplicación Cuida a tus Mayores iniciada.")
    return app


from .models import Cuidador  # noqa: E402