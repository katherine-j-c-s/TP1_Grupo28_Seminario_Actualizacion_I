"""Conexión a la base relacional de Book Manager."""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def _url_desde_env() -> str:
    """Lee DATABASE_URL del .env y resuelve la ruta de SQLite.

    Returns:
        str: URL de SQLAlchemy lista para create_engine.

    Raises:
        ConnectionError: Si el .env no define DATABASE_URL.
    """
    raiz = Path(__file__).resolve().parents[3]
    load_dotenv(raiz / ".env")
    url = os.getenv("DATABASE_URL", "").strip()
    if url == "":
        raise ConnectionError(
            "No se pudo conectar: falta DATABASE_URL en el archivo .env."
        )
    prefijo = "sqlite:///"
    if url.startswith(prefijo):
        ruta = url[len(prefijo):]
        if ruta != "" and not Path(ruta).is_absolute():
            absoluta = (raiz / ruta).resolve()
            url = prefijo + absoluta.as_posix()
    return url


class ConexionDB:
    """Maneja el motor, las sesiones y las transacciones de SQLAlchemy."""

    def __init__(self, db_url: Optional[str] = None) -> None:
        """Abre la conexión.

        Si no se pasa una URL, la lee de DATABASE_URL en el archivo .env.
        Ante una falla informa el problema con un mensaje y no deja
        propagar el error crudo del motor.

        Args:
            db_url (Optional[str]): URL de SQLAlchemy. None usa el .env.

        Raises:
            ConnectionError: Si falta la URL o la base no responde.
        """
        if db_url is None or db_url.strip() == "":
            db_url = _url_desde_env()
        try:
            self.engine = create_engine(db_url, echo=False)

            @event.listens_for(self.engine, "connect")
            def _activar_claves_foraneas(conexion, _registro) -> None:
                cursor = conexion.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

            with self.engine.connect() as conexion:
                conexion.execute(text("SELECT 1"))
        except (SQLAlchemyError, OSError, ValueError) as error:
            raise ConnectionError(
                "No se pudo conectar a la base de datos. "
                f"Revisá DATABASE_URL en el archivo .env. Detalle: {error}"
            ) from error
        self.SessionLocal = sessionmaker(
            autoflush=False,
            expire_on_commit=False,
            bind=self.engine,
        )

    def crear_tablas(self) -> None:
        """Crea las tablas definidas en los modelos que heredan de Base.

        El import de los modelos queda dentro del método para registrar
        las tablas en Base sin un ciclo al cargar este módulo.
        """
        from book_manager.models import models as _modelos  # noqa: F401

        Base.metadata.create_all(bind=self.engine)

    def obtener_sesion(self) -> Session:
        """Abre una sesión nueva.

        Returns:
            Session: Sesión lista para consultar la base.
        """
        return self.SessionLocal()

    @contextmanager
    def transaccion(self) -> Generator[Session, None, None]:
        """Abre una transacción con commit, rollback y cierre.

        Yields:
            Session: Sesión de la transacción.

        Raises:
            Exception: Relanza el error después de hacer rollback.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
