import csv
import re
from pathlib import Path

from sqlalchemy import text

from book_manager.database.connection import ConexionDB

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
    db.crear_tablas()

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


def cargar_datos_desde_sql(
    carpeta_sqls: str,
    db: ConexionDB | None = None,
) -> dict[str, int]:
    """Carga los scripts .sql en la base.

    Si la tabla de un archivo ya tiene filas, no vuelve a insertarlas.
    Así se puede ejecutar de nuevo sin duplicar el catálogo.

    Args:
        carpeta_sqls (str): Carpeta con los .sql generados en el Sprint 2.
        db (ConexionDB): Conexión a reutilizar. Si es None se crea una.

    Returns:
        dict[str, int]: Cantidad de filas por archivo.

    Raises:
        FileNotFoundError: Si la carpeta no tiene scripts.
        ValueError: Si un script no empieza con INSERT INTO.
    """
    path_sql = Path(carpeta_sqls)
    archivos = sorted(path_sql.glob("*.sql"))
    if not archivos:
        raise FileNotFoundError(
            f"No hay scripts SQL para cargar en {carpeta_sqls}."
        )
    if db is None:
        db = ConexionDB()
    db.crear_tablas()
    resumen: dict[str, int] = {}
    for archivo in archivos:
        sentencias = [
            linea.strip()
            for linea in archivo.read_text(encoding="utf-8").splitlines()
            if linea.strip()
        ]
        if not sentencias:
            resumen[archivo.name] = 0
            continue
        tabla = _tabla_de_insert(sentencias[0], archivo.name)
        with db.engine.connect() as conexion:
            cantidad = conexion.execute(
                text(f"SELECT COUNT(*) FROM {tabla}")
            ).scalar()
        if cantidad:
            resumen[archivo.name] = int(cantidad)
            continue
        with db.transaccion() as sesion:
            for sentencia in sentencias:
                sesion.execute(text(sentencia))
        resumen[archivo.name] = len(sentencias)
    return resumen


def _tabla_de_insert(sentencia: str, archivo: str) -> str:
    """Obtiene el nombre de tabla de un INSERT INTO."""
    coincidencia = re.match(
        r"INSERT\s+INTO\s+([a-z_]+)\b",
        sentencia,
        flags=re.IGNORECASE,
    )
    if coincidencia is None:
        raise ValueError(f"{archivo} no empieza con INSERT INTO.")
    return coincidencia.group(1)
