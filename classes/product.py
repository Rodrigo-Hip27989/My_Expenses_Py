import my_utils as utils

class Product:
    def __init__(self, name, quantity, unit, total, date, category=None):
        self.name = name.strip().title()
        self.quantity = quantity.strip()
        self.unit = unit.strip().upper()
        self.total = float(total)
        self.price = Product.calculate_price(self.quantity, self.total)
        self.date = date.strip()
        if((category is not None) and (category.strip() != "")):
            self.category = f"{category.strip().title()}"
        else:
            self.category = Product.get_unspecified_category_name()

    # Getters
    def get_name(self):
        return self.name

    def get_quantity(self):
        return self.quantity

    def get_unit(self):
        return self.unit

    def get_price(self):
        return self.price

    def get_total(self):
        return self.total

    def get_date(self):
        return self.date

    def get_category(self):
        return self.category

    @staticmethod
    def get_unspecified_unit():
        return "UNITS"

    @staticmethod
    def get_unspecified_date():
        return "0001-01-01"

    @staticmethod
    def get_unspecified_category_name():
        return "Unspecified"

    @staticmethod
    def calculate_price(quantity, total):
        return round(utils.convert_to_float(total)/utils.convert_to_float(quantity), 7)

    @staticmethod
    def calculate_total(quantity, price):
        return round(utils.convert_to_float(quantity)*utils.convert_to_float(price), 7)

    # Setters
    def set_name(self, name):
        if not name:
            raise ValueError("El nombre no puede estar vacío.")
        self.name = name

    def set_quantity(self, quantity):
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        self.quantity = quantity
        self.price = Product.calculate_price(self.quantity, self.total)

    def set_unit(self, unit):
        if not unit:
            raise ValueError("La unidad de medida no puede estar vacía.")
        self.unit = unit

    def set_price(self, price):
        if price < 0:
            raise ValueError("El precio no puede ser negativo.")
        self.price = price
        self.total = Product.calculate_total(self.quantity, self.price)

    def set_total(self, total):
        if total < 0:
            raise ValueError("El total no puede ser negativo.")
        self.total = total
        self.price = Product.calculate_price(self.quantity, self.total)

    def set_date(self, date):
        self.date = date

    def set_category(self, category):
        self.category = category

    def get_db_values(self):
        return [self.get_name(), self.get_quantity(), self.get_unit(), self.get_price(), self.get_total(), self.get_date(), self.get_category()]

    def __str__(self):
        return (f"Nombre: {self.get_name()}\n"
                f"Cantidad: {self.get_quantity()}\n"
                f"Unidad de Medida: {self.get_unit()}\n"
                f"Precio Unitario: {self.get_price()}\n"
                f"Total: {self.get_total()}\n"
                f"Fecha: {self.get_date()}\n"
                f"Categoria: {self.get_category()}")
