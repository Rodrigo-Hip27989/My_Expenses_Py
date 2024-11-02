import sqlite3
import os
import csv
from datetime import datetime

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

    def commit(self, c):
        if self.conn:
            self.conn.commit()
            print(f"\n  >>> Filas modificadas: {c.rowcount} <<<")
            c.close()

    def rollback(self):
        if self.conn:
            self.conn.rollback()
            print("\n *** Operación cancelada ***")

    def create_table(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE if not exists productos (id INTEGER PRIMARY KEY, nombre TEXT, cantidad REAL, medida TEXT, precio REAL, total REAL, fecha TEXT)")
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

    def export_to_csv(self, table_name):
        try:
            timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
            file_name = f"{table_name.capitalize()}_{timestamp}.csv"
            query_select = f"SELECT * FROM {table_name}"
            headers = self.get_headers(f"{table_name}")
            rows = self.fetch_all(query_select)
            with open(file_name, mode='w', newline='', encoding='utf-8') as archivo_csv:
                escritor_csv = csv.writer(archivo_csv)
                escritor_csv.writerow(headers)
                escritor_csv.writerows(rows)
            print(f"\n   >>> Exportación '{file_name}' exitosa!! <<<")
        except Exception as e:
            print(f"\n   >>> Error durante la exportación!! <<<\n   *** {e} ***")
        input("\n   >>> Presione ENTER para continuar <<<")
