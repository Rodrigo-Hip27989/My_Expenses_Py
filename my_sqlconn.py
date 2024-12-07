import sqlite3
import os
import csv
import re
import my_utils as utils
from classes.product import Product
from classes.path import Path

class Database:
    def __init__(self, dir="sqlite_db", file="my_expenses.db"):
        self.db_dir = dir
        self.db_file = file
        self.db_full_path = os.path.join(dir, file)
        os.makedirs(self.db_dir, exist_ok=True)
        self.connect()
        self.create_products_tbl()
        self.create_paths_tbl()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_full_path)
        except sqlite3.Error as e:
            print(f"\n   >>> Error al conectar a la base de datos: {e}")
            self.conn = None

    def get_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_full_path)
        return self.conn

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def cursor(self):
        if self.conn:
            return self.conn.cursor()
        else:
            return self.get_connection().cursor()

    def commit(self, c):
        if self.conn:
            self.conn.commit()
            c.close()

    def rollback(self):
        if self.conn:
            self.conn.rollback()
            print("\n  *** Operación cancelada ***")

    def create_products_tbl(self):
        sql_query = "CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, quantity TEXT, unit TEXT, price REAL, total REAL, date TEXT, category TEXT)"
        c = self.execute_query(sql_query)
        self.commit(c)

    def create_paths_tbl(self):
        sql_query = "CREATE TABLE IF NOT EXISTS paths (id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT NOT NULL, is_export BOOLEAN NOT NULL DEFAULT 0, is_import BOOLEAN NOT NULL DEFAULT 0)"
        c = self.execute_query(sql_query)
        self.commit(c)

    def execute_query(self, query, params=()):
        cursor = self.cursor()
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

    def fetch_one(self, query, params=()):
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchone()
        return None

    def get_headers(self, table_name, sql_query = None):
        if sql_query is None:
            sql_query = f"SELECT * FROM {table_name}"

        sql_query = sql_query.strip().lower()

        if '*' in sql_query:
            try:
                pragma_query = f"PRAGMA table_info({table_name});"
                columns_info = self.execute_query(pragma_query)
                if(columns_info is not None):
                    columns = [column[1] for column in columns_info]
                    return columns
            except Exception as e:
                print(f"Error al obtener las columnas de la tabla con PRAGMA: {e}")
                return []

        else:
            match = re.search(r"select\s+([\w_,\s]+)\s+from\s+", sql_query)
            if match:
                columns_str = match.group(1)
                columns = [col.strip() for col in columns_str.split(',')]
                return columns
            else:
                print("No se encontraron columnas explícitas en la instrucción SELECT.")
                return []

    def get_num_rows_table(self, table_name):
        c = self.execute_query(f"SELECT COUNT(*) Num FROM {table_name}")
        numero_columnas = c.fetchone()[0]
        c.close()
        return numero_columnas

    def is_table_empty(self, table_name):
        return (self.get_num_rows_table(table_name) == 0)

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
            _, name, qty, unit, _, total, date_, cat = found_item
            return Product(name=name, quantity=qty, unit=unit, total=total, date=date_, category=cat)
        else:
            return None

    def insert_product(self, product):
        sqlite_statement = '''INSERT INTO products (name, quantity, unit, price, total, date, category) VALUES (?, ?, ?, ?, ?, ?, ?)'''
        c = self.execute_query(sqlite_statement, product.get_db_values())
        self.confirm_transaction_database(c)

    def insert_path(self, table_paths, path, is_first_entry):
        if not is_first_entry:
            if(path.get_is_export()):
                self.execute_query(f"UPDATE {table_paths} SET is_export = 0")
            if(path.get_is_import()):
                self.execute_query(f"UPDATE {table_paths} SET is_import = 0")
        c = self.execute_query(f"INSERT INTO {table_paths} (path, is_export, is_import) VALUES (?, ?, ?)", path.get_db_values())
        self.confirm_transaction_database(c)

    def update_path(self, table_name, id_path, field):
        self.execute_query(f"UPDATE {table_name} SET {field} = 0")
        c = self.execute_query(f"UPDATE {table_name} SET {field} = 1 WHERE id = {id_path}")
        self.confirm_transaction_database(c)

    def update_product(self, table_name, id_prod, product_obj, confirm=False):
        params = product_obj.get_db_values() + [id_prod]
        query = f"UPDATE {table_name} SET name = ?, quantity = ?, unit = ?, price = ?, total = ?, date = ?, category = ? WHERE id = ?;"
        c = self.execute_query(query, params)
        if(confirm):
            self.confirm_transaction_database(c)
        else:
            self.commit(c)

    def delete_database(self):
        try:
            if os.path.exists(self.db_full_path):
                if os.path.isfile(self.db_full_path):
                    os.remove(self.db_full_path)
                    print(f"\n   >>> La base de datos ha sido eliminada!")
                else:
                    print("\n   >>> La ruta proporcionada no es un archivo válido!")
            else:
                print(f"\n   >>> No se encontró el archivo de base de datos en la ruta: {self.db_dir}")
        except Exception as e:
            print(f"\n   >>> Hubo un error al eliminar la base de datos: {e}")

    def export_table_to_csv(self, table_name, file_name, file_path):
        try:
            query_select = f"SELECT * FROM {table_name}"
            tbl_headers = self.get_headers(f"{table_name}")
            rows = self.fetch_all(query_select)
            with open(f"{file_path}/{file_name}", mode='w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(tbl_headers)
                csv_writer.writerows(rows)
            print(f"\n   >>> Exportación exitosa!!\n")
        except Exception as e:
            print(f"\n   >>> Error durante la exportación!! <<<\n   >>> {e}\n")

    def import_table_from_csv(self, table_name, file_name, file_path):
        try:
            tbl_headers = self.get_headers(f"{table_name}")
            with open(f"{file_path}/{file_name}", mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                csv_headers = next(csv_reader)

                if len(csv_headers) != len(tbl_headers):
                    raise ValueError(f"Las cabeceras del archivo CSV y la tabla no coinciden en número. "
                                     f"\n\n  * Num. cabeceras del archivo: {len(csv_headers)}\n  * Num. cabeceras de la tabla: {len(tbl_headers)}")

                tbl_headers_clean = [header.strip().lower() for header in tbl_headers]
                csv_headers_clean = [header.strip().lower() for header in csv_headers]

                if tbl_headers_clean != csv_headers_clean:
                    raise ValueError(f"Las cabeceras del archivo CSV y la tabla no coinciden"
                                     f"\n\n  * csv_headers: {csv_headers_clean}\n  * tbl_headers: {tbl_headers_clean}")

                for row in csv_reader:
                    row = [cell.strip() for cell in row]
                    while len(row) < len(csv_headers):
                        row.append("")
                    placeholders = ', '.join(['?' for _ in csv_headers])
                    query_insert = f"INSERT INTO {table_name} ({', '.join(csv_headers_clean)}) VALUES ({placeholders})"
                    c = self.execute_query(query_insert, row)
                    self.commit(c)
            print("\n   >>> Importación exitosa!!\n")
        except Exception as e:
            print(f"\n   >>> Error durante la importación!!\n   >>> {e}\n")
