"""Punto de entrada de Book Manager."""

from pathlib import Path

from book_manager.preload_data.preload_data import preparar_datos
from book_manager.repositories.repositories import RepositorioCotizacionDolar
from book_manager.repositories.repositories import RepositorioEditorial
from book_manager.repositories.repositories import RepositorioGenero
from book_manager.repositories.repositories import RepositorioLibro
from book_manager.repositories.repositories import RepositorioMoneda
from book_manager.repositories.repositories import RepositorioPrecio
from book_manager.repositories.repositories import RepositorioStock
from book_manager.repositories.repositories import RepositorioTipoCotizacion
from book_manager.services.services import Contexto
from book_manager.services.services import CotizacionDolarServicio
from book_manager.services.services import EditorialServicio
from book_manager.services.services import GeneroServicio
from book_manager.services.services import LibroServicio
from book_manager.services.services import MonedaServicio
from book_manager.services.services import PrecioServicio
from book_manager.services.services import ReporteServicio
from book_manager.services.services import StockServicio
from book_manager.services.services import TipoCotizacionServicio
from book_manager.ui.console import Consola
from book_manager.ui.console import ejecutar_demostracion


def construir_contexto(directorio: Path) -> Contexto:
    """Arma repositorios y servicios a partir de la carpeta de CSV.

    Args:
        directorio (Path): Carpeta con los CSV de trabajo.

    Returns:
        Contexto: Servicios listos para la consola o la demostración.
    """
    generos = RepositorioGenero(directorio)
    editoriales = RepositorioEditorial(directorio)
    monedas = RepositorioMoneda(directorio)
    tipos = RepositorioTipoCotizacion(directorio)
    libros = RepositorioLibro(directorio)
    precios = RepositorioPrecio(directorio)
    stocks = RepositorioStock(directorio)
    cotizaciones = RepositorioCotizacionDolar(directorio)
    return Contexto(
        generos=GeneroServicio(generos, libros),
        editoriales=EditorialServicio(editoriales, libros),
        monedas=MonedaServicio(monedas, precios),
        tipos_cotizacion=TipoCotizacionServicio(tipos, cotizaciones),
        libros=LibroServicio(libros, generos, editoriales, precios, stocks),
        precios=PrecioServicio(precios, libros, monedas),
        stocks=StockServicio(stocks, libros),
        cotizaciones=CotizacionDolarServicio(cotizaciones, tipos),
        reportes=ReporteServicio(
            libros,
            precios,
            monedas,
            stocks,
            cotizaciones,
            tipos,
        ),
    )


def main(import_default_data: bool = False, interactivo: bool = False) -> None:
    """Inicia el sistema.

    Con interactivo en False ejecuta el listado y el alta o la modificación
    de cada modelo, más los reportes, y termina. Así el notebook puede
    continuar con las celdas de git. Con interactivo en True abre la consola.

    Args:
        import_default_data (bool): Si es True, repone los CSV semilla.
        interactivo (bool): Si es True, abre el menú de consola.
    """
    directorio = preparar_datos(importar_semillas=import_default_data)
    contexto = construir_contexto(directorio)
    if interactivo:
        Consola(contexto).ejecutar()
        return
    ejecutar_demostracion(contexto)


if __name__ == "__main__":
    main(import_default_data=False, interactivo=True)
