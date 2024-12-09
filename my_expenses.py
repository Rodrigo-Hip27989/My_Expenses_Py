import subprocess
import signal
import time
from datetime import datetime
import my_sqlconn as sqlc
import utils.various as utils
import utils.file_operations as fop
import utils.input_validations as valid
from models.product import Product
from models.path import Path

def handle_interrupt(sig, frame):
    raise KeyboardInterrupt

def warning_interrupt():
    subprocess.run(["clear"])
    print("\n\n\n\n    Interrupción detectada !!!\n\n    Volviendo al menú principal ...\n\n")
    time.sleep(1.2)

def choose_option_in_menu(title, menu_options, clear="clear"):
    if clear.strip() != "no_clear":
        subprocess.run(["clear"])
    utils.draw_tittle_border(title)
    print("  0. Regresar")
    for idx, description in menu_options:
        print(f"  {idx}. {description}")
    max_option = len(menu_options)
    return valid.read_options_menu(0, max_option)

def choose_option_in_menu_import_export(title, menu_options, clear="clear"):
    if clear.strip() != "no_clear":
        subprocess.run(["clear"])
    utils.draw_tittle_border(title)
    print("  0. Regresar")
    for idx, (description, _, _, _) in enumerate(menu_options, 1):
        print(f"  {idx}. {description}")
    max_option = len(menu_options)
    return valid.read_options_menu(0, max_option)

def check_and_update_date_format(conn, table_products):
    rows = conn.fetch_all(f"SELECT id, date FROM {table_products}")
    found_wrong_rows = utils.check_formats_date(rows)
    if found_wrong_rows:
        update_wrong_date = valid.read_short_answer("¿Su tabla contiene fechas en formato incorrecto desea actualizarlas ahora?")
        if update_wrong_date.lower() in ['si', 's']:
            conn.update_formats_date(table_products, found_wrong_rows)
        else:
            input("\n   *** La ordenación no se aplicará correctamente ***\n")

def adjust_quantity_column(column):
    if column == "quantity":
        return sqlc.Database.convert_column_sql_quantity_to_float(column)
    return column

def create_query_for_sorting_products(option, columns, table_products):
    if option in range(1, 8):
        column = columns[option - 1]
        column = adjust_quantity_column(column)
        return f"SELECT * FROM {table_products} ORDER BY {column} ASC;"
    elif option in range(8, 14):
        column = columns[option - 8]
        column = adjust_quantity_column(column)
        return f"SELECT * FROM {table_products} ORDER BY category ASC, {column} ASC;"
    return None

def show_products_summary(conn, table_products):
    drop_view_query = "DROP VIEW IF EXISTS summary_products;"
    conn.execute_query(drop_view_query)
    query_create_view = f"""
        CREATE VIEW summary_products AS
        SELECT
            category,
            COUNT(*) AS num_items,
            ROUND(SUM(CASE WHEN total IS NOT NULL AND total != '' THEN total ELSE 0 END), 3) AS total_cost,
            ROUND(AVG(CASE WHEN total IS NOT NULL AND total != '' THEN total ELSE NULL END), 3) AS avg_cost,
            ROUND(MIN(CASE WHEN total IS NOT NULL AND total != '' THEN total ELSE NULL END), 3) AS min_cost,
            ROUND(MAX(CASE WHEN total IS NOT NULL AND total != '' THEN total ELSE NULL END), 3) AS max_cost,
            (SELECT name FROM {table_products} WHERE total IS NOT NULL AND total != '' AND category = p.category ORDER BY total DESC LIMIT 1) AS most_expensive,
            (SELECT name FROM {table_products} WHERE total IS NOT NULL AND total != '' AND category = p.category ORDER BY total ASC LIMIT 1) AS least_expensive
        FROM {table_products} p
        GROUP BY category
        ORDER BY category;
    """
    conn.execute_query(query_create_view)
    utils.display_formatted_table(conn, "summary_products")

def ask_for_product_details(date_ = "", cat = ""):
    name = valid.read_simple_text("  * Nombre: ")
    qty = valid.read_float_fraction_str("  * Cantidad: ")
    unit = valid.read_simple_text("  * Medida: ")
    total = valid.read_float("  * Total: ")
    date_ = datetime.now().strftime("%Y-%m-%d") if date_.strip() == "" else date_
    cat = Product.get_unspecified_category() if cat.strip() == "" else cat

    print(f"  * Fecha (Año-Mes-Día): {date_}")
    change_date = valid.read_short_answer("¿Desea cambiar la fecha?")
    if(change_date.lower() in ['si', 's']):
        date_ = valid.read_date("  * Fecha (Año-Mes-Día): ")

    print(f"  * Categoria: {cat}")
    change_category = valid.read_short_answer("¿Desea asignar/cambiar la categoria?")
    if(change_category.lower() in ['si', 's']):
        cat = valid.read_simple_text("  * Categoria: ")

    return Product(name=name, quantity=qty, unit=unit, total=total, date=date_, category=cat)

def register_multiple_products(conn):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Registrar nuevo producto")
        conn.insert_product(ask_for_product_details())
        stop = valid.read_short_answer("¿Desea agregar otro producto?")
        if(stop.lower() in ['no', 'n']):
            break

def update_product(conn, table_products):
    utils.display_formatted_table(conn, table_products)
    utils.draw_tittle_border(f"Actualizando detalles del producto")
    id_prod = valid.read_integer("\n  * Ingrese el ID: ")
    prod_obj = conn.find_product(table_products, "ID", id_prod)
    if(prod_obj is not None):
        print(f"\n  [ DATOS ACTUALES ]\n")
        print(prod_obj.__str__())
        print(f"\n  [ NUEVOS DATOS ]\n")
        conn.update_product(table_products, id_prod, ask_for_product_details(prod_obj.date, prod_obj.category), True)

def handle_product_deletion_menu(conn, table_products):
    while True:
        utils.display_formatted_table(conn, table_products)
        menu_options = (
            (1, "Usando su ID"),
            (2, "Todos con el NOMBRE"),
            (3, "Todos con la FECHA")
        )
        option = choose_option_in_menu("Eliminar un producto", menu_options, "no_clear")
        if(option == 0):
            break
        elif(option == 1):
            id_product = valid.read_integer("\n  * Ingrese el ID: ")
            conn.delete_item(table_products, "ID", id_product)
        elif(option == 2):
            name_product = valid.read_simple_text("\n  * Ingrese el NOMBRE: ")
            conn.delete_item(table_products, "NAME", name_product)
        elif(option == 3):
            date_product = valid.read_date("\n  * Ingrese el FECHA: ")
            conn.delete_item(table_products, "DATE", date_product)
        if conn.is_table_empty(table_products):
            break

def ask_for_path_to_insert(is_first_entry):
    new_path = valid.read_paths_linux("\n  * Ruta: ")
    if(is_first_entry):
        return Path(path=new_path, is_export=1, is_import=1)
    else:
        is_exp = valid.read_short_answer("¿Establecer como ruta de exportación?").lower() in ['si', 's']
        is_imp = valid.read_short_answer("¿Establecer como ruta de importación?").lower() in ['si', 's']
        return Path(path=new_path, is_export=is_exp, is_import=is_imp)

def register_multiple_paths(conn, table_paths):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Registrar nueva ruta")
        is_first_entry = conn.is_table_empty(table_paths)
        conn.insert_path(table_paths, ask_for_path_to_insert(is_first_entry), is_first_entry)
        stop = valid.read_short_answer("¿Desea agregar otra ruta?")
        if(stop.lower() in ['no', 'n']):
            break

def update_path(conn, table_paths):
    utils.display_formatted_table(conn, table_paths)
    utils.draw_tittle_border(f"Actualizando ruta")
    id_path = valid.read_integer("\n  * Ingrese el ID: ")
    path_obj = conn.find_path(table_paths, "ID", id_path)
    if(path_obj is not None):
        is_first_entry = conn.get_num_rows_table(table_paths) == 1
        conn.update_path(table_paths, id_path, ask_for_path_to_insert(is_first_entry), is_first_entry, True)

def delete_multiple_paths(conn, table_paths):
    while True:
        utils.display_formatted_table(conn, table_paths)
        utils.draw_tittle_border("Eliminar una ruta")
        id_path = valid.read_integer("\n  * Ingrese el ID: ")
        path_obj = conn.find_path(table_paths, "ID", id_path)
        if(path_obj is not None):
            if(path_obj.is_export == 1 or path_obj.is_import == 1):
                print(f"\n  *** No es posible eliminar una ruta csv en uso***")
            else:
                conn.delete_item(table_paths, "ID", id_path)
        if not conn.is_table_empty(table_paths):
            stop = valid.read_short_answer("¿Desea eliminar otra ruta?")
            if(stop.lower() in ['no', 'n']):
                break
        else:
            break

def handle_delete_tables_menu(conn, table_products, table_paths):
    menu_options = (
        (1, "Eliminar datos de productos"),
        (2, "Eliminar datos de rutas"),
        (3, "Eliminar datos de todas las tablas")
    )
    option = choose_option_in_menu("Eliminando datos de tablas", menu_options)
    if(option != 0):
        if(option == 1):
            c = conn.execute_query(f"DELETE FROM {table_products}")
            conn.confirm_transaction_database(c)
            c = conn.execute_query(f"UPDATE sqlite_sequence SET seq = 0 WHERE name = '{table_products}'")
            conn.commit(c)
        elif(option == 2):
            c = conn.execute_query(f"DELETE FROM {table_paths}")
            conn.confirm_transaction_database(c)
            c = conn.execute_query(f"UPDATE sqlite_sequence SET seq = 0 WHERE name = '{table_paths}'")
            conn.commit(c)
        elif(option == 3):
            print("\n  *** Esta acción no puede deshacerse ***\n")
            delete_db = valid.read_answer_continue()
            if(delete_db.lower() in ['si', 's']):
                conn.disconnect()
                conn.delete_database()
                conn = sqlc.Database()
            else:
                print("\n   >>> Operacion cancelada")
    return conn

def handle_paths_menu(conn, table_paths):
    while True:
        menu_options = (
            (1, "Registrar nueva ruta"),
            (2, "Visualizar rutas guardadas"),
            (3, "Actualizar ruta"),
            (4, "Eliminar una ruta")
        )
        option = choose_option_in_menu("Administrar rutas", menu_options)
        if(option == 0):
            break
        elif(option == 1):
            register_multiple_paths(conn, table_paths)
        elif(option == 2):
            conn.validate_table_not_empty("No hay datos para mostrar...", utils.display_formatted_table, table_paths)
        elif(option == 3):
            conn.validate_table_not_empty("No hay datos para actualizar...", update_path, table_paths)
        elif(option == 4):
            conn.validate_table_not_empty("No hay datos para eliminar...", delete_multiple_paths, table_paths)

def update_data_to_correct_format(conn, table_products):
    query = f"SELECT id, name, quantity, unit, price, total, date, category FROM {table_products};"
    tbl_rows = conn.fetch_all(query)
    for row in tbl_rows:
        product_obj = Product(
            name=row['name'],
            quantity=row['quantity'],
            unit=row['unit'],
            price=row['price'],
            total=row['total'],
            date=row['date'],
            category=row['category']
        )
        conn.update_product(table_products, row['id'], product_obj)
    return conn

def view_sorted_product_list(conn, table_products):
    columns = conn.get_headers(table_products)[1:]

    menu_options = []
    menu_options.extend((i + 1, f"Ordenar por {column.upper()}") for i, column in enumerate(columns))
    menu_options.extend((i + 8, f"Ordenar por CATEGORY y {columns[i].upper()}") for i in range(len(columns) - 1))

    while True:
        option = choose_option_in_menu("Ordenamiento de productos", menu_options)
        if option == 0:
            break
        query = create_query_for_sorting_products(option, columns, table_products)
        if query:
            if option in [6, 13]:
                check_and_update_date_format(conn, table_products)
            conn.validate_table_not_empty("No hay datos para mostrar...", utils.display_formatted_table, table_products, query)

def handle_products_menu(conn, table_products):
    while True:
        menu_options = (
            (1, "Registrar un producto"),
            (2, "Ver lista de productos"),
            (3, "Actualizar un producto"),
            (4, "Eliminar un producto"),
            (5, "Ver resumen de los productos"),
            (6, "Ver lista de productos ordenada"),
            (7, "Actualizar el formato de los datos")
        )
        option = choose_option_in_menu("Administrar productos", menu_options)
        if(option == 0):
            break
        elif(option == 1):
            register_multiple_products(conn)
        elif(option == 2):
            conn.validate_table_not_empty("No hay datos para mostrar...", utils.display_formatted_table, table_products)
        elif(option == 3):
            conn.validate_table_not_empty("No hay datos para actualizar...", update_product, table_products)
        elif(option == 4):
            conn.validate_table_not_empty("No hay datos para eliminar...", handle_product_deletion_menu, table_products)
        elif(option == 5):
            conn.validate_table_not_empty("No hay productos del cual ver resumen...", show_products_summary, table_products)
        elif(option == 6):
            conn.validate_table_not_empty("No hay datos para mostrar...", view_sorted_product_list, table_products)
        elif(option == 7):
            conn.validate_table_not_empty("No hay datos para actualizar...", update_data_to_correct_format, table_products)

def handle_export_import_data_menu(conn, table_paths, table_names):
    export_path = conn.find_path(table_paths, "is_export", 1)
    import_path = conn.find_path(table_paths, "is_import", 1)

    menu_options = []

    if export_path is not None:
        menu_options.extend((f"Exportar {table} como CSV", fop.export_table_to_csv_default, table, export_path) for table in table_names)

    if import_path is not None:
        menu_options.extend((f"Importar {table} desde CSV", fop.import_table_from_csv_default, table, import_path) for table in table_names)

    total_options = len(menu_options)

    while True:
        option = choose_option_in_menu_import_export("Opciones de exportación e importación", menu_options)
        if option == 0:
            break
        elif 1 <= option <= total_options:
            _, action, table, path = menu_options[option - 1]
            action(conn, table, path)

def main():
    table_products = "products"
    table_paths = "paths"
    conn = sqlc.Database()
    signal.signal(signal.SIGINT, handle_interrupt)
    while True:
        menu_options = (
            (1, "Administrar tabla de productos"),
            (2, "Administrar tabla de rutas"),
            (3, "Exportar/Importar datos"),
            (4, "Eliminar datos de tablas")
        )
        try:
            option = choose_option_in_menu("Administrar datos", menu_options)
            if(option == 0):
                break
            elif(option == 1):
                handle_products_menu(conn, table_products)
            elif(option == 2):
                handle_paths_menu(conn, table_paths)
            elif(option == 3):
                conn.validate_table_not_empty("No hay rutas guardadas", handle_export_import_data_menu, table_paths, [table_paths, table_products])
            elif(option == 4):
                handle_delete_tables_menu(conn, table_products, table_paths)
        except (KeyboardInterrupt, EOFError):
            warning_interrupt()
    conn.disconnect()

if __name__ == "__main__":
    main()
