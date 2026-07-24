from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

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


def _texto(campo: str) -> str:
    """Obtiene un campo del formulario y elimina espacios en sus extremos."""
    return request.form.get(campo, "").strip()


def _leer_formulario() -> tuple[dict, list[str]]:
    """Lee, normaliza y valida los datos enviados por el formulario.

    Retorna un diccionario listo para crear o actualizar un cuidador y una
    lista con los mensajes de validación encontrados.
    """
    errores: list[str] = []

    nombre = _texto("nombre")
    correo = _texto("correo").lower()
    telefono = _texto("telefono")
    comuna = _texto("comuna")
    especialidad = _texto("especialidad")
    descripcion = _texto("descripcion")
    estado_validacion = _texto("estado_validacion") or "Pendiente"
    disponible = request.form.get("disponible") == "on"

    if not nombre:
        errores.append("El nombre es obligatorio.")
    if not correo or "@" not in correo:
        errores.append("Ingresa un correo válido.")
    if not telefono:
        errores.append("El teléfono es obligatorio.")
    if not comuna:
        errores.append("La comuna es obligatoria.")
    if especialidad not in ESPECIALIDADES:
        errores.append("Selecciona una especialidad válida.")
    if estado_validacion not in ESTADOS:
        errores.append("Selecciona un estado de validación válido.")

    try:
        experiencia_anios = int(request.form.get("experiencia_anios", "0"))
        if experiencia_anios < 0 or experiencia_anios > 60:
            raise ValueError
    except ValueError:
        experiencia_anios = 0
        errores.append("Los años de experiencia deben estar entre 0 y 60.")

    try:
        tarifa_diaria = int(request.form.get("tarifa_diaria", "0"))
        if tarifa_diaria <= 0:
            raise ValueError
    except ValueError:
        tarifa_diaria = 0
        errores.append("La tarifa diaria debe ser mayor que cero.")

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


@bp.route("/")
def lista():
    """Lista los cuidadores y aplica los filtros recibidos por la URL."""
    q = request.args.get("q", "").strip()
    comuna = request.args.get("comuna", "").strip()
    especialidad = request.args.get("especialidad", "").strip()
    estado = request.args.get("estado", "").strip()

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
        db.select(Cuidador.comuna).distinct().order_by(Cuidador.comuna)
    ).scalars().all()

    return render_template(
        "cuidadores/lista.html",
        cuidadores=cuidadores,
        comunas=comunas,
        especialidades=ESPECIALIDADES,
        estados=ESTADOS,
        filtros={"q": q, "comuna": comuna, "especialidad": especialidad, "estado": estado},
    )


@bp.route("/<int:cuidador_id>")
def detalle(cuidador_id: int):
    """Muestra el detalle del cuidador indicado o responde con error 404."""
    cuidador = db.get_or_404(Cuidador, cuidador_id)
    return render_template("cuidadores/detalle.html", cuidador=cuidador)


@bp.route("/nuevo", methods=("GET", "POST"))
def crear():
    """Muestra el formulario y registra un cuidador cuando se envía por POST."""
    if request.method == "POST":
        datos, errores = _leer_formulario()
        if not errores:
            cuidador = Cuidador(**datos)
            db.session.add(cuidador)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                errores.append("Ya existe un cuidador registrado con ese correo.")
            else:
                flash("Cuidador registrado correctamente.", "success")
                return redirect(url_for("cuidadores.detalle", cuidador_id=cuidador.id))

        for error in errores:
            flash(error, "danger")

    return render_template(
        "cuidadores/formulario.html",
        cuidador=None,
        estados=ESTADOS,
        especialidades=ESPECIALIDADES,
        titulo="Registrar cuidador",
    )


@bp.route("/<int:cuidador_id>/editar", methods=("GET", "POST"))
def editar(cuidador_id: int):
    """Muestra el formulario y actualiza el cuidador indicado al recibir POST."""
    cuidador = db.get_or_404(Cuidador, cuidador_id)

    if request.method == "POST":
        datos, errores = _leer_formulario()
        if not errores:
            for campo, valor in datos.items():
                setattr(cuidador, campo, valor)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                errores.append("Ya existe otro cuidador registrado con ese correo.")
            else:
                flash("Datos actualizados correctamente.", "success")
                return redirect(url_for("cuidadores.detalle", cuidador_id=cuidador.id))

        for error in errores:
            flash(error, "danger")

    return render_template(
        "cuidadores/formulario.html",
        cuidador=cuidador,
        estados=ESTADOS,
        especialidades=ESPECIALIDADES,
        titulo="Editar cuidador",
    )


@bp.route("/<int:cuidador_id>/eliminar", methods=("GET", "POST"))
def eliminar(cuidador_id: int):
    """Solicita confirmación y elimina el cuidador indicado mediante POST."""
    cuidador = db.get_or_404(Cuidador, cuidador_id)
    if request.method == "POST":
        db.session.delete(cuidador)
        db.session.commit()
        flash("Cuidador eliminado correctamente.", "success")
        return redirect(url_for("cuidadores.lista"))

    return render_template("cuidadores/confirmar_eliminar.html", cuidador=cuidador)
