from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from book_manager.database.connection import Base

class GeneroModel(Base):
    __tablename__ = "generos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False, unique=True)
    descripcion = Column(String, nullable=True)

    libros = relationship("LibroModel", back_populates="genero")

class EditorialModel(Base):
    __tablename__ = "editoriales"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False, unique=True)
    pais = Column(String, nullable=True)
    sitio_web = Column(String, nullable=True)

    libros = relationship("LibroModel", back_populates="editorial")

class MonedaModel(Base):
    __tablename__ = "monedas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String, nullable=False, unique=True)
    nombre = Column(String, nullable=False)
    simbolo = Column(String, nullable=False)

    precios = relationship("PrecioLibroModel", back_populates="moneda")

class TipoCotizacionModel(Base):
    __tablename__ = "tipos_cotizacion"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False, unique=True)
    descripcion = Column(String, nullable=True)

    cotizaciones = relationship("CotizacionDolarModel", back_populates="tipo_cotizacion")

class LibroModel(Base):
    __tablename__ = "libros"
    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String, nullable=False, unique=True)
    titulo = Column(String, nullable=False)
    autor = Column(String, nullable=False)
    editorial_id = Column(Integer, ForeignKey("editoriales.id"), nullable=False)
    genero_id = Column(Integer, ForeignKey("generos.id"), nullable=False)
    anio = Column(Integer, nullable=False)
    paginas = Column(Integer, nullable=False)

    editorial = relationship("EditorialModel", back_populates="libros")
    genero = relationship("GeneroModel", back_populates="libros")
    precios = relationship("PrecioLibroModel", back_populates="libro", cascade="all, delete-orphan")
    stock = relationship("StockLibroModel", back_populates="libro", uselist=False, cascade="all, delete-orphan")

class PrecioLibroModel(Base):
    __tablename__ = "precios_libro"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libro_id = Column(Integer, ForeignKey("libros.id"), nullable=False)
    moneda_id = Column(Integer, ForeignKey("monedas.id"), nullable=False)
    precio = Column(Float, nullable=False)

    libro = relationship("LibroModel", back_populates="precios")
    moneda = relationship("MonedaModel", back_populates="precios")

class StockLibroModel(Base):
    __tablename__ = "stock_libro"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libro_id = Column(Integer, ForeignKey("libros.id"), nullable=False, unique=True)
    cantidad = Column(Integer, nullable=False)
    punto_reposicion = Column(Integer, nullable=True)

    libro = relationship("LibroModel", back_populates="stock")

class CotizacionDolarModel(Base):
    __tablename__ = "cotizaciones_dolar"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_cotizacion_id = Column(Integer, ForeignKey("tipos_cotizacion.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    compra = Column(Float, nullable=False)
    venta = Column(Float, nullable=False)

    tipo_cotizacion = relationship("TipoCotizacionModel", back_populates="cotizaciones")
