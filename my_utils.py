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

def read_valid_varchar(patron, mensaje):
    input_varchar = ""
    while len(input_varchar.strip()) == 0:
        try: 
            input_varchar = read_input_regex(patron, mensaje)
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
    regex_integer = r'^[1-9]\d*$'
    return read_valid_number(mostrar_mensaje, minimo, maximo, regex_integer, int)

def read_input_float(mostrar_mensaje, minimo, maximo):
    regex_float = r'^(?!.*\/0)(-?\d+(\.\d+)?|-\d+/\d+|\d+/\d+)$'
    return read_valid_number(mostrar_mensaje, minimo, maximo, regex_float, convert_to_float)

def read_input_simple_text(mensaje):
    regex_simple_text = r'^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ]+[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ()\.\-\_\ ]*'
    return read_valid_varchar(regex_simple_text, mensaje)

def read_input_date(mensaje):
    regex_date = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$'
    return read_valid_varchar(regex_date, mensaje)

def read_input_yes_no(mensaje):
    regex_options = r'^(SI|NO|Si|No|si|no|S|N|s|n)$'
    return read_valid_varchar(regex_options, mensaje)

def read_input_continue_confirmation():
    return read_input_yes_no("\n  >>> ¿Desea continuar (Si/No)? ")

