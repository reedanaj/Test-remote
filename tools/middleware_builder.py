########################################################################################################################
#       Author: Reedan Ajamia.                                                                                         #
#       Date: July, 2021.                                                                                              #
#       Company: Personetics.                                                                                          #
#                                                                                                                      #
#   This Python script gets 3 csv files of virtual users, seed population and middleware hints.                        #
#   It generates a file of virtual users with their middleware hints values.                                           #
#                                                                                                                      #
#   This script takes as an input the following files:                                                                 #
#   1. virtual_users.csv                                                                                               #
#       Header: partyId                                                                                                #
#   2. population.csv                                                                                                  #
#       Header: partyId                                                                                                #
#   3. Live_users_with_hints.csv                                                                                       #
#       Header: partyId,hints                                                                                          #
#                                                                                                                      #
#   The output of this script is:                                                                                      #
#   1. virtuals_with_hints.csv                                                                                         #
#       Header: partyId,hints                                                                                          #
########################################################################################################################


#!/usr/bin/env python3

from csv_functions import *

# Initializations
maximize_csv_field_limit()

# Constants
INPUTS_DIR = "./input_files/"
OUTPUTS_DIR = "./output_files/"

VIRTUALS_HEADER = "partyId"
VIRTUALS_HEADER_LEN = 7
VIRTUALS_ROW_LEN = 1
POPULATION_HEADER = "partyId"
POPULATION_HEADER_LEN = 7
POPULATION_ROW_LEN = 1
MIDDLEWARE_HINTS_HEADER = "partyId,hints"
MIDDLEWARE_HINTS_HEADER_LEN = 13
MIDDLEWARE_HINTS_ROW_LEN = 2

LIVES_W_HINTS_HEADER = "partyId,hints"
LIVES_W_HINTS_HEADER_LEN = 13
VIRTUALS_WITH_HINTS_HEADER = "partyId,hints"

NO_HINTS_PADDING = "{\"accounts\":[]}"


# ------------------------------------------ Functions ------------------------------------------

# -------------------------- Overview --------------------------
# This function changes the first instance of the "comma" delimiter to
# a new given delimiter.

# ** input **
# csv_path: path of the csv file.
# redelimited_outFile_name: name of the output file.
# new_delimiter: new delimiter to be replaced with the comma.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def change_first_comma_delimiter(csv_path, redelimited_outFile_name, new_delimiter):
    # arguments validity check
    if type(csv_path) != str or "" == csv_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(redelimited_outFile_name) != str or "" == redelimited_outFile_name:
        return Status.ERR_INVALID_PARAMETERS
    if type(new_delimiter) != str or "" == new_delimiter:
        return Status.ERR_INVALID_PARAMETERS

    # open files
    try:
        with open(csv_path, "r", encoding='utf-8') as csv_file, \
                open(OUTPUTS_DIR + redelimited_outFile_name, "w", encoding='utf-8', newline='') as reformatted_file:

            lines = csv_file.readlines()
            for line in lines:
                line_lst = list(line)
                first_comma = True
                list_iter = 0
                for ch in line_lst:
                    if ch == ',':
                        if first_comma:
                            line_lst[list_iter] = new_delimiter
                            first_comma = False
                    list_iter += 1

                new_line = "".join(line_lst)
                reformatted_file.write(new_line)
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function validates that the files exist and if the files format
# complies with the required format.

# ** input **
# virtuals_inFile_path: path of the virtual users file.
# population_inFile_path: path of the population file.
# hints_inFile_path: path of the middleware hints file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_FILE - file does not comply with required format.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def validate_input_files(virtuals_inFile_path, population_inFile_path, hints_inFile_path):
    # arguments validity check
    if type(virtuals_inFile_path) != str or "" == virtuals_inFile_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(population_inFile_path) != str or "" == population_inFile_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(hints_inFile_path) != str or "" == hints_inFile_path:
        return Status.ERR_INVALID_PARAMETERS

    # open files for validation
    try:
        with open(virtuals_inFile_path, "r", encoding='utf-8') as virtuals_file, \
                open(population_inFile_path, "r", encoding='utf-8') as population_file, \
                open(hints_inFile_path, "r", encoding='utf-8') as hints_file:

            virtuals_reader = csv.reader(virtuals_file)
            population_reader = csv.reader(population_file)
            hints_reader = csv.reader(hints_file)

            # read headers
            virtuals_row = next(virtuals_reader)
            population_row = next(population_reader)
            hints_row = next(hints_reader)

            virtuals_header = ','.join(virtuals_row)
            population_header = ','.join(population_row)
            hints_header = ','.join(hints_row)

            if virtuals_header != VIRTUALS_HEADER:
                print("ERROR:")
                print("The first file input doesn't comply with required format!")
                print("Required file format:")
                print("\"partyId\"")
                return Status.ERR_INVALID_FILE
            if population_header != POPULATION_HEADER:
                print("ERROR:")
                print("The second file input doesn't comply with required format!")
                print("Required file format:")
                print("\"partyId\"")
                return Status.ERR_INVALID_FILE
            if hints_header != MIDDLEWARE_HINTS_HEADER:
                print("ERROR:")
                print("The Third file input doesn't comply with required format!")
                print("Required file format:")
                print("\"partyId,hints\"")
                return Status.ERR_INVALID_FILE

    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function matches between two files:
# 1) "population" file.
# 2) "middleware hints" file.

# It outputs a file with the following entries example:
# example:
# partyId,hints
# 957_1943|{"accounts":[{"accountCurrency":"USD","accountName":"3545-CHECKING",...}}}
# 957_257565|{"accounts":[{"accountCurrency":"USD","accountName":"9195-CHECKING",...}}}

# ** input **
# population_path: path of the "population" file.
# hints_path: path of the "hints" file.
# population_with_hints_name: name of the output file.
# population_file_deli: delimiter used in population csv file.
# hints_file_deli: delimiter used in middleware hints csv file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def get_hints_for_population_users(population_path, hints_path, population_with_hints_name,
                                   population_file_deli, hints_file_deli):
    # arguments validity check
    if type(population_path) != str or "" == population_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(hints_path) != str or "" == hints_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(population_with_hints_name) != str or "" == population_with_hints_name:
        return Status.ERR_INVALID_PARAMETERS
    if type(population_file_deli) != str or "" == population_file_deli:
        return Status.ERR_INVALID_PARAMETERS
    if type(hints_file_deli) != str or "" == hints_file_deli:
        return Status.ERR_INVALID_PARAMETERS

    # open files
    try:
        population_file = pandas.read_csv(population_path, encoding='utf-8', delimiter=population_file_deli)
        hints_file = pandas.read_csv(hints_path, encoding='utf-8', delimiter=hints_file_deli)

        merged_df = pandas.merge(population_file, hints_file, on='partyId', how='inner')
        merged_df.to_csv(OUTPUTS_DIR + population_with_hints_name, encoding='utf-8',
                         line_terminator='', sep=hints_file_deli, index=False, quoting=csv.QUOTE_NONE)
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function builds a file of virtual users with middleware hints
# using two files:
# 1) "virtual users" file.
# 2) "live_users_with_hints" file.

# It outputs a file with the following entries example:
# example:
# partyId,hints
# 00000000000000|{"accounts":[{"accountCurrency":"USD","accountName":"3545-CHECKING",...}}}
# 00010000000001|{"accounts":[{"accountCurrency":"USD","accountName":"9195-CHECKING",...}}}

# ** input **
# virtuals_file_path: path of the "virtual users" file.
# base_file_path: path of the "live_users_with_hints" file.
# virtuals_with_hints_name: name of the output file.
# virtuals_file_deli: delimiter used in "virtual users" csv file.
# base_file_deli: delimiter used in "live users with hints" csv file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def build_virtuals_w_hints_file(virtuals_file_path, base_file_path, virtuals_with_hints_name,
                                virtuals_file_deli, base_file_deli):
    # arguments validity check
    if type(virtuals_file_path) != str or "" == virtuals_file_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(base_file_path) != str or "" == base_file_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(virtuals_with_hints_name) != str or "" == virtuals_with_hints_name:
        return Status.ERR_INVALID_PARAMETERS
    if type(virtuals_file_deli) != str or "" == virtuals_file_deli:
        return Status.ERR_INVALID_PARAMETERS
    if type(base_file_deli) != str or "" == base_file_deli:
        return Status.ERR_INVALID_PARAMETERS

    virtuals_count = []
    status_result = get_file_lines_count(virtuals_file_path, virtuals_count)
    if Status.OK != status_result:
        return status_result

    population_count = []
    status_result = get_file_lines_count(base_file_path, population_count)
    if Status.OK != status_result:
        return status_result

    # open files
    try:
        with open(virtuals_file_path, "r", encoding='utf-8') as virtuals_file,\
                open(base_file_path, "r", encoding='utf-8') as base_file:

            virtuals_reader = csv.reader(virtuals_file, delimiter=virtuals_file_deli)
            base_file_reader = csv.reader(base_file, delimiter=base_file_deli, quoting=csv.QUOTE_NONE)

            # skip headers
            virtuals_row = next(virtuals_reader)
            base_file_row = next(base_file_reader)

            final_header = base_file_row
            lives_w_hints_itr = 0
            final_output_list = []
            for virtuals_itr in range(virtuals_count[0]):
                row_list = []
                virtuals_row = next(virtuals_reader)
                base_file_row = next(base_file_reader)

                # assign info from virtuals file to row list
                row_list.append(virtuals_row[0])

                # assign info from lives with accounts file to row list
                row_list.append(base_file_row[1])

                # append a single row to the final output list
                final_output_list.append(row_list)

                lives_w_hints_itr += 1
                if lives_w_hints_itr == population_count[0]:
                    base_file.seek(LIVES_W_HINTS_HEADER_LEN + 1, 0)
                    lives_w_hints_itr = 0

            output_dataframe = pandas.DataFrame(final_output_list)
            output_dataframe.to_csv(OUTPUTS_DIR + virtuals_with_hints_name, encoding='utf-8',
                                    line_terminator='', sep=base_file_deli, index=False,
                                    quoting=csv.QUOTE_NONE, header=final_header)

    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# ** input **
# virtuals_inFile_path: path of the "virtual users" file.
# population_inFile_path: path of the "seed population" file.
# hints_inFile_path: path of the "middleware hints" file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def clean_cr_chars_in_csv_input(virtuals_inFile_path, population_inFile_path, hints_inFile_path):
    # arguments validity check
    if type(virtuals_inFile_path) != str or "" == virtuals_inFile_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(population_inFile_path) != str or "" == population_inFile_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(hints_inFile_path) != str or "" == hints_inFile_path:
        return Status.ERR_INVALID_PARAMETERS

    status_result = clean_carriage_return(virtuals_inFile_path)
    if Status.OK != status_result:
        return status_result
    status_result = clean_carriage_return(population_inFile_path)
    if Status.OK != status_result:
        return status_result
    status_result = clean_carriage_return(hints_inFile_path)
    if Status.OK != status_result:
        return status_result

    return Status.OK

# -------------------------- Overview --------------------------
# This function is called from the main function, and it calls for
# all functions in the script.

# ** input **
# virtuals_inFile_path: path of the "virtual users" file.
# population_inFile_path: path of the "seed population" file.
# hints_inFile_path: path of the "middleware hints" file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_DIR_EXISTS - directory already exists.
# ERR_DIR_NOT_EXISTS - directory does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_OS - system error.
# ERR_INVALID_FILE - file does not comply with required format.
def run_script(virtuals_inFile_path, population_inFile_path, hints_inFile_path):
    validation_result = validate_input_files(virtuals_inFile_path, population_inFile_path, hints_inFile_path)
    if Status.OK != validation_result:
        print("files validation failure")
        return validation_result

    file_delimiter = ","
    alternative_delimiter = "|"
    status_result = create_directory(OUTPUTS_DIR)
    if Status.OK != status_result and Status.ERR_DIR_EXISTS != status_result:
        print("creating directory failure")
        return status_result

    status_result = clean_cr_chars_in_csv_input(virtuals_inFile_path, population_inFile_path, hints_inFile_path)
    if Status.OK != status_result:
        print("cleaning carriage return in csv input failure")
        return status_result

    redelimited_hints_outFile_name = "redelimited_{}".format(os.path.basename(hints_inFile_path))
    status_result = change_first_comma_delimiter(hints_inFile_path,
                                                 redelimited_hints_outFile_name,
                                                 alternative_delimiter)
    if Status.OK != status_result:
        print("changing first comma delimiter failure")
        return status_result
    redelimited_hints_outFile_path = OUTPUTS_DIR + redelimited_hints_outFile_name
    status_result = clean_carriage_return(redelimited_hints_outFile_path)
    if Status.OK != status_result:
        print("cleaning carriage return failure")
        return status_result

    virtual_users_count = []
    status_result = get_file_lines_count(virtuals_inFile_path, virtual_users_count)
    if Status.OK != status_result:
        print("getting virtual users count failure")
        return status_result
    population_count = []
    status_result = get_file_lines_count(population_inFile_path, population_count)
    if Status.OK != status_result:
        print("getting population count failure")
        return status_result

    status_result = sort_csv_file_with_pandas(population_inFile_path, "partyId", "ASC", file_delimiter)
    if Status.OK != status_result:
        print("sorting file failure")
        return status_result
    sorted_population_outFile_name = "sorted_{}".format(os.path.basename(population_inFile_path))
    sorted_population_outFile_path = OUTPUTS_DIR + sorted_population_outFile_name
    status_result = clean_carriage_return(sorted_population_outFile_path)
    if Status.OK != status_result:
        print("cleaning carriage return failure")
        return status_result

    status_result = sort_csv_file_with_pandas(redelimited_hints_outFile_path, "partyId", "ASC", alternative_delimiter)
    if Status.OK != status_result:
        print("sorting file failure")
        return status_result
    sorted_hints_outFile_name = "sorted_{}".format(os.path.basename(redelimited_hints_outFile_name))
    sorted_hints_outFile_path = OUTPUTS_DIR + sorted_hints_outFile_name
    status_result = clean_carriage_return(sorted_hints_outFile_path)
    if Status.OK != status_result:
        print("cleaning carriage return failure")
        return status_result

    lives_with_hints_outFile_name = "live_users_with_hints.csv"
    status_result = get_hints_for_population_users(sorted_population_outFile_path, sorted_hints_outFile_path,
                                                   lives_with_hints_outFile_name,
                                                   file_delimiter, alternative_delimiter)
    if Status.OK != status_result:
        print("building live users with middleware hints file failure")
        return status_result
    lives_with_hints_outFile_path = OUTPUTS_DIR + lives_with_hints_outFile_name
    status_result = clean_carriage_return(lives_with_hints_outFile_path)
    if Status.OK != status_result:
        print("cleaning carriage return failure")
        return status_result

    virtuals_with_hints_outFile_name = "virtuals_with_hints.csv"
    status_result = build_virtuals_w_hints_file(virtuals_inFile_path, lives_with_hints_outFile_path,
                                                virtuals_with_hints_outFile_name, file_delimiter,
                                                alternative_delimiter)
    if Status.OK != status_result:
        print("building virtual users with middleware hints file failure")
        return status_result
    virtuals_with_hints_outFile_path = OUTPUTS_DIR + virtuals_with_hints_outFile_name
    status_result = clean_carriage_return(virtuals_with_hints_outFile_path)
    if Status.OK != status_result:
        print("cleaning carriage return failure")
        return status_result

    return Status.OK

def main():
    if len(sys.argv) < 4:
        sys.exit("\nUsage:\n"
                 "python3 middleware_builder.py <file1_path> <file2_path> <file3_path>\n"
                 "Where:\n"
                 "<file1_path> - file path of virtual users file.\n"
                 "<file2_path> - file path of seed population file.\n"
                 "<file3_path> - file path of live users with their middleware hints file.\n"
                 "e.g:\n"
                 "python3 middleware_builder.py virtuals.csv seed_population.csv middleware.csv\n")

    virtual_users_path = sys.argv[1]
    seed_population_path = sys.argv[2]
    middleware_path = sys.argv[3]

    # virtual_users_path = ".\\input_files\\virtuals.csv"
    # seed_population_path = ".\\input_files\\population.csv"
    # middleware_path = ".\\input_files\\hints.csv"

    run_time_result = run_script(virtual_users_path, seed_population_path, middleware_path)
    if Status.OK == run_time_result:
        print_status_message(run_time_result)
    else:
        print_status_message(run_time_result)
        print("Terminating...")

if __name__ == "__main__":
    main()
