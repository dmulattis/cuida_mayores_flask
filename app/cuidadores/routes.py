import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError, DataError, OperationalError, SQLAlchemyError
from app.extensions import db
from app.models import Cuidador, Comuna, Especialidad, Auditoria

# Configuración del registrador de errores (logging)
logger = logging.getLogger(__name__)

# Definición del Blueprint para la sección de cuidadores
bp = Blueprint('cuidadores', __name__)


@bp.route('/', methods=['GET'])
def lista():
    """Lista todos los cuidadores activos con soporte para búsqueda y filtros."""
    try:
        q = request.args.get('q', '').strip()
        filtros = {'q': q}

        query = Cuidador.query.filter_by(activo=True)

        # Aplicar filtro de búsqueda por nombre si se ingresó un valor
        if q:
            query = query.filter(Cuidador.nombre.ilike(f"%{q}%"))

        cuidadores = query.all()
        return render_template('cuidadores/lista.html', cuidadores=cuidadores, filtros=filtros)

    except SQLAlchemyError as e:
        logger.error(f"Error al obtener la lista de cuidadores: {str(e)}")
        flash("Ocurrió un error al cargar la lista de cuidadores.", "danger")
        return render_template('cuidadores/lista.html', cuidadores=[], filtros={'q': ''})


@bp.route('/<int:id>', methods=['GET'])
def detalle(id):
    """Muestra la vista detallada de un cuidador activo."""
    cuidador = Cuidador.query.filter_by(id=id, activo=True).first_or_404()
    return render_template('cuidadores/detalle.html', cuidador=cuidador)


@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    """Crea un nuevo cuidador vinculando Comuna, Especialidad y auditoría."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        comuna_nombre = request.form.get('comuna')
        especialidad_nombre = request.form.get('especialidad')

        if not nombre or not comuna_nombre or not especialidad_nombre:
            flash("Todos los campos obligatorios deben ser completados.", "warning")
            return render_template('cuidadores/formulario.html', cuidador=None)

        try:
            # Buscar o instanciar la Comuna
            comuna = Comuna.query.filter_by(nombre=comuna_nombre).first()
            if not comuna:
                comuna = Comuna(nombre=comuna_nombre)
                db.session.add(comuna)

            # Buscar o instanciar la Especialidad
            especialidad = Especialidad.query.filter_by(nombre=especialidad_nombre).first()
            if not especialidad:
                especialidad = Especialidad(nombre=especialidad_nombre)
                db.session.add(especialidad)

            # Instanciar el Cuidador
            nuevo_cuidador = Cuidador(
                nombre=nombre,
                telefono=telefono,
                comuna=comuna,
                especialidad=especialidad,
                activo=True
            )
            db.session.add(nuevo_cuidador)

            # Registro en tabla Auditoria
            log_auditoria = Auditoria(
                accion="CREAR",
                detalle=f"Se creó el cuidador: {nombre}"
            )
            db.session.add(log_auditoria)

            # Confirmar transacción completa
            db.session.commit()

            flash("Cuidador registrado exitosamente.", "success")
            return redirect(url_for('cuidadores.lista'))

        except (IntegrityError, DataError) as e:
            db.session.rollback()
            logger.error(f"Error de datos/integridad al crear cuidador: {str(e)}")
            flash("Error en los datos ingresados. Revisa el formulario e intenta de nuevo.", "danger")
        except OperationalError as e:
            db.session.rollback()
            logger.error(f"Error operacional de la base de datos: {str(e)}")
            flash("Error de conexión con la base de datos.", "danger")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error general de SQLAlchemy: {str(e)}")
            flash("Ocurrió un error inesperado al guardar el registro.", "danger")

    return render_template('cuidadores/formulario.html', cuidador=None)


@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    """Edita la información de un cuidador existente."""
    cuidador = Cuidador.query.filter_by(id=id, activo=True).first_or_404()

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        comuna_nombre = request.form.get('comuna')
        especialidad_nombre = request.form.get('especialidad')

        try:
            cuidador.nombre = nombre
            cuidador.telefono = telefono

            if comuna_nombre:
                comuna = Comuna.query.filter_by(nombre=comuna_nombre).first()
                if not comuna:
                    comuna = Comuna(nombre=comuna_nombre)
                    db.session.add(comuna)
                cuidador.comuna = comuna

            if especialidad_nombre:
                especialidad = Especialidad.query.filter_by(nombre=especialidad_nombre).first()
                if not especialidad:
                    especialidad = Especialidad(nombre=especialidad_nombre)
                    db.session.add(especialidad)
                cuidador.especialidad = especialidad

            # Auditoría
            log_auditoria = Auditoria(
                accion="ACTUALIZAR",
                detalle=f"Se actualizó el cuidador ID: {cuidador.id}"
            )
            db.session.add(log_auditoria)
            db.session.commit()

            flash("Cuidador actualizado correctamente.", "success")
            return redirect(url_for('cuidadores.detalle', id=cuidador.id))

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al actualizar el cuidador ID {id}: {str(e)}")
            flash("No se pudieron guardar los cambios por un error de base de datos.", "danger")

    return render_template('cuidadores/formulario.html', cuidador=cuidador)


@bp.route('/eliminar/<int:id>', methods=['GET', 'POST'])
def eliminar(id):
    """Ejecuta el borrado lógico (soft delete) marcando activo=False y registrando auditoría."""
    cuidador = Cuidador.query.filter_by(id=id, activo=True).first_or_404()

    if request.method == 'GET':
        return render_template('cuidadores/confirmar_eliminar.html', cuidador=cuidador)

    try:
        # Borrado lógico
        cuidador.activo = False

        # Auditoría
        log_auditoria = Auditoria(
            accion="ELIMINAR_LOGICO",
            detalle=f"Se desactivó el cuidador {cuidador.nombre} (ID: {cuidador.id})"
        )
        db.session.add(log_auditoria)
        db.session.commit()

        flash(f"El cuidador {cuidador.nombre} ha sido eliminado del sistema.", "warning")
        return redirect(url_for('cuidadores.lista'))

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error al realizar borrado lógico del cuidador ID {id}: {str(e)}")
        flash("Ocurrió un error al intentar eliminar el registro.", "danger")
        return redirect(url_for('cuidadores.lista'))