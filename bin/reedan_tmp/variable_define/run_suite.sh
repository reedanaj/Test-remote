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

#AutomationDir=${WORKSPACE}/Automation
#testFlowTracking=${WORKSPACE}/Automation/testFlowTracking

source ${WORKSPACE}/Automation/conf/configfile.cfg
source ${WORKSPACE}/Automation/bin/functions.sh

if [ -z "$2" ]; then
   worngRunErrMessage
fi


DB_sid_default="orcl"
AutoConfigFileName="Auto_env_configfile"

##################################################################################
#####   get arguments from command line  Or working with configuration file ######
##################################################################################

if [[ $1 == --* ]]; then
        if [[ "$1" =~ ^((-{1,2})([Hh]$|[Hh][Ee][Ll][Pp])|)$ ]]; then
            print_usage; exit 1
        else
            while [[ $# -gt 0 ]]; do
              opt="$1"
              shift;
              current_arg="$1"
              if [[ "$current_arg" =~ ^-{1,2}.* ]]; then
                echo "WARNING: You may have left an argument blank. Double check your command."
              fi
              case "$opt" in
                "--pname"      ) projectName="$1"; shift;;
                "--sname"     ) suiteName="$1"; shift;;
                "--pid"     ) PServerIps="$1"; echo "PServerIps=${PServerIps}" > ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ;shift;;
                "--purl"     ) PServerUrl="$1"; echo "PServerUrl=${PServerUrl}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ;shift;;
                "--pport"   ) PServerPort="$1"; echo "PServerPort=${PServerPort}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--puser"    ) PserverUser="$1"; echo "PserverUser=${PserverUser}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--pver"     ) PServerVersion="$1"; echo "PServerVersion=${PServerVersion}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--pkeyname"    ) KeyName="$1"; echo "KeyName=${KeyName}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--dbip" ) DataBaseIP="$1"; echo "DataBaseIP=${DataBaseIP}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--dbport" ) DataBasePort="$1"; echo "DataBasePort=${DataBasePort}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--dbschema" ) SchemaName="$1"; echo "SchemaName=${SchemaName}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--dbuser" ) UserName="$1"; echo "UserName=${UserName}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--dbpass" ) SchemaPassword="$1"; echo "SchemaPassword=${SchemaPassword}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--dbsid" ) SID_ServiceName="$1"; echo "SID_ServiceName=${SID_ServiceName}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                *                   ) echo "ERROR: Invalid option: \""$opt"\"" >&2
                                      exit 1;;
              esac
            done
        fi
        if [[ "$SID_ServiceName" == "" ]]; then
                SID_ServiceName=$DB_sid_default
                echo "SID_ServiceName=$DB_sid_default" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg
        fi
        if [[ "$projectName" == "" || "$suiteName" == "" || "$PServerIps" == "" || "$PServerUrl" == "" || "$PServerPort" == "" || "$PserverUser" == "" || "$PServerVersion" == "" || "$KeyName" == "" || "$DataBaseIP" == "" || "$DataBasePort" == "" || "$SchemaName" == "" || "$UserName" == "" || "$SchemaPassword" == "" || "$SID_ServiceName" == "" ]]; then
           worngRunErrMessage
        fi
else
        projectName=$1
        suiteName=$2
        rm -f ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg 2>&1
fi
if [ -z "$2" ]; then
   worngRunErrMessage
fi


DB_sid_default="orcl"
AutoConfigFileName="Auto_env_configfile"

##################################################################################
#####   get arguments from command line  Or working with configuration file ######
##################################################################################

if [[ $1 == --* ]]; then
        if [[ "$1" =~ ^((-{1,2})([Hh]$|[Hh][Ee][Ll][Pp])|)$ ]]; then
            print_usage; exit 1
        else
            while [[ $# -gt 0 ]]; do
              opt="$1"
              shift;
              current_arg="$1"
              if [[ "$current_arg" =~ ^-{1,2}.* ]]; then
                echo "WARNING: You may have left an argument blank. Double check your command."
              fi
              case "$opt" in
                "--pname"      ) projectName="$1"; shift;;
                "--sname"     ) suiteName="$1"; shift;;
                "--pid"     ) PServerIps="$1"; echo "PServerIps=${PServerIps}" > ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ;shift;;
                "--purl"     ) PServerUrl="$1"; echo "PServerUrl=${PServerUrl}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ;shift;;
                "--pport"   ) PServerPort="$1"; echo "PServerPort=${PServerPort}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--puser"    ) PserverUser="$1"; echo "PserverUser=${PserverUser}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--pver"     ) PServerVersion="$1"; echo "PServerVersion=${PServerVersion}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--pkeyname"    ) KeyName="$1"; echo "KeyName=${KeyName}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--dbip" ) DataBaseIP="$1"; echo "DataBaseIP=${DataBaseIP}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--dbport" ) DataBasePort="$1"; echo "DataBasePort=${DataBasePort}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--dbschema" ) SchemaName="$1"; echo "SchemaName=${SchemaName}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--dbuser" ) UserName="$1"; echo "UserName=${UserName}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--dbpass" ) SchemaPassword="$1"; echo "SchemaPassword=${SchemaPassword}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                "--dbsid" ) SID_ServiceName="$1"; echo "SID_ServiceName=${SID_ServiceName}" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg ; shift;;
                *                   ) echo "ERROR: Invalid option: \""$opt"\"" >&2
                                      exit 1;;
              esac
            done
        fi
        if [[ "$SID_ServiceName" == "" ]]; then
                SID_ServiceName=$DB_sid_default
                echo "SID_ServiceName=$DB_sid_default" >> ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg
        fi
        if [[ "$projectName" == "" || "$suiteName" == "" || "$PServerIps" == "" || "$PServerUrl" == "" || "$PServerPort" == "" || "$PserverUser" == "" || "$PServerVersion" == "" || "$KeyName" == "" || "$DataBaseIP" == "" || "$DataBasePort" == "" || "$SchemaName" == "" || "$UserName" == "" || "$SchemaPassword" == "" || "$SID_ServiceName" == "" ]]; then
           worngRunErrMessage
        fi
else
        projectName=$1
        suiteName=$2
        rm -f ${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg 2>&1
fi

#######################################################################
#####   parameter settings                                      #######
#######################################################################

#SuiteFile=${SuiteFolder}/$1.csv
SuiteFile=${WORKSPACE}/Projects/${projectName}/suite/${suiteName}.csv
suiteRunTime="$(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)"
suiteFolderName="${suiteName}_${suiteRunTime}"
testSuiteTracking=${WORKSPACE}/Automation/testFlowTracking/${suiteFolderName}.log
suiteResultsPath=${WORKSPACE}/Projects/${projectName}/results/${suiteFolderName}

echo "The Suite $suiteName is started at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)"
echo "The Suite $suiteName is started at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)" >> ${testSuiteTracking}

#######################################################################
#####   Run run_jmx.sh for each row in the suite                #######
#######################################################################

exec < ${SuiteFile} || exit 1
#read header
IFS="=" read -r FiledName EMAIL_RECIPENT
while IFS="," read -r JmxName JmeterThreads ProjectName LoopCount EffectiveDate requestTypeToAnalyzed testRemark Project_Channel configFileName WarmupCycles settingFile remark;
do
        if [ -f "${WorkingDirectory}/${projectName}/configuration/${AutoConfigFileName}.cfg" ]; then
                configFileName=${AutoConfigFileName}

	[[ "$JmxName" =~ ^#.*$ ]] && continue
	printf '\n################################################################################################### \n \n'
	printf '\n################################################################################################### \n \n' >> ${testSuiteTracking}
	echo "Call run_jmx.sh with ${suiteFolderName}, ${JmxName}, ${JmeterThreads}, ${ProjectName}, ${LoopCount}, ${EffectiveDate}, ${requestTypeToAnalyzed}, ${testRemark}, ${Project_Channel}, ${configFileName}, ${WarmupCycles}, ${settingFile}, ${remark}"
	echo "Call run_jmx.sh with ${suiteFolderName}, ${JmxName}, ${JmeterThreads}, ${ProjectName}, ${LoopCount}, ${EffectiveDate}, ${requestTypeToAnalyzed}, ${testRemark}, ${Project_Channel}, ${configFileName}, ${WarmupCycles}, ${settingFile}, ${remark} " >> ${testSuiteTracking}
	echo "${JmxName}.jmx start running at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)"
	echo "${JmxName}.jmx start running at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)" >> ${testSuiteTracking}
	printf '\n################################################################################################### \n \n'

        ${WORKSPACE}/Automation/bin/run_jmx.sh ${suiteFolderName} ${JmxName} ${JmeterThreads} ${ProjectName} ${LoopCount} ${EffectiveDate} ${requestTypeToAnalyzed} ${testRemark} ${Project_Channel} ${configFileName} ${WarmupCycles} ${settingFile} ${remark} &
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

python3 ${WORKSPACE}/Automation/tools/aggregateReport_excel.py ${suiteResultsPath}

send_email ${suiteResultsPath}

echo "The Suite $suiteName is done at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)"
echo "The Suite $suiteName is done at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)" >> ${testSuiteTracking}

