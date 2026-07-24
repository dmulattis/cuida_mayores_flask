from pathlib import Path

from app import create_app
from app.extensions import db
from app.models import Cuidador


def build_app(tmp_path: Path):
    """Crea una aplicación de prueba con una base SQLite temporal y aislada."""
    database = tmp_path / "test.db"
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database}",
        }
    )
    return app


def test_crud_completo(tmp_path):
    """Comprueba el flujo completo de creación, edición y eliminación."""
    app = build_app(tmp_path)
    client = app.test_client()

    respuesta = client.post(
        "/cuidadores/nuevo",
        data={
            "nombre": "Ana López",
            "correo": "ana@example.com",
            "telefono": "+56 9 1111 2222",
            "comuna": "Santiago",
            "especialidad": "Cuidado general",
            "experiencia_anios": "4",
            "tarifa_diaria": "45000",
            "estado_validacion": "Pendiente",
            "descripcion": "Perfil de prueba",
            "disponible": "on",
        },
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert b"Ana L" in respuesta.data

    with app.app_context():
        cuidador = db.session.execute(db.select(Cuidador)).scalar_one()
        cuidador_id = cuidador.id

    respuesta = client.post(
        f"/cuidadores/{cuidador_id}/editar",
        data={
            "nombre": "Ana López",
            "correo": "ana@example.com",
            "telefono": "+56 9 1111 2222",
            "comuna": "Providencia",
            "especialidad": "TENS",
            "experiencia_anios": "5",
            "tarifa_diaria": "55000",
            "estado_validacion": "Aprobado",
            "descripcion": "Perfil actualizado",
            "disponible": "on",
        },
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert b"Providencia" in respuesta.data
    assert b"Aprobado" in respuesta.data

    respuesta = client.post(
        f"/cuidadores/{cuidador_id}/eliminar",
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert b"eliminado correctamente" in respuesta.data

    with app.app_context():
        assert db.session.execute(db.select(Cuidador)).scalar_one_or_none() is None
