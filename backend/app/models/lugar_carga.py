from sqlalchemy import Column, Integer, String, SmallInteger
from app.core.database import Base


class LugarCarga(Base):
    __tablename__ = "lugarcarga"

    idLugarCarga = Column(Integer, primary_key=True, autoincrement=True)
    Detalle = Column(String(80), nullable=False, default="")
    activo = Column(SmallInteger, nullable=False, default=1)
    unidad_negocio = Column(Integer, nullable=False, default=1)
