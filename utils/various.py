import io
import subprocess
import csv
import re

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

def check_formats_date(rows):
    regex_iso8601 = r'^\d{4}-\d{2}-\d{2}$'
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
