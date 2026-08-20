from pathlib import Path

from flask_frozen import Freezer

from app import create_app
from app.models import Cuidador


BASE_DIR = Path(__file__).resolve().parent

app = create_app()
app.config.update(
    FREEZER_DESTINATION=str(BASE_DIR / "docs"),
    FREEZER_RELATIVE_URLS=True,
    FREEZER_IGNORE_MIMETYPE_WARNINGS=True,
    FREEZER_REMOVE_EXTRA_FILES=True,
)

freezer = Freezer(
    app,
    with_static_files=True,
    with_no_argument_rules=False,
    log_url_for=False,
)


@freezer.register_generator
def paginas_estaticas():
    yield "inicio", {}
    yield "cuidadores.lista", {}
    yield "cuidadores.crear", {}


@freezer.register_generator
def cuidador_detalle_urls():
    with app.app_context():
        for cuidador in Cuidador.query.filter_by(activo=True).all():
            yield "cuidadores.detalle", {"id": cuidador.id}


if __name__ == "__main__":
    freezer.freeze()
    Path(app.config["FREEZER_DESTINATION"], ".nojekyll").touch()
    print("Sitio estático generado correctamente en la carpeta docs/")