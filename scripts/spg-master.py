#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 16:20:26 2011

@author: -
"""


from spg.master import DataExchanger
from spg.pool import Queue, TorqueQueue
from spg.utils import newline_msg, inline_msg


# logica del programa
#   leer la cantidad de procesos a ejecutar de la DB central
#   si este numero es menor (para alguna cola) que el que esta corriendo. lanzar los que faltan
#   si este numero es mayor (para alguna cola) que el que esta corriendo. matar los que sobran
#   en este ultimo caso, limpiar la DB central
  #print cmd
  
import time, sys
import optparse



if __name__ == "__main__":
    parser = optparse.OptionParser(usage = "usage: %prog [options] project_id1 ")
    parser.add_option("--sleep", type="int", action='store', dest="sleep",
                            default = 120 , help = "waiting time before refresh" )
    parser.add_option("--populate", type="int", action='store', dest="populate",
                            default = 50 , help = "how many processes to populate" )
    parser.add_option("--queue-type", type='string', dest="queue",default="base",
                            help = "type of queue: can be base, torque" )
    parser.add_option("--skip-harvest", action='store_true', dest="skip_harvest",
                            help = "do not harvest data" )
    parser.add_option("--skip-init", action='store_true', dest="skip_init",
                            help = "do not initialise files" )
    parser.add_option("--skip-sync", action='store_true', dest="skip_sync",
                            help = "do not sync dbs" )

    options, args = parser.parse_args()
    pex = DataExchanger(  )
    pex.waiting_processes = options.populate

    all_queues = {}
    while True:
        ls_queues  = pex.execute_query("SELECT name, max_jobs FROM queues WHERE status = 'R'")
#        inline_msg("INF", "awaken @%s.........................."%time.ctime())
        print ls_queues
        tbr_queues = set( all_queues.keys() ) - set( [i for (i,j) in ls_queues] )
        for q in tbr_queues:
            all_queues[q].kill_processes()

        for (name, max_jobs) in ls_queues:
 #           inline_msg("INF", "process queue '%s'"%name,indent = 2)
            #pp = ProcessPool()
            #pp.update_worker_info()
            if not all_queues.has_key(name):
                newline_msg("INF", "creating queue '%s'"%name,indent = 2)
                
                if options.queue == "torque":
                    all_queues[name] = TorqueQueue(name, max_jobs)
                else:
                    all_queues[name] = Queue(name, max_jobs)
            else:
                all_queues[name].jobs = max_jobs
            
            newline_msg("INF", "update_worker.",indent = 2)
            all_queues[name].update_worker_info()
#            inline_msg("INF", "%s - queue.normalise_processes()"%pp.queues[i_j].name,indent = 4)
            newline_msg("INF", "normalise.",indent = 2)
            all_queues[name].normalise_workers()
    
#            pex.update_dbs()
    
            newline_msg("INF", "populate/harvest data.",indent = 2)
            if not options.skip_init:
      #       newline_msg("INF", "initialise_infiles()")
                pex.seed_atoms( name )
    #       newline_msg("INF", "harvesting_data()")
        if not options.skip_harvest:
            pex.harvest_atoms()
    
        if not options.skip_sync:
            inline_msg("INF", "syncing..........(s:%d - h:%d)..................."%(pex.seeded_atoms, pex.harvested_atoms), indent = 2)
            pex.synchronise_master()
    
        newline_msg("INF", "sleep %s"%options.sleep,indent = 2)
        if options.sleep < 0:  sys.exit(0)
        time.sleep(options.sleep)
