
import time
import sqlite3
import subprocess

conn = sqlite3.connect("sqlite_db/my_expenses.db")

def create_table():
    c = conn.cursor()
    c.execute("CREATE TABLE if not exists productos (id integer PRIMARY KEY, nombre text, cantidad integer, medida text, precio_unitario real, precio_total real, fecha text)")
    conn.commit()

def validate_data_is_integer(mostrar_mensaje, minimo, maximo):
    numero = 0
    while True:
        try: 
            numero = int(input(mostrar_mensaje))
        except ValueError:
            print("\n  Usted debe ingresar un numero !!!\n")
            continue
        if(numero >=minimo):
            if(numero <= maximo):
                return numero
            else:
                print("\n  La cantidad debe ser menor a (10^12) !!!\n")
        elif(numero < minimo): 
            print(f"\n  La cantidad no puede ser negativo !!!\n")

def validate_data_is_float(mostrar_mensaje, minimo, maximo):
    numero = 0
    while True:
        try: 
            numero = float(input(mostrar_mensaje))
        except ValueError:
            print("\n  Usted debe ingresar un numero decimal !!!\n")
            continue
        if(numero >=minimo):
            if(numero <= maximo):
                return numero
            else:
                print("\n  La cantidad debe ser menor a (10^12) !!!\n")
        elif(numero < minimo): 
            print(f"\n  La cantidad no puede ser negativo !!!\n")

def validate_and_delete_in_database():    
    if(show_num_rows() > 0):
        delete_in_database()
    else: 
        print("\n  ** La base de datos esta vacia, no hay nada que hacer...\n")
        input("\n  Presione ENTER para continuar...\n")

def delete_in_database():
        print("\n  ** Elige una opción para continuar... **\n")
        print("  1. Eliminar un producto por medio de su ID")
        print("  2. Eliminar todos los productos con cierto NOMBRE")
        print("  3. Eliminar todos los productos en cierta FECHA")
        print("  4. Cancelar y regresar")
        opcion = validate_data_is_integer("\n  * Opción >> ", 1, 4)
        if(opcion == 1): 
            c = conn.cursor()
            id_producto = validate_data_is_integer("\n  Ingrese el ID del produto a eliminar: ", 1, 1000000000000)
            sqlite_statement = "DELETE FROM productos WHERE id=?"
            c.execute(sqlite_statement, (id_producto, ))
            conn.commit()
            print(f"\n  El número de filas afectadas fue: {c.rowcount}\n")
        elif(opcion == 2): 
            c = conn.cursor()
            nombre = input("\n  Ingrese el nombre del producto: ")
            sqlite_statement = "DELETE FROM productos WHERE nombre=?"
            c.execute(sqlite_statement, (nombre, ))
            conn.commit()
            print(f"\n   El número de filas afectadas fue: {c.rowcount}\n")
        elif(opcion == 3): 
            c = conn.cursor()
            fecha = input("\n  Ingrese una fecha: ")
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
    print("\n  ** Mostrando el contenido de la base de datos **\n")
    for row in data:
        print(f"  {row}")
    print("\n  ************************************************")
    input("\n  Presione ENTER para continuar...\n")

def show_num_rows():
    c = conn.cursor()
    c.execute("SELECT COUNT(*) Num FROM productos")
    numero_columnas = c.fetchone()[0]
    return numero_columnas

def show_producto(producto):
    print("\n  ======================\n  * Datos del Producto\n  ======================\n")
    [print(f"  * Atributo: {atributo}") for atributo in producto]

def request_a_product():
    print("\n  =========================== * Registrando un nuevo producto  ===========================\n")
    producto = []
    nombre          = input("  * Nombre del producto: ")
    cantidad        = validate_data_is_integer("  * Cantidad: ", 1, 1000000000000)
    medida          = input("  * Medida: ")
    precio_unitario = validate_data_is_float("  * Precio Unitario: ", 0, 1000000000000)
    precio_total    = cantidad*precio_unitario
    fecha           = input("  * Ingrese la fecha (Dia-Mes-Año): ")

    print("\n  * Desea continuar con la operación?")
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

        print("\n  * ¿Desea agregar un nuevo producto?")
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
        print("\n\n  ** Programa para realizar operaciones con base de datos (SQLite)\n")
        print("  1. Mostrar contenido de la base de datos")
        print("  2. Insertar un elemento en la base de datos")
        print("  3. Eliminar un elemento en la base de datos")
        print("  4. Limpiar pantalla")
        print("  5. Salir")
        opcion = validate_data_is_integer("\n  * Opción >> ", 1, 5)
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

