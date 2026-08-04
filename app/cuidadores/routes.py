from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.extensions import db
from app.models import Auditoria, Comuna, Cuidador, Especialidad

bp = Blueprint("cuidadores", __name__)


# 1. LISTAR CUIDADORES (CON FILTROS)
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
        query = query.filter(Cuidador.estado_validacion == estado_filtro)

    cuidadores = query.all()

    comunas = [c.nombre for c in Comuna.query.order_by(Comuna.nombre).all()]
    especialidades = [
        e.nombre for e in Especialidad.query.order_by(Especialidad.nombre).all()
    ]
    estados = ["Pendiente", "Aprobado", "Rechazado"]

    filtros = {
        "q": q,
        "comuna": comuna_filtro,
        "especialidad": especialidad_filtro,
        "estado": estado_filtro,
    }

    return render_template(
        "cuidadores/lista.html",
        cuidadores=cuidadores,
        comunas=comunas,
        especialidades=especialidades,
        estados=estados,
        filtros=filtros,
    )


# 2. CREAR CUIDADOR
@bp.route("/crear", methods=["GET", "POST"])
def crear():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        correo = request.form.get("correo")
        telefono = request.form.get("telefono")
        comuna_id = request.form.get("comuna_id")
        especialidad_id = request.form.get("especialidad_id")
        experiencia_anios = request.form.get("experiencia_anios", 0)
        tarifa_diaria = request.form.get("tarifa_diaria")
        descripcion = request.form.get("descripcion", "")

        nuevo_cuidador = Cuidador(
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            comuna_id=int(comuna_id),
            especialidad_id=int(especialidad_id),
            experiencia_anios=int(experiencia_anios),
            tarifa_diaria=int(tarifa_diaria),
            descripcion=descripcion,
        )

        db.session.add(nuevo_cuidador)
        db.session.commit()

        # Auditoría
        log = Auditoria(
            cuidador_id=nuevo_cuidador.id,
            accion="CREACION",
            detalle=f"Se creó el perfil de {nuevo_cuidador.nombre}",
        )
        db.session.add(log)
        db.session.commit()

        flash("Cuidador registrado exitosamente.", "success")
        return redirect(url_for("cuidadores.lista"))

    comunas = Comuna.query.order_by(Comuna.nombre).all()
    especialidades = Especialidad.query.order_by(Especialidad.nombre).all()
    return render_template(
        "cuidadores/crear.html", comunas=comunas, especialidades=especialidades
    )


# 3. DETALLE DE CUIDADOR
@bp.route("/<int:id>", methods=["GET"])
def detalle(id):
    cuidador = Cuidador.query.get_or_404(id)
    return render_template("cuidadores/detalle.html", cuidador=cuidador)


# 4. EDITAR CUIDADOR
@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    cuidador = Cuidador.query.get_or_404(id)

    if request.method == "POST":
        cuidador.nombre = request.form.get("nombre")
        cuidador.correo = request.form.get("correo")
        cuidador.telefono = request.form.get("telefono")
        cuidador.comuna_id = int(request.form.get("comuna_id"))
        cuidador.especialidad_id = int(request.form.get("especialidad_id"))
        cuidador.experiencia_anios = int(
            request.form.get("experiencia_anios", 0)
        )
        cuidador.tarifa_diaria = int(request.form.get("tarifa_diaria"))
        cuidador.descripcion = request.form.get("descripcion", "")

        log = Auditoria(
            cuidador_id=cuidador.id,
            accion="EDICION",
            detalle=f"Se actualizó el perfil de {cuidador.nombre}",
        )
        db.session.add(log)
        db.session.commit()

        flash("Perfil actualizado con éxito.", "success")
        return redirect(url_for("cuidadores.detalle", id=cuidador.id))

    comunas = Comuna.query.order_by(Comuna.nombre).all()
    especialidades = Especialidad.query.order_by(Especialidad.nombre).all()
    return render_template(
        "cuidadores/editar.html",
        cuidador=cuidador,
        comunas=comunas,
        especialidades=especialidades,
    )


# 5. ELIMINAR CUIDADOR (SOFT DELETE)
@bp.route("/<int:id>/eliminar", methods=["POST", "GET"])
def eliminar(id):
    cuidador = Cuidador.query.get_or_404(id)
    cuidador.activo = False

    log = Auditoria(
        cuidador_id=cuidador.id,
        accion="SOFT_DELETE",
        detalle=f"Se desactivó/eliminó lógicamente a {cuidador.nombre}",
    )
    db.session.add(log)
    db.session.commit()

    flash("Cuidador eliminado del sistema.", "warning")
    return redirect(url_for("cuidadores.lista"))