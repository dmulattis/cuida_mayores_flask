import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

from .extensions import db
from .models import Cuidador


def _configurar_logging(app: Flask) -> None:
    archivo_log = Path(
        app.config.get("LOG_FILE") or Path(app.instance_path) / "app.log"
    ).resolve()
    archivo_log.parent.mkdir(parents=True, exist_ok=True)

    for manejador in list(app.logger.handlers):
        if not getattr(manejador, "_cuida_mayores_log", False):
            continue
        if Path(manejador.baseFilename).resolve() == archivo_log:
            return
        app.logger.removeHandler(manejador)
        manejador.close()

    manejador = RotatingFileHandler(
        archivo_log,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    manejador.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        )
    )
    manejador.setLevel(logging.ERROR)
    manejador._cuida_mayores_log = True
    app.logger.addHandler(manejador)

    app.logger.setLevel(logging.INFO)


def create_app(test_config: dict | None = None) -> Flask:
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

    @app.route("/")
    def inicio():
        total = db.session.scalar(
            db.select(db.func.count(Cuidador.id)).where(Cuidador.activo.is_(True))
        ) or 0
        aprobados = db.session.scalar(
            db.select(db.func.count(Cuidador.id)).where(
                Cuidador.activo.is_(True),
                Cuidador.estado_validacion == "Aprobado"
            )
        ) or 0
        pendientes = db.session.scalar(
            db.select(db.func.count(Cuidador.id)).where(
                Cuidador.activo.is_(True),
                Cuidador.estado_validacion == "Pendiente"
            )
        ) or 0
        disponibles = db.session.scalar(
            db.select(db.func.count(Cuidador.id)).where(
                Cuidador.activo.is_(True),
                Cuidador.disponible.is_(True)
            )
        ) or 0
        return render_template(
            "inicio.html",
            total=total,
            aprobados=aprobados,
            pendientes=pendientes,
            disponibles=disponibles,
        )

    @app.errorhandler(404)
    def no_encontrado(_error):
        return render_template("404.html"), 404

    @app.errorhandler(Exception)
    def error_no_controlado(error):
        if isinstance(error, HTTPException):
            return error

        try:
            db.session.rollback()
        except Exception as error_rollback:
            app.logger.exception(
                "Falló el rollback de la sesión.",
                exc_info=(
                    type(error_rollback),
                    error_rollback,
                    error_rollback.__traceback__,
                ),
            )

        app.logger.exception(
            "Excepción no controlada durante una solicitud.",
            exc_info=(type(error), error, error.__traceback__),
        )
        return render_template("500.html"), 500

    with app.app_context():
        db.create_all()

    return app
