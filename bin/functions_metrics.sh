#!/bin/bash


 #######################################################################
 #####   Run linux command on remote server                      #######
 #######################################################################

function runRemoteLinuxCommand()
        {
        ssh -o StrictHostKeyChecking=no -i ${PrivateKey}/${KeyName}.pem $1@${ServerIP} "$2"
        }

 #######################################################################
 #####   Run linux Scripts on remote server with args            #######
 #######################################################################

function runMultiServer()
{
functionName=$1
pserverNum=0
IFS="," paths=($PServerIps)
for (( pserverNum=0; pserverNum<${#paths[@]}; pserverNum++ ))
do
   eval ServerIP="${paths[$pserverNum]}"
#   ${functionName}&
   ${functionName}
done
#wait
}

 #######################################################################
 #####   Run linux Scripts on remote server with args            #######
 #######################################################################

function runRemoteScript()
        {
        local args script
        script=${scriptToRun}

        # generate eval-safe quoted version of current argument list
        printf -v args '%q_%q ' "${testFolder}" "${ServerIP}"

        # pass that through on the command line to bash -s
        # note that $args is parsed remotely by /bin/sh, not by bash!
        ssh -o StrictHostKeyChecking=no -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP} "bash -s -- $args" < "$script"
        }

 
function runRemotePythonScript()
{
	RequestType=getInsights
        pythonScript=${pythonScriptToRun}
        ssh -o StrictHostKeyChecking=no -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP} python3 - ${testFolder}_${ServerIP} ${RequestType} < ${pythonScript}
}

#######################################################################
#####   Chose App Server Type and OS user                       #######
#######################################################################

function AppServerAndOsUser()
{
#serverPort=${PServerPort}
pserverUser=${PserverUser}

runRemoteLinuxCommand ${pserverUser} "cd"  > /dev/null 2>&1
remoteUserRC=$?

if [ "${remoteUserRC}" = "0" ]; then
        echo "User ${pserverUser} successfully conected to Pserver : ${ServerIP}"
else
        echo "User ${pserverUser} can't connect to Pserver : ${ServerIP}"
        exit 1
fi
}

function findPersoneticsHome()
{
ssh -o StrictHostKeyChecking=no -i ${PrivateKey}/${KeyName}.pem ${PserverUser}@${PserverIP_1} "bash --login -c 'env'" | grep PERSONETICS_HOME | awk -F"=" '{print $2}' 2>&1
#echo "PERSONETICS_HOME: = ${PERSONETICS_HOME_V}"
}

 #######################################################################
 #####   Build Pserver IP's list in csv file                     #######
 #######################################################################

function findPserverIps()
{
PserverIpsNum=0
IFS=, paths=($PServerIps)
for (( PserverIpsNum=0; PserverIpsNum<${#paths[@]}; PserverIpsNum++ ))
do
   eval PserverIP_$PserverIpsNum="${paths[$PserverIpsNum]}"
done

NumberOfPservers=$PserverIpsNum

PserverIP_1=${paths[1]}

}


 #######################################################################
 #####   Backup logs on Pserver to result folder                 #######
 #######################################################################

function backupLogsMetricToResultFolder()
{
        backupFolder=${testFolder}_${ServerIP}
        runRemoteLinuxCommand ${pserverUser} 'mkdir -p '${PERSONETICS_HOME_V}'/logs/'${backupFolder}
#	echo "YesterdayZipName = ${YesterdayZipName}"
        runRemoteLinuxCommand ${pserverUser} 'mv '${PERSONETICS_HOME_V}'/logs/pserver.'${YesterdayZipName}'.*.zip '${PERSONETICS_HOME_V}'/logs/'${backupFolder} > /dev/null 2>&1
	runRemoteLinuxCommand ${pserverUser} 'mv '${PERSONETICS_HOME_V}'/logs/pserverErrors.'${YesterdayZipName}'.*.zip '${PERSONETICS_HOME_V}'/logs/'${backupFolder} > /dev/null 2>&1
}


function backUpPerfMonDB()
{
	echo "timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,sentBytes,grpThreads,allThreads,URL,Latency,IdleTime,Connect" > ${resultsFolder}/PerfMon_All.csv
#	echo "timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,grpThreads,allThreads,Latency,IdleTime,Connect" > ${resultsFolder}/PerfMon_All.csv
	find ${ProjectDir}/results -name "PerfMon.csv" | xargs grep -h "${Yesterday}" >> ${resultsFolder}/PerfMon_All.csv
#	echo "find ${ProjectDir}/results -name "PerfMon.csv" | xargs grep -h "${Yesterday}" >> ${resultsFolder}/PerfMon_All.csv"
}

 #######################################################################
 #####   Analyzed Logs                                           #######
 #######################################################################

function copyRemoteMeticsFiles()
{
        scp -r -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP}:${PERSONETICS_HOME_V}/logs/${testFolder}_${ServerIP}/${testFolder}*.csv ${resultsFolder}
}

function fixMetricsDateForJmeter()
{
#set -o xtrace
        sed -i -e s/${Today}T/${Today}\ /g ${resultsFolder}/${testFolder}_*_Total.csv
        sed -i -e s/${YesterdayFix}T/${YesterdayFix}\ /g ${resultsFolder}/${testFolder}_*_Total.csv
#set +o xtrace
}

function mergeMetricTotalFiles()
{
        tail -n +2 ${resultsFolder}/${testFolder}_${ServerIP}_${RequestType}_Total.csv >> ${resultsFolder}/${testFolder}_All_${RequestType}_Total.csv
}

function mergeMetricTotalFiles_Sql()
{
        tail -n +2 ${resultsFolder}/${testFolder}_${ServerIP}_SQL_TOTAL_Jmeter.csv >> ${resultsFolder}/${testFolder}_All_SQL_TOTAL_Jmeter.csv
}

function MetricLogToJMeter()
{
        python3 ${AutomationDir}/tools/LogToJmeter.py ${resultsFolder} ${RequestType} ${ServerIP}
}

function MetricLogToJMeter_All()
{
        python3 ${AutomationDir}/tools/LogToJmeter.py ${resultsFolder} ${RequestType} All
}

function createExcelFile()
{
	python3 ${AutomationDir}/tools/monitoringReport_excel.py ${resultsFolder}
}



 #######################################################################
 #####   Create Jmeter AggregateReport form csv results file     #######
 #######################################################################

function createMetricAggregateReport()
{

FileToAggregate=${testFolder}_${ServerIP}_${RequestType}_Total_Jmeter.csv
${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${resultsFolder}/${testFolder}_${ServerIP}_${RequestType}_Component_AggregateReport.csv --input-jtl ${resultsFolder}/${FileToAggregate} --plugin-type AggregateReport

${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${resultsFolder}/${testFolder}_${ServerIP}_${RequestType}_Total_ResponseTimesOverTime.png --input-jtl ${resultsFolder}/${FileToAggregate} --plugin-type ResponseTimesOverTime --auto-scale no --include-label-regex true --include-labels .*Duration.* --width 1200 --height 800 --limit-rows 200

${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${resultsFolder}/${testFolder}_${ServerIP}_${RequestType}_Total_TransactionsPerSecond.png --input-jtl ${resultsFolder}/${FileToAggregate} --plugin-type TransactionsPerSecond --auto-scale no --include-label-regex true --include-labels .*Duration.* --width 1200 --height 800 --limit-rows 200

${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${resultsFolder}/${testFolder}_${ServerIP}_${RequestType}_Total_ResponseTimesDistribution.png --input-jtl ${resultsFolder}/${FileToAggregate} --plugin-type ResponseTimesDistribution --auto-scale no --include-label-regex true --include-labels .*Duration.* --width 1200 --height 800 --limit-rows 200

SqlFileToAggregate=${testFolder}_${ServerIP}_SQL_TOTAL_Jmeter.csv
${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${resultsFolder}/${testFolder}_${ServerIP}_Sql_AggregateReport.csv --input-jtl ${resultsFolder}/${SqlFileToAggregate} --plugin-type AggregateReport

}

 #######################################################################
 #####   Create Jmeter Graphs form csv results file              #######
 ####################################################################################################################
 #                                                                                                              #####
 # To use this this option  jpgc-synthesis should be installed                                                  #####
 # To verify if installed: ./PluginsManagerCMD.sh status                                                        #####
 # If It not installed, from Jmeter installation folder run: bin/PluginsManagerCMD.sh install jpgc-synthesis    #####
 #                                                                                                              #####
 ####################################################################################################################

function jmeterReporterMetric()
{

exec < ${JmeterReporterFile} || exit 1
read header
while IFS="," read -r ReporterType graphType FileToAnalyzied ReportName extraCommand1 extraCommand2 extraCommand3 extraCommand4 extraCommand5 extraCommand6
do

       ${JmeterPath}/JMeterPluginsCMD.sh --generate-${ReporterType} ${resultsFolder}/${testFolder}_${ReportName}.${ReporterType} --input-jtl ${resultsFolder}/${FileToAnalyzied} --plugin-type ${graphType} ${extraCommand1} ${extraCommand2} ${extraCommand3} ${extraCommand4} ${extraCommand5} ${extraCommand6} --width 1200 --height 800 --limit-rows 200 > /dev/null 2>&1

done

}

#######################################################################
#####   clean Logs older then 14 days                           #######
#######################################################################

function deleteOldlogs()
{
	runRemoteLinuxCommand ${pserverUser} 'find ' ${PERSONETICS_HOME_V} ' VANILLA_SEKELETON_LogsMetrics* -type d -ctime +'${${daysToDeleteLogs}} ' -exec rm -rf {} \;' > /dev/null 2>&1
	runRemoteLinuxCommand ${pserverUser} 'find ' ${PERSONETICS_HOME_V} '/logs/*.zip -mtime +'${${daysToDeleteLogs}} ' -exec rm -rf {} \;' > /dev/null 2>&1
}

#######################################################################
#####   zip Folder                                              #######
#######################################################################
function zipFolder()
{
folderPath=$1
folderToZip="$(basename $folderPath)"
zip -x *_Jmeter.csv -rj $folderPath/$folderToZip.zip $folderPath/* > /dev/null 2>&1

cd $folderPath
find . -name '*.csv'  ! -name '*_PerfMon.csv' -type f -exec rm -f {} +
#rm -f $folderPath/*.csv
rm -f $folderPath/*.png
}

 #######################################################################
 #####   Send mail                                               #######
 #######################################################################
function on_error_handler(){
        if [ $? -ne 0 ]; then
                ERROR=1
        else
                ERROR=0
        fi
}

function send_email()
{
	EMAIL_RECIPENT="carmel.dekel@personetics.com, ofer.fort@personetics.com, benny.treiger@personetics.com, yaniv.itzhaki@personetics.com, reedan.ajamia@personetics.com"
#       EMAIL_RECIPENT=carmel.dekel@personetics.com 


        ####    Create zip files list to send in Mail   ####
#        zipFilesList="${resultsFolder}/${testFolder}.zip"
#	AggregateReportFileList=""
        ExcelAggregateReportFileName="${resultsFolder}/${testFolder}.xlsx"
        PerfMonReportFile="${resultsFolder}/${testFolder}_PerfMon.csv"
#	Sql_AggregateReportFile="${resultsFolder}/${testFolder}_ALL_SQL_AggregateReport.csv"
#	SqlCountReportFile="${resultsFolder}/SqlCount.csv"
#        AggregateReportFileList="${resultsFolder}/${testFolder}_All_getInsights_Component_AggregateReport.csv"
#        for AggregateReportFileName in ${resultsFolder}/${testFolder}_*_getInsights_Component_AggregateReport.csv; do
#                AggregateReportFileList+="-a ${AggregateReportFileName} " 
#        done

echo "######################################################################################################################################"
echo "#####	S e n d   e M a i l												############"
echo "######################################################################################################################################"

        #### Send email using mutt      ####
        echo  "Attached log analysis files for the Jmeter results" | \
#                mutt -s "High Scale Lab Performance Monitor for ${YesterdayZipName} " ${AggregateReportFileList} -a ${Sql_AggregateReportFile} -a ${SqlCountReportFile} -a ${PerfMonReportFile} -e "set content_type=text/html" -- ${EMAIL_RECIPENT}
                mutt -s "High Scale Lab Performance Monitor for ${YesterdayZipName} " -a ${ExcelAggregateReportFileName} -a ${PerfMonReportFile} -e "set content_type=text/html" -- ${EMAIL_RECIPENT}




        on_error_handler "Failed to send email"

        if [[ ERROR -eq 0 ]]; then
                echo "Finished send email "
        else
                if [[ ERROR != 0 ]]; then
                        echo "${testFolder} error sending email"
                fi
        fi

}






