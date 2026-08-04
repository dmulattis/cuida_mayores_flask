from pathlib import Path

import pytest

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


def registrar(client, **cambios):
    return client.post(
        "/cuidadores/nuevo",
        data=datos_validos(**cambios),
        follow_redirects=True,
    )


def test_inicio_listado_y_filtros(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()

    registrar(client)
    registrar(
        client,
        nombre="Beatriz Soto",
        correo="beatriz@example.com",
        telefono="+56 9 3333 4444",
        comuna_id="2",
        especialidad_id="2",
        estado_validacion="Aprobado",
    )

    inicio = client.get("/")
    assert inicio.status_code == 200
    assert "Total registrados" in inicio.get_data(as_text=True)

    listado = client.get("/cuidadores/")
    contenido_listado = listado.get_data(as_text=True)
    assert listado.status_code == 200
    assert "Ana López" in contenido_listado
    assert "Beatriz Soto" in contenido_listado

    filtrado = client.get(
        "/cuidadores/",
        query_string={
            "q": "Beatriz",
            "comuna": "Providencia",
            "especialidad": "TENS",
            "estado": "Aprobado",
        },
    )
    contenido_filtrado = filtrado.get_data(as_text=True)
    assert filtrado.status_code == 200
    assert "Beatriz Soto" in contenido_filtrado
    assert "Ana López" not in contenido_filtrado


def test_crud_completo_con_auditoria_y_borrado_logico(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()

    respuesta = registrar(client)
    assert respuesta.status_code == 200
    assert b"Ana L" in respuesta.data

    with app.app_context():
        cuidador = db.session.execute(db.select(Cuidador)).scalar_one()
        cuidador_id = cuidador.id

    detalle = client.get(f"/cuidadores/{cuidador_id}")
    assert detalle.status_code == 200
    assert b"ana@example.com" in detalle.data

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

    confirmacion = client.get(f"/cuidadores/{cuidador_id}/eliminar")
    assert confirmacion.status_code == 200
    assert "Desactivar perfil" in confirmacion.get_data(as_text=True)

    respuesta = client.post(
        f"/cuidadores/{cuidador_id}/eliminar",
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert b"eliminado del sistema" in respuesta.data
    assert client.get(f"/cuidadores/{cuidador_id}").status_code == 404

    with app.app_context():
        cuidador = db.session.get(Cuidador, cuidador_id)
        assert cuidador is not None
        assert cuidador.activo is False
        assert db.session.scalar(
            db.select(db.func.count(Auditoria.id))
        ) == 3


@pytest.mark.parametrize(
    ("cambios", "mensaje"),
    [
        ({"nombre": ""}, "El nombre es obligatorio"),
        ({"nombre": "A" * 51}, "nombre no puede superar los 50 caracteres"),
        ({"correo": ""}, "El correo es obligatorio"),
        (
            {"correo": ("a" * 109) + "@example.com"},
            "correo no puede superar los 120 caracteres",
        ),
        ({"correo": "correo-sin-dominio"}, "Ingresa un correo válido"),
        ({"telefono": ""}, "El teléfono es obligatorio"),
        (
            {"telefono": "+56 " + ("1 - " * 12)},
            "teléfono no puede superar los 30 caracteres",
        ),
        ({"telefono": "123-ABC"}, "Ingresa un teléfono válido"),
        (
            {"descripcion": "D" * 1001},
            "descripción no puede superar los 1000 caracteres",
        ),
        (
            {"estado_validacion": "Desconocido"},
            "Selecciona un estado de validación válido",
        ),
        ({"tarifa_diaria": "0"}, "La tarifa diaria debe ser mayor que cero"),
    ],
)
def test_crear_rechaza_datos_invalidos(tmp_path, cambios, mensaje):
    app = build_app(tmp_path)
    client = app.test_client()

    respuesta = registrar(client, **cambios)

    assert respuesta.status_code == 200
    assert mensaje in respuesta.get_data(as_text=True)
    with app.app_context():
        assert db.session.execute(
            db.select(Cuidador)
        ).scalar_one_or_none() is None


@pytest.mark.parametrize(
    ("campo", "mensaje"),
    [
        ("comuna_id", "Selecciona una comuna válida"),
        ("especialidad_id", "Selecciona una especialidad válida"),
    ],
)
def test_rechaza_relaciones_inexistentes(tmp_path, campo, mensaje):
    app = build_app(tmp_path)
    client = app.test_client()

    respuesta = registrar(client, **{campo: "999"})

    assert respuesta.status_code == 200
    assert mensaje in respuesta.get_data(as_text=True)


@pytest.mark.parametrize("experiencia", ["-1", "61"])
def test_rechaza_experiencia_fuera_de_rango(tmp_path, experiencia):
    app = build_app(tmp_path)
    client = app.test_client()

    respuesta = registrar(client, experiencia_anios=experiencia)

    assert respuesta.status_code == 200
    assert (
        "Los años de experiencia deben estar entre 0 y 60"
        in respuesta.get_data(as_text=True)
    )


def test_editar_aplica_validaciones_backend(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()
    registrar(client)

    with app.app_context():
        cuidador_id = db.session.scalar(db.select(Cuidador.id))

    respuesta = client.post(
        f"/cuidadores/{cuidador_id}/editar",
        data=datos_validos(nombre="A" * 51),
    )

    assert respuesta.status_code == 200
    assert (
        "nombre no puede superar los 50 caracteres"
        in respuesta.get_data(as_text=True)
    )
    with app.app_context():
        assert db.session.get(Cuidador, cuidador_id).nombre == "Ana López"


def test_crear_rechaza_correo_duplicado(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()
    registrar(client)

    respuesta = registrar(client, nombre="Otra persona")

    assert respuesta.status_code == 200
    assert (
        "Ya existe un cuidador registrado con ese correo"
        in respuesta.get_data(as_text=True)
    )
    with app.app_context():
        assert db.session.scalar(
            db.select(db.func.count(Cuidador.id))
        ) == 1
        assert db.session.scalar(
            db.select(db.func.count(Auditoria.id))
        ) == 1


def test_editar_rechaza_correo_duplicado(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()
    registrar(client)
    registrar(
        client,
        nombre="Beatriz Soto",
        correo="beatriz@example.com",
        telefono="+56 9 3333 4444",
    )

    with app.app_context():
        beatriz_id = db.session.scalar(
            db.select(Cuidador.id).where(
                Cuidador.correo == "beatriz@example.com"
            )
        )

    respuesta = client.post(
        f"/cuidadores/{beatriz_id}/editar",
        data=datos_validos(nombre="Beatriz Soto"),
    )

    assert respuesta.status_code == 200
    assert (
        "Ya existe un cuidador registrado con ese correo"
        in respuesta.get_data(as_text=True)
    )
    with app.app_context():
        beatriz = db.session.get(Cuidador, beatriz_id)
        assert beatriz.correo == "beatriz@example.com"
        assert db.session.scalar(
            db.select(db.func.count(Auditoria.id))
        ) == 2


def test_error_en_crud_hace_rollback_y_se_registra(
    tmp_path, monkeypatch
):
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
    assert "Traceback (most recent call last)" in contenido_log
    assert "RuntimeError: base de datos no disponible" in contenido_log


def test_respuestas_404_y_405_conservan_estado_http(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()

    no_encontrado = client.get("/ruta-inexistente")
    metodo_no_permitido = client.post("/cuidadores/")

    assert no_encontrado.status_code == 404
    assert "Página no encontrada" in no_encontrado.get_data(as_text=True)
    assert metodo_no_permitido.status_code == 405


def test_manejador_global_hace_rollback_registra_traceback_y_responde_500(
    tmp_path,
):
    app = build_app(tmp_path)

    def provocar_error():
        db.session.add(
            Auditoria(
                accion="PRUEBA_ERROR",
                detalle="Este registro debe revertirse.",
            )
        )
        raise RuntimeError("fallo global de prueba")

    app.add_url_rule(
        "/prueba/error-global",
        endpoint="error_global_prueba",
        view_func=provocar_error,
    )
    client = app.test_client()

    respuesta = client.get("/prueba/error-global")

    contenido = respuesta.get_data(as_text=True)
    assert respuesta.status_code == 500
    assert "Ocurrió un error inesperado" in contenido
    assert "fallo global de prueba" not in contenido
    with app.app_context():
        assert db.session.execute(
            db.select(Auditoria)
        ).scalar_one_or_none() is None

    contenido_log = (tmp_path / "app.log").read_text(encoding="utf-8")
    assert "Excepción no controlada durante una solicitud" in contenido_log
    assert "Traceback (most recent call last)" in contenido_log
    assert "RuntimeError: fallo global de prueba" in contenido_log
