import subprocess
import signal
import time
import re
from datetime import datetime
import my_sqlconn as sqlc
import my_utils as utils
import my_file_operations as fop
from classes.product import Product
from classes.path import Path

def handle_interrupt(sig, frame):
    raise KeyboardInterrupt

def show_products_summary(conn, table_products):
    query = f"""
        SELECT
            category,
            COUNT(*) AS total_products,
            SUM(CASE WHEN total IS NOT NULL AND total != '' THEN total ELSE 0 END) AS total_cost,
            AVG(CASE WHEN total IS NOT NULL AND total != '' THEN total ELSE NULL END) AS avg_cost,
            MIN(CASE WHEN total IS NOT NULL AND total != '' THEN total ELSE NULL END) AS min_cost,
            MAX(CASE WHEN total IS NOT NULL AND total != '' THEN total ELSE NULL END) AS max_cost,
            (SELECT name FROM {table_products} WHERE total IS NOT NULL AND total != '' AND category = p.category ORDER BY total DESC LIMIT 1) AS most_expensive,
            (SELECT name FROM {table_products} WHERE total IS NOT NULL AND total != '' AND category = p.category ORDER BY total ASC LIMIT 1) AS least_expensive
        FROM {table_products} p
        GROUP BY category
        ORDER BY category;
    """
    result = conn.fetch_all(query)

    if result:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Resumen de los productos")

        for row in result:
            category, total_products, total_cost, avg_cost, min_cost, max_cost, most_expensive, least_expensive = row
            if(category is None or category.strip() == ""):
                category = Product.get_unspecified_category()
            utils.draw_subtitle_border(f"Categoría: {category}")
            print(f"  - Num. Productos: {total_products}")
            print(f"  - Costo Total: ${total_cost:,.3f}")
            print(f"  - Costo Promedio: ${avg_cost:,.3f}")
            print(f"  - Producto más barato: {least_expensive}")
            print(f"  - Costo (mínimo): ${min_cost:,.3f}")
            print(f"  - Producto más caro: {most_expensive}")
            print(f"  - Costo (máximo): ${max_cost:,.3f}\n")
    else:
        print("\n    No hay datos disponibles en la tabla de productos.")

def ask_for_product_details(date_ = None):
    name = utils.read_input_simple_text("  * Nombre: ")
    quantity = utils.read_input_float_fraction_str("  * Cantidad: ")
    unit = utils.read_input_simple_text("  * Medida: ")
    total = utils.read_input_float("  * Total: ")
    if(date_ is None or date_.strip() == ""):
        date_ = datetime.now().strftime("%Y-%m-%d")
    print(f"  * Fecha (Año-Mes-Día): {date_}")
    change_date = utils.read_input_yes_no("¿Desea cambiar la fecha?")
    if(change_date.lower() in ['si', 's']):
        while True:
            try:
                date_ = utils.read_input_date("  * Fecha (Año-Mes-Día): ")
                date_obj = datetime.strptime(date_, "%Y-%m-%d")
                break
            except ValueError:
                print("\n   * La fecha proporcionada no es válida en el calendario.\n")
    set_category = utils.read_input_yes_no("¿Desea asignar a una categoria?")
    if(set_category.lower() in ['si', 's']):
        category = utils.read_input_simple_text("  * Categoria: ")
    else:
        category = Product.get_unspecified_category()
    return Product(name=name, quantity=quantity, unit=unit, total=total, date=date_, category=category)

def register_multiple_products(conn):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Registrar nuevo producto")
        conn.insert_product(ask_for_product_details())
        stop = utils.read_input_yes_no("¿Desea agregar otro producto?")
        if(stop.lower() in ['no', 'n']):
            break

def update_product(conn, table_products):
    utils.display_formatted_table(conn, table_products)
    utils.draw_tittle_border(f"Actualizando detalles del producto")
    id_prod = utils.read_input_integer("\n  * Ingrese el ID: ")
    prod_obj = conn.find_product(table_products, "ID", id_prod)
    if(prod_obj is not None):
        print(f"\n  [ DATOS ACTUALES ]\n")
        print(prod_obj.__str__())
        print(f"\n  [ NUEVOS DATOS ]\n")
        conn.update_product(table_products, id_prod, ask_for_product_details(prod_obj.date), True)
    input("\n   >>> Presione ENTER para continuar <<<")

def handle_product_deletion_menu(conn, table_products):
    while True:
        utils.display_formatted_table(conn, table_products)
        utils.draw_tittle_border("Eliminar un producto")
        print("  0. Regresar")
        print("  1. Usando su ID")
        print("  2. Todos con el NOMBRE")
        print("  3. Todos con la FECHA")
        option = utils.read_input_options_menu(0, 3)
        if(option == 0):
            break
        elif(option == 1):
            id_product = utils.read_input_integer("\n  * Ingrese el ID: ")
            conn.delete_item(table_products, "ID", id_product)
        elif(option == 2):
            name_product = utils.read_input_simple_text("\n  * Ingrese el NOMBRE: ")
            conn.delete_item(table_products, "NAME", name_product)
        elif(option == 3):
            date_product = utils.read_input_date("\n  * Ingrese el FECHA: ")
            conn.delete_item(table_products, "DATE", date_product)
        if conn.is_table_empty(table_products):
            break

def ask_for_path_to_insert(is_first_entry):
    new_path = utils.read_input_paths_linux("  * Ruta: ")
    if(is_first_entry):
        return Path(path=new_path, is_export=1, is_import=1)
    else:
        is_exp = utils.read_input_yes_no("¿Establecer como ruta de exportación?").lower() in ['si', 's']
        is_imp = utils.read_input_yes_no("¿Establecer como ruta de importación?").lower() in ['si', 's']
        return Path(path=new_path, is_export=is_exp, is_import=is_imp)

def register_multiple_paths(conn, table_paths):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Registrar nueva ruta")
        is_first_entry = conn.is_table_empty(table_paths)
        conn.insert_path(table_paths, ask_for_path_to_insert(is_first_entry), is_first_entry)
        stop = utils.read_input_yes_no("¿Desea agregar otra ruta?")
        if(stop.lower() in ['no', 'n']):
            break

def update_path(conn, table_paths, field):
    utils.display_formatted_table(conn, table_paths)
    type_update=""
    if(field == "is_export"):
        type_update="EXPORTACIÓN"
    elif(field == "is_import"):
        type_update="IMPORTACIÓN"
    else:
        raise ValueError(f"Campo desconocido: {field}")
    utils.draw_tittle_border(f"Actualizando ruta de {type_update}")
    id_path = utils.read_input_integer("\n  * Ingrese el ID: ")
    path_obj = conn.find_path(table_paths, "ID", id_path)
    if(path_obj is not None):
        conn.update_path(table_paths, id_path, field)

def delete_multiple_paths(conn, table_paths):
    while True:
        utils.display_formatted_table(conn, table_paths)
        utils.draw_tittle_border("Eliminar una ruta")
        id_path = utils.read_input_integer("\n  * Ingrese el ID: ")
        path_obj = conn.find_path(table_paths, "ID", id_path)
        if(path_obj is not None):
            if(path_obj.is_export == 1 or path_obj.is_import == 1):
                print(f"\n  *** No es posible eliminar una ruta csv en uso***")
            else:
                conn.delete_item(table_paths, "ID", id_path)
        if not conn.is_table_empty(table_paths):
            stop = utils.read_input_yes_no("¿Desea eliminar otra ruta?")
            if(stop.lower() in ['no', 'n']):
                break
        else:
            break

def check_formats_date(conn, table_name):
    regex_iso8601 = r'^\d{4}-\d{2}-\d{2}$'
    rows = conn.fetch_all(f"SELECT id, date FROM {table_name}")
    wrong_rows = []
    for row in rows:
        id_, date_ = row
        if not re.match(regex_iso8601, date_):
            wrong_rows.append({'id': id_, 'date': date_})
    return wrong_rows

def update_formats_date(conn, table_name, wrong_rows):
    for row in wrong_rows:
        id_ = row['id']
        original_date = row['date']
        normalized_date = utils.convert_ddmmyyyy_to_iso8601(original_date)
        c = conn.execute_query(f"UPDATE {table_name} SET date = ? WHERE id = ?", (normalized_date, id_))
        conn.commit(c)
    return conn

def handle_delete_tables_menu(conn, table_products, table_paths):
    subprocess.run(["clear"])
    utils.draw_tittle_border("Eliminando datos de tablas")
    print("   0. Regresar")
    print("   1. Eliminar datos de productos")
    print("   2. Eliminar datos de rutas")
    print("   3. Eliminar datos de todas las tablas")
    option = utils.read_input_options_menu(0, 3)
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
            delete_db = utils.read_input_continue_confirmation()
            if(delete_db.lower() in ['si', 's']):
                conn.disconnect()
                conn.delete_database()
                conn = sqlc.Database()
            else:
                print("\n   >>> Operacion cancelada")
    return conn

def handle_paths_menu(conn, table_paths):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Administrar rutas")
        print("  0. Regresar")
        print("  1. Visualizar rutas guardadas")
        print("  2. Registrar nueva ruta")
        print("  3. Eliminar una ruta")
        print("  4. Actualizar ruta de exportación")
        print("  5. Actualizar ruta de importación")
        option = utils.read_input_options_menu(0, 5)
        if(option == 0):
            break
        elif(option == 1):
            conn.validate_table_not_empty("No hay datos para mostrar...", utils.display_formatted_table, table_paths)
            input("\n  >>> Presione ENTER para continuar <<<")
        elif(option == 2):
            register_multiple_paths(conn, table_paths)
        elif(option == 3):
            conn.validate_table_not_empty("No hay datos para eliminar...", delete_multiple_paths, table_paths)
        elif(option == 4):
            conn.validate_table_not_empty("No hay datos para actualizar...", update_path, table_paths, "is_export")
        elif(option == 5):
            conn.validate_table_not_empty("No hay datos para actualizar...", update_path, table_paths, "is_import")
        if option in range(4,6):
            time.sleep(1.5)

def update_data_to_correct_format(conn, table_products):
    query = f"SELECT id, name, quantity, unit, price, total, date, category FROM {table_products};"
    tbl_rows = conn.fetch_all(query)
    for row in tbl_rows:
        id_, name_, quantity_, unit_, price_, total_, date_, category_ = row
        product_obj = Product(name=name_, quantity=quantity_, unit=unit_, price=price_, total=total_, date=date_, category=category_)
        conn.update_product(table_products, id_, product_obj)
    return conn

def view_sorted_product_list(conn, table_products):
    columns = conn.get_headers(table_products)[1:]
    menu_options = [(0, "Regresar")]

    for index, column in enumerate(columns, start=1):
        menu_options.append((index, f"Ver lista en orden por {column.upper()}"))

    for i, column in enumerate(columns[:-1]):
        menu_options.append((i + 8, f"Ver lista en orden por CATEGORY y {columns[i].upper()}"))

    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Ordenamiento de productos")

        for option, description in menu_options:
            print(f"  {option}. {description}")

        option = utils.read_input_options_menu(0, 13)

        if option == 0:
            break

        if option in range(1, 8):
            column = columns[option - 1]
            if column == "quantity":
                column = utils.convert_column_sql_quantity_to_float(column)
            query = f"SELECT * FROM {table_products} ORDER BY {column} ASC;"

        elif option in range(8, 14):
            column = columns[option - 8]
            if column == "quantity":
                column = utils.convert_column_sql_quantity_to_float(column)
            query = f"SELECT * FROM {table_products} ORDER BY category ASC, {column} ASC;"

        if option in [6, 13]:
            found_wrong_rows = check_formats_date(conn, table_products)
            if found_wrong_rows:
                update_wrong_date = utils.read_input_yes_no("¿Su tabla contiene fechas en formato incorrecto desea actualizarlas ahora?")
                if update_wrong_date.lower() in ['si', 's']:
                    update_formats_date(conn, table_products, found_wrong_rows)
                else:
                    input("\n   *** La ordenación no se aplicará correctamente ***\n")

        conn.validate_table_not_empty("No hay datos para mostrar...", utils.display_formatted_table, table_products, query)
        input("\n   >>> Presione ENTER para continuar <<<")

def handle_products_menu(conn, table_products):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Tabla productos")
        print("  0. Salir")
        print("  1. Ver resumen de los productos")
        print("  2. Registrar un producto")
        print("  3. Eliminar un producto")
        print("  4. Actualizar un producto")
        print("  5. Actualizar el formato de todos los datos")
        print("  6. Ver lista de productos")
        print("  7. Ver lista de productos ordenada")
        option = utils.read_input_options_menu(0, 7)
        if(option == 0):
            break
        elif(option == 1):
            conn.validate_table_not_empty("No hay productos del cual ver resumen...", show_products_summary, table_products)
            input("\n   >>> Presione ENTER para continuar <<<")
        elif(option == 2):
            register_multiple_products(conn)
        elif(option == 3):
            conn.validate_table_not_empty("No hay datos para eliminar...", handle_product_deletion_menu, table_products)
            time.sleep(0.7)
        elif(option == 4):
            conn.validate_table_not_empty("No hay datos para actualizar...", update_product, table_products)
        elif(option == 5):
            conn.validate_table_not_empty("No hay datos para actualizar...", update_data_to_correct_format, table_products)
            input("\n   >>> Actualización completada <<<")
        elif(option == 6):
            conn.validate_table_not_empty("No hay datos para mostrar...", utils.display_formatted_table, table_products)
            input("\n   >>> Presione ENTER para continuar <<<")
        elif(option == 7):
            conn.validate_table_not_empty("No hay datos para mostrar...", view_sorted_product_list, table_products)

def handle_export_import_data_menu(conn, table_names):
    table_paths = table_names[0]
    if(conn.is_table_empty(table_paths)):
        print(f"\n      No hay rutas guardas!!")
        input("\n   >>> Presione ENTER para continuar <<<")
        return

    export_path = conn.find_path(table_paths, "is_export", 1)
    import_path = conn.find_path(table_paths, "is_import", 1)
    if(export_path is None or import_path is None):
        print(f"\n      No hay rutas de exportación y/o importación configuradas!!")
        input("\n   >>> Presione ENTER para continuar <<<")
        return

    menu_options = []
    for table in (t.upper() for t in table_names):
        menu_options.append((f"Exportar {table} como CSV", fop.export_table_to_csv_default, table, export_path))
        menu_options.append((f"Importar {table} desde CSV", fop.import_table_from_csv_default, table, import_path))
    total_options = len(menu_options)

    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Opciones de exportacion/importación")
        print("  0. Salir")
        for idx, (description, _, _, _) in enumerate(menu_options, 1):
            print(f"  {idx}. {description}")
        option = utils.read_input_options_menu(0, total_options)
        if option == 0:
            break
        elif 1 <= option <= total_options:
            description, action, table, path = menu_options[option - 1]
            action(conn, table, path)
        input("\n   >>> Presione ENTER para continuar <<<")

def main():
    table_products = "products"
    table_paths = "paths"
    conn = sqlc.Database()
    signal.signal(signal.SIGINT, handle_interrupt)
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Resgistrar gastos de productos")
        print("  0. Salir")
        print("  1. Administrar tabla de productos")
        print("  2. Administrar tabla de rutas")
        print("  3. Exportar/Importar datos")
        print("  4. Eliminar datos de tablas")
        try:
            option = utils.read_input_options_menu(0, 4)
            if(option == 0):
                break
            elif(option == 1):
                handle_products_menu(conn, table_products)
            elif(option == 2):
                handle_paths_menu(conn, table_paths)
            elif(option == 3):
                handle_export_import_data_menu(conn, [table_paths, table_products])
            elif(option == 4):
                conn = handle_delete_tables_menu(conn, table_products, table_paths)
        except (KeyboardInterrupt, EOFError):
            subprocess.run(["clear"])
            print("\n\n\n\n    Interrupción detectada !!!\n\n    Volviendo al menú principal ...\n\n")
            time.sleep(1.3)
    conn.disconnect()

if __name__ == "__main__":
    main()
