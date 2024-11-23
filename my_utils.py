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

def read_input_regex(patron, mensaje):
    input_varchar = input(mensaje)
    if(re.fullmatch(patron, input_varchar) is not None):
        return input_varchar
    else:
        raise ValueError(f"El valor '{input_varchar}' no es valido!")

def read_input_regex_no_full(patron, mensaje):
    input_varchar = input(mensaje)
    if(re.match(patron, input_varchar) is not None):
        return input_varchar
    else:
        raise ValueError(f"El valor '{input_varchar}' no es valido!")

def read_valid_varchar(patron, mensaje):
    input_varchar = ""
    while len(input_varchar.strip()) == 0:
        try: 
            input_varchar = read_input_regex(patron, mensaje)
        except ValueError as e:
            input_varchar = ""
            print(f"\n *** {e} ***\n")
    return input_varchar

def read_valid_varchar_no_full(patron, mensaje):
    input_varchar = ""
    while len(input_varchar.strip()) == 0:
        try:
            input_varchar = read_input_regex_no_full(patron, mensaje)
        except ValueError as e:
            input_varchar = ""
            print(f"\n *** {e} ***\n")
    return input_varchar

def read_valid_number(mostrar_mensaje, minimo, maximo, patron, convert_func):
    numero = minimo - 1
    while not (minimo <= numero <= maximo):
        try:
            numero = convert_func(read_valid_varchar(patron, mostrar_mensaje))
        except ValueError:
            numero = minimo - 1
        if not (minimo <= numero <= maximo):
            print(f"\n  >>> El número debe estar en el rango [{minimo}-{maximo}] <<<\n")
    return numero

def read_input_integer(mostrar_mensaje, minimo, maximo):
    regex_integer = r'^[0-9]\d*$'
    return read_valid_number(mostrar_mensaje, minimo, maximo, regex_integer, int)

def read_input_float(mostrar_mensaje, minimo, maximo):
    regex_float = r'^(?!.*\/0)(-?\d+(\.\d+)?|-\d+/\d+|\d+/\d+)$'
    return read_valid_number(mostrar_mensaje, minimo, maximo, regex_float, convert_to_float)

def read_input_simple_text(mensaje):
    regex_simple_text = r'^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ]+[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ()\.\-\_\ ]*'
    return read_valid_varchar(regex_simple_text, mensaje)

def read_input_paths_linux(mensaje):
    env_var_path = r'^(?:/[\w\.áéíóúÁÉÍÓÚñÑ_-]+|\$\w+)(?:/[\w\.áéíóúÁÉÍÓÚñÑ_-]*|\$\w*)*(?<!/)$'
    absolute_path = r'^(?:/([\$\w+]|[\w\.áéíóúÁÉÍÓÚñÑ_-]+(?:/[\w\.-áéíóúÁÉÍÓÚñÑ_-]+)*))(?<!/)$'
    relative_path = r'^[\w\.áéíóúÁÉÍÓÚñÑ_-]+(?:/[\w\.-áéíóúÁÉÍÓÚñÑ_-]+)*(?<!/)$'
    home_path = r'^~/?([\w\.áéíóúÁÉÍÓÚñÑ_-]+(?:/[\w\.-áéíóúÁÉÍÓÚñÑ_-]+)*)(?<!/)$'
    regex_path = f'({env_var_path}|{absolute_path}|{relative_path}|{home_path})'
    return read_valid_varchar_no_full(regex_path, mensaje)

def read_input_date(mensaje):
    regex_date = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$'
    return read_valid_varchar(regex_date, mensaje)

def read_input_yes_no(mensaje):
    regex_options = r'^(SI|NO|Si|No|si|no|S|N|s|n)$'
    return read_valid_varchar(regex_options, mensaje)

def read_input_continue_confirmation():
    return read_input_yes_no("\n  >>> ¿Desea continuar (Si/No)? ")

def draw_tittle_border(titulo):
    border = '=' * (len(titulo) + 7)
    print(f"\n  {border}\n  |  {titulo.upper()}  |\n  {border}\n")

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

