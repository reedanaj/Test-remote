#!/bin/bash 
#set -o xtrace

#if [ -z "$1" ]; then
#        echo "please run this script as: ./parss_log.sh <pserver log files path> (for Exp. >./deleteOldLog.sh /usr/local/personetics/p_home/logs )"
#        exit 1;
#fi

#file_path=$1

TotalsAnalysis()
{
	#pattern_partyid="party="
	pattern_partyid="PARTY_ID: "
	pattern_Tx="NUM_OF_TRANSACTIONS: "

	cd $PERSONETICS_HOME/logs/

	zgrep -h -q -m1 "TOTAL:" ${file_path}/pserver.* 
	if [ $? -eq 0 ];
	   then
		SearchText="TOTAL:"
		pattern_date="^"
		pattern_HISTORY="HISTORY: "
		pattern_LOGIC="LOGIC: "
		pattern_PERSIST="PERSIST: "
		pattern_RESPONSE=" RESPONSE: "
		pattern_TOTAL="TOTAL: "
		pattern_DI="DI: "
        	pattern_DI_AWAIT="DI.AWAIT: "
	        pattern_GET_DATA="DI.FETCH.GET_DATA: "
	        pattern_PREPARE="DI.FETCH.PREPARE: "
	        pattern_DI_PROCESS="DI.FETCH.PROCESS: "
		pattern_INSIGHTS_RESPONSE="NUM_OF_INSIGHTS_RESPONSE: "
		pattern_INSIGHTS_GENERATED="NUM_OF_INSIGHTS_GENERATED: "
		pattern_ACCOUNTS="NUM_OF_ACCOUNTS: "
	else
		zgrep -h -q -m1 "TOTAL=" ${file_path}/pserver.*
		if [ $? -eq 0 ];
		   then
			SearchText="TOTAL="
			pattern_date="^"
			pattern_HISTORY="HISTORY="
			pattern_LOGIC="LOGIC="
			pattern_PERSIST="PERSIST="
			pattern_RESPONSE=" RESPONSE="
			pattern_TOTAL="TOTAL="
			pattern_DI="DI="
        	        pattern_DI_AWAIT="DI.AWAIT="
                	pattern_GET_DATA="DI.FETCH.GET_DATA="
	                pattern_PREPARE="DI.FETCH.PREPARE="
        	        pattern_DI_PROCESS="DI.FETCH.PROCESS="
			pattern_INSIGHTS_RESPONSE="NUM_OF_INSIGHTS_RESPONSE="
			pattern_INSIGHTS_GENERATED="NUM_OF_INSIGHTS_GENERATED="
			pattern_ACCOUNTS="NUM_OF_ACCOUNTS="
		else
			echo "Unknowen Log format exit from analysis"
			exit 1;
		fi
	fi

zgrep -h ${SearchText} ${file_path}/pserver.* | grep 'REQUEST_TYPE: getInsights,' |sed s/\\[/,\\[/g | sed s/\\[http/,\\[http/g | sed s/\|\ /,/g |sed s/\ ,\ /,/g | sed s/},\ /,/g | sed s/-/\\//g | sed s/+000//g | sed s/DT=//g | awk \
	-v pattern_date="${pattern_date}" \
	-v pattern_partyid="${pattern_partyid}" \
	-v pattern_HISTORY="${pattern_HISTORY}" \
	-v pattern_LOGIC="${pattern_LOGIC}" \
	-v pattern_PERSIST="${pattern_PERSIST}" \
	-v pattern_RESPONSE="${pattern_RESPONSE}" \
	-v pattern_TOTAL="${pattern_TOTAL}" \
	-v pattern_Tx="${pattern_Tx}" \
	-v pattern_DI="${pattern_DI}" \
        -v pattern_DI_AWAIT="${pattern_DI_AWAIT}" \
        -v pattern_GET_DATA="${pattern_GET_DATA}" \
        -v pattern_PREPARE="${pattern_PREPARE}" \
        -v pattern_DI_PROCESS="${pattern_DI_PROCESS}" \
	-v pattern_INSIGHTS_RESPONSE="${pattern_INSIGHTS_RESPONSE}" \
	-v pattern_INSIGHTS_GENERATED="${pattern_INSIGHTS_GENERATED}" \
	-v pattern_ACCOUNTS="${pattern_ACCOUNTS}" \ '
	{
	val_date=val_PartyId=val_get_history=val_logic=val_persist=val_response=val_total=val_numTx=val_di=val_di_await=val_di_getDate=val_Di_prepare=val_di_process=val_insightResponse=val_insightGenerated=val_account="0";

	#Get Date & Time 
	pos_DateAndTime=match($0, pattern_date);
	if (pos_DateAndTime>0) 
		{
		pos_DateAndTime=length (pattern_date);
		seg_val_date=substr($0,pos_DateAndTime,30);
		match(seg_val_date,/^([^,\|]*[,\|])/); 
		val_date=substr(seg_val_date, RSTART, RLENGTH-2);
		}

	# Get Party ID
	pos_PartyId=match($0, pattern_partyid); 
	if (pos_PartyId>0) 
		{
		pos_PartyId += length (pattern_partyid);
		seg_val_PartyId=substr($0,pos_PartyId,100);
		match(seg_val_PartyId, /[A-Za-z0-9]+([.][A-Za-z0-9]+)?/);
		val_PartyId=substr(seg_val_PartyId, RSTART, RLENGTH);	
		}

	#Get History
	pos_get_history=match($0, pattern_HISTORY); 
	if (pos_get_history>0) 
		{
		pos_get_history+=length (pattern_HISTORY);
		seg_val_get_history=substr($0,pos_get_history,5);
		match(seg_val_get_history, /[0-9]+([.][0-9]+)?/);
		val_get_history=substr(seg_val_get_history, RSTART, RLENGTH);
		}

	#Get LOGIC
	pos_logic=match($0, pattern_LOGIC);
	if (pos_logic>0) 
		{
		pos_logic+=length (pattern_LOGIC);
		seg_val_logic=substr($0,pos_logic,5);
		match(seg_val_logic, /[0-9]+([.][0-9]+)?/);
		val_logic=substr(seg_val_logic, RSTART, RLENGTH);
		}

	#Get PERSIST
	pos_persist=match($0, pattern_PERSIST);
	if (pos_persist>0) {
		pos_persist+=length (pattern_PERSIST);
		seg_val_persist=substr($0,pos_persist,5);
		match(seg_val_persist, /[0-9]+([.][0-9]+)?/);
		val_persist=substr(seg_val_persist, RSTART, RLENGTH);
		}

	#Get RESPONSE
	pos_response=match($0, pattern_RESPONSE);
	if (pos_response>0) {
		pos_response+=length (pattern_RESPONSE);
		seg_val_response=substr($0,pos_response,5);
		match(seg_val_response, /[0-9]+([.][0-9]+)?/);
		val_response=substr(seg_val_response, RSTART, RLENGTH);
		}

	#Get TOTAL
	pos_total=match($0, pattern_TOTAL);
	if (pos_total>0) {
		pos_total+=length (pattern_TOTAL);
		seg_val_total=substr($0,pos_total,5);
		match(seg_val_total, /[0-9]+([.][0-9]+)?/);
		val_total=substr(seg_val_total, RSTART, RLENGTH);
		}

	#Get NUM OF TRANSACTION
	pos_numTx=match($0, pattern_Tx);
	if (pos_get_history>0) {
		pos_numTx+=length (pattern_Tx);
		seg_val_numTx=substr($0,pos_numTx,5);
		match(seg_val_numTx, /[0-9]+([.][0-9]+)?/);
		val_numTx=substr(seg_val_numTx, RSTART, RLENGTH);
		}

	#Get DI
	pos_di=match($0, pattern_DI);
	if (pos_di>0)
		{
		pos_di+=length (pattern_DI);
		seg_val_di=substr($0,pos_di,5);
		match(seg_val_di, /[0-9]+([.][0-9]+)?/);
		val_di=substr(seg_val_di, RSTART, RLENGTH);
		}

	#Get DI_AWAIT
        pos_di_await=match($0, pattern_DI_AWAIT);
        if (pos_di_await>0) {
        	pos_di_await+=length (pattern_DI_AWAIT);
                seg_val_di_await=substr($0,pos_di_await,5);
                match(seg_val_di_await, /[0-9]+([.][0-9]+)?/);
                val_di_await=substr(seg_val_di_await, RSTART, RLENGTH);
                }

	#Get DI.FETCH.GET_DATA
        pos_di_getDate=match($0, pattern_GET_DATA);
        if (pos_di_getDate>0) {
        	pos_di_getDate+=length (pattern_GET_DATA);
                seg_val_di_getDate=substr($0,pos_di_getDate,5);
                match(seg_val_di_getDate, /[0-9]+([.][0-9]+)?/);
                val_di_getDate=substr(seg_val_di_getDate, RSTART, RLENGTH);
                }

	#Get DI.FETCH.PREPARE
        pos_di_prepare=match($0, pattern_PREPARE);
        if (pos_di_prepare>0) {
        	pos_di_prepare+=length (pattern_PREPARE);
                seg_val_Di_prepare=substr($0,pos_di_prepare,5);
                match(seg_val_Di_prepare, /[0-9]+([.][0-9]+)?/);
                val_Di_prepare=substr(seg_val_Di_prepare, RSTART, RLENGTH);
                }

	#Get DI.FETCH.PROCESS
        pos_di_process=match($0, pattern_DI_PROCESS);
        if (pos_di_process>0) {
        	pos_di_process+=length (pattern_DI_PROCESS);
                seg_val_di_process=substr($0,pos_di_process,5);
                match(seg_val_di_process, /[0-9]+([.][0-9]+)?/);
                val_di_process=substr(seg_val_di_process, RSTART, RLENGTH);
                }

	#Get NUM_OF_INSIGHTS_RESPONSE
	pos_insightResponse=match($0, pattern_INSIGHTS_RESPONSE);
	if (pos_insightResponse>0) {
		pos_insightResponse+=length (pattern_INSIGHTS_RESPONSE);
		seg_val_insightResponse=substr($0,pos_insightResponse,5);
		match(seg_val_insightResponse, /[0-9]+([.][0-9]+)?/);
		val_insightResponse=substr(seg_val_insightResponse, RSTART, RLENGTH);
		}

	#Get NUM_OF_INSIGHTS_GENERATED
	pos_insightGenerated=match($0, pattern_INSIGHTS_GENERATED);
	if (pos_insightGenerated>0) {
		pos_insightGenerated+=length (pattern_INSIGHTS_GENERATED);
		seg_val_insightGenerated=substr($0,pos_insightGenerated,5);
		match(seg_val_insightGenerated, /[0-9]+([.][0-9]+)?/);
		val_insightGenerated=substr(seg_val_insightGenerated, RSTART, RLENGTH);
		}

	#Get NUM_OF_ACCOUNTS
	pos_account=match($0, pattern_ACCOUNTS);
	if (pos_account>0) {
		pos_account+=length (pattern_ACCOUNTS);
		seg_val_account=substr($0,pos_account,5);
		match(seg_val_account, /[0-9]+([.][0-9]+)?/);
		val_account=substr(seg_val_account, RSTART, RLENGTH);
		}

	# Print the tooks line only when some value was extracted
	if (val_get_date	!= "0" ||
		val_PartyId		!= "0" ||
		val_get_history		!= "0" ||
		val_logic		!= "0" ||
		val_persist		!= "0" ||
		val_response		!= "0" ||
		val_total		!= "0" ||
		val_numTx		!= "0" ||
		val_di			!= "0" ||
                val_di_await            != "0" ||
                val_di_getDate          != "0" ||
                val_Di_prepare          != "0" ||
                val_di_process          != "0" ||
		val_insightResponse	!= "0" ||
		val_insightGenerated	!= "0" ||
		val_account		!= "0" )
		printf ("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n", val_date,val_PartyId,val_get_history,val_logic,val_persist,val_response,val_total,val_numTx,val_di,val_di_await,val_di_getDate,val_Di_prepare,val_di_process,val_insightResponse,val_insightGenerated,val_account) ;
		
	}' > ${file_path}/${file_path}_Total.csv
}

max()
{
 FILE=$1
 cat $FILE |sort -n |tail -1 |sed 's/ //g'
}

average()
{
 FILE=$1
 if [ -f $FILE ] && [ -s $FILE  ] ; then
        cat $FILE | awk '{ sum+=$1 } END { print sum/ NR }' | cut -d"." -f1
 fi
}

percentile50()
{
 NUM_LINES=$1
 FILE=$2
 FIRST_50=$(( $NUM_LINES -  $NUM_LINES * 1/2 ))
 cat $FILE |sort -n |head -"$FIRST_50" |tail -1

}

percentile90()
{
 NUM_LINES=$1
 FILE=$2
 FIRST_90=$(( $NUM_LINES -  $NUM_LINES * 1/10 ))
 # average of the highest 90% average
 #cat $FILE |sort -n |head -"$FIRST_90" | awk '{ sum+=$1 } END { print sum/ NR }' |cut -d"." -f1
 cat $FILE |sort -n |head -"$FIRST_90" |tail -1
 #cat $FILE |sort -n | awk 'BEGIN{c=0} {total[c]=$1; c++;} END{print total[int(NR*0.95-0.5)]}'

}

percentile99()
{
 NUM_LINES=$1
 FILE=$2
 FIRST_99=$(( $NUM_LINES -  $NUM_LINES * 1/100 ))
 # average of the highest 99% average
 #cat $FILE |sort -n |head -"$FIRST_99" | awk '{ sum+=$1 } END { print sum/ NR }' |cut -d"." -f1
 cat $FILE |sort -n |head -"$FIRST_99" |tail -1
 #cat $FILE |sort -n | awk 'BEGIN{c=0} {total[c]=$1; c++;} END{print total[int(NR*0.99-0.5)]}'
}


AnalyzeErrors()
{
#        echo "" | tee -a ${file_path}/${file_path}_Errors.log
        echo "Top errors found:" | tee -a ${file_path}/${file_path}_Errors.log
         zgrep -h "ERROR\|Memory collection threshold reached\|pserver started" ${file_path}/pserver.* >  ${file_path}/${file_path}_all_errors.log
        cat ${file_path}/${file_path}_all_errors.log | awk '{print  $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24}' | sed 's/RequestId=.*,//' |sed 's/party=.*,//' | sed 's/ProcId=.*}//' |sed 's/id: .*//g' |sed 's/modelId .*//g' | sed 's/[0-9]*//g' |sed 's/|//g' |sed 's/\-//' |sed 's/\=//' |sort | uniq -c |sort -n | tail -20 | tee -a ${file_path}/${file_path}_Errors.log

         echo "" | tee -a ${file_path}/${file_path}_Errors.log
         echo "Top user errors:" | tee -a ${file_path}/${file_path}_Errors.log
         cat ${file_path}/${file_path}_all_errors.log |grep -oP "PARTY_ID: \w*" |cut -d"=" -f2 |sort | uniq -c |sort -n |tail -10 > ${file_path}/${file_path}_top_user_errors.log
         cat ${file_path}/${file_path}_top_user_errors.log| tee -a ${file_path}/${file_path}_Errors.log


         echo "" | tee -a ${file_path}/${file_path}_Errors.log
         echo "Errors distribuson per hour:" | tee -a ${file_path}/${file_path}_Errors.log
         echo "Hour,Number_of_Errors" | tee -a ${file_path}/${file_path}_Errors.log
         cat ${file_path}/${file_path}_all_errors.log | cut -d"." -f1 |cut -d":" -f1 |sort | uniq -c |awk '{print $2,$3,","$1}' | tee -a ${file_path}/${file_path}_Errors.log

         echo "" | tee -a ${file_path}/${file_path}_Errors.log
         grep -h -q -m1 "Memory collection threshold reached" ${file_path}/${file_path}_all_errors.log
         if [ $? -eq 0 ]; then
                echo "Memory collection threshold reached events!"  | tee -a ${file_path}/${file_path}_Errors.log
                grep "Memory collection threshold reached" ${file_path}/${file_path}_all_errors.log |cut -d":" -f1,2 |sort |uniq -c | tee -a ${file_path}/${file_path}_Errors.log
         fi

         echo "" | tee -a ${file_path}/${file_path}_Errors.log
         grep -h -q -m1 "pserver started" ${file_path}/${file_path}_all_errors.log
         if [ $? -eq 0 ]; then
                echo "pserver started events!"  | tee -a ${file_path}/${file_path}_Errors.log
                grep "pserver started" ${file_path}/${file_path}_all_errors.log |cut -d":" -f1,2 |sort |uniq -c | tee -a ${file_path}/${file_path}_Errors.log
         else
                echo "No application restarts" | tee -a ${file_path}/${file_path}_Errors.log
         fi

        rm -f ${file_path}/${file_path}_all_errors.log
        rm -f ${file_path}/${file_path}_top_user_errors.log
}

AnalyzeSQLs()
{
        echo "" | tee -a  ${file_path}/${file_path}_SQL.log
        echo "SQL queries repsonse time statistics:" | tee -a  ${file_path}/${file_path}_SQL.log
        echo "" | tee -a  ${file_path}/${file_path}_SQL.log
        zgrep -h "SQL " ${file_path}/pserver.* |grep -v "value :" > ${file_path}/${file_path}_all_sql_queries.log
        grep Thread  ${file_path}/${file_path}_all_sql_queries.log | grep -v "param\|DEBUG_USERS" > ${file_path}/${file_path}_transferdb_sql_queries.log
        echo "transferdb_sql_queries_response_times,Durarion_in_MS" > ${file_path}/${file_path}_transferdb_sql_queries_response_times.csv
        cat ${file_path}/${file_path}_transferdb_sql_queries.log | sed 's/ \[.*, duration=/,/g' |sed 's/ms//g' >> ${file_path}/${file_path}_transferdb_sql_queries_response_times.csv

        grep -v Thread  ${file_path}/${file_path}_all_sql_queries.log | grep -v "param\|DEBUG_USERS" > ${file_path}/${file_path}_chatdb_sql_queries.log
        grep -v -i " merge \| update \| insert " ${file_path}/${file_path}_chatdb_sql_queries.log > ${file_path}/${file_path}_chatdb_read_sql_queries.log
        echo "chatdb_read_sql_queries_response_times,Durarion_in_MS" > ${file_path}/${file_path}_chatdb_read_sql_queries_response_times.csv
        cat ${file_path}/${file_path}_chatdb_read_sql_queries.log | sed 's/ \[.*, duration=/,/g' | sed 's/ms//g'  >>  ${file_path}/${file_path}_chatdb_read_sql_queries_response_times.csv

        grep -i " merge \| update \| insert " ${file_path}/${file_path}_chatdb_sql_queries.log > ${file_path}/${file_path}_chatdb_write_sql_queries.log
        echo "chatdb_write_sql_queries_response_times,Durarion_in_MS" > ${file_path}/${file_path}_chatdb_write_sql_queries_response_times.csv
        cat  ${file_path}/${file_path}_chatdb_write_sql_queries.log | sed 's/ \[.*, duration=/,/g' |sed 's/ms//g'  >> ${file_path}/${file_path}_chatdb_write_sql_queries_response_times.csv

        grep -oP "duration=\w*" ${file_path}/${file_path}_chatdb_read_sql_queries.log |cut -d"=" -f2 | sed 's/ms//g' > ${file_path}/${file_path}_CHATDB_READ_SQL_RESPONSE
        grep -oP "duration=\w*" ${file_path}/${file_path}_chatdb_write_sql_queries.log |cut -d"=" -f2 |sed 's/ms//g' > ${file_path}/${file_path}_CHATDB_WRITE_SQL_RESPONSE
        grep -oP "duration=\w*" ${file_path}/${file_path}_transferdb_sql_queries.log |cut -d"=" -f2 | sed 's/ms//g' > ${file_path}/${file_path}_TRANSFERDB_SQL_RESPONSE

        echo "DB Queries,Count,Average,50%,90%,99%,Max" > ${file_path}/${file_path}_sql_table
        for COMPONENT in $(echo ${file_path}_CHATDB_READ_SQL_RESPONSE ${file_path}_CHATDB_WRITE_SQL_RESPONSE ${file_path}_TRANSFERDB_SQL_RESPONSE ) ; do
                NUM_LINES=$(cat ${file_path}/$COMPONENT |wc -l)
                AVERAGE=$(average ${file_path}/$COMPONENT )
                MAX=$(max ${file_path}/$COMPONENT )
                PERCENTILE_50=$(percentile50 $NUM_LINES ${file_path}/$COMPONENT )
                PERCENTILE_90=$(percentile90 $NUM_LINES ${file_path}/$COMPONENT )
                PERCENTIME_99=$(percentile99 $NUM_LINES ${file_path}/$COMPONENT )
                echo $COMPONENT,$NUM_LINES,$AVERAGE,$PERCENTILE_50,$PERCENTILE_90,$PERCENTIME_99,$MAX  >> ${file_path}/${file_path}_sql_table
        done
        column -t -s, ${file_path}/${file_path}_sql_table | tee -a  ${file_path}/${file_path}_SQL.log

        rm -f  ${file_path}/${file_path}_all_sql_queries.log
        rm -f  ${file_path}/${file_path}_transferdb_sql_queries.log
        rm -f  ${file_path}/${file_path}_transferdb_sql_queries_response_times.csv
        rm -f  ${file_path}/${file_path}_chatdb_sql_queries.log
        rm -f  ${file_path}/${file_path}_chatdb_read_sql_queries.log
        rm -f  ${file_path}/${file_path}_chatdb_read_sql_queries_response_times.csv
        rm -f  ${file_path}/${file_path}_chatdb_write_sql_queries.log
        rm -f  ${file_path}/${file_path}_chatdb_write_sql_queries_response_times.csv
        rm -f  ${file_path}/${file_path}_CHATDB_READ_SQL_RESPONSE
        rm -f  ${file_path}/${file_path}_CHATDB_WRITE_SQL_RESPONSE
        rm -f  ${file_path}/${file_path}_TRANSFERDB_SQL_RESPONSE
        rm -f  ${file_path}/${file_path}_sql_table
}

checkInsights()
{
        zgrep -h "Response Sent" ${file_path}/pserver.*  > ${file_path}/${file_path}_all_responses.log
        zgrep -h LOGIC ${file_path}/pserver.* | grep "totals" > ${file_path}/${file_path}_all_logic_totals.log


        echo "" | tee -a ${file_path}/${file_path}_Insights.log
        echo "Top Insights:" | tee -a ${file_path}/${file_path}_Insights.log
                grep -h -q -m1 "GENERATE_INSIGHTS_FACTS" ${file_path}/${file_path}_all_logic_totals.log
                if [ ! $? -eq 0 ]; then
                        echo "inside if"
                        #using old version format
                        cat ${file_path}/${file_path}_all_responses.log |grep -oP '"insightId":"\w*' |cut -d'"' -f4 > ${file_path}/${file_path}_all_insights.log
                else
                        echo "inside else"
                        grep -oP "GENERATE_INSIGHTS_FACTS.\w*" ${file_path}/${file_path}_all_logic_totals.log |grep -v ":" | cut -d"." -f2 > ${file_path}/${file_path}_all_insights.log
                        NUM_OF_INSIGHTS=$(cat ${file_path}/${file_path}_all_insights.log |wc -l)
                        NUM_INSIGHTS_RESPONSES=$(grep -oP "NUM_OF_INSIGHTS_RESPONSE: \w*" ${file_path}/${file_path}_all_logic_totals.log |awk '{ sum+=$2 } END { print sum }')
                        NUM_INSIGHTS_TRIGGERED=$(grep -oP "NUM_OF_TRIGGERED_INSIGHTS: \w*" ${file_path}/${file_path}_all_logic_totals.log |awk '{ sum+=$2 } END { print sum }')
                        echo "Number of insights responses: $NUM_INSIGHTS_RESPONSES" | tee -a ${file_path}/${file_path}_Insights.log
                        echo "Number of insights triggered: $NUM_INSIGHTS_TRIGGERED" | tee -a ${file_path}/${file_path}_Insights.log
                        echo "" | tee -a ${file_path}/${file_path}_Insights.log
                        echo "Number of insights generated: $NUM_OF_INSIGHTS" | tee -a ${file_path}/${file_path}_Insights.log
                        cat ${file_path}/${file_path}_all_insights.log |sort |uniq -c |sort -n | tee -a ${file_path}/${file_path}_Insights.log
                fi

        rm -f  ${file_path}/${file_path}_all_responses.log
        rm -f ${file_path}/${file_path}_all_logic_totals.log
        rm -f ${file_path}/${file_path}_all_insights.log
}

checkTPS()
{
	echo "Date&Time,RequestId,PartyId" > ${file_path}/${file_path}_Request_received.csv
	zgrep -h 'Request received:' ${file_path}/pserver.* | sed s/\ \\[/,\\[/g | sed s/\|/,\|/g | sed s/\|{RequestId=//g | sed s/\ partyId:\ //g | sed s/-/\\//g | awk -F ',' '{print $1","$3","$9}' >> ${file_path}/${file_path}_Request_received.csv
}



if [ -z "$1" ]; then
        echo "please run this script as: ./parss_log.sh <pserver log files path> (for Exp. >./deleteOldLog.sh /usr/local/personetics/p_home/logs )"
        exit 1;
fi

file_path=$1
cd $PERSONETICS_HOME/logs/

#        TotalsAnalysis
AnalyzeErrors
AnalyzeSQLs
checkInsights
checkTPS
