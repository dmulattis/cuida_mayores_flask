import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, render_template

from .extensions import db
from .models import Cuidador


def _configurar_logging(app: Flask) -> None:
    archivo_log = Path(
        app.config.get("LOG_FILE") or Path(app.instance_path) / "app.log"
    ).resolve()
    archivo_log.parent.mkdir(parents=True, exist_ok=True)

    manejador_existente = any(
        isinstance(manejador, RotatingFileHandler)
        and Path(manejador.baseFilename).resolve() == archivo_log
        for manejador in app.logger.handlers
    )
    if not manejador_existente:
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

    @app.errorhandler(500)
    def error_servidor(error):
        app.logger.error("Error interno no controlado: %s", error)
        return render_template("500.html"), 500

    with app.app_context():
        db.create_all()

    return app
