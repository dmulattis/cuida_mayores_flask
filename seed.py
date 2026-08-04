from app import create_app
from app.extensions import db
from app.models import Auditoria, Comuna, Cuidador, Especialidad


def poblar_base_datos():
    app = create_app()

    with app.app_context():
        print("Limpiando y recreando las tablas de la base de datos...")
        db.drop_all()
        db.create_all()

        # 1. Crear Comunas
        print("Registrando comunas...")
        comuna_concepcion = Comuna(nombre="Concepción")
        comuna_talcahuano = Comuna(nombre="Talcahuano")
        comuna_san_pedro = Comuna(nombre="San Pedro de la Paz")

        db.session.add_all(
            [comuna_concepcion, comuna_talcahuano, comuna_san_pedro]
        )
        db.session.commit()

        # 2. Crear Especialidades
        print("Registrando especialidades...")
        esp_adulto_mayor = Especialidad(nombre="Cuidado Adulto Mayor")
        esp_enfermeria = Especialidad(nombre="Enfermería Básica")
        esp_kinesiologia = Especialidad(nombre="Kinesiología")

        db.session.add_all([esp_adulto_mayor, esp_enfermeria, esp_kinesiologia])
        db.session.commit()

        # 3. Crear Cuidadores
        print("Registrando cuidadores...")
        cuidador1 = Cuidador(
            nombre="María González",
            correo="maria@example.com",
            telefono="+56912345678",
            comuna_id=comuna_concepcion.id,
            especialidad_id=esp_adulto_mayor.id,
            experiencia_anios=5,
            tarifa_diaria=35000,
            descripcion="Especialista en atención y compañía para adultos mayores.",
            estado_validacion="Aprobado",
            disponible=True,
            activo=True,
        )

        cuidador2 = Cuidador(
            nombre="Juan Pérez",
            correo="juan@example.com",
            telefono="+56987654321",
            comuna_id=comuna_talcahuano.id,
            especialidad_id=esp_enfermeria.id,
            experiencia_anios=3,
            tarifa_diaria=30000,
            descripcion="Técnico en enfermería con experiencia en cuidados del adulto mayor.",
            estado_validacion="Pendiente",
            disponible=True,
            activo=True,
        )

        db.session.add_all([cuidador1, cuidador2])
        db.session.commit()

        # 4. Registro en Auditoría
        print("Generando registro inicial de auditoría...")
        audit = Auditoria(
            accion="SEED",
            detalle="Poblado inicial de base de datos realizado con éxito.",
        )
        db.session.add(audit)
        db.session.commit()

        print("\n¡Base de datos poblada exitosamente!")


if __name__ == "__main__":
    poblar_base_datos()