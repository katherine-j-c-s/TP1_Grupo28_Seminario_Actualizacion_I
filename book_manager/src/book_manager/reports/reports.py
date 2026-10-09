from typing import List, Dict, Any
from sqlalchemy import func
from book_manager.database.connection import ConexionDB
from book_manager.models.models import (
    LibroModel, GeneroModel, StockLibroModel, PrecioLibroModel, MonedaModel
)

class ReportesService:
    """Servicio encargado de generar reportes y consultas complejas."""

    def __init__(self, db: ConexionDB):
        self.db = db

    def obtener_stock_por_genero(self) -> List[Dict[str, Any]]:
        """Calcula el stock total agrupado por género."""
        with self.db.transaccion() as session:
            resultados = (
                session.query(
                    GeneroModel.nombre.label("genero"),
                    func.coalesce(func.sum(StockLibroModel.cantidad), 0).label("total_stock")
                )
                .join(LibroModel, GeneroModel.id == LibroModel.genero_id)
                .join(StockLibroModel, LibroModel.id == StockLibroModel.libro_id)
                .group_by(GeneroModel.nombre)
                .all()
            )
            return [{"genero": row.genero, "total_stock": row.total_stock} for row in resultados]

    def obtener_valorizacion_catalogo(self) -> List[Dict[str, Any]]:
        """Obtiene el listado de libros con sus precios por moneda y stock disponible."""
        with self.db.transaccion() as session:
            resultados = (
                session.query(
                    LibroModel.titulo,
                    LibroModel.isbn,
                    PrecioLibroModel.precio,
                    MonedaModel.codigo.label("moneda"),
                    func.coalesce(StockLibroModel.cantidad, 0).label("stock")
                )
                .join(PrecioLibroModel, LibroModel.id == PrecioLibroModel.libro_id)
                .join(MonedaModel, PrecioLibroModel.moneda_id == MonedaModel.id)
                .outerjoin(StockLibroModel, LibroModel.id == StockLibroModel.libro_id)
                .all()
            )
            return [
                {
                    "titulo": r.titulo,
                    "isbn": r.isbn,
                    "precio": r.precio,
                    "moneda": r.moneda,
                    "stock": r.stock
                }
                for r in resultados
            ]
