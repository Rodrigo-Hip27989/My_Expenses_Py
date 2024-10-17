import re
import time
import sqlite3
import subprocess
from fractions import Fraction
import os

name_folder="sqlite_db"
if not os.path.exists(name_folder):
    os.makedirs(name_folder)
conn = sqlite3.connect("sqlite_db/my_expenses.db")

def create_table():
    c = conn.cursor()
    c.execute("CREATE TABLE if not exists productos (id INTEGER PRIMARY KEY, nombre TEXT, cantidad REAL, medida TEXT, precio_unitario REAL, precio_total REAL, fecha TEXT)")
    conn.commit()

def convertir_a_flotante(input_string):
    try:
        # Intentar convertir la entrada como una fracción
        return float(Fraction(input_string))
    except ValueError:
        # Si falla, intentar convertir como float directamente
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
            print(f"\n *** {e} ***\n");
    return input_varchar

def get_valid_data_integer(mostrar_mensaje, minimo, maximo):
    regex_numero_entero = r'^[1-9]\d*$'
    numero = minimo-1
    while (numero < minimo or numero > maximo):
        numero = int(get_valid_data_varchar(regex_numero_entero, mostrar_mensaje))
        if(numero >=minimo and numero <= maximo):
            break
        else:
            numero = minimo-1
            print(f"\n  ==> El número debe estar en el rango [{minimo}-{maximo}] <==\n")
    return numero

def get_valid_data_float(mostrar_mensaje, minimo, maximo):
    regex_numero_entero = r'^(-?\d+(\.\d+)?|-\d+/\d+|\d+/\d+)$'
    numero = minimo-1
    while (numero < minimo or numero > maximo):
        numero = convertir_a_flotante(get_valid_data_varchar(regex_numero_entero, mostrar_mensaje))
        if(numero >=minimo and numero <= maximo):
            break
        else:
            numero = minimo-1
            print(f"\n  ==> El número debe estar en el rango [{minimo}-{maximo}] <==\n")
    return numero

def get_valid_data_simple_text(mensaje):
    patron = r'^[a-zA-ZñÑ]+[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9()\.\-\_\ ]*'
    return get_valid_data_varchar(patron, mensaje)

def get_valid_data_fecha(mensaje):
    patron = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$'
    return get_valid_data_varchar(patron, mensaje)

def get_valid_data_confirmacion(mensaje):
    patron = r'^(SI|NO|Si|No|si|no|S|N|s|n)$'
    return get_valid_data_varchar(patron, mensaje)

def confirm_transaction_database(conn, c):
    respuesta = get_valid_data_confirmacion("\n  >>> Desea continuar (Si/No)? ")
    if((respuesta == 'SI') or (respuesta == 'Si') or (respuesta == 'si') or (respuesta == 'S') or (respuesta == 's')):
        conn.commit()
        if(c.rowcount > 0): 
            print("\n  *** Transacción Realizada Con Exito ***")
    else:
        conn.rollback()
        print("\n  *** Operación cancelada...***")
    input("\n  ==> Presione ENTER para continuar...")

def delete_product_using_id(): 
    c = conn.cursor()
    id_producto = get_valid_data_integer("\n  Ingrese el ID: ", 1, 1000000)
    c.execute("DELETE FROM productos WHERE id=?", (id_producto, ))
    confirm_transaction_database(conn, c)

def delete_product_using_name(): 
    c = conn.cursor()
    nombre = get_valid_data_simple_text("\n  Ingrese el nombre: ")
    c.execute("DELETE FROM productos WHERE nombre=?", (nombre, ))
    confirm_transaction_database(conn, c)

def delete_product_using_date(): 
    c = conn.cursor()
    fecha = get_valid_data_fecha("\n  Ingrese la fecha (Día/Mes/Año):")
    c.execute("DELETE FROM productos WHERE fecha=?", (fecha, ))
    confirm_transaction_database(conn, c)

def delete_in_database():
    show_database_product()
    print("\n  =======================================", end='')
    print("\n  |  Opciones Para Eliminar El Producto |", end='')
    print("\n  =======================================", end='\n\n')
    print("  1. Eliminar producto por medio del ID")
    print("  2. Eliminar todos los productos con cierto NOMBRE")
    print("  3. Eliminar todos los productos en cierta FECHA")
    print("  4. Limpiar pantalla")
    print("  5. Regresar")
    opcion = get_valid_data_integer("\n  * Opción >> ", 1, 5)
    if(opcion == 1):
        delete_product_using_id()
    elif(opcion == 2):
        delete_product_using_name()
    elif(opcion == 3):
        delete_product_using_date()
    elif(opcion == 4):
        subprocess.run(["clear"])
        delete_in_database()
    elif(opcion == 5):
        print("\n  Regresando...")
        time.sleep(1)

def get_num_rows_table_products():
    c = conn.cursor()
    c.execute("SELECT COUNT(*) Num FROM productos")
    numero_columnas = c.fetchone()[0]
    return numero_columnas

def validate_and_delete_in_database():
    if(get_num_rows_table_products() > 0):
        delete_in_database()
    else:
        print("\n  >>> La base de datos esta vacia, ho hay nada que hacer...")
        input("\n      Presione ENTER para continuar...")

def insert_in_database(producto):
    c = conn.cursor()
    sqlite_statement = '''INSERT INTO productos (nombre, cantidad, medida, precio_unitario, precio_total, fecha) VALUES (?, ?, ?, ?, ?, ?)'''
    c.execute(sqlite_statement, producto)
    confirm_transaction_database(conn, c)

def show_database_product():
    c = conn.cursor()
    c.execute("SELECT * FROM productos")
    data = c.fetchall()
    subprocess.run(["clear"])
    print("\n\n  >>> Mostrando el contenido de la base de datos...")
    print("\n  --------------------------------------------------------\n")
    [print(f"  |  {row}") for row in data]
    print("\n  --------------------------------------------------------\n")
    input("\n  Presione ENTER para continuar...")

def request_a_product():
    nombre          = get_valid_data_simple_text("  * Nombre: ")
    cantidad        = get_valid_data_float("  * Cantidad: ", 0.0001, 1000000)
    medida          = get_valid_data_simple_text("  * Medida: ")
    precio_unitario = get_valid_data_float("  * Precio Unitario: ", 0, 1000000)
    precio_total    = cantidad*precio_unitario
    fecha           = get_valid_data_fecha("  * Fecha (Día/Mes/Año): ")
    return [nombre, cantidad, medida, precio_unitario, precio_total, fecha]

def request_and_insert_product_list(): 
    while True:
        subprocess.run(["clear"])
        print("\n  ================================", end='')
        print("\n  |  Registrando Nuevo Producto  |", end='')
        print("\n  ================================", end='\n\n')
        insert_in_database(request_a_product())
        respuesta = get_valid_data_confirmacion("\n  >>> ¿Desea agregar otro producto (Si/No)?: ")
        if((respuesta == 'SI') or (respuesta == 'Si') or (respuesta == 'si') or (respuesta == 'S') or (respuesta == 's')):
            continue
        else:
            break

def main():
    create_table()
    while True:
        subprocess.run(["clear"])
        print("\n  ====================================", end='')
        print("\n  |  Programa Para Registrar Gastos  |", end='')
        print("\n  ====================================", end='\n\n')
        print("  1. Mostrar contenido de la base de datos")
        print("  2. Insertar un elemento en la base de datos")
        print("  3. Eliminar un elemento en la base de datos")
        print("  4. Limpiar pantalla")
        print("  5. Salir")
        opcion = get_valid_data_integer("\n  * Opción >> ", 1, 5)
        if(opcion == 1):
            show_database_product()
        elif(opcion == 2):
            request_and_insert_product_list()
        elif(opcion == 3):
            validate_and_delete_in_database()
        elif(opcion == 4):
            subprocess.run(["clear"])
        elif(opcion == 5):
            print("\n  Saliendo del programa...\n")
            time.sleep(1)
            break
    conn.close()

main()
