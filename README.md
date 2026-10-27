# Book Manager — Grupo 28

Trabajo práctico de Seminario de Actualización I. El catálogo de referencia es [Cúspide](https://cuspide.com/).

Grupo 28: Joaquín Betes, Katherine Contreras, Silvina Moyano, Mateo Maibach y Emilce Robles.

Repositorio: https://github.com/katherine-j-c-s/TP1_Grupo28_Seminario_Actualizacion_I.git

El código de la aplicación está en `book_manager/`. El detalle de cómo ejecutarlo está en [book_manager/README.md](book_manager/README.md).

## TP1 — Sprint 1

Notebook: `01_Book_Manager_Grupo_28.ipynb`  
Rama: `Sprint_1`

Consola para el inventario de la librería. Las entidades quedan encapsuladas, el CRUD se persiste en CSV y los servicios concentran las reglas. Los reportes comparan los precios públicos de Cúspide con el costo de reposición según la cotización del dólar.

## TP2 — Sprint 2

Notebook: `02_Book_Manager_Grupo_28.ipynb`  
Rama: `Sprint_2`, creada a partir de `Sprint_1`

La persistencia pasa de CSV a SQLite con SQLAlchemy. Las relaciones siguen siendo objetos: un libro conoce su género y su editorial. Se migran los CSV a scripts SQL, se registran las cotizaciones del dólar desde la API, se muestra la lista de precios en pesos y en otra moneda, y se exportan todos los precios a CSV.

La URL de la API está en `book_manager/.env`:

```
API_URL=https://dolarapi.com/v1/dolares
```

## TP3 — Sprint 3

Notebook: `03_Book_Manager_Grupo_28.ipynb`  
Rama: `Sprint_3`, creada a partir de `Sprint_2`

Se cargan los datos desde los scripts SQL. `CuspideSpider` busca solo los títulos del catálogo, toma los 10 primeros resultados y, con loaders y pipelines, guarda el precio, la imagen, las formas de pago y la descripción. Antes de cada scraping el menú pide la diferencia de precios y genera un CSV de alertas. El reporte Excel compara el precio interno con el de la web. Un decorador deja cada operación en la tabla de auditoría.

## Cómo se entregan los trabajos

- Los trabajos se entregan por el aula siempre y cuando se encuentren dentro del tiempo estipulado.
  - Se debe entregar un archivo con formato `.ipynb`. Para esto, voy al menú de Colab, a la sección **Archivo -> Descargar -> Descargar .ipynb**.
  - El archivo se adjunta al trabajo correspondiente.
- Los trabajos que se entregan fuera de tiempo deben enviarse como adjunto al correo de la cátedra: [lcd-sa182@ugr.edu.ar](mailto:lcd-sa182@ugr.edu.ar), los cuales serán tomados como nota de concepto.
- No se realizarán correcciones de enlaces a archivos/notebooks.
