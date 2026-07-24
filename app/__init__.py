from pathlib import Path

from flask import Flask, render_template

from .extensions import db


def create_app(test_config: dict | None = None) -> Flask:
    """Crea y configura la aplicación Flask y sus extensiones.

    Si se entrega ``test_config``, sus valores reemplazan la configuración
    predeterminada para facilitar la ejecución de pruebas automatizadas.
    """
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
        """Muestra el panel principal con estadísticas de los cuidadores."""
        total = db.session.scalar(db.select(db.func.count(Cuidador.id))) or 0
        aprobados = db.session.scalar(
            db.select(db.func.count(Cuidador.id)).where(Cuidador.estado_validacion == "Aprobado")
        ) or 0
        pendientes = db.session.scalar(
            db.select(db.func.count(Cuidador.id)).where(Cuidador.estado_validacion == "Pendiente")
        ) or 0
        disponibles = db.session.scalar(
            db.select(db.func.count(Cuidador.id)).where(Cuidador.disponible.is_(True))
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
        """Renderiza una página personalizada cuando una ruta no existe."""
        return render_template("404.html"), 404

    with app.app_context():
        db.create_all()

    return app


from .models import Cuidador  # noqa: E402
