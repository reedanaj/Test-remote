########################################################################################################################
#       Author: Reedan Ajamia.                                                                                         #
#       Date: July, 2021.                                                                                              #
#       Company: Personetics.                                                                                          #
#                                                                                                                      #
#   This Python script gets a csv file of totals of users and desired around mean of the transactions of users.        #
#   It simulates a Normal Distribution of the users, in the following way:                                             #
#   users must have:                                                                                                   #
# 	a. Num_of_transactions > 100 and transactions < 2000.                                                              #
# 	b. Num_of_insights_generated > 3.                                                                                  #
# 	c. Num_of_accounts > 1.                                                                                            #
#                                                                                                                      #
#   Then, the distribution would be as follows:                                                                        #
#   a. top 3 users with maximum Num_of_transactions. (smaller than 2000)                                               #
#   b. 50 users with Num_of_transactions > (avg + 150) and Num_of_transactions < 2000 and not in the top 3 users.      #
#   c. 400 users with Num_of_transactions (avg - 150) --> (avg + 150).                                                 #
#   d. 50 users with Num_of_transactions between 100 --> (avg - 150).                                                  #
########################################################################################################################


#!/usr/bin/env python3
import sys
import os           # remove
import random       # shuffle
import shutil       # copy
from csv_functions import *


# constants
INPUTS_DIR = "./input_files/"
OUTPUTS_DIR = "./output_files/"

# population conditions
MAX_TRANSACTIONS = 2000
MIN_TRANSACTIONS = 100
MIN_GEN_INSIGHTS = 3
MIN_NUM_ACCOUNTS = 1
DEVIATION = 150
TOP_TRANSACTIONS = 3        # default = 3
MORE_DEV_CNT = 50           # default = 50
AROUND_MEAN_CNT = 400       # default = 400
LESS_DEV_CNT = 50           # default = 50
SHUFFLE_TIMES = 5


# ------------------------------------------ Functions ------------------------------------------

# -------------------------- Overview --------------------------
# This function validates that the population file exist and its format
# complies with the required format.

# ** input **
# population_inFile_path: path of the "population" file.
# mandatory_columns_list: list of the required columns in the header.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_INVALID_FILE - file does not comply with required format.
def validate_population_file(population_inFile_path, mandatory_columns_list):
    # arguments validity check
    if type(population_inFile_path) != str or "" == population_inFile_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(mandatory_columns_list) != list or len(mandatory_columns_list) == 0:
        return Status.ERR_INVALID_PARAMETERS

    # open file for validation
    try:
        with open(population_inFile_path, "r", encoding='utf-8') as population_file:
            population_reader = csv.reader(population_file)

            # read header
            population_header = next(population_reader)

            header_len = len(population_header)
            mandatory_list_len = len(mandatory_columns_list)
            for mandatory_itr in range(mandatory_list_len):
                mandatory_col_st = mandatory_columns_list[mandatory_itr]
                for header_itr in range(header_len):

                    # if mandatory column found in header, stop search
                    if mandatory_col_st == population_header[header_itr]:
                        break

                # if reached end, therefore mandatory column not found in header
                if header_itr == header_len - 1 and mandatory_col_st != population_header[header_itr]:
                    print("ERROR:")
                    print("The file input doesn't comply with required format!")
                    print("Required file format:")

                    # print mandatory header list
                    for i in range(mandatory_list_len):
                        print(mandatory_columns_list[i], end="")
                        if i != mandatory_list_len - 1:
                            print(",", end="")

                    print()
                    return Status.ERR_INVALID_FILE

    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function runs over transactions of users in population file
# and computes the average of them.

# ** input **
# population_path: path of the population file.
# avg: list variable to store the average in.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def get_average_of_transactions(population_path, avg):
    # arguments validity check
    if type(population_path) != str or "" == population_path or type(avg) != list:
        return Status.ERR_INVALID_PARAMETERS

    transactions_sum = 0
    transactions_count = 0
    # open file
    try:
        with open(population_path, "r", encoding='utf-8') as population_file:
            population_reader = csv.reader(population_file)

            # skip headers
            population_row = next(population_file)

            for population_row in population_reader:
                transactions_sum += int(population_row[1])
                transactions_count += 1
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    avg.append(transactions_sum / transactions_count)
    return Status.OK

# -------------------------- Overview --------------------------
# This function searches and creates a file of qualified users,
# fulfilling the requested conditions:
# 	a. have transactions > 100 and transactions < 2000
# 	b. have Num_of_insights_generated > 3.
# 	c. have Num_of_accounts > 1.

# ** input **
# sorted_population_path: path of the population file sorted in Descending order.
# base_population_inFile_name: name of base population file (this argument
# is passed to make it possible to create a file with specific pattern).
# population_header: list of columns in the population header.
# deli: delimiter used in csv file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def build_qualified_population_file(sorted_population_path, base_population_inFile_name, population_header, deli):
    # arguments validity check
    if type(sorted_population_path) != str or "" == sorted_population_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(base_population_inFile_name) != str or "" == base_population_inFile_name:
        return Status.ERR_INVALID_PARAMETERS
    if type(population_header) != list:
        return Status.ERR_INVALID_PARAMETERS
    if type(deli) != str or "" == deli:
        return Status.ERR_INVALID_PARAMETERS

    # open files
    try:
        with open(sorted_population_path, "r", encoding='utf-8') as sorted_pop_file, \
                open(OUTPUTS_DIR + "qualified_{}".format(base_population_inFile_name),
                     "w", encoding='utf-8', newline='') as processed_file:

            sorted_pop_reader = csv.reader(sorted_pop_file, delimiter=deli)
            processed_file_writer = csv.writer(processed_file, delimiter=deli)

            # skip header
            population_row = next(sorted_pop_reader)

            population_file_header = ','.join(population_header) + "\n"
            processed_file.write(population_file_header)
            population_row = next(sorted_pop_reader)
            population_row_len = len(population_row)
            final_output_list = []
            while int(population_row[1]) > MIN_TRANSACTIONS:
                if int(population_row[1]) < MAX_TRANSACTIONS and int(population_row[3]) > MIN_GEN_INSIGHTS and \
                        int(population_row[4]) > MIN_NUM_ACCOUNTS:
                    row_list = []
                    for population_col_itr in range(population_row_len):
                        # assign info from population file to row list
                        row_list.append(population_row[population_col_itr])

                    final_output_list.append(row_list)

                population_row = next(sorted_pop_reader)

            for row in final_output_list:
                processed_file_writer.writerow(row)

    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function randomly picks several kinds of groups of users and writes
# these users to a file. Users must fulfill the requested conditions to be
# in certain group:
# a. top 3 users with maximum Num_of_transactions. (smaller than 2000)
# b. 50 users with Num_of_transactions > (avg + 150) and Num_of_transactions < 2000
#    and not in the top 3 users.
# c. 400 users with Num_of_transactions (avg - 150) --> (avg + 150).
# d. 50 users with Num_of_transactions between 100 --> (avg - 150).

# ** input **
# qualified_population_path: path of the population file of qualified users.
# base_population_inFile_name: name of base population file (this argument
# is passed to make it possible to create a file with specific pattern).
# gaussian_mean: mean of distribution of users.
# users_counter: list variable to store the users count in.
# population_header: list of columns in the population header.
# deli: delimiter used in csv file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def build_final_population_file(qualified_population_path, base_population_inFile_name,
                                gaussian_mean, users_counter, population_header, deli):
    # arguments validity check
    if type(qualified_population_path) != str or "" == qualified_population_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(base_population_inFile_name) != str or "" == base_population_inFile_name:
        return Status.ERR_INVALID_PARAMETERS
    if (type(gaussian_mean) != int and type(gaussian_mean) != float) or 1 > gaussian_mean:
        return Status.ERR_INVALID_PARAMETERS
    if type(users_counter) != list or type(population_header) != list:
        return Status.ERR_INVALID_PARAMETERS
    if type(deli) != str or "" == deli:
        return Status.ERR_INVALID_PARAMETERS

    # open files
    try:
        with open(qualified_population_path, "r", encoding='utf-8') as qualified_pop_file, \
                open(OUTPUTS_DIR + "final_{}".format(base_population_inFile_name), "w",
                     encoding='utf-8', newline='') as processed_file:

            qualified_pop_reader = csv.reader(qualified_pop_file, delimiter=deli)
            processed_file_writer = csv.writer(processed_file, delimiter=deli)

            # skip header
            population_row = next(qualified_pop_reader)

            # skip top users of max NUM_OF_TRANSACTIONS
            for top_users_itr in range(TOP_TRANSACTIONS):
                population_row = next(qualified_pop_reader)

            # build lists of users indexes for each range
            less_dev_list = []
            around_mean_list = []
            more_dev_list = []
            file_running_index = TOP_TRANSACTIONS  # step over top transactions
            for population_row in qualified_pop_reader:
                file_running_index += 1
                if int(population_row[1]) > gaussian_mean + DEVIATION:
                    more_dev_list.append(file_running_index)

                elif gaussian_mean + DEVIATION >= int(population_row[1]) >= gaussian_mean - DEVIATION:
                    around_mean_list.append(file_running_index)

                elif gaussian_mean - DEVIATION > int(population_row[1]) >= MIN_TRANSACTIONS:
                    less_dev_list.append(file_running_index)

            # shuffle lists to create randomization factor
            for i in range(SHUFFLE_TIMES):
                random.shuffle(less_dev_list)
                random.shuffle(around_mean_list)
                random.shuffle(more_dev_list)

            # pick the wanted amount of random users
            new_more_dev_list = []
            new_around_mean_list = []
            new_less_dev_list = []
            final_users_counter = TOP_TRANSACTIONS

            current_len = MORE_DEV_CNT if MORE_DEV_CNT < len(more_dev_list) else len(more_dev_list)
            final_users_counter += current_len
            for i in range(current_len):
                new_more_dev_list.append(more_dev_list[i])

            current_len = AROUND_MEAN_CNT if AROUND_MEAN_CNT < len(around_mean_list) else len(around_mean_list)
            final_users_counter += current_len
            for j in range(current_len):
                new_around_mean_list.append(around_mean_list[j])

            current_len = LESS_DEV_CNT if LESS_DEV_CNT < len(less_dev_list) else len(less_dev_list)
            final_users_counter += current_len
            for k in range(current_len):
                new_less_dev_list.append(less_dev_list[k])

            # sort lists of randomly picked users
            new_more_dev_list.sort()
            new_around_mean_list.sort()
            new_less_dev_list.sort()

            # build final population file
            file_running_index = 1
            more_list_runner = 0
            around_list_runner = 0
            less_list_runner = 0
            new_more_dev_list_max = max(new_more_dev_list)
            new_around_mean_list_max = max(new_around_mean_list)
            new_less_dev_list_max = max(new_less_dev_list)

            population_file_header = ','.join(population_header) + "\n"
            processed_file.write(population_file_header)
            population_header_len = len(population_file_header) - 1  # -1 for line feed ('\n')
            population_header_count = len(population_header)
            qualified_pop_file.seek(population_header_len + 1, 0)
            final_output_list = []
            for population_row in qualified_pop_reader:
                # final_top_transactions_list = []
                # final_more_dev_list = []
                # final_around_mean_list = []
                # final_less_dev_list = []
                final_population_row = []
                # loop over "top transactions" users
                if file_running_index <= TOP_TRANSACTIONS:
                    for top_iter in range(population_header_count):
                        final_population_row.append(population_row[top_iter])
                    final_output_list.append(final_population_row)

                # loop over "deviation more than mean" users
                elif file_running_index <= new_more_dev_list_max and\
                        file_running_index == new_more_dev_list[more_list_runner]:

                    for more_iter in range(population_header_count):
                        final_population_row.append(population_row[more_iter])
                    final_output_list.append(final_population_row)
                    more_list_runner += 1

                # loop over "around mean" users
                elif file_running_index <= new_around_mean_list_max and\
                        file_running_index == new_around_mean_list[around_list_runner]:

                    for around_iter in range(population_header_count):
                        final_population_row.append(population_row[around_iter])
                    final_output_list.append(final_population_row)
                    around_list_runner += 1

                # loop over "deviation less than mean" users
                elif file_running_index <= new_less_dev_list_max and\
                        file_running_index == new_less_dev_list[less_list_runner]:

                    for less_iter in range(population_header_count):
                        final_population_row.append(population_row[less_iter])
                    final_output_list.append(final_population_row)
                    less_list_runner += 1

                file_running_index += 1

            for row in final_output_list:
                processed_file_writer.writerow(row)
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    users_counter.append(final_users_counter)
    return Status.OK

# -------------------------- Overview --------------------------
# This function does the following procedure:
# a. creates the final file name according to a predefined pattern.
# b. drops all columns from file except partyId column.
# c. removes header from file.

# ** input **
# final_population_outFile_path: path of the last processed population file.
# final_name: name of base population file (this argument is passed
#             to make it possible to create a file with specific pattern).
# metrics: list of two floats values:
#           a. qualified users count.
#           b. average of transactions of qualified users.
# final_users_name: list variable to store the final users file name in.
# deli: delimiter used in csv file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def build_final_users_file(final_population_outFile_path, final_name, metrics, final_users_name, deli):
    # arguments validity check
    if type(final_population_outFile_path) != str or "" == final_population_outFile_path:
        return Status.ERR_INVALID_PARAMETERS
    if type(final_name) != str or "" == final_name:
        return Status.ERR_INVALID_PARAMETERS
    if type(metrics) != list or 2 != len(metrics):
        return Status.ERR_INVALID_PARAMETERS
    if type(final_users_name) != list:
        return Status.ERR_INVALID_PARAMETERS
    if type(deli) != str or "" == deli:
        return Status.ERR_INVALID_PARAMETERS

    underscore_st = "_"
    seed_st = "seed"
    users_st = str(int(metrics[0])) + "Users"
    tx_avg_st = str(int(metrics[1])) + "Tx"
    csv_extension = ".csv"
    final_users_file_name = final_name +\
                            underscore_st +\
                            seed_st +\
                            underscore_st +\
                            users_st +\
                            underscore_st + \
                            tx_avg_st + \
                            csv_extension

    shutil.copy(final_population_outFile_path, OUTPUTS_DIR + "temp_copied_file.csv")
    drop_list = []
    keep_list = ["PartyId"]
    status_result = get_columns_drop_list(OUTPUTS_DIR + "temp_copied_file.csv", keep_list, drop_list)
    if Status.OK != status_result:
        return status_result
    status_result = eliminate_columns_from_csv(OUTPUTS_DIR + "temp_copied_file.csv", drop_list)
    if Status.OK != status_result:
        return status_result

    # open files
    try:
        with open(OUTPUTS_DIR + "temp_copied_file.csv", "r", encoding='utf-8') as temp_file, \
                open(OUTPUTS_DIR + final_users_file_name, "w", encoding='utf-8', newline='') as final_file:

            temp_reader = csv.reader(temp_file, delimiter=deli)
            final_writer = csv.writer(final_file, delimiter=deli)

            # skip header
            user_row = next(temp_reader)

            for user_row in temp_reader:
                final_writer.writerow(user_row)
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    # delete temp file
    os.remove(OUTPUTS_DIR + "temp_copied_file.csv")

    final_users_name.append(final_users_file_name)
    return Status.OK

# -------------------------- Overview --------------------------
# This function cleans carriage return chars from input files.

# ** input **
# population_file_path: path of first csv population file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def clean_cr_chars_in_csv_input(population_file_path):
    # arguments validity check
    if type(population_file_path) != str or "" == population_file_path:
        return Status.ERR_INVALID_PARAMETERS

    status_result = clean_carriage_return(population_file_path)
    if Status.OK != status_result:
        return status_result

    return Status.OK

# -------------------------- Overview --------------------------
# This function is called from the main function, and it calls for
# all functions in the script.

# ** input **
# population_file_path: path of first csv population file.
# gaussian_mean: mean of distribution of users.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_DIR_EXISTS - directory already exists.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_OS - system error.
# ERR_INVALID_FILE - file does not comply with required format.
def run_script(population_file_path, gaussian_mean):
    header_keep_list = ["PartyId",
                        "NUM_OF_TRANSACTIONS",
                        "NUM_OF_INSIGHTS_RESPONSE",
                        "NUM_OF_INSIGHTS_GENERATED",
                        "NUM_OF_ACCOUNTS"]

    validation_result = validate_population_file(population_file_path, header_keep_list)
    if Status.OK != validation_result:
        print("population file validation failure")
        return validation_result

    file_delimiter = ","
    file_info = []
    status_result = clean_cr_chars_in_csv_input(population_file_path)
    if Status.OK != status_result:
        print("cleaning carriage return in csv input failure")
        return status_result

    status_result = get_file_name_and_extension_separated(population_file_path, file_info)
    if Status.OK != status_result:
        print("getting file name and extension failure")
        return status_result
    population_file_name = file_info[0]
    full_population_file_name = file_info[0] + file_info[1]

    header_drop_list = []
    status_result = get_columns_drop_list(population_file_path, header_keep_list, header_drop_list)
    if Status.OK != status_result:
        print("getting drop list failure")
        return status_result

    # -------------------------------------------------------------------------------------
    # constant prefixes
    sorted_st = "sorted_"
    qualified_st = "qualified_"
    final_st = "final_"

    # output files names
    base_population_inFile_name = full_population_file_name
    sortedTX_outFile_name = sorted_st + full_population_file_name
    qualified_population_outFile_name = qualified_st + full_population_file_name
    final_population_outFile_name = final_st + full_population_file_name

    # output files paths
    base_population_inFile_path = OUTPUTS_DIR + base_population_inFile_name
    sortedTX_outFile_path = OUTPUTS_DIR + sortedTX_outFile_name
    qualified_population_outFile_path = OUTPUTS_DIR + qualified_population_outFile_name
    final_population_outFile_path = OUTPUTS_DIR + final_population_outFile_name
    # -------------------------------------------------------------------------------------

    # function calls
    status_result = create_directory(OUTPUTS_DIR)
    status_result = eliminate_columns_from_csv(population_file_path, header_drop_list)
    if Status.OK != status_result:
        print("columns elimination failure")
        return status_result

    status_result = sort_csv_file(OUTPUTS_DIR + base_population_inFile_name,
                                  "NUM_OF_TRANSACTIONS", "DESC", "N", file_delimiter)
    if Status.OK != status_result:
        print("sorting file failure")
        return status_result
    status_result = clean_carriage_return(sortedTX_outFile_path)
    if Status.OK != status_result:
        print("cleaning carriage return failure")
        return status_result

    status_result = build_qualified_population_file(sortedTX_outFile_path, base_population_inFile_name,
                                                    header_keep_list, file_delimiter)
    if Status.OK != status_result:
        print("building qualified population failure")
        return status_result
    status_result = clean_carriage_return(qualified_population_outFile_path)
    if Status.OK != status_result:
        print("cleaning carriage return failure")
        return status_result

    final_users_count = []
    status_result = build_final_population_file(qualified_population_outFile_path, base_population_inFile_name,
                                                gaussian_mean, final_users_count, header_keep_list, file_delimiter)
    if Status.OK != status_result:
        print("building final population failure")
        return status_result
    status_result = clean_carriage_return(final_population_outFile_path)
    if Status.OK != status_result:
        print("cleaning carriage return failure")
        return status_result

    transactions_avg = []
    status_result = get_average_of_transactions(final_population_outFile_path, transactions_avg)
    if Status.OK != status_result:
        print("getting average of transactions failure")
        return status_result

    metrics = [float(final_users_count[0]), transactions_avg[0]]
    final_users_outFile_name = []
    status_result = build_final_users_file(final_population_outFile_path, population_file_name,
                                           metrics, final_users_outFile_name, file_delimiter)
    if Status.OK != status_result:
        print("building final users failure")
        return status_result
    final_users_outFile_path = OUTPUTS_DIR + final_users_outFile_name[0]
    status_result = clean_carriage_return(final_users_outFile_path)
    if Status.OK != status_result:
        print("cleaning carriage return failure")
        return status_result

    return Status.OK

def main():
    if len(sys.argv) < 3:
        sys.exit("\nUsage:\n"
                 "python3 population_builder.py <csv_file_path> <desired_transactions_average>\n"
                 "e.g:\n"
                 "python3 population_builder.py population.csv 400\n")

    population_file_path = sys.argv[1]
    gaussian_mean = sys.argv[2]

    # population_file_path = ".\\input_files\\FIS_TOTAL.csv"
    # gaussian_mean = 400

    run_time_result = run_script(population_file_path, int(gaussian_mean))
    if Status.OK == run_time_result:
        print_status_message(run_time_result)
    else:
        print_status_message(run_time_result)
        print("Terminating...")

if __name__ == "__main__":
    main()
