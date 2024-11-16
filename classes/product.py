import random

class Product:
    def __init__(self, name, quantity, unit, total, date):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.total = total
        self.price = self.calculate_price()
        self.date = date

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

    def calculate_price(self):
        return self.total/self.quantity

    def calculate_total(self):
        return self.quantity*self.price

    # Setters
    def set_name(self, name):
        if not name:
            raise ValueError("El nombre no puede estar vacío.")
        self.name = name

    def set_quantity(self, quantity):
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        self.quantity = quantity
        self.price = self.calculate_price()

    def set_unit(self, unit):
        if not unit:
            raise ValueError("La unidad de medida no puede estar vacía.")
        self.unit = unit

    def set_price(self, price):
        if price < 0:
            raise ValueError("El precio no puede ser negativo.")
        self.price = price
        self.total = self.calculate_total()

    def set_total(self, total):
        if total < 0:
            raise ValueError("El total no puede ser negativo.")
        self.total = total
        self.price = self.calculate_price()

    def set_date(self, date):
        self.date = date

    def get_db_values(self):
        return [self.name, self.quantity, self.unit, self.price, self.total, self.date]

    def __str__(self):
        """Representación en string del producto."""
        return (f"Nombre: {self.get_name()}\n"
                f"Cantidad: {self.get_quantity()}\n"
                f"Unidad de Medida: {self.get_unit()}\n"
                f"Precio Unitario: {self.get_price()}\n"
                f"Total: {self.get_total()}\n"
                f"Fecha: {self.get_date()}")
