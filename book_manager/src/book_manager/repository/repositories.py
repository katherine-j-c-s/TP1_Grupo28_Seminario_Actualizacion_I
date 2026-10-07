from typing import List, Optional
from book_manager.database.connection import ConexionDB
from book_manager.models.models import (
    LibroModel, GeneroModel, EditorialModel
)

class LibroRepository:
    """Repositorio para gestionar la entidad Libro en la base de datos relacional."""

    def __init__(self, db: ConexionDB):
        self.db = db

    def obtener_todos(self) -> List[LibroModel]:
        with self.db.transaccion() as session:
            return session.query(LibroModel).all()

    def obtener_por_id(self, libro_id: int) -> Optional[LibroModel]:
        with self.db.transaccion() as session:
            return session.query(LibroModel).filter(LibroModel.id == libro_id).first()

    def agregar(self, libro: LibroModel) -> LibroModel:
        with self.db.transaccion() as session:
            session.add(libro)
            session.flush()
            session.refresh(libro)
            return libro

    def actualizar(self, libro: LibroModel) -> LibroModel:
        with self.db.transaccion() as session:
            session.merge(libro)
            return libro

    def eliminar(self, libro_id: int) -> bool:
        with self.db.transaccion() as session:
            libro = session.query(LibroModel).filter(LibroModel.id == libro_id).first()
            if libro:
                session.delete(libro)
                return True
            return False

class GeneroRepository:
    """Repositorio para la entidad Género."""

    def __init__(self, db: ConexionDB):
        self.db = db

    def obtener_todos(self) -> List[GeneroModel]:
        with self.db.transaccion() as session:
            return session.query(GeneroModel).all()

    def obtener_por_id(self, genero_id: int) -> Optional[GeneroModel]:
        with self.db.transaccion() as session:
            return session.query(GeneroModel).filter(GeneroModel.id == genero_id).first()

    def agregar(self, genero: GeneroModel) -> GeneroModel:
        with self.db.transaccion() as session:
            session.add(genero)
            session.flush()
            session.refresh(genero)
            return genero

    def buscar_por_nombre(self, nombre: str) -> Optional[GeneroModel]:
        with self.db.transaccion() as session:
            return session.query(GeneroModel).filter(
                GeneroModel.nombre == nombre
            ).first()

class EditorialRepository:
    """Repositorio para la entidad Editorial."""

    def __init__(self, db: ConexionDB):
        self.db = db

    def obtener_todos(self) -> List[EditorialModel]:
        with self.db.transaccion() as session:
            return session.query(EditorialModel).all()

    def obtener_por_id(self, editorial_id: int) -> Optional[EditorialModel]:
        with self.db.transaccion() as session:
            return session.query(EditorialModel).filter(EditorialModel.id == editorial_id).first()

    def agregar(self, editorial: EditorialModel) -> EditorialModel:
        with self.db.transaccion() as session:
            session.add(editorial)
            session.flush()
            session.refresh(editorial)
            return editorial

    def buscar_por_nombre(self, nombre: str) -> Optional[EditorialModel]:
        with self.db.transaccion() as session:
            return session.query(EditorialModel).filter(
                EditorialModel.nombre == nombre
            ).first()
