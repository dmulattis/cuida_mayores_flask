from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .extensions import db


class Cuidador(db.Model):
    """Representa un cuidador registrado en la base de datos."""

    __tablename__ = "cuidadores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    correo: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False)
    comuna: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    especialidad: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    experiencia_anios: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tarifa_diaria: Mapped[int] = mapped_column(Integer, nullable=False)
    disponible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    estado_validacion: Mapped[str] = mapped_column(String(20), nullable=False, default="Pendiente")
    descripcion: Mapped[str] = mapped_column(Text, nullable=False, default="")
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        """Devuelve una representación breve del cuidador para depuración."""
        return f"<Cuidador {self.nombre}>"
