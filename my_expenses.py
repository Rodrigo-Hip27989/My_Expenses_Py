import os
import re
import time
import sqlite3
import subprocess
import csv
from fractions import Fraction

def create_folder(name_folder):
    if not os.path.exists(name_folder):
        os.makedirs(name_folder)

def create_db(name_folder, name_file_db):
    conn = sqlite3.connect(f"{name_folder}/{name_file_db}")
    create_table(conn)
    return conn

def create_table(conn):
    c = conn.cursor()
    c.execute("CREATE TABLE if not exists productos (id INTEGER PRIMARY KEY, nombre TEXT, cantidad REAL, medida TEXT, precio_unitario REAL, precio_total REAL, fecha TEXT)")
    conn.commit()
    c.close()

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
    regex_simple_text = r'^[a-zA-ZñÑ]+[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9()\.\-\_\ ]*'
    return get_valid_data_varchar(regex_simple_text, mensaje)

def get_valid_data_date(mensaje):
    regex_date = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$'
    return get_valid_data_varchar(regex_date, mensaje)

def get_valid_data_option_yes_no(mensaje):
    regex_options = r'^(SI|NO|Si|No|si|no|S|N|s|n)$'
    return get_valid_data_varchar(regex_options, mensaje)

def confirm_transaction_database(conn):
    respuesta = get_valid_data_option_yes_no("\n  >>> Desea continuar (Si/No)? ")
    c = conn.cursor()
    if((respuesta == 'SI') or (respuesta == 'Si') or (respuesta == 'si') or (respuesta == 'S') or (respuesta == 's')):
        conn.commit()
        if(c.rowcount > 0): 
            print("\n  *** Transacción Realizada Con Exito ***")
    else:
        conn.rollback()
        print("\n  *** Operación cancelada...***")
    input("\n  >>> Presione ENTER para continuar <<<")
    c.close()

def delete_product_using_id(conn):
    id_producto = get_valid_data_integer("\n  Ingrese el ID: ", 1, 1000000)
    c = conn.cursor()
    c.execute("DELETE FROM productos WHERE id=?", (id_producto, ))
    confirm_transaction_database(conn)
    c.close()

def delete_product_using_name(conn):
    nombre = get_valid_data_simple_text("\n  Ingrese el nombre: ")
    c = conn.cursor()
    c.execute("DELETE FROM productos WHERE nombre=?", (nombre, ))
    confirm_transaction_database(conn)
    c.close()

def delete_product_using_date(conn):
    fecha = get_valid_data_date("\n  Ingrese la fecha (Día/Mes/Año):")
    c = conn.cursor()
    c.execute("DELETE FROM productos WHERE fecha=?", (fecha, ))
    confirm_transaction_database(conn)
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
    c = conn.cursor()
    c.execute("SELECT COUNT(*) Num FROM productos")
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
    c = conn.cursor()
    sqlite_statement = '''INSERT INTO productos (nombre, cantidad, medida, precio_unitario, precio_total, fecha) VALUES (?, ?, ?, ?, ?, ?)'''
    c.execute(sqlite_statement, producto)
    confirm_transaction_database(conn)
    c.close()

def get_header_sizes(terminal_size):
    if(terminal_size >= 130):
        return [4, 28, 16, 26, 17, 17]
    elif((terminal_size >= 115) and (terminal_size < 130)):
        return [4, 24, 13, 22, 15, 15]
    elif((terminal_size >= 105) and (terminal_size < 115)):
        return [3, 22, 11, 19, 13, 13]
    elif((terminal_size >= 97) and (terminal_size < 105)):
        return [3, 19, 9, 17, 11, 11]
    elif((terminal_size >= 90) and (terminal_size < 97)):
        return [3, 16, 8, 12, 10, 10]
    else:
        return []

def draw_table_data(data, encabezados, headers_size):
    # DESEÑO DE BORDE
    borde = "   +" + "+".join(["-" * (hsize+2) for hsize in headers_size]) + "+"
    # ENCABEZADOS
    print(f"{borde}\n   | " + " | ".join(f"{nombre:<{hsize}}" for nombre, hsize in zip(encabezados, headers_size)) + f" |\n{borde}")
    # IMPRESION DE DATOS
    for row in data:
        print("   | " + " | ".join(f"{str(item):<{hsize}}" for item, hsize in zip(row, headers_size)) + " |")
    print(f"{borde}")

def show_unformated_data(data):
    border = '*' * (75)
    print(f"\n  {border}\n")
    [print(f"  |  {row}") for row in data]
    print(f"\n  {border}\n")

def show_database_product(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM productos")
    data = c.fetchall()
    c.close()
    subprocess.run(["clear"])
    print("\n")
    terminal_size = os.get_terminal_size().columns
    if(terminal_size>=90):
        encabezados = [desc[0] for desc in c.description]
        headers_size = get_header_sizes(terminal_size)
        draw_table_data(data, encabezados, headers_size)
    else:
        show_unformated_data(data)
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

def export_to_csv(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM productos")
    filas = c.fetchall()
    # Obtener los nombres de las columnas
    columnas = [desc[0] for desc in c.description]
    # Escribir los datos en un archivo CSV
    with open('My_List.csv', mode='w', newline='', encoding='utf-8') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        # Escribir los encabezados
        escritor_csv.writerow(columnas)
        # Escribir los datos
        escritor_csv.writerows(filas)
    input("\n   >>> Presione ENTER para continuar <<<")

def main():
    name_folder="sqlite_db"
    name_file_db="my_expenses.db"
    create_folder(name_folder)
    conn = create_db(name_folder, name_file_db)
    create_table(conn)
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
            export_to_csv(conn)
        elif(opcion == 5):
            subprocess.run(["clear"])
        elif(opcion == 6):
            print("\n  Saliendo del programa...\n")
            time.sleep(0.5)
            subprocess.run(["clear"])
            break
    conn.close()

main()
