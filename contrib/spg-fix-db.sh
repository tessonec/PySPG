#!/bin/bash



echo "begin; " > cmd.sql
echo "create temp table temp_table as select * from results; " >> cmd.sql
echo "drop table results; " >> cmd.sql

sqlite3 ${1} .schema | grep results | sed  's/variables_id/values_set_id/g' >> cmd.sql





echo "insert into results select * from temp_table;" >> cmd.sql
echo "drop table temp_table;" >> cmd.sql
echo "commit;" >> cmd.sql

cp ${1} ${1}.backup

sqlite3 ${1} < cmd.sql


