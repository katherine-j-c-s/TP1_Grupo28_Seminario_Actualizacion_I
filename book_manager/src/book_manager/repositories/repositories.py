"""Repositorios SQLAlchemy de Book Manager.

Cada clase concreta implementa el CRUD de una entidad y hereda la
interfaz del Sprint 1, así la firma queda obligada. Las relaciones
se guardan como objetos: el id de la clave foránea se toma del objeto
relacionado al persistir.
"""

from abc import ABC
from abc import abstractmethod
from datetime import date
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar

from sqlalchemy.orm import joinedload

from book_manager.database.connection import ConexionDB
from book_manager.entities.entities import Auditoria
from book_manager.entities.entities import CotizacionDolar
from book_manager.entities.entities import Editorial
from book_manager.entities.entities import ExtraccionWeb
from book_manager.entities.entities import Genero
from book_manager.entities.entities import Libro
from book_manager.entities.entities import Moneda
from book_manager.entities.entities import Precio
from book_manager.entities.entities import Stock
from book_manager.entities.entities import TipoCotizacion
from book_manager.models.models import AuditoriaModel
from book_manager.models.models import CotizacionDolarModel
from book_manager.models.models import EditorialModel
from book_manager.models.models import ExtraccionWebModel
from book_manager.models.models import GeneroModel
from book_manager.models.models import LibroModel
from book_manager.models.models import MonedaModel
from book_manager.models.models import PrecioLibroModel
from book_manager.models.models import StockLibroModel
from book_manager.models.models import TipoCotizacionModel

T = TypeVar("T")


class IRepositorio(ABC, Generic[T]):
    """Interfaz del CRUD de una entidad."""

    @abstractmethod
    def crear(self, entidad: T) -> T:
        """Crea una entidad.

        Args:
            entidad (T): Entidad a crear.

        Returns:
            T: Entidad creada.

        Raises:
            ValueError: Si ya existe una entidad con el mismo id.
        """

    @abstractmethod
    def leer_por_id(self, id: int) -> Optional[T]:
        """Lee una entidad por id.

        Args:
            id (int): Id de la entidad.

        Returns:
            Optional[T]: La entidad, o None si no está.
        """

    @abstractmethod
    def leer_todos(self) -> List[T]:
        """Lee todas las entidades.

        Returns:
            List[T]: Entidades cargadas.
        """

    @abstractmethod
    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad existente.

        Args:
            entidad (T): Entidad con el id a actualizar.

        Returns:
            T: Entidad actualizada.

        Raises:
            ValueError: Si no se encuentra la entidad.
        """

    @abstractmethod
    def eliminar(self, id: int) -> bool:
        """Elimina una entidad por id.

        Args:
            id (int): Id de la entidad a eliminar.

        Returns:
            bool: True si se eliminó, False si no estaba.
        """


class IRepositorioStock(ABC):
    """Interfaz del repositorio de stock, identificado por libro."""

    @abstractmethod
    def crear(self, stock: Stock) -> Stock:
        """Crea el stock de un libro.

        Args:
            stock (Stock): Stock a crear.

        Returns:
            Stock: Stock creado.

        Raises:
            ValueError: Si ese libro ya tiene stock.
        """

    @abstractmethod
    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Lee el stock de un libro.

        Args:
            libro_id (int): Id del libro.

        Returns:
            Optional[Stock]: El stock, o None si no está.
        """

    @abstractmethod
    def leer_todos(self) -> List[Stock]:
        """Lee todos los registros de stock.

        Returns:
            List[Stock]: Stocks cargados.
        """

    @abstractmethod
    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza el stock de un libro.

        Args:
            stock (Stock): Stock a actualizar.

        Returns:
            Stock: Stock actualizado.

        Raises:
            ValueError: Si no se encuentra el stock.
        """

    @abstractmethod
    def eliminar(self, libro_id: int) -> bool:
        """Elimina el stock de un libro.

        Args:
            libro_id (int): Id del libro.

        Returns:
            bool: True si se eliminó, False si no estaba.
        """


class IRepositorioCotizacionDolar(ABC):
    """Interfaz del repositorio de cotizaciones, identificado por tipo y fecha."""

    @abstractmethod
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Crea una cotización.

        Args:
            cotizacion (CotizacionDolar): Cotización a crear.

        Returns:
            CotizacionDolar: Cotización creada.

        Raises:
            ValueError: Si ya existe una cotización para ese tipo y fecha.
        """

    @abstractmethod
    def leer_por_tipo_y_fecha(
        self,
        tipo_id: int,
        fecha: date,
    ) -> Optional[CotizacionDolar]:
        """Lee una cotización por tipo y fecha.

        Args:
            tipo_id (int): Id del tipo de cotización.
            fecha (date): Fecha de la cotización.

        Returns:
            Optional[CotizacionDolar]: La cotización, o None si no está.
        """

    @abstractmethod
    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Lee el histórico de un tipo de cotización.

        Args:
            tipo_id (int): Id del tipo de cotización.

        Returns:
            List[CotizacionDolar]: Cotizaciones de ese tipo, por fecha.
        """

    @abstractmethod
    def leer_todas(self) -> List[CotizacionDolar]:
        """Lee todas las cotizaciones.

        Returns:
            List[CotizacionDolar]: Cotizaciones cargadas.
        """

    @abstractmethod
    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Actualiza una cotización existente.

        Args:
            cotizacion (CotizacionDolar): Cotización a actualizar.

        Returns:
            CotizacionDolar: Cotización actualizada.

        Raises:
            ValueError: Si no se encuentra la cotización.
        """

    @abstractmethod
    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina una cotización por tipo y fecha.

        Args:
            tipo_id (int): Id del tipo de cotización.
            fecha (date): Fecha de la cotización.

        Returns:
            bool: True si se eliminó, False si no estaba.
        """


def a_genero(modelo: GeneroModel) -> Genero:
    """Convierte un modelo de género en la entidad de dominio."""
    return Genero(
        id=modelo.id,
        nombre=modelo.nombre,
        descripcion=modelo.descripcion or "Sin descripción",
    )


def a_editorial(modelo: EditorialModel) -> Editorial:
    """Convierte un modelo de editorial en la entidad de dominio."""
    return Editorial(
        id=modelo.id,
        nombre=modelo.nombre,
        pais=modelo.pais or "Sin país",
        sitio_web=modelo.sitio_web or "https://cuspide.com",
    )


def a_moneda(modelo: MonedaModel) -> Moneda:
    """Convierte un modelo de moneda en la entidad de dominio."""
    return Moneda(
        id=modelo.id,
        codigo=modelo.codigo,
        nombre=modelo.nombre,
        simbolo=modelo.simbolo,
    )


def a_tipo(modelo: TipoCotizacionModel) -> TipoCotizacion:
    """Convierte un modelo de tipo de cotización en la entidad de dominio."""
    return TipoCotizacion(
        id=modelo.id,
        nombre=modelo.nombre,
        descripcion=modelo.descripcion or "Sin descripción",
    )


def a_libro(modelo: LibroModel) -> Libro:
    """Convierte un modelo de libro y adjunta género y editorial."""
    return Libro(
        id=modelo.id,
        isbn=modelo.isbn,
        titulo=modelo.titulo,
        autor=modelo.autor,
        editorial=a_editorial(modelo.editorial),
        genero=a_genero(modelo.genero),
        anio=modelo.anio,
        paginas=modelo.paginas,
    )


def a_precio(modelo: PrecioLibroModel) -> Precio:
    """Convierte un modelo de precio y adjunta libro y moneda."""
    return Precio(
        id=modelo.id,
        libro=a_libro(modelo.libro),
        moneda=a_moneda(modelo.moneda),
        importe=modelo.precio,
    )


def a_stock(modelo: StockLibroModel) -> Stock:
    """Convierte un modelo de stock y adjunta el libro."""
    return Stock(
        libro=a_libro(modelo.libro),
        cantidad=modelo.cantidad,
        punto_reposicion=modelo.punto_reposicion or 0,
    )


def a_cotizacion(modelo: CotizacionDolarModel) -> CotizacionDolar:
    """Convierte un modelo de cotización y adjunta el tipo."""
    return CotizacionDolar(
        tipo_cotizacion=a_tipo(modelo.tipo_cotizacion),
        fecha=modelo.fecha,
        compra=modelo.compra,
        venta=modelo.venta,
    )


def _opciones_libro():
    """Carga género y editorial junto con el libro."""
    return (
        joinedload(LibroModel.editorial),
        joinedload(LibroModel.genero),
    )


class RepositorioGenero(IRepositorio[Genero]):
    """CRUD de géneros sobre la tabla generos."""

    def __init__(self, db: ConexionDB) -> None:
        self._db = db

    def crear(self, entidad: Genero) -> Genero:
        """Inserta un género. Si el id es 0, lo asigna la base."""
        with self._db.transaccion() as session:
            if entidad.id and session.get(GeneroModel, entidad.id) is not None:
                raise ValueError("Ya existe una entidad con el mismo ID.")
            modelo = GeneroModel(
                nombre=entidad.nombre,
                descripcion=entidad.descripcion,
            )
            if entidad.id:
                modelo.id = entidad.id
            session.add(modelo)
            session.flush()
            entidad.id = modelo.id
            return a_genero(modelo)

    def leer_por_id(self, id: int) -> Optional[Genero]:
        """Lee un género por id."""
        with self._db.transaccion() as session:
            modelo = session.get(GeneroModel, id)
            if modelo is None:
                return None
            return a_genero(modelo)

    def leer_todos(self) -> List[Genero]:
        """Lee todos los géneros ordenados por id."""
        with self._db.transaccion() as session:
            filas = session.query(GeneroModel).order_by(GeneroModel.id).all()
            return [a_genero(fila) for fila in filas]

    def actualizar(self, entidad: Genero) -> Genero:
        """Actualiza un género existente."""
        with self._db.transaccion() as session:
            modelo = session.get(GeneroModel, entidad.id)
            if modelo is None:
                raise ValueError("No se encuentra la entidad para actualizar.")
            modelo.nombre = entidad.nombre
            modelo.descripcion = entidad.descripcion
            session.flush()
            return a_genero(modelo)

    def eliminar(self, id: int) -> bool:
        """Elimina un género por id."""
        with self._db.transaccion() as session:
            modelo = session.get(GeneroModel, id)
            if modelo is None:
                return False
            session.delete(modelo)
            return True


class RepositorioEditorial(IRepositorio[Editorial]):
    """CRUD de editoriales."""

    def __init__(self, db: ConexionDB) -> None:
        self._db = db

    def crear(self, entidad: Editorial) -> Editorial:
        """Inserta una editorial."""
        with self._db.transaccion() as session:
            if entidad.id and session.get(EditorialModel, entidad.id) is not None:
                raise ValueError("Ya existe una entidad con el mismo ID.")
            modelo = EditorialModel(
                nombre=entidad.nombre,
                pais=entidad.pais,
                sitio_web=entidad.sitio_web,
            )
            if entidad.id:
                modelo.id = entidad.id
            session.add(modelo)
            session.flush()
            entidad.id = modelo.id
            return a_editorial(modelo)

    def leer_por_id(self, id: int) -> Optional[Editorial]:
        """Lee una editorial por id."""
        with self._db.transaccion() as session:
            modelo = session.get(EditorialModel, id)
            if modelo is None:
                return None
            return a_editorial(modelo)

    def leer_todos(self) -> List[Editorial]:
        """Lee todas las editoriales."""
        with self._db.transaccion() as session:
            filas = session.query(EditorialModel).order_by(EditorialModel.id).all()
            return [a_editorial(fila) for fila in filas]

    def actualizar(self, entidad: Editorial) -> Editorial:
        """Actualiza una editorial."""
        with self._db.transaccion() as session:
            modelo = session.get(EditorialModel, entidad.id)
            if modelo is None:
                raise ValueError("No se encuentra la entidad para actualizar.")
            modelo.nombre = entidad.nombre
            modelo.pais = entidad.pais
            modelo.sitio_web = entidad.sitio_web
            session.flush()
            return a_editorial(modelo)

    def eliminar(self, id: int) -> bool:
        """Elimina una editorial por id."""
        with self._db.transaccion() as session:
            modelo = session.get(EditorialModel, id)
            if modelo is None:
                return False
            session.delete(modelo)
            return True


class RepositorioMoneda(IRepositorio[Moneda]):
    """CRUD de monedas."""

    def __init__(self, db: ConexionDB) -> None:
        self._db = db

    def crear(self, entidad: Moneda) -> Moneda:
        """Inserta una moneda."""
        with self._db.transaccion() as session:
            if entidad.id and session.get(MonedaModel, entidad.id) is not None:
                raise ValueError("Ya existe una entidad con el mismo ID.")
            modelo = MonedaModel(
                codigo=entidad.codigo,
                nombre=entidad.nombre,
                simbolo=entidad.simbolo,
            )
            if entidad.id:
                modelo.id = entidad.id
            session.add(modelo)
            session.flush()
            entidad.id = modelo.id
            return a_moneda(modelo)

    def leer_por_id(self, id: int) -> Optional[Moneda]:
        """Lee una moneda por id."""
        with self._db.transaccion() as session:
            modelo = session.get(MonedaModel, id)
            if modelo is None:
                return None
            return a_moneda(modelo)

    def leer_todos(self) -> List[Moneda]:
        """Lee todas las monedas."""
        with self._db.transaccion() as session:
            filas = session.query(MonedaModel).order_by(MonedaModel.id).all()
            return [a_moneda(fila) for fila in filas]

    def actualizar(self, entidad: Moneda) -> Moneda:
        """Actualiza una moneda."""
        with self._db.transaccion() as session:
            modelo = session.get(MonedaModel, entidad.id)
            if modelo is None:
                raise ValueError("No se encuentra la entidad para actualizar.")
            modelo.codigo = entidad.codigo
            modelo.nombre = entidad.nombre
            modelo.simbolo = entidad.simbolo
            session.flush()
            return a_moneda(modelo)

    def eliminar(self, id: int) -> bool:
        """Elimina una moneda por id."""
        with self._db.transaccion() as session:
            modelo = session.get(MonedaModel, id)
            if modelo is None:
                return False
            session.delete(modelo)
            return True


class RepositorioTipoCotizacion(IRepositorio[TipoCotizacion]):
    """CRUD de tipos de cotización."""

    def __init__(self, db: ConexionDB) -> None:
        self._db = db

    def crear(self, entidad: TipoCotizacion) -> TipoCotizacion:
        """Inserta un tipo de cotización."""
        with self._db.transaccion() as session:
            if entidad.id and session.get(TipoCotizacionModel, entidad.id) is not None:
                raise ValueError("Ya existe una entidad con el mismo ID.")
            modelo = TipoCotizacionModel(
                nombre=entidad.nombre,
                descripcion=entidad.descripcion,
            )
            if entidad.id:
                modelo.id = entidad.id
            session.add(modelo)
            session.flush()
            entidad.id = modelo.id
            return a_tipo(modelo)

    def leer_por_id(self, id: int) -> Optional[TipoCotizacion]:
        """Lee un tipo de cotización por id."""
        with self._db.transaccion() as session:
            modelo = session.get(TipoCotizacionModel, id)
            if modelo is None:
                return None
            return a_tipo(modelo)

    def leer_todos(self) -> List[TipoCotizacion]:
        """Lee todos los tipos de cotización."""
        with self._db.transaccion() as session:
            filas = (
                session.query(TipoCotizacionModel)
                .order_by(TipoCotizacionModel.id)
                .all()
            )
            return [a_tipo(fila) for fila in filas]

    def actualizar(self, entidad: TipoCotizacion) -> TipoCotizacion:
        """Actualiza un tipo de cotización."""
        with self._db.transaccion() as session:
            modelo = session.get(TipoCotizacionModel, entidad.id)
            if modelo is None:
                raise ValueError("No se encuentra la entidad para actualizar.")
            modelo.nombre = entidad.nombre
            modelo.descripcion = entidad.descripcion
            session.flush()
            return a_tipo(modelo)

    def eliminar(self, id: int) -> bool:
        """Elimina un tipo de cotización por id."""
        with self._db.transaccion() as session:
            modelo = session.get(TipoCotizacionModel, id)
            if modelo is None:
                return False
            session.delete(modelo)
            return True


class RepositorioLibro(IRepositorio[Libro]):
    """CRUD de libros. Género y editorial se persisten por el objeto relacionado."""

    def __init__(self, db: ConexionDB) -> None:
        self._db = db

    def crear(self, entidad: Libro) -> Libro:
        """Inserta un libro."""
        with self._db.transaccion() as session:
            if entidad.id and session.get(LibroModel, entidad.id) is not None:
                raise ValueError("Ya existe una entidad con el mismo ID.")
            modelo = LibroModel(
                isbn=entidad.isbn,
                titulo=entidad.titulo,
                autor=entidad.autor,
                editorial_id=entidad.editorial.id,
                genero_id=entidad.genero.id,
                anio=entidad.anio,
                paginas=entidad.paginas,
            )
            if entidad.id:
                modelo.id = entidad.id
            session.add(modelo)
            session.flush()
            entidad.id = modelo.id
            cargado = (
                session.query(LibroModel)
                .options(*_opciones_libro())
                .filter(LibroModel.id == modelo.id)
                .one()
            )
            return a_libro(cargado)

    def leer_por_id(self, id: int) -> Optional[Libro]:
        """Lee un libro por id, con su género y su editorial."""
        with self._db.transaccion() as session:
            modelo = (
                session.query(LibroModel)
                .options(*_opciones_libro())
                .filter(LibroModel.id == id)
                .one_or_none()
            )
            if modelo is None:
                return None
            return a_libro(modelo)

    def leer_todos(self) -> List[Libro]:
        """Lee todos los libros."""
        with self._db.transaccion() as session:
            filas = (
                session.query(LibroModel)
                .options(*_opciones_libro())
                .order_by(LibroModel.id)
                .all()
            )
            return [a_libro(fila) for fila in filas]

    def actualizar(self, entidad: Libro) -> Libro:
        """Actualiza un libro."""
        with self._db.transaccion() as session:
            modelo = session.get(LibroModel, entidad.id)
            if modelo is None:
                raise ValueError("No se encuentra la entidad para actualizar.")
            modelo.isbn = entidad.isbn
            modelo.titulo = entidad.titulo
            modelo.autor = entidad.autor
            modelo.editorial_id = entidad.editorial.id
            modelo.genero_id = entidad.genero.id
            modelo.anio = entidad.anio
            modelo.paginas = entidad.paginas
            session.flush()
            cargado = (
                session.query(LibroModel)
                .options(*_opciones_libro())
                .filter(LibroModel.id == modelo.id)
                .one()
            )
            return a_libro(cargado)

    def eliminar(self, id: int) -> bool:
        """Elimina un libro por id."""
        with self._db.transaccion() as session:
            modelo = session.get(LibroModel, id)
            if modelo is None:
                return False
            session.delete(modelo)
            return True


class RepositorioPrecio(IRepositorio[Precio]):
    """CRUD de precios. El libro y la moneda son objetos."""

    def __init__(self, db: ConexionDB) -> None:
        self._db = db

    def _cargar(self, session, id: int) -> PrecioLibroModel:
        return (
            session.query(PrecioLibroModel)
            .options(
                joinedload(PrecioLibroModel.moneda),
                joinedload(PrecioLibroModel.libro).joinedload(LibroModel.editorial),
                joinedload(PrecioLibroModel.libro).joinedload(LibroModel.genero),
            )
            .filter(PrecioLibroModel.id == id)
            .one()
        )

    def crear(self, entidad: Precio) -> Precio:
        """Inserta un precio."""
        with self._db.transaccion() as session:
            if entidad.id and session.get(PrecioLibroModel, entidad.id) is not None:
                raise ValueError("Ya existe una entidad con el mismo ID.")
            modelo = PrecioLibroModel(
                libro_id=entidad.libro.id,
                moneda_id=entidad.moneda.id,
                precio=entidad.importe,
            )
            if entidad.id:
                modelo.id = entidad.id
            session.add(modelo)
            session.flush()
            entidad.id = modelo.id
            return a_precio(self._cargar(session, modelo.id))

    def leer_por_id(self, id: int) -> Optional[Precio]:
        """Lee un precio por id."""
        with self._db.transaccion() as session:
            if session.get(PrecioLibroModel, id) is None:
                return None
            return a_precio(self._cargar(session, id))

    def leer_todos(self) -> List[Precio]:
        """Lee todos los precios."""
        with self._db.transaccion() as session:
            filas = (
                session.query(PrecioLibroModel)
                .options(
                    joinedload(PrecioLibroModel.moneda),
                    joinedload(PrecioLibroModel.libro).joinedload(LibroModel.editorial),
                    joinedload(PrecioLibroModel.libro).joinedload(LibroModel.genero),
                )
                .order_by(PrecioLibroModel.id)
                .all()
            )
            return [a_precio(fila) for fila in filas]

    def actualizar(self, entidad: Precio) -> Precio:
        """Actualiza un precio."""
        with self._db.transaccion() as session:
            modelo = session.get(PrecioLibroModel, entidad.id)
            if modelo is None:
                raise ValueError("No se encuentra la entidad para actualizar.")
            modelo.libro_id = entidad.libro.id
            modelo.moneda_id = entidad.moneda.id
            modelo.precio = entidad.importe
            session.flush()
            return a_precio(self._cargar(session, modelo.id))

    def eliminar(self, id: int) -> bool:
        """Elimina un precio por id."""
        with self._db.transaccion() as session:
            modelo = session.get(PrecioLibroModel, id)
            if modelo is None:
                return False
            session.delete(modelo)
            return True


class RepositorioStock(IRepositorioStock):
    """CRUD de stock. La clave de negocio es el libro."""

    def __init__(self, db: ConexionDB) -> None:
        self._db = db

    def _opciones(self):
        return (
            joinedload(StockLibroModel.libro).joinedload(LibroModel.editorial),
            joinedload(StockLibroModel.libro).joinedload(LibroModel.genero),
        )

    def crear(self, stock: Stock) -> Stock:
        """Inserta el stock de un libro."""
        with self._db.transaccion() as session:
            existente = (
                session.query(StockLibroModel)
                .filter(StockLibroModel.libro_id == stock.libro.id)
                .one_or_none()
            )
            if existente is not None:
                raise ValueError("Ya existe un registro de stock para el mismo libro.")
            modelo = StockLibroModel(
                libro_id=stock.libro.id,
                cantidad=stock.cantidad,
                punto_reposicion=stock.punto_reposicion,
            )
            session.add(modelo)
            session.flush()
            cargado = (
                session.query(StockLibroModel)
                .options(*self._opciones())
                .filter(StockLibroModel.id == modelo.id)
                .one()
            )
            return a_stock(cargado)

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Lee el stock de un libro."""
        with self._db.transaccion() as session:
            modelo = (
                session.query(StockLibroModel)
                .options(*self._opciones())
                .filter(StockLibroModel.libro_id == libro_id)
                .one_or_none()
            )
            if modelo is None:
                return None
            return a_stock(modelo)

    def leer_todos(self) -> List[Stock]:
        """Lee todos los stocks."""
        with self._db.transaccion() as session:
            filas = (
                session.query(StockLibroModel)
                .options(*self._opciones())
                .order_by(StockLibroModel.libro_id)
                .all()
            )
            return [a_stock(fila) for fila in filas]

    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza el stock de un libro."""
        with self._db.transaccion() as session:
            modelo = (
                session.query(StockLibroModel)
                .filter(StockLibroModel.libro_id == stock.libro.id)
                .one_or_none()
            )
            if modelo is None:
                raise ValueError("No se encuentra el stock para actualizar.")
            modelo.cantidad = stock.cantidad
            modelo.punto_reposicion = stock.punto_reposicion
            session.flush()
            cargado = (
                session.query(StockLibroModel)
                .options(*self._opciones())
                .filter(StockLibroModel.id == modelo.id)
                .one()
            )
            return a_stock(cargado)

    def eliminar(self, libro_id: int) -> bool:
        """Elimina el stock de un libro."""
        with self._db.transaccion() as session:
            modelo = (
                session.query(StockLibroModel)
                .filter(StockLibroModel.libro_id == libro_id)
                .one_or_none()
            )
            if modelo is None:
                return False
            session.delete(modelo)
            return True


class RepositorioCotizacionDolar(IRepositorioCotizacionDolar):
    """CRUD del histórico de cotizaciones del dólar."""

    def __init__(self, db: ConexionDB) -> None:
        self._db = db

    def _buscar(self, session, tipo_id: int, fecha: date) -> Optional[CotizacionDolarModel]:
        return (
            session.query(CotizacionDolarModel)
            .options(joinedload(CotizacionDolarModel.tipo_cotizacion))
            .filter(
                CotizacionDolarModel.tipo_cotizacion_id == tipo_id,
                CotizacionDolarModel.fecha == fecha,
            )
            .one_or_none()
        )

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Inserta una cotización."""
        with self._db.transaccion() as session:
            if self._buscar(
                session, cotizacion.tipo_cotizacion.id, cotizacion.fecha
            ) is not None:
                raise ValueError("Ya existe una cotización para el mismo tipo y fecha.")
            modelo = CotizacionDolarModel(
                tipo_cotizacion_id=cotizacion.tipo_cotizacion.id,
                fecha=cotizacion.fecha,
                compra=cotizacion.compra,
                venta=cotizacion.venta,
            )
            session.add(modelo)
            session.flush()
            cargado = self._buscar(
                session, cotizacion.tipo_cotizacion.id, cotizacion.fecha
            )
            return a_cotizacion(cargado)

    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: date
    ) -> Optional[CotizacionDolar]:
        """Lee una cotización por tipo y fecha."""
        with self._db.transaccion() as session:
            modelo = self._buscar(session, tipo_id, fecha)
            if modelo is None:
                return None
            return a_cotizacion(modelo)

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Lee el histórico de un tipo, ordenado por fecha."""
        with self._db.transaccion() as session:
            filas = (
                session.query(CotizacionDolarModel)
                .options(joinedload(CotizacionDolarModel.tipo_cotizacion))
                .filter(CotizacionDolarModel.tipo_cotizacion_id == tipo_id)
                .order_by(CotizacionDolarModel.fecha)
                .all()
            )
            return [a_cotizacion(fila) for fila in filas]

    def leer_todas(self) -> List[CotizacionDolar]:
        """Lee todas las cotizaciones."""
        with self._db.transaccion() as session:
            filas = (
                session.query(CotizacionDolarModel)
                .options(joinedload(CotizacionDolarModel.tipo_cotizacion))
                .order_by(CotizacionDolarModel.fecha, CotizacionDolarModel.tipo_cotizacion_id)
                .all()
            )
            return [a_cotizacion(fila) for fila in filas]

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Actualiza compra y venta de una cotización existente."""
        with self._db.transaccion() as session:
            modelo = self._buscar(
                session, cotizacion.tipo_cotizacion.id, cotizacion.fecha
            )
            if modelo is None:
                raise ValueError("No se encuentra la cotización para actualizar.")
            modelo.compra = cotizacion.compra
            modelo.venta = cotizacion.venta
            session.flush()
            return a_cotizacion(modelo)

    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina una cotización por tipo y fecha."""
        with self._db.transaccion() as session:
            modelo = self._buscar(session, tipo_id, fecha)
            if modelo is None:
                return False
            session.delete(modelo)
            return True


def a_extraccion(modelo: ExtraccionWebModel) -> ExtraccionWeb:
    """Convierte una fila de extracción web en la entidad."""
    return ExtraccionWeb(
        id=modelo.id,
        libro_id=modelo.libro_id,
        titulo_buscado=modelo.titulo_buscado,
        titulo_web=modelo.titulo_web,
        precio_web=modelo.precio_web,
        url_imagen=modelo.url_imagen or "",
        formas_pago=modelo.formas_pago or "",
        descripcion=modelo.descripcion or "",
        url_producto=modelo.url_producto,
        fecha_extraccion=modelo.fecha_extraccion,
        coincide=bool(modelo.coincide),
    )


def a_auditoria(modelo: AuditoriaModel) -> Auditoria:
    """Convierte una fila de auditoría en la entidad."""
    return Auditoria(
        id=modelo.id,
        accion=modelo.accion,
        fecha=modelo.fecha,
        detalles=modelo.detalles,
    )


class RepositorioExtraccionWeb:
    """CRUD de los resultados del scraper de Cúspide."""

    def __init__(self, db: ConexionDB) -> None:
        self._db = db

    def crear(self, entidad: ExtraccionWeb) -> ExtraccionWeb:
        """Inserta una extracción."""
        with self._db.transaccion() as session:
            modelo = ExtraccionWebModel(
                libro_id=entidad.libro_id,
                titulo_buscado=entidad.titulo_buscado,
                titulo_web=entidad.titulo_web,
                precio_web=entidad.precio_web,
                url_imagen=entidad.url_imagen,
                formas_pago=entidad.formas_pago[:500],
                descripcion=entidad.descripcion,
                url_producto=entidad.url_producto,
                fecha_extraccion=entidad.fecha_extraccion,
                coincide=1 if entidad.coincide else 0,
            )
            session.add(modelo)
            session.flush()
            return a_extraccion(modelo)

    def leer_por_id(self, id: int) -> Optional[ExtraccionWeb]:
        """Lee una extracción por id."""
        with self._db.transaccion() as session:
            modelo = session.get(ExtraccionWebModel, id)
            if modelo is None:
                return None
            return a_extraccion(modelo)

    def leer_todos(self) -> List[ExtraccionWeb]:
        """Lee todas las extracciones."""
        with self._db.transaccion() as session:
            filas = session.query(ExtraccionWebModel).order_by(ExtraccionWebModel.id).all()
            return [a_extraccion(fila) for fila in filas]

    def leer_por_libro(self, libro_id: int) -> List[ExtraccionWeb]:
        """Lee las extracciones de un libro del catálogo."""
        with self._db.transaccion() as session:
            filas = (
                session.query(ExtraccionWebModel)
                .filter(ExtraccionWebModel.libro_id == libro_id)
                .all()
            )
            return [a_extraccion(fila) for fila in filas]

    def actualizar(self, entidad: ExtraccionWeb) -> ExtraccionWeb:
        """Actualiza una extracción existente."""
        with self._db.transaccion() as session:
            modelo = session.get(ExtraccionWebModel, entidad.id)
            if modelo is None:
                raise ValueError("No se encuentra la extracción para actualizar.")
            modelo.titulo_web = entidad.titulo_web
            modelo.precio_web = entidad.precio_web
            modelo.url_imagen = entidad.url_imagen
            modelo.formas_pago = entidad.formas_pago[:500]
            modelo.descripcion = entidad.descripcion
            modelo.coincide = 1 if entidad.coincide else 0
            session.flush()
            return a_extraccion(modelo)

    def eliminar(self, id: int) -> bool:
        """Elimina una extracción por id."""
        with self._db.transaccion() as session:
            modelo = session.get(ExtraccionWebModel, id)
            if modelo is None:
                return False
            session.delete(modelo)
            return True

    def eliminar_todas(self) -> int:
        """Vacía la tabla antes de un scraping nuevo.

        Returns:
            int: Filas eliminadas.
        """
        with self._db.transaccion() as session:
            cantidad = session.query(ExtraccionWebModel).delete()
            return int(cantidad or 0)


class RepositorioAuditoria:
    """CRUD de la tabla de auditoría."""

    def __init__(self, db: ConexionDB) -> None:
        self._db = db

    def crear(self, entidad: Auditoria) -> Auditoria:
        """Inserta un registro de auditoría."""
        with self._db.transaccion() as session:
            modelo = AuditoriaModel(
                accion=entidad.accion[:80],
                fecha=entidad.fecha,
                detalles=entidad.detalles[:500],
            )
            if entidad.id:
                modelo.id = entidad.id
            session.add(modelo)
            session.flush()
            return a_auditoria(modelo)

    def leer_por_id(self, id: int) -> Optional[Auditoria]:
        """Lee un registro por id."""
        with self._db.transaccion() as session:
            modelo = session.get(AuditoriaModel, id)
            if modelo is None:
                return None
            return a_auditoria(modelo)

    def leer_todos(self) -> List[Auditoria]:
        """Lee el historial ordenado por fecha."""
        with self._db.transaccion() as session:
            filas = session.query(AuditoriaModel).order_by(AuditoriaModel.fecha, AuditoriaModel.id).all()
            return [a_auditoria(fila) for fila in filas]

    def actualizar(self, entidad: Auditoria) -> Auditoria:
        """Actualiza el detalle de un registro existente."""
        with self._db.transaccion() as session:
            modelo = session.get(AuditoriaModel, entidad.id)
            if modelo is None:
                raise ValueError("No se encuentra la auditoría para actualizar.")
            modelo.accion = entidad.accion[:80]
            modelo.fecha = entidad.fecha
            modelo.detalles = entidad.detalles[:500]
            session.flush()
            return a_auditoria(modelo)

    def eliminar(self, id: int) -> bool:
        """Elimina un registro de auditoría."""
        with self._db.transaccion() as session:
            modelo = session.get(AuditoriaModel, id)
            if modelo is None:
                return False
            session.delete(modelo)
            return True
