import os
import time
import subprocess
import sqlite_conn
import my_utils as utils

def draw_tittle_border(titulo):
    border = '=' * (len(titulo) + 7)
    print(f"\n  {border}\n  |  {titulo}  |\n  {border}\n")

def show_product_deletion_menu(conn):
    show_table_product(conn)
    draw_tittle_border("ELIMINAR UN PRODUCTO")
    print("  1. Usando su ID")
    print("  2. Todos los que coincidan con el NOMBRE")
    print("  3. Todos los que coincidan en cierta FECHA")
    print("  4. Limpiar pantalla")
    print("  5. Regresar")
    opcion = utils.read_input_integer("\n  * Opción >> ", 1, 5)
    if(opcion == 1):
        conn.delete_product(utils.read_input_integer, "ID", 1, 1000000)
    elif(opcion == 2):
        conn.delete_product(utils.read_input_simple_text, "nombre")
    elif(opcion == 3):
        conn.delete_product(utils.read_input_date, "fecha")
    elif(opcion == 4):
        subprocess.run(["clear"])
        show_product_deletion_menu(conn)
    elif(opcion == 5):
        print("\n  Regresando...")
        time.sleep(0.25)

def get_header_sizes(terminal_size):
    if(terminal_size >= 127):
        return [4, 28, 11, 18, 15, 15, 11]
    elif((terminal_size >= 117) and (terminal_size < 127)):
        return [3, 25, 10, 17, 13, 13, 11]
    elif((terminal_size >= 107) and (terminal_size < 117)):
        return [3, 22, 9, 16, 11, 11, 10]
    elif((terminal_size >= 97) and (terminal_size < 107)):
        return [2, 19, 8, 15, 9, 9, 10]
    elif((terminal_size >= 87) and (terminal_size < 97)):
        return [2, 17, 8, 13, 6, 6, 10]
    elif((terminal_size >= 77) and (terminal_size < 87)):
        return [2, 12, 8, 8, 6, 6, 10]
    else:
        return []

def draw_table(data, encabezados, headers_size):
    border = "   +" + "+".join(["-" * (hsize+2) for hsize in headers_size]) + "+"
    print(f"{border}\n   | " + " | ".join(f"{nombre.upper():<{hsize}}" for nombre, hsize in zip(encabezados, headers_size)) + f" |\n{border}")
    for row in data:
        print("   | " + " | ".join(f"{str(item):<{hsize}}" for item, hsize in zip(row, headers_size)) + " |")
    print(f"{border}")

def draw_simple_borders(data, encabezados):
    max_len = max(len(f"{row}") for row in data)
    border = '-' * (max_len+4)
    print(f"\n  {border}\n  | " + " | ".join(f"{str(nombre).upper()}" for nombre in encabezados) + f"  |\n  {border}")
    for row in data:
        simple_row = " | ".join(str(item) for item in row)
        print(f"  |  {simple_row}  |")
    print(f"  {border}\n")

def show_table_product(conn):
    table_name = "productos"
    sql_query = f"SELECT * FROM {table_name}"
    data = conn.fetch_all(sql_query)
    subprocess.run(["clear"])
    print("\n")
    terminal_size = os.get_terminal_size().columns
    encabezados = conn.get_headers(f"{table_name}")
    if(terminal_size>=77):
        headers_size = get_header_sizes(terminal_size)
        draw_table(data, encabezados, headers_size)
    else:
        draw_simple_borders(data, encabezados)

def request_product():
    nombre          = utils.read_input_simple_text("  * Nombre: ")
    cantidad        = utils.read_input_float("  * Cantidad: ", 0.0001, 1000000)
    medida          = utils.read_input_simple_text("  * Medida: ")
    precio_unitario = utils.read_input_float("  * Precio Unitario: ", 0, 1000000)
    precio_total    = cantidad*precio_unitario
    fecha           = utils.read_input_date("  * Fecha (Día/Mes/Año): ")
    return [nombre, cantidad, medida, precio_unitario, precio_total, fecha]

def request_and_insert_product(conn):
    while True:
        subprocess.run(["clear"])
        draw_tittle_border("REGISTRAR NUEVO PRODUCTO")
        conn.insert_product(request_product())
        respuesta = utils.read_input_yes_no("\n  >>> ¿Desea agregar otro producto (Si/No)?: ")
        if(respuesta.lower() in ['si', 's']):
            continue
        else:
            break

def main():
    db_path="sqlite_db"
    db_file="my_expenses.db"
    conn = sqlite_conn.Database(db_path, db_file)
    conn.connect()
    conn.create_products_table()

    while True:
        subprocess.run(["clear"])
        draw_tittle_border("REGISTRAR GASTOS DE PRODUCTOS")
        print("  1. Mostrar lista completa")
        print("  2. Registrar un producto")
        print("  3. Eliminar un producto")
        print("  4. Exportar a CSV")
        print("  5. Limpiar pantalla")
        print("  6. Salir")
        opcion = utils.read_input_integer("\n  * Opción >> ", 1, 6)
        if(opcion == 1):
            conn.validate_table_not_empty(show_table_product, "productos", "No hay datos para mostrar...")
        elif(opcion == 2):
            request_and_insert_product(conn)
        elif(opcion == 3):
            conn.validate_table_not_empty(show_product_deletion_menu, "productos", "No hay datos para eliminar...")
        elif(opcion == 4):
            conn.export_to_csv("productos")
        elif(opcion == 5):
            subprocess.run(["clear"])
        elif(opcion == 6):
            print("\n  Saliendo del programa...\n")
            time.sleep(0.25)
            subprocess.run(["clear"])
            break
        input("\n  >>> Presione ENTER para continuar <<<")
    conn.disconnect()

if __name__ == "__main__":
    main()
