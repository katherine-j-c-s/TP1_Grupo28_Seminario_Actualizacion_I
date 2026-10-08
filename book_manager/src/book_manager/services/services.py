from typing import List, Optional
from book_manager.database.connection import ConexionDB
from book_manager.repository.repositories import LibroRepository, GeneroRepository, EditorialRepository
from book_manager.models.models import LibroModel, GeneroModel, EditorialModel

class LibroService:
    """Servicio para gestionar la lógica de negocio de libros."""

    def __init__(self, db: ConexionDB):
        self.db = db
        self.libro_repo = LibroRepository(db)
        self.genero_repo = GeneroRepository(db)
        self.editorial_repo = EditorialRepository(db)

    def listar_libros(self) -> List[LibroModel]:
        return self.libro_repo.obtener_todos()

    def buscar_libro_por_id(self, libro_id: int) -> Optional[LibroModel]:
        return self.libro_repo.obtener_por_id(libro_id)

    def registrar_libro(self, isbn: str, titulo: str, autor: str, editorial_id: int, genero_id: int, anio: int, paginas: int) -> LibroModel:
        nuevo_libro = LibroModel(
            isbn=isbn,
            titulo=titulo,
            autor=autor,
            editorial_id=editorial_id,
            genero_id=genero_id,
            anio=anio,
            paginas=paginas
        )
        return self.libro_repo.agregar(nuevo_libro)

    def eliminar_libro(self, libro_id: int) -> bool:
        return self.libro_repo.eliminar(libro_id)

class CatalogoService:
    """Servicio para consultas auxiliares del catálogo."""

    def __init__(self, db: ConexionDB):
        self.db = db
        self.genero_repo = GeneroRepository(db)
        self.editorial_repo = EditorialRepository(db)

    def listar_generos(self) -> List[GeneroModel]:
        return self.genero_repo.obtener_todos()

    def listar_editoriales(self) -> List[EditorialModel]:
        return self.editorial_repo.obtener_todos()

    def registrar_genero(self, nombre: str, descripcion: str = None) -> GeneroModel:
        """Crea un genero y devuelve el existente si el nombre ya estaba."""
        existente = self.genero_repo.buscar_por_nombre(nombre)
        if existente is not None:
            return existente
        return self.genero_repo.agregar(GeneroModel(nombre=nombre, descripcion=descripcion))

    def registrar_editorial(self, nombre: str) -> EditorialModel:
        """Crea una editorial y devuelve la existente si el nombre ya estaba."""
        existente = self.editorial_repo.buscar_por_nombre(nombre)
        if existente is not None:
            return existente
        return self.editorial_repo.agregar(EditorialModel(nombre=nombre))
