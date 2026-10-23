"""Items que produce CuspideSpider."""

import scrapy


class LibroWebItem(scrapy.Item):
    """Ficha obtenida de Cúspide para un libro del catálogo."""

    libro_id = scrapy.Field()
    titulo_buscado = scrapy.Field()
    titulo_web = scrapy.Field()
    precio_web = scrapy.Field()
    url_imagen = scrapy.Field()
    formas_pago = scrapy.Field()
    descripcion = scrapy.Field()
    url_producto = scrapy.Field()
    coincide = scrapy.Field()
