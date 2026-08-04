from pathlib import Path

from app import create_app
from app.extensions import db
from app.models import Auditoria, Comuna, Cuidador, Especialidad


def build_app(tmp_path: Path):
    database = tmp_path / "test.db"
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database}",
            "LOG_FILE": str(tmp_path / "app.log"),
        }
    )

    with app.app_context():
        db.session.add_all(
            [
                Comuna(nombre="Santiago"),
                Comuna(nombre="Providencia"),
                Especialidad(nombre="Cuidado general"),
                Especialidad(nombre="TENS"),
            ]
        )
        db.session.commit()

    return app


def datos_validos(**cambios):
    datos = {
        "nombre": "Ana López",
        "correo": "ana@example.com",
        "telefono": "+56 9 1111 2222",
        "comuna_id": "1",
        "especialidad_id": "1",
        "experiencia_anios": "4",
        "tarifa_diaria": "45000",
        "estado_validacion": "Pendiente",
        "descripcion": "Perfil de prueba",
        "disponible": "on",
    }
    datos.update(cambios)
    return datos


def test_crud_completo(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()

    respuesta = client.post(
        "/cuidadores/nuevo",
        data=datos_validos(),
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert b"Ana L" in respuesta.data

    with app.app_context():
        cuidador = db.session.execute(db.select(Cuidador)).scalar_one()
        cuidador_id = cuidador.id

    respuesta = client.post(
        f"/cuidadores/{cuidador_id}/editar",
        data=datos_validos(
            comuna_id="2",
            especialidad_id="2",
            experiencia_anios="5",
            tarifa_diaria="55000",
            estado_validacion="Aprobado",
            descripcion="Perfil actualizado",
        ),
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
    assert b"eliminado del sistema" in respuesta.data

    with app.app_context():
        cuidador = db.session.get(Cuidador, cuidador_id)
        assert cuidador is not None
        assert cuidador.activo is False
        assert db.session.scalar(
            db.select(db.func.count(Auditoria.id))
        ) == 3


def test_backend_rechaza_longitudes_y_formatos_invalidos(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()

    respuesta = client.post(
        "/cuidadores/nuevo",
        data=datos_validos(
            nombre="A" * 51,
            correo="correo-sin-dominio",
            telefono="123-ABC",
            descripcion="D" * 1001,
        ),
    )

    contenido = respuesta.get_data(as_text=True)
    assert respuesta.status_code == 200
    assert "nombre no puede superar los 50 caracteres" in contenido
    assert "Ingresa un correo válido" in contenido
    assert "Ingresa un teléfono válido" in contenido
    assert "descripción no puede superar los 1000 caracteres" in contenido

    with app.app_context():
        assert db.session.execute(
            db.select(Cuidador)
        ).scalar_one_or_none() is None


def test_error_inesperado_hace_rollback_y_se_registra(tmp_path, monkeypatch):
    app = build_app(tmp_path)
    client = app.test_client()

    def commit_con_error():
        raise RuntimeError("base de datos no disponible")

    with app.app_context():
        monkeypatch.setattr(db.session, "commit", commit_con_error)
        respuesta = client.post(
            "/cuidadores/nuevo",
            data=datos_validos(),
        )

        assert db.session.execute(
            db.select(Cuidador)
        ).scalar_one_or_none() is None
        assert db.session.execute(
            db.select(Auditoria)
        ).scalar_one_or_none() is None

    contenido = respuesta.get_data(as_text=True)
    assert respuesta.status_code == 200
    assert "No fue posible registrar el cuidador por un error interno" in contenido

    contenido_log = (tmp_path / "app.log").read_text(encoding="utf-8")
    assert "Error inesperado al registrar un cuidador" in contenido_log
    assert "RuntimeError: base de datos no disponible" in contenido_log
