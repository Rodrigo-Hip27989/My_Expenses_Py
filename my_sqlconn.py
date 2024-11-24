import sqlite3
import os
import csv
import my_utils as utils
from classes.product import Product
from classes.path import Path

class Database:
    def __init__(self, path, file):
        self.db_path = path
        self.db_file = file
        os.makedirs(self.db_path, exist_ok=True)
        self.conn = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(f"{self.db_path}/{self.db_file}")
        except sqlite3.Error as e:
            print(f"\n   >>> Error al conectar a la base de datos: {e}")

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def cursor(self):
        if self.conn:
            return self.conn.cursor()

    def commit(self, c):
        if self.conn:
            self.conn.commit()
            c.close()

    def rollback(self):
        if self.conn:
            self.conn.rollback()
            print("\n  *** Operación cancelada ***")

    def create_products_tbl(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, quantity REAL, unit TEXT, price REAL, total REAL, date TEXT)")
        self.conn.commit()
        c.close()


    def create_paths_tbl(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS paths (id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT NOT NULL, is_export BOOLEAN NOT NULL DEFAULT 0, is_import BOOLEAN NOT NULL DEFAULT 0)")
        self.conn.commit()
        c.close()

    def execute_query(self, query, params=()):
        if self.conn is None:
            print("\n   >>> Error: No hay conexión a la base de datos.")
            return None

        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor
        except sqlite3.Error as e:
            print(f"\n   >>> Error al ejecutar la consulta: \n   >>> {e}")
            return None

    def fetch_all(self, query, params=()):
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchall()
        return []

    def get_headers(self, table_name):
        query = f"PRAGMA table_info({table_name})"
        cursor = self.execute_query(query)
        if cursor:
            return [desc[1] for desc in cursor.fetchall()]
        return []

    def get_num_rows_table(self, table_name):
        c = self.execute_query(f"SELECT COUNT(*) Num FROM {table_name}")
        numero_columnas = c.fetchone()[0]
        c.close()
        return numero_columnas

    def validate_table_not_empty(self, message_if_empty, operation, table_name, *args):
        if self.get_num_rows_table(table_name) > 0:
            operation(self, table_name, *args)
        else:
            print(f"\n      {message_if_empty}")

    def confirm_transaction_database(self, c):
        continuar = utils.read_input_continue_confirmation()
        if(continuar.lower() in ['si', 's']):
            self.commit(c)
            print(f"\n  >>> Filas modificadas: {c.rowcount} <<<")
        else:
            self.rollback()

    def delete_item(self, table_name, field, value):
        query_delete = f"DELETE FROM {table_name} WHERE {field}=?"
        c = self.execute_query(query_delete, (value,))
        self.confirm_transaction_database(c)
        c.close()

    def find_item(self, table_name, field, value):
        query_select = f"SELECT * FROM {table_name} WHERE {field}=? LIMIT 1"
        found_item = self.execute_query(query_select, (value,)).fetchone()
        if(found_item is not None and found_item != []):
            return found_item
        else:
            print(f"\n   *** Ningun elemento con el {field} = {value} fue encontrado ***")
        return None

    def find_path(self, table_name, field, value):
        found_item = self.find_item(table_name, field, value)
        if(found_item is not None and found_item != []):
            _, *found_path = found_item
            return Path(*found_path)
        else:
            return None

    def find_product(self, table_name, field, value):
        found_item = self.find_item(table_name, field, value)
        if(found_item is not None and found_item != []):
            _, *found_product = found_item
            return Product(*found_product)
        else:
            return None

    def insert_product(self, product):
        sqlite_statement = '''INSERT INTO products (name, quantity, unit, price, total, date) VALUES (?, ?, ?, ?, ?, ?)'''
        c = self.execute_query(sqlite_statement, product.get_db_values())
        self.confirm_transaction_database(c)
        c.close()

    def insert_path(self, table_paths, path, is_first_entry):
        if not is_first_entry:
            if(path.get_is_export()):
                self.execute_query(f"UPDATE {table_paths} SET is_export = 0")
            if(path.get_is_import()):
                self.execute_query(f"UPDATE {table_paths} SET is_import = 0")
        c = self.execute_query(f"INSERT INTO {table_paths} (path, is_export, is_import) VALUES (?, ?, ?)", path.get_db_values())
        self.confirm_transaction_database(c)
        c.close()

    def update_path(self, table_name, id_path, field):
        self.execute_query(f"UPDATE {table_name} SET {field} = 0")
        c = self.execute_query(f"UPDATE {table_name} SET {field} = 1 WHERE id = {id_path}")
        self.confirm_transaction_database(c)

    def delete_database(self):
        try:
            db_full_path = os.path.join(self.db_path, self.db_file)
            if os.path.exists(db_full_path):
                if os.path.isfile(db_full_path):
                    os.remove(db_full_path)
                    print(f"\n   >>> La base de datos ha sido eliminada!")
                else:
                    print("\n   >>> La ruta proporcionada no es un archivo válido!")
            else:
                print(f"\n   >>> No se encontró el archivo de base de datos en la ruta: {self.db_path}")
        except Exception as e:
            print(f"\n   >>> Hubo un error al eliminar la base de datos: {e}")

    def export_table_to_csv(self, table_name, file_name, file_path):
        try:
            query_select = f"SELECT * FROM {table_name}"
            headers = self.get_headers(f"{table_name}")
            rows = self.fetch_all(query_select)
            with open(f"{file_path}/{file_name}", mode='w', newline='', encoding='utf-8') as archivo_csv:
                escritor_csv = csv.writer(archivo_csv)
                escritor_csv.writerow(headers)
                escritor_csv.writerows(rows)
            print(f"\n   >>> Exportación exitosa!!\n")
            print(f"   * Nombre: {file_name}")
            print(f"   * Ruta:   {file_path}")
        except Exception as e:
            print(f"\n   >>> Error durante la exportación!! <<<\n   >>> {e}\n")

    def import_table_from_csv(self, table_name, file_name, file_path):
        try:
            headers_tbl = self.get_headers(f"{table_name}")
            with open(f"{file_path}/{file_name}", mode='r', encoding='utf-8') as archivo_csv:
                lector_csv = csv.reader(archivo_csv)
                headers_csv = next(lector_csv)
                if(len(headers_csv) != len(headers_tbl)):
                    raise ValueError("Las cabeceras del archivo y la tabla no coinciden !!!")
                for fila in lector_csv:
                    placeholders = ', '.join(['?' for _ in headers_csv])
                    query_insert = f"INSERT INTO {table_name} ({', '.join(headers_csv)}) VALUES ({placeholders})"
                    c = self.execute_query(query_insert, fila)
                    self.commit(c)
            print("\n   >>> Importación exitosa!!\n")
        except Exception as e:
            print(f"\n   >>> Error durante la importación!!\n   >>> {e}\n")
