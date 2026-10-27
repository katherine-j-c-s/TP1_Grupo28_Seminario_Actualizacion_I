"""Ajustes de Scrapy para el scraper de Cúspide."""

AJUSTES = {
    "BOT_NAME": "cuspide",
    "ROBOTSTXT_OBEY": True,
    "USER_AGENT": "BookManager/1.0 (Grupo 28; educational)",
    "DOWNLOAD_DELAY": 0.3,
    "CONCURRENT_REQUESTS": 4,
    "TELNETCONSOLE_ENABLED": False,
    "LOG_LEVEL": "INFO",
    "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
    "ITEM_PIPELINES": {
        "book_manager.scraper.pipelines.LimpiezaPipeline": 100,
        "book_manager.scraper.pipelines.GuardarExtraccionPipeline": 300,
    },
}
