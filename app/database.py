"""Database initialization module using SQLAlchemy"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models"""

    pass


# Create SQLAlchemy database instance
db = SQLAlchemy(model_class=Base)
