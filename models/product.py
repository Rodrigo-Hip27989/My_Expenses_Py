import utils.various as utils
from fractions import Fraction
from utils.input_validations import convert_to_number as str_to_num
from utils.input_validations import validate_float_fraction_str as validate_float_fraction

class Product:
    def __init__(self, name="", quantity="", unit="", price=None, total=None, date="", category=""):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.date = date
        self.category = category
        if (total is not None) and isinstance(total, float):
            self.total = total
            self._price = self.calculate_price(self.quantity, total)
        elif (price is not None) and isinstance(price, float):
            self.price = price
            self._total = self.calculate_total(self.quantity, price)
        else:
            self._total = Product.get_unspecified_total()
            self._price = Product.get_unspecified_price()

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
        return "Item"

    @staticmethod
    def get_unspecified_quantity():
        return "0"

    @staticmethod
    def get_unspecified_unit():
        return "Units"

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
    def calculate_price(qty, total):
        return round(float(str_to_num(total))/float(str_to_num(qty)), 2) if float(str_to_num(qty)) != 0 else 0

    @staticmethod
    def calculate_total(qty, price):
        return round(float(str_to_num(price))*float(str_to_num(qty)), 2)

    @name.setter
    def name(self, name):
        self._name = f"{name.strip().title()}" if name.strip() else Product.get_unspecified_name()

    @quantity.setter
    def quantity(self, quantity=""):
        quantity = str(quantity).strip()
        if quantity:
            if (validate_float_fraction(quantity)):
                converted_quantity = str_to_num(quantity)

                if isinstance(converted_quantity, Fraction):
                    self._quantity = str(converted_quantity)
                elif isinstance(converted_quantity, float) and converted_quantity.is_integer():
                    self._quantity = f"{int(converted_quantity)}"
                else:
                    self._quantity = f"{converted_quantity}"
            else:
                self._quantity = Product.get_unspecified_quantity()
        else:
            self._quantity = Product.get_unspecified_quantity()

    @unit.setter
    def unit(self, unit=""):
        self._unit = f"{unit.strip().lower()}" if unit.strip() else Product.get_unspecified_unit()

    @price.setter
    def price(self, price):
        if (price != None) and (price < 0):
            raise ValueError("El precio no puede ser negativo.")
        self._price = round(price, 2)

    @total.setter
    def total(self, total):
        if (total != None) and (total < 0):
            raise ValueError("El total no puede ser negativo.")
        self._total = round(total, 2)

    @date.setter
    def date(self, date=""):
        self._date = utils.convert_ddmmyyyy_to_iso8601(date.strip()) if date.strip() else Product.get_unspecified_date()

    @category.setter
    def category(self, category=""):
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
