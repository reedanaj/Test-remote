########################################################################################################################
#       Author: Reedan Ajamia.                                                                                         #
#       Date: July, 2021.                                                                                              #
#       Company: Personetics.                                                                                          #
########################################################################################################################

import sys          # maxsize
import os           # makedirs, splitext, remove, path
import errno        # errno
import shutil       # rmtree
import operator     # sorted
import csv          # reader, writer
import pandas       # read_excel, read_csv
import re           # sub
import enum         # Enum

# enumerations
class Status(enum.Enum):
    OK = 0
    ERR_FILE_NOT_EXISTS = 1
    ERR_DIR_EXISTS = 2
    ERR_DIR_NOT_EXISTS = 3
    ERR_INVALID_PARAMETERS = 4
    ERR_OS = 5
    ERR_INVALID_FILE = 6

# -------------------------- Overview --------------------------
# This function maximizes the limit of csv field to support very
# long lines in csv files.

# ** input **
# no input.
# ** output **
# no output.
def maximize_csv_field_limit():
    max_size = sys.maxsize
    while True:
        try:
            csv.field_size_limit(max_size)
            break
        except OverflowError:
            max_size = int(max_size / 10)

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
    elif Status.ERR_INVALID_FILE == status_result:
        print("Input file format is invalid")

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
# This function runs over a file and counts how many lines there are in it.

# ** input **
# file_path: path of the input file.
# lines_count: empty list to save in it the lines count.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def get_file_lines_count(file_path, lines_count):
    # arguments validity check
    if type(file_path) != str or "" == file_path or type(lines_count) != list:
        return Status.ERR_INVALID_PARAMETERS

    try:
        with open(file_path, "r", encoding='utf-8') as in_file:
            file_reader = csv.reader(in_file)

            # skip header
            file_header = next(file_reader)
            lines_counter = 0
            for file_row in file_reader:
                lines_counter += 1

            lines_count.append(lines_counter)
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function provides the dir path without the base name of the file
# in a certain file path.

# ** input **
# file_path: path of the input file.
# dir_path: empty list to save in it the dir path.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def get_path_without_basename(file_path, dir_path):
    # arguments validity check
    if type(file_path) != str or "" == file_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(dir_path) != list or 0 != len(dir_path):
        return Status.ERR_INVALID_PARAMETERS

    try:
        dir_path.append(os.path.dirname(file_path))
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function extracts file info out of path:
# 1. file directory.
# 2. file name.
# 3. file extension.

# ** input **
# file_path: path of the input file.
# file_info: empty list to save file info into.
#            file_info[0] --> file directory.
#            file_info[1] --> file name.
#            file_info[2] --> file extension.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def extract_file_path_info(file_path, file_info):
    # arguments validity check
    if type(file_path) != str or "" == file_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(file_info) != list or 0 != len(file_info):
        return Status.ERR_INVALID_PARAMETERS

    try:
        # extract file info
        dir_path = os.path.dirname(file_path)
        full_name = os.path.basename(file_path)
        separated_info = os.path.splitext(full_name)

        # save file info
        file_info.append(dir_path + "/")
        file_info.append(separated_info[0])
        file_info.append(separated_info[1])
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function adds the header of csv file to an empty list.

# ** input **
# csv_path: path of the csv file.
# header_list: empty list to save in it the header.
# deli: delimiter used in csv file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def get_csv_header_as_list(csv_path, header_list, deli):
    # arguments validity check
    if type(csv_path) != str or "" == csv_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(header_list) != list or len(header_list) != 0:
        return Status.ERR_INVALID_PARAMETERS
    if type(deli) != str or "" == deli:
        return Status.ERR_INVALID_PARAMETERS

    # open file
    try:
        with open(csv_path, "r", encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=deli)
            csv_header = next(csv_reader)
            csv_header_length = len(csv_header)
            for i in range(csv_header_length):
                header_list.append(csv_header[i])

    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function checks a file existence by given path

# ** input **
# file_path: path of the input file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def check_file_existence(file_path):
    # arguments validity check
    if type(file_path) != str or "" == file_path:
        return Status.ERR_INVALID_PARAMETERS

    if os.path.exists(file_path):
        return Status.OK
    else:
        return Status.ERR_FILE_NOT_EXISTS

# -------------------------- Overview --------------------------
# This function removes the CR chars from a given file. (overwrites existing file)

# ** input **
# file_path: path of the input file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def clean_carriage_return(file_path):
    # arguments validity check
    if type(file_path) != str or "" == file_path:
        return Status.ERR_INVALID_PARAMETERS

    try:
        with open(file_path, 'r', encoding='utf-8') as in_file:
            content = in_file.read()
        with open(file_path, "w", encoding='utf-8', newline='') as out_file:
            out_file.write(content)
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function substitutes double consequent LF chars for single LF char
# in a given file. (overwrites existing file)

# ** input **
# file_path: path of the input file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def clean_line_feed_doubles(file_path):
    # arguments validity check
    if type(file_path) != str or "" == file_path:
        return Status.ERR_INVALID_PARAMETERS

    try:
        with open(file_path, "r", encoding='utf-8') as in_file:
            content = in_file.read()
        with open(file_path, "w", encoding='utf-8', newline='') as out_file:
            # content.replace("\n\n", "\n")
            content = re.sub('\n\n', '\n', content)  # remove double newlines
            out_file.write(content)
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function substitutes duplicated consequent spaces for single space
# in a given file. (overwrites existing file)

# ** input **
# file_path: path of the input file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def clean_space_duplicates(file_path):
    # arguments validity check
    if type(file_path) != str or "" == file_path:
        return Status.ERR_INVALID_PARAMETERS

    try:
        with open(file_path, "r", encoding='utf-8') as in_file:
            content = in_file.read()
        with open(file_path, "w", encoding='utf-8', newline='') as out_file:
            content = re.sub(' +', ' ', content)  # remove duplicated space
            out_file.write(content)
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function cleans all spaces in a given file. (overwrites existing file)

# ** input **
# file_path: path of the input file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def clean_all_spaces(file_path):
    # arguments validity check
    if type(file_path) != str or "" == file_path:
        return Status.ERR_INVALID_PARAMETERS

    try:
        with open(file_path, "r", encoding='utf-8') as in_file:
            content = in_file.read()
        with open(file_path, "w", encoding='utf-8', newline='') as out_file:
            content = re.sub(' +', '', content)
            out_file.write(content)
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function extracts file info out of path:
# 1- file name.
# 2. file extension.

# ** input **
# file_path: path of the input file.
# file_info: empty list to save file info into.
#            file_info[0] --> file name
#            file_info[1] --> file extension
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def get_file_name_and_extension_separated(file_path, file_info):
    # arguments validity check
    if type(file_path) != str or "" == file_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(file_info) != list or 0 != len(file_info):
        return Status.ERR_INVALID_PARAMETERS

    try:
        full_name = os.path.basename(file_path)
        separated_info = os.path.splitext(full_name)
        file_info.append(separated_info[0])
        file_info.append(separated_info[1])
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function converts a xlsx file to csv file.

# ** input **
# xlsx_path: path of the xlsx file.
# sheet_name: name of the sheet in the xlsx file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def convert_xlsx_to_csv(xlsx_path, sheet_name):
    # arguments validity check
    if type(xlsx_path) != str or "" == xlsx_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(sheet_name) != str or "" == sheet_name:
        return Status.ERR_INVALID_PARAMETERS

    output_dir = "./output_files/"
    # Parse new csv file name
    file_info = []
    file_status = get_file_name_and_extension_separated(xlsx_path, file_info)
    if file_status == Status.OK:
        print("convert xlsx: file_info = ", file_info)
        csv_name = file_info[0] + ".csv"
        save_path = output_dir + csv_name

        # Read Excel file and convert
        xlsx_data = pandas.read_excel(xlsx_path, sheet_name, index_col=None)
        xlsx_data.to_csv(save_path, encoding='utf-8', index=False)

    return file_status

# -------------------------- Overview --------------------------
# This function checks if a given column name exists in a given csv
# file header and returns the index of the column.

# ** input **
# csv_header: header of a csv file.
# column: column name to be checked.
# ** output **
# returns index of column if column exists in header, otherwise returns -1.
def get_column_index_in_header(csv_header, column):
    header_len = len(csv_header)
    for header_itr in range(header_len):
        if column == csv_header[header_itr]:
            return header_itr

    return -1

# -------------------------- Overview --------------------------
# This function sorts a csv file by given column, order and sorting type.

# ** input **
# csv_path: path of the csv input file to be sorted.
# column: desired column to be sorted by.
# order: "ASC" for ascending, "DESC" for descending.
# sortType: "A" for alphabetically, "N" for numerically.
# deli: delimiter used in csv file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def sort_csv_file(csv_path, column, order, sortType, deli):
    # arguments validity check
    if type(csv_path) != str or "" == csv_path or type(column) != str or "" == column:
        return Status.ERR_INVALID_PARAMETERS
    if order != "ASC" and order != "DESC":
        print("please insert right order format. file was not sorted!")
        return Status.ERR_INVALID_PARAMETERS
    if sortType != "A" and sortType != "N":
        print("please insert right sorting type format. file was not sorted!")
        return Status.ERR_INVALID_PARAMETERS
    if type(deli) != str or "" == deli:
        print("please insert right delimiter format. file was not sorted!")
        return Status.ERR_INVALID_PARAMETERS

    output_dir = "./output_files/"
    # open file
    try:
        sorted_csv_name = "sorted_{}".format(os.path.basename(csv_path))
        with open(csv_path, "r", encoding='utf-8') as input_file, \
                open(output_dir + sorted_csv_name, "w", encoding='utf-8', newline='') as sorted_file:
            file_reader = csv.reader(input_file, delimiter=deli)
            file_writer = csv.writer(sorted_file, delimiter=deli)

            # save and skip header
            header = next(file_reader)
            column_index = get_column_index_in_header(header, column)
            if -1 == column_index:
                return Status.ERR_INVALID_PARAMETERS

            # sort file by Live_user column
            if order == "ASC":
                if sortType == "A":
                    sortedlist = sorted(file_reader, key=operator.itemgetter(column_index), reverse=False)
                elif sortType == "N":
                    sortedlist = sorted(file_reader, key=lambda row: int(row[column_index]), reverse=False)
            else:
                if sortType == "A":
                    sortedlist = sorted(file_reader, key=operator.itemgetter(column_index), reverse=True)
                elif sortType == "N":
                    sortedlist = sorted(file_reader, key=lambda row: int(row[column_index]), reverse=True)

            if header is not None:
                file_writer.writerow(header)
            for row in sortedlist:
                file_writer.writerow(row)
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function finds the list of the columns to be dropped from a file
# by a predefined keep columns list.

# ** input **
# file_path: path of the input file.
# keep_list: list of columns to keep in csv file.
# drop_list: empty list to save in it columns to be dropped from csv file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def get_columns_drop_list(file_path, keep_list, drop_list):
    # arguments validity check
    if type(file_path) != str or "" == file_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(keep_list) != list or type(drop_list) != list or 0 == len(keep_list):
        return Status.ERR_INVALID_PARAMETERS

    # open file
    try:
        with open(file_path, "r", encoding='utf-8') as input_file:
            input_file_reader = csv.reader(input_file)

            header_row = next(input_file_reader)
            header_len = len(header_row)
            keep_list_len = len(keep_list)
            for header_itr in range(header_len):
                header_col_st = header_row[header_itr]
                for keep_itr in range(keep_list_len):
                    if header_col_st == keep_list[keep_itr]:  # if found in keep list, stop search
                        break

                # if reached end, therefore not found in keep list
                if keep_itr == keep_list_len - 1 and header_col_st != keep_list[keep_itr]:
                    drop_list.append(header_col_st)

    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function eliminates a given list of columns unnecessary from
# header in a given file path.

# ** input **
# file_path: path of the input file.
# list_to_eliminate: list of the columns in csv header that are unnecessary
# to the final users file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def eliminate_columns_from_csv(file_path, list_to_eliminate):
    # arguments validity check
    if type(file_path) != str or "" == file_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(list_to_eliminate) != list or 0 == len(list_to_eliminate):
        return Status.ERR_INVALID_PARAMETERS

    output_dir = "./output_files/"
    try:
        processed_file_name = os.path.basename(file_path)
        output_path = output_dir + processed_file_name

        data = pandas.read_csv(file_path)
        new_data = data.drop(list_to_eliminate, inplace=False, axis=1)
        new_data.to_csv(output_path, index=False, escapechar=' ', quoting=csv.QUOTE_NONE)
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function sorts a csv file by given column, order using pandas library.

# ** input **
# csv_path: path of the csv input file to be sorted.
# column: desired column to be sorted by.
# order: "ASC" for ascending, "DESC" for descending.
# deli: delimiter used in csv file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def sort_csv_file_with_pandas(csv_path, column, order, deli):
    # arguments validity check
    if type(csv_path) != str or "" == csv_path or type(column) != str or "" == column:
        return Status.ERR_INVALID_PARAMETERS
    if order != "ASC" and order != "DESC":
        print("please insert right order format. file was not sorted!")
        return Status.ERR_INVALID_PARAMETERS
    if type(deli) != str or "" == deli:
        print("please insert right delimiter format. file was not sorted!")
        return Status.ERR_INVALID_PARAMETERS

    output_dir = "./output_files/"
    # open file
    try:
        sorted_csv_name = "sorted_{}".format(os.path.basename(csv_path))
        csv_file = pandas.read_csv(csv_path, encoding='utf-8', delimiter=deli)

        if order == "ASC":
            sorted_csv = csv_file.sort_values(column, ascending=True)
        else:
            sorted_csv = csv_file.sort_values(column, ascending=False)

        sorted_csv.to_csv(output_dir + sorted_csv_name, encoding='utf-8', line_terminator='',
                          sep=deli, index=False, quoting=csv.QUOTE_NONE)

    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function converts a csv file to html file using pandas library.

# ** input **
# csv_path: path of the csv input file.
# html_name: name of the output html file.
# deli: delimiter used in csv file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def convert_csv_to_html(csv_path, html_name, deli):
    # arguments validity check
    if type(csv_path) != str or "" == csv_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(html_name) != str or "" == html_name:
        return Status.ERR_INVALID_PARAMETERS
    if type(deli) != str or "" == deli:
        return Status.ERR_INVALID_PARAMETERS

    dir_path = []
    status_result = get_path_without_basename(csv_path, dir_path)
    if Status.OK != status_result:
        print("getting path without basename failure")
        return status_result
    html_path = dir_path[0] + "/{}".format(html_name)

    try:
        # pandas.set_option('display.max_colwidth', 600)
        # pandas.describe_option('display')
        csv_dataframe = pandas.read_csv(csv_path, encoding='utf-8', delimiter=deli)
        csv_dataframe.to_html(html_path, encoding='utf-8', justify="center")
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK
