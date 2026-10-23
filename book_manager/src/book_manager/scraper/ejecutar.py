"""Corre CuspideSpider en un proceso propio.

Scrapy usa un reactor que no se puede reiniciar en el mismo proceso.
Por eso el menú y la demostración lo lanzan como módulo.
"""

import sys

from scrapy.crawler import CrawlerProcess

from book_manager.scraper.settings import AJUSTES
from book_manager.scraper.spiders.cuspide import CuspideSpider


def correr(limite: int = 0) -> None:
    """Ejecuta el spider.

    Args:
        limite (int): Cantidad máxima de títulos. Cero recorre el catálogo.
    """
    proceso = CrawlerProcess(AJUSTES)
    proceso.crawl(CuspideSpider, limite=int(limite or 0))
    proceso.start()


if __name__ == "__main__":
    cantidad = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    correr(cantidad)
