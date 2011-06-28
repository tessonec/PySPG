#!/usr/bin/python


#import spg
import spg.params as params
import spg.utils as utils
from spg.pool import ProcessPool


# import sqlite3 as sql
#from subprocess import Popen, PIPE
import sys, os, os.path
import optparse
import sqlite3 as sql


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
   #print cmd, name, params
   queue = cur_master.execute( "SELECT id FROM queues WHERE name = '%s' "%name).fetchone()
   queue_exists = False
   if queue is not None:
       queue_exists = True
       (queue_id,) = queue
       
#   if cmd == "add" and queue:
#          utils.newline_msg("SKP", "add-error queue '%s' already exists"%name )
#          sys.exit(2)
   if cmd == "add"  :
       if queue_exists:
          utils.newline_msg("SKP", "add-error queue '%s' already exists"%name )
          sys.exit(2)
           
       try:
           max_jobs = params["jobs"]
       except:
           max_jobs = 1
       cur_master.execute( "INSERT INTO queues (name, max_jobs, status) VALUES (?,?,?)",(name,  max_jobs, 'S') )
   elif not queue:
       utils.newline_msg("SKP", "delete-error queue does not '%s' exist"%name )
       sys.exit(2)
   elif cmd == "remove":
       cur_master.execute( "DELETE FROM queues WHERE id = ?",(queue_id ,) )
   elif cmd == "set":
           max_jobs = params["jobs"]
           cur_master.execute( 'UPDATE queues SET max_jobs=? WHERE id = ?', ( max_jobs, queue_id  ) )
   elif cmd == "start":
           cur_master.execute( "UPDATE queues SET status = 'R' WHERE id = ?", (queue_id ,) )
   elif cmd == "stop":
           cur_master.execute( "UPDATE queues SET status = 'S' WHERE id = ?", (queue_id ,) )
   
   else:
       utils.newline_msg("SYN", "command '%s' not understood"%cmd )
       sys.exit(1)
   db_master.commit()
######################################################################################################


def process_db(cmd, name, params):
   # db [add|remove|set|start|stop|clean] DB_NAME {params} 
   
#    cursor.execute("CREATE TABLE IF NOT EXISTS dbs "
#                   "(id INTEGER PRIMARY KEY, full_name CHAR(256), path CHAR(256), db_name CHAR(256), status CHAR(1), "
#                   " total_combinations INTEGER, done_combinations INTEGER, running_combinations INTEGER, error_combinations INTEGER,  "
#                   " weight FLOAT)")
#    
   full_name = os.path.realpath(name)
   
   path, db_name = os.path.split(full_name)
   
   db_id = cur_master.execute( "SELECT id FROM dbs WHERE full_name = '%s' "%full_name).fetchone()
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
       try:
           queue = params["queue"]
       except:
           queue = 'any'
       if os.path.exists( name ):
          full_name = os.path.realpath(name)
       else:
          utils.newline_msg("PTH", "database '%s' does not exist"%name)
          sys.exit(2)
          
       conn2 = sql.connect(full_name)
       cur2 = conn2.cursor()
       #:::~    'N': not run yet
       #:::~    'R': running
       #:::~    'D': successfully run (done)
       #:::~    'E': run but with non-zero error code

       d_status = {"E":0,"R":0,"D":0}
       (n_all, ) = cur2.execute("SELECT COUNT(*) FROM run_status ;").fetchone()
       (total_sov, ) = cur2.execute("SELECT COUNT(*) FROM values_set ;").fetchone()
       
       cur2.execute("SELECT status, COUNT(*) FROM run_status GROUP BY status;")
       for k,v in cur2:
           d_status[k] = v
       cur_master.execute( "INSERT INTO dbs (full_name, path, db_name, status, total_values_set, total_combinations, done_combinations, running_combinations, error_combinations,weight,queue) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(full_name, path, db_name , 'R', total_sov, n_all, d_status['D'],d_status['R'],d_status['E'], weight, queue) )
   elif not db_id:
       utils.newline_msg("SKP", "db '%s' is not registered"%full_name )
       sys.exit(2)
   elif cmd == "remove":
       cur_master.execute( "DELETE FROM dbs WHERE id = ?",(db_id,) )
   elif cmd == "set":
        if 'weight' in params.keys():
            cur_master.execute( 'UPDATE dbs SET weight=? WHERE id = ?', ( params["weight"], db_id ) )
        if 'queue' in params.keys():
            cur_master.execute( 'UPDATE dbs SET queue=? WHERE id = ?', ( params["queue"], db_id ) )
   elif cmd == "start":
        cur_master.execute( "UPDATE dbs SET status = 'R' WHERE id = ?", (db_id,) )
   elif cmd == "stop":
        cur_master.execute( "UPDATE dbs SET status = 'S' WHERE id = ?", (db_id,) )
   elif cmd == "clean":
        cur_master.execute( "DELETE FROM dbs WHERE status = 'D'")
   else:
        utils.newline_msg("SYN", "command '%s' not understood"%cmd )
        sys.exit(1)
   db_master.commit()

######################################################################################################


def get_stats(cmd, name, params):
   # queue [add|remove|set|stop] QUEUE_NAME {params} 
   pp = ProcessPool()
   if cmd == "queue":
       pp.update_worker_info()
       for q in pp.queues:
           print "queue: '%s' -- running jobs: %d -- maximum: %s"%(q, len(pp.queues[q].processes), pp.queues[q].jobs)
   # "(id INTEGER PRIMARY KEY, name CHAR(64), max_jobs INTEGER, status CHAR(1))")
   elif cmd == "db":
       res = pp.cur_master.execute("SELECT full_name, status, total_combinations, done_combinations, "
                        "running_combinations, error_combinations FROM dbs")
#       print res
       for full_name, status, total, done, running, error in res:
           frac_done = float(done)/float(total)
           frac_running = float(running)/float(total)
           frac_error = float(error)/float(total)
           print "db: '%s' [%s] TOT: %d - D: %d (%.5f) - R: %d (%.5f) -- E: %d (%.5f)"%(os.path.relpath(full_name,"/home/tessonec"), status, total, done, frac_done, running, frac_running, error, frac_error) 
###    (id INTEGER PRIMARY KEY, full_name CHAR(256), path CHAR(256), 
###     db_name CHAR(256), status CHAR(1), 
###     total_combinations INTEGER, done_combinations INTEGER, 
###     running_combinations INTEGER, error_combinations INTEGER, 
###     weight FLOAT)

   elif cmd == "process":
       res = pp.cur_master.execute("SELECT dbs.full_name, dbs.weight, COUNT(*), queue FROM dbs, running WHERE dbs.id = running.dbs_id GROUP BY running.dbs_id ")
       for fn, w, c, q in res:
           print "db: '%s' -- weight=%f -- running proc: %d -- queueable in: '%s'"%(fn,w,c,q)
   else:
       utils.newline_msg("SYN", "command '%s' not understood"%cmd )
       sys.exit(1)


dict_functions = { "db":process_db, "queue": process_queue, "stat": get_stats }

def execute_command( arguments ):
#    if len( arguments ) <3 :
#        return
    name = None
    params = {}
    
    full_command = arguments[0]

    cmd = arguments[1] 
    if len(arguments) > 2 :
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
    
    db_master = sql.connect("%s/running.sqlite"%VAR_PATH)
    cur_master = db_master.cursor()
    
    #:::~ status can be either 
    #:::~    'S': stopped
    #:::~    'R': running
    #:::~    'F': finished
    cur_master.execute("CREATE TABLE IF NOT EXISTS dbs "
                   "(id INTEGER PRIMARY KEY, full_name CHAR(256), path CHAR(256), db_name CHAR(256), status CHAR(1), total_values_set INTEGER, "
                   " total_combinations INTEGER, done_combinations INTEGER, running_combinations INTEGER, error_combinations INTEGER, "
                   " weight FLOAT, queue CHAR(64))")
    
    #:::~ status can be either 
    #:::~    'S': stopped
    #:::~    'R': running
    cur_master.execute("CREATE TABLE IF NOT EXISTS queues "
                   "(id INTEGER PRIMARY KEY, name CHAR(64), max_jobs INTEGER, status CHAR(1))")


    cur_master.execute("CREATE TABLE IF NOT EXISTS running "
                   "(id INTEGER PRIMARY KEY, job_id CHAR(64), dbs_id INTEGER, params_id INTEGER)")

    #### :::~ ( end ) DB connection 
    ##################################################################################################


    parser = optparse.OptionParser(usage = "usage: %prog [options] CMD VERB NAME {params}\n"
                                      "commands [VERBs] NAME {params}: \n"
                                      "   queue [add|remove|set*|start|stop] QUEUE_NAME {params} \n"
                                      "        params :: jobs=NJOBS\n"
                                      "   db    [add|remove|set*|start|stop|clean|clean-all|reset] DB_NAME {params} \n"
                                      "        params :: weight=WEIGHT[1] queue=STR[any] \n"
                                      "   stat  [queue|db] \n"
                                      "VERBs with * indicate that accept params"
                                  )

#    parser.add_option("--tree", action='store_true', dest="tree",
#                       help = "whether to create a directory tree with the key-value pairs" )
#
#    parser.add_option("-d","--directory-var", action='store', type = "string", dest="directory_vars",
#                       default = False, help = "which variables to store as directories, only if tree" )

    options, args = parser.parse_args()

    execute_command(args)
