########################################################################################################################
#       Author: Reedan Ajamia.                                                                                         #
#       Date: October, 2021.                                                                                           #
#       Company: Personetics.                                                                                          #
#                                                                                                                      #
#       This Python script aggregates all data from a given suite directory, and generates an excel file for the       #
#       monitoring script of the High Scale Lab. The suite directory might contain csv files for each pserver          #
#       with the raw data of the performance test, like totals of getInsights API request.                             #
#       Directory content may be like:                                                                                 #
#       - 10.0.20.34_getInsights_Component_AggregateReport.csv                                                         #
#       - 10.0.20.34_10.0.20.34_Sql_AggregateReport.csv                                                                #
#       - 10.0.20.147_getInsights_Component_AggregateReport.csv                                                        #
#       - 10.0.20.147_10.0.20.34_Sql_AggregateReport.csv                                                               #
#                               .                                                                                      #
#                               .                                                                                      #
#                               .                                                                                      #
#                                                                                                                      #
#       And for all pservers combined:                                                                                 #
#       - All_getInsights_Component_AggregateReport.csv                                                                #
#       - ALL_SQL_AggregateReport.csv                                                                                  #
#       - SqlCount_20211107_0857.csv                                                                                   #
#                                                                                                                      #
########################################################################################################################


#!/usr/bin/env python3
import sys          # sys.argv
from excel_functions import *
from xlsxwriter.exceptions import DuplicateWorksheetName
import os.path      # join, isdir, splitext, basename
import re           # search
import shutil       # rmtree

# Constants
INPUTS_DIR = "./input_files/"
OUTPUTS_DIR = "./output_files/"

PERFMON_REMOVED_METRICS_LIST = ["Swap", "Network I/O", "Disks I/O"]
COMPONENT_REPORT_REMOVED_METRICS_LIST = ["TOTAL,"]

SHEET_NAME_MAX_LENGTH = 31
FILE_INFO_ROWS_COUNT = 2
LINES_BETWEEN_TABLES = 2

# Images Constants
IMAGE_X_SCALE = 0.6
IMAGE_Y_SCALE = 0.6
IMAGE_ROWS_COUNT = 24

RIGHT_IMAGES_COL_BASE = "O"
RIGHT_IMAGES_TITLES_COL_BASE = "T"
RIGHT_IMAGES_ROW_OFFSET = 27
LEFT_IMAGES_COL_BASE = "B"
LEFT_IMAGES_TITLES_COL_BASE = "G"
LEFT_IMAGES_ROW_OFFSET = 27

# Titles & Files names Constants
IP_REGEX = "(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})"
IP_EXTRACTION_REGEX = "(.+?)_[0-9]{6}_(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})_(.+?)_Component_AggregateReport\.csv$"

ALL_PSERVERS_REPORT_SUFFIXES = ["SqlCount_(.+?)\.csv$", "(.+?)_All_([a-zA-Z]+?)_Component_AggregateReport\.csv$",
                                "(.+?)_ALL_SQL_AggregateReport\.csv$"]
ALL_PSERVERS_IMAGES_SUFFIXES = ["[.]*_[0-9]{6}_PerfMon\.png"]
ALL_PSERVERS_REQUEST_TYPE_SUFFIX = "(.+?)_All_([a-zA-Z]+?)_Component_AggregateReport\.csv$"

SINGLE_PSERVER_REPORT_PREFIX = "(.+?)_[0-9]{6}_"
SINGLE_PSERVER_REPORT_SUFFIXES = ["_([a-zA-Z]+?)_Component_AggregateReport\.csv$", "_Sql_AggregateReport\.csv$"]
SINGLE_PSERVER_REQUEST_TYPE_SUFFIX = "_([a-zA-Z]+?)_Component_AggregateReport\.csv$"

PERFMON_FILE_SUFFIX = "[.]*_[0-9]{6}_PerfMon\.csv$"
ALL_AGGREGATE_REPORT_FILE_SUFFIX = "(.+?)_All_([a-zA-Z]+?)_Component_AggregateReport\.csv$"
SINGLE_AGGREGATE_REPORT_FILE_SUFFIX = "(.+?)_([a-zA-Z]+?)_Component_AggregateReport\.csv$"

# ------------------------------------------ TEMP ------------------------------------------
SINGLE_COMPONENT_REPORT_FILE_SUFFIX = "(.+?)_([a-zA-Z]+?)_Component_AggregateReport\.csv$"
MULTIPLE_COMPONENT_REPORT_FILE_SUFFIX = "(.+?)_All_([a-zA-Z]+?)_Component_AggregateReport\.csv$"

TEST_DIRECTORY_NAME_COMPONENTS = ["Project Name", "Jmeter Threads", "Pserver Revision",
                                  "Suite Test Remark", "Test Time"]

# ------------------------------------------ Functions ------------------------------------------
g_pserver_ips = []
g_requests_types = []
g_ordered_files = []
g_ordered_images = []
g_tables_titles = []
g_images_titles = []
g_tables_rows_count = []
g_tests_info_indexes = []
g_spaces_indexes = []
g_tables_titles_indexes = []
g_tables_headers_indexes = []
g_ordered_text_files = []

g_sheet_name_duplication_indexer = 1

# -------------------------- Overview --------------------------
# This function checks if a given file is qualified for the combination
# process.

# ** input **
# file: string of the file's name.
# qualified_list: list that contains regexes of the qualified file names.
# request_type: empty list to save in it the request type of this specific test.
# ** output **
# returns True if file is qualified, otherwise returns False.
def is_file_qualified_for_processing(file, qualified_list):
    for item in qualified_list:
        if re.search(item, file):
            # extracted_request = re.findall('(.+?)_([a-zA-Z]+?)_Component_AggregateReport\.csv$', file)
            # if len(extracted_request) != 0:
            #     global g_requests_types
            #     g_requests_types.append(extracted_request[0][1])

            return True

    return False

# -------------------------- Overview --------------------------
# This function checks if a given image file is qualified for the
# combination process.

# ** input **
# file: string of the image's file name.
# qualified_list: list that contains regexes of the qualified images file names.
# ** output **
# returns True if image file is qualified, otherwise returns False.
def is_image_qualified_for_processing(file, qualified_list):
    for item in qualified_list:
        if re.search(item, file):
            return True

    return False

# -------------------------- Overview --------------------------
# This function converts a given string representing an IP to a a tuple.

# ** input **
# ip_str: string of the IP.
# ** output **
# returns the IP saved in a tuple.
def ip_to_tuple(ip_str):
    ip_list = ip_str.split('.')  # make a list
    return tuple(map(int, ip_list))  # convert to int

# -------------------------- Overview --------------------------
# This function sorts a given list of IPs in the same subnet in two
# different ways: ascending, descending.

# ** input **
# ips_list: list of the IPs.
# sort_type: two different ways - ascending, descending.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def sort_ips_list_in_the_same_subnet(ips_list, sort_type):
    # arguments validity check
    if type(ips_list) != list:
        return Status.ERR_INVALID_PARAMETERS
    if type(sort_type) != str or ("ASC" != sort_type and "DESC" != sort_type):
        return Status.ERR_INVALID_PARAMETERS

    ips_as_tuples = []
    for ip in ips_list:
        ips_as_tuples.append(ip_to_tuple(ip))

    new_list = []
    if "ASC" == sort_type:
        new_list = sorted(ips_as_tuples, key=lambda x: x[0])
        new_list = sorted(ips_as_tuples, key=lambda x: x[1])
        new_list = sorted(ips_as_tuples, key=lambda x: x[2])
        new_list = sorted(ips_as_tuples, key=lambda x: x[3])

    elif "DESC" == sort_type:
        new_list = sorted(ips_as_tuples, key=lambda x: x[0], reverse=True)
        new_list = sorted(ips_as_tuples, key=lambda x: x[1], reverse=True)
        new_list = sorted(ips_as_tuples, key=lambda x: x[2], reverse=True)
        new_list = sorted(ips_as_tuples, key=lambda x: x[3], reverse=True)

    ips_list.clear()
    for tup in new_list:
        ips_list.append('.'.join(map(str, tup)))

    return Status.OK

# -------------------------- Overview --------------------------
# This function gets all IPs of pservers in a given testing directory.
# It extracts all IPs from files names for later use.

# ** input **
# dir_path: directory path of test.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_DIR_NOT_EXISTS - directory does not exist.
def get_all_pservers_ips(dir_path):
    # arguments validity check
    status_result = validate_directory_path(dir_path)
    if Status.OK != status_result:
        print("validate_directory_path failure")
        return status_result

    global g_pserver_ips
    for file in os.listdir(dir_path):
        full_file_path = dir_path + file
        if re.search(IP_EXTRACTION_REGEX, full_file_path):
            extracted_ip = re.findall(IP_EXTRACTION_REGEX, file)
            if len(extracted_ip) != 0:
                g_pserver_ips.append(extracted_ip[0][1])

    status_result = sort_ips_list_in_the_same_subnet(g_pserver_ips, "ASC")
    if Status.OK != status_result:
        print("sort_ips_list_in_the_same_subnet failure")
        return status_result

    return Status.OK

# -------------------------- Overview --------------------------
# This function arranges csv files paths needed for the all IPs report
# in a predefined order. The paths are saved in a global list variable.

# ** input **
# dir_path: directory path of test.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_DIR_NOT_EXISTS - directory does not exist.
def get_all_report_files_paths_arranged(dir_path):
    # arguments validity check
    status_result = validate_directory_path(dir_path)
    if Status.OK != status_result:
        print("validate_directory_path failure")
        return status_result

    global g_requests_types
    global g_ordered_files
    files_list = []
    for file_pattern in ALL_PSERVERS_REPORT_SUFFIXES:
        for file in os.listdir(dir_path):
            full_file_path = dir_path + file
            if re.search(file_pattern, full_file_path):
                extracted_request = re.findall(ALL_PSERVERS_REQUEST_TYPE_SUFFIX, file)
                if len(extracted_request) != 0:
                    # print(extracted_request[0][1])
                    g_requests_types.append(extracted_request[0][1])
                files_list.append(full_file_path)
                break

    g_ordered_files.append(files_list)

    return Status.OK

# -------------------------- Overview --------------------------
# This function arranges images files paths needed for the all IPs report
# in a predefined order. The paths are saved in a global list variable.

# ** input **
# dir_path: directory path of test.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_DIR_NOT_EXISTS - directory does not exist.
def get_all_report_images_paths_arranged(dir_path):
    # arguments validity check
    status_result = validate_directory_path(dir_path)
    if Status.OK != status_result:
        print("validate_directory_path failure")
        return status_result

    global g_ordered_images
    images_list = []
    for image_pattern in ALL_PSERVERS_IMAGES_SUFFIXES:
        for file in os.listdir(dir_path):
            full_image_path = dir_path + file
            if re.search(image_pattern, full_image_path):
                images_list.append(full_image_path)
                break

    g_ordered_images.append(images_list)

    return Status.OK

# -------------------------- Overview --------------------------
# This function arranges csv files paths needed for the single IP report
# in a predefined order. The paths are saved in a global list variable.

# ** input **
# dir_path: directory path of test.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_DIR_NOT_EXISTS - directory does not exist.
def get_single_report_files_paths_arranged(dir_path):
    # arguments validity check
    status_result = validate_directory_path(dir_path)
    if Status.OK != status_result:
        print("validate_directory_path failure")
        return status_result

    global g_requests_types
    global g_ordered_files
    single_files_len = len(SINGLE_PSERVER_REPORT_SUFFIXES)
    for ip in g_pserver_ips:
        files_list = []
        single_file_type = 0
        for file_type in range(single_files_len):
            pattern_to_check = SINGLE_PSERVER_REPORT_PREFIX + ip + SINGLE_PSERVER_REPORT_SUFFIXES[single_file_type]
            for file in os.listdir(dir_path):
                full_file_path = dir_path + file
                if re.search(pattern_to_check, full_file_path):
                    extracted_request = re.findall(SINGLE_PSERVER_REQUEST_TYPE_SUFFIX, file)
                    if len(extracted_request) != 0:
                        g_requests_types.append(extracted_request[0])
                    files_list.append(full_file_path)
                    break

            single_file_type += 1

        g_ordered_files.append(files_list)

    return Status.OK

# -------------------------- Overview --------------------------
# This function arranges images files paths needed for the single IP report
# in a predefined order. The paths are saved in a global list variable.

# ** input **
# dir_path: directory path of test.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_DIR_NOT_EXISTS - directory does not exist.
def get_single_report_images_paths_arranged(dir_path):
    # arguments validity check
    status_result = validate_directory_path(dir_path)
    if Status.OK != status_result:
        print("validate_directory_path failure")
        return status_result

    global g_ordered_images
    pservers_count = len(g_pserver_ips)
    for pserver_index in range(pservers_count):
        g_ordered_images.append([])  # add empty lists, because there are no images for single reports

    return Status.OK

# -------------------------- Overview --------------------------
# This function saves for each test in suite the titles of tables,
# and saves the titles in a global list of titles lists.

# ** input **
# None.
# ** output **
# returns one of the following enums:
# OK - success.
def get_all_report_tables_titles():
    tables_titles_list = []
    for file_path in g_ordered_files[0]:
        # Extract file name from file path
        full_name = os.path.basename(file_path)

        if re.search(ALL_PSERVERS_REPORT_SUFFIXES[0], full_name):
            file_title = "All_SQL_Count"
            tables_titles_list.append(file_title)
        elif re.search(ALL_PSERVERS_REPORT_SUFFIXES[1], full_name):
            file_title = "All_" + g_requests_types[0] + "_AggregateReport"
            tables_titles_list.append(file_title)
        elif re.search(ALL_PSERVERS_REPORT_SUFFIXES[2], full_name):
            file_title = "All_SQL_AggregateReport"
            tables_titles_list.append(file_title)

    global g_tables_titles
    g_tables_titles.append(tables_titles_list)

# -------------------------- Overview --------------------------
# This function saves for each test in suite the titles of tables,
# and saves the titles in a global list of titles lists.

# ** input **
# None.
# ** output **
# returns one of the following enums:
# OK - success.
def get_single_report_tables_titles():
    global g_tables_titles
    sheets_count = len(g_ordered_files)
    for sheet_index in range(sheets_count):
        if sheet_index > 0:  # skip 0 because 0 is the all report sheet
            tables_titles_list = []
            for file_path in g_ordered_files[sheet_index]:
                # Extract file name from file path
                full_name = os.path.basename(file_path)

                if re.search(SINGLE_PSERVER_REPORT_SUFFIXES[0], full_name):
                    file_title = g_pserver_ips[sheet_index - 1] + "_" + g_requests_types[0] + "_AggregateReport"
                    tables_titles_list.append(file_title)
                elif re.search(SINGLE_PSERVER_REPORT_SUFFIXES[1], full_name):
                    file_title = g_pserver_ips[sheet_index - 1] + "_SQL_AggregateReport"
                    tables_titles_list.append(file_title)

            g_tables_titles.append(tables_titles_list)

# -------------------------- Overview --------------------------
# This function saves for each test in suite the titles of images,
# and saves the titles in a global list of titles lists.

# ** input **
# None.
# ** output **
# returns one of the following enums:
# OK - success.
def get_all_report_images_titles():
    global g_images_titles
    images_titles_list = []
    for image_path in g_ordered_images[0]:
        # Extract image name from image path
        full_name = os.path.basename(image_path)
        separated_info = os.path.splitext(full_name)
        image_name = separated_info[0]

        # Extract image title from image name
        str_iterator = 0
        reversed_image_name = image_name[::-1]
        ch = reversed_image_name[str_iterator]
        while '_' != ch:
            str_iterator += 1
            ch = reversed_image_name[str_iterator]

        reversed_image_title = reversed_image_name[0:str_iterator:1]
        image_title = reversed_image_title[::-1]
        images_titles_list.append(image_title)

    g_images_titles.append(images_titles_list)

# -------------------------- Overview --------------------------
# This function saves for each test in suite the titles of images,
# and saves the titles in a global list of titles lists.

# ** input **
# None.
# ** output **
# returns one of the following enums:
# OK - success.
def get_single_report_images_titles():
    global g_images_titles
    sheets_count = len(g_ordered_files)
    for sheet_index in range(sheets_count):
        if sheet_index > 0:  # skip 0 because 0 is the all report sheet
            images_titles_list = []
            for image_path in g_ordered_images[sheet_index]:
                # Extract image name from image path
                full_name = os.path.basename(image_path)
                separated_info = os.path.splitext(full_name)
                image_name = separated_info[0]

                # Extract image title from image name
                str_iterator = 0
                reversed_image_name = image_name[::-1]
                ch = reversed_image_name[str_iterator]
                while '_' != ch:
                    str_iterator += 1
                    ch = reversed_image_name[str_iterator]

                reversed_image_title = reversed_image_name[0:str_iterator:1]
                image_title = reversed_image_title[::-1]
                images_titles_list.append(image_title)

            g_images_titles.append(images_titles_list)

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
# This function filters double consequent LF chars in all csv files
# required for the report.

# ** input **
# None.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def filter_line_feed_doubles():
    tests_count = len(g_ordered_files)
    for test_index in range(tests_count):
        for file_path in g_ordered_files[test_index]:
            status_result = clean_line_feed_doubles(file_path)
            if Status.OK != status_result:
                print("clean_line_feed_doubles failure")
                return status_result

    return Status.OK

# -------------------------- Overview --------------------------
# This function filters SQL tables counts lines by eliminating extra
# irrelevant text and keeping only relevant data.

# ** input **
# None.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
def filter_all_sql_count_table():
    file_path = g_ordered_files[0][0]  # 0 for test of all pservers, 0 for sql count table
    try:
        with open(file_path, "r", encoding='utf-8') as in_file:
            content = in_file.readlines()

        header_index = 0
        with open(file_path, "w", encoding='utf-8', newline='') as out_file:
            for line in content:
                if 0 == header_index:
                    out_file.write(line)
                    header_index += 1

                else:
                    if re.search("(.+?)TableName=([A-Z]+(_([A-Z]+))+)(.+?)RowCnt=([0-9]+)(.+)", line):
                        findings = re.findall("(.+?)TableName=([A-Z]+(_([A-Z]+))+)(.+?)RowCnt=([0-9]+)(.+)", line)
                        if len(findings) != 0:
                            new_line = findings[0][1] + "," + findings[0][5] + "\n"
                            out_file.write(new_line)
                    else:
                        out_file.write(line)

    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function checks if a given "PerfMon" line is irrelevant or not.

# ** input **
# perf_line: string variable of the line to be checked.
# ** output **
# returns True if it is an irrelevant "PerfMon" label, otherwise returns False.
def has_perfmon_irrelevant_metrics(perf_line):
    # arguments validity check
    if type(perf_line) != str or "" == perf_line:
        return False

    perf_list_len = len(PERFMON_REMOVED_METRICS_LIST)
    for i in range(perf_list_len):
        if -1 != perf_line.find(PERFMON_REMOVED_METRICS_LIST[i]):
            return True

    return False

# -------------------------- Overview --------------------------
# This function removes irrelevant metrics from a given "PerfMon" csv file.

# ** input **
# file_path: path of the input csv file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def remove_perfmon_irrelevant_metrics(file_path):
    # arguments validity check
    if type(file_path) != str or "" == file_path:
        return Status.ERR_INVALID_PARAMETERS

    try:
        with open(file_path, "r", encoding='utf-8') as in_file:
            file_lines = in_file.readlines()
            keep_lines = []
            for line in file_lines:
                if not has_perfmon_irrelevant_metrics(line):
                    keep_lines.append(line)

        with open(file_path, "w", encoding='utf-8', newline='') as out_file:
            filtered_lines = ''.join(keep_lines)
            out_file.write(filtered_lines)

    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function filters irrelevant metrics from all "PerfMon" csv
# files in a suite.

# ** input **
# None.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def filter_metrics_in_perfmon_csv_files():
    tests_count = len(g_ordered_files)
    for test_index in range(tests_count):
        for file_path in g_ordered_files[test_index]:
            if is_file_qualified_for_processing(file_path, [PERFMON_FILE_SUFFIX]):
                status_result = remove_perfmon_irrelevant_metrics(file_path)
                if Status.OK != status_result:
                    print("remove_perfmon_irrelevant_metrics failure")
                    return status_result

    return Status.OK

# -------------------------- Overview --------------------------
# This function checks if a given "Component_AggregateReport" line is
# irrelevant or not.

# ** input **
# report_line: string variable of the line to be checked.
# ** output **
# returns True if it is an irrelevant "Component_AggregateReport" label, otherwise returns False.
def has_component_aggregate_report_irrelevant_metrics(report_line):
    # arguments validity check
    if type(report_line) != str or "" == report_line:
        return False

    report_list_len = len(COMPONENT_REPORT_REMOVED_METRICS_LIST)
    for i in range(report_list_len):
        if -1 != report_line.find(COMPONENT_REPORT_REMOVED_METRICS_LIST[i]):
            return True

    return False

# -------------------------- Overview --------------------------
# This function removes irrelevant metrics from a given "Component_AggregateReport"
# csv file.

# ** input **
# file_path: path of the input csv file.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def remove_component_aggregate_report_irrelevant_metrics(file_path):
    # arguments validity check
    if type(file_path) != str or "" == file_path:
        return Status.ERR_INVALID_PARAMETERS

    try:
        with open(file_path, "r", encoding='utf-8') as in_file:
            file_lines = in_file.readlines()
            keep_lines = []
            for line in file_lines:
                if not has_component_aggregate_report_irrelevant_metrics(line):
                    keep_lines.append(line)

        with open(file_path, "w", encoding='utf-8', newline='') as out_file:
            filtered_lines = ''.join(keep_lines)
            out_file.write(filtered_lines)

    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function filters irrelevant metrics from all "Component_AggregateReport"
# csv files in a suite.

# ** input **
# None.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def filter_metrics_in_component_aggregate_report_csv_files():
    tests_count = len(g_ordered_files)
    for test_index in range(tests_count):
        for file_path in g_ordered_files[test_index]:
            if is_file_qualified_for_processing(file_path, [ALL_AGGREGATE_REPORT_FILE_SUFFIX]) or \
                    is_file_qualified_for_processing(file_path, [SINGLE_AGGREGATE_REPORT_FILE_SUFFIX]):
                status_result = remove_component_aggregate_report_irrelevant_metrics(file_path)
                if Status.OK != status_result:
                    print("remove_component_aggregate_report_irrelevant_metrics failure")
                    return status_result

    return Status.OK

# -------------------------- Overview --------------------------
# This function counts the number of rows in csv files of each test
# in suite, and saves the counts in a global list of count lists.

# ** input **
# None.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def count_tables_rows_in_csv_files():
    global g_tables_rows_count
    tests_count = len(g_ordered_files)
    for test_index in range(tests_count):

        test_rows_counts = []
        files_count = len(g_ordered_files[test_index])
        for file_index in range(files_count):
            file_path = g_ordered_files[test_index][file_index]
            try:
                with open(file_path, "r", encoding='utf-8') as in_file:
                    lines_count = len(in_file.readlines())
                    test_rows_counts.append(lines_count)
            except FileNotFoundError:
                return Status.ERR_FILE_NOT_EXISTS

        g_tables_rows_count.append(test_rows_counts)

    return Status.OK

# -------------------------- Overview --------------------------
# This function calculates the indexes of rows of test info in
# excel files of tests in a suite directory, and saves indexes in a
# global list of indexes lists.

# ** input **
# no input.
# ** output **
# no output.
def calculate_test_info_indexes():
    global g_tests_info_indexes
    tests_count = len(g_ordered_files)
    for test_index in range(tests_count):
        test_info_indexes = [1, 2]
        g_tests_info_indexes.append(test_info_indexes)

# -------------------------- Overview --------------------------
# This function calculates the indexes of rows of spaces in excel files
# of tests in a suite directory, and saves indexes in a global list of
# indexes lists.

# ** input **
# no input.
# ** output **
# no output.
def calculate_spaces_indexes():
    global g_spaces_indexes
    tests_count = len(g_ordered_files)
    for test_index in range(tests_count):
        spaces_indexes = []
        starting_index = FILE_INFO_ROWS_COUNT
        index_runner = starting_index
        tables_count = len(g_tables_rows_count[test_index])
        for tables_index in range(tables_count):
            index_runner += 1
            spaces_indexes.append(index_runner)
            index_runner += 1
            spaces_indexes.append(index_runner)
            index_runner += 1 + g_tables_rows_count[test_index][tables_index]

        # Two more times for spaces after last table
        index_runner += 1
        spaces_indexes.append(index_runner)
        index_runner += 1
        spaces_indexes.append(index_runner)

        g_spaces_indexes.append(spaces_indexes)

# -------------------------- Overview --------------------------
# This function calculates the indexes of rows of tables titles in
# excel files of tests in a suite directory, and saves indexes in a
# global list of indexes lists.

# ** input **
# no input.
# ** output **
# no output.
def calculate_tables_titles_indexes():
    global g_tables_titles_indexes
    tests_count = len(g_ordered_files)
    for test_index in range(tests_count):
        tables_titles_indexes = []
        starting_index = FILE_INFO_ROWS_COUNT
        index_runner = starting_index
        tables_count = len(g_tables_rows_count[test_index])
        for tables_index in range(tables_count):
            index_runner += LINES_BETWEEN_TABLES + 1
            tables_titles_indexes.append(index_runner)
            index_runner += g_tables_rows_count[test_index][tables_index]

        g_tables_titles_indexes.append(tables_titles_indexes)

# -------------------------- Overview --------------------------
# This function calculates the indexes of rows of tables headers in
# excel files of tests in a suite directory, and saves indexes in a
# global list of indexes lists.

# ** input **
# no input.
# ** output **
# no output.
def calculate_tables_headers_indexes():
    global g_tables_headers_indexes
    tests_count = len(g_ordered_files)
    for test_index in range(tests_count):
        tables_headers_indexes = []
        starting_index = FILE_INFO_ROWS_COUNT
        index_runner = starting_index
        tables_count = len(g_tables_rows_count[test_index])
        for tables_index in range(tables_count):
            index_runner += LINES_BETWEEN_TABLES + 2
            tables_headers_indexes.append(index_runner)
            index_runner += g_tables_rows_count[test_index][tables_index] - 1  # -1 for excluding header from count

        g_tables_headers_indexes.append(tables_headers_indexes)

# -------------------------- Overview --------------------------
# This function combines all csv files in a suite folder into a single
# text file.

# ** input **
# None.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_FILE_NOT_EXISTS - file does not exist.
def combine_csv_files_into_single_text_file():
    sheets_count = len(g_ordered_files)
    for sheet_index in range(sheets_count):
        if 0 == sheet_index:
            sheet_name = "All_AggregateReport"
        else:
            sheet_name = g_pserver_ips[sheet_index - 1] + "_AggregateReport"

        table_title_index = 0
        try:
            final_out_path = OUTPUTS_DIR + sheet_name + ".txt"
            with open(final_out_path, "a", encoding='utf-8', newline='') as combined_file:
                # write some info in the head of file
                combined_file.write("Test folder info:\n")
                combined_file.write(sheet_name + "\n")

                for file in g_ordered_files[sheet_index]:
                    try:
                        with open(file, "r", encoding='utf-8') as csv_file:
                            for i in range(LINES_BETWEEN_TABLES):
                                combined_file.write("\n")
                            combined_file.write(g_tables_titles[sheet_index][table_title_index] + "\n")
                            table_title_index += 1
                            lines = csv_file.readlines()
                            for line in lines:
                                combined_file.write(line)
                    except FileNotFoundError:
                        return Status.ERR_FILE_NOT_EXISTS

                for i in range(LINES_BETWEEN_TABLES):
                    combined_file.write("\n")

        except FileNotFoundError:
            return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function arranges text files paths needed for the final report
# in a predefined order. The paths are saved in a global list variable.

# ** input **
# dir_path: directory path of test.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_DIR_NOT_EXISTS - directory does not exist.
def get_text_files_paths_arranged(dir_path):
    # arguments validity check
    status_result = validate_directory_path(dir_path)
    if Status.OK != status_result:
        print("validate_directory_path failure")
        return status_result

    pattern_to_check = "(.+?)All(.+?)"
    for file in os.listdir(dir_path):
        full_file_path = dir_path + file
        if re.search(pattern_to_check, full_file_path):
            # global g_ordered_text_files
            g_ordered_text_files.append(full_file_path)
            break

    for ip in g_pserver_ips:
        pattern_to_check = "(.+?)" + ip + "(.+?)"
        for file in os.listdir(dir_path):
            full_file_path = dir_path + file
            if re.search(pattern_to_check, full_file_path):
                # global g_ordered_text_files
                g_ordered_text_files.append(full_file_path)
                break

    return Status.OK

# -------------------------- Overview --------------------------
# This function extracts the title of the image out of the image
# file name.

# ** input **
# image_name: name of image file.
# image_title_list: empty list to save in it the title of the image.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def get_title_for_image(image_name, image_title_list):
    # arguments validity check
    if type(image_name) != str or "" == image_name:
        return Status.ERR_INVALID_PARAMETERS
    if type(image_title_list) != list or 0 != len(image_title_list):
        return Status.ERR_INVALID_PARAMETERS

    str_iterator = 0
    reversed_image_name = image_name[::-1]
    ch = reversed_image_name[str_iterator]
    while '_' != ch:
        str_iterator += 1
        ch = reversed_image_name[str_iterator]

    reversed_image_title = reversed_image_name[0:str_iterator:1]
    image_title = reversed_image_title[::-1]
    image_title_list.append(image_title)

    return Status.OK

# -------------------------- Overview --------------------------
# This function formats the rows of test info to be written in the
# final excel output file.

# ** input **
# workbook: a "XlsxWriter" workbook object used for the final excel output file.
# worksheet: a "XlsxWriter" worksheet object used for the final sheet output file.
# test_name: string of the test name.
# ** output **
# no output.
def format_test_info(workbook, worksheet, test_name):
    # Create a format to use in the merged range.
    test_info_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'yellow'})

    test_name_format = workbook.add_format({
        'valign': 'vcenter'})

    worksheet.merge_range("A1:Y1", "Test Information", test_info_format)
    worksheet.merge_range("A2:Y2", test_name, test_name_format)

# -------------------------- Overview --------------------------
# This function formats the rows of tables titles to be written in the
# final excel output file.

# ** input **
# workbook: a "XlsxWriter" workbook object used for the final excel output file.
# worksheet: a "XlsxWriter" worksheet object used for the final sheet output file.
# file_iterator: file iterator of files of tests.
# ** output **
# no output.
def format_tables_titles(workbook, worksheet, file_iterator):
    # Create a format to use in the merged range.
    table_title_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'FF8000'})

    starting_index = FILE_INFO_ROWS_COUNT + LINES_BETWEEN_TABLES + 1
    table_title_starting_col = "A"
    table_title_ending_col = "M"
    num_of_tables = len(g_ordered_files[file_iterator])
    index_runner = starting_index
    for i in range(num_of_tables):
        current_table_title_index = index_runner
        table_title_cells_range = table_title_starting_col + str(current_table_title_index) + \
            ":{}".format(table_title_ending_col + str(current_table_title_index))
        worksheet.merge_range(table_title_cells_range, g_tables_titles[file_iterator][i], table_title_format)

        index_runner += g_tables_rows_count[file_iterator][i] + LINES_BETWEEN_TABLES + 1

# -------------------------- Overview --------------------------
# This function formats the rows of images titles to be written in the
# final excel output file.

# ** input **
# workbook: a "XlsxWriter" workbook object used for the final excel output file.
# worksheet: a "XlsxWriter" worksheet object used for the final sheet output file.
# left_image_title_pos: index of row of the fifth image title.
# ** output **
# no output.
def format_images_titles(workbook, worksheet, left_image_title_pos, images_titles, images_count):
    # Create a format to use in the merged range.
    image_title_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '66B2FF'})

    starting_index = FILE_INFO_ROWS_COUNT + LINES_BETWEEN_TABLES + 1
    right_images_title_starting_col = "O"
    right_images_title_ending_col = "Y"
    index_runner = starting_index
    current_image_title_index = index_runner
    for i in range(images_count - 1):
        current_image_title_index = index_runner
        image_title_cells_range = right_images_title_starting_col + str(current_image_title_index) +\
            ":{}".format(right_images_title_ending_col + str(current_image_title_index))
        worksheet.merge_range(image_title_cells_range, images_count[i], image_title_format)

        index_runner += IMAGE_ROWS_COUNT + LINES_BETWEEN_TABLES + 1

    left_images_title_starting_col = "B"
    left_images_title_ending_col = "L"
    for i in range(1):
        image_title_cells_range = left_images_title_starting_col + str(left_image_title_pos) +\
                                  ":{}".format(left_images_title_ending_col + str(left_image_title_pos))
        worksheet.merge_range(image_title_cells_range, images_titles[images_count - 1], image_title_format)

        index_runner += IMAGE_ROWS_COUNT + LINES_BETWEEN_TABLES + 1

# -------------------------- Overview --------------------------
# This function converts a text file to a sheet of tables and images.

# ** input **
# text_file_path: path of the input text file.
# file_iterator: file iterator of files of tests.
# workbook: a "XlsxWriter" workbook object used for the final excel output file.
# delimiter: delimiter used in original csv files.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_FILE_NOT_EXISTS - file does not exist.
def convert_text_file_to_sheet_with_images(text_file_path, file_iterator, workbook, delimiter):
    # arguments validity check
    if type(text_file_path) != str or "" == text_file_path:
        return Status.ERR_INVALID_PARAMETERS

    file_name = get_file_name_without_extension(text_file_path)
    if "" == file_name:
        print("get_file_name_without_extension failure")
        return Status.ERR_INVALID_PARAMETERS

    # -3 for leaving space for index in case of sheet name duplication
    parsed_sheet_name = file_name[0:SHEET_NAME_MAX_LENGTH - 3:1]
    # Create a workbook and add a worksheet.
    # workbook = xlsxwriter.Workbook(OUTPUTS_DIR + file_name + ".xlsx")
    try:
        worksheet = workbook.add_worksheet(parsed_sheet_name)
    except DuplicateWorksheetName:
        global g_sheet_name_duplication_indexer
        sheet_index = str(g_sheet_name_duplication_indexer)
        new_parsed_sheet_name = parsed_sheet_name + "_{}".format(sheet_index)
        worksheet = workbook.add_worksheet(new_parsed_sheet_name)
        g_sheet_name_duplication_indexer += 1

    # Copy text file's content into workbook.
    try:
        with open(text_file_path, "r", encoding='utf-8') as text_file:
            text_content = text_file.readlines()
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    worksheet.set_column('B:M', 15)
    table_header_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': 1})

    label_format = workbook.add_format({
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'})

    metrics_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'})

    row_index = 0
    max_label_width = 0
    for row in text_content:
        is_test_info = False
        is_space = False
        is_title = False
        is_header = False

        # check if row to be written is test info, space, table title, table header or data
        for i in range(len(g_tests_info_indexes[file_iterator])):
            g_variable = g_tests_info_indexes[file_iterator][i]
            # if unnecessarily to continue looking
            if row_index + 1 < g_variable and row_index + 1 != g_variable:
                break
            if row_index + 1 == g_variable:
                is_test_info = True
                break
        # row to be written is either space, table title, table header or data
        if not is_test_info:
            # check if row to be written is space
            for j in range(len(g_spaces_indexes[file_iterator])):
                g_variable = g_spaces_indexes[file_iterator][j]
                # if unnecessarily to continue looking
                if row_index + 1 < g_variable and row_index + 1 != g_variable:
                    break
                if row_index + 1 == g_variable:
                    is_space = True
                    break
            # row to be written is either table title, table header or data
            if not is_space:
                # check if row to be written is a title of a table
                for k in range(len(g_tables_titles_indexes[file_iterator])):
                    g_variable = g_tables_titles_indexes[file_iterator][k]
                    # if unnecessarily to continue looking
                    if row_index + 1 < g_variable and row_index + 1 != g_variable:
                        break
                    if row_index + 1 == g_variable:
                        is_title = True
                        break
                # row to be written is either table header or data
                if not is_title:
                    # check if row to be written is header of a table
                    for h in range(len(g_tables_headers_indexes[file_iterator])):
                        g_variable = g_tables_headers_indexes[file_iterator][h]
                        # if unnecessarily to continue looking
                        if row_index + 1 < g_variable and row_index + 1 != g_variable:
                            break
                        if row_index + 1 == g_variable:
                            is_header = True
                            break

        row_items = row.split(delimiter)
        col_index = 0
        if is_test_info:  # if row is test info
            for item in row_items:
                worksheet.write(row_index, col_index, item)
                col_index += 1
        elif is_space:  # if row is space
            for item in row_items:
                worksheet.write(row_index, col_index, item)
                col_index += 1
        elif is_title:  # if row is title of table
            for item in row_items:
                worksheet.write(row_index, col_index, item)
                col_index += 1
        elif is_header:  # if row is header of table
            for item in row_items:
                worksheet.write(row_index, col_index, item, table_header_format)
                col_index += 1
        else:
            if file_iterator > 0:  # this is a file of single pserver ip report
                for item in row_items:
                    if 0 == col_index:  # if cell is in the "label" column
                        if len(item) > max_label_width:
                            max_label_width = len(item)
                        worksheet.write(row_index, col_index, item, label_format)
                    elif 9 == col_index:  # if cell is in the "error" column (Percentage)
                        worksheet.write(row_index, col_index, item, metrics_format)
                    elif 10 == col_index or 11 == col_index or 12 == col_index:  # if cell has float value
                        worksheet.write(row_index, col_index, item, metrics_format)
                    else:
                        worksheet.write(row_index, col_index, int(float(item)), metrics_format)
                    col_index += 1

            else:  # this is a file of all pservers ips report
                if row_index < g_tables_headers_indexes[file_iterator][1]:  # this is a row of SQL counts table
                    for item in row_items:
                        if 0 == col_index:  # if cell is in the "label" column
                            if len(item) > max_label_width:
                                max_label_width = len(item)
                            worksheet.write(row_index, col_index, item, label_format)
                        else:
                            worksheet.write(row_index, col_index, item, metrics_format)
                        col_index += 1
                else:  # these are the other tables
                    for item in row_items:
                        if 0 == col_index:  # if cell is in the "label" column
                            if len(item) > max_label_width:
                                max_label_width = len(item)
                            worksheet.write(row_index, col_index, item, label_format)
                        elif 9 == col_index:  # if cell is in the "error" column (Percentage)
                            worksheet.write(row_index, col_index, item, metrics_format)
                        elif 10 == col_index or 11 == col_index or 12 == col_index:  # if cell has float value
                            worksheet.write(row_index, col_index, item, metrics_format)
                        else:
                            worksheet.write(row_index, col_index, int(float(item)), metrics_format)
                        col_index += 1

        row_index += 1

    worksheet.set_column('A:A', max_label_width)
    tables_count = len(g_tables_titles_indexes[file_iterator])

    # set titles metrics
    last_row_of_tables = g_tables_titles_indexes[file_iterator][tables_count - 1] + \
        g_tables_rows_count[file_iterator][tables_count - 1]

    # ---------------------------------------------------------------------------------------
    # ----------------------- Format titles of: info, tables & images -----------------------
    # ---------------------------------------------------------------------------------------
    format_test_info(workbook, worksheet, file_name)
    format_tables_titles(workbook, worksheet, file_iterator)
    last_image_title_row_index = last_row_of_tables + LINES_BETWEEN_TABLES + LINES_BETWEEN_TABLES

    images_count = len(g_images_titles[file_iterator])
    if 0 != images_count:
        # ---------------------------------------------------------------------------------------
        # ----------------------- Add images & their titles to excel file -----------------------
        # ---------------------------------------------------------------------------------------

        format_images_titles(workbook, worksheet, last_image_title_row_index,
                             g_images_titles[file_iterator], images_count)

        # set images metrics
        right_images_titles_row_base = FILE_INFO_ROWS_COUNT + LINES_BETWEEN_TABLES + 1
        right_images_row_base = FILE_INFO_ROWS_COUNT + LINES_BETWEEN_TABLES + 2
        last_image_pos = LEFT_IMAGES_COL_BASE + str(last_row_of_tables + LINES_BETWEEN_TABLES +
                                                    LINES_BETWEEN_TABLES + 1)
        last_image_title_pos = LEFT_IMAGES_TITLES_COL_BASE + str(last_row_of_tables + LINES_BETWEEN_TABLES +
                                                                 LINES_BETWEEN_TABLES)

        # insert images & titles to excel file
        images_index = 0
        # images_count = len(g_ordered_images[file_iterator])
        for image in g_ordered_images[file_iterator]:
            image_name = get_file_name_without_extension(image)
            image_title = g_images_titles[file_iterator][images_index]
            image_pos = RIGHT_IMAGES_COL_BASE + str(right_images_row_base)
            image_title_pos = RIGHT_IMAGES_TITLES_COL_BASE + str(right_images_titles_row_base)
            if images_index == images_count - 1:
                worksheet.write(last_image_title_pos, image_title)
                worksheet.insert_image(last_image_pos, image, {'x_scale': IMAGE_X_SCALE, 'y_scale': IMAGE_Y_SCALE})
            else:
                worksheet.write(image_title_pos, image_title)
                worksheet.insert_image(image_pos, image, {'x_scale': IMAGE_X_SCALE, 'y_scale': IMAGE_Y_SCALE})
            right_images_row_base += RIGHT_IMAGES_ROW_OFFSET
            right_images_titles_row_base += RIGHT_IMAGES_ROW_OFFSET
            images_index += 1

    # workbook.close()

    return Status.OK

# -------------------------- Overview --------------------------
# This function converts text files of tests to a final suite excel file.

# ** input **
# suite_path: path of the suite directory.
# output_dir_path: path of the output (xlsx + txt) files directory.
# final_outFile_name: name of the final output suite excel file.
# delimiter: delimiter used in original csv files.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_DIR_NOT_EXISTS - directory does not exist.
# ERR_FILE_NOT_EXISTS - file does not exist.
def convert_combined_text_files_into_big_excel_file(suite_path, output_dir_path, final_outFile_name, delimiter):
    # arguments validity check
    status_result = validate_directory_path(output_dir_path)
    if Status.OK != status_result:
        print("validate_directory_path failure")
        return status_result

    file_iterator = 0
    workbook = xlsxwriter.Workbook(suite_path + final_outFile_name)
    for file_path in g_ordered_text_files:
        status_result = convert_text_file_to_sheet_with_images(file_path, file_iterator, workbook, delimiter)
        if Status.OK != status_result:
            print("convert_text_file_to_sheet_with_images failure")
            return status_result
        file_iterator += 1

    workbook.close()

    return Status.OK

# -------------------------- Overview --------------------------
# This function deletes all excel and text files in a given directory path.

# ** input **
# dir_path: path of the folder.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_DIR_NOT_EXISTS - directory does not exist.
def delete_all_excel_and_text_files(dir_path):
    # arguments validity check
    status_result = validate_directory_path(dir_path)
    if Status.OK != status_result:
        print("validate_directory_path failure")
        return status_result

    files = os.listdir(dir_path)
    for file in files:
        if file.endswith((".txt", ".xlsx")):
            full_file_path = dir_path + file
            os.remove(full_file_path)

    return Status.OK

# -------------------------- Overview --------------------------
# This function runs all functions of the script.

# ** input **
# suite_path: path of the "suite" directory.
# ** output **
# returns one of the following enums:
# OK - file exists.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_DIR_EXISTS - directory already exists.
# ERR_DIR_NOT_EXISTS - directory does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_OS - system error.
def run_script(suite_path):
    validation_result = validate_directory_path(suite_path)
    if Status.OK != validation_result:
        print("validating directory path failure")
        return validation_result

    corrected_suite_path = []
    status_result = correct_directory_path(suite_path, corrected_suite_path)
    if Status.OK != status_result:
        print("correcting directory path failure")
        return status_result
    suite_path = corrected_suite_path[0]

    csv_delimiter = ","
    status_result = create_directory(OUTPUTS_DIR)
    if Status.OK != status_result and Status.ERR_DIR_EXISTS != status_result:
        print("creating directory failure")
        return status_result

    status_result = get_all_pservers_ips(suite_path)
    if Status.OK != status_result:
        print("getting all pserver ips failure")
        return status_result

    status_result = get_all_report_files_paths_arranged(suite_path)
    if Status.OK != status_result:
        print("getting all report files paths arranged failure")
        return status_result

    status_result = get_all_report_images_paths_arranged(suite_path)
    if Status.OK != status_result:
        print("getting all report images paths arranged failure")
        return status_result

    status_result = get_single_report_files_paths_arranged(suite_path)
    if Status.OK != status_result:
        print("getting single report files paths arranged failure")
        return status_result

    status_result = get_single_report_images_paths_arranged(suite_path)
    if Status.OK != status_result:
        print("getting single report images paths arranged failure")
        return status_result

    get_all_report_tables_titles()
    get_single_report_tables_titles()
    get_all_report_images_titles()
    get_single_report_images_titles()

    status_result = filter_line_feed_doubles()
    if Status.OK != status_result:
        print("filtering line feed doubles failure")
        return status_result

    status_result = filter_all_sql_count_table()
    if Status.OK != status_result:
        print("filtering all sql count table failure")
        return status_result

    status_result = filter_metrics_in_perfmon_csv_files()
    if Status.OK != status_result:
        print("filtering metrics in perfMon csv files failure")
        return status_result

    status_result = filter_metrics_in_component_aggregate_report_csv_files()
    if Status.OK != status_result:
        print("filtering metrics in component aggregateReport csv files failure")
        return status_result

    status_result = count_tables_rows_in_csv_files()
    if Status.OK != status_result:
        print("counting tables rows in csv files failure")
        return status_result

    calculate_test_info_indexes()
    calculate_spaces_indexes()
    calculate_tables_titles_indexes()
    calculate_tables_headers_indexes()

    combine_csv_files_into_single_text_file()
    get_text_files_paths_arranged(OUTPUTS_DIR)

    suite_dir_name = []
    status_result = extract_directory_name_from_path(suite_path, suite_dir_name)
    if Status.OK != status_result:
        print("extracting directory name from path failure")
        return status_result

    suite_excel_outFile_name = suite_dir_name[0] + ".xlsx"
    # parent_dir_of_suite = os.path.abspath(os.path.join(suite_path, os.pardir)) + "/"  # get cwd parent directory
    status_result = convert_combined_text_files_into_big_excel_file(suite_path, OUTPUTS_DIR,
                                                                    suite_excel_outFile_name, csv_delimiter)
    if Status.OK != status_result:
        print("converting combined text files into big excel file failure")
        return status_result

    # Delete output directory with its all content
    shutil.rmtree(OUTPUTS_DIR)

    return Status.OK

def main():
    if len(sys.argv) < 2:
        sys.exit("\nUsage:\n"
                 "python3 monitoringReport_excel.py <suite_path>\n"
                 "Where:\n"
                 "<suite_path> - path of suite directory.\n"
                 "e.g:\n"
                 "python3 monitoringReport_excel.py ./Vanilla_suite\n")

    suite_path = sys.argv[1]

    # suite_path = ".\\input_files\\VANILLA_SEKELETON_LogsMetrics_20211014_124857\\"
    # suite_path = ".\\input_files\\VANILLA_SEKELETON_LogsMetrics_20211112_020001\\"

    run_time_result = run_script(suite_path)
    if Status.OK == run_time_result:
        print_status_message(run_time_result)
    else:
        print_status_message(run_time_result)
        print("Terminating...")

if __name__ == "__main__":
    main()
