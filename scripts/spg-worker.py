#!/usr/bin/python



import spg.params as params
import spg.utils as utils
from spg.pool import ProcessPool, PickledExecutor, DBInfo, VAR_PATH 




import os, time
    
  #  
#DB_TIMEOUT = 180

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
          time.sleep(10*60)

        pex = PickledExecutor(next_file)
        pex.launch_process()
        pex.store()


