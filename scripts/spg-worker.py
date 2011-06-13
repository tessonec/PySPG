#!/usr/bin/python



import spg.params as params
import spg.utils as utils
from spg.pool import ProcessPool, DBExecutor, DBInfo


import os, os.path, random
    
    
DB_TIMEOUT = 180

process_id = int(os.environ['PBS_JOBID'].split(".")[0])
this_queue = os.environ['PBS_QUEUE']
#process_id = 12345
#this_queue = "default"

def pick_db(pp):
    db_fits = False
    while not db_fits :
        rnd = DBInfo.normalising * random.random()
        dbs = sorted( pp.dbs.keys() )
        curr_db = dbs.pop()
        ac = pp.dbs[ curr_db ].weight
 #       print DBInfo.normalising , rnd, dbs, pp.dbs[ curr_db ].full_name, pp.dbs[ curr_db ].weight
        while rnd > ac:
            curr_db = dbs.pop()
            ac += pp.dbs[ curr_db ].weight
        res = pp.db_master.select_fetchone("SELECT queue FROM dbs WHERE id = ?",(pp.dbs[ curr_db ].id,))
        (res,) = res
#        print res
        if res == 'any' or this_queue in res.split(","):
            db_fits = True
    return  pp.dbs[ curr_db ]


if __name__ == "__main__":

     while True:
        pp = ProcessPool()
        pp.update_worker_info()

        selected = pick_db(pp)
        os.chdir(selected.path)

        executor = DBExecutor( selected.db_name, timeout = DB_TIMEOUT)
#        print executor.create_trees()
        if executor.create_trees():
          executor.generate_tree( )
        try:
          executor.next()
        except StopIteration:
          pp.db_master.execute('UPDATE dbs SET status = "D" where id = ?',(selected.id,))
 #         pp.conn_master.commit()
          continue
        running_id = executor.current_run_id 
        selected.set_db( pp.conn_master )
        selected.update_master_db(process_id, running_id)
        
  #      print process_id, selected.full_name, selected.weight
#        executor.launch_process()
        pp.update_db_info( selected.full_name )





  
