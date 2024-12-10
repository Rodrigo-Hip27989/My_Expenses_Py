import sqlite3
import os
import csv
import re
import time
import utils.various as utils
import utils.input_validations as valid
from models.product import Product
from models.path import Path

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
            self.conn.row_factory = sqlite3.Row
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

                if columns_info:
                    columns = [column['name'] for column in columns_info]
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
        row = self.fetch_one(f"SELECT COUNT(*) as count FROM {table_name}")
        if row:
            return row['count']
        else:
            return 0

    def is_table_empty(self, table_name):
        return (self.get_num_rows_table(table_name) == 0)

    def validate_table_not_empty(self, message_if_empty, operation, table_name, *args):
        if self.get_num_rows_table(table_name) > 0:
            operation(self, table_name, *args)
            input("\n   >>> Presione ENTER para continuar <<<")
        else:
            print(f"\n      {message_if_empty}")
            time.sleep(1)

    def confirm_transaction_database(self, c):
        continuar = valid.read_answer_continue()
        if(continuar.lower() in ['si', 's']):
            self.commit(c)
            print(f"\n  >>> Filas modificadas: {c.rowcount} <<<")
        else:
            self.rollback()

    def delete_item(self, table_name, field, value):
        query_delete = f"DELETE FROM {table_name} WHERE {field}=?"
        c = self.execute_query(query_delete, (value,))
        self.confirm_transaction_database(c)

    def find_item(self, table_name, field, value, msg=""):
        query_select = f"SELECT * FROM {table_name} WHERE {field}=? LIMIT 1"
        found_item = self.fetch_one(query_select, (value,))
        if(found_item is not None and found_item != []):
            return found_item
        else:
            if msg.strip() != "":
                print(f"\n   *** {msg} ***")
        return None

    def find_path(self, table_name, field, value):
        msg = f"La ruta con el campo {field.upper()} = {bool(value)} no se recupero"
        found_item = self.find_item(table_name, field, value, msg)
        if(found_item is not None and found_item != []):
            _, *found_path = found_item
            return Path(*found_path)
        else:
            return None

    def find_product(self, table_name, field, value):
        msg = f"El producto con el campo {field.upper()} = {value} no se recupero"
        found_item = self.find_item(table_name, field, value, msg)
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
            if(path.is_export):
                self.execute_query(f"UPDATE {table_paths} SET is_export = 0")
            if(path.is_import):
                self.execute_query(f"UPDATE {table_paths} SET is_import = 0")
        c = self.execute_query(f"INSERT INTO {table_paths} (path, is_export, is_import) VALUES (?, ?, ?)", path.get_db_values())
        self.confirm_transaction_database(c)

    def update_path(self, table_paths, path_id, path_obj, is_first_entry, confirm=False):
        params = path_obj.get_db_values() + [path_id]
        query = f"UPDATE {table_paths} SET path = ?, is_export = ?, is_import = ? WHERE id = ?;"

        if not is_first_entry:
            if(path_obj.is_export):
                self.execute_query(f"UPDATE {table_paths} SET is_export = 0")
            if(path_obj.is_import):
                self.execute_query(f"UPDATE {table_paths} SET is_import = 0")

        c = self.execute_query(query, params)
        if confirm:
            self.confirm_transaction_database(c)
        else:
            self.commit(c)

    def update_product(self, table_name, id_prod, product_obj, confirm=False):
        params = product_obj.get_db_values() + [id_prod]
        query = f"UPDATE {table_name} SET name = ?, quantity = ?, unit = ?, price = ?, total = ?, date = ?, category = ? WHERE id = ?;"
        c = self.execute_query(query, params)
        if(confirm):
            self.confirm_transaction_database(c)
        else:
            self.commit(c)

    def update_formats_date(self, table_name, wrong_rows):
        for row in wrong_rows:
            id_ = row['id']
            original_date = row['date']
            normalized_date = utils.convert_ddmmyyyy_to_iso8601(original_date)
            c = self.execute_query(f"UPDATE {table_name} SET date = ? WHERE id = ?", (normalized_date, id_))
            self.commit(c)

    @staticmethod
    def convert_column_sql_quantity_to_float(column):
        converted_column_template = f"""
        CASE
            WHEN {column} LIKE '%/%' THEN
                CAST(SUBSTR({column}, 1, INSTR({column}, '/') - 1) AS REAL) /
                CAST(SUBSTR({column}, INSTR({column}, '/') + 1) AS REAL)
            ELSE
                CAST({column} AS REAL)
        END
        """
        return converted_column_template

    def delete_table(self, table_name):
        c = self.execute_query(f"DELETE FROM {table_name}")
        self.commit(c)
        c = self.execute_query(f"UPDATE sqlite_sequence SET seq = 0 WHERE name = '{table_name}'")
        self.commit(c)

    @staticmethod
    def delete_database(db_full_path):
        try:
            if os.path.exists(db_full_path):
                if os.path.isfile(db_full_path):
                    os.remove(db_full_path)
                    print(f"\n   >>> La base de datos ha sido eliminada!")
                else:
                    print("\n   >>> La ruta proporcionada no es un archivo válido!")
            else:
                print(f"\n   >>> No se encontró el archivo de base de datos en la ruta: {os.path.dirname(db_full_path)}")
        except Exception as e:
            print(f"\n   >>> Hubo un error al eliminar la base de datos: {e}")

    def export_table_to_csv(self, table_name, file_name, file_path):
        try:
            query_select = f"SELECT * FROM {table_name}"
            tbl_headers = self.get_headers(f"{table_name}")
            tbl_headers = tbl_headers[1:]

            rows = self.fetch_all(query_select)
            rows = [row[1:] for row in rows]

            with open(f"{file_path}/{file_name}", mode='w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(tbl_headers)
                csv_writer.writerows(rows)

            print(f"\n   *** Exportación exitosa ***")
        except Exception as e:
            print(f"\n   >>> Error durante la exportación!!\n   >>> {e}\n")
            time.sleep(1.5)

    def import_table_from_csv(self, table_name, file_name, file_path):
        try:
            tbl_headers = self.get_headers(f"{table_name}")
            tbl_headers = tbl_headers[1:]

            with open(f"{file_path}/{file_name}", mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                csv_headers = next(csv_reader)

                csv_headers_clean = [header.strip().lower() for header in csv_headers]
                tbl_headers_clean = [header.strip().lower() for header in tbl_headers]

                found_csv_id = csv_headers_clean.index('id') if 'id' in csv_headers_clean else None
                if found_csv_id is not None:
                    csv_headers_clean = csv_headers_clean[1:]

                if len(csv_headers_clean) != len(tbl_headers_clean):
                    raise ValueError(f"Las cabeceras del archivo CSV y la tabla no coinciden en número.\n"
                                     f"\n  * Num. cabeceras del archivo: {len(csv_headers)}"
                                     f"\n  * Num. cabeceras de la tabla: {len(tbl_headers)}")

                if tbl_headers_clean != csv_headers_clean:
                    raise ValueError(f"Las cabeceras del archivo CSV y la tabla no coinciden"
                                     f"\n\n  * csv_headers: {csv_headers_clean}\n  * tbl_headers: {tbl_headers_clean}")

                for row in csv_reader:
                    row = [cell.strip() for cell in row]

                    while len(row) < len(csv_headers):
                        row.append("")

                    if found_csv_id is not None:
                        del row[found_csv_id]

                    placeholders = ', '.join(['?' for _ in tbl_headers_clean])
                    query_insert = f"INSERT INTO {table_name} ({', '.join(tbl_headers_clean)}) VALUES ({placeholders})"
                    c = self.execute_query(query_insert, row)
                    self.commit(c)

            print("\n   *** Importación exitosa ***")
        except Exception as e:
            print(f"\n   >>> Error durante la importación!!\n   >>> {e}\n")
            time.sleep(1.5)
