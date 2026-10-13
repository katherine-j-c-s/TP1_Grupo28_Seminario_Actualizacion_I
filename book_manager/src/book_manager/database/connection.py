import os
from contextlib import contextmanager
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class ConexionDB:
    """Clase encargada de manejar la conexión a la base de datos relacional con SQLAlchemy."""

    def __init__(self, db_url: Optional[str] = None) -> None:
        if not db_url:
            db_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__), "..", "..", "..", "book_manager.db"
                )
            )
            db_url = f"sqlite:///{db_path}"

        self.engine = create_engine(db_url, echo=False)

        @event.listens_for(self.engine, "connect")
        def _activar_claves_foraneas(conexion, _registro) -> None:
            cursor = conexion.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        self.SessionLocal = sessionmaker(
            autoflush=False, expire_on_commit=False, bind=self.engine
        )

    def crear_tablas(self):
        """Crea todas las tablas definidas en los modelos que heredan de Base."""
        from book_manager.models import models  # noqa: F401

        Base.metadata.create_all(bind=self.engine)

    def obtener_sesion(self):
        """Retorna una nueva sesión de la base de datos."""
        return self.SessionLocal()

    @contextmanager
    def transaccion(self):
        """Context Manager para gestionar transacciones con commit y rollback automático."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
