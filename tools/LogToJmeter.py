import configparser
import csv
import sys
import os

write_fields = ["timeStamp","elapsed","label","responseCode","responseMessage","threadName","dataType","success","failureMessage","bytes","grpThreads","allThreads","Latency","IdleTime"]


def parse(input_filename, output_filename):
    with open(input_filename , "r", encoding='utf-8') as totals_file:
        totals_reader = csv.reader(totals_file, delimiter=',')
        totals_header = next(totals_reader)  # read header
        metric_index = 0
        read_fields = []
        for metric in totals_header:
            if metric_index > 1:  # skip first two columns
                read_fields.append(metric)
            metric_index += 1

    headers = ["TIME", "USER_ID"] + read_fields

#    print("read_fields=:",read_fields)
#    print("write_fields=:",write_fields)

    with open(input_filename, newline='') as csvfile:
        next(csvfile)
        with open(output_filename, 'w', newline='') as output:
            reader = csv.DictReader(csvfile, fieldnames=headers)
            writer = csv.writer(output, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(write_fields)

            for row in reader:
                for field in read_fields:
                    output_row = [row["TIME"], row[field], field.replace("TOTAL","TOTAL Duration"), 200, 'OK', 'GetInsight 2-1', 'text', 'true', '',
                                  '458674', '1', '1', '1266', '0']
                    writer.writerow(output_row)

def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: python3 LogToJmeter.py <results dir> <Request Type>\ne.g: python3 logAnalysis.py USB_Push_3.15.2_Engage_2019.1.8.22_5_20200816_1047_PS6 pushNotificationLive\nthis script support:\n1.getInsights\n2.pushNotificationLive\n3.moneyTransfer\n4.getInsightDetails\n5.sendEvents\n6.updateInsightRating\n7.getInboxInsights\n8.getNumberOfInsights\n9.generateInsights\n10.MicroSavingsAndDataAssets\n11.ProfilesAndPYFEligibilityFUT\n12.PYFMoneyTransfer\n13.DataAssets\n14.NO_TYPE_PROVIDED")
    # This parameter will reciev  the results folder name
    fullFilePath = sys.argv[1]
    file_path = os.path.split(os.path.split( fullFilePath )[1])[1]
    # This parameter will reciev the request type that we want to analyzed
    reqtype = sys.argv[2]

    if len(sys.argv) < 4:
        totals_path = fullFilePath + '/' + file_path + '_' + reqtype + '_Total.csv'
        output_path = fullFilePath + '/' + file_path + '_' + reqtype + '_Total_Jmeter.csv'
    else:
        pServerIp = sys.argv[3]
        totals_path = fullFilePath + '/' + file_path + '_' + pServerIp + '_' + reqtype + '_Total.csv'
        output_path = fullFilePath + '/' + file_path + '_' + pServerIp + '_' + reqtype + '_Total_Jmeter.csv'

    parse(totals_path, output_path)

if __name__ == '__main__':
	main()
