"""Modelos ORM de Book Manager."""

from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from book_manager.database.connection import Base


class GeneroModel(Base):
    """Género literario."""

    __tablename__ = "generos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False, unique=True)
    descripcion = Column(String(255), nullable=True)

    libros = relationship("LibroModel", back_populates="genero")


class EditorialModel(Base):
    """Editorial del catálogo."""

    __tablename__ = "editoriales"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False, unique=True)
    pais = Column(String(80), nullable=True)
    sitio_web = Column(String(200), nullable=True)

    libros = relationship("LibroModel", back_populates="editorial")


class MonedaModel(Base):
    """Moneda en la que se expresa un precio."""

    __tablename__ = "monedas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(3), nullable=False, unique=True)
    nombre = Column(String(80), nullable=False)
    simbolo = Column(String(8), nullable=False)

    precios = relationship("PrecioLibroModel", back_populates="moneda")


class TipoCotizacionModel(Base):
    """Tipo de cotización del dólar (oficial, blue, MEP, etc.)."""

    __tablename__ = "tipos_cotizacion"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(80), nullable=False, unique=True)
    descripcion = Column(String(255), nullable=True)

    cotizaciones = relationship(
        "CotizacionDolarModel",
        back_populates="tipo_cotizacion",
    )


class LibroModel(Base):
    """Libro del catálogo, con editorial y género como objetos."""

    __tablename__ = "libros"
    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String(20), nullable=False, unique=True)
    titulo = Column(String(200), nullable=False)
    autor = Column(String(150), nullable=False)
    editorial_id = Column(Integer, ForeignKey("editoriales.id"), nullable=False)
    genero_id = Column(Integer, ForeignKey("generos.id"), nullable=False)
    anio = Column(Integer, nullable=False)
    paginas = Column(Integer, nullable=False)

    editorial = relationship("EditorialModel", back_populates="libros")
    genero = relationship("GeneroModel", back_populates="libros")
    precios = relationship(
        "PrecioLibroModel",
        back_populates="libro",
        cascade="all, delete-orphan",
    )
    stock = relationship(
        "StockLibroModel",
        back_populates="libro",
        uselist=False,
        cascade="all, delete-orphan",
    )


class PrecioLibroModel(Base):
    """Precio de un libro en una moneda."""

    __tablename__ = "precios_libro"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libro_id = Column(Integer, ForeignKey("libros.id"), nullable=False)
    moneda_id = Column(Integer, ForeignKey("monedas.id"), nullable=False)
    precio = Column(Float, nullable=False)

    libro = relationship("LibroModel", back_populates="precios")
    moneda = relationship("MonedaModel", back_populates="precios")


class StockLibroModel(Base):
    """Stock de un libro. Hay un solo registro por libro."""

    __tablename__ = "stock_libro"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libro_id = Column(Integer, ForeignKey("libros.id"), nullable=False, unique=True)
    cantidad = Column(Integer, nullable=False)
    punto_reposicion = Column(Integer, nullable=True)

    libro = relationship("LibroModel", back_populates="stock")


class CotizacionDolarModel(Base):
    """Cotización de un tipo de dólar en una fecha. El par es único."""

    __tablename__ = "cotizaciones_dolar"
    __table_args__ = (
        UniqueConstraint(
            "tipo_cotizacion_id",
            "fecha",
            name="uq_cotizacion_tipo_fecha",
        ),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_cotizacion_id = Column(
        Integer,
        ForeignKey("tipos_cotizacion.id"),
        nullable=False,
    )
    fecha = Column(Date, nullable=False)
    compra = Column(Float, nullable=False)
    venta = Column(Float, nullable=False)

    tipo_cotizacion = relationship(
        "TipoCotizacionModel",
        back_populates="cotizaciones",
    )


class ExtraccionWebModel(Base):
    """Resultado de buscar un libro del catálogo en Cúspide."""

    __tablename__ = "extracciones_web"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libro_id = Column(Integer, ForeignKey("libros.id"), nullable=False)
    titulo_buscado = Column(String(200), nullable=False)
    titulo_web = Column(String(200), nullable=False)
    precio_web = Column(Float, nullable=True)
    url_imagen = Column(String(300), nullable=True)
    formas_pago = Column(String(500), nullable=True)
    descripcion = Column(Text, nullable=True)
    url_producto = Column(String(300), nullable=False)
    fecha_extraccion = Column(DateTime, nullable=False)
    coincide = Column(Integer, nullable=False, default=0)


class AuditoriaModel(Base):
    """Registro de una operación del sistema."""

    __tablename__ = "auditorias"
    id = Column(Integer, primary_key=True, autoincrement=True)
    accion = Column(String(80), nullable=False)
    fecha = Column(DateTime, nullable=False)
    detalles = Column(String(500), nullable=False)


PrecioModel = PrecioLibroModel
StockModel = StockLibroModel
