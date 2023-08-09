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

def validate_and_delete_in_database():    
    if(show_num_rows() > 0):
        delete_in_database()
    else:
        input("\n  >>> La base de datos esta vacia, ho hay nada que hacer...\n  Presione ENTER para continuar...\n")

def delete_in_database():
        print("\n  =======================================", end='')
        print("\n  |  Opciones Para Eliminar El Producto |", end='')
        print("\n  =======================================", end='\n\n')
        print("  1. Eliminar producto por medio del ID")
        print("  2. Eliminar todos los productos con cierto NOMBRE")
        print("  3. Eliminar todos los productos en cierta FECHA")
        print("  4. Cancelar y regresar")
        opcion = get_valid_data_integer("\n  * Opción >> ", 1, 4)
        if(opcion == 1): 
            c = conn.cursor()
            id_producto = get_valid_data_integer("\n  Ingrese el ID: ", 1, 1000000000000)
            sqlite_statement = "DELETE FROM productos WHERE id=?"
            c.execute(sqlite_statement, (id_producto, ))
            conn.commit()
            print(f"\n  El número de filas afectadas fue: {c.rowcount}\n")
        elif(opcion == 2): 
            c = conn.cursor()
            nombre = get_valid_data_varchar("\n  Ingrese el nombre: ", '^[a-zA-Z]+[a-zA-Z0-9\.\-\_\ ]*')
            sqlite_statement = "DELETE FROM productos WHERE nombre=?"
            c.execute(sqlite_statement, (nombre, ))
            conn.commit()
            print(f"\n   El número de filas afectadas fue: {c.rowcount}\n")
        elif(opcion == 3): 
            c = conn.cursor()
            fecha = get_valid_data_varchar("\n  Ingrese la fecha (Día/Mes/Año):", '[0-3][0-9]\/[0-1][0-9]\/20[0-2][0-9]')
            sqlite_statement = "DELETE FROM productos WHERE fecha=?"
            c.execute(sqlite_statement, (fecha, ))
            conn.commit()
            print(f"\n  El número de filas afectadas fue: {c.rowcount}\n")
        elif(opcion == 4):
            print("\n  Cancelando operación...\n")
            time.sleep(1.5)
        input("\n  Presione ENTER para continuar...\n")

def insert_in_database(lista_productos):
    c = conn.cursor()
    for producto in lista_productos:
        sqlite_statement = '''INSERT INTO productos (nombre, cantidad, medida, precio_unitario, precio_total, fecha) VALUES (?, ?, ?, ?, ?, ?)'''
        c.execute(sqlite_statement, producto)
    conn.commit()

def show_database():
    c = conn.cursor()
    c.execute("SELECT * FROM productos")
    data = c.fetchall()
    print("\n\n  >>> Mostrando el contenido de la base de datos...")
    print("\n  --------------------------------------------------------\n")
    for row in data:
        print(f"  |  {row}")
    print("\n  --------------------------------------------------------\n")
    input("\n  Presione ENTER para continuar...\n")

def show_num_rows():
    c = conn.cursor()
    c.execute("SELECT COUNT(*) Num FROM productos")
    numero_columnas = c.fetchone()[0]
    return numero_columnas

def show_producto(producto):
    print("\n  ========================", end='')
    print("\n  |  Datos Del Producto  |", end='')
    print("\n  ========================", end='\n\n')
    [print(f"  * Atributo: {atributo}") for atributo in producto]

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

    print("\n  >>> Desea continuar con la operación?")
    if(input("    (Y/N): ") == 'Y'):
        return [nombre, cantidad, medida, precio_unitario, precio_total, fecha]
    else:
        return []

def request_product_list(): 
    lista_productos = []

    continuar = True
    while(continuar == True):
        nuevo_producto = request_a_product()
        if(nuevo_producto != []):
            lista_productos.append(nuevo_producto)

        print("\n  >>> ¿Desea agregar un nuevo producto?")
        if(input("    (Y/N): ") == 'Y'):
            continuar = True
        else:
            continuar = False
    return lista_productos

def main():
    create_table()
    continuar = True
    while(continuar): 
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
            subprocess.run(["clear"])
            show_database()
        elif(opcion == 2):
            subprocess.run(["clear"])
            insert_in_database(request_product_list())
        elif(opcion == 3):
            subprocess.run(["clear"])
            validate_and_delete_in_database()
        elif(opcion == 4):
            subprocess.run(["clear"])
        elif(opcion == 5): 
            subprocess.run(["clear"])
            print("\n  Saliendo del programa...\n")
            time.sleep(1)
            continuar = False
    conn.close()

main()
