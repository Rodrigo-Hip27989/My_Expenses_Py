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
    option = utils.read_input_integer("\n  * Opción >> ", 1, (len(file_list)))
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

def ask_for_product_details():
    name = utils.read_input_simple_text("  * Nombre: ")
    quantity = utils.read_input_float("  * Cantidad: ", 0.0001, 1000000)
    unit = utils.read_input_simple_text("  * Medida: ")
    total = utils.read_input_float("  * Total: ", 0, 1000000)
    date = datetime.now().strftime("%d/%m/%Y")
    print(f"  * Fecha (Día/Mes/Año): {date}")
    change_date = utils.read_input_yes_no("\n  >>> ¿Desea cambiar la fecha (Si/No)?: ")
    if(change_date.lower() in ['si', 's']):
        date = utils.read_input_date("  * Fecha (Día/Mes/Año): ")
    return Product(name=name, quantity=quantity, unit=unit, total=total, date=date)

def register_multiple_products(conn):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Registrar nuevo producto")
        conn.insert_product(ask_for_product_details())
        stop = utils.read_input_yes_no("\n  >>> ¿Desea agregar otro producto (Si/No)?: ")
        if(stop.lower() in ['no', 'n']):
            break

def ask_for_path_to_insert(is_first_entry):
    new_path = utils.read_input_paths_linux("  * Ruta: ")
    if(is_first_entry):
        return Path(path=new_path, is_export=1, is_import=1)
    else:
        is_exp = utils.read_input_yes_no("\n  * Establecer como ruta de exportación (Si/No): ").lower() in ['si', 's']
        is_imp = utils.read_input_yes_no("\n  * Establecer como ruta de importación (Si/No): ").lower() in ['si', 's']
        return Path(path=new_path, is_export=is_exp, is_import=is_imp)

def register_multiple_paths(conn, table_paths):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Registrar nueva ruta")
        is_first_entry = conn.get_num_rows_table(table_paths) == 0
        conn.insert_path(table_paths, ask_for_path_to_insert(is_first_entry), is_first_entry)
        stop = utils.read_input_yes_no("\n  >>> ¿Desea agregar otra ruta (Si/No)?: ")
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
    id_path = utils.read_input_integer(f"\n  * Ingrese el ID: ", 1, 1000000)
    path_obj = conn.find_path(table_paths, "ID", id_path)
    if(path_obj is not None):
        conn.update_path(table_paths, id_path, field)

def delete_multiple_paths(conn, table_paths):
    while True:
        render_table_with_csv_memory(conn, table_paths)
        utils.draw_tittle_border("Eliminar una ruta")
        id_path = utils.read_input_integer(f"\n  * Ingrese el ID: ", 1, 1000000)
        path_obj = conn.find_path(table_paths, "ID", id_path)
        if(path_obj is not None):
            if(path_obj.is_export == 1 or path_obj.is_import == 1):
                print(f"\n  *** No es posible eliminar una ruta csv en uso***")
            else:
                conn.delete_item(table_paths, "ID", id_path)
        if conn.get_num_rows_table(table_paths) > 0:
            stop = utils.read_input_yes_no("\n  >>> ¿Desea eliminar otra ruta (Si/No)?: ")
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
        return None
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
        return None
    except OSError as e:
        print(f"\n   >>> Error: Ha ocurrido un error con el sistema operativo. \n   >>>Detalles: {e}")
        return None
    except Exception as e:
        print(f"\n   >>> Ha ocurrido un error inesperado: {e}")
        return None

def export_table_to_csv_default(conn, table_name, table_paths):
    path_obj = conn.find_path(table_paths, "is_export", True)
    if(path_obj is not None):
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        file_name = f"{table_name.capitalize()}_{timestamp}.csv"
        expanded_path = create_directory_and_get_expanded_path(path_obj.path)
        conn.export_table_to_csv(table_name, file_name, expanded_path)
    else:
        print("\n   >>> Por favor configure una ruta de exportación!")

def import_table_from_csv_default(conn, table_name, table_paths):
    path_obj = conn.find_path(table_paths, "is_import", 1)
    if(path_obj is None):
        print("\n   >>> No hay rutas de importación configuradas")
        return 0

    file_path = get_expanded_path(path_obj.path)
    file_list = find_files_by_extension(file_path, "csv")

    if len(file_list) < 1:
        print(f"\n   >>> No se encontraron archivos: *.csv")
        return 0

    option = select_file_from_list(file_list)
    selected_file = os.path.basename(file_list[option-1])
    print(f"\n   [ Ruta de Importación ] \n   > {file_path}")
    print(f"\n   [ Archivo seleccionado ] \n   > {selected_file}")

    if(conn.get_num_rows_table(table_name) > 0):
        confirm_clear_table = utils.read_input_yes_no("\n   *** SU TABLA NO ESTA VACIA ***\n\n   ¿Desea reemplazar los datos existentes? (Si/No) ")
        if(confirm_clear_table.lower() in ['si', 's']):
            c = conn.execute_query(f"DELETE FROM {table_name}")
            conn.commit(c)
            conn.import_table_from_csv(table_name, selected_file, file_path)
        else:
            print("\n   >>> Operacion cancelada")
    else:
        conn.import_table_from_csv(table_name, selected_file, file_path)

def delete_tables(conn, table_products, table_paths):
    subprocess.run(["clear"])
    utils.draw_tittle_border("Eliminando datos de tablas")
    print("   0. Regresar")
    print("   1. Eliminar datos de productos")
    print("   2. Eliminar datos de rutas")
    print("   3. Eliminar datos de todas las tablas")
    option = utils.read_input_integer("\n   * Opción >> ", 0, 3)
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
            delete_db = utils.read_input_yes_no("\n    >>> Esta acción no puede deshacerse <<< \n\n    ¿Esta seguro de continuar? (Si/No): ")
            if(delete_db.lower() in ['si', 's']):
                conn.disconnect()
                conn.delete_database()
                conn = initialize_db()
            else:
                print("\n   >>> Operacion cancelada")
    return conn

def show_product_deletion_menu(conn, table_products):
    while True:
        render_table_with_csv_memory(conn, table_products)
        utils.draw_tittle_border("Eliminar un producto")
        print("  0. Regresar")
        print("  1. Limpiar pantalla")
        print("  2. Usando su ID")
        print("  3. Todos los que coincidan con el NOMBRE")
        print("  4. Todos los que coincidan en cierta FECHA")
        option = utils.read_input_integer("\n  * Opción >> ", 0, 4)
        if(option == 0):
            break
        elif(option == 1):
            subprocess.run(["clear"])
        elif(option == 2):
            id_product = utils.read_input_integer(f"\n  * Ingrese el ID: ", 1, 10000000)
            conn.delete_item(table_products, "ID", id_product)
        elif(option == 3):
            name_product = utils.read_input_simple_text(f"\n  * Ingrese el NOMBRE: ")
            conn.delete_item(table_products, "NOMBRE", name_product)
        elif(option == 4):
            date_product = utils.read_input_date(f"\n  * Ingrese el FECHA: ")
            conn.delete_item(table_products, "FECHA", date_product)
        if conn.get_num_rows_table(table_products) < 1:
            break
        time.sleep(0.5)

def show_manager_paths_menu(conn, table_paths):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Administrar rutas")
        print("  0. Regresar")
        print("  1. Limpiar pantalla")
        print("  2. Visualizar rutas guardadas")
        print("  3. Registrar nueva ruta")
        print("  4. Eliminar una ruta")
        print("  5. Actualizar ruta de exportación")
        print("  6. Actualizar ruta de importación")
        option = utils.read_input_integer("\n  * Opción >> ", 0, 6)
        if(option == 0):
            break
        elif(option == 1):
            subprocess.run(["clear"])
        elif(option == 2):
            conn.validate_table_not_empty(render_table_with_csv_memory, table_paths, "No hay datos para mostrar...")
            input("\n  >>> Presione ENTER para continuar <<<")
        elif(option == 3):
            register_multiple_paths(conn, table_paths)
        elif(option == 4):
            conn.validate_table_not_empty(delete_multiple_paths, table_paths, "No hay datos para eliminar...")
        elif(option == 5):
            conn.validate_table_not_empty(update_path, table_paths, "No hay datos para actualizar...", "is_export")
        elif(option == 6):
            conn.validate_table_not_empty(update_path, table_paths, "No hay datos para actualizar...", "is_import")
        time.sleep(0.5)

def show_manager_products_menu(conn, table_products):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Tabla productos")
        print("  0. Salir")
        print("  1. Visualizar lista de productos")
        print("  2. Registrar un producto")
        print("  3. Eliminar un producto")
        option = utils.read_input_integer("\n  * Opción >> ", 0, 3)
        if(option == 0):
            break
        elif(option == 1):
            conn.validate_table_not_empty(render_table_with_csv_memory, table_products, "No hay datos para mostrar...")
            input("\n   >>> Presione ENTER para continuar <<<")
        elif(option == 2):
            register_multiple_products(conn)
        elif(option == 3):
            conn.validate_table_not_empty(show_product_deletion_menu, table_products, "No hay datos para eliminar...")
            time.sleep(0.7)

def show_manager_export_import_data_menu(conn, table_products, table_paths):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Opciones de exportacion/importación")
        print("  0. Salir")
        print(f"  1. Exportar {table_products.upper()} como CSV")
        print(f"  2. Importar {table_products.upper()} desde CSV")
        option = utils.read_input_integer("\n  * Opción >> ", 0, 2)
        if(option == 0):
            break
        elif(option== 1):
            conn.validate_table_not_empty(export_table_to_csv_default, table_products, "Aún no hay datos para exportar!", table_paths)
            input("\n   >>> Presione ENTER para continuar <<<")
        elif(option == 2):
            conn.validate_table_not_empty(import_table_from_csv_default, table_products, "Aún no hay rutas guardadas!", table_paths)
            input("\n   >>> Presione ENTER para continuar <<<")

def main(conn):
    table_products = "products"
    table_paths = "paths"
    signal.signal(signal.SIGINT, handle_interrupt)
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("Resgistrar gastos de productos")
        print("  0. Salir")
        print("  1. Limpiar pantalla")
        print("  2. Administrar tabla de productos")
        print("  3. Administrar tabla de rutas")
        print("  4. Exportar/Importar datos")
        print("  5. Eliminar datos de tablas")
        try:
            option = utils.read_input_integer("\n  * Opción >> ", 0, 5)
            if(option == 0):
                break
            elif(option == 1):
                subprocess.run(["clear"])
            elif(option == 2):
                show_manager_products_menu(conn, table_products)
            elif(option == 3):
                show_manager_paths_menu(conn, table_paths)
            elif(option == 4):
                show_manager_export_import_data_menu(conn, table_products, table_paths)
            elif(option == 5):
                conn = delete_tables(conn, table_products, table_paths)
        except (KeyboardInterrupt, EOFError):
            subprocess.run(["clear"])
            print("\n\n\n\n    Interrupción detectada !!!\n\n    Volviendo al menú principal ...\n\n")
            time.sleep(1.3)
    conn.disconnect()

if __name__ == "__main__":
    main(initialize_db())
