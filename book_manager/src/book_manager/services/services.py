"""Lógica de negocio de Book Manager.

Los servicios validan las reglas antes de llamar al repositorio.
La consola no decide si un género se puede borrar o si un precio
está duplicado: eso vive acá.
"""

from dataclasses import dataclass
from datetime import date
from typing import List
from typing import Optional

from book_manager.entities.entities import CotizacionDolar
from book_manager.entities.entities import Editorial
from book_manager.entities.entities import Genero
from book_manager.entities.entities import Libro
from book_manager.entities.entities import Moneda
from book_manager.entities.entities import Precio
from book_manager.entities.entities import Stock
from book_manager.entities.entities import TipoCotizacion
from book_manager.repositories.repositories import IRepositorio
from book_manager.repositories.repositories import IRepositorioCotizacionDolar
from book_manager.repositories.repositories import IRepositorioStock


def _mismo_texto(izquierdo: str, derecho: str) -> bool:
    """Compara dos textos sin distinguir mayúsculas ni espacios laterales."""
    return izquierdo.strip().casefold() == derecho.strip().casefold()


class GeneroServicio:
    """Reglas de alta, lectura, modificación y borrado de géneros."""

    def __init__(
        self,
        repositorio: IRepositorio[Genero],
        libros: IRepositorio[Libro],
    ) -> None:
        self.__repositorio = repositorio
        self.__libros = libros

    def crear(self, entidad: Genero) -> Genero:
        """Crea un género si el nombre no está repetido."""
        if self.buscar_por_nombre(entidad.nombre) is not None:
            raise ValueError(f"Ya existe un género llamado {entidad.nombre}.")
        return self.__repositorio.crear(entidad)

    def leer_por_id(self, id: int) -> Optional[Genero]:
        """Lee un género por id."""
        return self.__repositorio.leer_por_id(id)

    def leer_todos(self) -> List[Genero]:
        """Lee todos los géneros."""
        return self.__repositorio.leer_todos()

    def buscar_por_nombre(self, nombre: str) -> Optional[Genero]:
        """Busca un género por nombre."""
        for genero in self.__repositorio.leer_todos():
            if _mismo_texto(genero.nombre, nombre):
                return genero
        return None

    def actualizar(self, entidad: Genero) -> Genero:
        """Actualiza un género y evita nombres duplicados."""
        if self.__repositorio.leer_por_id(entidad.id) is None:
            raise ValueError("No se encuentra el género para actualizar.")
        otro = self.buscar_por_nombre(entidad.nombre)
        if otro is not None and otro.id != entidad.id:
            raise ValueError(f"Ya existe un género llamado {entidad.nombre}.")
        return self.__repositorio.actualizar(entidad)

    def eliminar(self, id: int) -> bool:
        """Elimina un género que no tenga libros asociados."""
        if any(libro.genero_id == id for libro in self.__libros.leer_todos()):
            raise ValueError(
                "No se puede eliminar el género porque hay libros asociados."
            )
        return self.__repositorio.eliminar(id)


class EditorialServicio:
    """Reglas de alta, lectura, modificación y borrado de editoriales."""

    def __init__(
        self,
        repositorio: IRepositorio[Editorial],
        libros: IRepositorio[Libro],
    ) -> None:
        self.__repositorio = repositorio
        self.__libros = libros

    def crear(self, entidad: Editorial) -> Editorial:
        """Crea una editorial si el nombre no está repetido."""
        if self.buscar_por_nombre(entidad.nombre) is not None:
            raise ValueError(f"Ya existe la editorial {entidad.nombre}.")
        return self.__repositorio.crear(entidad)

    def leer_por_id(self, id: int) -> Optional[Editorial]:
        """Lee una editorial por id."""
        return self.__repositorio.leer_por_id(id)

    def leer_todos(self) -> List[Editorial]:
        """Lee todas las editoriales."""
        return self.__repositorio.leer_todos()

    def buscar_por_nombre(self, nombre: str) -> Optional[Editorial]:
        """Busca una editorial por nombre."""
        for editorial in self.__repositorio.leer_todos():
            if _mismo_texto(editorial.nombre, nombre):
                return editorial
        return None

    def actualizar(self, entidad: Editorial) -> Editorial:
        """Actualiza una editorial."""
        if self.__repositorio.leer_por_id(entidad.id) is None:
            raise ValueError("No se encuentra la editorial para actualizar.")
        otro = self.buscar_por_nombre(entidad.nombre)
        if otro is not None and otro.id != entidad.id:
            raise ValueError(f"Ya existe la editorial {entidad.nombre}.")
        return self.__repositorio.actualizar(entidad)

    def eliminar(self, id: int) -> bool:
        """Elimina una editorial que no tenga libros asociados."""
        if any(libro.editorial_id == id for libro in self.__libros.leer_todos()):
            raise ValueError(
                "No se puede eliminar la editorial porque hay libros asociados."
            )
        return self.__repositorio.eliminar(id)


class MonedaServicio:
    """Reglas de alta, lectura, modificación y borrado de monedas."""

    def __init__(
        self,
        repositorio: IRepositorio[Moneda],
        precios: IRepositorio[Precio],
    ) -> None:
        self.__repositorio = repositorio
        self.__precios = precios

    def crear(self, entidad: Moneda) -> Moneda:
        """Crea una moneda si el código no está repetido."""
        if self.buscar_por_codigo(entidad.codigo) is not None:
            raise ValueError(f"Ya existe la moneda {entidad.codigo}.")
        return self.__repositorio.crear(entidad)

    def leer_por_id(self, id: int) -> Optional[Moneda]:
        """Lee una moneda por id."""
        return self.__repositorio.leer_por_id(id)

    def leer_todos(self) -> List[Moneda]:
        """Lee todas las monedas."""
        return self.__repositorio.leer_todos()

    def buscar_por_codigo(self, codigo: str) -> Optional[Moneda]:
        """Busca una moneda por su código."""
        buscado = codigo.strip().upper()
        for moneda in self.__repositorio.leer_todos():
            if moneda.codigo == buscado:
                return moneda
        return None

    def actualizar(self, entidad: Moneda) -> Moneda:
        """Actualiza una moneda."""
        if self.__repositorio.leer_por_id(entidad.id) is None:
            raise ValueError("No se encuentra la moneda para actualizar.")
        otro = self.buscar_por_codigo(entidad.codigo)
        if otro is not None and otro.id != entidad.id:
            raise ValueError(f"Ya existe la moneda {entidad.codigo}.")
        return self.__repositorio.actualizar(entidad)

    def eliminar(self, id: int) -> bool:
        """Elimina una moneda que no esté usada en precios."""
        if any(precio.moneda_id == id for precio in self.__precios.leer_todos()):
            raise ValueError(
                "No se puede eliminar la moneda porque hay precios asociados."
            )
        return self.__repositorio.eliminar(id)


class TipoCotizacionServicio:
    """Reglas de alta, lectura, modificación y borrado de tipos de cotización."""

    def __init__(
        self,
        repositorio: IRepositorio[TipoCotizacion],
        cotizaciones: IRepositorioCotizacionDolar,
    ) -> None:
        self.__repositorio = repositorio
        self.__cotizaciones = cotizaciones

    def crear(self, entidad: TipoCotizacion) -> TipoCotizacion:
        """Crea un tipo de cotización si el nombre no está repetido."""
        if self.buscar_por_nombre(entidad.nombre) is not None:
            raise ValueError(f"Ya existe el tipo de cotización {entidad.nombre}.")
        return self.__repositorio.crear(entidad)

    def leer_por_id(self, id: int) -> Optional[TipoCotizacion]:
        """Lee un tipo de cotización por id."""
        return self.__repositorio.leer_por_id(id)

    def leer_todos(self) -> List[TipoCotizacion]:
        """Lee todos los tipos de cotización."""
        return self.__repositorio.leer_todos()

    def buscar_por_nombre(self, nombre: str) -> Optional[TipoCotizacion]:
        """Busca un tipo de cotización por nombre."""
        for tipo in self.__repositorio.leer_todos():
            if _mismo_texto(tipo.nombre, nombre):
                return tipo
        return None

    def actualizar(self, entidad: TipoCotizacion) -> TipoCotizacion:
        """Actualiza un tipo de cotización."""
        if self.__repositorio.leer_por_id(entidad.id) is None:
            raise ValueError("No se encuentra el tipo de cotización para actualizar.")
        otro = self.buscar_por_nombre(entidad.nombre)
        if otro is not None and otro.id != entidad.id:
            raise ValueError(f"Ya existe el tipo de cotización {entidad.nombre}.")
        return self.__repositorio.actualizar(entidad)

    def eliminar(self, id: int) -> bool:
        """Elimina un tipo que no tenga cotizaciones cargadas."""
        if self.__cotizaciones.leer_historico_por_tipo(id):
            raise ValueError(
                "No se puede eliminar el tipo porque tiene cotizaciones cargadas."
            )
        return self.__repositorio.eliminar(id)


class LibroServicio:
    """Reglas de alta, lectura, modificación y borrado de libros."""

    def __init__(
        self,
        repositorio: IRepositorio[Libro],
        generos: IRepositorio[Genero],
        editoriales: IRepositorio[Editorial],
        precios: IRepositorio[Precio],
        stocks: IRepositorioStock,
    ) -> None:
        self.__repositorio = repositorio
        self.__generos = generos
        self.__editoriales = editoriales
        self.__precios = precios
        self.__stocks = stocks

    def crear(self, entidad: Libro) -> Libro:
        """Crea un libro si el ISBN es único y las relaciones existen."""
        self.__validar_relaciones(entidad)
        if self.buscar_por_isbn(entidad.isbn) is not None:
            raise ValueError(f"Ya existe un libro con ISBN {entidad.isbn}.")
        return self.__repositorio.crear(entidad)

    def leer_por_id(self, id: int) -> Optional[Libro]:
        """Lee un libro por id."""
        return self.__repositorio.leer_por_id(id)

    def leer_todos(self) -> List[Libro]:
        """Lee todos los libros."""
        return self.__repositorio.leer_todos()

    def buscar_por_isbn(self, isbn: str) -> Optional[Libro]:
        """Busca un libro por ISBN."""
        for libro in self.__repositorio.leer_todos():
            if _mismo_texto(libro.isbn, isbn):
                return libro
        return None

    def actualizar(self, entidad: Libro) -> Libro:
        """Actualiza un libro."""
        if self.__repositorio.leer_por_id(entidad.id) is None:
            raise ValueError("No se encuentra el libro para actualizar.")
        self.__validar_relaciones(entidad)
        otro = self.buscar_por_isbn(entidad.isbn)
        if otro is not None and otro.id != entidad.id:
            raise ValueError(f"Ya existe un libro con ISBN {entidad.isbn}.")
        return self.__repositorio.actualizar(entidad)

    def eliminar(self, id: int) -> bool:
        """Elimina un libro que no tenga precio ni stock."""
        if any(precio.libro_id == id for precio in self.__precios.leer_todos()):
            raise ValueError(
                "No se puede eliminar el libro porque tiene precios asociados."
            )
        if self.__stocks.leer_por_libro(id) is not None:
            raise ValueError(
                "No se puede eliminar el libro porque tiene stock asociado."
            )
        return self.__repositorio.eliminar(id)

    def __validar_relaciones(self, entidad: Libro) -> None:
        if self.__generos.leer_por_id(entidad.genero_id) is None:
            raise ValueError("El género indicado no existe.")
        if self.__editoriales.leer_por_id(entidad.editorial_id) is None:
            raise ValueError("La editorial indicada no existe.")


class PrecioServicio:
    """Reglas de alta, lectura, modificación y borrado de precios."""

    def __init__(
        self,
        repositorio: IRepositorio[Precio],
        libros: IRepositorio[Libro],
        monedas: IRepositorio[Moneda],
    ) -> None:
        self.__repositorio = repositorio
        self.__libros = libros
        self.__monedas = monedas

    def crear(self, entidad: Precio) -> Precio:
        """Crea un precio si el libro y la moneda existen y no hay duplicado."""
        self.__validar_relaciones(entidad)
        if self.buscar(entidad.libro_id, entidad.moneda_id) is not None:
            raise ValueError("Ya existe un precio para ese libro y esa moneda.")
        return self.__repositorio.crear(entidad)

    def leer_por_id(self, id: int) -> Optional[Precio]:
        """Lee un precio por id."""
        return self.__repositorio.leer_por_id(id)

    def leer_todos(self) -> List[Precio]:
        """Lee todos los precios."""
        return self.__repositorio.leer_todos()

    def buscar(self, libro_id: int, moneda_id: int) -> Optional[Precio]:
        """Busca el precio de un libro en una moneda."""
        for precio in self.__repositorio.leer_todos():
            if precio.libro_id == libro_id and precio.moneda_id == moneda_id:
                return precio
        return None

    def actualizar(self, entidad: Precio) -> Precio:
        """Actualiza un precio."""
        if self.__repositorio.leer_por_id(entidad.id) is None:
            raise ValueError("No se encuentra el precio para actualizar.")
        self.__validar_relaciones(entidad)
        otro = self.buscar(entidad.libro_id, entidad.moneda_id)
        if otro is not None and otro.id != entidad.id:
            raise ValueError("Ya existe un precio para ese libro y esa moneda.")
        return self.__repositorio.actualizar(entidad)

    def eliminar(self, id: int) -> bool:
        """Elimina un precio por id."""
        return self.__repositorio.eliminar(id)

    def __validar_relaciones(self, entidad: Precio) -> None:
        if self.__libros.leer_por_id(entidad.libro_id) is None:
            raise ValueError("El libro indicado no existe.")
        if self.__monedas.leer_por_id(entidad.moneda_id) is None:
            raise ValueError("La moneda indicada no existe.")


class StockServicio:
    """Reglas de alta, lectura, modificación y borrado de stock."""

    def __init__(
        self,
        repositorio: IRepositorioStock,
        libros: IRepositorio[Libro],
    ) -> None:
        self.__repositorio = repositorio
        self.__libros = libros

    def crear(self, stock: Stock) -> Stock:
        """Crea el stock de un libro."""
        self.__validar_libro(stock.libro_id)
        if self.__repositorio.leer_por_libro(stock.libro_id) is not None:
            raise ValueError("Ya existe stock para ese libro.")
        return self.__repositorio.crear(stock)

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Lee el stock de un libro."""
        return self.__repositorio.leer_por_libro(libro_id)

    def leer_todos(self) -> List[Stock]:
        """Lee todos los stocks."""
        return self.__repositorio.leer_todos()

    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza el stock de un libro."""
        self.__validar_libro(stock.libro_id)
        return self.__repositorio.actualizar(stock)

    def eliminar(self, libro_id: int) -> bool:
        """Elimina el stock de un libro."""
        return self.__repositorio.eliminar(libro_id)

    def __validar_libro(self, libro_id: int) -> None:
        if self.__libros.leer_por_id(libro_id) is None:
            raise ValueError("El libro indicado no existe.")


class CotizacionDolarServicio:
    """Reglas de alta, lectura, modificación y borrado de cotizaciones."""

    def __init__(
        self,
        repositorio: IRepositorioCotizacionDolar,
        tipos: IRepositorio[TipoCotizacion],
    ) -> None:
        self.__repositorio = repositorio
        self.__tipos = tipos

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Crea una cotización si el tipo existe y la fecha no está repetida."""
        self.__validar_tipo(cotizacion.tipo_cotizacion_id)
        existente = self.__repositorio.leer_por_tipo_y_fecha(
            cotizacion.tipo_cotizacion_id,
            cotizacion.fecha,
        )
        if existente is not None:
            raise ValueError("Ya existe una cotización para ese tipo y esa fecha.")
        return self.__repositorio.crear(cotizacion)

    def leer_por_tipo_y_fecha(
        self,
        tipo_id: int,
        fecha: date,
    ) -> Optional[CotizacionDolar]:
        """Lee una cotización por tipo y fecha."""
        return self.__repositorio.leer_por_tipo_y_fecha(tipo_id, fecha)

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Lee el histórico de un tipo de cotización."""
        self.__validar_tipo(tipo_id)
        return self.__repositorio.leer_historico_por_tipo(tipo_id)

    def leer_todas(self) -> List[CotizacionDolar]:
        """Lee todas las cotizaciones."""
        return self.__repositorio.leer_todas()

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Actualiza compra y venta de una cotización existente."""
        self.__validar_tipo(cotizacion.tipo_cotizacion_id)
        return self.__repositorio.actualizar(cotizacion)

    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina una cotización por tipo y fecha."""
        return self.__repositorio.eliminar(tipo_id, fecha)

    def __validar_tipo(self, tipo_id: int) -> None:
        if self.__tipos.leer_por_id(tipo_id) is None:
            raise ValueError("El tipo de cotización indicado no existe.")


@dataclass(frozen=True)
class ComparacionCuspide:
    """Comparación entre el precio público de Cúspide y el costo de reposición."""

    titulo: str
    autor: str
    precio_cuspide_ars: float
    costo_usd: float
    tipo_cotizacion: str
    cotizacion_venta: float
    costo_reposicion_ars: float

    @property
    def diferencia_ars(self) -> float:
        """Diferencia entre el precio de Cúspide y el costo en pesos."""
        return round(self.precio_cuspide_ars - self.costo_reposicion_ars, 2)

    @property
    def cubre_el_costo(self) -> bool:
        """Indica si el precio de Cúspide alcanza para cubrir la reposición."""
        return self.diferencia_ars >= 0


@dataclass(frozen=True)
class LineaStock:
    """Fila del reporte de reposición."""

    titulo: str
    autor: str
    cantidad: int
    punto_reposicion: int


@dataclass(frozen=True)
class LineaHistorico:
    """Fila del histórico de una cotización."""

    fecha: date
    tipo: str
    compra: float
    venta: float


class ReporteServicio:
    """Reportes del sprint: cotización, Cúspide, stock e histórico."""

    def __init__(
        self,
        libros: IRepositorio[Libro],
        precios: IRepositorio[Precio],
        monedas: IRepositorio[Moneda],
        stocks: IRepositorioStock,
        cotizaciones: IRepositorioCotizacionDolar,
        tipos: IRepositorio[TipoCotizacion],
    ) -> None:
        self.__libros = libros
        self.__precios = precios
        self.__monedas = monedas
        self.__stocks = stocks
        self.__cotizaciones = cotizaciones
        self.__tipos = tipos

    def comparar_con_cuspide(self, tipo_id: int) -> List[ComparacionCuspide]:
        """Cotiza el costo en dólares y lo compara con el precio de Cúspide.

        Args:
            tipo_id (int): Tipo de dólar usado para pasar el costo a pesos.

        Returns:
            List[ComparacionCuspide]: Una fila por libro que tenga precio
            en pesos y en dólares.

        Raises:
            ValueError: Si el tipo no existe o no tiene cotizaciones.
        """
        tipo = self.__tipos.leer_por_id(tipo_id)
        if tipo is None:
            raise ValueError("El tipo de cotización indicado no existe.")
        cotizacion = self.__ultima_cotizacion(tipo_id)
        moneda_ars = self.__moneda_por_codigo("ARS")
        moneda_usd = self.__moneda_por_codigo("USD")
        filas: List[ComparacionCuspide] = []
        for libro in self.__libros.leer_todos():
            precio_ars = self.__importe(libro.id, moneda_ars.id)
            costo_usd = self.__importe(libro.id, moneda_usd.id)
            if precio_ars is None or costo_usd is None:
                continue
            costo_ars = round(costo_usd * cotizacion.venta, 2)
            filas.append(
                ComparacionCuspide(
                    titulo=libro.titulo,
                    autor=libro.autor,
                    precio_cuspide_ars=precio_ars,
                    costo_usd=costo_usd,
                    tipo_cotizacion=tipo.nombre,
                    cotizacion_venta=cotizacion.venta,
                    costo_reposicion_ars=costo_ars,
                )
            )
        return filas

    def stock_a_reponer(self) -> List[LineaStock]:
        """Devuelve los libros con stock en el punto de reposición o por debajo."""
        titulos = {
            libro.id: libro
            for libro in self.__libros.leer_todos()
        }
        filas: List[LineaStock] = []
        for stock in self.__stocks.leer_todos():
            if stock.cantidad > stock.punto_reposicion:
                continue
            libro = titulos.get(stock.libro_id)
            if libro is None:
                continue
            filas.append(
                LineaStock(
                    titulo=libro.titulo,
                    autor=libro.autor,
                    cantidad=stock.cantidad,
                    punto_reposicion=stock.punto_reposicion,
                )
            )
        return filas

    def historico(self, tipo_id: int) -> List[LineaHistorico]:
        """Devuelve el histórico de un tipo de dólar, ordenado por fecha."""
        tipo = self.__tipos.leer_por_id(tipo_id)
        if tipo is None:
            raise ValueError("El tipo de cotización indicado no existe.")
        return [
            LineaHistorico(
                fecha=item.fecha,
                tipo=tipo.nombre,
                compra=item.compra,
                venta=item.venta,
            )
            for item in self.__cotizaciones.leer_historico_por_tipo(tipo_id)
        ]

    def __ultima_cotizacion(self, tipo_id: int) -> CotizacionDolar:
        historico = self.__cotizaciones.leer_historico_por_tipo(tipo_id)
        if not historico:
            raise ValueError("No hay cotizaciones para el tipo indicado.")
        return historico[-1]

    def __moneda_por_codigo(self, codigo: str) -> Moneda:
        for moneda in self.__monedas.leer_todos():
            if moneda.codigo == codigo:
                return moneda
        raise ValueError(f"No está cargada la moneda {codigo}.")

    def __importe(self, libro_id: int, moneda_id: int) -> Optional[float]:
        for precio in self.__precios.leer_todos():
            if precio.libro_id == libro_id and precio.moneda_id == moneda_id:
                return precio.importe
        return None


@dataclass
class Contexto:
    """Servicios que usa la consola y la demostración."""

    generos: GeneroServicio
    editoriales: EditorialServicio
    monedas: MonedaServicio
    tipos_cotizacion: TipoCotizacionServicio
    libros: LibroServicio
    precios: PrecioServicio
    stocks: StockServicio
    cotizaciones: CotizacionDolarServicio
    reportes: ReporteServicio
