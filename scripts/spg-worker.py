#!/usr/bin/python



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

     while True:
        try:
          next_file = min ( os.listdir("%s/queued"%(VAR_PATH) ) )
          
        except ValueError:
          utils.newline_msg("WRN", "no newly pickled elements")
          time.sleep(EXE_TIMEOUT)

        pex = ParameterAtomExecutor(next_file)
        pex.load()
#        utils.newline_msg("INF","%s -- %s -> %s "%(pex.path, pex.full_db_name, pex.values))
#       utils.newline_msg("INF","<<<<< %s - %s - %s "%(pex.in_name , pex.current_run_id, pex.current_valuesset_id))
        pex.launch_process("%s.dat"%next_file)
        pex.dump()

