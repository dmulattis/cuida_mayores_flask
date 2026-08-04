from pathlib import Path
from flask import Flask, render_template
from .extensions import db
from .models import Cuidador


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
    def error_servidor(_error):
        return render_template("500.html"), 500

    with app.app_context():
        db.create_all()

    return app