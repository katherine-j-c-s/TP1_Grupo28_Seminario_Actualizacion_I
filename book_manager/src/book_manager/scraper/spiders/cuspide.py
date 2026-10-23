"""Spider que busca en Cúspide solo los libros del catálogo."""

from urllib.parse import quote_plus

import scrapy

from book_manager.database.connection import ConexionDB
from book_manager.repositories.repositories import RepositorioLibro
from book_manager.scraper.items import LibroWebItem
from book_manager.scraper.loaders import LibroCuspideLoader
from book_manager.scraper.loaders import formas_de_pago
from book_manager.scraper.loaders import limpiar_precio


class CuspideSpider(scrapy.Spider):
    """Busca cada título del catálogo y toma los 10 primeros resultados."""

    name = "cuspide"
    allowed_domains = ["cuspide.com"]

    def __init__(self, limite: int = 0, *args, **kwargs) -> None:
        """Arma la lista de títulos desde la base.

        Args:
            limite (int): Si es mayor a cero, busca solo esa cantidad de libros.
        """
        super().__init__(*args, **kwargs)
        self.limite = int(limite or 0)
        self.libros = self._libros_del_catalogo()

    async def start(self):
        """Entrega las búsquedas iniciales. Scrapy 2.13+ llama a este método."""
        for pedido in self.start_requests():
            yield pedido

    def start_requests(self):
        """Una búsqueda por cada título del catálogo."""
        for libro in self.libros:
            consulta = quote_plus(libro["titulo"])
            url = f"https://cuspide.com/?s={consulta}&post_type=product"
            yield scrapy.Request(
                url,
                callback=self.parse_busqueda,
                cb_kwargs={
                    "libro_id": libro["id"],
                    "titulo_buscado": libro["titulo"],
                },
            )

    def parse_busqueda(self, response, libro_id: int, titulo_buscado: str):
        """Sigue los 10 primeros productos de la búsqueda."""
        vistos = []
        for href in response.css("div.product-small a::attr(href)").getall():
            if "/producto/" not in href:
                continue
            absoluto = response.urljoin(href.split("?")[0])
            if absoluto in vistos:
                continue
            vistos.append(absoluto)
            if len(vistos) == 10:
                break
        for url in vistos:
            yield response.follow(
                url,
                callback=self.parse_producto,
                cb_kwargs={
                    "libro_id": libro_id,
                    "titulo_buscado": titulo_buscado,
                },
            )

    def parse_producto(self, response, libro_id: int, titulo_buscado: str):
        """Extrae precio, imagen, formas de pago y descripción."""
        precio_txt = response.css(
            ".product-page-price .woocommerce-Price-amount bdi::text"
        ).get()
        precio = limpiar_precio(precio_txt)
        loader = LibroCuspideLoader(item=LibroWebItem(), selector=response.selector)
        loader.add_value("libro_id", libro_id)
        loader.add_value("titulo_buscado", titulo_buscado)
        loader.add_css("titulo_web", "h1.product-title::text")
        loader.add_css("titulo_web", "h1.entry-title::text")
        loader.add_css("titulo_web", "h1::text")
        loader.add_value("precio_web", precio)
        loader.add_css(
            "url_imagen",
            ".woocommerce-product-gallery__image a::attr(href)",
        )
        loader.add_css("descripcion", "p.livriz-text-synopsis::text")
        loader.add_value("url_producto", response.url)
        loader.add_value("formas_pago", formas_de_pago(response.text, precio))
        item = loader.load_item()
        item["coincide"] = _mismo_titulo(
            titulo_buscado,
            str(item.get("titulo_web") or ""),
        )
        yield item

    def _libros_del_catalogo(self) -> list:
        """Lee los títulos desde SQL. No busca libros fuera del catálogo."""
        import book_manager.models.models  # registra las tablas

        db = ConexionDB()
        db.crear_tablas()
        libros = RepositorioLibro(db).leer_todos()
        if self.limite > 0:
            libros = libros[: self.limite]
        return [{"id": libro.id, "titulo": libro.titulo} for libro in libros]


def _mismo_titulo(buscado: str, publicado: str) -> bool:
    """Compara títulos sin distinguir mayúsculas."""
    izquierdo = " ".join(buscado.split()).casefold()
    derecho = " ".join(publicado.split()).casefold()
    if izquierdo == "" or derecho == "":
        return False
    return izquierdo == derecho or izquierdo in derecho or derecho in izquierdo
