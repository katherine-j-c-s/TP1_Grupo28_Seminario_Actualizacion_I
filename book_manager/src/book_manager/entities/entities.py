"""Entidades de Book Manager.

Cada atributo queda encapsulado: se guarda en un nombre privado y se
expone con una propiedad que valida el valor antes de aceptarlo.
"""

from datetime import date


def _exigir_texto(valor: str, campo: str) -> str:
    """Devuelve el texto sin espacios laterales.

    Args:
        valor (str): Texto ingresado.
        campo (str): Nombre del campo, para el mensaje de error.

    Returns:
        str: Texto limpio.

    Raises:
        ValueError: Si el valor no es un texto o queda vacío.
    """
    if not isinstance(valor, str):
        raise ValueError(f"{campo} debe ser un texto.")
    limpio = valor.strip()
    if limpio == "":
        raise ValueError(f"{campo} no puede estar vacío.")
    return limpio


def _exigir_entero(valor: int, campo: str, permitir_cero: bool) -> int:
    """Valida un entero.

    Args:
        valor (int): Número a validar.
        campo (str): Nombre del campo.
        permitir_cero (bool): Permite el cero cuando es verdadero.

    Returns:
        int: El mismo entero, ya validado.

    Raises:
        ValueError: Si el valor no es un entero o está fuera de rango.
    """
    if type(valor) is not int:
        raise ValueError(f"{campo} debe ser un número entero.")
    if permitir_cero and valor < 0:
        raise ValueError(f"{campo} no puede ser negativo.")
    if not permitir_cero and valor <= 0:
        raise ValueError(f"{campo} debe ser mayor a cero.")
    return valor


def _exigir_importe(valor: float, campo: str) -> float:
    """Valida un importe positivo y lo redondea a dos decimales.

    Args:
        valor (float): Importe a validar.
        campo (str): Nombre del campo.

    Returns:
        float: Importe redondeado.

    Raises:
        ValueError: Si el valor no es numérico o no es positivo.
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{campo} debe ser un número.")
    importe = round(float(valor), 2)
    if importe <= 0:
        raise ValueError(f"{campo} debe ser mayor a cero.")
    return importe


class EntidadBase:
    """Entidad identificada por un id.

    El id 0 indica que el repositorio todavía no lo persistió.
    """

    def __init__(self, id: int) -> None:
        """Constructor.

        Args:
            id (int): Identificador. Cero si todavía no fue asignado.
        """
        self.__id = 0
        self.id = id

    @property
    def id(self) -> int:
        """Devuelve el identificador."""
        return self.__id

    @id.setter
    def id(self, valor: int) -> None:
        """Asigna el identificador.

        Args:
            valor (int): Nuevo identificador.

        Raises:
            ValueError: Si el valor no es un entero mayor o igual a cero.
        """
        self.__id = _exigir_entero(valor, "El id", permitir_cero=True)

    def __str__(self) -> str:
        return f"[{self.id}] {self.__class__.__name__}"


class Genero(EntidadBase):
    """Categoría literaria de un libro."""

    def __init__(self, id: int, nombre: str, descripcion: str) -> None:
        """Constructor.

        Args:
            id (int): Identificador.
            nombre (str): Nombre del género.
            descripcion (str): Descripción breve.
        """
        super().__init__(id)
        self.__nombre = ""
        self.__descripcion = ""
        self.nombre = nombre
        self.descripcion = descripcion

    @property
    def nombre(self) -> str:
        """Devuelve el nombre del género."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Asigna el nombre del género."""
        self.__nombre = _exigir_texto(valor, "El nombre del género")

    @property
    def descripcion(self) -> str:
        """Devuelve la descripción del género."""
        return self.__descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        """Asigna la descripción del género."""
        self.__descripcion = _exigir_texto(valor, "La descripción del género")

    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre}: {self.descripcion}"


class Editorial(EntidadBase):
    """Proveedor que distribuye los libros."""

    def __init__(self, id: int, nombre: str, pais: str, sitio_web: str) -> None:
        """Constructor.

        Args:
            id (int): Identificador.
            nombre (str): Nombre de la editorial.
            pais (str): País de origen.
            sitio_web (str): Sitio web.
        """
        super().__init__(id)
        self.__nombre = ""
        self.__pais = ""
        self.__sitio_web = ""
        self.nombre = nombre
        self.pais = pais
        self.sitio_web = sitio_web

    @property
    def nombre(self) -> str:
        """Devuelve el nombre de la editorial."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Asigna el nombre de la editorial."""
        self.__nombre = _exigir_texto(valor, "El nombre de la editorial")

    @property
    def pais(self) -> str:
        """Devuelve el país de la editorial."""
        return self.__pais

    @pais.setter
    def pais(self, valor: str) -> None:
        """Asigna el país de la editorial."""
        self.__pais = _exigir_texto(valor, "El país")

    @property
    def sitio_web(self) -> str:
        """Devuelve el sitio web de la editorial."""
        return self.__sitio_web

    @sitio_web.setter
    def sitio_web(self, valor: str) -> None:
        """Asigna el sitio web de la editorial."""
        self.__sitio_web = _exigir_texto(valor, "El sitio web")

    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre} ({self.pais}) - {self.sitio_web}"


class Moneda(EntidadBase):
    """Moneda en la que se puede expresar un precio."""

    def __init__(self, id: int, codigo: str, nombre: str, simbolo: str) -> None:
        """Constructor.

        Args:
            id (int): Identificador.
            codigo (str): Código de tres letras.
            nombre (str): Nombre de la moneda.
            simbolo (str): Símbolo.
        """
        super().__init__(id)
        self.__codigo = ""
        self.__nombre = ""
        self.__simbolo = ""
        self.codigo = codigo
        self.nombre = nombre
        self.simbolo = simbolo

    @property
    def codigo(self) -> str:
        """Devuelve el código de la moneda."""
        return self.__codigo

    @codigo.setter
    def codigo(self, valor: str) -> None:
        """Asigna el código de tres letras."""
        limpio = _exigir_texto(valor, "El código").upper()
        if len(limpio) != 3 or not limpio.isalpha():
            raise ValueError("El código de la moneda debe tener 3 letras.")
        self.__codigo = limpio

    @property
    def nombre(self) -> str:
        """Devuelve el nombre de la moneda."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Asigna el nombre de la moneda."""
        self.__nombre = _exigir_texto(valor, "El nombre de la moneda")

    @property
    def simbolo(self) -> str:
        """Devuelve el símbolo de la moneda."""
        return self.__simbolo

    @simbolo.setter
    def simbolo(self, valor: str) -> None:
        """Asigna el símbolo de la moneda."""
        self.__simbolo = _exigir_texto(valor, "El símbolo")

    def __str__(self) -> str:
        return f"[{self.id}] {self.codigo} - {self.nombre} ({self.simbolo})"


class TipoCotizacion(EntidadBase):
    """Tipo de cotización del dólar."""

    def __init__(self, id: int, nombre: str, descripcion: str) -> None:
        """Constructor.

        Args:
            id (int): Identificador.
            nombre (str): Nombre del tipo. Por ejemplo, Blue o MEP.
            descripcion (str): Descripción breve.
        """
        super().__init__(id)
        self.__nombre = ""
        self.__descripcion = ""
        self.nombre = nombre
        self.descripcion = descripcion

    @property
    def nombre(self) -> str:
        """Devuelve el nombre del tipo de cotización."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Asigna el nombre del tipo de cotización."""
        self.__nombre = _exigir_texto(valor, "El nombre del tipo de cotización")

    @property
    def descripcion(self) -> str:
        """Devuelve la descripción del tipo de cotización."""
        return self.__descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        """Asigna la descripción del tipo de cotización."""
        self.__descripcion = _exigir_texto(valor, "La descripción")

    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre}: {self.descripcion}"


class Libro(EntidadBase):
    """Título del catálogo de la librería."""

    def __init__(
        self,
        id: int,
        isbn: str,
        titulo: str,
        autor: str,
        editorial_id: int,
        genero_id: int,
        anio: int,
        paginas: int,
    ) -> None:
        """Constructor.

        Args:
            id (int): Identificador.
            isbn (str): Código de inventario del título.
            titulo (str): Título.
            autor (str): Autor.
            editorial_id (int): Id de la editorial.
            genero_id (int): Id del género.
            anio (int): Año de publicación.
            paginas (int): Cantidad de páginas.
        """
        super().__init__(id)
        self.__isbn = ""
        self.__titulo = ""
        self.__autor = ""
        self.__editorial_id = 0
        self.__genero_id = 0
        self.__anio = 0
        self.__paginas = 0
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.editorial_id = editorial_id
        self.genero_id = genero_id
        self.anio = anio
        self.paginas = paginas

    @property
    def isbn(self) -> str:
        """Devuelve el código de inventario."""
        return self.__isbn

    @isbn.setter
    def isbn(self, valor: str) -> None:
        """Asigna el código de inventario."""
        self.__isbn = _exigir_texto(valor, "El ISBN")

    @property
    def titulo(self) -> str:
        """Devuelve el título."""
        return self.__titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        """Asigna el título."""
        self.__titulo = _exigir_texto(valor, "El título")

    @property
    def autor(self) -> str:
        """Devuelve el autor."""
        return self.__autor

    @autor.setter
    def autor(self, valor: str) -> None:
        """Asigna el autor."""
        self.__autor = _exigir_texto(valor, "El autor")

    @property
    def editorial_id(self) -> int:
        """Devuelve el id de la editorial."""
        return self.__editorial_id

    @editorial_id.setter
    def editorial_id(self, valor: int) -> None:
        """Asigna el id de la editorial."""
        self.__editorial_id = _exigir_entero(
            valor, "La editorial", permitir_cero=False
        )

    @property
    def genero_id(self) -> int:
        """Devuelve el id del género."""
        return self.__genero_id

    @genero_id.setter
    def genero_id(self, valor: int) -> None:
        """Asigna el id del género."""
        self.__genero_id = _exigir_entero(
            valor, "El género", permitir_cero=False
        )

    @property
    def anio(self) -> int:
        """Devuelve el año de publicación."""
        return self.__anio

    @anio.setter
    def anio(self, valor: int) -> None:
        """Asigna el año de publicación."""
        anio = _exigir_entero(valor, "El año", permitir_cero=False)
        if anio < 1400 or anio > 2100:
            raise ValueError("El año debe estar entre 1400 y 2100.")
        self.__anio = anio

    @property
    def paginas(self) -> int:
        """Devuelve la cantidad de páginas."""
        return self.__paginas

    @paginas.setter
    def paginas(self, valor: int) -> None:
        """Asigna la cantidad de páginas."""
        self.__paginas = _exigir_entero(
            valor, "Las páginas", permitir_cero=False
        )

    def __str__(self) -> str:
        return (
            f"[{self.id}] {self.titulo} - {self.autor} "
            f"(ISBN {self.isbn}, {self.anio}, {self.paginas} pág.)"
        )


class Precio(EntidadBase):
    """Valor monetario de un libro en una moneda."""

    def __init__(
        self,
        id: int,
        libro_id: int,
        moneda_id: int,
        importe: float,
    ) -> None:
        """Constructor.

        Args:
            id (int): Identificador.
            libro_id (int): Id del libro.
            moneda_id (int): Id de la moneda.
            importe (float): Importe.
        """
        super().__init__(id)
        self.__libro_id = 0
        self.__moneda_id = 0
        self.__importe = 0.0
        self.libro_id = libro_id
        self.moneda_id = moneda_id
        self.importe = importe

    @property
    def libro_id(self) -> int:
        """Devuelve el id del libro."""
        return self.__libro_id

    @libro_id.setter
    def libro_id(self, valor: int) -> None:
        """Asigna el id del libro."""
        self.__libro_id = _exigir_entero(
            valor, "El libro", permitir_cero=False
        )

    @property
    def moneda_id(self) -> int:
        """Devuelve el id de la moneda."""
        return self.__moneda_id

    @moneda_id.setter
    def moneda_id(self, valor: int) -> None:
        """Asigna el id de la moneda."""
        self.__moneda_id = _exigir_entero(
            valor, "La moneda", permitir_cero=False
        )

    @property
    def importe(self) -> float:
        """Devuelve el importe."""
        return self.__importe

    @importe.setter
    def importe(self, valor: float) -> None:
        """Asigna el importe."""
        self.__importe = _exigir_importe(valor, "El importe")

    def __str__(self) -> str:
        return (
            f"[{self.id}] libro {self.libro_id} / moneda {self.moneda_id}: "
            f"{self.importe:.2f}"
        )


class Stock:
    """Cantidad disponible de un libro.

    La clave es el libro: hay un único stock por título.
    """

    def __init__(
        self,
        libro_id: int,
        cantidad: int,
        punto_reposicion: int,
    ) -> None:
        """Constructor.

        Args:
            libro_id (int): Id del libro.
            cantidad (int): Unidades disponibles.
            punto_reposicion (int): Cantidad a partir de la cual hay que reponer.
        """
        self.__libro_id = 0
        self.__cantidad = 0
        self.__punto_reposicion = 0
        self.libro_id = libro_id
        self.cantidad = cantidad
        self.punto_reposicion = punto_reposicion

    @property
    def libro_id(self) -> int:
        """Devuelve el id del libro."""
        return self.__libro_id

    @libro_id.setter
    def libro_id(self, valor: int) -> None:
        """Asigna el id del libro."""
        self.__libro_id = _exigir_entero(
            valor, "El libro", permitir_cero=False
        )

    @property
    def cantidad(self) -> int:
        """Devuelve las unidades disponibles."""
        return self.__cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        """Asigna las unidades disponibles."""
        self.__cantidad = _exigir_entero(
            valor, "La cantidad", permitir_cero=True
        )

    @property
    def punto_reposicion(self) -> int:
        """Devuelve el punto de reposición."""
        return self.__punto_reposicion

    @punto_reposicion.setter
    def punto_reposicion(self, valor: int) -> None:
        """Asigna el punto de reposición."""
        self.__punto_reposicion = _exigir_entero(
            valor, "El punto de reposición", permitir_cero=True
        )

    def __str__(self) -> str:
        texto = "1 unidad" if self.cantidad == 1 else f"{self.cantidad} unidades"
        return (
            f"Libro {self.libro_id}: {texto} "
            f"(reponer al llegar a {self.punto_reposicion})"
        )


class CotizacionDolar:
    """Cotización del dólar para un tipo y una fecha."""

    def __init__(
        self,
        tipo_cotizacion_id: int,
        fecha: date,
        compra: float,
        venta: float,
    ) -> None:
        """Constructor.

        Args:
            tipo_cotizacion_id (int): Id del tipo de cotización.
            fecha (date): Fecha de la cotización.
            compra (float): Valor de compra.
            venta (float): Valor de venta.
        """
        self.__tipo_cotizacion_id = 0
        self.__fecha = date(2026, 10, 1)
        self.__compra = 0.0
        self.__venta = 0.0
        self.tipo_cotizacion_id = tipo_cotizacion_id
        self.fecha = fecha
        self.compra = compra
        self.venta = venta

    @property
    def tipo_cotizacion_id(self) -> int:
        """Devuelve el id del tipo de cotización."""
        return self.__tipo_cotizacion_id

    @tipo_cotizacion_id.setter
    def tipo_cotizacion_id(self, valor: int) -> None:
        """Asigna el id del tipo de cotización."""
        self.__tipo_cotizacion_id = _exigir_entero(
            valor, "El tipo de cotización", permitir_cero=False
        )

    @property
    def fecha(self) -> date:
        """Devuelve la fecha de la cotización."""
        return self.__fecha

    @fecha.setter
    def fecha(self, valor: date) -> None:
        """Asigna la fecha de la cotización."""
        if type(valor) is not date:
            raise ValueError("La fecha debe ser un datetime.date.")
        self.__fecha = valor

    @property
    def compra(self) -> float:
        """Devuelve el valor de compra."""
        return self.__compra

    @compra.setter
    def compra(self, valor: float) -> None:
        """Asigna el valor de compra."""
        compra = _exigir_importe(valor, "La compra")
        if self.__venta and compra > self.__venta:
            raise ValueError("La compra no puede superar a la venta.")
        self.__compra = compra

    @property
    def venta(self) -> float:
        """Devuelve el valor de venta."""
        return self.__venta

    @venta.setter
    def venta(self, valor: float) -> None:
        """Asigna el valor de venta."""
        venta = _exigir_importe(valor, "La venta")
        if self.__compra and venta < self.__compra:
            raise ValueError("La venta no puede ser menor que la compra.")
        self.__venta = venta

    def __str__(self) -> str:
        return (
            f"Tipo {self.tipo_cotizacion_id} @ {self.fecha.isoformat()}: "
            f"compra {self.compra:.2f} / venta {self.venta:.2f}"
        )
