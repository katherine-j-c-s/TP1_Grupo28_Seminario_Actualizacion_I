# Book Manager — Sprint 1

## Objetivo

Aplicar programación orientada a objetos y persistencia en archivos para gestionar el inventario de una librería: libros, precios en distintas monedas y cotización del dólar.

## Introducción y contexto

Una librería con venta al público necesita reemplazar el control manual del catálogo. Los costos de reposición siguen al dólar, y los precios de mostrador se comparan con los que publica [Cúspide](https://cuspide.com/).

Este sprint entrega una aplicación de consola. Las entidades encapsulan sus datos, cada una tiene alta, lectura, modificación y borrado, y los CSV guardan el estado entre ejecuciones. La lógica de negocio está en los servicios; la consola solo pide datos y muestra resultados.

El catálogo inicial toma títulos, autores y precios en pesos del listado público de Cúspide al 1 de octubre de 2026. El código de inventario no es un ISBN oficial verificado. El año y la cantidad de páginas son datos de referencia del inventario. La editorial se cargó como dato de catálogo cuando el listado público no la informa.

Las cotizaciones del 30 de septiembre y del 1 de octubre de 2026 de los dólares oficial, blue, MEP, CCL, mayorista, tarjeta y cripto siguen los valores publicados ese día (Banco Nación y prensa). El 29 de septiembre y los tipos Futuro, Ahorro y Minorista completan la serie de práctica del histórico.

## Grupo 28

- Joaquín Betes
- Katherine Contreras
- Silvina Moyano
- Mateo Maibach
- Emilce Robles

Repositorio: https://github.com/katherine-j-c-s/TP1_Grupo28_Seminario_Actualizacion_I.git

## Cómo ejecutarlo

Desde `book_manager/src`:

```bash
python -m book_manager.main
```

Eso abre la consola. La celda del notebook llama `main(import_default_data=False)`, que lista cada modelo, hace un alta o una modificación y muestra los reportes, sin pedir datos por teclado.

`import_default_data=True` vuelve a copiar los CSV de `migrations/csv` sobre la carpeta de trabajo `data/`.

## Reportes

- Comparación del precio publicado en Cúspide contra el costo en dólares pasado a pesos con la última cotización del tipo elegido.
- Libros con stock en el punto de reposición o por debajo.
- Histórico de cotizaciones por tipo de dólar.
