import re

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Auditoria, Comuna, Cuidador, Especialidad

bp = Blueprint("cuidadores", __name__, url_prefix="/cuidadores")

ESTADOS = ("Pendiente", "Aprobado", "Rechazado")

LARGO_MAX_NOMBRE = 50
LARGO_MAX_CORREO = 120
LARGO_MAX_TELEFONO = 30
LARGO_MAX_DESCRIPCION = 1000

PATRON_CORREO = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$"
)
PATRON_TELEFONO = re.compile(
    r"^(?=(?:\D*\d){8,15}\D*$)\+?\d(?:[\d ()-]*\d)?$"
)


def _texto(campo: str) -> str:
    return request.form.get(campo, "").strip()


def _validar_longitud(
    valor: str, nombre_campo: str, largo_maximo: int, errores: list[str]
) -> bool:
    if len(valor) > largo_maximo:
        errores.append(
            f"El campo {nombre_campo} no puede superar los {largo_maximo} caracteres."
        )
        return False
    return True


def _leer_id(campo: str, nombre_campo: str, errores: list[str]) -> int | None:
    try:
        valor = int(_texto(campo))
        if valor <= 0:
            raise ValueError
        return valor
    except (TypeError, ValueError):
        errores.append(f"Selecciona una {nombre_campo} válida.")
        return None


def _leer_formulario() -> tuple[dict[str, object], list[str]]:
    errores: list[str] = []

    nombre = _texto("nombre")
    correo = _texto("correo").lower()
    telefono = _texto("telefono")
    descripcion = _texto("descripcion")
    estado_validacion = _texto("estado_validacion") or "Pendiente"
    disponible = request.form.get("disponible") == "on"

    if not nombre:
        errores.append("El nombre es obligatorio.")
    else:
        _validar_longitud(nombre, "nombre", LARGO_MAX_NOMBRE, errores)

    if not correo:
        errores.append("El correo es obligatorio.")
    elif _validar_longitud(correo, "correo", LARGO_MAX_CORREO, errores):
        if PATRON_CORREO.fullmatch(correo) is None:
            errores.append("Ingresa un correo válido.")

    if not telefono:
        errores.append("El teléfono es obligatorio.")
    elif _validar_longitud(
        telefono, "teléfono", LARGO_MAX_TELEFONO, errores
    ):
        if PATRON_TELEFONO.fullmatch(telefono) is None:
            errores.append(
                "Ingresa un teléfono válido (entre 8 y 15 dígitos)."
            )

    _validar_longitud(
        descripcion, "descripción", LARGO_MAX_DESCRIPCION, errores
    )

    comuna_id = _leer_id("comuna_id", "comuna", errores)
    if comuna_id is not None and db.session.get(Comuna, comuna_id) is None:
        errores.append("Selecciona una comuna válida.")

    especialidad_id = _leer_id(
        "especialidad_id", "especialidad", errores
    )
    if (
        especialidad_id is not None
        and db.session.get(Especialidad, especialidad_id) is None
    ):
        errores.append("Selecciona una especialidad válida.")

    if estado_validacion not in ESTADOS:
        errores.append("Selecciona un estado de validación válido.")

    try:
        experiencia_anios = int(_texto("experiencia_anios"))
        if experiencia_anios < 0 or experiencia_anios > 60:
            raise ValueError
    except (TypeError, ValueError):
        experiencia_anios = 0
        errores.append("Los años de experiencia deben estar entre 0 y 60.")

    try:
        tarifa_diaria = int(_texto("tarifa_diaria"))
        if tarifa_diaria <= 0:
            raise ValueError
    except (TypeError, ValueError):
        tarifa_diaria = 0
        errores.append("La tarifa diaria debe ser mayor que cero.")

    datos: dict[str, object] = {
        "nombre": nombre,
        "correo": correo,
        "telefono": telefono,
        "comuna_id": comuna_id,
        "especialidad_id": especialidad_id,
        "experiencia_anios": experiencia_anios,
        "tarifa_diaria": tarifa_diaria,
        "descripcion": descripcion,
        "estado_validacion": estado_validacion,
        "disponible": disponible,
    }
    return datos, errores


def _opciones_formulario() -> dict[str, object]:
    return {
        "comunas": Comuna.query.order_by(Comuna.nombre).all(),
        "especialidades": Especialidad.query.order_by(
            Especialidad.nombre
        ).all(),
        "estados": ESTADOS,
    }


@bp.route("/", methods=["GET"])
def lista():
    q = request.args.get("q", "").strip()
    comuna_filtro = request.args.get("comuna", "").strip()
    especialidad_filtro = request.args.get("especialidad", "").strip()
    estado_filtro = request.args.get("estado", "").strip()

    query = Cuidador.query.filter_by(activo=True)

    if q:
        query = query.filter(
            (Cuidador.nombre.ilike(f"%{q}%"))
            | (Cuidador.correo.ilike(f"%{q}%"))
            | (Cuidador.descripcion.ilike(f"%{q}%"))
        )
    if comuna_filtro:
        query = query.join(Cuidador.comuna_rel).filter(
            Comuna.nombre == comuna_filtro
        )
    if especialidad_filtro:
        query = query.join(Cuidador.especialidad_rel).filter(
            Especialidad.nombre == especialidad_filtro
        )
    if estado_filtro:
        query = query.filter(
            Cuidador.estado_validacion == estado_filtro
        )

    return render_template(
        "cuidadores/lista.html",
        cuidadores=query.all(),
        comunas=Comuna.query.order_by(Comuna.nombre).all(),
        especialidades=Especialidad.query.order_by(
            Especialidad.nombre
        ).all(),
        estados=ESTADOS,
        filtros={
            "q": q,
            "comuna": comuna_filtro,
            "especialidad": especialidad_filtro,
            "estado": estado_filtro,
        },
    )


@bp.route("/crear", methods=["GET", "POST"])
@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    if request.method == "POST":
        errores: list[str] = []
        try:
            datos, errores = _leer_formulario()
            if not errores:
                cuidador = Cuidador(**datos)
                db.session.add(cuidador)
                db.session.flush()
                db.session.add(
                    Auditoria(
                        cuidador_id=cuidador.id,
                        accion="CREACION",
                        detalle=f"Se creó el perfil de {cuidador.nombre}",
                    )
                )
                db.session.commit()
        except IntegrityError:
            db.session.rollback()
            errores.append(
                "Ya existe un cuidador registrado con ese correo."
            )
        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Error inesperado al registrar un cuidador."
            )
            errores.append(
                "No fue posible registrar el cuidador por un error interno. "
                "Intenta nuevamente."
            )
        else:
            if not errores:
                flash("Cuidador registrado exitosamente.", "success")
                return redirect(url_for("cuidadores.lista"))

        for error in errores:
            flash(error, "danger")

    return render_template(
        "cuidadores/crear.html",
        cuidador=None,
        titulo="Registrar nuevo cuidador",
        **_opciones_formulario(),
    )


@bp.route("/<int:id>", methods=["GET"])
def detalle(id: int):
    cuidador = Cuidador.query.filter_by(id=id, activo=True).first_or_404()
    return render_template("cuidadores/detalle.html", cuidador=cuidador)


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id: int):
    cuidador = Cuidador.query.filter_by(id=id, activo=True).first_or_404()

    if request.method == "POST":
        errores: list[str] = []
        try:
            datos, errores = _leer_formulario()
            if not errores:
                for campo, valor in datos.items():
                    setattr(cuidador, campo, valor)
                db.session.add(
                    Auditoria(
                        cuidador_id=cuidador.id,
                        accion="EDICION",
                        detalle=(
                            f"Se actualizó el perfil de {cuidador.nombre}"
                        ),
                    )
                )
                db.session.commit()
        except IntegrityError:
            db.session.rollback()
            errores.append(
                "Ya existe otro cuidador registrado con ese correo."
            )
        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Error inesperado al actualizar el cuidador con id %s.",
                id,
            )
            errores.append(
                "No fue posible actualizar el cuidador por un error interno. "
                "Intenta nuevamente."
            )
        else:
            if not errores:
                flash("Perfil actualizado con éxito.", "success")
                return redirect(
                    url_for("cuidadores.detalle", id=cuidador.id)
                )

        for error in errores:
            flash(error, "danger")

    return render_template(
        "cuidadores/crear.html",
        cuidador=cuidador,
        titulo="Editar cuidador",
        **_opciones_formulario(),
    )


@bp.route("/<int:id>/eliminar", methods=["GET", "POST"])
def eliminar(id: int):
    cuidador = Cuidador.query.filter_by(id=id, activo=True).first_or_404()

    if request.method == "POST":
        try:
            cuidador.activo = False
            db.session.add(
                Auditoria(
                    cuidador_id=cuidador.id,
                    accion="SOFT_DELETE",
                    detalle=(
                        f"Se desactivó lógicamente a {cuidador.nombre}"
                    ),
                )
            )
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Error inesperado al eliminar el cuidador con id %s.",
                id,
            )
            flash(
                "No fue posible eliminar el cuidador por un error interno. "
                "Intenta nuevamente.",
                "danger",
            )
        else:
            flash("Cuidador eliminado del sistema.", "warning")
            return redirect(url_for("cuidadores.lista"))

    return render_template(
        "cuidadores/confirmar_eliminar.html", cuidador=cuidador
    )
