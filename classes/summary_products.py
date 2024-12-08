from classes.product import Product

class SummaryProducts:
    def __init__(self, category, total_products, total_cost, avg_cost, min_cost, max_cost, most_expensive, least_expensive):
        self.category = category or Product.get_unspecified_category()
        self.total_products = total_products
        self.total_cost = total_cost
        self.avg_cost = avg_cost
        self.min_cost = min_cost
        self.max_cost = max_cost
        self.most_expensive = most_expensive
        self.least_expensive = least_expensive

    def format_summary(self):
        return (
            f"  - Categoría: {self.category}\n"
            f"  - Num. Productos: {self.total_products}\n"
            f"  - Costo Total: ${self.total_cost:,.3f}\n"
            f"  - Costo Promedio: ${self.avg_cost:,.3f}\n"
            f"  - Producto más barato: {self.least_expensive}\n"
            f"  - Costo (mínimo): ${self.min_cost:,.3f}\n"
            f"  - Producto más caro: {self.most_expensive}\n"
            f"  - Costo (máximo): ${self.max_cost:,.3f}\n"
        )
