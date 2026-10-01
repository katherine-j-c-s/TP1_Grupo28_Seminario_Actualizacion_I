"""Repositorios CSV de Book Manager.

Cada clase concreta implementa el CRUD de una entidad. El archivo de
trabajo es un CSV: la migración inicial no se modifica desde acá.
"""

import abc
import csv
from datetime import date
from pathlib import Path
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar

from book_manager.entities.entities import CotizacionDolar
from book_manager.entities.entities import Editorial
from book_manager.entities.entities import EntidadBase
from book_manager.entities.entities import Genero
from book_manager.entities.entities import Libro
from book_manager.entities.entities import Moneda
from book_manager.entities.entities import Precio
from book_manager.entities.entities import Stock
from book_manager.entities.entities import TipoCotizacion

T = TypeVar("T", bound=EntidadBase)


def leer_filas(archivo: Path) -> List[Dict[str, str]]:
    """Lee un CSV y devuelve sus filas.

    Args:
        archivo (Path): Ruta del CSV.

    Returns:
        List[Dict[str, str]]: Filas, sin incluir el encabezado.
    """
    if not archivo.exists():
        return []
    with archivo.open("r", encoding="utf-8", newline="") as origen:
        return [
            fila
            for fila in csv.DictReader(origen)
            if fila and any(fila.values())
        ]


def escribir_filas(
    archivo: Path,
    columnas: List[str],
    filas: List[Dict[str, str]],
) -> None:
    """Escribe un CSV completo.

    Args:
        archivo (Path): Ruta del CSV.
        columnas (List[str]): Encabezados.
        filas (List[Dict[str, str]]): Filas a guardar.
    """
    archivo.parent.mkdir(parents=True, exist_ok=True)
    with archivo.open("w", encoding="utf-8", newline="") as destino:
        escritor = csv.DictWriter(destino, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)


class IRepositorio(abc.ABC, Generic[T]):
    """Interfaz para repositorios que manejan entidades con operaciones CRUD."""

    @abc.abstractmethod
    def crear(self, entidad: T) -> T:
        """Crea una nueva entidad en el repositorio.

        Args:
            entidad (T): La entidad a crear.

        Returns:
            T: La entidad creada.

        Raises:
            ValueError: Si ya existe una entidad con el mismo ID.
        """

    @abc.abstractmethod
    def leer_por_id(self, id: int) -> Optional[T]:
        """Lee una entidad del repositorio por su ID.

        Args:
            id (int): El ID de la entidad a leer.

        Returns:
            Optional[T]: La entidad si se encuentra, None en caso contrario.
        """

    @abc.abstractmethod
    def leer_todos(self) -> List[T]:
        """Lee todas las entidades del repositorio.

        Returns:
            List[T]: Una lista de todas las entidades.
        """

    @abc.abstractmethod
    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad existente en el repositorio.

        Args:
            entidad (T): La entidad a actualizar (debe tener un ID existente).

        Returns:
            T: La entidad actualizada.

        Raises:
            ValueError: Si no se encuentra la entidad para actualizar.
        """

    @abc.abstractmethod
    def eliminar(self, id: int) -> bool:
        """Elimina una entidad del repositorio por su ID.

        Args:
            id (int): El ID de la entidad a eliminar.

        Returns:
            bool: True si la entidad fue eliminada, False si no se encontró.
        """


class IRepositorioStock(abc.ABC):
    """Interfaz para repositorios del tipo Stock."""

    @abc.abstractmethod
    def crear(self, stock: Stock) -> Stock:
        """Crea un nuevo registro de stock.

        Args:
            stock (Stock): El objeto Stock a crear.

        Returns:
            Stock: El objeto Stock creado.

        Raises:
            ValueError: Si ya existe un registro de stock para el mismo libro.
        """

    @abc.abstractmethod
    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Lee un registro de stock por ID de libro.

        Args:
            libro_id (int): El ID del libro asociado al stock.

        Returns:
            Optional[Stock]: El objeto Stock si se encuentra, None en caso contrario.
        """

    @abc.abstractmethod
    def leer_todos(self) -> List[Stock]:
        """Lee todos los registros de stock.

        Returns:
            List[Stock]: Stocks cargados.
        """

    @abc.abstractmethod
    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza un registro de stock existente.

        Args:
            stock (Stock): El objeto Stock a actualizar.

        Returns:
            Stock: El objeto Stock actualizado.

        Raises:
            ValueError: Si no se encuentra el stock para actualizar.
        """

    @abc.abstractmethod
    def eliminar(self, libro_id: int) -> bool:
        """Elimina un registro de stock por ID de libro.

        Args:
            libro_id (int): El ID del libro asociado al stock a eliminar.

        Returns:
            bool: True si el stock fue eliminado, False si no se encontró.
        """


class IRepositorioCotizacionDolar(abc.ABC):
    """Interfaz para repositorios del tipo RepositorioCotizacionDolar."""

    @abc.abstractmethod
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Crea una nueva cotización de dólar.

        Args:
            cotizacion (CotizacionDolar): El objeto CotizacionDolar a crear.

        Returns:
            CotizacionDolar: El objeto CotizacionDolar creado.

        Raises:
            ValueError: Si ya existe una cotización para el mismo tipo y fecha.
        """

    @abc.abstractmethod
    def leer_por_tipo_y_fecha(
        self,
        tipo_id: int,
        fecha: date,
    ) -> Optional[CotizacionDolar]:
        """Lee una cotización de dólar por tipo y fecha.

        Args:
            tipo_id (int): El ID del tipo de cotización.
            fecha (date): La fecha de la cotización.

        Returns:
            Optional[CotizacionDolar]: La cotización si se encuentra, None si no.
        """

    @abc.abstractmethod
    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Lee el histórico de cotizaciones para un tipo específico.

        Args:
            tipo_id (int): El ID del tipo de cotización.

        Returns:
            List[CotizacionDolar]: Cotizaciones históricas del tipo, por fecha.
        """

    @abc.abstractmethod
    def leer_todas(self) -> List[CotizacionDolar]:
        """Lee todas las cotizaciones.

        Returns:
            List[CotizacionDolar]: Cotizaciones cargadas.
        """

    @abc.abstractmethod
    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Actualiza una cotización de dólar existente.

        Args:
            cotizacion (CotizacionDolar): El objeto CotizacionDolar a actualizar.

        Returns:
            CotizacionDolar: El objeto CotizacionDolar actualizado.

        Raises:
            ValueError: Si no se encuentra la cotización para actualizar.
        """

    @abc.abstractmethod
    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina una cotización de dólar por tipo y fecha.

        Args:
            tipo_id (int): El ID del tipo de cotización.
            fecha (date): La fecha de la cotización a eliminar.

        Returns:
            bool: True si la cotización fue eliminada, False si no se encontró.
        """


class RepositorioCSV(IRepositorio[T], abc.ABC):
    """CRUD genérico persistido en un CSV, con clave entera."""

    def __init__(self, archivo: Path) -> None:
        """Constructor.

        Args:
            archivo (Path): CSV de la entidad.
        """
        self._archivo = archivo
        self._entidades: Dict[int, T] = {}
        self._cargar()

    @abc.abstractmethod
    def _columnas(self) -> List[str]:
        """Devuelve los encabezados del CSV."""

    @abc.abstractmethod
    def _desde_fila(self, fila: Dict[str, str]) -> T:
        """Construye la entidad a partir de una fila."""

    @abc.abstractmethod
    def _hacia_fila(self, entidad: T) -> Dict[str, str]:
        """Convierte la entidad en una fila de CSV."""

    def _clonar(self, entidad: T) -> T:
        """Devuelve una copia para no exponer el objeto interno."""
        return self._desde_fila(self._hacia_fila(entidad))

    def _cargar(self) -> None:
        """Carga el CSV en memoria."""
        self._entidades = {}
        for fila in leer_filas(self._archivo):
            entidad = self._desde_fila(fila)
            self._entidades[entidad.id] = entidad

    def _guardar(self) -> None:
        """Vuelve a escribir el CSV completo."""
        filas = [
            self._hacia_fila(self._entidades[clave])
            for clave in sorted(self._entidades)
        ]
        escribir_filas(self._archivo, self._columnas(), filas)

    def _siguiente_id(self) -> int:
        """Calcula el próximo id libre."""
        if not self._entidades:
            return 1
        return max(self._entidades) + 1

    def crear(self, entidad: T) -> T:
        """Crea una entidad. Si el id es 0, asigna el siguiente."""
        if entidad.id == 0:
            entidad.id = self._siguiente_id()
        if entidad.id in self._entidades:
            raise ValueError("Ya existe una entidad con el mismo ID.")
        self._entidades[entidad.id] = self._clonar(entidad)
        self._guardar()
        return entidad

    def leer_por_id(self, id: int) -> Optional[T]:
        """Lee una entidad por id."""
        entidad = self._entidades.get(id)
        if entidad is None:
            return None
        return self._clonar(entidad)

    def leer_todos(self) -> List[T]:
        """Lee todas las entidades ordenadas por id."""
        return [self._clonar(self._entidades[clave]) for clave in sorted(self._entidades)]

    def actualizar(self, entidad: T) -> T:
        """Reemplaza una entidad existente."""
        if entidad.id not in self._entidades:
            raise ValueError("No se encuentra la entidad para actualizar.")
        self._entidades[entidad.id] = self._clonar(entidad)
        self._guardar()
        return entidad

    def eliminar(self, id: int) -> bool:
        """Elimina una entidad por id."""
        if id not in self._entidades:
            return False
        del self._entidades[id]
        self._guardar()
        return True


class RepositorioGenero(RepositorioCSV[Genero]):
    """Persistencia de géneros."""

    def __init__(self, directorio: Path) -> None:
        super().__init__(directorio / "generos.csv")

    def _columnas(self) -> List[str]:
        return ["id", "nombre", "descripcion"]

    def _desde_fila(self, fila: Dict[str, str]) -> Genero:
        return Genero(
            id=int(fila["id"]),
            nombre=fila["nombre"],
            descripcion=fila["descripcion"],
        )

    def _hacia_fila(self, entidad: Genero) -> Dict[str, str]:
        return {
            "id": str(entidad.id),
            "nombre": entidad.nombre,
            "descripcion": entidad.descripcion,
        }


class RepositorioEditorial(RepositorioCSV[Editorial]):
    """Persistencia de editoriales."""

    def __init__(self, directorio: Path) -> None:
        super().__init__(directorio / "editoriales.csv")

    def _columnas(self) -> List[str]:
        return ["id", "nombre", "pais", "sitio_web"]

    def _desde_fila(self, fila: Dict[str, str]) -> Editorial:
        return Editorial(
            id=int(fila["id"]),
            nombre=fila["nombre"],
            pais=fila["pais"],
            sitio_web=fila["sitio_web"],
        )

    def _hacia_fila(self, entidad: Editorial) -> Dict[str, str]:
        return {
            "id": str(entidad.id),
            "nombre": entidad.nombre,
            "pais": entidad.pais,
            "sitio_web": entidad.sitio_web,
        }


class RepositorioMoneda(RepositorioCSV[Moneda]):
    """Persistencia de monedas."""

    def __init__(self, directorio: Path) -> None:
        super().__init__(directorio / "monedas.csv")

    def _columnas(self) -> List[str]:
        return ["id", "codigo", "nombre", "simbolo"]

    def _desde_fila(self, fila: Dict[str, str]) -> Moneda:
        return Moneda(
            id=int(fila["id"]),
            codigo=fila["codigo"],
            nombre=fila["nombre"],
            simbolo=fila["simbolo"],
        )

    def _hacia_fila(self, entidad: Moneda) -> Dict[str, str]:
        return {
            "id": str(entidad.id),
            "codigo": entidad.codigo,
            "nombre": entidad.nombre,
            "simbolo": entidad.simbolo,
        }


class RepositorioTipoCotizacion(RepositorioCSV[TipoCotizacion]):
    """Persistencia de tipos de cotización."""

    def __init__(self, directorio: Path) -> None:
        super().__init__(directorio / "tipos_cotizacion.csv")

    def _columnas(self) -> List[str]:
        return ["id", "nombre", "descripcion"]

    def _desde_fila(self, fila: Dict[str, str]) -> TipoCotizacion:
        return TipoCotizacion(
            id=int(fila["id"]),
            nombre=fila["nombre"],
            descripcion=fila["descripcion"],
        )

    def _hacia_fila(self, entidad: TipoCotizacion) -> Dict[str, str]:
        return {
            "id": str(entidad.id),
            "nombre": entidad.nombre,
            "descripcion": entidad.descripcion,
        }


class RepositorioLibro(RepositorioCSV[Libro]):
    """Persistencia de libros."""

    def __init__(self, directorio: Path) -> None:
        super().__init__(directorio / "libros.csv")

    def _columnas(self) -> List[str]:
        return [
            "id",
            "isbn",
            "titulo",
            "autor",
            "editorial_id",
            "genero_id",
            "anio",
            "paginas",
        ]

    def _desde_fila(self, fila: Dict[str, str]) -> Libro:
        return Libro(
            id=int(fila["id"]),
            isbn=fila["isbn"],
            titulo=fila["titulo"],
            autor=fila["autor"],
            editorial_id=int(fila["editorial_id"]),
            genero_id=int(fila["genero_id"]),
            anio=int(fila["anio"]),
            paginas=int(fila["paginas"]),
        )

    def _hacia_fila(self, entidad: Libro) -> Dict[str, str]:
        return {
            "id": str(entidad.id),
            "isbn": entidad.isbn,
            "titulo": entidad.titulo,
            "autor": entidad.autor,
            "editorial_id": str(entidad.editorial_id),
            "genero_id": str(entidad.genero_id),
            "anio": str(entidad.anio),
            "paginas": str(entidad.paginas),
        }


class RepositorioPrecio(RepositorioCSV[Precio]):
    """Persistencia de precios."""

    def __init__(self, directorio: Path) -> None:
        super().__init__(directorio / "precios.csv")

    def _columnas(self) -> List[str]:
        return ["id", "libro_id", "moneda_id", "importe"]

    def _desde_fila(self, fila: Dict[str, str]) -> Precio:
        return Precio(
            id=int(fila["id"]),
            libro_id=int(fila["libro_id"]),
            moneda_id=int(fila["moneda_id"]),
            importe=float(fila["importe"]),
        )

    def _hacia_fila(self, entidad: Precio) -> Dict[str, str]:
        return {
            "id": str(entidad.id),
            "libro_id": str(entidad.libro_id),
            "moneda_id": str(entidad.moneda_id),
            "importe": f"{entidad.importe:.2f}",
        }


class RepositorioStock(IRepositorioStock):
    """Persistencia de stock. La clave es el id del libro."""

    def __init__(self, directorio: Path) -> None:
        self.__archivo = directorio / "stocks.csv"
        self.__stocks: Dict[int, Stock] = {}
        self.__cargar()

    def __columnas(self) -> List[str]:
        return ["libro_id", "cantidad", "punto_reposicion"]

    def __desde_fila(self, fila: Dict[str, str]) -> Stock:
        return Stock(
            libro_id=int(fila["libro_id"]),
            cantidad=int(fila["cantidad"]),
            punto_reposicion=int(fila["punto_reposicion"]),
        )

    def __hacia_fila(self, stock: Stock) -> Dict[str, str]:
        return {
            "libro_id": str(stock.libro_id),
            "cantidad": str(stock.cantidad),
            "punto_reposicion": str(stock.punto_reposicion),
        }

    def __clonar(self, stock: Stock) -> Stock:
        return self.__desde_fila(self.__hacia_fila(stock))

    def __cargar(self) -> None:
        self.__stocks = {}
        for fila in leer_filas(self.__archivo):
            stock = self.__desde_fila(fila)
            self.__stocks[stock.libro_id] = stock

    def __guardar(self) -> None:
        filas = [
            self.__hacia_fila(self.__stocks[clave])
            for clave in sorted(self.__stocks)
        ]
        escribir_filas(self.__archivo, self.__columnas(), filas)

    def crear(self, stock: Stock) -> Stock:
        if stock.libro_id in self.__stocks:
            raise ValueError("Ya existe un registro de stock para el mismo libro.")
        self.__stocks[stock.libro_id] = self.__clonar(stock)
        self.__guardar()
        return stock

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        stock = self.__stocks.get(libro_id)
        if stock is None:
            return None
        return self.__clonar(stock)

    def leer_todos(self) -> List[Stock]:
        return [self.__clonar(self.__stocks[clave]) for clave in sorted(self.__stocks)]

    def actualizar(self, stock: Stock) -> Stock:
        if stock.libro_id not in self.__stocks:
            raise ValueError("No se encuentra el stock para actualizar.")
        self.__stocks[stock.libro_id] = self.__clonar(stock)
        self.__guardar()
        return stock

    def eliminar(self, libro_id: int) -> bool:
        if libro_id not in self.__stocks:
            return False
        del self.__stocks[libro_id]
        self.__guardar()
        return True


class RepositorioCotizacionDolar(IRepositorioCotizacionDolar):
    """Persistencia del histórico de cotizaciones del dólar."""

    def __init__(self, directorio: Path) -> None:
        self.__archivo = directorio / "cotizaciones_dolar.csv"
        self.__cotizaciones: Dict[tuple, CotizacionDolar] = {}
        self.__cargar()

    def __columnas(self) -> List[str]:
        return ["tipo_id", "fecha", "compra", "venta"]

    def __clave(self, tipo_id: int, fecha: date) -> tuple:
        return (tipo_id, fecha.isoformat())

    def __desde_fila(self, fila: Dict[str, str]) -> CotizacionDolar:
        return CotizacionDolar(
            tipo_cotizacion_id=int(fila["tipo_id"]),
            fecha=date.fromisoformat(fila["fecha"]),
            compra=float(fila["compra"]),
            venta=float(fila["venta"]),
        )

    def __hacia_fila(self, cotizacion: CotizacionDolar) -> Dict[str, str]:
        return {
            "tipo_id": str(cotizacion.tipo_cotizacion_id),
            "fecha": cotizacion.fecha.isoformat(),
            "compra": f"{cotizacion.compra:.2f}",
            "venta": f"{cotizacion.venta:.2f}",
        }

    def __clonar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        return self.__desde_fila(self.__hacia_fila(cotizacion))

    def __cargar(self) -> None:
        self.__cotizaciones = {}
        for fila in leer_filas(self.__archivo):
            cotizacion = self.__desde_fila(fila)
            clave = self.__clave(cotizacion.tipo_cotizacion_id, cotizacion.fecha)
            self.__cotizaciones[clave] = cotizacion

    def __guardar(self) -> None:
        ordenadas = sorted(
            self.__cotizaciones.values(),
            key=lambda item: (item.tipo_cotizacion_id, item.fecha),
        )
        filas = [self.__hacia_fila(item) for item in ordenadas]
        escribir_filas(self.__archivo, self.__columnas(), filas)

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        clave = self.__clave(cotizacion.tipo_cotizacion_id, cotizacion.fecha)
        if clave in self.__cotizaciones:
            raise ValueError("Ya existe una cotización para el mismo tipo y fecha.")
        self.__cotizaciones[clave] = self.__clonar(cotizacion)
        self.__guardar()
        return cotizacion

    def leer_por_tipo_y_fecha(
        self,
        tipo_id: int,
        fecha: date,
    ) -> Optional[CotizacionDolar]:
        cotizacion = self.__cotizaciones.get(self.__clave(tipo_id, fecha))
        if cotizacion is None:
            return None
        return self.__clonar(cotizacion)

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        historico = [
            self.__clonar(item)
            for item in self.__cotizaciones.values()
            if item.tipo_cotizacion_id == tipo_id
        ]
        return sorted(historico, key=lambda item: item.fecha)

    def leer_todas(self) -> List[CotizacionDolar]:
        ordenadas = sorted(
            self.__cotizaciones.values(),
            key=lambda item: (item.fecha, item.tipo_cotizacion_id),
        )
        return [self.__clonar(item) for item in ordenadas]

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        clave = self.__clave(cotizacion.tipo_cotizacion_id, cotizacion.fecha)
        if clave not in self.__cotizaciones:
            raise ValueError("No se encuentra la cotización para actualizar.")
        self.__cotizaciones[clave] = self.__clonar(cotizacion)
        self.__guardar()
        return cotizacion

    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        clave = self.__clave(tipo_id, fecha)
        if clave not in self.__cotizaciones:
            return False
        del self.__cotizaciones[clave]
        self.__guardar()
        return True
