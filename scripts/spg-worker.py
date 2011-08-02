#!/usr/bin/python

import optparse


import spg.params as params
import spg.utils as utils
from spg.pool import ParameterAtomExecutor
from spg import VAR_PATH 




import os, time
    
EXE_TIMEOUT = 60*10 # in seconds

#process_id = int(os.environ['PBS_JOBID'].split(".")[0])
#this_queue = os.environ['PBS_QUEUE']
#process_id = 12345
#this_queue = "default"




if __name__ == "__main__":
     parser = optparse.OptionParser(usage = "usage: %prog [options] project_id1 ")
     parser.add_option("--sleep", type="int", action='store', dest="sleep",
                            default = 120 , help = "waiting time in case of a lack of new parameters" )

     options, args = parser.parse_args()
     while True:
        try:
          next_file = min ( os.listdir("%s/queued"%(VAR_PATH) ) )
          pex = ParameterAtomExecutor(next_file)
          pex.load()
          
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

