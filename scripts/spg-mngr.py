#!/usr/bin/python


import spg
import spg.params as params
import spg.utils as utils

import sqlite3 as sql
from subprocess import Popen, PIPE
import sys, os, os.path
import optparse

VAR_PATH = os.path.abspath(params.CONFIG_DIR+"/../var/spg")
BINARY_PATH = os.path.abspath(params.CONFIG_DIR+"/../bin")

DB_TIMEOUT = 120

######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################

def get_parameters(arg):
    ret = {}
    
    for i in arg.split(":"):
        [k,v] = i.split("=")
        ret[k] = v

    return ret
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################


def process_queue(cmd, name, params):
   # queue [add|remove|set|stop] QUEUE_NAME {params} 
   
   # "(id INTEGER PRIMARY KEY, name CHAR(64), max_jobs INTEGER, status CHAR(1))")
 
   #checks whether the queue is in the 
   cursor.execute( "SELECT id FROM queues WHERE name = '%s' "%name)
   queue = cursor.fetchone()
   if queue is not None:
       (queue, ) = queue
   
   
   if cmd == "add" and queue:
          utils.newline_msg("SKP", "add-error queue '%s' already exists"%name )
          sys.exit(2)
   elif cmd == "add" :
       try:
           max_jobs = params["jobs"]
       except:
           max_jobs = 1
           
       cursor.execute( "INSERT INTO queues (name, max_jobs, status) VALUES (?,?,?)",(name,  max_jobs, 'S') )
   elif not queue:
       utils.newline_msg("SKP", "delete-error queue does not '%s' exist"%name )
       sys.exit(2)
   elif cmd == "remove":
       cursor.execute( "DELETE FROM queues WHERE id = ?",(queue,) )
   elif cmd == "set":
           max_jobs = params["jobs"]
           cursor.execute( 'UPDATE queues SET max_jobs=? WHERE id = ?', ( max_jobs, queue ) )
   elif cmd == "start":
           cursor.execute( "UPDATE queues SET status = 'R' WHERE id = ?", (queue,) )
   elif cmd == "stop":
           cursor.execute( "UPDATE queues SET status = 'S' WHERE id = ?", (queue,) )
   
   else:
       utils.newline_msg("SYN", "command '%s' not understood"%cmd )
       sys.exit(1)
   connection.commit()
   
   
######################################################################################################


def process_db(cmd, name, params):
   # db [add|remove|set|start|stop|clean] DB_NAME {params} 
   
#    cursor.execute("CREATE TABLE IF NOT EXISTS dbs "
#                   "(id INTEGER PRIMARY KEY, full_name CHAR(256), path CHAR(256), db_name CHAR(256), status CHAR(1), "
#                   " total_combinations INTEGER, done_combinations INTEGER, running_combinations INTEGER, error_combinations INTEGER,  "
#                   " weight FLOAT)")
#    
   if os.path.exists( name ):
       full_name = os.path.realpath(name)
   else:
       utils.newline_msg("PTH", "database '%s' does not exist"%name)
       sys.exit(2)
   
   path, db_name = os.path.split(full_name)
   
   cursor.execute( "SELECT id FROM dbs WHERE full_name = '%s' "%full_name)
   db_id = cursor.fetchone()
   if db_id is not None:
       (db_id, ) = db_id

   if cmd == "add" and db_id:
          utils.newline_msg("SKP", "add-error db '%s' already exists"%full_name )
          sys.exit(2)
   elif cmd == "add" :
       try:
           weight = params["weight"]
       except:
           weight = 1.
           
       conn2 = sql.connect(full_name)
       cur2 = conn2.cursor()
                #:::~    'N': not run yet
                #:::~    'R': running
                #:::~    'D': successfully run (done)
                #:::~    'E': run but with non-zero error code


       d_status = {"E":0,"R":0,"D":0}
       cur2.execute("SELECT COUNT(*) FROM run_status ;")
       (n_all, ) = cur2.fetchone()
       d_status["all"] = n_all
       cur2.execute("SELECT status, COUNT(*) FROM run_status GROUP BY status;")
       for k,v in cur2:
           d_status[k] = v
       cursor.execute( "INSERT INTO dbs (full_name, path, db_name, status, total_combinations, done_combinations, running_combinations, error_combinations,weight) VALUES (?,?,?,?,?,?,?,?,?)",(full_name, path, db_name , 'R', d_status["all"], d_status['D'],d_status['R'],d_status['E'], weight) )
   elif not db_id:
       utils.newline_msg("SKP", "db '%s' is not registered"%full_name )
       sys.exit(2)
   elif cmd == "remove":
       cursor.execute( "DELETE FROM dbs WHERE id = ?",(db_id,) )
   elif cmd == "set":
#       try:
           weight = params["weight"]
           cursor.execute( 'UPDATE dbs SET weight=? WHERE id = ?', ( weight, db_id ) )
#       except:
#           pass
   elif cmd == "start":
           cursor.execute( "UPDATE dbs SET status = 'R' WHERE id = ?", (db_id,) )
   elif cmd == "stop":
           cursor.execute( "UPDATE dbs SET status = 'S' WHERE id = ?", (db_id,) )
   elif cmd == "clean":
           cursor.execute( "DELETE FROM dbs WHERE status = 'D'")
   else:
       utils.newline_msg("SYN", "command '%s' not understood"%cmd )
       sys.exit(1)
   connection.commit()
   
   
######################################################################################################



dict_functions = { "db":process_db, "queue": process_queue }

def execute_command( arguments ):
    if len( arguments ) <3 :
        return
        
    full_command = arguments[0]

    cmd = arguments[1] 
    name = arguments[2]
    if len(arguments) > 3 :
        params = get_parameters( arguments[3] )
    else:
        params = {}

    f = dict_functions[ full_command ] 
    f(cmd, name, params)



if __name__ == "__main__":
    
    ##################################################################################################
    #### :::~ (begin) DB connection 
    
    connection = sql.connect("%s/running.sqlite"%VAR_PATH)
    cursor = connection.cursor()
    
    #:::~ status can be either 
    #:::~    'S': stopped
    #:::~    'R': running
    #:::~    'F': finished
    cursor.execute("CREATE TABLE IF NOT EXISTS dbs "
                   "(id INTEGER PRIMARY KEY, full_name CHAR(256), path CHAR(256), db_name CHAR(256), status CHAR(1), "
                   " total_combinations INTEGER, done_combinations INTEGER, running_combinations INTEGER, error_combinations INTEGER,  "
                   " weight FLOAT)")
    
    #:::~ status can be either 
    #:::~    'S': stopped
    #:::~    'R': running
    cursor.execute("CREATE TABLE IF NOT EXISTS queues "
                   "(id INTEGER PRIMARY KEY, name CHAR(64), max_jobs INTEGER, status CHAR(1))")


    cursor.execute("CREATE TABLE IF NOT EXISTS running "
                   "(id INTEGER PRIMARY KEY, jobid CHAR(64), id_dbs INTEGER, id_params INTEGER)")




    connection.commit()
    
    #### :::~ ( end ) DB connection 
    ##################################################################################################


    parser = optparse.OptionParser(usage = "usage: %prog [options] CMD VERB NAME {params}\n"
                                      "commands [VERBs] NAME {params}: \n"
                                      "   queue [add|remove|set*|start|stop] QUEUE_NAME {params} \n"
                                      "        params :: jobs=NJOBS\n"
                                      "   db    [add|remove|set*|start|stop|clean] DB_NAME {params} \n"
                                      "        params :: weight=WEIGHT[1] \n"
                                      "VERBs with * indicate that accept params"
                                  )

#    parser.add_option("--tree", action='store_true', dest="tree",
#                       help = "whether to create a directory tree with the key-value pairs" )
#
#    parser.add_option("-d","--directory-var", action='store', type = "string", dest="directory_vars",
#                       default = False, help = "which variables to store as directories, only if tree" )

    options, args = parser.parse_args()

    execute_command(args)
