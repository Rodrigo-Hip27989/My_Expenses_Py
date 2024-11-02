import os
import re
import time
import subprocess
import csv
import sqlite_conn
from fractions import Fraction
from datetime import datetime

def convert_to_float(input_string):
    try:
        return float(Fraction(input_string))
    except ValueError:
        return float(input_string)

def read_input_regex(patron, mensaje):
    input_varchar = input(mensaje)
    if(re.fullmatch(patron, input_varchar) is not None):
        return input_varchar
    else:
        raise ValueError(f"El valor '{input_varchar}' no es valido!")

def get_valid_data_varchar(patron, mensaje):
    input_varchar = ""
    while len(input_varchar.strip()) == 0:
        try: 
            input_varchar = read_input_regex(patron, mensaje)
        except ValueError as e:
            input_varchar = ""
            print(f"\n *** {e} ***\n")
    return input_varchar

def get_valid_data_numeric(mostrar_mensaje, minimo, maximo, patron, convert_func):
    numero = minimo - 1
    while not (minimo <= numero <= maximo):
        try:
            numero = convert_func(get_valid_data_varchar(patron, mostrar_mensaje))
        except ValueError:
            numero = minimo - 1
        if not (minimo <= numero <= maximo):
            print(f"\n  >>> El número debe estar en el rango [{minimo}-{maximo}] <<<\n")
    return numero

def get_valid_data_integer(mostrar_mensaje, minimo, maximo):
    regex_integer = r'^[1-9]\d*$'
    return get_valid_data_numeric(mostrar_mensaje, minimo, maximo, regex_integer, int)

def get_valid_data_float(mostrar_mensaje, minimo, maximo):
    regex_float = r'^(?!.*\/0)(-?\d+(\.\d+)?|-\d+/\d+|\d+/\d+)$'
    return get_valid_data_numeric(mostrar_mensaje, minimo, maximo, regex_float, convert_to_float)

def get_valid_data_simple_text(mensaje):
    regex_simple_text = r'^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ]+[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ()\.\-\_\ ]*'
    return get_valid_data_varchar(regex_simple_text, mensaje)

def get_valid_data_date(mensaje):
    regex_date = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$'
    return get_valid_data_varchar(regex_date, mensaje)

def get_valid_data_option_yes_no(mensaje):
    regex_options = r'^(SI|NO|Si|No|si|no|S|N|s|n)$'
    return get_valid_data_varchar(regex_options, mensaje)

def confirm_transaction_database(conn, c):
    respuesta = get_valid_data_option_yes_no("\n  >>> Desea continuar (Si/No)? ")
    if((respuesta == 'SI') or (respuesta == 'Si') or (respuesta == 'si') or (respuesta == 'S') or (respuesta == 's')):
        conn.commit(c)
    else:
        conn.rollback()
    input("\n  >>> Presione ENTER para continuar <<<")

def delete_product_using_id(conn):
    id_producto = get_valid_data_integer("\n  Ingrese el ID: ", 1, 1000000)
    c = conn.execute_query("DELETE FROM productos WHERE id=?", (id_producto, ))
    confirm_transaction_database(conn, c)
    c.close()

def delete_product_using_name(conn):
    nombre = get_valid_data_simple_text("\n  Ingrese el nombre: ")
    c = conn.execute_query("DELETE FROM productos WHERE nombre=?", (nombre, ))
    confirm_transaction_database(conn, c)
    c.close()

def delete_product_using_date(conn):
    fecha = get_valid_data_date("\n  Ingrese la fecha (Día/Mes/Año):")
    c = conn.execute_query("DELETE FROM productos WHERE fecha=?", (fecha, ))
    confirm_transaction_database(conn, c)
    c.close()

def draw_tittle_border(titulo):
    border = '=' * (len(titulo) + 7)
    print(f"\n  {border}\n  |  {titulo}  |\n  {border}\n")

def delete_in_database(conn):
    show_database_product(conn)
    draw_tittle_border("ELIMINAR UN PRODUCTO")
    print("  1. Usando su ID")
    print("  2. Todos los que coincidan con el NOMBRE")
    print("  3. Todos los que coincidan en cierta FECHA")
    print("  4. Limpiar pantalla")
    print("  5. Regresar")
    opcion = get_valid_data_integer("\n  * Opción >> ", 1, 5)
    if(opcion == 1):
        delete_product_using_id(conn)
    elif(opcion == 2):
        delete_product_using_name(conn)
    elif(opcion == 3):
        delete_product_using_date(conn)
    elif(opcion == 4):
        subprocess.run(["clear"])
        delete_in_database(conn)
    elif(opcion == 5):
        print("\n  Regresando...")
        time.sleep(1)

def get_num_rows_table_products(conn):
    c = conn.execute_query("SELECT COUNT(*) Num FROM productos")
    numero_columnas = c.fetchone()[0]
    c.close()
    return numero_columnas

def validate_and_delete_in_database(conn):
    if(get_num_rows_table_products(conn) > 0):
        delete_in_database(conn)
    else:
        print("\n       No hay datos para mostrar...")
        input("\n   >>> Presione ENTER para continuar <<<")

def insert_in_database(conn, producto):
    sqlite_statement = '''INSERT INTO productos (nombre, cantidad, medida, precio, total, fecha) VALUES (?, ?, ?, ?, ?, ?)'''
    c = conn.execute_query(sqlite_statement, producto)
    confirm_transaction_database(conn, c)
    c.close()

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

def draw_table_data(data, encabezados, headers_size):
    border = "   +" + "+".join(["-" * (hsize+2) for hsize in headers_size]) + "+"
    print(f"{border}\n   | " + " | ".join(f"{nombre.upper():<{hsize}}" for nombre, hsize in zip(encabezados, headers_size)) + f" |\n{border}")
    for row in data:
        print("   | " + " | ".join(f"{str(item):<{hsize}}" for item, hsize in zip(row, headers_size)) + " |")
    print(f"{border}")

def show_simple_data(data, encabezados):
    max_len = max(len(f"{row}") for row in data)
    border = '-' * (max_len+4)
    print(f"\n  {border}\n  | " + " | ".join(f"{str(nombre).upper()}" for nombre in encabezados) + f"  |\n  {border}")
    for row in data:
        simple_row = " | ".join(str(item) for item in row)
        print(f"  |  {simple_row}  |")
    print(f"  {border}\n")

def show_database_product(conn):
    table_name = "productos"
    sql_query = f"SELECT * FROM {table_name}"
    data = conn.fetch_all(sql_query)
    subprocess.run(["clear"])
    print("\n")
    terminal_size = os.get_terminal_size().columns
    encabezados = conn.get_headers(f"{table_name}")
    if(terminal_size>=77):
        headers_size = get_header_sizes(terminal_size)
        draw_table_data(data, encabezados, headers_size)
    else:
        show_simple_data(data, encabezados)
    input("\n   >>> Presione ENTER para continuar <<<")

def request_a_product():
    nombre          = get_valid_data_simple_text("  * Nombre: ")
    cantidad        = get_valid_data_float("  * Cantidad: ", 0.0001, 1000000)
    medida          = get_valid_data_simple_text("  * Medida: ")
    precio_unitario = get_valid_data_float("  * Precio Unitario: ", 0, 1000000)
    precio_total    = cantidad*precio_unitario
    fecha           = get_valid_data_date("  * Fecha (Día/Mes/Año): ")
    return [nombre, cantidad, medida, precio_unitario, precio_total, fecha]

def request_and_insert_product_list(conn):
    while True:
        subprocess.run(["clear"])
        draw_tittle_border("REGISTRAR NUEVO PRODUCTO")
        insert_in_database(conn, request_a_product())
        respuesta = get_valid_data_option_yes_no("\n  >>> ¿Desea agregar otro producto (Si/No)?: ")
        if((respuesta == 'SI') or (respuesta == 'Si') or (respuesta == 'si') or (respuesta == 'S') or (respuesta == 's')):
            continue
        else:
            break

def export_to_csv(conn, table_name):
    try:
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        file_name = f"{table_name.capitalize()}_{timestamp}.csv"
        query_select = f"SELECT * FROM {table_name}"
        headers = conn.get_headers(f"{table_name}")
        rows = conn.fetch_all(query_select)
        with open(file_name, mode='w', newline='', encoding='utf-8') as archivo_csv:
            escritor_csv = csv.writer(archivo_csv)
            escritor_csv.writerow(headers)
            escritor_csv.writerows(rows)
        print(f"\n   >>> Exportación '{file_name}' exitosa!! <<<")
    except Exception as e:
        print(f"\n   >>> Error durante la exportación!! <<<\n   *** {e} ***")
    input("\n   >>> Presione ENTER para continuar <<<")

def main():
    db_path="sqlite_db"
    db_file="my_expenses.db"
    conn = sqlite_conn.Database(db_path, db_file)
    conn.connect()
    conn.create_table()

    while True:
        subprocess.run(["clear"])
        draw_tittle_border("REGISTRAR GASTOS DE PRODUCTOS")
        print("  1. Mostrar lista completa")
        print("  2. Registrar un producto")
        print("  3. Eliminar un producto")
        print("  4. Exportar a CSV")
        print("  5. Limpiar pantalla")
        print("  6. Salir")
        opcion = get_valid_data_integer("\n  * Opción >> ", 1, 6)
        if(opcion == 1):
            show_database_product(conn)
        elif(opcion == 2):
            request_and_insert_product_list(conn)
        elif(opcion == 3):
            validate_and_delete_in_database(conn)
        elif(opcion == 4):
            export_to_csv(conn, "productos")
        elif(opcion == 5):
            subprocess.run(["clear"])
        elif(opcion == 6):
            print("\n  Saliendo del programa...\n")
            time.sleep(0.5)
            subprocess.run(["clear"])
            break
    conn.disconnect()

if __name__ == "__main__":
    main()
