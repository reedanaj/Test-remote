#########################################################################################################################################################################
#																					#
#   This automation will run one Jmeter JMX script, analyzied the results include Pserver Log analysis and send the analyized results by mail.				#
#	Author: Carmel Dekel																		#
#	Data: Jun,2019																			#
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

source $PWD/../conf/configfile.cfg
source ${AutomationDir}/bin/functions.sh

if [ -z "$10" ]; then
   echo "You run this script wrong way !!!"
   echo "You should run this script as follow:"
   echo "./run_jmx.sh <Result Folder Name> <jmxFile> <JmeterThreads> <Project> <NumberOfUsers> <EffectiveDate> <requestTypeToAnalyzed> <TestRemark> <ProjectChannel> <configFileName> <WarmupCycles> [ <SettingFile> | <Remark>]"
   echo "For example: ./run_jmx.sh #PERSONETICS_HOME/logs/test USB_JMX 6 USB 1000 06/25/2018 getInsights PerformanceTest USB_LIVE env_confige 100 "
   exit 1
fi

suiteRunFolderName=$1
jmxFile=$2		# Jmeter script that will run at that test.
JmeterThreads=$3	# How Many Thread Jmeter will load for this test.
Project=$4		# Bank name.
NumberOfUsers=$5	# How many users each Jmeter Thread will run.
EffectiveDate=$6	# The Effective date to run the test
RequestType=$7		# The Request Type that will be analyzed in the log Analysis process
suiteTestRemark=$8      # text that taken from suite and will add to the test result name
ProjectChannel=$9	# The channel that we will test with   - U s e    O n l y   F o r    W a r m u p   ! ! ! .
configFileName=${10}	# The name of confige file that the test will run with
WarmupCycles=${11}	# How many cycles to warm the pserver.
SettingFile=${12}	# File containe settings and command lines to run on PServer
Remark=${13}

#testFolder="${Project}_${JmeterThreads}_Threads_${PserverRevision}_$(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)"
#ResultsDir="${WorkingDirectory}/${Project}/results/${testFolder}"
Today=$(date +%Y)\\/$(date +%m)\\/$(date +%d)
Tommorow=$(date +%Y)\\/$(date +%m)\\/$(date --date 'next day' +%d) 
DayAfterTomorrow=$(date +%Y)\\/$(date +%m)\\/$(date --date '2 day' +%d)

ProjectDir="${WorkingDirectory}/${Project}"

source ${ProjectDir}/configuration/${configFileName}.cfg
echo "This test is runnint now with ${configFileName}.cfg configuration file "

#Url_Body=${UrlBody}


#######################################################################
#####   Create Pserver IP's list in csv file                    #######
#######################################################################

#createPserverList

#######################################################################
#####   Set OS user and Pserver Ports, check connectivity       #######
#######################################################################

#runMultiServer AppServerAndOsUser

#######################################################################

#pserverVersion

#######################################################################

PserverRevision=${PServerVersion}      # Pserver version (exp. WebSphere_2.10.1.4_Engage_2018.3.2.36.10 )
testFolder="${Project}_${JmeterThreads}_Threads_${PserverRevision}_${suiteTestRemark}_$(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)"


suiteResultsFolder="${ProjectDir}/results/${suiteRunFolderName}"
resultsFolder=${suiteResultsFolder}/${testFolder}
TestDetailsFile=${suiteResultsFolder}/${testFolder}/TestDetails.log
mkdir -p ${resultsFolder}

cp ${ProjectDir}/configuration/${configFileName}.cfg ${suiteResultsFolder}/${testFolder} > /dev/null 2>&1
sudo truncate -s 0 ${AutomationDir}/bin/jmeter.log

echo "resultsFolder = ${suiteResultsFolder}/${testFolder}"
echo "suiteResultsFolder = ${suiteResultsFolder}"

#######################################################################
#####   Create Pserver IP's list in csv file 			#######
#######################################################################

createPserverList

#######################################################################
#####   Set OS user and Pserver Ports, check connectivity	#######
#######################################################################

runMultiServer AppServerAndOsUser 

#######################################################################

pserverVersion

#######################################################################
#####   Run chnage setting file to set and configure PServer    #######
#######################################################################

if [ "${SettingFile}" != "" ]; then
        echo "changing the Pserver setting"
        runSettingFile ${ProjectDir}/configuration/${SettingFile}.cfg
fi

#######################################################################
#####	Warming up and Validate PServer working 		#######
#######################################################################

echo "Start Warming at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)"

#if [ -z "$WarmupCycles" ];then
#        WarmupCycles="0"
#fi


if [ "$WarmupCycles" -gt 0 ];then
        runMultiServer WarmingUpAndValidatePServer
	else  
		echo "########## Skip Warming up and Validatte Pserver  ##########"
fi

#runMultiServer WarmingUpAndValidatePServer

#######################################################################
#####	clean pserver logs					#######
#######################################################################

runMultiServer cleanPserverLogs

#######################################################################
#####	Run Jmeter						#######
#######################################################################

echo "${JmeterPath}/jmeter -n -t ${ProjectDir}/scripts/${jmxFile}.jmx -JThreads=${JmeterThreads} -JProjectName=${Project} -JLoopCount=${NumberOfUsers} -JEffectiveTime=${EffectiveDate} -JProjectDir=${ProjectDir} -JresultsFolder=${resultsFolder} -JServerIp=${PServerUrl} -JPServerPort=${PServerPort} -JDBServerIp=${DataBaseIP} -JDBport=${DataBasePort} -JSchemaName=${SchemaName} -JUserName=${UserName} -JSchemaPassword=${SchemaPassword} -JSID_ServiceName=${SID_ServiceName} -JChannel=${ProjectChannel} -JPServerPort=${PServerPort} "  >> ${TestDetailsFile}

#runJmeter
${JmeterPath}/jmeter -n -t ${ProjectDir}/scripts/${jmxFile}.jmx -JThreads=${JmeterThreads} -JProjectName=${Project} -JLoopCount=${NumberOfUsers} -JEffectiveTime=${EffectiveDate} -JProjectDir=${ProjectDir} -JresultsFolder=${resultsFolder} -JServerIp=${PServerUrl} -JPServerPort=${PServerPort} -JDBServerIp=${DataBaseIP} -JDBport=${DataBasePort} -JSchemaName=${SchemaName} -JUserName=${UserName} -JSchemaPassword=${SchemaPassword} -JSID_ServiceName=${SID_ServiceName} -JChannel=${ProjectChannel} -JPServerPort=${PServerPort}
wait

#######################################################################
######  If request Type = None					#######
#######################################################################

# If [ "${RequestType}" != "None" ]; then

#######################################################################
#####	Remote Analyzied Logs					#######
#######################################################################

runMultiServer backupLogsToResultFolder

# run Errors, Sqls and Insights statistics from logs
scriptToRun=${AutomationDir}/tools/logAnalysis.sh
runMultiServer runRemoteScript 

#run logAnalysis.py on remote Pserver 
pythonScriptToRun=${AutomationDir}/tools/logAnalysis.py
runMultiServer runRemotePythonScript

# run Sqls statistics from logs
scriptToRun=${AutomationDir}/tools/SqlLogToJmeter.sh
runMultiServer runRemoteScript

#Pivot Tables for Totals and Component Analysis

#######################################################################
#####	Copy analyzid logs from PServer				#######
#######################################################################

runMultiServer copyRemoteFiles

#######################################################################
#####   Local Component Analysis and Create Pivot table		#######
#######################################################################

runMultiServer fixDateForJmeter

if [ "${NumberOfPservers}" -gt "1" ]; then
        echo "there is more than one Pserver to analyzed"
	grep -h  Date ${resultsFolder}/${testFolder}_*_${RequestType}_Total.csv | head -1 > ${resultsFolder}/${testFolder}_All_${RequestType}_Total.csv
        runMultiServer mergeTotalFiles
#	ComponentAnalysis ${suiteResultsFolder}/${testFolder}/${testFolder}_${RequestType}_All_Total
	LogToJMeter_All
        ${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${suiteResultsFolder}/${testFolder}/${testFolder}_All_${RequestType}_Component_AggregateReport.csv --input-jtl ${suiteResultsFolder}/${testFolder}/${testFolder}_All_${RequestType}_Total_Jmeter.csv --plugin-type AggregateReport
        echo "${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${suiteResultsFolder}/${testFolder}/${testFolder}_All_${RequestType}_Component_AggregateReport.csv --input-jtl ${suiteResultsFolder}/${testFolder}/${testFolder}_All_${RequestType}_Total_Jmeter.csv --plugin-type AggregateReport"
else
	# Parsing log analysis result to Jmeter format
	runMultiServer LogToJMeter
fi

#runMultiServer ComponentAnalysis
runMultiServer RequestReceivedAnalysis

# Parsing log analysis result to Jmeter format
#runMultiServer LogToJMeter

#######################################################################
#####	Jmeter Reporting					#######
#######################################################################
#   read commands from /home/ec2-user/performance/Automation/JmeterReporterList.csv
#   This file can be configure by JmeterReporterFile in configfile.cfg

runMultiServer createAggregateReport

jmeterReporter

cp ${AutomationDir}/bin/jmeter.log ${suiteResultsFolder}/${testFolder} > /dev/null 2>&1

#######################################################################
##### end of if request Type = None				#######
#######################################################################

#fi

#######################################################################
#####	Send Results in mail					#######
#######################################################################
zipFolder $resultsFolder
#send_email

#######################################################################
#####   End of run_jmx.sh script                                #######
#######################################################################
