# Book Manager — Sprint 2

## Objetivo

Migrar la persistencia del Sprint 1 a una base relacional con SQLAlchemy, conservar las relaciones de la programación orientada a objetos como objetos (un libro conoce su género y su editorial) y sumar la cotización del dólar en vivo, la lista de precios bimonetaria y la exportación a CSV.

## Contexto

Book Manager es el trabajo práctico del Grupo 28 de Seminario de Actualización I: Joaquín Betes, Katherine Contreras, Silvina Moyano, Mateo Maibach y Emilce Robles. El catálogo de referencia es [Cúspide](https://cuspide.com/). El Sprint 1 dejó las entidades, los CSV semilla y la consola. Este sprint parte de la rama `Sprint_1`, crea la rama `Sprint_2` y reemplaza los archivos CSV de trabajo por SQLite (`book_manager/book_manager.db`).

Los CSV de `src/book_manager/migrations/csv` siguen siendo la semilla. `migrar_datos` los lee, genera los `INSERT` en `src/book_manager/migrations/sql` y carga las tablas. La URL de la API del dólar está en `.env`:

```
API_URL=https://dolarapi.com/v1/dolares
```

Los ISBN `978-950-28-0001-1` a `978-950-28-0012-1` son códigos internos del inventario de práctica, no ISBN oficiales verificados. El costo en dólares es una estimación de reposición (pesos publicados divididos por 1800) para comparar contra la cotización. La serie publicada de práctica usa el 29 de septiembre y los tipos Futuro, Ahorro y Minorista; el sistema también carga Oficial, Blue, MEP, CCL, Mayorista, Tarjeta y Cripto, que son las casas que devuelve la API.

## Cómo ejecutarlo

```bash
pip install -r book_manager/requirements.txt
cd book_manager
python -m book_manager.main
```

Hay que definir `PYTHONPATH` en `book_manager/src`. Sin argumentos, `main` abre la consola. Desde el notebook se llama `main(import_default_data=False)` para la demostración no interactiva, o `main(import_default_data=False, interactivo=True)` para el menú.

## Estructura

```
book_manager/
  .env
  CHANGELOG.md
  README.md
  requirements.txt
  src/book_manager/
    database/connection.py
    entities/entities.py
    models/models.py
    preload_data/preload_data.py
    repositories/repositories.py
    services/services.py
    migrations/csv/
    migrations/sql/
    ui/console.py
    main.py
```
