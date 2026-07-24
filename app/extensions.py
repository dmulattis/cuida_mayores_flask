from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Clase base de la que heredan los modelos administrados por SQLAlchemy."""

    pass


db = SQLAlchemy(model_class=Base)
