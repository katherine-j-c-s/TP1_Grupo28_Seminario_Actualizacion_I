import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class ConexionDB:
    """Clase encargada de manejar la conexión a la base de datos relacional con SQLAlchemy."""

    def __init__(self, db_url: str = None):
        if not db_url:
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "book_manager.db"))
            db_url = f"sqlite:///{db_path}"

        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(
            autoflush=False, expire_on_commit=False, bind=self.engine
        )

    def crear_tablas(self):
        """Crea todas las tablas definidas en los modelos que heredan de Base."""
        Base.metadata.create_all(bind=self.engine)

    def obtener_sesion(self):
        """Retorna una nueva sesión de la base de datos."""
        return self.SessionLocal()
