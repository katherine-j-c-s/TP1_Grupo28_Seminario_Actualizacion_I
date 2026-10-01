# Changelog

Los cambios se listan del más reciente al más antiguo. Cada ejercicio del práctico es un día de trabajo distinto.

## [Punto 07] — 2026-10-01

- Se creó `src/book_manager/main.py` como único punto de entrada del sistema.
- `construir_contexto` instancia los ocho repositorios CSV y los inyecta en los servicios, para que la consola no conozca los archivos.
- `main(import_default_data=False)` abre los CSV de trabajo ya existentes. Si la carpeta `data/` todavía no tiene archivos, copia una sola vez las semillas de `migrations/csv`.
- `main(import_default_data=True)` vuelve a copiar las semillas y descarta los cambios de la sesión anterior.
- Con `interactivo=False` corre la demostración y termina, así el notebook puede seguir con las celdas de git. La celda de entrega llama `main(import_default_data=False)`.
- La demostración, para cada modelo y en este orden, imprime el listado y después hace un alta o una modificación: Género "Teatro", Editorial "Cátedra", Moneda "XXX", Tipo de cotización "Prueba", Libro `978-950-28-0099-1`, su precio en pesos, su stock y la cotización oficial del 2026-10-02. La segunda ejecución modifica ese registro y no lo duplica.
- Después de los modelos muestra la comparación con Cúspide al dólar blue y al oficial, el stock a reponer y el histórico del dólar blue.
- `python -m book_manager.main` abre la consola interactiva.

## [Punto 06] — 2026-09-30

- Se creó `src/book_manager/ui/console.py`. Toda la entrada y la salida quedan en la consola; las reglas siguen en los servicios.
- El menú principal ofrece Géneros, Editoriales, Monedas, Tipos de cotización, Libros, Precios, Stock, Cotizaciones del dólar y Reportes.
- Los puntos 1 a 7 muestran una sola línea de acciones: `1. Listado  2. Alta  3. Modificación  4. Borrado  5. Lectura  0. Volver`.
- El punto 8 usa la misma línea y aclara la lectura: `5. Lectura por tipo y fecha`. No vuelve a listar las opciones debajo.
- El punto 9 lista cada acción en su propio renglón, con un número distinto: 1 comparación con Cúspide, 2 stock a reponer, 3 histórico, 4 listado, 5 alta, 6 modificación, 7 borrado y 8 lectura de informes guardados durante la sesión.
- Las opciones 1, 2 y 3 del punto 9 calculan el reporte en el momento. La opción 5 guarda una copia con título. La 4 lista esas copias, la 8 las lee, la 6 cambia el título y la 7 las borra.
- Los importes de los reportes se muestran con separador de miles y coma decimal.
- Un dato inválido muestra el mensaje de la regla y no corta el resto del programa.

## [Punto 05] — 2026-09-29

- Se creó `src/book_manager/preload_data/preload_data.py`, que copia los CSV de `migrations/csv` a `data/` sin modificar las semillas.
- Cada clase quedó con al menos diez registros: 12 géneros, 12 editoriales, 10 monedas, 10 tipos de cotización, 12 libros, 24 precios, 12 stocks y 16 cotizaciones.
- Los títulos, autores y precios en pesos salen del listado público de Cúspide del 2026-10-01. Por ejemplo, "El buen mal" de Samanta Schweblin a $ 38.999,00 y "La amiga estupenda" de Elena Ferrante a $ 50.999,00.
- Cada libro tiene además un costo en dólares para poder cotizar la reposición.
- Los códigos `978-950-28-0001-1` a `978-950-28-0012-7` son códigos internos de inventario. El año, las páginas y la editorial que no figuran en el listado público se cargaron como dato de catálogo.
- La cotización del 2026-09-30 y del 2026-10-01 del oficial, blue, MEP, CCL, mayorista, tarjeta y cripto sigue los valores publicados ese día. El 2026-09-29 y los tipos Futuro, Ahorro y Minorista completan la serie del histórico.
- El stock deja títulos por debajo del punto de reposición, entre ellos "Los días de la Constitución", "El día de la trilla" y "Mi nombre es Emilia del Valle".

## [Ejercicio 04] — 2026-09-28

- Se creó `src/book_manager/services/services.py` con un servicio por entidad: `GeneroServicio`, `EditorialServicio`, `MonedaServicio`, `TipoCotizacionServicio`, `LibroServicio`, `PrecioServicio`, `StockServicio` y `CotizacionDolarServicio`.
- Cada servicio expone crear, leer, actualizar y eliminar, y rechaza duplicados: nombre de género, editorial y tipo de cotización, código de moneda, ISBN, par libro-moneda, stock del mismo libro y cotización del mismo tipo y fecha.
- No se elimina un género, una editorial, una moneda, un tipo de cotización o un libro si otra entidad lo está usando.
- Un libro solo se guarda si el género y la editorial existen. Un precio exige libro y moneda existentes. El stock y la cotización exigen que existan el libro y el tipo.
- `ReporteServicio.comparar_con_cuspide` toma el precio en pesos publicado por Cúspide, multiplica el costo en dólares por la venta de la última cotización del tipo elegido y calcula la diferencia.
- `stock_a_reponer` devuelve los libros cuya cantidad está en el punto de reposición o por debajo.
- `historico` devuelve las cotizaciones de un tipo ordenadas por fecha.
- `Contexto` reúne los servicios para que la consola reciba un solo objeto.

## [Ejercicio 03] — 2026-09-27

- Se creó `src/book_manager/repositories/repositories.py` con las interfaces del enunciado: `IRepositorio`, `IRepositorioStock` e `IRepositorioCotizacionDolar`.
- `RepositorioCSV` implementa el alta, la lectura por id, la lectura de todos, la modificación y el borrado, y persiste cada cambio en el CSV.
- Hay un repositorio concreto por entidad: `RepositorioGenero`, `RepositorioEditorial`, `RepositorioMoneda`, `RepositorioTipoCotizacion`, `RepositorioLibro` y `RepositorioPrecio`.
- `RepositorioStock` usa el id del libro como clave. No permite dos stocks para el mismo título.
- `RepositorioCotizacionDolar` usa el par tipo y fecha como clave, lee una cotización puntual y devuelve el histórico ordenado por fecha.
- Si el id llega en 0, el repositorio asigna el siguiente. Leer devuelve una copia, así un cambio externo no se escribe hasta llamar a actualizar.
- Los CSV se leen y escriben en UTF-8, con encabezado.

## [Ejercicio 02] — 2026-09-26

- Se creó `src/book_manager/entities/entities.py`.
- `EntidadBase` encapsula el id. El valor 0 indica que el repositorio todavía no lo asignó.
- Quedaron definidas `Genero`, `Editorial`, `Moneda`, `TipoCotizacion`, `Libro`, `Precio`, `Stock` y `CotizacionDolar`.
- Cada atributo es privado y se expone con `@property`. El setter rechaza textos vacíos, ids inválidos, importes no positivos, años fuera de 1400 a 2100 y un código de moneda que no tenga tres letras.
- `Libro` se relaciona con editorial y género por id. `Precio` se relaciona con libro y moneda. `Stock` se relaciona con el libro. `CotizacionDolar` se relaciona con el tipo de cotización y una fecha.
- `Stock` no tiene un id propio: la clave es el libro, como pide la interfaz. `CotizacionDolar` se identifica por tipo y fecha.
- En la cotización, la compra no puede superar a la venta.

## [Ejercicio 01] — 2026-09-25

- Se armó la estructura del sprint dentro de `book_manager/`: `src/book_manager/entities`, `repositories`, `services`, `preload_data`, `ui`, `migrations/csv` y `main.py`.
- Se escribió `book_manager/README.md` con el objetivo, el contexto del Sprint 1, el grupo 28 y la forma de ejecutar el sistema.
- El grupo queda integrado por Joaquín Betes, Katherine Contreras, Silvina Moyano, Mateo Maibach y Emilce Robles.
- El repositorio de trabajo es `https://github.com/katherine-j-c-s/TP1_Grupo28_Seminario_Actualizacion_I.git`, sobre la rama `Sprint_1`.
- `requirements.txt` deja asentado que el sprint usa la biblioteca estándar de Python.
- `.gitignore` excluye la carpeta de trabajo `data/` y los `__pycache__`, para no versionar datos generados al ejecutar.
