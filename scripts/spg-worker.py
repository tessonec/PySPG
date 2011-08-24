#!/usr/bin/python


from spg.parameter import ParameterAtomExecutor
from spg.queue import get_queueing_system
import spg.queue.torque as torque
 
import spg.utils as utils
from spg import VAR_PATH 



import optparse
import os, time
    
EXE_TIMEOUT = 60*10 # in seconds

#process_id = int(os.environ['PBS_JOBID'].split(".")[0])
#this_queue = os.environ['PBS_QUEUE']
#process_id = 12345
#this_queue = "default"




if __name__ == "__main__":
     parser = optparse.OptionParser(usage = "usage: %prog [options] project_id1 ")
     parser.add_option("--sleep", type="int", action='store', dest="sleep",
                            default = 5 , help = "waiting time in case of a lack of new parameters" )
     parser.add_option("--queue", type="string", action='store', dest="queue",
                            default = "default" , help = "name of the queue this worker lives in" )

     options, args = parser.parse_args()
     queue_type = get_queueing_system()

     

     if queue_type == "base":
         queue_name = opt_queue
     elif queue_type == "torque":
         queue_name =  torque.get_queue_name()
     print "queue_type =",queue_type, " ///// queue_name",queue_name
     while True:
        try:
          next_file = min ( os.listdir("%s/queue/%s"%(VAR_PATH,queue_name) ) )
          pex = ParameterAtomExecutor(next_file)
          pex.load("queue/%s"%(queue_name) )
          
        except ValueError:
          utils.newline_msg("WRN", "no newly pickled elements")
          time.sleep(options.sleep)
          continue
        except:
          utils.newline_msg("WRN", "file already taken")
          time.sleep(options.sleep)
          continue
#        utils.newline_msg("INF","%s -- %s -> %s "%(pex.path, pex.full_db_name, pex.values))
#       utils.newline_msg("INF","<<<<< %s - %s - %s "%(pex.in_name , pex.current_run_id, pex.current_valuesset_id))
        pex.launch_process("%s.dat"%next_file)
        pex.dump()

