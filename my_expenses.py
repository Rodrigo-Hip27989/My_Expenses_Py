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
    utils.draw_tittle_border("SELECCIONE UN ARCHIVO PARA IMPORTAR")
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
        utils.draw_tittle_border("REGISTRAR NUEVO PRODUCTO")
        conn.insert_product(ask_for_product_details())
        stop = utils.read_input_yes_no("\n  >>> ¿Desea agregar otro producto (Si/No)?: ")
        if(stop.lower() in ['no', 'n']):
            break

def ask_for_path_to_insert(is_first_entry):
    new_path = utils.read_input_paths_linux("  * Ruta: ")
    if(is_first_entry):
        return Path(path=new_path, is_export=1, is_import=1)
    else:
        is_export = utils.read_input_yes_no("\n  * Establecer como ruta de exportación (Si/No): ")
        is_import = utils.read_input_yes_no("\n  * Establecer como ruta de importación (Si/No): ")
        return Path(new_path, is_export.lower() in ['si', 's'], is_import.lower() in ['si', 's'])

def register_multiple_paths(conn, table_paths):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("REGISTRAR NUEVA RUTA")
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
    if(field == "is_import"):
        type_update="IMPORTACIÓN"
    utils.draw_tittle_border(f"ATUALIZANDO RUTA DE {type_update}")
    id_path = utils.read_input_integer(f"\n  * Ingrese el ID: ", 1, 1000000)
    found_path = conn.find_item(table_paths, "ID", id_path)
    if(found_path != None):
        conn.update_path(table_paths, id_path, field)

def delete_multiple_paths(conn, table_paths):
    while True:
        render_table_with_csv_memory(conn, table_paths)
        utils.draw_tittle_border("ELIMINAR UNA RUTA")
        id_path = utils.read_input_integer(f"\n  * Ingrese el ID: ", 1, 1000000)
        found_path = conn.find_item(table_paths, "ID", id_path)
        if(found_path != None):
            if(found_path[2] == 1 or found_path[3] == 1):
                print(f"\n  *** No es posible eliminar una ruta csv en uso***")
            else:
                conn.delete_item(table_paths, "ID", found_path[0])
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

def export_csv_with_default_name(conn, table_products, table_paths):
    found_path = conn.find_item(table_paths, "is_export", True)
    if(found_path != None):
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        file_name = f"{table_products.capitalize()}_{timestamp}.csv"
        expanded_path = create_directory_and_get_expanded_path(found_path[1])
        conn.export_csv(table_products, file_name, expanded_path)
    else:
        print("\n   >>> Por favor configure una ruta de exportación!")

def import_products_from_csv(conn, table_paths, table_products, extension):
    found_path = conn.find_item(table_paths, "is_import", True)
    if(found_path == None):
        print("\n   >>> No hay rutas de importación configuradas")
        return 0

    file_path = get_expanded_path(found_path[1])
    file_list = find_files_by_extension(file_path, extension)

    if len(file_list) < 1:
        print(f"\n   >>> No se encontraron archivos: *.{extension}")
        return 0

    option = select_file_from_list(file_list)
    selected_file = os.path.basename(file_list[option-1])
    print(f"\n   [ Ruta de Importación ] \n   > {file_path}")
    print(f"\n   [ Archivo seleccionado ] \n   > {selected_file}")

    if(conn.get_num_rows_table(table_products) > 0):
        confirm_clear_table = utils.read_input_yes_no("\n   *** SU TABLA NO ESTA VACIA ***\n\n   ¿Desea reemplazar los datos existentes? (Si/No) ")
        if(confirm_clear_table.lower() in ['si', 's']):
            c = conn.execute_query(f"DELETE FROM {table_products}")
            conn.commit(c)
            conn.import_from_csv(table_products, selected_file, file_path)
        else:
            print("\n   >>> Operacion cancelada")
    else:
        conn.import_from_csv(table_products, selected_file, file_path)

def drop_tables(conn, table_products, table_paths):
    subprocess.run(["clear"])
    utils.draw_tittle_border("ELIMINANDO DATOS DE TABLAS")
    print("   0. Regresar")
    print("   1. Eliminar datos de productos")
    print("   2. Eliminar datos de rutas")
    print("   3. Eliminar datos de todas las tablas")
    option = utils.read_input_integer("\n   * Opción >> ", 0, 3)
    if(option != 0):
        if(option == 1):
            c = conn.execute_query(f"DELETE FROM {table_products}")
            conn.confirm_transaction_database(c)
        elif(option == 2):
            c = conn.execute_query(f"DELETE FROM {table_paths}")
            conn.confirm_transaction_database(c)
        elif(option == 3):
            drop_db = utils.read_input_yes_no("\n    >>> Esta acción no puede deshacerse <<< \n\n    ¿Esta seguro de continuar? (Si/No): ")
            if(drop_db.lower() in ['si', 's']):
                conn.disconnect()
                conn.delete_database()
                conn = initialize_db()
            else:
                print("\n   >>> Operacion cancelada")
    return conn

def show_product_deletion_menu(conn, table_products):
    while True:
        render_table_with_csv_memory(conn, table_products)
        utils.draw_tittle_border("ELIMINAR UN PRODUCTO")
        print("  0. Regresar")
        print("  1. Limpiar pantalla")
        print("  2. Usando su ID")
        print("  3. Todos los que coincidan con el NOMBRE")
        print("  4. Todos los que coincidan en cierta FECHA")
        opcion = utils.read_input_integer("\n  * Opción >> ", 0, 4)
        if(opcion == 0):
            break
        elif(opcion == 1):
            subprocess.run(["clear"])
        elif(opcion == 2):
            id_product = utils.read_input_integer(f"\n  * Ingrese el ID: ", 1, 10000000)
            conn.delete_item(table_products, "ID", id_product)
        elif(opcion == 3):
            name_product = utils.read_input_simple_text(f"\n  * Ingrese el NOMBRE: ")
            conn.delete_item(table_products, "NOMBRE", name_product)
        elif(opcion == 4):
            date_product = utils.read_input_date(f"\n  * Ingrese el FECHA: ")
            conn.delete_item(table_products, "FECHA", date_product)
        if conn.get_num_rows_table(table_products) < 1:
            break
        time.sleep(0.5)

def show_manager_paths_menu(conn, table_paths):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("ADMINSTRAR RUTAS")
        print("  0. Regresar")
        print("  1. Limpiar pantalla")
        print("  2. Visualizar rutas guardadas")
        print("  3. Registrar nueva ruta")
        print("  4. Eliminar una ruta")
        print("  5. Actualizar ruta de exportación")
        print("  6. Actualizar ruta de importación")
        opcion = utils.read_input_integer("\n  * Opción >> ", 0, 6)
        if(opcion == 0):
            break
        elif(opcion == 1):
            subprocess.run(["clear"])
        elif(opcion == 2):
            conn.validate_table_not_empty(render_table_with_csv_memory, table_paths, "No hay datos para mostrar...")
            input("\n  >>> Presione ENTER para continuar <<<")
        elif(opcion == 3):
            register_multiple_paths(conn, table_paths)
        elif(opcion == 4):
            conn.validate_table_not_empty(delete_multiple_paths, table_paths, "No hay datos para eliminar...")
        elif(opcion == 5):
            conn.validate_table_not_empty(update_path, table_paths, "No hay datos para actualizar...", "is_export")
        elif(opcion == 6):
            conn.validate_table_not_empty(update_path, table_paths, "No hay datos para actualizar...", "is_import")
        time.sleep(0.5)

def main(conn):
    table_products = "productos"
    table_paths = "paths"
    signal.signal(signal.SIGINT, handle_interrupt)
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("REGISTRAR GASTOS DE PRODUCTOS")
        print("  0. Salir")
        print("  1. Limpiar pantalla")
        print("  2. Visualizar lista de productos")
        print("  3. Registrar un producto")
        print("  4. Eliminar un producto")
        print("  5. Exportar CSV")
        print("  6. Importar CSV")
        print("  7. Configurar rutas")
        print("  8. Configurar listas de productos")
        print("  9. Eliminar datos")
        try:
            opcion = utils.read_input_integer("\n  * Opción >> ", 0, 9)
            if(opcion == 0):
                break
            elif(opcion == 1):
                subprocess.run(["clear"])
            elif(opcion == 2):
                conn.validate_table_not_empty(render_table_with_csv_memory, table_products, "No hay datos para mostrar...")
                input("\n   >>> Presione ENTER para continuar <<<")
            elif(opcion == 3):
                register_multiple_products(conn)
            elif(opcion == 4):
                conn.validate_table_not_empty(show_product_deletion_menu, table_products, "No hay datos para eliminar...")
                time.sleep(0.7)
            elif(opcion== 5):
                conn.validate_table_not_empty(export_csv_with_default_name, table_products, "Aun no hay datos para exportar!", table_paths)
                input("\n   >>> Presione ENTER para continuar <<<")
            elif(opcion == 6):
                conn.validate_table_not_empty(import_products_from_csv, table_paths, "Aún no hay rutas guardadas", table_products, "csv")
                input("\n   >>> Presione ENTER para continuar <<<")
            elif(opcion == 7):
                show_manager_paths_menu(conn, table_paths)
            elif(opcion == 8):
                print("\n   En proceso de creación...")
                time.sleep(0.7)
            elif(opcion == 9):
                conn = drop_tables(conn, table_products, table_paths)
        except (KeyboardInterrupt, EOFError):
            subprocess.run(["clear"])
            print("\n\n\n\n    Interrupción detectada !!!\n\n    Volviendo al menú principal ...\n\n")
            time.sleep(1.3)
    conn.disconnect()

if __name__ == "__main__":
    main(initialize_db())
