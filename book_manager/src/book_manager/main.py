"""Punto de entrada de Book Manager."""

from pathlib import Path

from sqlalchemy import text

import book_manager.models.models  # registra las tablas en Base
from book_manager.database.connection import Base
from book_manager.database.connection import ConexionDB
from book_manager.migrations.migrations import migrar_datos
from book_manager.repositories.repositories import RepositorioAuditoria
from book_manager.repositories.repositories import RepositorioCotizacionDolar
from book_manager.repositories.repositories import RepositorioEditorial
from book_manager.repositories.repositories import RepositorioExtraccionWeb
from book_manager.repositories.repositories import RepositorioGenero
from book_manager.repositories.repositories import RepositorioLibro
from book_manager.repositories.repositories import RepositorioMoneda
from book_manager.repositories.repositories import RepositorioPrecio
from book_manager.repositories.repositories import RepositorioStock
from book_manager.repositories.repositories import RepositorioTipoCotizacion
from book_manager.services.services import Contexto
from book_manager.services.services import EditorialServicio
from book_manager.services.services import GeneroServicio
from book_manager.services.services import LibroServicio
from book_manager.services.services import MonedaServicio
from book_manager.services.services import PrecioServicio
from book_manager.services.services import ReporteServicio
from book_manager.services.services import ServicioAuditoria
from book_manager.services.services import ServicioCotizacionDolar
from book_manager.services.services import ServicioScraping
from book_manager.services.services import StockServicio
from book_manager.services.services import TipoCotizacionServicio
from book_manager.services.services import cargar_env
from book_manager.ui.console import Consola
from book_manager.ui.console import ejecutar_demostracion


def _base_vacia(db: ConexionDB) -> bool:
    """Indica si todavía no hay libros persistidos."""
    with db.engine.connect() as conexion:
        tablas = conexion.execute(
            text("SELECT name FROM sqlite_master WHERE type = 'table'")
        ).scalars()
        if "libros" not in set(tablas):
            return True
        cantidad = conexion.execute(text("SELECT COUNT(*) FROM libros")).scalar()
    return not cantidad


def preparar_base(importar_semillas: bool) -> ConexionDB:
    """Crea las tablas y, si hace falta, migra los CSV del Sprint 1.

    Args:
        importar_semillas (bool): Si es True, vacía la base y vuelve a migrar.

    Returns:
        ConexionDB: Conexión lista para los repositorios.
    """
    db = ConexionDB()
    if importar_semillas or _base_vacia(db):
        Base.metadata.drop_all(bind=db.engine)
        db.crear_tablas()
        paquete = Path(__file__).resolve().parent
        migrar_datos(
            str(paquete / "migrations" / "csv"),
            str(paquete / "migrations" / "sql"),
            db=db,
        )
        return db
    db.crear_tablas()
    return db


def construir_contexto(db: ConexionDB) -> Contexto:
    """Arma repositorios y servicios sobre la conexión indicada.

    Args:
        db (ConexionDB): Conexión compartida por todos los repositorios.

    Returns:
        Contexto: Servicios listos para la consola o la demostración.
    """
    generos = RepositorioGenero(db)
    editoriales = RepositorioEditorial(db)
    monedas = RepositorioMoneda(db)
    tipos = RepositorioTipoCotizacion(db)
    libros = RepositorioLibro(db)
    precios = RepositorioPrecio(db)
    stocks = RepositorioStock(db)
    cotizaciones = RepositorioCotizacionDolar(db)
    extracciones = RepositorioExtraccionWeb(db)
    auditorias = RepositorioAuditoria(db)
    return Contexto(
        generos=GeneroServicio(generos, libros),
        editoriales=EditorialServicio(editoriales, libros),
        monedas=MonedaServicio(monedas, precios),
        tipos_cotizacion=TipoCotizacionServicio(tipos, cotizaciones),
        libros=LibroServicio(libros, generos, editoriales, precios, stocks),
        precios=PrecioServicio(precios, libros, monedas),
        stocks=StockServicio(stocks, libros),
        cotizaciones=ServicioCotizacionDolar(cotizaciones, tipos),
        reportes=ReporteServicio(
            libros,
            precios,
            monedas,
            stocks,
            cotizaciones,
            tipos,
        ),
        scraping=ServicioScraping(extracciones, libros, precios),
        auditoria=ServicioAuditoria(auditorias),
    )


def main(import_default_data: bool = False, interactivo: bool = False) -> None:
    """Inicia el sistema sobre la base relacional.

    Con interactivo en False ejecuta el listado y el alta o la modificación
    de cada modelo, los reportes, la API, la lista bimonetaria y la exportación
    a CSV, y termina. Así el notebook puede continuar con las celdas de git.
    Con interactivo en True abre la consola.

    Args:
        import_default_data (bool): Si es True, vacía la base y migra los CSV.
        interactivo (bool): Si es True, abre el menú de consola.
    """
    cargar_env()
    db = preparar_base(importar_semillas=import_default_data)
    contexto = construir_contexto(db)
    if interactivo:
        Consola(contexto).ejecutar()
        return
    ejecutar_demostracion(contexto)


if __name__ == "__main__":
    main(import_default_data=False, interactivo=True)
