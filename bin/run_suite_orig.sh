#########################################################################################################################################################
#                                                                                                                                                       #
#   This automation will run suite, each row in the suite is one performance test.									#
#   For each test this automation will run Jmeter, analyzied the results include Pserver Log analysis and send the analyized results by mail..		#
#       Author: Carmel Dekel                                                                                                                            #
#       Data: AUG,2019                                                                                                                                  #
#       Company: Personetice                                                                                                                            #
#                                                                                                                                                       #
#       To be able to run this Automation Jmeter should include the follow plugins:                                                                     #
#       1. Composite Timeline Graph                                                                                                                     #
#       2. Distribution/Percentile Graphs                                                                                                               #
#       3. Dummy Sampler                                                                                                                                #
#       4. JMXMon Sample CollectorJMXMon Sample Collector                                                                                               #
#       5. PerfMon (Servers Performance Monitoring)                                                                                                     #
#       6. jmeter - JDBC Support                                                                                                                        #
#       7. Synthesis Report                                                                                                                             #
#                                                                                                                                                       #
#########################################################################################################################################################

#!/bin/bash
#set -o xtrace

clear

if [ -z "$2" ]; then
   echo "You run this script wrong way !!!"
   echo "You should run this script as follow:"
   echo "./run_suite.sh <projectName> <SuiteName>"
   echo "For example: ./run_suite.sh USB USB_Automation"
   exit 1
fi

source /home/centos/performance/Automation/conf/configfile.cfg
source ${AutomationDir}/bin/functions.sh

projectName=$1
suiteName=$2

#source ${WorkingDirectory}/${projectName}/configuration/env_configfile.cfg

#SuiteFile=${SuiteFolder}/$1.csv
SuiteFile=${WorkingDirectory}/${projectName}/suite/${suiteName}.csv
suiteRunTime="$(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)"
suiteFolderName="${suiteName}_${suiteRunTime}"
testSuiteTracking=${testFlowTracking}/${suiteFolderName}.log
suiteResultsPath=${WorkingDirectory}/${projectName}/results/${suiteFolderName}

echo "The Suite $2 is started at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)"
echo "The Suite $2 is started at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)" >> ${testSuiteTracking}

#######################################################################
#####   Run run_jmx.sh for each row in the suite                #######
#######################################################################

exec < ${SuiteFile} || exit 1
#read header
IFS="=" read -r FiledName EMAIL_RECIPENT
while IFS="," read -r JmxName JmeterThreads ProjectName LoopCount EffectiveDate requestTypeToAnalyzed testRemark Project_Channel configFileName WarmupCycles settingFile remark;
do
	[[ "$JmxName" =~ ^#.*$ ]] && continue
	printf '\n################################################################################################### \n \n'
	printf '\n################################################################################################### \n \n' >> ${testSuiteTracking}
	echo "Call run_jmx.sh with ${suiteFolderName}, ${JmxName}, ${JmeterThreads}, ${ProjectName}, ${LoopCount}, ${EffectiveDate}, ${requestTypeToAnalyzed}, ${testRemark}, ${Project_Channel}, ${configFileName}, ${WarmupCycles}, ${settingFile}, ${remark}"
	echo "Call run_jmx.sh with ${suiteFolderName}, ${JmxName}, ${JmeterThreads}, ${ProjectName}, ${LoopCount}, ${EffectiveDate}, ${requestTypeToAnalyzed}, ${testRemark}, ${Project_Channel}, ${configFileName}, ${WarmupCycles}, ${settingFile}, ${remark} " >> ${testSuiteTracking}
	echo "${JmxName}.jmx start running at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)"
	echo "${JmxName}.jmx start running at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)" >> ${testSuiteTracking}
	printf '\n################################################################################################### \n \n'

        ${AutomationDir}/bin/run_jmx.sh ${suiteFolderName} ${JmxName} ${JmeterThreads} ${ProjectName} ${LoopCount} ${EffectiveDate} ${requestTypeToAnalyzed} ${testRemark} ${Project_Channel} ${configFileName} ${WarmupCycles} ${settingFile} ${remark} &
	wait

#        BACK_PID=$!
#        while kill -0 $BACK_PID ; do
#                echo "run_jmx is still active..."
#                sleep 1m
#        done


	printf '\n################################################################################################### \n \n'
	echo "${JmxName}.jmx is done at:      $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)"
	echo "${JmxName}.jmx is done at:      $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)" >> ${testSuiteTracking}
	printf '\n################################################################################################### \n \n'
	printf '\n################################################################################################### \n \n' >> ${testSuiteTracking}
	echo "The process is going to sleep for ${waitTime} minutes before starting the next test or finish this Suite"
	lastconfigFileName=${configFileName}
	sleep ${waitTime}m
done

cp ${SuiteFile} ${suiteResultsPath}

python3 ${AutomationDir}/tools/aggregateReport_excel.py ${suiteResultsPath}

send_email ${suiteResultsPath}

echo "The Suite $1 is done at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)"
echo "The Suite $1 is done at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)" >> ${testSuiteTracking}

