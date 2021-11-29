########################################################################################################################
#       Author: Reedan Ajamia + Carmel Dekel.                                                                          #
#       Date: November, 2021.                                                                                          #
#       Company: Personetics.                                                                                          #
#                                                                                                                      #
#   This Python script analyzes zipped logs of pserver in a given logs directory, with specified API request.          #
########################################################################################################################


#!/usr/bin/env python3

import sys          # sys
import enum         # Enum
import os.path      # basename
# import subprocess   # Popen
import csv          # writer
import re           # search


# Global variables
g_header = []

# Request types metrics
g_metrics = {
"moneyTransfer": ["PARTY_ID", "DATA_ASSETS_SAVE", "DI", "DI.AWAIT", "DROOLS.ACCESS_ACQUIRED", "DROOLS.EXECUTION", "FLOW.MoneyTransfer", "REALTIME_PREDICTION_ANALYSIS_MODEL", "TOTAL", "DI.DIParallelJoinWork.run"],
"getInsights": ["USER_ID", "GET HISTORY", "LOGIC", "PERSIST", "RESPONSE", "TOTAL", "NUM_OF_TRANSACTIONS", "DI", "DI.AWAIT", "GET_SETTINGS_AND_ASSETS", "NUM_OF_INSIGHTS_RESPONSE", "NUM_OF_INSIGHTS_GENERATED", "NUM_OF_ACCOUNTS", "SECURITIES.DB_RETRIEVAL.TIME", "SECURITIES.EVALUATION.TIME"],
"pushNotificationLive": ["USER_ID", "GET HISTORY", "LOGIC", "PERSIST", "RESPONSE", "TOTAL", "NUM_OF_TRANSACTIONS", "DI", "DI.AWAIT", "NUM_OF_INSIGHTS_RESPONSE", "NUM_OF_INSIGHTS_GENERATED"],
"NO_TYPE_PROVIDED": ["USER_ID", "DATA_ASSETS_SAVE", "DI", "DI.AWAIT", "DROOLS.ACCESS_ACQUIRED", "DROOLS.EXECUTION", "FLOW.CrossAccountActivity", "FLOW.FreeToUse", "FLOW.GetMicroSavingsEligibility", "FLOW.UserProfile", "TOTAL"],
"getInsightDetails": ["PARTY_ID", "MERGE_EXPRESSIONS_TO_TEASER", "REPORTS_SAVE", "RESPONSE", "TOTAL"],
"sendEvents": ["PARTY_ID", "REPORTS_SAVE", "TOTAL"],
"updateInsightRating": ["PARTY_ID", "REPORTS_SAVE", "TOTAL"],
"getInboxInsights": ["PARTY_ID", "MERGE_EXPRESSIONS_TO_TEASER", "REPORTS_SAVE", "RESPONSE", "TOTAL"],
"getNumberOfInsights": ["PARTY_ID", "GET HISTORY", "PERSIST", "POPULATE SEGMENTS HISTORY", "REPORTS_SAVE", "RESPONSE", "TOTAL", "NUM_OF_INSIGHTS_RESPONSE"],
"generateInsights": ["PARTY_ID", "GET HISTORY", "LOGIC", "PERSIST", "RESPONSE", "TOTAL", "NUM_OF_TRANSACTIONS", "DI", "DI.AWAIT", "DI.FETCH.GET_DATA", "DI.FETCH.PREPARE", "DI.FETCH.PROCESS", "NUM_OF_INSIGHTS_RESPONSE", "NUM_OF_INSIGHTS_GENERATED", "NUM_OF_ACCOUNTS"],
"MicroSavingsAndDataAssets": ["PARTY_ID", "DATA_ASSETS_SAVE", "DI", "DI.AWAIT", "DROOLS.ACCESS_ACQUIRED", "DROOLS.EXECUTION", "FLOW.CrossAccountActivity", "FLOW.FreeToUse", "FLOW.GetMicroSavingsEligibility", "FLOW.PYFEligibility", "FLOW.UserProfile", "PROGRAMS_ELIGIBILITY", "PROGRAMS_ELIGIBILITY.PYF", "TOTAL", "DI.DIParallelJoinWork.run"],
"ProfilesAndPYFEligibilityFUT": ["PARTY_ID", "DATA_ASSETS_SAVE", "DI", "DI.AWAIT", "DROOLS.ACCESS_ACQUIRED", "DROOLS.EXECUTION", "FLOW.FreeToUse", "FLOW.PYFEligibility", "FLOW.UserProfile", "PROGRAMS_ELIGIBILITY", "PROGRAMS_ELIGIBILITY.PYF", "TOTAL", "DI.DIParallelJoinWork.run"],
"setMicrosavingsSettings": ["PARTY_ID", "REPORTS_SAVE", "TOTAL"],
"setProgramSettings": ["PARTY_ID", "REPORTS_SAVE", "TOTAL"],
"PYFMoneyTransfer": ["PARTY_ID", "DATA_ASSETS_SAVE", "DI", "DI.AWAIT", "DROOLS.ACCESS_ACQUIRED", "DROOLS.EXECUTION", "FLOW.PYFMoneyTransferDecision", "FLOW.PYFMoneyTransferExecutor", "PROGRAM_TRANSFER_DECISION_MAKER", "PROGRAM_TRANSFER_DECISION_MAKER.PYF", "PROGRAM_TRANSFER_EXECUTOR", "PROGRAM_TRANSFER_EXECUTOR.PYF", "REALTIME_PREDICTION_ANALYSIS_MODEL", "TOTAL", "DI.DIParallelJoinWork.run"],
"DataAssets": ["PARTY_ID", "DATA_ASSETS_SAVE", "DI", "DI.AWAIT", "DI.FETCH.GET_DATA", "DI.FETCH.PREPARE", "DI.FETCH.PROCESS", "DROOLS.ACCESS_ACQUIRED", "DROOLS.EXECUTION", "FLOW.CrossAccountActivity", "FLOW.FreeToUse", "FLOW.UserProfile", "TOTAL"],
"getUserTransactions": ["USER_ID","DI","DI.AWAIT","TOTAL","PIPE.dataEnrichmentFull","PIPE.enrichmentRT","PIPE.deviceAndCategorization","PIPE.selectionAndFinalPopulation","PIPE.subscriptionPipe","PIPE.businessModels","DATA_ASSETS_SAVE","NUM_OF_ACCOUNTS"],
"executeMLRecurring": ["USER_ID", "RECURRING_ML_SERVICE.SEGMENTATION", "TOTAL", "RECURRING_ML_SERVICE.FORECASTING", "RECURRING_ML_SERVICE.RESPONSE_BUILDER", "RECURRING_ML_SERVICE.PATTERN_FILTER_POLICY", "RECURRING_ML_SERVICE.BEST_SELECTION", "RECURRING_ML_SERVICE.EXECUTE_REQUEST", "RECURRING_ML_SERVICE.PREPROCESSING", "REPORTS_SAVE", "RECURRING_ML_SERVICE.GROUPING", "RECURRING_ML_SERVICE.PRIORITIZATION", "RECURRING_ML_SERVICE.BUSINESS_FILTER_POLICY", "RECURRING_ML_SERVICE.CLASSIFY", "RECURRING_ML_SERVICE.EXECUTE_SINGLE_ACCOUNT_MODEL_STEPS"]
}

# Log files names
g_logs_names = {
"moneyTransfer": ["pserver"],
"getInsights": ["pserver"],
"pushNotificationLive": ["pserver"],
"NO_TYPE_PROVIDED": ["pserver"],
"getInsightDetails": ["pserver"],
"sendEvents": ["pserver"],
"updateInsightRating": ["pserver"],
"getInboxInsights": ["pserver"],
"getNumberOfInsights": ["pserver"],
"generateInsights": ["pserver"],
"MicroSavingsAndDataAssets": ["pserver"],
"ProfilesAndPYFEligibilityFUT": ["pserver"],
"setMicrosavingsSettings": ["pserver"],
"setProgramSettings": ["pserver"],
"PYFMoneyTransfer": ["pserver"],
"DataAssets": ["pserver"],
"getUserTransactions": ["user"],
"executeMLRecurring": ["srv-mle"]
}

# enumerations
class Status(enum.Enum):
    OK = 0
    ERR_FILE_NOT_EXISTS = 1
    ERR_DIR_EXISTS = 2
    ERR_DIR_NOT_EXISTS = 3
    ERR_INVALID_PARAMETERS = 4
    ERR_KEY_NOT_FOUND = 5

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
# This function initializes a global variable represents the final header
# of a given API request with basic metrics to be analyzed.

# ** input **
# request_type: request type to be analyzed.
# ** output **
# returns one of the following enums:
# OK - success.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_KEY_NOT_FOUND - key is not of found in metrics dictionary.
def initialize_header_by_request(request_type):
    # arguments validity check
    if type(request_type) != str or "" == request_type:
        return Status.ERR_INVALID_PARAMETERS

    try:
        basic_metrics = g_metrics[request_type]
    except KeyError:
        return Status.ERR_KEY_NOT_FOUND

    global g_header
    for metric in basic_metrics:
        g_header.append(metric)

    return Status.OK

# -------------------------- Overview --------------------------
# This function parses a single "totals" line from the pserver logs
# to a parsed totals line.
#
# For example:
# Date,USER_ID,GET HISTORY,LOGIC,PERSIST,RESPONSE,TOTAL .....

# ** input **
# line: a single "totals" line from the pserver logs.
# ** output **
# returns a parsed "totals" line.
def parse_line(line):
    # Remove file prefix if exists
    line = line[line.find(":") + 1:] if line.startswith("pserver") else line
    line_date = line[0:23].replace("-", "/")

    metrics_str = re.search('totals : -(.*)', line).group(1)
    if metrics_str.endswith(', '):
        metrics_str = metrics_str[:-2]
    elif metrics_str.endswith(',') or metrics_str.endswith(' '):
        metrics_str = metrics_str[:-1]
    totals_metrics_list = metrics_str.split(', ')

    global g_header
    # Extract enrichment metrics if from totals line
    enrichments = []
    for metric in totals_metrics_list:
        enrichment_search = re.search('(enrichment\\.([a-zA-Z]+)\\.([a-zA-Z]+))', metric)
        if enrichment_search:
            enrichments.append(enrichment_search.group(1))

    # Update header with new enrichment metrics
    for enrichment in enrichments:
        is_found = False
        for header_item in g_header:
            if enrichment == header_item:
                is_found = True
                break

        if not is_found:
            g_header.append(enrichment)

    # Build a dictionary out of totals line
    metrics_dict = {}
    for metric in g_header:
        totals_search = re.search(' ' + metric + ': ([0-9]+)', metrics_str)
        if totals_search:
            metrics_dict[metric] = totals_search.group(1)

    return [line_date] + [metrics_dict.get(metric, '0') for metric in g_header]

# -------------------------- Overview --------------------------
# This function analyzes a specific API request type in a given pserver logs
# directory containing zip files.

# ** input **
# logs_path: path of the "logs" directory.
# request_type: request type to be analyzed.
# deli: delimiter of the csv files.
# ** output **
# returns one of the following enums:
# OK - file exists.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_DIR_NOT_EXISTS - directory does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
def analyze_logs(logs_path, request_type, deli):
    # arguments validity check
    if type(request_type) != str or "" == request_type:
        return Status.ERR_INVALID_PARAMETERS
    if type(deli) != str or "" == deli:
        return Status.ERR_INVALID_PARAMETERS
    validation_result = validate_directory_path(logs_path)
    if Status.OK != validation_result:
        print("validate_directory_path failure")
        return validation_result

    # Extract logs directory name out of logs path
    tmp_path = logs_path[0:len(logs_path) - 1:1]
    logs_dir_name = os.path.basename(tmp_path)

    logs_file_name = g_logs_names[request_type][0]
    request_totals_name = 'request_totals.tmp'
    cmd = 'zgrep'
    cmd_args = '-h "totals : - STATUS: 200" ' + logs_path + logs_file_name + '.*'
    first_pipe = ' | egrep "BATCH: ' + request_type + '|REQUEST_TYPE: ' + request_type + '"'
    second_pipe = ' | sed s/\ -\ totals\ -/\ -\ totals\ :\ -/g'
    redirection = ' > ' + logs_path + request_totals_name
    full_cmd_args = cmd_args + first_pipe + second_pipe + redirection
    os.system(cmd + ' ' + full_cmd_args)
    # cmd_temp_output = subprocess.Popen([cmd, full_cmd_args], stdout=subprocess.PIPE)
    # cmd_output = str(cmd_temp_output.communicate())

    request_totals_path = logs_path + request_totals_name
    try:
        with open(request_totals_path, "r", encoding='utf-8') as request_totals_file:
            content = request_totals_file.readlines()
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    cmd = 'rm'
    cmd_args = '-f ' + request_totals_path
    os.system(cmd + ' ' + cmd_args)
    # cmd_temp_output = subprocess.Popen([cmd, cmd_args], stdout=subprocess.PIPE)
    # cmd_output = str(cmd_temp_output.communicate())

    totals_name = logs_dir_name + '_' + request_type + '_Total.csv'
    totals_path = logs_path + totals_name
    try:
        with open(totals_path, "w", encoding='utf-8') as totals_file:
            totals_writer = csv.writer(totals_file, delimiter=deli, lineterminator='\n')

            # Write totals
            for line in content:
                totals_writer.writerow(parse_line(line))
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    try:
        with open(totals_path, "r", encoding='utf-8') as totals_file:
            content = totals_file.readlines()
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    try:
        with open(totals_path, "w", encoding='utf-8') as totals_file:
            totals_writer = csv.writer(totals_file, delimiter=deli, lineterminator='\n')

            # Write header
            final_header = ['Date']
            for metric in g_header:
                final_header.append(metric)
            totals_writer.writerow(final_header)

            # Rewrite totals
            max_totals_len = len(g_header) + 1  # +1 for the date column
            for line in content:
                line_items = line.strip('\n').split(',')
                totals_length = len(line_items)
                padding_times = max_totals_len - totals_length

                # pad totals lines with 0 for missing metrics if needed
                if 0 != padding_times:
                    for padding_index in range(padding_times):
                        line_items.append('0')

                totals_writer.writerow(line_items)
    except FileNotFoundError:
        return Status.ERR_FILE_NOT_EXISTS

    return Status.OK

# -------------------------- Overview --------------------------
# This function runs all functions of the script.

# ** input **
# logs_dir_name: name of the "logs" directory.
# request_type: request type to be analyzed.
# ** output **
# returns one of the following enums:
# OK - file exists.
# ERR_FILE_NOT_EXISTS - file does not exist.
# ERR_DIR_NOT_EXISTS - directory does not exist.
# ERR_INVALID_PARAMETERS - one of the inputs is invalid.
# ERR_KEY_NOT_FOUND - key is not of found in metrics dictionary.
def run_script(logs_dir_name, request_type):
    # arguments validity check
    if type(logs_dir_name) != str or "" == logs_dir_name:
        return Status.ERR_INVALID_PARAMETERS
    if type(request_type) != str or "" == request_type:
        return Status.ERR_INVALID_PARAMETERS

    phome_path = os.environ.get("PERSONETICS_HOME")
    logs_path = phome_path + '/logs/' + logs_dir_name + '/'

    validation_result = validate_directory_path(logs_path)
    if Status.OK != validation_result:
        print("validating directory path failure")
        return validation_result

    csv_delimiter = ","
    status_result = initialize_header_by_request(request_type)
    if Status.OK != status_result:
        print("initializing header by request failure")
        return status_result

    status_result = analyze_logs(logs_path, request_type, csv_delimiter)
    if Status.OK != status_result:
        print("analyzing logs failure")
        return status_result

    return Status.OK

def main():
    if len(sys.argv) < 3:
        sys.exit("\nUsage:\n"
                 "python3 logAnalysis.py <logs_dir_name> <request_type>\n"
                 "Where:\n"
                 "<logs_dir_name> - name of logs directory.\n"
                 "<request_type> - request type to be analyzed.\n"
                 "e.g:\n"
                 "python3 logAnalysis.py VANILLA_SEKELETON_1_Threads_20211003_104704_10.0.20.193 getInsights\n")

    logs_dir_name = sys.argv[1]
    request_type = sys.argv[2]
    
    run_time_result = run_script(logs_dir_name, request_type)
    if Status.OK == run_time_result:
        print_status_message(run_time_result)
    else:
        print_status_message(run_time_result)
        print("Terminating...")

if __name__ == "__main__":
    main()
