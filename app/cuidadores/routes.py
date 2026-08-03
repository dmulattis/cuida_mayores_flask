from __future__ import annotations

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
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from app.extensions import db
from app.models import Cuidador


bp = Blueprint("cuidadores", __name__, url_prefix="/cuidadores")

ESTADOS = ("Pendiente", "Aprobado", "Rechazado")
ESPECIALIDADES = (
    "Acompañamiento",
    "Cuidado general",
    "Enfermería",
    "Kinesiología",
    "TENS",
    "Otro",
)

# Reglas de validación centralizadas.
EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}$"
)
TELEFONO_REGEX = re.compile(r"^\+?\d{8,15}$")

NOMBRE_MIN = 3
NOMBRE_MAX = 120
CORREO_MAX = 120
TELEFONO_MAX = 16
COMUNA_MIN = 2
COMUNA_MAX = 80
DESCRIPCION_MAX = 1000
EXPERIENCIA_MIN = 0
EXPERIENCIA_MAX = 60
TARIFA_MINIMA = 10_000
TARIFA_MAXIMA = 500_000


def _normalizar_texto(valor: str) -> str:
    """Elimina espacios sobrantes y normaliza espacios internos."""
    return re.sub(r"\s+", " ", valor).strip()


def _texto_formulario(campo: str) -> str:
    """Obtiene y normaliza un campo de texto enviado por formulario."""
    return _normalizar_texto(request.form.get(campo, ""))


def _texto_consulta(campo: str, largo_maximo: int = 120) -> str:
    """Obtiene, normaliza y limita un parámetro recibido por URL."""
    valor = _normalizar_texto(request.args.get(campo, ""))
    return valor[:largo_maximo]


def _normalizar_telefono(valor: str) -> str:
    """Elimina espacios, guiones, puntos y paréntesis del teléfono."""
    return re.sub(r"[\s\-().]", "", valor)


def _validar_largo(
    valor: str,
    nombre_campo: str,
    minimo: int,
    maximo: int,
    errores: list[str],
) -> None:
    """Agrega un error cuando el largo del valor está fuera del rango."""
    if not minimo <= len(valor) <= maximo:
        errores.append(
            f"{nombre_campo} debe tener entre {minimo} y {maximo} caracteres."
        )


def _leer_formulario() -> tuple[dict, list[str]]:
    """Lee, normaliza y valida los datos del formulario de cuidadores."""
    errores: list[str] = []

    nombre = _texto_formulario("nombre")
    correo = _texto_formulario("correo").lower()
    telefono = _normalizar_telefono(_texto_formulario("telefono"))
    comuna = _texto_formulario("comuna")
    especialidad = _texto_formulario("especialidad")
    descripcion = _texto_formulario("descripcion")
    estado_validacion = _texto_formulario("estado_validacion") or "Pendiente"
    disponible = request.form.get("disponible") == "on"

    if nombre:
        _validar_largo(nombre, "El nombre", NOMBRE_MIN, NOMBRE_MAX, errores)
    else:
        errores.append("El nombre es obligatorio.")

    if not correo:
        errores.append("El correo es obligatorio.")
    elif len(correo) > CORREO_MAX:
        errores.append(f"El correo no puede superar {CORREO_MAX} caracteres.")
    elif not EMAIL_REGEX.fullmatch(correo):
        errores.append("Ingresa un correo electrónico válido.")

    if not telefono:
        errores.append("El teléfono es obligatorio.")
    elif len(telefono) > TELEFONO_MAX:
        errores.append("El teléfono ingresado es demasiado largo.")
    elif not TELEFONO_REGEX.fullmatch(telefono):
        errores.append(
            "El teléfono debe contener entre 8 y 15 dígitos "
            "y puede comenzar con el símbolo +."
        )

    if comuna:
        _validar_largo(comuna, "La comuna", COMUNA_MIN, COMUNA_MAX, errores)
    else:
        errores.append("La comuna es obligatoria.")

    if especialidad not in ESPECIALIDADES:
        errores.append("Selecciona una especialidad válida.")

    if estado_validacion not in ESTADOS:
        errores.append("Selecciona un estado de validación válido.")

    if len(descripcion) > DESCRIPCION_MAX:
        errores.append(
            f"La descripción no puede superar {DESCRIPCION_MAX} caracteres."
        )

    try:
        experiencia_anios = int(request.form.get("experiencia_anios", "0"))
        if not EXPERIENCIA_MIN <= experiencia_anios <= EXPERIENCIA_MAX:
            raise ValueError
    except (TypeError, ValueError):
        experiencia_anios = 0
        errores.append(
            f"Los años de experiencia deben estar entre "
            f"{EXPERIENCIA_MIN} y {EXPERIENCIA_MAX}."
        )

    try:
        tarifa_diaria = int(request.form.get("tarifa_diaria", "0"))
        if not TARIFA_MINIMA <= tarifa_diaria <= TARIFA_MAXIMA:
            raise ValueError
    except (TypeError, ValueError):
        tarifa_diaria = 0
        minimo = f"${TARIFA_MINIMA:,}".replace(",", ".")
        maximo = f"${TARIFA_MAXIMA:,}".replace(",", ".")
        errores.append(
            f"La tarifa diaria debe estar entre {minimo} y {maximo}."
        )

    datos = {
        "nombre": nombre,
        "correo": correo,
        "telefono": telefono,
        "comuna": comuna,
        "especialidad": especialidad,
        "experiencia_anios": experiencia_anios,
        "tarifa_diaria": tarifa_diaria,
        "disponible": disponible,
        "estado_validacion": estado_validacion,
        "descripcion": descripcion,
    }

    return datos, errores


@bp.route("/", methods=["GET"])
def lista():
    """Muestra y filtra el listado de cuidadores."""
    q = _texto_consulta("q")
    comuna = _texto_consulta("comuna", COMUNA_MAX)
    especialidad = _texto_consulta("especialidad", 100)
    estado = _texto_consulta("estado", 20)

    try:
        stmt = db.select(Cuidador).order_by(Cuidador.nombre)

        if q:
            termino = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Cuidador.nombre.ilike(termino),
                    Cuidador.correo.ilike(termino),
                    Cuidador.descripcion.ilike(termino),
                )
            )

        if comuna:
            stmt = stmt.where(Cuidador.comuna == comuna)
        if especialidad:
            stmt = stmt.where(Cuidador.especialidad == especialidad)
        if estado:
            stmt = stmt.where(Cuidador.estado_validacion == estado)

        cuidadores = db.session.execute(stmt).scalars().all()
        comunas = db.session.execute(
            db.select(Cuidador.comuna)
            .distinct()
            .order_by(Cuidador.comuna)
        ).scalars().all()

    except Exception as error:
        current_app.logger.exception(
            "Error al consultar el listado de cuidadores: %s",
            error,
        )
        flash("No fue posible cargar el listado de cuidadores.", "danger")
        cuidadores = []
        comunas = []

    return render_template(
        "cuidadores/lista.html",
        cuidadores=cuidadores,
        comunas=comunas,
        especialidades=ESPECIALIDADES,
        estados=ESTADOS,
        filtros={
            "q": q,
            "comuna": comuna,
            "especialidad": especialidad,
            "estado": estado,
        },
    )


@bp.route("/<int:cuidador_id>", methods=["GET"])
def detalle(cuidador_id: int):
    """Muestra el detalle de un cuidador."""
    try:
        cuidador = db.get_or_404(Cuidador, cuidador_id)
        return render_template("cuidadores/detalle.html", cuidador=cuidador)
    except HTTPException:
        raise
    except Exception as error:
        current_app.logger.exception(
            "Error al cargar el cuidador %s: %s",
            cuidador_id,
            error,
        )
        flash("No fue posible cargar el perfil solicitado.", "danger")
        return redirect(url_for("cuidadores.lista"))


@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    """Muestra el formulario y registra un nuevo cuidador."""
    if request.method == "POST":
        try:
            datos, errores = _leer_formulario()

            if not errores:
                cuidador = Cuidador(**datos)
                db.session.add(cuidador)
                db.session.commit()

                current_app.logger.info(
                    "Cuidador creado correctamente. id=%s correo=%s",
                    cuidador.id,
                    cuidador.correo,
                )
                flash("Cuidador registrado correctamente.", "success")
                return redirect(
                    url_for(
                        "cuidadores.detalle",
                        cuidador_id=cuidador.id,
                    )
                )

        except IntegrityError as error:
            db.session.rollback()
            current_app.logger.warning(
                "Intento de registrar un correo duplicado: %s",
                error,
            )
            errores = ["Ya existe un cuidador registrado con ese correo."]

        except Exception as error:
            db.session.rollback()
            current_app.logger.exception(
                "Error inesperado al registrar un cuidador: %s",
                error,
            )
            errores = [
                "Ocurrió un error inesperado al registrar el cuidador."
            ]

        for mensaje in errores:
            flash(mensaje, "danger")

    return render_template(
        "cuidadores/formulario.html",
        cuidador=None,
        estados=ESTADOS,
        especialidades=ESPECIALIDADES,
        titulo="Registrar cuidador",
    )


@bp.route("/<int:cuidador_id>/editar", methods=["GET", "POST"])
def editar(cuidador_id: int):
    """Muestra el formulario y actualiza un cuidador."""
    try:
        cuidador = db.get_or_404(Cuidador, cuidador_id)
    except HTTPException:
        raise
    except Exception as error:
        current_app.logger.exception(
            "Error al buscar el cuidador %s: %s",
            cuidador_id,
            error,
        )
        flash("No fue posible cargar el cuidador para editarlo.", "danger")
        return redirect(url_for("cuidadores.lista"))

    if request.method == "POST":
        try:
            datos, errores = _leer_formulario()

            if not errores:
                for campo, valor in datos.items():
                    setattr(cuidador, campo, valor)

                db.session.commit()
                current_app.logger.info(
                    "Cuidador actualizado correctamente. id=%s",
                    cuidador.id,
                )
                flash("Datos actualizados correctamente.", "success")
                return redirect(
                    url_for(
                        "cuidadores.detalle",
                        cuidador_id=cuidador.id,
                    )
                )

        except IntegrityError as error:
            db.session.rollback()
            current_app.logger.warning(
                "Correo duplicado al actualizar cuidador id=%s: %s",
                cuidador_id,
                error,
            )
            errores = [
                "Ya existe otro cuidador registrado con ese correo."
            ]

        except Exception as error:
            db.session.rollback()
            current_app.logger.exception(
                "Error inesperado al actualizar cuidador id=%s: %s",
                cuidador_id,
                error,
            )
            errores = [
                "Ocurrió un error inesperado al actualizar el cuidador."
            ]

        for mensaje in errores:
            flash(mensaje, "danger")

    return render_template(
        "cuidadores/formulario.html",
        cuidador=cuidador,
        estados=ESTADOS,
        especialidades=ESPECIALIDADES,
        titulo="Editar cuidador",
    )


@bp.route("/<int:cuidador_id>/eliminar", methods=["GET", "POST"])
def eliminar(cuidador_id: int):
    """Muestra la confirmación y elimina un cuidador."""
    try:
        cuidador = db.get_or_404(Cuidador, cuidador_id)
    except HTTPException:
        raise
    except Exception as error:
        current_app.logger.exception(
            "Error al buscar cuidador para eliminar. id=%s: %s",
            cuidador_id,
            error,
        )
        flash("No fue posible cargar el cuidador.", "danger")
        return redirect(url_for("cuidadores.lista"))

    if request.method == "POST":
        try:
            db.session.delete(cuidador)
            db.session.commit()

            current_app.logger.info(
                "Cuidador eliminado correctamente. id=%s",
                cuidador_id,
            )
            flash("Cuidador eliminado correctamente.", "success")
            return redirect(url_for("cuidadores.lista"))

        except Exception as error:
            db.session.rollback()
            current_app.logger.exception(
                "Error inesperado al eliminar cuidador id=%s: %s",
                cuidador_id,
                error,
            )
            flash(
                "Ocurrió un error inesperado al eliminar el cuidador.",
                "danger",
            )

    return render_template(
        "cuidadores/confirmar_eliminar.html",
        cuidador=cuidador,
    )