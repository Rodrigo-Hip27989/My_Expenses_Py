import sqlite3
import os
import csv
import my_utils as utils

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
            print(f"Error al conectar a la base de datos: {e}")

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
        c.execute("CREATE TABLE IF NOT EXISTS productos (id INTEGER PRIMARY KEY, nombre TEXT, cantidad REAL, medida TEXT, precio REAL, total REAL, fecha TEXT)")
        self.conn.commit()
        c.close()


    def paths_tbl(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS paths (id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT NOT NULL, is_export BOOLEAN NOT NULL DEFAULT 0, is_import BOOLEAN NOT NULL DEFAULT 0)")
        self.conn.commit()
        c.close()

    def execute_query(self, query, params=()):
        if self.conn is None:
            print("Error: No hay conexión a la base de datos.")
            return None

        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor
        except sqlite3.Error as e:
            print(f"Error al ejecutar la consulta: {e}")
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

    def validate_table_not_empty(self, operation, table_name, message_if_empty, *args):
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

    def delete_item(self, table_name, field_name, get_value_func, *args):
        value = get_value_func(f"\n  * Ingrese el {field_name}: ", *args)
        query = f"DELETE FROM {table_name} WHERE {field_name}=?"
        c = self.execute_query(query, (value,))
        self.confirm_transaction_database(c)
        c.close()

    def insert_product(self, producto):
        sqlite_statement = '''INSERT INTO productos (nombre, cantidad, medida, precio, total, fecha) VALUES (?, ?, ?, ?, ?, ?)'''
        c = self.execute_query(sqlite_statement, producto)
        self.confirm_transaction_database(c)
        c.close()

    def delete_path(self, table_name, field_name, get_value_func, *args):
        input_id = get_value_func(f"\n  * Ingrese el {field_name}: ", *args)
        query_select = f"SELECT * FROM {table_name} WHERE {field_name}=?"
        c = self.execute_query(query_select, (input_id,))
        path_found = c.fetchone()
        if(path_found != None):
            if(path_found[2] == 1 or path_found[3] == 1):
                print(f"\n  *** No es posible eliminar una ruta csv en uso***")
            else:
                query_delete = f"DELETE FROM {table_name} WHERE {field_name}=?"
                c2 = self.execute_query(query_delete, (input_id,))
                self.confirm_transaction_database(c2)
                c2.close()
        else:
            print(f"\n  *** No se encontro el ID ingresado ***")
        c.close()

    def insert_path(self, table_name, request_path):
        num_rows = self.get_num_rows_table(f"{table_name}")
        is_first_entry = (num_rows == 0)
        path = request_path(is_first_entry)
        if(num_rows > 0):
            if(path[1] == 1):
                self.execute_query(f"UPDATE {table_name} SET is_export = 0")
            if(path[2] == 1):
                self.execute_query(f"UPDATE {table_name} SET is_import = 0")
        c = self.execute_query(f"INSERT INTO {table_name} (path, is_export, is_import) VALUES (?, ?, ?)", path)
        self.confirm_transaction_database(c)
        c.close()

    def export_csv(self, table_name, file_name, path):
        try:
            query_select = f"SELECT * FROM {table_name}"
            headers = self.get_headers(f"{table_name}")
            rows = self.fetch_all(query_select)
            with open(f"{path}/{file_name}", mode='w', newline='', encoding='utf-8') as archivo_csv:
                escritor_csv = csv.writer(archivo_csv)
                escritor_csv.writerow(headers)
                escritor_csv.writerows(rows)
            print(f"\n   >>> Exportación exitosa!!\n")
            print(f"   * Nombre: {file_name}")
            print(f"   * Ruta:   {path}")
        except Exception as e:
            print(f"\n   >>> Error durante la exportación!! <<<\n   *** {e} ***")
