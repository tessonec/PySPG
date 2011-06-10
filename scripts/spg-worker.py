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
        executor.launch_process()
        
        
        
        





  
 
if __name__ == "__main__":

    parser = optparse.OptionParser(usage = "usage: %prog [options] project_id1 project_id2 project_id3... ")
    parser.add_option("--timeout", type="int", action='store', dest="timeout",
                            default = 60 , help = "timeout for database connection" )

    parser.add_option("--tree", action='store_true', dest="tree",
                       help = "whether to create a directory tree with the key-value pairs" )

    parser.add_option("-d","--directory-var", action='store', type = "string", dest="directory_vars",
                       default = False, help = "which variables to store as directories, only if tree" )

    options, args = parser.parse_args()
    
    if len(args) == 0:
        args = ["results.sqlite"]
    
    for i_arg in args:
      if ".sqlite" not in i_arg:
          db_name = i_arg.replace("parameters","").replace(".dat","")
          db_name = "results%s.sqlite"%db_name
      else:
          db_name = i_arg



      for values in executor:
          
          
          #      parser.init_db()
          #      parser.fill_status(repeat = options.repeat )

