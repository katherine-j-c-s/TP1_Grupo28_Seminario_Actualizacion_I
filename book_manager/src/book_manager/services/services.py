"""Lógica de negocio de Book Manager sobre la base relacional."""

import csv
import json
import os
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from pathlib import Path
from typing import List
from typing import Optional
from urllib.request import Request
from urllib.request import urlopen

from dotenv import load_dotenv

from book_manager.database.connection import ConexionDB
from book_manager.entities.entities import CotizacionDolar
from book_manager.entities.entities import Editorial
from book_manager.entities.entities import Genero
from book_manager.entities.entities import Libro
from book_manager.entities.entities import Moneda
from book_manager.entities.entities import Precio
from book_manager.entities.entities import Stock
from book_manager.entities.entities import TipoCotizacion
from book_manager.repositories.repositories import RepositorioCotizacionDolar
from book_manager.repositories.repositories import RepositorioEditorial
from book_manager.repositories.repositories import RepositorioGenero
from book_manager.repositories.repositories import RepositorioLibro
from book_manager.repositories.repositories import RepositorioMoneda
from book_manager.repositories.repositories import RepositorioPrecio
from book_manager.repositories.repositories import RepositorioStock
from book_manager.repositories.repositories import RepositorioTipoCotizacion

MAPA_CASA_DOLAR = {
    "oficial": "Oficial",
    "blue": "Blue",
    "bolsa": "MEP",
    "contadoconliqui": "CCL",
    "mayorista": "Mayorista",
    "tarjeta": "Tarjeta",
    "cripto": "Cripto",
}


def _mismo_texto(izquierdo: str, derecho: str) -> bool:
    """Compara dos textos sin distinguir mayúsculas."""
    return izquierdo.strip().casefold() == derecho.strip().casefold()


def cargar_env() -> None:
    """Carga el archivo .env de la raíz del proyecto book_manager."""
    ruta = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(ruta)


class GeneroServicio:
    """Reglas de alta, lectura, modificación y borrado de géneros."""

    def __init__(self, repositorio: RepositorioGenero, libros: RepositorioLibro) -> None:
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
        if any(libro.genero.id == id for libro in self.__libros.leer_todos()):
            raise ValueError(
                "No se puede eliminar el género porque hay libros asociados."
            )
        return self.__repositorio.eliminar(id)


class EditorialServicio:
    """Reglas de alta, lectura, modificación y borrado de editoriales."""

    def __init__(
        self, repositorio: RepositorioEditorial, libros: RepositorioLibro
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
        if any(libro.editorial.id == id for libro in self.__libros.leer_todos()):
            raise ValueError(
                "No se puede eliminar la editorial porque hay libros asociados."
            )
        return self.__repositorio.eliminar(id)


class MonedaServicio:
    """Reglas de alta, lectura, modificación y borrado de monedas."""

    def __init__(self, repositorio: RepositorioMoneda, precios: RepositorioPrecio) -> None:
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
        if any(precio.moneda.id == id for precio in self.__precios.leer_todos()):
            raise ValueError(
                "No se puede eliminar la moneda porque hay precios asociados."
            )
        return self.__repositorio.eliminar(id)


class TipoCotizacionServicio:
    """Reglas de alta, lectura, modificación y borrado de tipos de cotización."""

    def __init__(
        self,
        repositorio: RepositorioTipoCotizacion,
        cotizaciones: RepositorioCotizacionDolar,
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
        repositorio: RepositorioLibro,
        generos: RepositorioGenero,
        editoriales: RepositorioEditorial,
        precios: RepositorioPrecio,
        stocks: RepositorioStock,
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
        if any(precio.libro.id == id for precio in self.__precios.leer_todos()):
            raise ValueError(
                "No se puede eliminar el libro porque tiene precios asociados."
            )
        if self.__stocks.leer_por_libro(id) is not None:
            raise ValueError(
                "No se puede eliminar el libro porque tiene stock asociado."
            )
        return self.__repositorio.eliminar(id)

    def __validar_relaciones(self, entidad: Libro) -> None:
        if self.__generos.leer_por_id(entidad.genero.id) is None:
            raise ValueError("El género indicado no existe.")
        if self.__editoriales.leer_por_id(entidad.editorial.id) is None:
            raise ValueError("La editorial indicada no existe.")


class PrecioServicio:
    """Reglas de alta, lectura, modificación y borrado de precios."""

    def __init__(
        self,
        repositorio: RepositorioPrecio,
        libros: RepositorioLibro,
        monedas: RepositorioMoneda,
    ) -> None:
        self.__repositorio = repositorio
        self.__libros = libros
        self.__monedas = monedas

    def crear(self, entidad: Precio) -> Precio:
        """Crea un precio si el libro y la moneda existen y no hay duplicado."""
        self.__validar_relaciones(entidad)
        if self.buscar(entidad.libro.id, entidad.moneda.id) is not None:
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
            if precio.libro.id == libro_id and precio.moneda.id == moneda_id:
                return precio
        return None

    def actualizar(self, entidad: Precio) -> Precio:
        """Actualiza un precio."""
        if self.__repositorio.leer_por_id(entidad.id) is None:
            raise ValueError("No se encuentra el precio para actualizar.")
        self.__validar_relaciones(entidad)
        otro = self.buscar(entidad.libro.id, entidad.moneda.id)
        if otro is not None and otro.id != entidad.id:
            raise ValueError("Ya existe un precio para ese libro y esa moneda.")
        return self.__repositorio.actualizar(entidad)

    def eliminar(self, id: int) -> bool:
        """Elimina un precio por id."""
        return self.__repositorio.eliminar(id)

    def __validar_relaciones(self, entidad: Precio) -> None:
        if self.__libros.leer_por_id(entidad.libro.id) is None:
            raise ValueError("El libro indicado no existe.")
        if self.__monedas.leer_por_id(entidad.moneda.id) is None:
            raise ValueError("La moneda indicada no existe.")


class StockServicio:
    """Reglas de alta, lectura, modificación y borrado de stock."""

    def __init__(self, repositorio: RepositorioStock, libros: RepositorioLibro) -> None:
        self.__repositorio = repositorio
        self.__libros = libros

    def crear(self, stock: Stock) -> Stock:
        """Crea el stock de un libro."""
        self.__validar_libro(stock.libro.id)
        if self.__repositorio.leer_por_libro(stock.libro.id) is not None:
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
        self.__validar_libro(stock.libro.id)
        return self.__repositorio.actualizar(stock)

    def eliminar(self, libro_id: int) -> bool:
        """Elimina el stock de un libro."""
        return self.__repositorio.eliminar(libro_id)

    def __validar_libro(self, libro_id: int) -> None:
        if self.__libros.leer_por_id(libro_id) is None:
            raise ValueError("El libro indicado no existe.")


class ServicioCotizacionDolar:
    """Reglas de cotización y descarga desde la API del dólar."""

    def __init__(
        self,
        repositorio: RepositorioCotizacionDolar,
        tipos: RepositorioTipoCotizacion,
    ) -> None:
        self.__repositorio = repositorio
        self.__tipos = tipos

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Crea una cotización si el tipo existe y la fecha no está repetida."""
        self.__validar_tipo(cotizacion.tipo_cotizacion.id)
        existente = self.__repositorio.leer_por_tipo_y_fecha(
            cotizacion.tipo_cotizacion.id,
            cotizacion.fecha,
        )
        if existente is not None:
            raise ValueError("Ya existe una cotización para ese tipo y esa fecha.")
        return self.__repositorio.crear(cotizacion)

    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: date
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
        self.__validar_tipo(cotizacion.tipo_cotizacion.id)
        return self.__repositorio.actualizar(cotizacion)

    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina una cotización por tipo y fecha."""
        return self.__repositorio.eliminar(tipo_id, fecha)

    def obtener_cotizaciones(self) -> List[CotizacionDolar]:
        """Descarga las cotizaciones de la API y las registra en la base.

        La URL se lee de la variable API_URL del archivo .env.

        Returns:
            List[CotizacionDolar]: Cotizaciones creadas o actualizadas.

        Raises:
            ValueError: Si falta API_URL o la respuesta no es una lista.
        """
        cargar_env()
        url = os.getenv("API_URL", "").strip()
        if url == "":
            raise ValueError("Falta API_URL en el archivo .env.")
        pedido = Request(
            url,
            headers={"User-Agent": "BookManager/1.0 (Grupo 28; educational)"},
        )
        with urlopen(pedido, timeout=30) as respuesta:
            payload = json.loads(respuesta.read().decode("utf-8"))
        if not isinstance(payload, list):
            raise ValueError("La API del dólar no devolvió una lista.")
        registradas: List[CotizacionDolar] = []
        for item in payload:
            casa = str(item.get("casa", "")).strip().lower()
            nombre = MAPA_CASA_DOLAR.get(casa)
            if nombre is None:
                continue
            compra = item.get("compra")
            venta = item.get("venta")
            if compra is None or venta is None:
                continue
            if float(compra) <= 0 or float(venta) <= 0 or float(compra) > float(venta):
                continue
            fecha = _fecha_de_api(item.get("fechaActualizacion"))
            tipo = self.__tipo_para(nombre, str(item.get("nombre") or nombre))
            cotizacion = CotizacionDolar(
                tipo_cotizacion=tipo,
                fecha=fecha,
                compra=float(compra),
                venta=float(venta),
            )
            existente = self.__repositorio.leer_por_tipo_y_fecha(tipo.id, fecha)
            if existente is None:
                registradas.append(self.__repositorio.crear(cotizacion))
            else:
                registradas.append(self.__repositorio.actualizar(cotizacion))
        return registradas

    def __tipo_para(self, nombre: str, descripcion: str) -> TipoCotizacion:
        existente = None
        for tipo in self.__tipos.leer_todos():
            if _mismo_texto(tipo.nombre, nombre):
                existente = tipo
                break
        if existente is not None:
            return existente
        return self.__tipos.crear(
            TipoCotizacion(id=0, nombre=nombre, descripcion=descripcion)
        )

    def __validar_tipo(self, tipo_id: int) -> None:
        if self.__tipos.leer_por_id(tipo_id) is None:
            raise ValueError("El tipo de cotización indicado no existe.")


def _fecha_de_api(valor: Optional[str]) -> date:
    """Toma la fecha de la marca de tiempo que devuelve la API."""
    if not valor:
        return date.today()
    texto = str(valor).replace("Z", "")
    try:
        return datetime.fromisoformat(texto).date()
    except ValueError:
        return date.fromisoformat(texto[:10])


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


@dataclass(frozen=True)
class LineaBimonetaria:
    """Precio de un libro en pesos y en otra moneda."""

    titulo: str
    autor: str
    precio_ars: Optional[float]
    codigo_moneda: str
    precio_otra: Optional[float]


class ReporteServicio:
    """Reportes de cotización, Cúspide, stock, histórico y precios bimonetarios."""

    def __init__(
        self,
        libros: RepositorioLibro,
        precios: RepositorioPrecio,
        monedas: RepositorioMoneda,
        stocks: RepositorioStock,
        cotizaciones: RepositorioCotizacionDolar,
        tipos: RepositorioTipoCotizacion,
    ) -> None:
        self.__libros = libros
        self.__precios = precios
        self.__monedas = monedas
        self.__stocks = stocks
        self.__cotizaciones = cotizaciones
        self.__tipos = tipos

    def comparar_con_cuspide(self, tipo_id: int) -> List[ComparacionCuspide]:
        """Cotiza el costo en dólares y lo compara con el precio de Cúspide."""
        tipo = self.__tipos.leer_por_id(tipo_id)
        if tipo is None:
            raise ValueError("El tipo de cotización indicado no existe.")
        historico = self.__cotizaciones.leer_historico_por_tipo(tipo_id)
        if not historico:
            raise ValueError("No hay cotizaciones para el tipo indicado.")
        cotizacion = historico[-1]
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
        filas: List[LineaStock] = []
        for stock in self.__stocks.leer_todos():
            if stock.cantidad > stock.punto_reposicion:
                continue
            filas.append(
                LineaStock(
                    titulo=stock.libro.titulo,
                    autor=stock.libro.autor,
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

    def lista_bimonetaria(self, codigo_moneda: str) -> List[LineaBimonetaria]:
        """Lista cada libro en pesos y en la moneda elegida.

        Args:
            codigo_moneda (str): Código de tres letras de la segunda moneda.

        Returns:
            List[LineaBimonetaria]: Una fila por libro.
        """
        moneda_ars = self.__moneda_por_codigo("ARS")
        otra = self.__moneda_por_codigo(codigo_moneda)
        filas: List[LineaBimonetaria] = []
        for libro in self.__libros.leer_todos():
            filas.append(
                LineaBimonetaria(
                    titulo=libro.titulo,
                    autor=libro.autor,
                    precio_ars=self.__importe(libro.id, moneda_ars.id),
                    codigo_moneda=otra.codigo,
                    precio_otra=self.__importe(libro.id, otra.id),
                )
            )
        return filas

    def exportar_precios_csv(self, ruta: Optional[Path] = None) -> Path:
        """Exporta el precio de cada libro en todas las monedas cargadas.

        Args:
            ruta (Optional[Path]): Destino del CSV. Si no se indica, se usa
                book_manager/export/precios.csv.

        Returns:
            Path: Ruta del archivo generado.
        """
        if ruta is None:
            ruta = Path(__file__).resolve().parents[3] / "export" / "precios.csv"
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with ruta.open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(
                archivo,
                fieldnames=["isbn", "titulo", "autor", "moneda", "importe"],
            )
            escritor.writeheader()
            for precio in self.__precios.leer_todos():
                escritor.writerow(
                    {
                        "isbn": precio.libro.isbn,
                        "titulo": precio.libro.titulo,
                        "autor": precio.libro.autor,
                        "moneda": precio.moneda.codigo,
                        "importe": f"{precio.importe:.2f}",
                    }
                )
        return ruta

    def __moneda_por_codigo(self, codigo: str) -> Moneda:
        buscado = codigo.strip().upper()
        for moneda in self.__monedas.leer_todos():
            if moneda.codigo == buscado:
                return moneda
        raise ValueError(f"No está cargada la moneda {codigo}.")

    def __importe(self, libro_id: int, moneda_id: int) -> Optional[float]:
        for precio in self.__precios.leer_todos():
            if precio.libro.id == libro_id and precio.moneda.id == moneda_id:
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
    cotizaciones: ServicioCotizacionDolar
    reportes: ReporteServicio
