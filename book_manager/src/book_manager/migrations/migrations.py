import csv
from pathlib import Path
from sqlalchemy import text
from book_manager.database.connection import ConexionDB, Base

COLUMNAS_ENTERAS = {
    "id", "editorial_id", "genero_id", "anio", "paginas", "libro_id",
    "moneda_id", "cantidad", "tipo_cotizacion_id", "punto_reposicion",
}
COLUMNAS_DECIMALES = {"precio", "compra", "venta"}

ARCHIVOS_CSV = [
    {
        "archivo": "generos.csv",
        "tabla": "generos",
        "mapeo": {"id": "id", "nombre": "nombre", "descripcion": "descripcion"},
    },
    {
        "archivo": "editoriales.csv",
        "tabla": "editoriales",
        "mapeo": {
            "id": "id",
            "nombre": "nombre",
            "pais": "pais",
            "sitio_web": "sitio_web",
        },
    },
    {
        "archivo": "monedas.csv",
        "tabla": "monedas",
        "mapeo": {
            "id": "id",
            "codigo": "codigo",
            "nombre": "nombre",
            "simbolo": "simbolo",
        },
    },
    {
        "archivo": "tipos_cotizacion.csv",
        "tabla": "tipos_cotizacion",
        "mapeo": {"id": "id", "nombre": "nombre", "descripcion": "descripcion"},
    },
    {
        "archivo": "libros.csv",
        "tabla": "libros",
        "mapeo": {
            "id": "id",
            "isbn": "isbn",
            "titulo": "titulo",
            "autor": "autor",
            "editorial_id": "editorial_id",
            "genero_id": "genero_id",
            "anio": "anio",
            "paginas": "paginas",
        },
    },
    {
        "archivo": "precios.csv",
        "tabla": "precios_libro",
        "mapeo": {
            "id": "id",
            "libro_id": "libro_id",
            "moneda_id": "moneda_id",
            "importe": "precio",
        },
    },
    {
        "archivo": "stocks.csv",
        "tabla": "stock_libro",
        "mapeo": {
            "libro_id": "libro_id",
            "cantidad": "cantidad",
            "punto_reposicion": "punto_reposicion",
        },
    },
    {
        "archivo": "cotizaciones_dolar.csv",
        "tabla": "cotizaciones_dolar",
        "mapeo": {
            "tipo_id": "tipo_cotizacion_id",
            "fecha": "fecha",
            "compra": "compra",
            "venta": "venta",
        },
    },
]

OBLIGATORIAS = {
    "generos": {"id", "nombre"},
    "editoriales": {"id", "nombre"},
    "monedas": {"id", "codigo", "nombre", "simbolo"},
    "tipos_cotizacion": {"id", "nombre"},
    "libros": {"id", "isbn", "titulo", "autor", "editorial_id",
               "genero_id", "anio", "paginas"},
    "precios_libro": {"id", "libro_id", "moneda_id", "precio"},
    "stock_libro": {"libro_id", "cantidad"},
    "cotizaciones_dolar": {"tipo_cotizacion_id", "fecha", "compra", "venta"},
}


def _escapar_valor(valor):
    """Escapa comillas simples para generar sintaxis SQL valida.

    Args:
        valor (str): Valor de texto taken del CSV.

    Returns:
        str: Literal SQL entre comillas simples.
    """
    return "'" + valor.replace("'", "''") + "'"


def _formatear_valor(origen, destino):
    """Convierte un valor del CSV al literal SQL segun el tipo del destino.

    Args:
        origen (str): Valor crudo de la celda del CSV.
        destino (str): Nombre de la columna en el modelo.

    Returns:
        str: Literal SQL listo para el INSERT.
    """
    valor = (origen or "").strip()
    if valor == "":
        return "NULL"
    if destino in COLUMNAS_ENTERAS:
        return str(int(float(valor)))
    if destino in COLUMNAS_DECIMALES:
        return str(float(valor))
    return _escapar_valor(valor)


def migrar_datos(carpeta_csvs: str, carpeta_sqls: str, db: ConexionDB = None) -> None:
    """Migra los CSV a la base relacional y guarda los scripts SQL generados.

    Antes de insertar valida que cada CSV tenga las columnas del mapeo, de modo
    que una diferencia de nombres se reporte en lugar de terminar en un
    IntegrityError a mitad de la carga.

    Args:
        carpeta_csvs (str): Carpeta con los CSV de origen.
        carpeta_sqls (str): Carpeta donde se guardan los SQL generados.
        db (ConexionDB): Conexion a reutilizar. Si es None se crea una.

    Raises:
        FileNotFoundError: Si falta un CSV o le faltan columnas del mapeo.
    """
    path_csv = Path(carpeta_csvs)
    path_sql = Path(carpeta_sqls)
    path_sql.mkdir(parents=True, exist_ok=True)

    if db is None:
        db = ConexionDB()
    Base.metadata.create_all(bind=db.engine)

    problemas = []
    resumen = []

    for entrada in ARCHIVOS_CSV:
        archivo_csv = path_csv / entrada["archivo"]

        if not archivo_csv.exists():
            problemas.append(entrada["archivo"] + ": el archivo no existe")
            continue

        with open(archivo_csv, "r", encoding="utf-8-sig") as archivo:
            reader = csv.DictReader(archivo)
            encabezados = reader.fieldnames or []

            faltantes = [c for c in entrada["mapeo"] if c not in encabezados]
            if faltantes:
                problemas.append(
                    entrada["archivo"] + ": faltan columnas " + str(faltantes)
                    + " (encabezado real: " + str(encabezados) + ")"
                )
                continue

            destinos = list(entrada["mapeo"].values())
            obligatorias = OBLIGATORIAS.get(entrada["tabla"], set())

            lineas_sql = []
            descartadas = 0

            for numero, fila in enumerate(reader, start=2):
                vacias = [
                    destino
                    for origen, destino in entrada["mapeo"].items()
                    if destino in obligatorias
                    and not (fila.get(origen) or "").strip()
                ]
                if vacias:
                    descartadas += 1
                    problemas.append(
                        entrada["archivo"] + ": fila " + str(numero)
                        + " sin valores obligatorios en " + str(vacias)
                    )
                    continue

                valores = [
                    _formatear_valor(fila.get(origen), destino)
                    for origen, destino in entrada["mapeo"].items()
                ]
                lineas_sql.append(
                    "INSERT INTO " + entrada["tabla"]
                    + " (" + ", ".join(destinos) + ") VALUES ("
                    + ", ".join(valores) + ");\n"
                )

        archivo_sql = path_sql / (entrada["tabla"] + ".sql")
        with open(archivo_sql, "w", encoding="utf-8") as salida:
            salida.writelines(lineas_sql)

        with db.transaccion() as sesion:
            for sentencia in lineas_sql:
                if sentencia.strip():
                    sesion.execute(text(sentencia))

        resumen.append(
            "  " + entrada["archivo"] + " -> " + entrada["tabla"] + ": "
            + str(len(lineas_sql)) + " filas"
            + (" (" + str(descartadas) + " descartadas)" if descartadas else "")
        )

    print("\n".join(resumen))

    if problemas:
        raise FileNotFoundError(
            "Problemas en la migracion:\n"
            + "\n".join("  - " + p for p in problemas)
        )

    print("Migracion completada.")
