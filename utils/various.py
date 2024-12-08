import io
import subprocess
import csv
import re
from fractions import Fraction
from datetime import datetime

def convert_to_float(input_string):
    try:
        return float(Fraction(input_string))
    except ValueError:
        return float(input_string)

def convert_column_sql_quantity_to_float(column):
    converted_column = f"""
    CASE
        WHEN {column} LIKE '%/%' THEN
            CAST(SUBSTR({column}, 1, INSTR({column}, '/') - 1) AS REAL) /
            CAST(SUBSTR({column}, INSTR({column}, '/') + 1) AS REAL)
        ELSE
            CAST({column} AS REAL)
    END
    """
    return converted_column

def read_input_regex(pattern, message):
    try:
        input_varchar = input(message)
        if(re.fullmatch(pattern, input_varchar) is not None):
            return input_varchar
        else:
            raise ValueError(f"\n   *** El valor '{input_varchar}' no es valido! ***")
    except re.error as regex_error:
        raise ValueError(f"\n   Expresión regular inválido:\n   {regex_error}")

def read_input_regex_no_full(pattern, message):
    try:
        input_varchar = input(message)
        if(re.match(pattern, input_varchar) is not None):
            return input_varchar
        else:
            raise ValueError(f"\n   *** El valor '{input_varchar}' no es valido! ***")
    except re.error as regex_error:
        raise ValueError(f"\n   Expresión regular inválido:\n   {regex_error}")

def read_valid_varchar(pattern, message):
    input_varchar = ""
    while len(input_varchar.strip()) == 0:
        try:
            input_varchar = read_input_regex(pattern, message)
        except ValueError as e:
            print(f"{e}")
    return input_varchar

def read_valid_varchar_no_full(pattern, message):
    input_varchar = ""
    while len(input_varchar.strip()) == 0:
        try:
            input_varchar = read_input_regex_no_full(pattern, message)
        except ValueError as e:
            print(f"{e}")
    return input_varchar

def read_valid_number(pattern, convert_func, message, minimum, maximum):
    while True:
        number = convert_func(read_valid_varchar(pattern, message))
        if minimum is not None and number < minimum:
            print(f"\n  *** El número debe ser mayor o igual a {minimum} ***")
        elif maximum is not None and number > maximum:
            print(f"\n  *** El número debe ser menor o igual a {maximum} ***")
        else:
            return number

def read_input_integer(message, minimum=None, maximum=None):
    regex_integer = r'^[0-9]\d*$'
    return read_valid_number(regex_integer, int, message, minimum, maximum)

def read_input_options_menu(minimum, maximum):
    return read_input_integer(f"\n  [ Opción ]: ", minimum, maximum)

def read_input_float(message, minimum=None, maximum=None):
    regex_float = r'^(0(\.\d+)?|([1-9]\d*)(\.\d+)?)$'
    return read_valid_number(regex_float, float, message, minimum, maximum)

def read_input_float_fraction_str(message):
    regex_float = r'^(0(\.\d+)?|([1-9]\d*)(\.\d+)?)$'
    regex_fraction = r'^(?!0\/)(?!.*\/0)[1-9]\d*\/[1-9]\d*$'
    return read_valid_varchar(f'({regex_float})|({regex_fraction})', message)

def read_input_simple_text(message):
    regex_simple_text = r'^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ]+[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ()\.\-\_\ ]*'
    return read_valid_varchar(regex_simple_text, message)

def read_input_file_csv(message):
    regex_file_csv = r'^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ\(\)\.\-\_\ ]+\.(?i:csv)$'
    return read_valid_varchar(regex_file_csv, message)

def read_input_paths_linux(message):
    env_var_path = r'^(?:/[\w\.áéíóúÁÉÍÓÚñÑ_-]+|\$\w+)(?:/[\w\.áéíóúÁÉÍÓÚñÑ_-]*|\$\w*)*(?<!/)$'
    absolute_path = r'^(?:/([\$\w+]|[\w\.áéíóúÁÉÍÓÚñÑ_-]+(?:/[\w\.-áéíóúÁÉÍÓÚñÑ_-]+)*))(?<!/)$'
    relative_path = r'^[\w\.áéíóúÁÉÍÓÚñÑ_-]+(?:/[\w\.-áéíóúÁÉÍÓÚñÑ_-]+)*(?<!/)$'
    home_path = r'^~/?([\w\.áéíóúÁÉÍÓÚñÑ_-]+(?:/[\w\.-áéíóúÁÉÍÓÚñÑ_-]+)*)(?<!/)$'
    regex_path = f'({env_var_path}|{absolute_path}|{relative_path}|{home_path})'
    return read_valid_varchar_no_full(regex_path, message)

def read_input_date(message):
    regex_year = r'\d{4}'
    regex_month = r'(0[1-9]|1[0-2])'
    regex_day = r'(0[1-9]|[12][0-9]|3[01])'
    regex_date = f"{regex_year}-{regex_month}-{regex_day}"
    while True:
        try:
            date_ = read_valid_varchar(regex_date, message)
            datetime.strptime(date_, "%Y-%m-%d")
            return date_
        except ValueError:
            print("\n  *** La fecha proporcionada no es válida en el calendario. ***\n")

def read_input_yes_no(message):
    regex_options = r'^(SI|NO|Si|No|si|no|S|N|s|n)$'
    return read_valid_varchar(regex_options, f"\n  * {message} (si/no): ")

def read_input_continue_confirmation():
    return read_input_yes_no("¿Desea continuar?")

def convert_ddmmyyyy_to_iso8601(date_):
    date_ = date_.strip()
    if len(date_) == 10 and date_[4] == '-' and date_[7] == '-':
        return date_
    if '/' in date_:
        segments = date_.split('/')
        return f"{segments[2]}-{segments[1]}-{segments[0]}"
    elif '-' in date_:
        segments = date_.split('-')
        return f"{segments[2]}-{segments[1]}-{segments[0]}"
    return date_

def draw_tittle_border(tittle):
    border = '=' * (len(tittle) + 7)
    print(f"\n  {border}\n  |  {tittle.upper()}  |\n  {border}\n")

def draw_subtitle_border(subtittle):
    border = '-' * (len(subtittle) + 6)
    print(f"\n  {border}\n  |  {subtittle.title()}  |\n  {border}\n")

def convert_table_to_in_memory_csv(headers, rows):
    output = io.StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(headers)
    csv_writer.writerows(rows)
    return output.getvalue()

def format_csv_using_column_command(csv_data):
    try:
        process = subprocess.Popen(
            ['column', '-t', '-s,'],  # Comando 'column' para formatear con tabuladores
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=csv_data)
        if stderr:
            raise Exception(f"Error al ejecutar 'column': {stderr}")
        return stdout
    except Exception as e:
        print(f"Error al formatear con 'column': {e}")
        return ""

def add_borders_and_margins_to_table(formatted_data, margin=4):
    if not formatted_data:
        return ""

    lines = formatted_data.splitlines()
    if len(lines) > 0:
        max_length = max(len(line) for line in lines)
        lines.insert(0, '-' * max_length)
        lines.insert(2, '-' * max_length)
        lines.append('-' * max_length)

    return "\n".join([f"{' ' * margin}{line}" for line in lines])

def display_formatted_table(conn, table_name, query=None):
    subprocess.run(["clear"])
    print("\n")
    if(query is None):
        query = f"SELECT * FROM {table_name}"
    tbl_rows = conn.fetch_all(query)
    tbl_headers = conn.get_headers(table_name, query)
    tbl_headers = [header.upper() for header in tbl_headers]
    csv_data = convert_table_to_in_memory_csv(tbl_headers, tbl_rows)
    formatted_data = format_csv_using_column_command(csv_data)
    fully_formatted_table = add_borders_and_margins_to_table(formatted_data)
    print(fully_formatted_table)

def check_formats_date(conn, table_name):
    regex_iso8601 = r'^\d{4}-\d{2}-\d{2}$'
    rows = conn.fetch_all(f"SELECT id, date FROM {table_name}")
    wrong_rows = []
    for row in rows:
        id_ = row['id']
        date_ = row['date']
        if not re.match(regex_iso8601, date_):
            wrong_rows.append({'id': id_, 'date': date_})
    return wrong_rows

def update_formats_date(conn, table_name, wrong_rows):
    for row in wrong_rows:
        id_ = row['id']
        original_date = row['date']
        normalized_date = convert_ddmmyyyy_to_iso8601(original_date)
        c = conn.execute_query(f"UPDATE {table_name} SET date = ? WHERE id = ?", (normalized_date, id_))
        conn.commit(c)
    return conn