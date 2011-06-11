#!/usr/bin/python



import spg.params as params
import spg.utils as utils
from spg.pool import ProcessPool, DBExecutor, DBInfo


import os, os.path, random
    
    
DB_TIMEOUT = 180

if __name__ == "__main__":
     process_id = int(os.environ()['PBS_JOBID'].split(".")[0])
     
    
     while True:
         
        rnd = DDInfo.normalising * random.random()
        pp = ProcessPool()
        pp.update_process_list()
        dbs = sorted( pp.dbs.keys() )
        curr_db = dbs.pop()
        ac = pp.dbs[ curr_db ].weight
        while rnd > ac:
            curr_db = dbs.pop()
            ac += pp.dbs[ curr_db ].weight
        
        selected = pp.dbs[ curr_db ]
        os.chdir(selected.path)
        
        executor = DBExecutor( selected.db_name, timeout = DB_TIMEOUT)
        
        if options.tree:
          executor.generate_tree( options.directory_vars )
        executor.next()
        running_id = executor.current_run_id 
        
        selected.update_master_db(process_id, running_id)
        
        
        executor.launch_process()
        
        
        
        





  
