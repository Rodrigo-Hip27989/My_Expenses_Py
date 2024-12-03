import my_utils as utils

class Product:
    def __init__(self, name="", quantity="", unit="", price=None, total=None, date="", category=""):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.date = date
        self.category = category
        if (price is not None) and isinstance(price, float):
            self._price = price
            self._total = self.calculate_total(self._quantity, price)
        elif (total is not None) and isinstance(total, float):
            self._total = total
            self._price = self.calculate_price(self._quantity, total)
        else:
            self.quantity = Product.get_unspecified_quantity()
            self._price = Product.get_unspecified_price()
            self._total = Product.get_unspecified_total()

    @property
    def name(self):
        return self._name

    @property
    def quantity(self):
        return self._quantity

    @property
    def unit(self):
        return self._unit

    @property
    def price(self):
        return self._price

    @property
    def total(self):
        return self._total

    @property
    def date(self):
        return self._date

    @property
    def category(self):
        return self._category

    @staticmethod
    def get_unspecified_name():
        return "ITEM"

    @staticmethod
    def get_unspecified_quantity():
        return "1.0"

    @staticmethod
    def get_unspecified_unit():
        return "UNITS"

    @staticmethod
    def get_unspecified_price():
        return 0

    @staticmethod
    def get_unspecified_total():
        return 0

    @staticmethod
    def get_unspecified_date():
        return "0001-01-01"

    @staticmethod
    def get_unspecified_category():
        return "Unspecified"

    @staticmethod
    def calculate_price(quantity, total):
        return round(utils.convert_to_float(total)/utils.convert_to_float(quantity), 7)

    @staticmethod
    def calculate_total(quantity, price):
        return round(utils.convert_to_float(quantity)*utils.convert_to_float(price), 7)

    @name.setter
    def name(self, name):
        self._name = f"{name.strip().title()}" if name.strip() else Product.get_unspecified_name()

    @quantity.setter
    def quantity(self, quantity):
        self._quantity = f"{quantity.strip()}" if quantity.strip() else Product.get_unspecified_quantity()

    @unit.setter
    def unit(self, unit):
        self._unit = f"{unit.strip().upper()}" if unit.strip() else Product.get_unspecified_unit()

    @price.setter
    def price(self, price):
        if price < 0:
            raise ValueError("El precio no puede ser negativo.")
        self._price = price

    @total.setter
    def total(self, total):
        if total < 0:
            raise ValueError("El total no puede ser negativo.")
        self._total = total

    @date.setter
    def date(self, date):
        self._date = utils.convert_ddmmyyyy_to_iso8601(date.strip()) if date.strip() else Product.get_unspecified_date()

    @category.setter
    def category(self, category):
        self._category = f"{category.strip().title()}" if category.strip() else Product.get_unspecified_category()

    def get_db_values(self):
        return [self._name, self._quantity, self._unit, self._price, self._total, self._date, self._category]

    def __str__(self):
        return (f"  - Nombre: {self._name}\n"
                f"  - Cantidad: {self._quantity}\n"
                f"  - Unidad de Medida: {self._unit}\n"
                f"  - Precio Unitario: {self._price}\n"
                f"  - Total: {self._total}\n"
                f"  - Fecha: {self._date}\n"
                f"  - Categoria: {self._category}")
