import os
import time
import subprocess
import sqlite_conn
import my_utils as utils
from datetime import datetime

def initialize_db():
    db_path="sqlite_db"
    db_file="my_expenses.db"
    conn = sqlite_conn.Database(db_path, db_file)
    conn.connect()
    conn.create_products_tbl()
    conn.paths_tbl()
    return conn

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
    measurement_unit = utils.read_input_simple_text("  * Medida: ")
    price = utils.read_input_float("  * Precio Unitario: ", 0, 1000000)
    total = quantity*price
    date = datetime.now().strftime("%d/%m/%Y")
    print(f"  * Fecha (Día/Mes/Año): {date}")
    change_date = utils.read_input_yes_no("\n  >>> ¿Desea cambiar la fecha (Si/No)?: ")
    if(change_date.lower() in ['si', 's']):
        date = utils.read_input_date("  * Fecha (Día/Mes/Año): ")
    return [name, quantity, measurement_unit, price, total, date]

def register_multiple_products(conn):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("REGISTRAR NUEVO PRODUCTO")
        conn.insert_product(ask_for_product_details())
        stop = utils.read_input_yes_no("\n  >>> ¿Desea agregar otro producto (Si/No)?: ")
        if(stop.lower() in ['no', 'n']):
            break

def ask_for_path_details():
    is_export = utils.read_input_yes_no("\n  * Establecer como ruta de exportación (Si/No): ")
    is_import = utils.read_input_yes_no("\n  * Establecer como ruta de importación (Si/No): ")
    return [is_export.lower() in ['si', 's'], is_import.lower() in ['si', 's']]

def ask_for_path_to_insert(is_first_entry):
    new_path = utils.read_input_paths_linux("  * Ruta: ")
    if(is_first_entry):
        return [new_path, 1, 1]
    else:
        is_export, is_import = ask_for_path_details()
        return [new_path, is_export, is_import]

def register_multiple_paths(conn, table_name):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("REGISTRAR NUEVA RUTA")
        conn.insert_path(table_name, ask_for_path_to_insert)
        stop = utils.read_input_yes_no("\n  >>> ¿Desea agregar otra ruta (Si/No)?: ")
        if(stop.lower() in ['no', 'n']):
            break

def update_multiple_paths(conn, table_paths):
    while True:
        render_table_with_csv_memory(conn, table_paths)
        utils.draw_tittle_border("MODIFICAR UNA RUTA")
        path_found = conn.find_item(table_paths, "ID", utils.read_input_integer, 1, 10000000)
        if(path_found != []):
            conn.update_path(table_paths, path_found[0], ask_for_path_details)
        stop = utils.read_input_yes_no("\n  >>> ¿Desea modificar otra ruta (Si/No)?: ")
        if(stop.lower() in ['no', 'n']):
            break

def delete_multiple_paths(conn, table_paths):
    while True:
        render_table_with_csv_memory(conn, table_paths)
        utils.draw_tittle_border("ELIMINAR UNA RUTA")
        path_found = conn.find_item(table_paths, "ID", utils.read_input_integer, 1, 10000000)
        if(path_found != []):
            conn.delete_path(table_paths, path_found)
        if conn.get_num_rows_table(table_paths) > 0:
            stop = utils.read_input_yes_no("\n  >>> ¿Desea eliminar otra ruta (Si/No)?: ")
            if(stop.lower() in ['no', 'n']):
                break
        else:
            break

def create_directory_and_get_expanded_path(path):
    try:
        expanded_path = os.path.expandvars(path)
        expanded_path = os.path.expanduser(expanded_path)
        final_expanded_path = os.path.abspath(expanded_path)
        os.makedirs(expanded_path, exist_ok=True)
        return final_expanded_path
    except KeyError as e:
        print(f"\n   >>> Error: Variable de entorno no encontrada en la ruta. \n   >>>Detalles: {e}")
        return None
    except PermissionError as e:
        print(f"\n   >>> Error: No tienes permisos suficientes para crear el directorio. \n   >>> Detalles: {e}")
        return None
    except OSError as e:
        print(f"\n   >>> Error: Ha ocurrido un error con el sistema operativo. \n   >>>Detalles: {e}")
        return None
    except Exception as e:
        print(f"\n   >>> Ha ocurrido un error inesperado: {e}")
        return None

def export_csv_with_default_name(conn, table_name, table_csv):
    default_path = conn.execute_query(f"SELECT * FROM {table_csv} WHERE is_export = 1").fetchone()
    if(default_path != None and default_path[1] != ""):
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        file_name = f"{table_name.capitalize()}_{timestamp}.csv"
        expanded_path = create_directory_and_get_expanded_path(default_path[1])
        conn.export_csv(table_name, file_name, expanded_path)
    else:
        print("\n   >>> Por favor configure una ruta de exportación!")

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
            print("\n  Regresando...")
            time.sleep(0.3)
            break
        elif(opcion == 1):
            subprocess.run(["clear"])
        elif(opcion == 2):
            conn.delete_item(table_products, "ID", utils.read_input_integer, 1, 1000000)
            time.sleep(1)
        elif(opcion == 3):
            conn.delete_item(table_products, "NOMBRE", utils.read_input_simple_text)
            time.sleep(1)
        elif(opcion == 4):
            conn.delete_item(table_products, "FECHA", utils.read_input_date)
            time.sleep(1)
        if conn.get_num_rows_table(table_products) < 1:
            break

def show_manager_paths_menu(conn, table_paths):
    while True:
        subprocess.run(["clear"])
        utils.draw_tittle_border("ADMINSTRAR RUTAS")
        print("  0. Regresar")
        print("  1. Limpiar pantalla")
        print("  2. Visualizar rutas guardadas")
        print("  3. Registrar nueva ruta")
        print("  4. Eliminar una ruta")
        print("  5. Modificar rutas de exportación o importación")
        opcion = utils.read_input_integer("\n  * Opción >> ", 0, 5)
        if(opcion == 0):
            print("\n  Saliendo del programa...\n")
            time.sleep(0.3)
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
            time.sleep(1.3)
        elif(opcion == 5):
            conn.validate_table_not_empty(update_multiple_paths, table_paths, "No hay datos para actualizar...")
            time.sleep(1.3)

def main(conn):
    table_products = "productos"
    table_paths = "paths"
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
        print("  9. Vaciar la base de datos")
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
            time.sleep(1.7)
        elif(opcion == 5):
            conn.validate_table_not_empty(export_csv_with_default_name, table_products, "Aun no hay datos para exportar!", table_paths)
            time.sleep(1.7)
        elif(opcion == 6):
            print("\n    En proceso de creación...")
            time.sleep(1.3)
        elif(opcion == 7):
            show_manager_paths_menu(conn, table_paths)
        elif(opcion == 8):
            print("\n   En proceso de creación...")
            time.sleep(1.3)
        elif(opcion == 9):
            delete_db = utils.read_input_yes_no("\n   ¿Esta seguro de borrar todos sus datos? (Si/No): ")
            if(delete_db.lower() in ['si', 's']):
                conn.disconnect()
                conn.delete_database()
                conn = initialize_db()
            else:
                print("\n   >>> Operacion cancelada")
            time.sleep(1.3)
    conn.disconnect()

if __name__ == "__main__":
    main(initialize_db())
