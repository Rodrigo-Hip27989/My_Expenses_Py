import io
import subprocess
import csv
import re
from fractions import Fraction

def convert_to_float(input_string):
    try:
        return float(Fraction(input_string))
    except ValueError:
        return float(input_string)

def read_input_regex(pattern, message):
    input_varchar = input(message)
    if(re.fullmatch(pattern, input_varchar) is not None):
        return input_varchar
    else:
        raise ValueError(f"El valor '{input_varchar}' no es valido!")

def read_input_regex_no_full(pattern, message):
    input_varchar = input(message)
    if(re.match(pattern, input_varchar) is not None):
        return input_varchar
    else:
        raise ValueError(f"El valor '{input_varchar}' no es valido!")

def read_valid_varchar(pattern, message):
    input_varchar = ""
    while len(input_varchar.strip()) == 0:
        try:
            input_varchar = read_input_regex(pattern, message)
        except ValueError as e:
            input_varchar = ""
            print(f"\n *** {e} ***\n")
    return input_varchar

def read_valid_varchar_no_full(pattern, message):
    input_varchar = ""
    while len(input_varchar.strip()) == 0:
        try:
            input_varchar = read_input_regex_no_full(pattern, message)
        except ValueError as e:
            input_varchar = ""
            print(f"\n *** {e} ***\n")
    return input_varchar

def read_valid_number(message, minimum, maximum, pattern, convert_func):
    number = minimum - 1
    while not (minimum <= number <= maximum):
        try:
            number = convert_func(read_valid_varchar(pattern, message))
        except ValueError:
            number = minimum - 1
        if not (minimum <= number <= maximum):
            print(f"\n  >>> El número debe estar en el rango [{minimum}-{maximum}] <<<\n")
    return number

def read_input_integer(message, minimum, maximum):
    regex_integer = r'^[0-9]\d*$'
    return read_valid_number(message, minimum, maximum, regex_integer, int)

def read_input_float(message, minimum, maximum):
    regex_float = r'^(0(\.\d+)?|([1-9]\d*)(\.\d+)?)$'
    return read_valid_number(message, minimum, maximum, regex_float, float)

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
    regex_date = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$'
    return read_valid_varchar(regex_date, message)

def read_input_yes_no(message):
    regex_options = r'^(SI|NO|Si|No|si|no|S|N|s|n)$'
    return read_valid_varchar(regex_options, message)

def read_input_continue_confirmation():
    return read_input_yes_no("\n  >>> ¿Desea continuar (Si/No)? ")

def draw_tittle_border(tittle):
    border = '=' * (len(tittle) + 7)
    print(f"\n  {border}\n  |  {tittle.upper()}  |\n  {border}\n")

def convert_table_to_in_memory_csv(headers, rows):
    """Genera el contenido CSV en memoria."""
    output = io.StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(headers)
    csv_writer.writerows(rows)
    return output.getvalue()

def format_csv_using_column_command(csv_data):
    """Formatea los datos CSV usando el comando 'column'."""
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
    """Agrega márgenes y bordes a la tabla formateada."""
    if not formatted_data:
        return ""

    lines = formatted_data.splitlines()

    if len(lines) > 0:
        max_length = max(len(line) for line in lines)
        lines.insert(0, '-' * max_length)
        lines.insert(2, '-' * max_length)
        lines.append('-' * max_length)

    # Añadir márgenes
    return "\n".join([f"{' ' * margin}{line}" for line in lines])

