import re
from fractions import Fraction
from datetime import datetime

def convert_to_float(input_string):
    try:
        return float(Fraction(input_string))
    except ValueError:
        return float(input_string)

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

def read_integer(message, minimum=None, maximum=None):
    regex_integer = r'^[0-9]\d*$'
    return read_valid_number(regex_integer, int, message, minimum, maximum)

def read_options_menu(minimum, maximum):
    return read_integer(f"\n  [ Opción ]: ", minimum, maximum)

def read_float(message, minimum=None, maximum=None):
    regex_float = r'^(0(\.\d+)?|([1-9]\d*)(\.\d+)?)$'
    return read_valid_number(regex_float, float, message, minimum, maximum)

def read_float_fraction_str(message):
    regex_float = r'^(0(\.\d+)?|([1-9]\d*)(\.\d+)?)$'
    regex_fraction = r'^(?!0\/)(?!.*\/0)[1-9]\d*\/[1-9]\d*$'
    return read_valid_varchar(f'({regex_float})|({regex_fraction})', message)

def read_simple_text(message):
    regex_simple_text = r'^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ]+[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ()\.\-\_\ ]*'
    return read_valid_varchar(regex_simple_text, message)

def read_file_name_csv(message):
    regex_file_csv = r'^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ\(\)\.\-\_\ ]+\.(?i:csv)$'
    return read_valid_varchar(regex_file_csv, message)

def read_paths_linux(message):
    env_var_path = r'^(?:/[\w\.áéíóúÁÉÍÓÚñÑ_-]+|\$\w+)(?:/[\w\.áéíóúÁÉÍÓÚñÑ_-]*|\$\w*)*(?<!/)$'
    absolute_path = r'^(?:/([\$\w+]|[\w\.áéíóúÁÉÍÓÚñÑ_-]+(?:/[\w\.-áéíóúÁÉÍÓÚñÑ_-]+)*))(?<!/)$'
    relative_path = r'^[\w\.áéíóúÁÉÍÓÚñÑ_-]+(?:/[\w\.-áéíóúÁÉÍÓÚñÑ_-]+)*(?<!/)$'
    home_path = r'^~/?([\w\.áéíóúÁÉÍÓÚñÑ_-]+(?:/[\w\.-áéíóúÁÉÍÓÚñÑ_-]+)*)(?<!/)$'
    regex_path = f'({env_var_path}|{absolute_path}|{relative_path}|{home_path})'
    return read_valid_varchar_no_full(regex_path, message)

def read_date(message):
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

def read_short_answer(message):
    regex_options = r'^(SI|NO|Si|No|si|no|S|N|s|n)$'
    return read_valid_varchar(regex_options, f"\n  * {message} (si/no): ")

def read_answer_continue():
    return read_short_answer("¿Desea continuar?")
