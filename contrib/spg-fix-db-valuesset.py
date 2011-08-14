#!/usr/bin/python


import sqlite3 as sql
import sys, shutil

fname = sys.argv[1]

shutil.copyfile(fname, "%s.backup"%fname)

connection = sql.connect( fname )
cursor = connection.cursor()


res = cursor.execute("PRAGMA table_info(results)")

output_columns = [ i[1] for i in res ]
output_columns = output_columns[2:]

cursor.execute( "BEGIN;" )
sql_command = "CREATE TEMP TABLE temp_results AS SELECT r.id, rs.values_set_id, %s FROM results AS r, run_status AS rs WHERE rs.id = r.values_set_id ;"%( ", ".join([ "r.%s"%i for i in output_columns]) )
print sql_command
cursor.execute( sql_command )
sql_command = "DROP TABLE results;"
cursor.execute( sql_command )
sql_command = "CREATE TABLE results AS SELECT * FROM temp_results ;"
cursor.execute( sql_command )
sql_command = "DROP TABLE temp_results;"
cursor.execute( sql_command )

connection.commit()



#echo "insert into results select * from temp_table;" >> cmd.sql
#echo "drop table temp_table;" >> cmd.sql
#echo "commit;" >> cmd.sql

