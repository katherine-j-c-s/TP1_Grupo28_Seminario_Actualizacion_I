"""Copia los CSV de migración al directorio de trabajo."""

import shutil
from pathlib import Path


def ruta_paquete() -> Path:
    """Devuelve el directorio del paquete book_manager."""
    return Path(__file__).resolve().parent.parent


def ruta_migraciones() -> Path:
    """Devuelve la carpeta de CSV semilla."""
    return ruta_paquete() / "migrations" / "csv"


def ruta_datos() -> Path:
    """Devuelve la carpeta de CSV de trabajo."""
    return ruta_paquete() / "data"


def preparar_datos(importar_semillas: bool) -> Path:
    """Prepara el directorio desde el que leen los repositorios.

    Si importar_semillas es verdadero, vuelve a copiar los CSV de
    migración. Si es falso y todavía no hay datos de trabajo, los
    copia una sola vez para que la primera ejecución tenga catálogo.

    Args:
        importar_semillas (bool): Indica si se repone el catálogo inicial.

    Returns:
        Path: Directorio de trabajo.

    Raises:
        FileNotFoundError: Si faltan los CSV de migración.
    """
    origen = ruta_migraciones()
    destino = ruta_datos()
    if not origen.exists():
        raise FileNotFoundError(
            f"No se encuentra la carpeta de migraciones: {origen}"
        )
    semillas = sorted(origen.glob("*.csv"))
    if not semillas:
        raise FileNotFoundError("No hay archivos CSV en migrations/csv.")
    destino.mkdir(parents=True, exist_ok=True)
    hay_datos = any(destino.glob("*.csv"))
    if importar_semillas or not hay_datos:
        for semilla in semillas:
            shutil.copy2(semilla, destino / semilla.name)
    return destino
