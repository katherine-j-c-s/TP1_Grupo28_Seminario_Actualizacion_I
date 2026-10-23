"""Pipelines del scraper de Cúspide."""

from datetime import datetime

from itemadapter import ItemAdapter
from scrapy import Item
from scrapy import Spider
from scrapy.exceptions import DropItem

from book_manager.database.connection import ConexionDB
from book_manager.scraper.loaders import limpiar_precio


class LimpiezaPipeline:
    """Descarta fichas vacías y normaliza el precio y la descripción."""

    def process_item(self, item: Item, spider: Spider) -> Item:
        """Limpia un item antes de guardarlo.

        Args:
            item (Item): Item producido por el loader.
            spider (Spider): Spider que lo generó.

        Returns:
            Item: Item limpio.

        Raises:
            DropItem: Si no hay título ni precio.
        """
        datos = ItemAdapter(item)
        titulo = (datos.get("titulo_web") or "").strip()
        precio = datos.get("precio_web")
        if isinstance(precio, str):
            precio = limpiar_precio(precio)
            datos["precio_web"] = precio
        if titulo == "" and precio is None:
            raise DropItem("Resultado sin título ni precio.")
        datos["titulo_web"] = titulo or datos.get("titulo_buscado") or "Sin título"
        descripcion = datos.get("descripcion") or ""
        datos["descripcion"] = " ".join(str(descripcion).split())
        return item


class GuardarExtraccionPipeline:
    """Guarda cada ficha en la tabla extracciones_web."""

    def open_spider(self, spider: Spider) -> None:
        """Crea la tabla y vacía las extracciones de la corrida anterior.

        Args:
            spider (Spider): Spider que está por empezar.
        """
        import book_manager.models.models  # registra las tablas
        from book_manager.repositories.repositories import (
            RepositorioExtraccionWeb,
        )

        self._db = ConexionDB()
        self._db.crear_tablas()
        self._repositorio = RepositorioExtraccionWeb(self._db)
        self._repositorio.eliminar_todas()

    def process_item(self, item: Item, spider: Spider) -> Item:
        """Persiste el item.

        Args:
            item (Item): Item ya limpio.
            spider (Spider): Spider que lo generó.

        Returns:
            Item: El mismo item.
        """
        from book_manager.entities.entities import ExtraccionWeb

        datos = ItemAdapter(item)
        self._repositorio.crear(
            ExtraccionWeb(
                id=0,
                libro_id=int(datos["libro_id"]),
                titulo_buscado=str(datos.get("titulo_buscado") or ""),
                titulo_web=str(datos.get("titulo_web") or ""),
                precio_web=datos.get("precio_web"),
                url_imagen=str(datos.get("url_imagen") or ""),
                formas_pago=str(datos.get("formas_pago") or ""),
                descripcion=str(datos.get("descripcion") or ""),
                url_producto=str(datos.get("url_producto") or ""),
                fecha_extraccion=datetime.now(),
                coincide=bool(datos.get("coincide")),
            )
        )
        return item

    def close_spider(self, spider: Spider) -> None:
        """Cierra el motor cuando el spider termina.

        Args:
            spider (Spider): Spider que finalizó.
        """
        motor = getattr(self, "_db", None)
        if motor is not None:
            motor.engine.dispose()
