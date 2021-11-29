#########################################################################################################################################################################
#																					#
#   This automation will run one Jmeter JMX script, analyzied the results include Pserver Log analysis and send the analyized results by mail.				#
#	Author: Carmel Dekel																		#
#	Data: iAug,2021																			#
#	Company: Personetice																		#
#																					#
#       To be able to run this Automation Jmeter should include the follow plugins:											#
#       1. Composite Timeline Graph																	#
#       2. Distribution/Percentile Graphs																#
#       3. Dummy Sampler																		#
#       4. JMXMon Sample CollectorJMXMon Sample Collector														#
#	5. PerfMon (Servers Performance Monitoring)															#
#	6. jmeter - JDBC Support																	#
#	7. Synthesis Report																		#
#																					#
#                                                                                                                               		                        #
#     We also should use the follow variables in the JMX File:                                                          	        	                        #
#       User Defined Variables (Test Plan ):                                                                    	                        	                #
#       - ProjectName:		${__P(ProjectName,HNB_WEB)}                                                    	                                        	        #
#       - effectiveTime:	${__P(EffectiveTime,04/26/2018)} 11:00:00                              	                                                        	#
#       - TestTime:		${__time(yyyyMMdd_HHmm)}						                                                                #
#       - Threads:		${__P(Threads,1)}                               	       	                                                                        #
#	- PserverRevision:	${__P(PserverRevision,20180428_Tomcat_2018.3.3)}											#
#       - LoopCount:		${__P(LoopCount,100)}                                                 	                                                        	#
#	Library: (Setting up a JDBC SQL Server Connection with JMeter)													#
#	/home/ec2-user/performance/Jmeter_installation/jtds-1.3.1-dist/jtds-1.3.1.jar											#
#	/home/ec2-user/performance/Jmeter_installation/jtds-1.3.1-dist/sqljdbc_4.1/enu/jre7/sqljdbc41.jar								#
#																					#
#	CSV Data Set Config																		#
#	-Filename:		${__P(ProjectDir,C:\Performance\Jmeter\\${ProjectName})}/data/HNB_Live_Users_Mapping.csv						#
#       JMXMon Samples Collector:                                                                       	                                                	#
#       - ${__P(resultsFolder,C:\Performance\Jmeter\\${ProjectName}\results\\${ProjectName}_${Threads}_Threads_${PserverRevision}_${TestTime})}/JMXMon.csv      	#
#       PerfMon Metrics Collector                                                                               	                                        	#
#       - ${__P(resultsFolder,C:\Performance\Jmeter\\${ProjectName}\results\\${ProjectName}_${Threads}_Threads_${PserverRevision}_${TestTime})}/PerfMon.csv   		#
#       Simple Data Writer - Success                                                                                    	                                	#
#       - ${__P(resultsFolder,C:\Performance\Jmeter\\${ProjectName}\results\\${ProjectName}_${Threads}_Threads_${PserverRevision}_${TestTime})}/jmeterresults.csv	#
#       Simple Data Writer - Error                                                                                              	                        	#
#       - ${__P(resultsFolder,C:\Performance\Jmeter\\${ProjectName}\results\\${ProjectName}_${Threads}_Threads_${PserverRevision}_${TestTime})}/errresults.csv 		#
#                                                                                                                                       	                	#
#																					#
#																					#
#	At the Pserevr you should verify that:																#
#	In the file /etc/environment you have : PERSONETICS_HOME=/home/centos/personetics/p_home/									#
#	If not please add it																		#
#																					#
#       Send Mails                                                                                                                                                      #
#       To be able to send mails from the automation  you should install mutt in the linux machine                                                                      #
#       Insallation command: sudo yum install mutt cyrus-sasl-plain	                                                                                                #
#       You also should add .mutt_certificates and .muttrc files to home directory                                                                                      #
#	You can find this files at: /home/ec2-user/performance/Automation/sendMail                                                                                      #
#																					#
#########################################################################################################################################################################

#!/bin/bash 
#set -o xtrace

clear
echo "script start at: $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "

source /home/centos/performance/Automation/conf/configfile.cfg
source ${AutomationDir}/bin/functions_metrics.sh

#source logAnalysis.sh

if [ -z "$10" ]; then
   echo "You run this script wrong way !!!"
   echo "You should run this script as follow:"
   echo "./run_jmx.sh <Result Folder Name> <jmxFile> <JmeterThreads> <Project> <NumberOfUsers> <EffectiveDate> <requestTypeToAnalyzed> <TestRemark> <ProjectChannel> <configFileName> <WarmupCycles> [ <SettingFile> | <Remark>]"
   echo "For example: ./run_jmx.sh #PERSONETICS_HOME/logs/test USB_JMX 6 USB 1000 06/25/2018 getInsights PerformanceTest USB_LIVE env_confige 100 "
   exit 1
fi

Project=$1		# Bank name.
configFileName=$2	# The name of confige file that the test will run with

Today=$(date +%Y)\\/$(date +%m)\\/$(date +%d)
Yesterday=$(date +%Y\/%m\/%d -d "1 day ago")
YesterdayFix=$(date +%Y\\/%m\%d -d "1 day ago")
YesterdayZipName=$(date +%Y-%m-%d -d "1 day ago")
ProjectDir="${WorkingDirectory}/${Project}"
testFolder="${Project}_LogsMetrics_$(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)"
resultsFolder="${ProjectDir}/results/${testFolder}"
RequestType=getInsights

source ${ProjectDir}/configuration/${configFileName}.cfg
echo "This test is running now with ${configFileName}.cfg configuration file "

#######################################################################
#####   Create results Folder for day of run	                #######
#######################################################################

mkdir -p ${resultsFolder}

#######################################################################
#####   MS-SQL table count                                      #######
#######################################################################

echo "${JmeterPath}/jmeter -n -t ${ProjectDir}/scripts/Vanilla_MsSql_countRows.jmx  -JProjectName=${Project} -JProjectDir=${ProjectDir} -JresultsFolder=${resultsFolder} -JDBServerIp=${DataBaseIP} -JDBport=${DataBasePort} -JSchemaName=${SchemaName} -JUserName=${UserName} -JSchemaPassword=${SchemaPassword} -JSID_ServiceName=${SID_ServiceName} "

#runJmeter
${JmeterPath}/jmeter -n -t ${ProjectDir}/scripts/Vanilla_MsSql_countRows.jmx -JProjectName=${Project} -JProjectDir=${ProjectDir} -JresultsFolder=${resultsFolder} -JDBServerIp=${DataBaseIP} -JDBport=${DataBasePort} -JSchemaName=${SchemaName} -JUserName=${UserName} -JSchemaPassword=${SchemaPassword} -JSID_ServiceName=${SID_ServiceName}
wait

#######################################################################
#####   Create Pserver IP's list in csv file 			#######
#######################################################################

echo "Create Pserver IP's list in csv file start at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
findPserverIps

#######################################################################
##### Create backup Folder on Pserver's and backup zip files 	#######
#######################################################################
echo "AppServerAndOsUser start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
runMultiServer AppServerAndOsUser

echo "findPersoneticsHome start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
PERSONETICS_HOME_V=$(findPersoneticsHome)

echo "PserverIP_1=: ${PserverIP_1}"

echo "backupLogsMetricToResultFolder start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
runMultiServer backupLogsMetricToResultFolder

#######################################################################
#####   clean Logs older then 14 days                           #######
#######################################################################

#runMultiServer deleteOldlogs
#find ${ProjectDir}/results/VANILLA_SEKELETON_LogsMetrics* -type d -ctime +${daysToDeleteLogs} -exec rm -rf {} \; > /dev/null 2>&1

#######################################################################
#####   Remote Analyzied Logs                                   #######
#######################################################################

#scriptToRun=${AutomationDir}/tools/logAnalysis.sh
#runMultiServer runRemoteScript

echo "logAnalysis.py start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "

#run logAnalysis.py on remote Pserver 
pythonScriptToRun=${AutomationDir}/tools/logAnalysis.py
runMultiServer runRemotePythonScript

echo "SqlLogToJmeter.sh start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "

# run Errors, Sqls and Insights statistics from logs
scriptToRun=${AutomationDir}/tools/SqlLogToJmeter.sh
runMultiServer runRemoteScript

#######################################################################
#####	Copy analyzid logs from PServer				#######
#######################################################################
echo "copyRemoteMeticsFiles start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
runMultiServer copyRemoteMeticsFiles

echo "fixMetricsDateForJmeter start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
fixMetricsDateForJmeter

echo "backUpPerfMonDB start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
backUpPerfMonDB

echo "PerfMon_All AggregateReport start at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${resultsFolder}/${testFolder}_PerfMon_tmp.csv --input-jtl ${resultsFolder}/PerfMon_All.csv --plugin-type AggregateReport --include-label-regex true --include-labels '.*CPU|.*Memory' --width 1200 --height 800 --limit-rows 200

echo "PerfMon_All png start at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${resultsFolder}/${testFolder}_PerfMon.png --input-jtl ${resultsFolder}/PerfMon_All.csv --plugin-type PerfMon --auto-scale yes --include-label-regex true --include-labels '.*CPU|.*Memory' --width 1200 --height 800 --limit-rows 200

tail -n+2 ${resultsFolder}/${testFolder}_PerfMon_tmp.csv | sort  > ${resultsFolder}/${testFolder}_PerfMon.csv
rm -f ${resultsFolder}/${testFolder}_PerfMon_tmp.csv

#######################################################################
#####   Local Component Analysis and Create Pivot table		#######
#######################################################################

echo "more than one Pserver to analyzed start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "

if [ "${NumberOfPservers}" -gt "1" ]; then
	grep -h  Date ${resultsFolder}/${testFolder}_*_${RequestType}_Total.csv | head -1 > ${resultsFolder}/${testFolder}_All_${RequestType}_Total.csv
        echo "there is more than one Pserver to analyzed"
        echo "mergeMetricTotalFiles start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
        runMultiServer mergeMetricTotalFiles
        echo "MetricLogToJMeter_All start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
	MetricLogToJMeter_All
        echo "timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,grpThreads,allThreads,Latency,IdleTime" > ${resultsFolder}/${testFolder}_All_SQL_TOTAL_Jmeter.csv
        echo "mergeMetricTotalFiles_Sql start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
	runMultiServer mergeMetricTotalFiles_Sql

        echo "PerfMon Jmeter reporter start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
        echo "${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${resultsFolder}/${testFolder}_All_${RequestType}_Component_AggregateReport.csv --input-jtl ${resultsFolder}/${testFolder}_All_${RequestType}_Total_Jmeter.csv --plugin-type AggregateReport"
        ${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${resultsFolder}/${testFolder}_All_${RequestType}_Component_AggregateReport.csv --input-jtl ${resultsFolder}/${testFolder}_All_${RequestType}_Total_Jmeter.csv --plugin-type AggregateReport

        echo "${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${resultsFolder}/${testFolder}_All_SQL_AggregateReport.csv --input-jtl ${resultsFolder}/${testFolder}_All_SQL_TOTAL_Jmeter.csv --plugin-type AggregateReport"
        ${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${resultsFolder}/${testFolder}_ALL_SQL_AggregateReport.csv --input-jtl ${resultsFolder}/${testFolder}_All_SQL_TOTAL_Jmeter.csv --plugin-type AggregateReport
fi


# Parsing log analysis result to Jmeter format
echo "MetricLogToJMeter start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
runMultiServer MetricLogToJMeter

#######################################################################
#####	Jmeter Reporting					#######
#######################################################################
#   read commands from /home/ec2-user/performance/Automation/JmeterReporterList.csv
#   This file can be configure by JmeterReporterFile in configfile.cfg
echo "createMetricAggregateReport start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
runMultiServer createMetricAggregateReport

echo "jmeterReporterMetric start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
jmeterReporterMetric

#######################################################################
#####   create AggregateReport excel file for all pservers      #######
#######################################################################
echo "createExcelFile #1 start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
createExcelFile

#######################################################################
#####	Send Results in mail					#######
#######################################################################
echo "zipFolder start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
zipFolder ${resultsFolder}

echo "send_email start at  $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "
send_email

#######################################################################
#####   End of run_mon.sh script                                #######
#######################################################################

echo "script ended at: $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S) "

