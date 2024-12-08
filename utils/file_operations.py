import os
import glob
import subprocess
import utils.various as utils
import utils.input_validations as valid
from datetime import datetime

def find_files_by_extension(path, extension):
    expanded_path = os.path.expandvars(path)
    expanded_path = os.path.expanduser(expanded_path)
    final_expanded_path = os.path.abspath(expanded_path)
    if not os.path.exists(final_expanded_path):
        print(f"Error: La ruta '{path}' no existe.")
        return []
    if not os.path.isdir(final_expanded_path):
        print(f"Error: '{path}' no es un directorio válido.")
        return []
    pattern = os.path.join(final_expanded_path, f"*.{extension}")
    file_list = glob.glob(pattern)
    file_list_sorted = sorted(file_list, key=lambda x: os.path.basename(x).lower())
    return file_list_sorted

def select_file_from_list(file_list):
    subprocess.run(["clear"])
    utils.draw_tittle_border("Seleccione un archivo para importar")
    for i, file in enumerate(file_list, start=1):
        name_file = os.path.basename(file)
        print(f"   {i}. {name_file}")
    option = valid.read_options_menu(1, (len(file_list)))
    return option

def get_expanded_path(path):
    try:
        expanded_path = os.path.expandvars(path)
        expanded_path = os.path.expanduser(expanded_path)
        final_expanded_path = os.path.abspath(expanded_path)
        return final_expanded_path
    except KeyError as e:
        print(f"\n   >>> Error: Variable de entorno no encontrada en la ruta. \n   >>>Detalles: {e}")
    except Exception as e:
        print(f"\n   >>> Ha ocurrido un error inesperado: {e}")
    return None

def create_directory_and_get_expanded_path(path):
    try:
        expanded_path = get_expanded_path(path)
        os.makedirs(expanded_path, exist_ok=True)
        return expanded_path
    except PermissionError as e:
        print(f"\n   >>> Error: No tienes permisos suficientes para crear el directorio. \n   >>> Detalles: {e}")
    except OSError as e:
        print(f"\n   >>> Error: Ha ocurrido un error con el sistema operativo. \n   >>>Detalles: {e}")
    except Exception as e:
        print(f"\n   >>> Ha ocurrido un error inesperado: {e}")
    return None

def export_table_to_csv_default(conn, table_name, export_path):
    subprocess.run(["clear"])
    utils.draw_tittle_border(f"Exportando tabla {table_name}")
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    file_name = f"{table_name.capitalize()}_{timestamp}.csv"
    print(f"\n   [ Ruta del archivo ] \n   > {export_path.path}")
    print(f"\n   [ Nombre del Archivo ] \n   > {file_name}")
    change_name = valid.read_short_answer("¿Desea cambiar el nombre del archivo?")
    if(change_name.lower() in ['si', 's']):
        file_name = valid.read_file_name_csv(f"\n   [ Nuevo Nombre ] \n   > ")
    expanded_path = create_directory_and_get_expanded_path(export_path.path)
    conn.export_table_to_csv(table_name, file_name, expanded_path)

def import_table_from_csv_default(conn, table_name, import_path):
    file_path = get_expanded_path(import_path.path)
    file_list = find_files_by_extension(file_path, "csv")

    if len(file_list) < 1:
        print(f"\n   >>> No se encontraron archivos: *.csv")
        return

    option = select_file_from_list(file_list)
    selected_file = os.path.basename(file_list[option-1])
    print(f"\n   [ Ruta de Importación ] \n   > {file_path}")
    print(f"\n   [ Archivo seleccionado ] \n   > {selected_file}")

    if not conn.is_table_empty(table_name):
        print("   *** SU TABLA NO ESTA VACIA ***")
        confirm_clear_table = valid.read_short_answer("¿Desea reemplazar los datos existentes?")
        if(confirm_clear_table.lower() in ['si', 's']):
            c = conn.execute_query(f"DELETE FROM {table_name}")
            conn.commit(c)
            conn.import_table_from_csv(table_name, selected_file, file_path)
        else:
            print("\n   >>> Operacion cancelada")
    else:
        conn.import_table_from_csv(table_name, selected_file, file_path)
