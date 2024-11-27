import os
import subprocess
import signal
import glob
import time
from datetime import datetime
import my_sqlconn as sqlc
import my_utils as utils
from classes.product import Product
from classes.path import Path

def initialize_db():
    db_path="sqlite_db"
    db_file="my_expenses.db"
    conn = sqlc.Database(db_path, db_file)
    conn.connect()
    conn.create_products_tbl()
    conn.create_paths_tbl()
    return conn

def handle_interrupt(sig, frame):
    raise KeyboardInterrupt

def find_files_by_extension(path, extension):
    expanded_path = os.path.expandvars(path)
    expanded_path = os.path.expanduser(expanded_path)
    final_expanded_path = os.path.abspath(expanded_path)
    if not os.path.exists(final_expanded_path):
        print(f"Error: La ruta '{path}' no existe.")
        return []
    if not os.path.isdir(final_expanded_path):
        print(f"Error: '{path}' no es un directorio válido.")
        return []
    pattern = os.path.join(final_expanded_path, f"*.{extension}")
    file_list = glob.glob(pattern)
    file_list_sorted = sorted(file_list, key=lambda x: os.path.getctime(x))
    return file_list_sorted

def select_file_from_list(file_list):
    subprocess.run(["clear"])
    utils.draw_tittle_border("Seleccione un archivo para importar")
    for i, file in enumerate(file_list, start=1):
        name_file = os.path.basename(file)
        print(f"   {i}. {name_file}")
    option = utils.read_input_options_menu(1, (len(file_list)))
    return option

def render_table_with_csv_memory(conn, table_name):
    subprocess.run(["clear"])
    print("\n")
    headers_table = conn.get_headers(f"{table_name}")
    headers_table = [header.upper() for header in headers_table]
    rows_table = conn.fetch_all(f"SELECT * FROM {table_name}")
    csv_data = utils.convert_table_to_in_memory_csv(headers_table, rows_table)
    formatted_data = utils.format_csv_using_column_command(csv_data)
    fully_formatted_table = utils.add_borders_and_margins_to_table(formatted_data)
    print(fully_formatted_table)

def show_products_summary(conn, table_products):
    query = f"""
        SELECT
            COUNT(*) AS total_products,
            SUM(total) AS total_cost,
            AVG(total) AS avg_cost,
            MIN(total) AS min_cost,
            MAX(total) AS max_cost,
            (SELECT name FROM {table_products} ORDER BY total DESC LIMIT 1) AS most_expensive,
            (SELECT name FROM {table_products} ORDER BY total ASC LIMIT 1) AS least_expensive
        FROM {table_products};
    """
    # Ejecutar la consulta
    result = conn.fetch_one(query)

    if result:
        total_products, total_cost, avg_cost, min_cost, max_cost, most_expensive, least_expensive = result

        # Mostrar el resumen
        subprocess.run(["clear"])
        utils.draw_tittle_border("Resumen de los productos")
        print(f"  - Num. Productos: {total_products}\n")
        print(f"  - Costo Total: ${total_cost:,.3f}")
        print(f"  - Costo Promedio: ${avg_cost:,.3f}\n")
        print(f"  - Producto más barato: {least_expensive}")
        print(f"  - Costo (mínimo): ${min_cost:,.3f}\n")
        print(f"  - Producto más caro: {most_expensive}")
        print(f"  - Costo (máximo): ${max_cost:,.3f}\n")
    else:
        print("\n    No hay datos disponibles en la tabla de productos.")

def ask_for_product_details(date = None):
    name = utils.read_input_simple_text("  * Nombre: ")
    quantity = utils.read_input_float_fraction_str("  * Cantidad: ")
    unit = utils.read_input_simple_text("  * Medida: ")
    total = utils.read_input_float("  * Total: ", 0, 1000000)
    if(date is None):
        date = datetime.now().strftime("%d/%m/%Y")
    print(f"  * Fecha (Día/Mes/Año): {date}")
    change_date = utils.read_input_yes_no("¿Desea cambiar la fecha?")
    if(change_date.lower() in ['si', 's']):
        date = utils.read_input_date("  * Fecha (Día/Mes/Año): ")
    return Product(name=name, quantity=quantity, unit=unit, total=total, date=date)

def register_multiple_products(conn):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Registrar nuevo producto")
        conn.insert_product(ask_for_product_details())
        stop = utils.read_input_yes_no("¿Desea agregar otro producto?")
        if(stop.lower() in ['no', 'n']):
            break

def update_product(conn, table_products):
    render_table_with_csv_memory(conn, table_products)
    utils.draw_tittle_border(f"Actualizando detalles del producto")
    id_prod = utils.read_input_integer("\n  * Ingrese el ID: ", 1, 1000000)
    prod_obj = conn.find_product(table_products, "ID", id_prod)
    if(prod_obj is not None):
        print(f"\n  [ DATOS ACTUALES ]\n")
        print(f"  * Nombre: {prod_obj.get_name()}")
        print(f"  * Cantidad: {prod_obj.get_quantity()}")
        print(f"  * Medida: {prod_obj.get_unit()}")
        print(f"  * Precio: {prod_obj.get_price()}")
        print(f"  * Total: {prod_obj.get_total()}")
        print(f"  * Fecha: {prod_obj.get_date()}")
        print(f"\n  [ NUEVOS DATOS ]\n")
        conn.update_product(table_products, id_prod, ask_for_product_details(prod_obj.get_date()))
    input("\n   >>> Presione ENTER para continuar <<<")

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
    render_table_with_csv_memory(conn, table_paths)
    type_update=""
    if(field == "is_export"):
        type_update="EXPORTACIÓN"
    elif(field == "is_import"):
        type_update="IMPORTACIÓN"
    else:
        raise ValueError(f"Campo desconocido: {field}")
    utils.draw_tittle_border(f"Actualizando ruta de {type_update}")
    id_path = utils.read_input_integer("\n  * Ingrese el ID: ", 1, 1000000)
    path_obj = conn.find_path(table_paths, "ID", id_path)
    if(path_obj is not None):
        conn.update_path(table_paths, id_path, field)

def delete_multiple_paths(conn, table_paths):
    while True:
        render_table_with_csv_memory(conn, table_paths)
        utils.draw_tittle_border("Eliminar una ruta")
        id_path = utils.read_input_integer("\n  * Ingrese el ID: ", 1, 1000000)
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

def get_expanded_path(path):
    try:
        expanded_path = os.path.expandvars(path)
        expanded_path = os.path.expanduser(expanded_path)
        final_expanded_path = os.path.abspath(expanded_path)
        return final_expanded_path
    except KeyError as e:
        print(f"\n   >>> Error: Variable de entorno no encontrada en la ruta. \n   >>>Detalles: {e}")
    except Exception as e:
        print(f"\n   >>> Ha ocurrido un error inesperado: {e}")
    return None

def create_directory_and_get_expanded_path(path):
    try:
        expanded_path = get_expanded_path(path)
        os.makedirs(expanded_path, exist_ok=True)
        return expanded_path
    except PermissionError as e:
        print(f"\n   >>> Error: No tienes permisos suficientes para crear el directorio. \n   >>> Detalles: {e}")
    except OSError as e:
        print(f"\n   >>> Error: Ha ocurrido un error con el sistema operativo. \n   >>>Detalles: {e}")
    except Exception as e:
        print(f"\n   >>> Ha ocurrido un error inesperado: {e}")
    return None

def export_table_to_csv_default(conn, table_name, export_path):
    subprocess.run(["clear"])
    utils.draw_tittle_border(f"Exportando tabla {table_name}")
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    file_name = f"{table_name.capitalize()}_{timestamp}.csv"
    print(f"\n   [ Ruta del archivo ] \n   > {export_path.path}")
    print(f"\n   [ Nombre del Archivo ] \n   > {file_name}")
    change_name = utils.read_input_yes_no("¿Desea cambiar el nombre del archivo?")
    if(change_name.lower() in ['si', 's']):
        file_name = utils.read_input_file_csv(f"\n   [ Nuevo Nombre ] \n   > ")
    expanded_path = create_directory_and_get_expanded_path(export_path.path)
    conn.export_table_to_csv(table_name, file_name, expanded_path)

def import_table_from_csv_default(conn, table_name, import_path):
    file_path = get_expanded_path(import_path.path)
    file_list = find_files_by_extension(file_path, "csv")

    if len(file_list) < 1:
        print(f"\n   >>> No se encontraron archivos: *.csv")
        return

    option = select_file_from_list(file_list)
    selected_file = os.path.basename(file_list[option-1])
    print(f"\n   [ Ruta de Importación ] \n   > {file_path}")
    print(f"\n   [ Archivo seleccionado ] \n   > {selected_file}")

    if not conn.is_table_empty(table_name):
        print("   *** SU TABLA NO ESTA VACIA ***")
        confirm_clear_table = utils.read_input_yes_no("¿Desea reemplazar los datos existentes?")
        if(confirm_clear_table.lower() in ['si', 's']):
            c = conn.execute_query(f"DELETE FROM {table_name}")
            conn.commit(c)
            conn.import_table_from_csv(table_name, selected_file, file_path)
        else:
            print("\n   >>> Operacion cancelada")
    else:
        conn.import_table_from_csv(table_name, selected_file, file_path)

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
                conn = initialize_db()
            else:
                print("\n   >>> Operacion cancelada")
    return conn

def handle_product_deletion_menu(conn, table_products):
    while True:
        render_table_with_csv_memory(conn, table_products)
        utils.draw_tittle_border("Eliminar un producto")
        print("  0. Regresar")
        print("  1. Usando su ID")
        print("  2. Todos los que coincidan con el NOMBRE")
        print("  3. Todos los que coincidan en cierta FECHA")
        option = utils.read_input_options_menu(0, 3)
        if(option == 0):
            break
        elif(option == 1):
            id_product = utils.read_input_integer("\n  * Ingrese el ID: ", 1, 10000000)
            conn.delete_item(table_products, "ID", id_product)
        elif(option == 2):
            name_product = utils.read_input_simple_text("\n  * Ingrese el NOMBRE: ")
            conn.delete_item(table_products, "NAME", name_product)
        elif(option == 3):
            date_product = utils.read_input_date("\n  * Ingrese el FECHA: ")
            conn.delete_item(table_products, "DATE", date_product)
        if conn.is_table_empty(table_products):
            break

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
            conn.validate_table_not_empty("No hay datos para mostrar...", render_table_with_csv_memory, table_paths)
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

def handle_products_menu(conn, table_products):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Tabla productos")
        print("  0. Salir")
        print("  1. Visualizar lista de productos")
        print("  2. Registrar un producto")
        print("  3. Eliminar un producto")
        print("  4. Actualizar un producto")
        print("  5. Ver resumen de los productos")
        option = utils.read_input_options_menu(0, 5)
        if(option == 0):
            break
        elif(option == 1):
            conn.validate_table_not_empty("No hay datos para mostrar...", render_table_with_csv_memory, table_products)
            input("\n   >>> Presione ENTER para continuar <<<")
        elif(option == 2):
            register_multiple_products(conn)
        elif(option == 3):
            conn.validate_table_not_empty("No hay datos para eliminar...", handle_product_deletion_menu, table_products)
            time.sleep(0.7)
        elif(option == 4):
            conn.validate_table_not_empty("No hay datos para actualizar...", update_product, table_products)
        elif(option == 5):
            conn.validate_table_not_empty("No hay productos del cual ver resumen...", show_products_summary, table_products)
            input("\n   >>> Presione ENTER para continuar <<<")

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
        menu_options.append((f"Exportar {table} como CSV", export_table_to_csv_default, table, export_path))
        menu_options.append((f"Importar {table} desde CSV", import_table_from_csv_default, table, import_path))
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

def main(conn):
    table_products = "products"
    table_paths = "paths"
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
    main(initialize_db())
