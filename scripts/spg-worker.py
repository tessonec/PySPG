#!/usr/bin/python



import spg.params as params
import spg.utils as utils
from spg.pool import ProcessPool, DBExecutor, DBInfo


import os, os.path, random
    
    
DB_TIMEOUT = 180

process_id = int(os.environ()['PBS_JOBID'].split(".")[0])
this_queue = int(os.environ()['PBS_QUEUE'])


def pick_db(pp):
    db_fits = False
    while not db_fits :
        rnd = DBInfo.normalising * random.random()
        dbs = sorted( pp.dbs.keys() )
        curr_db = dbs.pop()
        ac = pp.dbs[ curr_db ].weight
        while rnd > ac:
            curr_db = dbs.pop()
            ac += pp.dbs[ curr_db ].weight
        res = pp.curr_cur.execute("SELECT queue FROM dbs WHERE id = ?",(pp.dbs[ curr_db ].id,))
        (res, )= res
        if res == 'any' or this_queue in res.split(","):
            db_fits = True
    return  pp.dbs[ curr_db ]
        

if __name__ == "__main__":
     
    
     while True:
         
        pp = ProcessPool()
        pp.update_process_list()
        
        selected = pick_db(pp)
        
        os.chdir(selected.path)
        
        executor = DBExecutor( selected.db_name, timeout = DB_TIMEOUT)
        
        if executor.create_trees():
          executor.generate_tree( )
        executor.next()
        running_id = executor.current_run_id 
        
        selected.update_master_db(process_id, running_id)
        
        
        executor.launch_process()
        
        
        
        





  
