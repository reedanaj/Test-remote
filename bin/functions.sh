#!/bin/bash

#######################################################################
#####   Warming up and Validate PServer working                 #######
#######################################################################

worngRunErrMessage()
{
           echo "You run this script wrong way !!!"
           echo "You should run this script as follow:"
           echo "./run_suite.sh <projectName> <SuiteName>"
           echo "OR"
           echo "./run_suite.sh --pname VANILLA --sname Vanilla_MsSql --pid <pserver ip> --purl <pserver url> --pport <pserver port> --puser <pserver user> --pver <pserver version> --pkeyname <private key name> --dbip <DB ip> --dbport <DB port> --dbschema <DB schema> --dbuser <DB user> --dbpass <DB password> --dbsid <SID Id>"
           echo "For example: "
           echo "./run_suite.sh USB USB_Automation"
           echo "OR"
           echo "./run_suite.sh --pname VANILLA --sname Vanilla_MsSql --pid 10.0.11.42 --purl 10.0.11.42 --pport 8080 --puser ec2-user --pver 4.8.8_Tomcat_Engage_54 --pkeyname qa-dev --dbip auroramysqlaws.cpsow4kda4af.us-east-1.rds.amazonaws.com --dbport 3306 --dbschema V_4_8_MYSQL --dbuser V_4_8_MYSQL --dbpass V_4_8_MYSQL --dbsid orcl"
           exit 1

}

#######################################################################
#####   Warming up and Validate PServer working                 #######
#######################################################################

function sendApiRequest
{

## call getInsight API with dummy user that not exist ##
response_code="$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -H "effectiveTime: ${EffectiveDate}" -H "authToken: 000000000000${i}" -d '{"type": "getInsights", "protocolVersion": "2.5", "ctxId": "dashboard", "lang": "en", "autoGenerate": true }' http://${ServerIP}:${PServerPort}/pserver/execute?channel=${ProjectChannel})"
## validate response = 200
if [ "${response_code}" -ne "200" ]; then
	response_code="$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -H "effectiveTime: ${EffectiveDate}" -H "authToken: 000000000000${i}" -H "user: 01025640104708445" -H "person: 01025640104708445" -d '{"lang": "en","protocolVersion": "2.5","type": "cmdWrapper", "cmd": {"type": "getInsights","lang": "en", "protocolVersion": "2.5", "ctxId": "dashboard","autoGenerate": true ,"hints":{}}' http://${ServerIP}:${PServerPort}/pserver/execute?channel=${ProjectChannel})"
	if [ "${response_code}" -ne "200" ]; then
		echo "The pserver is not responed correctly (HTTP Return Code is not 200)"
		echo "curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -H "effectiveTime: ${EffectiveDate}" -H "authToken: 000000000000${i}" -d '{"type": "getInsights", "protocolVersion": "2.5", "ctxId": "dashboard", "lang": "en", "autoGenerate": true }' http://${ServerIP}:${PServerPort}/pserver/execute?channel=${ProjectChannel}"  >> ${TestDetailsFile}
	        echo "curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -H "effectiveTime: ${EffectiveDate}" -H "authToken: 000000000000${i}" -H "user: 01025640104708445" -H "person: 01025640104708445" -d '{"lang": "en","protocolVersion": "2.5","type": "cmdWrapper", "cmd": {"type": "getInsights","lang": "en", "protocolVersion": "2.5", "ctxId": "dashboard","autoGenerate": true ,"hints":{}}' http://${ServerIP}:${PServerPort}/pserver/execute?channel=${ProjectChannel})"  >> ${TestDetailsFile}
	        exit 1
	else
        	echo -e ".\c"
	fi
else
        echo -e ".\c"
fi

sleep .01
}


#######################################################################

function  WarmingUpAndValidatePServer()
{
sendApiRequest
HttpRC=${response_code}

if [ "${HttpRC}" != "200" ]; then
                echo "Warm up and PServer validation failed"
                exit 1
        else
		for ((y=0;y< ${WarmupCycles};y++))
	        do
        	        sendApiRequest&
                	sleep .4
	        done
		wait
		echo -e "\nWarming Pserver ${ServerIP} is Done at $(date +%Y)$(date +%m)$(date +%d)_$(date +%H)$(date +%M)$(date +%S)"
        fi
}
 #######################################################################
 #####   Run linux command on remote server			 #######
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
   ${functionName}
done

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
	pythonScript=${pythonScriptToRun}
	ssh -o StrictHostKeyChecking=no -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP} python3 - ${testFolder}_${ServerIP} ${RequestType} < ${pythonScript}
#	echo "ssh -o StrictHostKeyChecking=no -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP} python3 - ${testFolder}_${ServerIP} ${RequestType} < ${pythonScript}"
}



#######################################################################
 #####   clean pserver logs                                      #######
 #######################################################################

function cleanPserverLogs()
{
        runRemoteLinuxCommand ${pserverUser} 'rm -f $PERSONETICS_HOME/logs/*.zip' > /dev/null 2>&1
#        runRemoteLinuxCommand ${pserverUser} 'rm -f $PERSONETICS_HOME/logs/pserver.20*' > /dev/null 2>&1
#       runRemoteLinuxCommand ${pserverUser} 'rm -f $PERSONETICS_HOME/logs/2019*.log' > /dev/null 2>&1
#	runRemoteLinuxCommand ${pserverUser} 'mv $PERSONETICS_HOME/logs/2*settings.log $PERSONETICS_HOME/logs/2*settings.txt' > /dev/null 2>&1
        runRemoteLinuxCommand ${pserverUser} 'sudo truncate -s 0 $PERSONETICS_HOME/logs/*.log' > /dev/null 2>&1
}


#######################################################################
#####   Pserver Version and copy revision                       #######
#######################################################################
function pserverVersion()
{
scp -o StrictHostKeyChecking=no -r -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP}:\$PERSONETICS_HOME/revision.txt ${suiteResultsFolder}/${testFolder}
scp -o StrictHostKeyChecking=no -r -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP}:\$PERSONETICS_HOME/personetics.properties ${suiteResultsFolder}/${testFolder}
scp -o StrictHostKeyChecking=no -r -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP}:\$CATALINA_HOME/conf/Catalina/localhost/pserver.xml ${suiteResultsFolder}/${testFolder} > /dev/null 2>&1
scp -o StrictHostKeyChecking=no -r -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP}:\$CATALINA_HOME/conf/Catalina/localhost/srv-user.xml ${suiteResultsFolder}/${testFolder} > /dev/null 2>&1
}

#######################################################################
#####   Chose App Server Type and OS user                       #######
#######################################################################

function AppServerAndOsUser()
{
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

 #######################################################################
 #####   Build Pserver IP's list in csv file			 #######
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

}

function findPserverUrl()
{
echo "PServerID" > ${ProjectDir}/data/PserverList.csv
PServerUrlNum=0
IFS=, paths=($PServerUrl)
for (( PServerUrlNum=0; PServerUrlNum<${#paths[@]}; PServerUrlNum++ ))
do
   eval PserverUrl_$PServerUrlNum="${paths[$PServerUrlNum]}"
   echo "${paths[$PServerUrlNum]}" >> ${ProjectDir}/data/PserverList.csv
done

NumberOfPserverUrls=$PServerUrlNum

}

function createPserverList()
{
findPserverIps
findPserverUrl
}

 #######################################################################
 #####   Backup logs on Pserver to result folder                 #######
 #######################################################################
function runJmeter()
{
${JmeterPath}/jmeter -n -t ${ProjectDir}/scripts/${jmxFile}.jmx -JThreads=${JmeterThreads} -JProjectName=${Project} -JLoopCount=${NumberOfUsers} -JEffectiveTime=${EffectiveDate} -JProjectDir=${ProjectDir} -JTestFolder=${testFolder}

echo "${JmeterPath}/jmeter -n -t ${ProjectDir}/scripts/${jmxFile}.jmx -JThreads=${JmeterThreads} -JProjectName=${Project} -JLoopCount=${NumberOfUsers} -JEffectiveTime=${EffectiveDate} -JProjectDir=${ProjectDir} -JTestFolder=${testFolder}"  >> ${TestDetailsFile}

}


 #######################################################################
 #####   Backup logs on Pserver to result folder		 #######
 #######################################################################

function backupLogsToResultFolder()
{
	backupFolder=${testFolder}_${ServerIP}
	runRemoteLinuxCommand ${pserverUser} 'mkdir -p $PERSONETICS_HOME/logs/'${backupFolder}
	runRemoteLinuxCommand ${pserverUser} 'mv $PERSONETICS_HOME/logs/pserverErrors.*.zip $PERSONETICS_HOME/logs/'${backupFolder} > /dev/null 2>&1
	runRemoteLinuxCommand ${pserverUser} 'mv $PERSONETICS_HOME/logs/pserver.*.zip $PERSONETICS_HOME/logs/'${backupFolder} > /dev/null 2>&1
        runRemoteLinuxCommand ${pserverUser} 'mv $PERSONETICS_HOME/logs/srv-mleErrors.*.zip $PERSONETICS_HOME/logs/'${backupFolder} > /dev/null 2>&1
        runRemoteLinuxCommand ${pserverUser} 'mv $PERSONETICS_HOME/logs/srv-mle.*.zip $PERSONETICS_HOME/logs/'${backupFolder} > /dev/null 2>&1
        runRemoteLinuxCommand ${pserverUser} 'mv $PERSONETICS_HOME/logs/user.*.zip $PERSONETICS_HOME/logs/'${backupFolder} > /dev/null 2>&1
        runRemoteLinuxCommand ${pserverUser} 'mv $PERSONETICS_HOME/logs/userErrors.*.zip $PERSONETICS_HOME/logs/'${backupFolder} > /dev/null 2>&1
	runRemoteLinuxCommand ${pserverUser} 'cp $PERSONETICS_HOME/logs/pserver.log $PERSONETICS_HOME/logs/'${backupFolder} > /dev/null 2>&1
        runRemoteLinuxCommand ${pserverUser} 'cp $PERSONETICS_HOME/logs/pserverErrors.log $PERSONETICS_HOME/logs/'${backupFolder} > /dev/null 2>&1
        runRemoteLinuxCommand ${pserverUser} 'cp $PERSONETICS_HOME/logs/srv-mle.log $PERSONETICS_HOME/logs/'${backupFolder} > /dev/null 2>&1
        runRemoteLinuxCommand ${pserverUser} 'cp $PERSONETICS_HOME/logs/srv-mleErrors.log $PERSONETICS_HOME/logs/'${backupFolder} > /dev/null 2>&1
        runRemoteLinuxCommand ${pserverUser} 'cp $PERSONETICS_HOME/logs/user.log $PERSONETICS_HOME/logs/'${backupFolder} > /dev/null 2>&1
        runRemoteLinuxCommand ${pserverUser} 'cp $PERSONETICS_HOME/logs/userErrors.log $PERSONETICS_HOME/logs/'${backupFolder} > /dev/null 2>&1
        runRemoteLinuxCommand ${pserverUser} 'cp $PERSONETICS_HOME/logs/*.txt $PERSONETICS_HOME/logs/'${backupFolder} > /dev/null 2>&1
        runRemoteLinuxCommand ${pserverUser} 'cp $PERSONETICS_HOME/logs/gclog.log $PERSONETICS_HOME/logs/'${backupFolder} > /dev/null 2>&1
}

 #######################################################################
 #####   Analyzed Logs						 #######
 #######################################################################

#function AnalyzedResultLog()
#{
#        backupFolder=${testFolder}_${ServerIP}

##	MethodProcess
#	runRemoteLinuxCommand ${pserverUser} "echo ${MethodProcessHeader} > \$PERSONETICS_HOME/logs/${backupFolder}/${backupFolder}_MethodProcess.csv"
#        runRemoteLinuxCommand ${pserverUser} "zgrep \"Method processBlocksAndActions\" \$PERSONETICS_HOME/logs/${backupFolder}/pserver.* |  sed 'N;s/\n/,/' | grep -v 'isRetryApplied = false' | sed s/\|/,/g | sed s/\ RequestId=//g | sed s/\ party=//g | sed s/\ executed\ in\ //g | sed s/\ ms//g | awk -F ',' ${methodProcessAWK} >> \$PERSONETICS_HOME/logs/${backupFolder}/${backupFolder}_MethodProcess.csv"

##	TOOKS
#	runRemoteLinuxCommand ${pserverUser} "zgrep -h took \$PERSONETICS_HOME/logs/${backupFolder}/pserver.* | sed s/\|/,/g | awk -F 'AppBody' '{print \$2}' |sed s/:/\ /g | sed s/,/-/g | sed s/\ milliseconds//g | sed s/ms//g | sed s/\ milli-second//g | awk -F 'took' '{print \$1\",\"\$2}' > \$PERSONETICS_HOME/logs/${backupFolder}/${backupFolder}_Tooks.csv"

##	Duration
#        runRemoteLinuxCommand ${pserverUser} "zgrep duration= \$PERSONETICS_HOME/logs/${backupFolder}/pserver.* | awk -F 'AppBody=SQL' '{print \$2}' | sed s/ms//g | awk -F 'duration=' '{print substr(\$1,1,80)\",\"\$2}' > \$PERSONETICS_HOME/logs/${backupFolder}/${backupFolder}_Duration.csv"
#}

 #######################################################################
 #####   Analyzed Logs                                           #######
 #######################################################################

function RequestReceivedAnalysis()
{
        if [ -z "$1" ]; then
                RequestReceivedFileName=${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_Request_received
        else
                RequestReceivedFileName=$1
        fi


echo "timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,grpThreads,allThreads,Latency,IdleTime" > ${RequestReceivedFileName}_Jmeter.csv

exec < ${RequestReceivedFileName}.csv  >> ${RequestReceivedFileName}_Jmeter.csv || exit 1
read header
while read filename;
        do
        echo $filename | awk -F ',' '{print $1",1,Request_received,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
        done
}

##############################################################################

function ComponentAnalysis()
{
	if [ -z "$1" ]; then
		totalFileName=${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_Total
	else
		totalFileName=$1
	fi

	echo "timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,grpThreads,allThreads,Latency,IdleTime" > ${totalFileName}_Jmeter.csv

	IFS="
"
	while read totalFileLine;
        	do
	        echo ${totalFileLine} | awk -F ',' '{print $1","$3",HISTORY,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
        	echo ${totalFileLine} | awk -F ',' '{print $1","$4",LOGIC,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
	        echo ${totalFileLine} | awk -F ',' '{print $1","$5",PERSIST,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
        	echo ${totalFileLine} | awk -F ',' '{print $1","$6",RESPONSE,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
       		echo ${totalFileLine} | awk -F ',' '{print $1","$7",TOTAL Duration,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
	        echo ${totalFileLine} | awk -F ',' '{print $1","$8",NUM_OF_TRANSACTIONS,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
		echo ${totalFileLine} | awk -F ',' '{print $1","$9",DI,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
	        echo ${totalFileLine} | awk -F ',' '{print $1","$10",DI.AWAIT,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
        	echo ${totalFileLine} | awk -F ',' '{print $1","$11",DI.FETCH.GET_DATA,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
	        echo ${totalFileLine} | awk -F ',' '{print $1","$12",DI.FETCH.PREPARE,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
        	echo ${totalFileLine} | awk -F ',' '{print $1","$13",DI.FETCH.PROCESS,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
	        echo ${totalFileLine} | awk -F ',' '{print $1","$14",NUM_OF_INSIGHTS_RESPONSE,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
        	echo ${totalFileLine} | awk -F ',' '{print $1","$15",NUM_OF_INSIGHTS_GENERATED,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
	        echo ${totalFileLine} | awk -F ',' '{print $1","$16",NUM_OF_ACCOUNTS,200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}'
        	done < ${totalFileName}.csv  >> ${totalFileName}_Jmeter.csv

}

####################################################################################

function mergeTotalFiles()
{
	tail -n +2 ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_${RequestType}_Total.csv >> ${suiteResultsFolder}/${testFolder}/${testFolder}_All_${RequestType}_Total.csv
}

function LogToJMeter()
{
	python3 ${AutomationDir}/tools/LogToJmeter.py ${suiteResultsFolder}/${testFolder} ${RequestType} ${ServerIP}
}

function LogToJMeter_All()
{
        python3 ${AutomationDir}/tools/LogToJmeter.py ${suiteResultsFolder}/${testFolder} ${RequestType} All
}

 #######################################################################
 #####   Analyzed Logs                                           #######
 #######################################################################

function copyRemoteFiles()
{
        scp -o StrictHostKeyChecking=no -r -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP}:\$PERSONETICS_HOME/logs/${testFolder}_${ServerIP}/${testFolder}*.csv ${suiteResultsFolder}/${testFolder}
	scp -o StrictHostKeyChecking=no -r -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP}:\$PERSONETICS_HOME/logs/${testFolder}_${ServerIP}/*gclog.log ${suiteResultsFolder}/${testFolder}/${ServerIP}_gclog.log > /dev/null 2>&1
        scp -o StrictHostKeyChecking=no -r -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP}:\$PERSONETICS_HOME/logs/${testFolder}_${ServerIP}/${testFolder}_${ServerIP}_Errors.log ${suiteResultsFolder}/${testFolder}
        scp -o StrictHostKeyChecking=no -r -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP}:\$PERSONETICS_HOME/logs/${testFolder}_${ServerIP}/${testFolder}_${ServerIP}_SQL.log ${suiteResultsFolder}/${testFolder}
	scp -o StrictHostKeyChecking=no -r -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP}:\$PERSONETICS_HOME/logs/${testFolder}_${ServerIP}/${testFolder}_${ServerIP}_Insights.log ${suiteResultsFolder}/${testFolder}
}

function fixDateForJmeter()
{
	sed -i -e s/${Today}T/${Today}\ /g ${suiteResultsFolder}/${testFolder}/${testFolder}_*_Total.csv
	sed -i -e s/${Tommorow}T/${Tommorow}\ /g ${suiteResultsFolder}/${testFolder}/${testFolder}_*_Total.csv
	sed -i -e s/${DayAfterTomorrow}T/${DayAfterTomorrow}\ /g ${suiteResultsFolder}/${testFolder}/${testFolder}_*_Total.csv
}

 #######################################################################
 #####   Create Jmeter Graphs form csv results file              #######
 #######################################################################

function createJmeterGraphs()
{
graphType=$1
FileToAnalyzied=$2

${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${suiteResultsFolder}/${graphType}.png --input-jtl ${suiteResultsFolder}/${FileToAnalyzied} --plugin-type ${graphType} --width 1200 --height 800 --limit-rows 200

echo "${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${suiteResultsFolder}/${graphType}.png --input-jtl ${suiteResultsFolder}/${FileToAnalyzied} --plugin-type ${graphType} --width 1200 --height 800 --limit-rows 200"

}


 #######################################################################
 #####   Create Jmeter AggregateReport form csv results file     #######
 #######################################################################

function createAggregateReport()
{
FileToAggregate=${testFolder}_${ServerIP}_${RequestType}_Total_Jmeter.csv
${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_${RequestType}_Component_AggregateReport.csv --input-jtl ${suiteResultsFolder}/${testFolder}/${FileToAggregate} --plugin-type AggregateReport


${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_${RequestType}_Total_ResponseTimesOverTime.png --input-jtl ${suiteResultsFolder}/${testFolder}/${FileToAggregate} --plugin-type ResponseTimesOverTime --auto-scale no --include-label-regex true --include-labels .*Duration.* --width 1200 --height 800 --limit-rows 200

${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_${RequestType}_Total_TransactionsPerSecond.png --input-jtl ${suiteResultsFolder}/${testFolder}/${FileToAggregate} --plugin-type TransactionsPerSecond --auto-scale no --include-label-regex true --include-labels .*Duration.* --width 1200 --height 800 --limit-rows 200

${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_${RequestType}_Total_ResponseTimesDistribution.png --input-jtl ${suiteResultsFolder}/${testFolder}/${FileToAggregate} --plugin-type ResponseTimesDistribution --auto-scale no --include-label-regex true --include-labels .*Duration.* --width 1200 --height 800 --limit-rows 200

echo "${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_${RequestType}_Component_AggregateReport.csv --input-jtl ${suiteResultsFolder}/${testFolder}/${FileToAggregate} --plugin-type AggregateReport --width 1200 --height 800 --limit-rows 200"

echo "${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_${RequestType}_Total_ResponseTimesOverTime.png --input-jtl ${suiteResultsFolder}/${testFolder}/${FileToAggregate} --plugin-type ResponseTimesOverTime --auto-scale no --include-label-regex true --include-labels .*Duration.* --width 1200 --height 800 --limit-rows 200"

echo "${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_${RequestType}_Total_TransactionsPerSecond.png --input-jtl ${suiteResultsFolder}/${testFolder}/${FileToAggregate} --plugin-type TransactionsPerSecond --auto-scale no --include-label-regex true --include-labels .*Duration.* --width 1200 --height 800 --limit-rows 200"

echo "${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_${RequestType}_Total_ResponseTimesDistribution.png --input-jtl ${suiteResultsFolder}/${testFolder}/${FileToAggregate} --plugin-type ResponseTimesDistribution --auto-scale no --include-label-regex true --include-labels .*Duration.* --width 1200 --height 800 --limit-rows 200"


RequestReceived_FileToAggregate=${testFolder}_${ServerIP}_Request_received_Jmeter.csv
${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_RequestReceived_AggregateReport.csv --input-jtl ${suiteResultsFolder}/${testFolder}/${RequestReceived_FileToAggregate} --plugin-type AggregateReport

${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_RequestReceived_TransactionsPerSecond.png --input-jtl ${suiteResultsFolder}/${testFolder}/${RequestReceived_FileToAggregate} --plugin-type TransactionsPerSecond --auto-scale no --include-label-regex true --include-labels .*Request.* --width 1200 --height 800 --limit-rows 200

echo "${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_RequestReceived_AggregateReport.csv --input-jtl ${suiteResultsFolder}/${testFolder}/${RequestReceived_FileToAggregate} --plugin-type AggregateReport"

echo "${JmeterPath}/JMeterPluginsCMD.sh --generate-png ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_RequestReceived_TransactionsPerSecond.png --input-jtl ${suiteResultsFolder}/${testFolder}/${RequestReceived_FileToAggregate} --plugin-type TransactionsPerSecond --auto-scale no --include-label-regex true --include-labels .*Request.* --width 1200 --height 800 --limit-rows 200"

SqlFileToAggregate=${testFolder}_${ServerIP}_SQL_TOTAL_Jmeter.csv
${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_Sql_AggregateReport.csv --input-jtl 
${JmeterPath}/JMeterPluginsCMD.sh --generate-csv ${suiteResultsFolder}/${testFolder}/${testFolder}_${ServerIP}_RequestReceived_AggregateReport.csv --input-jtl ${suiteResultsFolder}/${testFolder}/${SqlFileToAggregate} --plugin-type AggregateReport

}

 #######################################################################
 #####   Create Jmeter Graphs form csv results file              #######
 ####################################################################################################################
 #                                                                                                              #####
 # To use this this option  jpgc-synthesis should be installed							#####
 # To verify if installed: ./PluginsManagerCMD.sh status							##### 
 # If It not installed, from Jmeter installation folder run: bin/PluginsManagerCMD.sh install jpgc-synthesis	#####
 #														#####
 ####################################################################################################################

function jmeterReporter()
{

exec < ${JmeterReporterFile} || exit 1
read header
while IFS="," read -r ReporterType graphType FileToAnalyzied ReportName extraCommand1 extraCommand2 extraCommand3 extraCommand4 extraCommand5 extraCommand6
do

echo "###################################################################################################################"


       ${JmeterPath}/JMeterPluginsCMD.sh --generate-${ReporterType} ${suiteResultsFolder}/${testFolder}/${testFolder}_${ReportName}.${ReporterType} --input-jtl ${suiteResultsFolder}/${testFolder}/${FileToAnalyzied} --plugin-type ${graphType} ${extraCommand1} ${extraCommand2} ${extraCommand3} ${extraCommand4} ${extraCommand5} ${extraCommand6} --width 1200 --height 800 --limit-rows 200 > /dev/null 2>&1

	echo "${JmeterPath}/JMeterPluginsCMD.sh --generate-${ReporterType} ${suiteResultsFolder}/${testFolder}/${testFolder}_${ReportName}.${ReporterType} --input-jtl ${suiteResultsFolder}/${testFolder}/${FileToAnalyzied} --plugin-type ${graphType} ${extraCommand1} ${extraCommand2} ${extraCommand3} ${extraCommand4} ${extraCommand5} ${extraCommand6} --width 1200 --height 800 --limit-rows 200"
	
	echo "${JmeterPath}/JMeterPluginsCMD.sh --generate-${ReporterType} ${suiteResultsFolder}/${testFolder}/${testFolder}_${ReportName}.${ReporterType} --input-jtl ${suiteResultsFolder}/${testFolder}/${FileToAnalyzied} --plugin-type ${graphType} ${extraCommand1} ${extraCommand2} ${extraCommand3} ${extraCommand4} ${extraCommand5} ${extraCommand6} --width 1200 --height 800 --limit-rows 200" >> ${TestDetailsFile}
done 

}


 #######################################################################
 #####   Create Jmeter AggregateReport form csv results file     #######
 #######################################################################
 #              This feature support only Tomcat Pserver                #
 ########################################################################

function runSettingFile()
{
SettingFile=$1

ssh -o StrictHostKeyChecking=no -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP} "sudo service tomcat stop"
echo ""
echo "PServer is going down"
sleep 1m

while read setingToChange
      do
      ssh -o StrictHostKeyChecking=no -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP} "${setingToChange}"
      done < ${SettingFile}

cleanPserverLogs
ssh -o StrictHostKeyChecking=no -i ${PrivateKey}/${KeyName}.pem ${pserverUser}@${ServerIP} "sudo service tomcat start"
echo "going to sleep for 5 minute while PServer is going up"
sleep 5m

}

 #######################################################################
 #####   zip Folder                                              #######
 #######################################################################
function zipFolder()
{
folderPath=$1
folderToZip="$(basename $folderPath)"
zip -rj $folderPath/$folderToZip.zip $folderPath/* > /dev/null 2>&1
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
	suiteName=$1

	####	Create zip files list to send in Mail	####	
	zipFilesList="-a ${suiteName}/${suiteFolderName}.xlsx "
	for zipFilesName in ${suiteName}/*/*.zip; do
		zipFilesList+="-a ${zipFilesName} " 
	done

        #### Send email using mutt	####
        echo  "Attached log analysis files for the Jmeter results" | \
                mutt -s "Jenkins Performance Test Results for ${suiteFolderName} " \
		${zipFilesList} \
		-e "set content_type=text/html" -- ${EMAIL_RECIPENT}

        on_error_handler "Failed to send email"

        if [[ ERROR -eq 0 ]]; then
                echo "Finished send email "
        else
                if [[ ERROR != 0 ]]; then
                        echo "${suiteFolderName} error sending email"
                fi
        fi

}

 #######################################################################
 #####   compare files                                           #######
 #######################################################################
function compareAPIsResults()
{
exec < ${ProjectDir}/configuration/api_configfile.cfg || exit 1
read header
while IFS="," read -r ApiName comparsionMethod givingGapValue
do
	if [[ ${comparsionMethod} = "value" ]];then
		compareAPIsByValue
	elif [[ ${comparsionMethod} = Percentile ]];then
		compareAPIsByPercentile
	else
		echo "this comparsionMethod ${comparsionMethod} is Not Supported"
		exit 1
	fi
done
}

function compareAPIsByValue()
{
echo "start compareAPIsByValue"
ApiName="generateInsight"

resultsFile="${ProjectDir}/results/${testFolder}/BMO_6_Threads_bmo_20200212_114609_172.17.1.94_Component_AggregateReport.csv"
benchMarkFile="${ProjectDir}/results/${testFolder}/BMO_6_Threads_bmo_20200211_104518_172.17.1.94_Component_AggregateReport.csv"


printf -v resultsAvg %d $(grep 'TOTAL Duration' $resultsFile | awk -F ',' '{print $3}')
printf -v benchMarkAvg %d $(grep 'TOTAL Duration' $benchMarkFile | awk -F ',' '{print $3}')
gapValue=$((${resultsAvg}-${benchMarkAvg}))
resultStatusV="none"

if [[ ${gapValue} -lt ${givingGapValue} && ${gapValue} -gt "-${givingGapValue}" ]];then
	resultStatusV="Passed"
elif [[ ${gapValue} -ge ${givingGapValue} ]];then
	resultStatusV="Failed"
else
	resultStatusV="Improvment"
fi

echo "${ApiName},${resultsAvg},${benchMarkAvg},${gapValue},${resultStatusV}" >> ${ProjectDir}/results/${testFolder}/${testFolder}_Status.csv

}


function compareAPIsByPercentile()
{
echo "Start compareAPIsByPercentile"
ApiName="generateInsight"
#resultsFile="${ProjectDir}/results/${testFolder}/BMO_6_Threads_bmo_20200212_114609_172.17.1.94_${ApiName}_Component_AggregateReport.csv"
#benchMarkFile="${ProjectDir}/results/${testFolder}/BMO_6_Threads_bmo_20200211_104518_172.17.1.94_${ApiName}_Component_AggregateReport.csv"

resultsFile="${ProjectDir}/results/${testFolder}/BMO_6_Threads_bmo_20200212_114609_172.17.1.94_Component_AggregateReport.csv"
benchMarkFile="${ProjectDir}/results/${testFolder}/BMO_6_Threads_bmo_20200211_104518_172.17.1.94_Component_AggregateReport.csv"


printf -v resultsAvg %d $(grep 'TOTAL Duration' $resultsFile | awk -F ',' '{print $3}')
printf -v benchMarkAvg %d $(grep 'TOTAL Duration' $benchMarkFile | awk -F ',' '{print $3}')

#echo "benchMarkAvg= ${benchMarkAvg}"
#echo "resultsAvg=${resultsAvg}"

#gapValue=$(expr ${resultsAvg} / ${benchMarkAvg})
gapValue=$( echo -e scale=2 "\n" ${resultsAvg}\/${benchMarkAvg} | bc -l)
maxValue=`echo 1+${givingGapValue} | bc `
minValue=`echo 1-${givingGapValue} | bc`

#echo "gapValue = ${gapValue}"
#echo "maxValue = ${maxValue}"
#echo "minValue = ${minValue}"

resultStatusP="none"

#if [[ ${gapValue%.*} < ${maxValue%.*} && ${gapValue%.*} > ${minValue%.*} ]];then
#if [[ ${gapValue%.*} -le ${maxValue%.*} && ${gapValue%.*} -ge ${minValue%.*} ]];then
if [[ $(bc -l <<< "$gapValue < $maxValue") -eq 1 && $(bc -l <<< "$gapValue > $minValue") -eq 1 ]];then
        resultStatusP="Passed"
elif [[ $(bc -l <<< "$gapValue > $maxValue") -eq 1 ]];then
        resultStatusP="Failed"
else
        resultStatusP="Improvment"
fi

echo "${ApiName},${resultsAvg},${benchMarkAvg},${gapValue},${resultStatusP}" >> ${ProjectDir}/results/${testFolder}/${testFolder}_Status.csv

}






