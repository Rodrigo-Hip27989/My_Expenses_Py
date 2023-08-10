import re
import time
import sqlite3
import subprocess

conn = sqlite3.connect("sqlite_db/my_expenses.db")

def create_table():
    c = conn.cursor()
    c.execute("CREATE TABLE if not exists productos (id integer PRIMARY KEY, nombre text, cantidad integer, medida text, precio_unitario real, precio_total real, fecha text)")
    conn.commit()

def validate_data_match_regex(entrada, regex):
    pattern = re.compile(regex)
    match = pattern.findall(entrada)
    if(len(match) > 0):
        if(len(match[0]) == len(entrada)):
            return True
        else: 
            return False

def get_valid_data_varchar(mensaje, patron):
    nombre = ""
    while True:
        try: 
            input_varchar = input(mensaje)
            input_varchar_valid = validate_data_match_regex(input_varchar, patron)
            if(input_varchar_valid):
                return input_varchar
            else:
                print(f"\n  ==> La entrada no es valida <==\n")
        except ValueError:
            print("\n  ==> Error! El tipo de dato introducido no es valido !!!\n")
            continue

def get_valid_data_integer(mostrar_mensaje, minimo, maximo):
    numero = 0
    while True:
        try: 
            numero = int(input(mostrar_mensaje))
            if(numero >=minimo and numero <= maximo):
                return numero
            else:
                print(f"\n  ==> El número debe estar en el rango [{minimo}-{maximo}] <==\n")
        except ValueError:
            print("\n  ==> Error! El tipo de dato introducido no es valido !!!\n")
            continue

def get_valid_data_float(mostrar_mensaje, minimo, maximo):
    numero = 0
    while True:
        try: 
            numero = float(input(mostrar_mensaje))
            if(numero >= minimo and numero <= maximo):
                return numero
            else:
                print(f"\n  ==> El número debe estar en el rango [{minimo}-{maximo}] <==\n")
        except ValueError:
            print("\n  ==> Error! El tipo de dato introducido no es valido !!! <==\n")
            continue

def confirm_transaction_database(conn, c):
    respuesta = get_valid_data_varchar("\n  >>> Desea continuar (Si/No)? ", '(Si|No|S|N|si|no|s|n)')
    if((respuesta == 'Si') or (respuesta == 'si') or (respuesta == 'S') or (respuesta == 's')):
        conn.commit()
        if(c.rowcount > 0): 
            print("\n  *** Transacción Realizada Con Exito ***")
    else:
        conn.rollback()
        print("\n  Operación cancelada...")
    input("\n  Presione ENTER para continuar...")

def delete_product_using_id(): 
    c = conn.cursor()
    id_producto = get_valid_data_integer("\n  Ingrese el ID: ", 1, 1000000000000)
    c.execute("DELETE FROM productos WHERE id=?", (id_producto, ))
    confirm_transaction_database(conn, c)

def delete_product_using_name(): 
    c = conn.cursor()
    nombre = get_valid_data_varchar("\n  Ingrese el nombre: ", '^[a-zA-Z]+[a-zA-Z0-9\.\-\_\ ]*')
    c.execute("DELETE FROM productos WHERE nombre=?", (nombre, ))
    confirm_transaction_database(conn, c)

def delete_product_using_date(): 
    c = conn.cursor()
    fecha = get_valid_data_varchar("\n  Ingrese la fecha (Día/Mes/Año):", '[0-3][0-9]\/[0-1][0-9]\/20[0-2][0-9]')
    c.execute("DELETE FROM productos WHERE fecha=?", (fecha, ))
    confirm_transaction_database(conn, c)

def delete_in_database():
    subprocess.run(["clear"])
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
        input("\n  >>> La base de datos esta vacia, ho hay nada que hacer...\n\n  Presione ENTER para continuar...")

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
    print("\n  ================================", end='')
    print("\n  |  Registrando Nuevo Producto  |", end='')
    print("\n  ================================", end='\n\n')
    producto = []
    nombre          = get_valid_data_varchar("  * Nombre: ", '^[a-zA-Z]+[a-zA-Z0-9\.\-\_\ ]*')
    cantidad        = get_valid_data_integer("  * Cantidad: ", 1, 1000000000000)
    medida          = get_valid_data_varchar("  * Medida: ", '^[a-zA-Z]+[a-zA-Z0-9\.\-\_\ ]*')
    precio_unitario = get_valid_data_float("  * Precio Unitario: ", 0, 1000000000000)
    precio_total    = cantidad*precio_unitario
    fecha           = get_valid_data_varchar("  * Fecha (Día/Mes/Año): ", '[0-3][0-9]\/[0-1][0-9]\/20[0-2][0-9]')
    return [nombre, cantidad, medida, precio_unitario, precio_total, fecha]

def request_and_insert_product_list(): 
    subprocess.run(["clear"])
    while True:
        nuevo_producto = request_a_product()
        insert_in_database(nuevo_producto)

        respuesta = get_valid_data_varchar("\n  >>> ¿Desea agregar otro producto (Si/No)?: ", '(Si|No|S|N|si|no|s|n)')
        if((respuesta == 'Si') or (respuesta == 'si') or (respuesta == 'S') or (respuesta == 's')):
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
