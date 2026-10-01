"""Consola de Book Manager.

Toda la entrada y la salida pasan por acá. Las reglas quedan en los
servicios. La demostración cubre el listado y el alta o la modificación
que pide el notebook, sin esperar teclas, para que "Ejecutar todo" pueda
seguir con las celdas de git.
"""

from dataclasses import dataclass
from datetime import date
from typing import Dict
from typing import Optional
from typing import Sequence

from book_manager.entities.entities import CotizacionDolar
from book_manager.entities.entities import Editorial
from book_manager.entities.entities import Genero
from book_manager.entities.entities import Libro
from book_manager.entities.entities import Moneda
from book_manager.entities.entities import Precio
from book_manager.entities.entities import Stock
from book_manager.entities.entities import TipoCotizacion
from book_manager.services.services import ComparacionCuspide
from book_manager.services.services import Contexto
from book_manager.services.services import LineaHistorico
from book_manager.services.services import LineaStock


def formatear_pesos(valor: float) -> str:
    """Formatea un importe con separador de miles y coma decimal."""
    texto = f"{valor:,.2f}"
    return "$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


@dataclass
class _InformeGuardado:
    """Copia de un reporte emitido durante la sesión de consola."""

    id: int
    titulo: str
    detalle: str


class Consola:
    """Menú de consola con el CRUD de cada clase y los reportes."""

    def __init__(self, contexto: Contexto) -> None:
        self.__contexto = contexto
        self.__informes: Dict[int, _InformeGuardado] = {}
        self.__proximo_informe = 1

    def ejecutar(self) -> None:
        """Abre el menú principal hasta que se elige salir."""
        try:
            self.__bucle_principal()
        except EOFError:
            print("\nSe cerró la entrada. Fin de la sesión.")

    def __bucle_principal(self) -> None:
        while True:
            print("\n=== Book Manager - Sprint 1 ===")
            print("Referencia de catálogo: https://cuspide.com/")
            print("1. Géneros")
            print("2. Editoriales")
            print("3. Monedas")
            print("4. Tipos de cotización")
            print("5. Libros")
            print("6. Precios")
            print("7. Stock")
            print("8. Cotizaciones del dólar")
            print("9. Reportes")
            print("0. Salir")
            opcion = input("Opción: ").strip()
            if opcion == "0":
                print("Fin de la sesión.")
                return
            try:
                match opcion:
                    case "1":
                        self.__menu_generos()
                    case "2":
                        self.__menu_editoriales()
                    case "3":
                        self.__menu_monedas()
                    case "4":
                        self.__menu_tipos()
                    case "5":
                        self.__menu_libros()
                    case "6":
                        self.__menu_precios()
                    case "7":
                        self.__menu_stock()
                    case "8":
                        self.__menu_cotizaciones()
                    case "9":
                        self.__menu_reportes()
                    case _:
                        print("Opción inválida.")
            except ValueError as error:
                print(f"No se pudo completar la operación: {error}")

    def __menu_generos(self) -> None:
        servicio = self.__contexto.generos
        while True:
            self.__titulo("Géneros")
            opcion = self.__leer_opcion_crud()
            if opcion == "0":
                return
            match opcion:
                case "1":
                    self.__listar(servicio.leer_todos())
                case "2":
                    creado = servicio.crear(
                        Genero(
                            id=0,
                            nombre=self.__pedir_texto("Nombre: "),
                            descripcion=self.__pedir_texto("Descripción: "),
                        )
                    )
                    print(f"Alta realizada: {creado}")
                case "3":
                    actual = self.__exigir(servicio.leer_por_id(self.__pedir_entero("Id: ")))
                    actual.nombre = self.__pedir_texto(
                        f"Nombre [{actual.nombre}]: ", actual.nombre
                    )
                    actual.descripcion = self.__pedir_texto(
                        f"Descripción [{actual.descripcion}]: ",
                        actual.descripcion,
                    )
                    print(f"Modificación realizada: {servicio.actualizar(actual)}")
                case "4":
                    self.__avisar_borrado(servicio.eliminar(self.__pedir_entero("Id: ")))
                case "5":
                    self.__mostrar(servicio.leer_por_id(self.__pedir_entero("Id: ")))
                case _:
                    print("Opción inválida.")

    def __menu_editoriales(self) -> None:
        servicio = self.__contexto.editoriales
        while True:
            self.__titulo("Editoriales")
            opcion = self.__leer_opcion_crud()
            if opcion == "0":
                return
            match opcion:
                case "1":
                    self.__listar(servicio.leer_todos())
                case "2":
                    creado = servicio.crear(
                        Editorial(
                            id=0,
                            nombre=self.__pedir_texto("Nombre: "),
                            pais=self.__pedir_texto("País: "),
                            sitio_web=self.__pedir_texto("Sitio web: "),
                        )
                    )
                    print(f"Alta realizada: {creado}")
                case "3":
                    actual = self.__exigir(servicio.leer_por_id(self.__pedir_entero("Id: ")))
                    actual.nombre = self.__pedir_texto(
                        f"Nombre [{actual.nombre}]: ", actual.nombre
                    )
                    actual.pais = self.__pedir_texto(
                        f"País [{actual.pais}]: ", actual.pais
                    )
                    actual.sitio_web = self.__pedir_texto(
                        f"Sitio web [{actual.sitio_web}]: ", actual.sitio_web
                    )
                    print(f"Modificación realizada: {servicio.actualizar(actual)}")
                case "4":
                    self.__avisar_borrado(servicio.eliminar(self.__pedir_entero("Id: ")))
                case "5":
                    self.__mostrar(servicio.leer_por_id(self.__pedir_entero("Id: ")))
                case _:
                    print("Opción inválida.")

    def __menu_monedas(self) -> None:
        servicio = self.__contexto.monedas
        while True:
            self.__titulo("Monedas")
            opcion = self.__leer_opcion_crud()
            if opcion == "0":
                return
            match opcion:
                case "1":
                    self.__listar(servicio.leer_todos())
                case "2":
                    creado = servicio.crear(
                        Moneda(
                            id=0,
                            codigo=self.__pedir_texto("Código de 3 letras: "),
                            nombre=self.__pedir_texto("Nombre: "),
                            simbolo=self.__pedir_texto("Símbolo: "),
                        )
                    )
                    print(f"Alta realizada: {creado}")
                case "3":
                    actual = self.__exigir(servicio.leer_por_id(self.__pedir_entero("Id: ")))
                    actual.codigo = self.__pedir_texto(
                        f"Código [{actual.codigo}]: ", actual.codigo
                    )
                    actual.nombre = self.__pedir_texto(
                        f"Nombre [{actual.nombre}]: ", actual.nombre
                    )
                    actual.simbolo = self.__pedir_texto(
                        f"Símbolo [{actual.simbolo}]: ", actual.simbolo
                    )
                    print(f"Modificación realizada: {servicio.actualizar(actual)}")
                case "4":
                    self.__avisar_borrado(servicio.eliminar(self.__pedir_entero("Id: ")))
                case "5":
                    self.__mostrar(servicio.leer_por_id(self.__pedir_entero("Id: ")))
                case _:
                    print("Opción inválida.")

    def __menu_tipos(self) -> None:
        servicio = self.__contexto.tipos_cotizacion
        while True:
            self.__titulo("Tipos de cotización")
            opcion = self.__leer_opcion_crud()
            if opcion == "0":
                return
            match opcion:
                case "1":
                    self.__listar(servicio.leer_todos())
                case "2":
                    creado = servicio.crear(
                        TipoCotizacion(
                            id=0,
                            nombre=self.__pedir_texto("Nombre: "),
                            descripcion=self.__pedir_texto("Descripción: "),
                        )
                    )
                    print(f"Alta realizada: {creado}")
                case "3":
                    actual = self.__exigir(servicio.leer_por_id(self.__pedir_entero("Id: ")))
                    actual.nombre = self.__pedir_texto(
                        f"Nombre [{actual.nombre}]: ", actual.nombre
                    )
                    actual.descripcion = self.__pedir_texto(
                        f"Descripción [{actual.descripcion}]: ",
                        actual.descripcion,
                    )
                    print(f"Modificación realizada: {servicio.actualizar(actual)}")
                case "4":
                    self.__avisar_borrado(servicio.eliminar(self.__pedir_entero("Id: ")))
                case "5":
                    self.__mostrar(servicio.leer_por_id(self.__pedir_entero("Id: ")))
                case _:
                    print("Opción inválida.")

    def __menu_libros(self) -> None:
        servicio = self.__contexto.libros
        while True:
            self.__titulo("Libros")
            opcion = self.__leer_opcion_crud()
            if opcion == "0":
                return
            match opcion:
                case "1":
                    self.__listar(servicio.leer_todos())
                case "2":
                    print("Géneros:")
                    self.__listar(self.__contexto.generos.leer_todos())
                    print("Editoriales:")
                    self.__listar(self.__contexto.editoriales.leer_todos())
                    creado = servicio.crear(
                        Libro(
                            id=0,
                            isbn=self.__pedir_texto("ISBN: "),
                            titulo=self.__pedir_texto("Título: "),
                            autor=self.__pedir_texto("Autor: "),
                            editorial_id=self.__pedir_entero("Id de editorial: "),
                            genero_id=self.__pedir_entero("Id de género: "),
                            anio=self.__pedir_entero("Año: "),
                            paginas=self.__pedir_entero("Páginas: "),
                        )
                    )
                    print(f"Alta realizada: {creado}")
                case "3":
                    actual = self.__exigir(servicio.leer_por_id(self.__pedir_entero("Id: ")))
                    actual.isbn = self.__pedir_texto(f"ISBN [{actual.isbn}]: ", actual.isbn)
                    actual.titulo = self.__pedir_texto(
                        f"Título [{actual.titulo}]: ", actual.titulo
                    )
                    actual.autor = self.__pedir_texto(
                        f"Autor [{actual.autor}]: ", actual.autor
                    )
                    actual.editorial_id = self.__pedir_entero(
                        f"Id de editorial [{actual.editorial_id}]: ",
                        actual.editorial_id,
                    )
                    actual.genero_id = self.__pedir_entero(
                        f"Id de género [{actual.genero_id}]: ",
                        actual.genero_id,
                    )
                    actual.anio = self.__pedir_entero(f"Año [{actual.anio}]: ", actual.anio)
                    actual.paginas = self.__pedir_entero(
                        f"Páginas [{actual.paginas}]: ", actual.paginas
                    )
                    print(f"Modificación realizada: {servicio.actualizar(actual)}")
                case "4":
                    self.__avisar_borrado(servicio.eliminar(self.__pedir_entero("Id: ")))
                case "5":
                    self.__mostrar(servicio.leer_por_id(self.__pedir_entero("Id: ")))
                case _:
                    print("Opción inválida.")

    def __menu_precios(self) -> None:
        servicio = self.__contexto.precios
        while True:
            self.__titulo("Precios")
            opcion = self.__leer_opcion_crud()
            if opcion == "0":
                return
            match opcion:
                case "1":
                    self.__listar(servicio.leer_todos())
                case "2":
                    creado = servicio.crear(
                        Precio(
                            id=0,
                            libro_id=self.__pedir_entero("Id de libro: "),
                            moneda_id=self.__pedir_entero("Id de moneda: "),
                            importe=self.__pedir_decimal("Importe: "),
                        )
                    )
                    print(f"Alta realizada: {creado}")
                case "3":
                    actual = self.__exigir(servicio.leer_por_id(self.__pedir_entero("Id: ")))
                    actual.importe = self.__pedir_decimal(
                        f"Importe [{actual.importe:.2f}]: ",
                        actual.importe,
                    )
                    print(f"Modificación realizada: {servicio.actualizar(actual)}")
                case "4":
                    self.__avisar_borrado(servicio.eliminar(self.__pedir_entero("Id: ")))
                case "5":
                    self.__mostrar(servicio.leer_por_id(self.__pedir_entero("Id: ")))
                case _:
                    print("Opción inválida.")

    def __menu_stock(self) -> None:
        servicio = self.__contexto.stocks
        while True:
            self.__titulo("Stock")
            opcion = self.__leer_opcion_crud()
            if opcion == "0":
                return
            match opcion:
                case "1":
                    self.__listar(servicio.leer_todos())
                case "2":
                    creado = servicio.crear(
                        Stock(
                            libro_id=self.__pedir_entero("Id de libro: "),
                            cantidad=self.__pedir_entero("Cantidad: "),
                            punto_reposicion=self.__pedir_entero("Punto de reposición: "),
                        )
                    )
                    print(f"Alta realizada: {creado}")
                case "3":
                    libro_id = self.__pedir_entero("Id de libro: ")
                    actual = self.__exigir(servicio.leer_por_libro(libro_id))
                    actual.cantidad = self.__pedir_entero(
                        f"Cantidad [{actual.cantidad}]: ", actual.cantidad
                    )
                    actual.punto_reposicion = self.__pedir_entero(
                        f"Punto de reposición [{actual.punto_reposicion}]: ",
                        actual.punto_reposicion,
                    )
                    print(f"Modificación realizada: {servicio.actualizar(actual)}")
                case "4":
                    self.__avisar_borrado(
                        servicio.eliminar(self.__pedir_entero("Id de libro: "))
                    )
                case "5":
                    self.__mostrar(
                        servicio.leer_por_libro(self.__pedir_entero("Id de libro: "))
                    )
                case _:
                    print("Opción inválida.")

    def __menu_cotizaciones(self) -> None:
        servicio = self.__contexto.cotizaciones
        while True:
            self.__titulo("Cotizaciones del dólar", "Lectura por tipo y fecha")
            opcion = self.__leer_opcion_crud()
            if opcion == "0":
                return
            match opcion:
                case "1":
                    self.__listar(servicio.leer_todas())
                case "2":
                    creado = servicio.crear(
                        CotizacionDolar(
                            tipo_cotizacion_id=self.__pedir_entero("Id de tipo: "),
                            fecha=self.__pedir_fecha("Fecha AAAA-MM-DD: "),
                            compra=self.__pedir_decimal("Compra: "),
                            venta=self.__pedir_decimal("Venta: "),
                        )
                    )
                    print(f"Alta realizada: {creado}")
                case "3":
                    tipo_id = self.__pedir_entero("Id de tipo: ")
                    fecha = self.__pedir_fecha("Fecha AAAA-MM-DD: ")
                    actual = self.__exigir(servicio.leer_por_tipo_y_fecha(tipo_id, fecha))
                    actual.compra = self.__pedir_decimal(
                        f"Compra [{actual.compra:.2f}]: ", actual.compra
                    )
                    actual.venta = self.__pedir_decimal(
                        f"Venta [{actual.venta:.2f}]: ", actual.venta
                    )
                    print(f"Modificación realizada: {servicio.actualizar(actual)}")
                case "4":
                    self.__avisar_borrado(
                        servicio.eliminar(
                            self.__pedir_entero("Id de tipo: "),
                            self.__pedir_fecha("Fecha AAAA-MM-DD: "),
                        )
                    )
                case "5":
                    self.__mostrar(
                        servicio.leer_por_tipo_y_fecha(
                            self.__pedir_entero("Id de tipo: "),
                            self.__pedir_fecha("Fecha AAAA-MM-DD: "),
                        )
                    )
                case _:
                    print("Opción inválida.")

    def __menu_reportes(self) -> None:
        while True:
            print("\n--- Reportes ---")
            print("1. Comparación con Cúspide según un tipo de dólar")
            print("2. Stock a reponer")
            print("3. Histórico de cotización")
            print("4. Listado")
            print("5. Alta")
            print("6. Modificación")
            print("7. Borrado")
            print("8. Lectura")
            print("0. Volver")
            opcion = input("Opción: ").strip()
            if opcion == "0":
                return
            match opcion:
                case "1":
                    tipo_id = self.__pedir_entero("Id de tipo de cotización: ")
                    self.mostrar_comparacion(
                        self.__contexto.reportes.comparar_con_cuspide(tipo_id)
                    )
                case "2":
                    self.mostrar_stock(self.__contexto.reportes.stock_a_reponer())
                case "3":
                    tipo_id = self.__pedir_entero("Id de tipo de cotización: ")
                    self.mostrar_historico(self.__contexto.reportes.historico(tipo_id))
                case "4":
                    self.__listar_informes()
                case "5":
                    self.__alta_informe()
                case "6":
                    self.__modificar_informe()
                case "7":
                    self.__borrar_informe()
                case "8":
                    self.__leer_informe()
                case _:
                    print("Opción inválida.")

    def __listar_informes(self) -> None:
        if not self.__informes:
            print("No hay informes guardados.")
            return
        for identificador in sorted(self.__informes):
            informe = self.__informes[identificador]
            print(f"  [{informe.id}] {informe.titulo}")

    def __alta_informe(self) -> None:
        titulo = self.__pedir_texto("Título del informe: ")
        print("1. Comparación con Cúspide")
        print("2. Stock a reponer")
        print("3. Histórico de cotización")
        origen = input("Origen: ").strip()
        match origen:
            case "1":
                tipo_id = self.__pedir_entero("Id de tipo de cotización: ")
                detalle = self._texto_comparacion(
                    self.__contexto.reportes.comparar_con_cuspide(tipo_id)
                )
            case "2":
                detalle = self._texto_stock(self.__contexto.reportes.stock_a_reponer())
            case "3":
                tipo_id = self.__pedir_entero("Id de tipo de cotización: ")
                detalle = self._texto_historico(self.__contexto.reportes.historico(tipo_id))
            case _:
                raise ValueError("El origen del informe no es válido.")
        informe = _InformeGuardado(self.__proximo_informe, titulo, detalle)
        self.__informes[informe.id] = informe
        self.__proximo_informe += 1
        print(f"Alta realizada: [{informe.id}] {informe.titulo}")
        print(informe.detalle)

    def __modificar_informe(self) -> None:
        informe = self.__informes.get(self.__pedir_entero("Id: "))
        if informe is None:
            raise ValueError("No se encontró el informe.")
        informe.titulo = self.__pedir_texto(
            f"Título [{informe.titulo}]: ",
            informe.titulo,
        )
        print(f"Modificación realizada: [{informe.id}] {informe.titulo}")

    def __borrar_informe(self) -> None:
        identificador = self.__pedir_entero("Id: ")
        if identificador not in self.__informes:
            print("No se encontró el informe.")
            return
        del self.__informes[identificador]
        print("Informe eliminado.")

    def __leer_informe(self) -> None:
        informe = self.__informes.get(self.__pedir_entero("Id: "))
        if informe is None:
            print("No se encontró el informe.")
            return
        print(f"[{informe.id}] {informe.titulo}")
        print(informe.detalle)

    def mostrar_comparacion(self, filas: Sequence[ComparacionCuspide]) -> None:
        """Imprime la comparación contra el precio público de Cúspide."""
        print(self._texto_comparacion(filas))

    def mostrar_stock(self, filas: Sequence[LineaStock]) -> None:
        """Imprime los libros que hay que reponer."""
        print(self._texto_stock(filas))

    def mostrar_historico(self, filas: Sequence[LineaHistorico]) -> None:
        """Imprime el histórico de un tipo de dólar."""
        print(self._texto_historico(filas))

    def _texto_comparacion(self, filas: Sequence[ComparacionCuspide]) -> str:
        """Arma el texto de la comparación con Cúspide."""
        if not filas:
            return "No hay libros con precio en pesos y en dólares."
        lineas = [
            f"Cotización usada: {filas[0].tipo_cotizacion} "
            f"venta {formatear_pesos(filas[0].cotizacion_venta)}"
        ]
        for fila in filas:
            estado = "cubre el costo" if fila.cubre_el_costo else "no cubre el costo"
            lineas.append(
                f"  {fila.titulo} ({fila.autor}) | "
                f"Cúspide {formatear_pesos(fila.precio_cuspide_ars)} | "
                f"costo USD {fila.costo_usd:.2f} -> "
                f"{formatear_pesos(fila.costo_reposicion_ars)} | "
                f"diferencia {formatear_pesos(fila.diferencia_ars)} ({estado})"
            )
        return "\n".join(lineas)

    def _texto_stock(self, filas: Sequence[LineaStock]) -> str:
        """Arma el texto del stock a reponer."""
        if not filas:
            return "No hay libros en el punto de reposición."
        lineas = []
        for fila in filas:
            texto = "1 unidad" if fila.cantidad == 1 else f"{fila.cantidad} unidades"
            lineas.append(
                f"  {fila.titulo} ({fila.autor}): "
                f"{texto}, reponer al llegar a {fila.punto_reposicion}"
            )
        return "\n".join(lineas)

    def _texto_historico(self, filas: Sequence[LineaHistorico]) -> str:
        """Arma el texto del histórico de cotización."""
        if not filas:
            return "No hay cotizaciones para ese tipo."
        return "\n".join(
            f"  {fila.fecha.isoformat()} {fila.tipo}: "
            f"compra {formatear_pesos(fila.compra)} / "
            f"venta {formatear_pesos(fila.venta)}"
            for fila in filas
        )

    def __titulo(self, texto: str, lectura: str = "Lectura") -> None:
        print(f"\n--- {texto} ---")
        print(
            "1. Listado  2. Alta  3. Modificación  4. Borrado  "
            f"5. {lectura}  0. Volver"
        )

    def __leer_opcion_crud(self) -> str:
        return input("Opción: ").strip()

    def __listar(self, entidades: Sequence[object]) -> None:
        if not entidades:
            print("No hay registros.")
            return
        for entidad in entidades:
            print(f"  {entidad}")

    def __mostrar(self, entidad: Optional[object]) -> None:
        if entidad is None:
            print("No se encontró el registro.")
            return
        print(entidad)

    def __exigir(self, entidad: Optional[object]) -> object:
        if entidad is None:
            raise ValueError("No se encontró el registro.")
        return entidad

    def __avisar_borrado(self, eliminado: bool) -> None:
        if eliminado:
            print("Registro eliminado.")
            return
        print("No se encontró el registro.")

    def __pedir_texto(self, mensaje: str, valor_actual: Optional[str] = None) -> str:
        texto = input(mensaje).strip()
        if texto == "" and valor_actual is not None:
            return valor_actual
        if texto == "":
            raise ValueError("El texto no puede estar vacío.")
        return texto

    def __pedir_entero(
        self,
        mensaje: str,
        valor_actual: Optional[int] = None,
    ) -> int:
        texto = input(mensaje).strip()
        if texto == "" and valor_actual is not None:
            return valor_actual
        if not texto.isdigit():
            raise ValueError("Se esperaba un número entero mayor o igual a cero.")
        return int(texto)

    def __pedir_decimal(
        self,
        mensaje: str,
        valor_actual: Optional[float] = None,
    ) -> float:
        texto = input(mensaje).strip().replace(",", ".")
        if texto == "" and valor_actual is not None:
            return valor_actual
        try:
            return float(texto)
        except ValueError as error:
            raise ValueError("Se esperaba un número.") from error

    def __pedir_fecha(self, mensaje: str) -> date:
        texto = input(mensaje).strip()
        try:
            return date.fromisoformat(texto)
        except ValueError as error:
            raise ValueError("La fecha debe tener el formato AAAA-MM-DD.") from error


def ejecutar_demostracion(contexto: Contexto) -> None:
    """Lista cada modelo y hace un alta o una modificación, y luego los reportes.

    La segunda ejecución modifica el registro de demostración en lugar de
    volver a darlo de alta.

    Args:
        contexto (Contexto): Servicios ya armados.
    """
    consola = Consola(contexto)
    print("Book Manager - demostración del Sprint 1")
    print("Catálogo de referencia: https://cuspide.com/")
    print("Grupo 28")
    _demostrar_genero(contexto)
    _demostrar_editorial(contexto)
    _demostrar_moneda(contexto)
    _demostrar_tipo(contexto)
    libro = _demostrar_libro(contexto)
    _demostrar_precio(contexto, libro.id)
    _demostrar_stock(contexto, libro.id)
    _demostrar_cotizacion(contexto)
    print("\n=== Reportes ===")
    print("\nComparación con Cúspide al dólar blue")
    blue = contexto.tipos_cotizacion.buscar_por_nombre("Blue")
    if blue is None:
        raise ValueError("Falta el tipo de cotización Blue en los datos iniciales.")
    consola.mostrar_comparacion(contexto.reportes.comparar_con_cuspide(blue.id))
    print("\nComparación con Cúspide al dólar oficial")
    oficial = contexto.tipos_cotizacion.buscar_por_nombre("Oficial")
    if oficial is None:
        raise ValueError("Falta el tipo de cotización Oficial en los datos iniciales.")
    consola.mostrar_comparacion(contexto.reportes.comparar_con_cuspide(oficial.id))
    print("\nStock a reponer")
    consola.mostrar_stock(contexto.reportes.stock_a_reponer())
    print("\nHistórico del dólar blue")
    consola.mostrar_historico(contexto.reportes.historico(blue.id))
    print("\nDemostración finalizada.")


def _demostrar_genero(contexto: Contexto) -> None:
    print("\n--- Géneros: listado ---")
    _imprimir(contexto.generos.leer_todos())
    existente = contexto.generos.buscar_por_nombre("Teatro")
    if existente is None:
        creado = contexto.generos.crear(
            Genero(
                id=0,
                nombre="Teatro",
                descripcion="Género cargado en la demostración del sprint 1.",
            )
        )
        print(f"Alta realizada: {creado}")
        return
    existente.descripcion = "Género actualizado en la demostración del sprint 1."
    print(f"Modificación realizada: {contexto.generos.actualizar(existente)}")


def _demostrar_editorial(contexto: Contexto) -> None:
    print("\n--- Editoriales: listado ---")
    _imprimir(contexto.editoriales.leer_todos())
    existente = contexto.editoriales.buscar_por_nombre("Cátedra")
    if existente is None:
        creado = contexto.editoriales.crear(
            Editorial(
                id=0,
                nombre="Cátedra",
                pais="España",
                sitio_web="https://www.catedra.com",
            )
        )
        print(f"Alta realizada: {creado}")
        return
    existente.sitio_web = "https://www.catedra.com"
    print(f"Modificación realizada: {contexto.editoriales.actualizar(existente)}")


def _demostrar_moneda(contexto: Contexto) -> None:
    print("\n--- Monedas: listado ---")
    _imprimir(contexto.monedas.leer_todos())
    existente = contexto.monedas.buscar_por_codigo("XXX")
    if existente is None:
        creado = contexto.monedas.crear(
            Moneda(id=0, codigo="XXX", nombre="Moneda de prueba", simbolo="X")
        )
        print(f"Alta realizada: {creado}")
        return
    existente.nombre = "Moneda de prueba del sprint 1"
    print(f"Modificación realizada: {contexto.monedas.actualizar(existente)}")


def _demostrar_tipo(contexto: Contexto) -> None:
    print("\n--- Tipos de cotización: listado ---")
    _imprimir(contexto.tipos_cotizacion.leer_todos())
    existente = contexto.tipos_cotizacion.buscar_por_nombre("Prueba")
    if existente is None:
        creado = contexto.tipos_cotizacion.crear(
            TipoCotizacion(
                id=0,
                nombre="Prueba",
                descripcion="Tipo cargado en la demostración del sprint 1.",
            )
        )
        print(f"Alta realizada: {creado}")
        return
    existente.descripcion = "Tipo actualizado en la demostración del sprint 1."
    print(f"Modificación realizada: {contexto.tipos_cotizacion.actualizar(existente)}")


def _demostrar_libro(contexto: Contexto) -> Libro:
    print("\n--- Libros: listado ---")
    _imprimir(contexto.libros.leer_todos())
    isbn = "978-950-28-0099-1"
    existente = contexto.libros.buscar_por_isbn(isbn)
    if existente is None:
        creado = contexto.libros.crear(
            Libro(
                id=0,
                isbn=isbn,
                titulo="Libro de demostración del sprint 1",
                autor="Grupo 28",
                editorial_id=1,
                genero_id=1,
                anio=2026,
                paginas=128,
            )
        )
        print(f"Alta realizada: {creado}")
        return creado
    existente.paginas = 128
    actualizado = contexto.libros.actualizar(existente)
    print(f"Modificación realizada: {actualizado}")
    return actualizado


def _demostrar_precio(contexto: Contexto, libro_id: int) -> None:
    print("\n--- Precios: listado ---")
    _imprimir(contexto.precios.leer_todos())
    moneda = contexto.monedas.buscar_por_codigo("ARS")
    if moneda is None:
        raise ValueError("Falta la moneda ARS en los datos iniciales.")
    existente = contexto.precios.buscar(libro_id, moneda.id)
    if existente is None:
        creado = contexto.precios.crear(
            Precio(id=0, libro_id=libro_id, moneda_id=moneda.id, importe=15000)
        )
        print(f"Alta realizada: {creado}")
        return
    existente.importe = 15000
    print(f"Modificación realizada: {contexto.precios.actualizar(existente)}")


def _demostrar_stock(contexto: Contexto, libro_id: int) -> None:
    print("\n--- Stock: listado ---")
    _imprimir(contexto.stocks.leer_todos())
    existente = contexto.stocks.leer_por_libro(libro_id)
    if existente is None:
        creado = contexto.stocks.crear(
            Stock(libro_id=libro_id, cantidad=4, punto_reposicion=2)
        )
        print(f"Alta realizada: {creado}")
        return
    existente.cantidad = 4
    print(f"Modificación realizada: {contexto.stocks.actualizar(existente)}")


def _demostrar_cotizacion(contexto: Contexto) -> None:
    print("\n--- Cotizaciones del dólar: listado ---")
    _imprimir(contexto.cotizaciones.leer_todas())
    oficial = contexto.tipos_cotizacion.buscar_por_nombre("Oficial")
    if oficial is None:
        raise ValueError("Falta el tipo de cotización Oficial en los datos iniciales.")
    fecha = date(2026, 10, 2)
    existente = contexto.cotizaciones.leer_por_tipo_y_fecha(oficial.id, fecha)
    if existente is None:
        creado = contexto.cotizaciones.crear(
            CotizacionDolar(
                tipo_cotizacion_id=oficial.id,
                fecha=fecha,
                compra=1490,
                venta=1540,
            )
        )
        print(f"Alta realizada: {creado}")
        return
    existente.compra = 1490
    existente.venta = 1540
    print(f"Modificación realizada: {contexto.cotizaciones.actualizar(existente)}")


def _imprimir(entidades: Sequence[object]) -> None:
    if not entidades:
        print("  No hay registros.")
        return
    for entidad in entidades:
        print(f"  {entidad}")
