
#!/bin/bash 
#set -o xtrace

clear
echo "script start at: $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "

source /home/centos/performance/Automation/conf/configfile.cfg
source ${AutomationDir}/bin/functions_metrics.sh
source /home/centos/performance/Projects/VANILLA_SEKELETON/configuration/env_configfile_OnDemand22PServers.cfg

Project=$1		# Bank name.

Today=$(date +%Y)\\/$(date +%m)\\/$(date +%d)
ProjectDir="${WorkingDirectory}/${Project}"
testFolder="VANILLA_SEKELETON_LogsMetrics_20211122_010001"
resultsFolder="${ProjectDir}/results/${testFolder}"
Yesterday="2021/11/21"
YesterdayFix="2021\/11\/21"
YesterdayZipName="2021-11-21"
RequestType=getInsights

#######################################################################
#####   Create Pserver IP's list in csv file                    #######
#######################################################################

echo "Create Pserver IP's list in csv file start at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#findPserverIps

#######################################################################
##### Create backup Folder on Pserver's and backup zip files    #######
#######################################################################
echo "AppServerAndOsUser start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#runMultiServer AppServerAndOsUser

echo "findPersoneticsHome start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#PERSONETICS_HOME_V=$(findPersoneticsHome)

#echo "PserverIP_1=: ${PserverIP_1}"

echo "backupLogsMetricToResultFolder start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#runMultiServer backupLogsMetricToResultFolder

#######################################################################
#####   clean Logs older then 14 days                           #######
#######################################################################

#runMultiServer deleteOldlogs
#find ${ProjectDir}/results/VANILLA_SEKELETON_LogsMetrics* -type d -ctime +${daysToDeleteLogs} -exec rm -rf {} \; > /dev/null 2>&1

#######################################################################
#####   Remote Analyzied Logs                                   #######
#######################################################################

echo "logAnalysis.py start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "

pythonScriptToRun=${AutomationDir}/tools/logAnalysis.py
#runMultiServer runRemotePythonScript

echo "SqlLogToJmeter.sh start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "

scriptToRun=${AutomationDir}/tools/SqlLogToJmeter.sh
#runMultiServer runRemoteScript

#######################################################################
#####   Copy analyzid logs from PServer                         #######
#######################################################################
echo "copyRemoteMeticsFiles start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#runMultiServer copyRemoteMeticsFiles

echo "fixMetricsDateForJmeter start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#fixMetricsDateForJmeter

echo "backUpPerfMonDB start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#backUpPerfMonDB

echo "PerfMon_All AggregateReport start at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${resultsFolder}/${testFolder}_PerfMon_tmp.csv --input-jtl ${resultsFolder}/PerfMon_All.csv --plugin-type AggregateReport --include-label-regex true --include-labels '.*CPU|.*Memory' --width 1200 --height 800 --limit-rows 200

echo "PerfMon_All png start at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${resultsFolder}/${testFolder}_PerfMon.png --input-jtl ${resultsFolder}/PerfMon_All.csv --plugin-type PerfMon --auto-scale yes --include-label-regex true --include-labels '.*CPU|.*Memory' --width 1200 --height 800 --limit-rows 200

#tail -n+2 ${resultsFolder}/${testFolder}_PerfMon_tmp.csv | sort  > ${resultsFolder}/${testFolder}_PerfMon.csv
#rm -f ${resultsFolder}/${testFolder}_PerfMon_tmp.csv

#######################################################################
#####   Local Component Analysis and Create Pivot table         #######
#######################################################################

echo "more than one Pserver to analyzed start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "

#if [ "${NumberOfPservers}" -gt "1" ]; then
#        grep -h  Date ${resultsFolder}/${testFolder}_*_${RequestType}_Total.csv | head -1 > ${resultsFolder}/${testFolder}_All_${RequestType}_Total.csv
#        echo "there is more than one Pserver to analyzed"
#        echo "mergeMetricTotalFiles start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#        runMultiServer mergeMetricTotalFiles
#        echo "MetricLogToJMeter_All start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#        MetricLogToJMeter_All
#        echo "timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,grpThreads,allThreads,Latency,IdleTime" > ${resultsFolder}/${testFolder}_All_SQL_TOTAL_Jmeter.csv
#        echo "mergeMetricTotalFiles_Sql start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#        runMultiServer mergeMetricTotalFiles_Sql

#        echo "PerfMon Jmeter reporter start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#        echo "${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${resultsFolder}/${testFolder}_All_${RequestType}_Component_AggregateReport.csv --input-jtl ${resultsFolder}/${testFolder}_All_${RequestType}_Total_Jmeter.csv --plugin-type AggregateReport"
#        ${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${resultsFolder}/${testFolder}_All_${RequestType}_Component_AggregateReport.csv --input-jtl ${resultsFolder}/${testFolder}_All_${RequestType}_Total_Jmeter.csv --plugin-type AggregateReport

#        echo "${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${resultsFolder}/${testFolder}_All_SQL_AggregateReport.csv --input-jtl ${resultsFolder}/${testFolder}_All_SQL_TOTAL_Jmeter.csv --plugin-type AggregateReport"
#        ${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${resultsFolder}/${testFolder}_ALL_SQL_AggregateReport.csv --input-jtl ${resultsFolder}/${testFolder}_All_SQL_TOTAL_Jmeter.csv --plugin-type AggregateReport
#fi

# Parsing log analysis result to Jmeter format
echo "MetricLogToJMeter start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#runMultiServer MetricLogToJMeter

#######################################################################
#####   Jmeter Reporting                                        #######
#######################################################################
#   read commands from /home/ec2-user/performance/Automation/JmeterReporterList.csv
#   This file can be configure by JmeterReporterFile in configfile.cfg
echo "createMetricAggregateReport start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#runMultiServer createMetricAggregateReport

echo "jmeterReporterMetric start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#jmeterReporterMetric

#######################################################################
#####   create AggregateReport excel file for all pservers      #######
#######################################################################
echo "createExcelFile start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
createExcelFile

#######################################################################
#####   Send Results in mail                                    #######
#######################################################################
echo "zipFolder start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
#zipFolder ${resultsFolder}

echo "send_email start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
send_email

#######################################################################
#####   End of run_mon.sh script                                #######
#######################################################################

echo "script ended at: $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "

