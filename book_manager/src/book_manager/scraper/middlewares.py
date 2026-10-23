"""Middlewares del scraper de Cúspide.

El User-Agent y el respeto de robots.txt se definen en settings.py.
Estas clases quedan en el paquete, que es la estructura de un proyecto
Scrapy, y no se activan para no alterar los pedidos.
"""

from scrapy import Spider
from scrapy.http import Request
from scrapy.http import Response


class CuspideDownloaderMiddleware:
    """Punto de extensión entre el motor y el descargador."""

    def process_request(self, request: Request, spider: Spider) -> None:
        """Deja pasar el pedido.

        Args:
            request (Request): Pedido saliente.
            spider (Spider): Spider que lo originó.

        Returns:
            None: Scrapy continúa con la descarga.
        """
        return None

    def process_response(
        self,
        request: Request,
        response: Response,
        spider: Spider,
    ) -> Response:
        """Devuelve la respuesta sin filtrarla.

        Args:
            request (Request): Pedido original.
            response (Response): Respuesta descargada.
            spider (Spider): Spider que la va a procesar.

        Returns:
            Response: La misma respuesta.
        """
        return response
