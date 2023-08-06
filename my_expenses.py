
import time
import sqlite3
import subprocess

conn = sqlite3.connect("sqlite_db/my_expenses.db")

def create_table():
    c = conn.cursor()
    c.execute("CREATE TABLE if not exists productos (id integer PRIMARY KEY, nombre text, cantidad integer, medida text, precio_unitario real, precio_total real, fecha text)")
    conn.commit()

def validate_option_num(minimo, maximo):
    numero = 0
    while True:
        try: 
            numero = int(input("\n  * Opción >> "))
        except ValueError:
            print("\n  Usted debe ingresar una cantidad numerica !!!")
            continue
        if(numero >=minimo and numero <=maximo): 
            return numero
        else: 
            print("\n  El número ingresado no es valido...")

def validate_and_delete_in_database():    
    if(show_num_rows() > 0):
        show_database()
        delete_in_database()
    else: 
        print("\n  ** La base de datos esta vacia, no hay nada que hacer...\n")
        time.sleep(3)

def delete_in_database():
        print("\n  ** Elige una opción para continuar... **\n")
        print("  1. Eliminar un producto por medio de su ID")
        print("  2. Eliminar todos los productos con cierto NOMBRE")
        print("  3. Eliminar todos los productos en cierta FECHA")
        print("  4. Cancelar y regresar")
        opcion = validate_option_num(1, 4)
        if(opcion == 1): 
            c = conn.cursor()
            id_producto = int(input("\n  Ingrese el ID del produto a eliminar: "))
            sqlite_statement = "DELETE FROM productos WHERE id=?"
            c.execute(sqlite_statement, (id_producto, ))
            conn.commit()
        elif(opcion == 2): 
            c = conn.cursor()
            nombre = input("\n  Ingrese el nombre del producto: ")
            sqlite_statement = "DELETE FROM productos WHERE nombre=?"
            c.execute(sqlite_statement, (nombre, ))
            conn.commit()
        elif(opcion == 3): 
            c = conn.cursor()
            fecha = input("\n  Ingrese una fecha: ")
            sqlite_statement = "DELETE FROM productos WHERE fecha=?"
            c.execute(sqlite_statement, (fecha, ))
            conn.commit()
        elif(opcion == 4):
            print("\n  Cancelando operación...\n")
            time.sleep(1.5)

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

def show_num_rows():
    c = conn.cursor()
    c.execute("SELECT COUNT(*) Num FROM productos")
    numero_columnas = c.fetchone()[0]
    return numero_columnas

def show_producto(producto):
    print("\n  ======================\n  * Datos del Producto\n  ======================\n")
    [print(f"  * Atributo: {atributo}") for atributo in producto]

def pedir_un_producto():
    print("\n  =========================== * Ingresando Nuevos Datos  ===========================\n")
    producto = []
    nombre          = input("  * Nombre del producto: ")
    cantidad        = int(input("  * Cantidad: "))
    medida          = input("  * Medida: ")
    precio_unitario = float(input("  * Precio Unitario: "))
    precio_total    = cantidad*precio_unitario
    fecha           = input("  * Ingrese la fecha (Dia-Mes-Año): ")
    return [nombre, cantidad, medida, precio_unitario, precio_total, fecha]

def pedir_lista_productos(): 
    lista_productos = []

    continuar = True
    while(continuar == True):
        lista_productos.append(pedir_un_producto())

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
        opcion = validate_option_num(1, 5)
        if(opcion == 1): 
            subprocess.run(["clear"])
            show_database()
            time.sleep(5)
        elif(opcion == 2):
            subprocess.run(["clear"])
            insert_in_database(pedir_lista_productos())
        elif(opcion == 3):
            subprocess.run(["clear"])
            delete_in_database()
        elif(opcion == 4):
            subprocess.run(["clear"])
        elif(opcion == 5): 
            subprocess.run(["clear"])
            print("\n  Saliendo del programa...\n")
            time.sleep(1.5)
            continuar = False
    conn.close()

main()

