"""
Modelos de datos relacionales para la plataforma Cuida a tus Mayores.
"""

from datetime import UTC, datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .extensions import db


def ahora_utc() -> datetime:
    return datetime.now(UTC)


class Comuna(db.Model):
    __tablename__ = "comunas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)

    cuidadores: Mapped[List["Cuidador"]] = relationship(back_populates="comuna_rel")

    def __repr__(self) -> str:
        return f"<Comuna {self.nombre}>"


class Especialidad(db.Model):
    __tablename__ = "especialidades"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    cuidadores: Mapped[List["Cuidador"]] = relationship(back_populates="especialidad_rel")

    def __repr__(self) -> str:
        return f"<Especialidad {self.nombre}>"


class Cuidador(db.Model):
    __tablename__ = "cuidadores"

    id: Mapped[int] = mapped_column(primary_key=True)

    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    correo: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False)

    # Relación a Comuna
    comuna_id: Mapped[int] = mapped_column(ForeignKey("comunas.id"), nullable=False)
    comuna_rel: Mapped["Comuna"] = relationship(back_populates="cuidadores")

    # Relación a Especialidad
    especialidad_id: Mapped[int] = mapped_column(ForeignKey("especialidades.id"), nullable=False)
    especialidad_rel: Mapped["Especialidad"] = relationship(back_populates="cuidadores")

    experiencia_anios: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tarifa_diaria: Mapped[int] = mapped_column(Integer, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False, default="")

    disponible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    estado_validacion: Mapped[str] = mapped_column(String(20), nullable=False, default="Pendiente")

    # Flag para Borrado Lógico (Soft Delete)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=ahora_utc
    )

    # Relación a Historial de Auditoría
    auditorias: Mapped[List["Auditoria"]] = relationship(
        back_populates="cuidador_rel", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Cuidador {self.nombre}>"


class Auditoria(db.Model):
    __tablename__ = "auditorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    cuidador_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cuidadores.id"), nullable=True)
    cuidador_rel: Mapped[Optional["Cuidador"]] = relationship(back_populates="auditorias")

    accion: Mapped[str] = mapped_column(String(50), nullable=False)  # CREACION, EDICION, SOFT_DELETE
    detalle: Mapped[str] = mapped_column(Text, nullable=True)
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=ahora_utc
    )

    def __repr__(self) -> str:
        return f"<Auditoria {self.accion} - {self.fecha}>"
