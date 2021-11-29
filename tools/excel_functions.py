########################################################################################################################
#       Author: Reedan Ajamia.                                                                                         #
#       Date: October, 2021.                                                                                           #
#       Company: Personetics.                                                                                          #
########################################################################################################################

import enum         # Enum
import os.path      # basename
import errno        # errno
import shutil       # rmtree
import pandas       # ExcelWriter, read_csv, DataFrame, ExcelFile
import xlsxwriter   # Workbook

# enumerations
class Status(enum.Enum):
    OK = 0
    ERR_FILE_NOT_EXISTS = 1
    ERR_DIR_EXISTS = 2
    ERR_DIR_NOT_EXISTS = 3
    ERR_INVALID_PARAMETERS = 4
    ERR_OS = 5

SHEET_NAME_MAX_LENGTH = 31
SPACE_BETWEEN_TABLES = 2

# -------------------------- Overview --------------------------
# This function returns a proper message on a given status.

# ** input **
# status_result: status result.
# ** output **
# string representing the occurred error.
def get_status_message(status_result):
    if Status.OK == status_result:
        return "Program execution Success!"
    elif Status.ERR_FILE_NOT_EXISTS == status_result:
        return "Input File does not exist"
    elif Status.ERR_DIR_EXISTS == status_result:
        return "Directory already exists"
    elif Status.ERR_DIR_NOT_EXISTS == status_result:
        return "Directory does not exist"
    elif Status.ERR_INVALID_PARAMETERS == status_result:
        return "Input arguments are invalid"
    elif Status.ERR_OS == status_result:
        return "System Error"

# -------------------------- Overview --------------------------
# This function prints a proper message on a given status.

# ** input **
# status_result: status result.
# ** output **
# no output.
def print_status_message(status_result):
    if Status.OK == status_result:
        print("Program execution Success!")
    elif Status.ERR_FILE_NOT_EXISTS == status_result:
        print("Input File does not exist")
    elif Status.ERR_DIR_EXISTS == status_result:
        print("Directory already exists")
    elif Status.ERR_DIR_NOT_EXISTS == status_result:
        print("Directory does not exist")
    elif Status.ERR_INVALID_PARAMETERS == status_result:
        print("Input arguments are invalid")
    elif Status.ERR_OS == status_result:
        print("System Error")

# -------------------------- Overview --------------------------
# This function creates a directory if it does not exist.

# ** input **
# dir_path: path of directory (including name) to be created.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_DIR_EXISTS - directory already exists.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def create_directory(dir_path):
    # arguments validity check
    if type(dir_path) != str or "" == dir_path:
        return Status.ERR_INVALID_PARAMETERS

    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
            return Status.OK
        except OSError:
            os.strerror(errno.errorcode)
            return Status.ERR_OS
    else:
        return Status.ERR_DIR_EXISTS

# -------------------------- Overview --------------------------
# This function deletes all content of a directory.

# ** input **
# dir_path: path of directory (including name) to be cleaned.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_DIR_NOT_EXISTS - directory does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def delete_all_content_in_directory(dir_path):
    # arguments validity check
    if type(dir_path) != str or "" == dir_path:
        return Status.ERR_INVALID_PARAMETERS

    if os.path.exists(dir_path):
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
        return Status.ERR_DIR_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function validates if a given folder exists.

# ** input **
# dir_path: path of the directory.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_DIR_NOT_EXISTS - directory does not exist.
def validate_directory_path(dir_path):
    # arguments validity check
    if type(dir_path) != str or "" == dir_path:
        return Status.ERR_INVALID_PARAMETERS

    if not os.path.isdir(dir_path):
        return Status.ERR_DIR_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function corrects a given path of directory to be valid
# with slashes.

# ** input **
# dir_path: path of the directory.
# new_dir_path: empty list to save in it the new path of directory.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_DIR_NOT_EXISTS - directory does not exist.
def correct_directory_path(dir_path, new_dir_path):
    # arguments validity check
    status_result = validate_directory_path(dir_path)
    if Status.OK != status_result:
        print("validate_directory_path failure")
        return status_result
    if type(new_dir_path) != list or 0 != len(new_dir_path):
        return Status.ERR_INVALID_PARAMETERS

    if not dir_path.endswith("/"):
        new_dir_path.append(dir_path + "/")
    else:
        new_dir_path.append(dir_path)

    return Status.OK

# -------------------------- Overview --------------------------
# This function prints all subdirectories and files in a given root
# directory.

# ** input **
# root_dir_path: path of the "root" folder.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_DIR_NOT_EXISTS - directory does not exist.
def print_subdirectories_and_files(root_dir_path):
    # arguments validity check
    status_result = validate_directory_path(root_dir_path)
    if Status.OK != status_result:
        print("validate_directory_path failure")
        return status_result

    directory = root_dir_path
    for root, subdirectories, files in os.walk(directory):
        for subdirectory in subdirectories:
            print(os.path.join(root, subdirectory))
        for file in files:
            print(os.path.join(root, file))

    return Status.OK

# -------------------------- Overview --------------------------
# This function extracts current working directory name and saves
# name in a list.

# ** input **
# path: path of directory or a file.
# dir_name: empty list to save in it name of directory.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def extract_directory_name_from_path(path, dir_name):
    # arguments validity check
    if type(path) != str or "" == path:
        return Status.ERR_INVALID_PARAMETERS
    if type(dir_name) != list or 0 != len(dir_name):
        return Status.ERR_INVALID_PARAMETERS

    if os.path.isdir(path):
        if path.endswith('/'):
            path = path[0:len(path) - 1:1]
            cwd_name = os.path.basename(path)
        else:
            cwd_name = os.path.basename(path)
    elif os.path.isfile(path):
        cwd_name = os.path.basename(os.path.dirname(path))
    else:
        return Status.ERR_INVALID_PARAMETERS

    dir_name.append(cwd_name)
    return Status.OK

# -------------------------- Overview --------------------------
# This function extracts current working directory name and its subdirectories
# names and saves names in a list.

# ** input **
# root_dir_path: path of the "root" folder.
# dirs_list: empty list to save in it names of directories.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_DIR_NOT_EXISTS - directory does not exist.
def extract_directory_and_subdirectories_names(root_dir_path, dirs_list):
    # arguments validity check
    status_result = validate_directory_path(root_dir_path)
    if Status.OK != status_result:
        print("validate_directory_path failure")
        return status_result
    if type(dirs_list) != list or 0 != len(dirs_list):
        return Status.ERR_INVALID_PARAMETERS

    # extract name of root folder (cwd)
    if root_dir_path.endswith('/'):
        root_dir_path = root_dir_path[0:len(root_dir_path) - 1:1]
        cwd_name = os.path.basename(root_dir_path)
    else:
        cwd_name = os.path.basename(root_dir_path)
    dirs_list.append(cwd_name)

    # list names of directory's content (subdirectories and files)
    ls_directory = os.listdir(root_dir_path)
    for item in ls_directory:
        item_path = os.path.join(root_dir_path, item)
        if os.path.isdir(item_path):
            dirs_list.append(item)

    return Status.OK

# -------------------------- Overview --------------------------
# This function extracts from a given path the file name without
# its extension.

# ** input **
# file_path: path of the input file.
# ** output **
# returns one of the following strings:
# empty string: if the the given path argument is invalid.
# file_name: name of file without extension.
def get_file_name_without_extension(file_path):
    # arguments validity check
    if type(file_path) != str or "" == file_path:
        return ""

    try:
        full_name = os.path.basename(file_path)
        separated_info = os.path.splitext(full_name)
        file_name = separated_info[0]
    except FileNotFoundError:
        return ""

    return file_name

# -------------------------- Overview --------------------------
# This function extracts the title of sheet in excel from a given file
# name according to the test files pattern ONLY!!!
# the extracted name is saved in a list variable.

# ** input **
# file_name: full name of csv file without its extension.
# title_name: empty list to save in it name of the sheet.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def get_title_for_sheet(file_name, title_name):
    # arguments validity check
    if type(file_name) != str or "" == file_name:
        return Status.ERR_INVALID_PARAMETERS
    if type(title_name) != list or 0 != len(title_name):
        return Status.ERR_INVALID_PARAMETERS

    title_counter = 0
    str_iterator = 0
    reversed_file_name = file_name[::-1]
    while title_counter < SHEET_NAME_MAX_LENGTH:
        ch = reversed_file_name[str_iterator]
        if '_' == ch:
            if reversed_file_name[str_iterator + 1].isdigit():
                break

        str_iterator += 1
        title_counter += 1

    last_underscore = 0
    if SHEET_NAME_MAX_LENGTH == title_counter:
        for i in range(SHEET_NAME_MAX_LENGTH):
            if '_' == reversed_file_name[i]:
                last_underscore = i

        reversed_sheet_title = reversed_file_name[0:last_underscore:1]
    else:
        reversed_sheet_title = reversed_file_name[0:title_counter:1]

    sheet_title = reversed_sheet_title[::-1]
    title_name.append(sheet_title)

    return Status.OK

# -------------------------- Overview --------------------------
# This function combines all csv files in a files paths list and
# saves them in separated sheets in one excel file.

# ** input **
# test_folder_name: name of test folder of the csv files.
# files_list: list of paths of all csv files to be combined together.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def combine_csv_files_to_excel_per_directory(test_folder_name, files_list):
    # arguments validity check
    if type(test_folder_name) != str or "" == test_folder_name:
        return Status.ERR_INVALID_PARAMETERS
    if type(files_list) != list or 0 == len(files_list):
        return Status.ERR_INVALID_PARAMETERS

    output_dir = "./output_files/"
    writer = pandas.ExcelWriter(output_dir + test_folder_name + ".xlsx")
    df_files_list = []
    for csv_file in files_list:
        # extract title from file name
        file_name = os.path.splitext(csv_file)[0]
        title_name = []
        status_result = get_title_for_sheet(file_name, title_name)
        if Status.OK != status_result:
            print("get_title_for_sheet failure")
            return status_result
        sheet_title = title_name[0]

        # read csv file into Dataframe
        file_df = pandas.read_csv(csv_file)
        df_files_list.append(file_df)

        file_df.to_excel(writer, sheet_name=sheet_title, index=False)
    writer.save()

    return Status.OK

# -------------------------- Overview --------------------------
# This function extracts the header of a table from a dataframe variable
# and returns it as a string.

# ** input **
# df: dataframe of the a given table.
# ** output **
# returns the header as a string.
def get_header_from_dataframe_as_string(df):
    header = df.columns
    header_str = (','.join(map(str, header))) + "\n"
    return header_str

# -------------------------- Overview --------------------------
# This function combines all sheets in an excel file into a single
# sheet, when tables are separated.

# ** input **
# excel_path: path of the input "excel" file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_FILE_NOT_EXISTS - file does not exist.
def combine_sheets_into_single_sheet_seperated_tables(excel_path):
    # arguments validity check
    if type(excel_path) != str or "" == excel_path:
        return Status.ERR_INVALID_PARAMETERS

    output_dir = "./output_files/"
    try:
        file_name = get_file_name_without_extension(excel_path)
        if "" == file_name:
            print("get_file_name_without_extension failure")
            return Status.ERR_INVALID_PARAMETERS

        final_out_path = output_dir + file_name + ".txt"
        with open(final_out_path, "a", encoding='utf-8', newline='') as combined_file:
            excel_file = pandas.ExcelFile(excel_path, engine="openpyxl")
            sheets = excel_file.sheet_names

            # write some info in the head of file
            combined_file.write("Test folder info:\n")
            combined_file.write(file_name + "\n")
            for i in range(SPACE_BETWEEN_TABLES):
                combined_file.write("\n")

            # loop through sheets inside an Excel file
            sheets_iter = 0
            for sheet in sheets:
                # combine sheets
                sheet_df = excel_file.parse(sheet_name=sheet)
                header_str = get_header_from_dataframe_as_string(sheet_df)
                title = sheets[sheets_iter]
                combined_file.write(title + "\n")
                combined_file.write(header_str)
                for index, row in sheet_df.iterrows():
                    row_str = (','.join(map(str, row))) + "\n"
                    combined_file.write(row_str)

                sheets_iter += 1
                combined_file.write("\n\n")
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function converts a text file to an excel file.

# ** input **
# text_file_path: path of the input text file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_FILE_NOT_EXISTS - file does not exist.
def convert_text_file_to_excel(text_file_path):
    # arguments validity check
    if type(text_file_path) != str or "" == text_file_path:
        return Status.ERR_INVALID_PARAMETERS

    output_dir = "./output_files/"
    file_name = get_file_name_without_extension(text_file_path)
    if "" == file_name:
        print("get_file_name_without_extension failure")
        return Status.ERR_INVALID_PARAMETERS

    try:
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook(output_dir + file_name + ".xlsx")
        worksheet = workbook.add_worksheet(file_name)

        # Copy text file's content into workbook.
        with open(text_file_path, "r", encoding='utf-8') as text_file:
            text_content = text_file.readlines()
            row_iter = 0
            for row in text_content:
                row_items = row.split(",")
                col_iter = 0
                for item in row_items:
                    worksheet.write(row_iter, col_iter, item)
                    col_iter += 1

                row_iter += 1

        workbook.close()
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK
