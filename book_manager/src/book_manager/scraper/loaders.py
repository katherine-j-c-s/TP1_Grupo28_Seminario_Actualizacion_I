"""Loaders del scraper de Cúspide."""

import re
from typing import Optional

from itemloaders import ItemLoader
from itemloaders.processors import MapCompose
from itemloaders.processors import TakeFirst

from book_manager.scraper.items import LibroWebItem

_METODOS = (
    "Transferencia",
    "Visa",
    "Mastercard",
    "American Express",
    "MercadoPago",
    "Mobbex",
    "RapiPago",
    "Pago Fácil",
)


def limpiar_precio(valor: object) -> Optional[float]:
    """Pasa un precio argentino ('38.999,00') a float.

    Args:
        valor (object): Texto o número leído de la página.

    Returns:
        Optional[float]: Precio, o None si no se pudo leer.
    """
    if valor is None:
        return None
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return float(valor)
    texto = str(valor).replace("\xa0", "").replace("$", "").strip()
    if texto == "":
        return None
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    coincidencia = re.search(r"\d+(?:\.\d+)?", texto)
    if coincidencia is None:
        return None
    return float(coincidencia.group(0))


def _comprimir(texto: str) -> str:
    return " ".join(texto.split())


def formas_de_pago(html: str, precio: Optional[float]) -> str:
    """Arma 'medio: precio' con los medios publicados en la ficha.

    Args:
        html (str): HTML de la ficha.
        precio (Optional[float]): Precio de contado de esa ficha.

    Returns:
        str: Medios separados por ' | '.
    """
    bajo = html.lower()
    precio_txt = f"{precio:.2f}" if precio is not None else "s/p"
    partes = [
        f"{nombre}: {precio_txt}"
        for nombre in _METODOS
        if nombre.lower() in bajo
    ]
    dolar = re.search(r"U\$s\s*(?:<span[^>]*>)?\s*([0-9.,]+)", html, re.I)
    if dolar is not None:
        valor = limpiar_precio(dolar.group(1))
        if valor is not None:
            partes.append(f"Precio en dólares: {valor:.2f}")
    return " | ".join(partes)


class LibroCuspideLoader(ItemLoader):
    """Toma los campos de la ficha y se queda con el primer valor útil."""

    default_item_class = LibroWebItem
    default_output_processor = TakeFirst()
    titulo_web_in = MapCompose(str.strip)
    descripcion_in = MapCompose(_comprimir)
    url_imagen_in = MapCompose(str.strip)
    precio_web_in = MapCompose(limpiar_precio)
    formas_pago_in = MapCompose(str.strip)
