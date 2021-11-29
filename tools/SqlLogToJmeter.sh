#!/bin/bash
#set -o xtrace

#clear

if [ -z "$1" ]; then
	exit 1;
	echo " please run this script as: ././SqlLogToJmeter.sh <Results Folder Nmae> (for Exp. > ./SqlLogToJmeter.sh VANILLA_MySql_4_Threads_Dev"
   else
	totalFileName=$1
   fi

cd $PERSONETICS_HOME/logs/

   echo "timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,grpThreads,allThreads,Latency,IdleTime" > ${totalFileName}/${totalFileName}_SQL_TOTAL_Jmeter.csv

   zgrep -h duration= ${totalFileName}/pserver.* | grep '\- SQL' | grep -v 'Thread acquired from the DI thread pool' | sed s/'\ SQL'/'\ ,XXXXSQL'/g | sed s/'\ \['/',XXXX\ \['/g  | sed s/duration=/,XXXXduration=/g | sed s/SQL\ Query\ //g | sed s/\ ms//g | sed s/?,//g | awk -F ',XXXX' '{print $1"XXXX"substr($3,1,120)"XXXX"$4}' |sed s/\ done,\ //g | sed s/duration=//g |sed s/,/\ /g | sed s/\"//g | sed s/\ SELECT/SELECT/g | sed s/\'//g | sed s/-/\\//g | awk -F 'XXXX' '{print $1","$3","$2",200,OK,GetInsight 2-1,text,true,,458674,1,1,1266,0"}' >> ${totalFileName}/${totalFileName}_SQL_TOTAL_Jmeter.csv

