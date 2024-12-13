import os
import io
import subprocess
import csv
import re
import utils.input_validations as valid

def draw_title_border(title):
    border = '=' * (len(title) + 7)
    print(f"\n  {border}\n  |  {title.upper()}  |\n  {border}\n")

def get_terminal_size():
    size = os.get_terminal_size()
    return size.columns, size.lines

def truncate_value(value, max_length):
    if len(str(value)) > max_length:
        return str(value)[:max_length]
    return str(value)

def convert_table_to_in_memory_csv(headers, rows):
    width_terminal, _ = get_terminal_size()
    max_length = round(width_terminal/(len(headers)-3))
    formatted_rows = []
    for row in rows:
        formatted_row = [truncate_value(value, max_length) for value in row]
        formatted_rows.append(formatted_row)

    output = io.StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(headers)
    csv_writer.writerows(formatted_rows)
    return output.getvalue()

def format_csv_using_column_command(csv_data):
    try:
        process = subprocess.Popen(
            ['column', '-t', '-s,'],
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

def check_formats_date(rows):
    regex_iso8601 = r'^\d{4}-\d{2}-\d{2}$'
    wrong_rows = []
    for row in rows:
        id_ = row['id']
        date_ = row['date']
        if not re.match(regex_iso8601, date_):
            wrong_rows.append({'id': id_, 'date': date_})
    return wrong_rows

def choose_option_in_menu(title, menu_options, clear="clear"):
    if clear.strip() != "no_clear":
        subprocess.run(["clear"])
    draw_title_border(title)
    print("  0. Regresar")
    for idx, description in menu_options:
        print(f"  {idx}. {description}")
    max_option = len(menu_options)
    return valid.read_options_menu(0, max_option)

def choose_option_in_menu_import_export(title, menu_options, clear="clear"):
    if clear.strip() != "no_clear":
        subprocess.run(["clear"])
    draw_title_border(title)
    print("  0. Regresar")
    for idx, (description, _, _, _) in enumerate(menu_options, 1):
        print(f"  {idx}. {description}")
    max_option = len(menu_options)
    return valid.read_options_menu(0, max_option)
