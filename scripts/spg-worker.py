#!/usr/bin/python


from spg.parameter import ParameterAtomExecutor
from spg.queue import get_queueing_system
import spg.queue.torque as torque
 
import spg.utils as utils
from spg import VAR_PATH 



import optparse
import os, time, sys
    
EXE_TIMEOUT = 60*10 # in seconds

#process_id = int(os.environ['PBS_JOBID'].split(".")[0])
#this_queue = os.environ['PBS_QUEUE']
#process_id = 12345
#this_queue = "default"


def parse_environment():
  ret = {}
  for k in [ k for k in os.environ if k[0:4] == "SPG_"]:
    ret[k[4:]] = os.environ[k]

  return ret


if __name__ == "__main__":
#     parser = optparse.OptionParser(usage = "usage: %prog [options] project_id1 ")
#     parser.add_option("--sleep", type="int", action='store', dest="sleep",
#                            default = 5 , help = "waiting time in case of a lack of new parameters" )
#     parser.add_option("--queue", type="string", action='store', dest="queue",
#                            default = "default" , help = "name of the queue this worker lives in" )
#     parser.add_option("--type", type="string", action='store', dest="type",
#                            default = None , help = "the type of the queue - use 'base' for stand-alone based" )
#
#     options, args = parser.parse_args()
#     if not options.type:
#       queue_type = get_queueing_system()
#     else:
#       queue_type = options.type
#
#     if queue_type == "base":
#         queue_name = options.queue
#     elif queue_type == "torque":
#         queue_name =  torque.get_queue_name()
#     print "queue_type =",queue_type, " ///// queue_name",queue_name

     env = parse_environment( )
     try:
         queue_type = env[ "QUEUE_TYPE" ]
     except:
         utils.newline_msg("WRN", "QUEUE_TYPE could not be parsed, using 'base'")
         queue_name = 'base'
     
     try:
         queue_name = env[ "QUEUE_NAME" ]
     except:
         utils.newline_msg("WRN", "QUEUE_NAME could not be parsed, using 'default'")
         queue_name = 'default'

     try:
         sleep_time = int( env[ "WORKERS_SLEEP" ] )
     except:
         utils.newline_msg("WRN", "WORKERS_SLEEP could not be parsed, using '5'")
         sleep_time = 5




     while True:
        try:
          next_file = min ( os.listdir("%s/queue/%s"%(VAR_PATH,queue_name) ) )
          pex = ParameterAtomExecutor(next_file)
          pex.load("queue/%s"%(queue_name) )
        except ValueError:
          utils.newline_msg("WRN", "no newly pickled elements")
          
          time.sleep(5)
          continue
        except:
          utils.newline_msg("WRN", "file already taken")
          time.sleep(sleep_time)
          continue
#        utils.newline_msg("INF","%s -- %s -> %s "%(pex.path, pex.full_db_name, pex.values))
#       utils.newline_msg("INF","<<<<< %s - %s - %s "%(pex.in_name , pex.current_run_id, pex.current_valuesset_id))
        pex.launch_process("%s.dat"%next_file)
        pex.dump()
        
        if sleep_time == 0:
            sys.exit(0)
