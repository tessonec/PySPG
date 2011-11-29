#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 16:20:26 2011

@author: -
"""


from spg.master import DataExchanger
from spg.queue import Queue, TorqueQueue, set_queueing_system
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
    
    file_log = open("spg-master.log","aw")
    
    set_queueing_system( options.queue )
    
    print >> file_log,  "starting session:  ", time.ctime()
    print >> file_log,  "queueing system: %s"%options.queue
    
    
    pex = DataExchanger(  )
    pex.max_atoms_to_seed = options.populate

    all_queues = {}
    while True:
        ls_queues  = pex.execute_query("SELECT name, max_jobs FROM queues WHERE status = 'R'")
        tbr_queues = set( all_queues.keys() ) - set( [i for (i,j) in ls_queues] )
        for q in tbr_queues:
            all_queues[q].kill_processes()
        seeded_atoms_ac = []
        for (name, max_jobs) in ls_queues:
            if not all_queues.has_key(name):
                newline_msg("INF", "initialising queue '%s'"%name,indent = 2)
                print >> file_log,  "initialising queue: %s [max_jobs: %s]"%(name, max_jobs)
                
                if options.queue == "torque":
                    all_queues[name] = TorqueQueue(name, max_jobs)
                else:
                    all_queues[name] = Queue(name, max_jobs)
            else:
                all_queues[name].jobs = max_jobs

            all_queues[name].update_worker_info()
            worker_diff  = all_queues[name].normalise_workers()
            if worker_diff > 0 :
                print >> file_log,  "queue: %s seeded-killed = %d]"%(name, worker_diff)
                
            inline_msg("INF", "populate data for '%s'."%name,indent = 2)
            if not options.skip_init:
                pex.seed_atoms( name )
                seeded_atoms_ac.append(pex.seeded_atoms )
         
        if not options.skip_harvest:
            inline_msg("INF", "harvest data..................",indent = 2)

            pex.harvest_atoms()
    
        inline_msg("INF", "syncing..................(s:%s - h:%d)"%(seeded_atoms_ac, pex.harvested_atoms), indent = 2)
        print >> file_log, "atoms: seeded= %s - harvested= %d"%(seeded_atoms_ac, pex.harvested_atoms)
        file_log.flush()
        
        if not options.skip_sync:
            pex.synchronise_master()
      
        newline_msg("INF", "sleep %s"%options.sleep,indent = 2)
        if options.sleep < 0:  sys.exit(0)
        time.sleep(options.sleep)
