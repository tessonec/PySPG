#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 16:20:26 2011

@author: -
"""
import optparse
# logica del programa
#   leer la cantidad de procesos a ejecutar de la DB central
#   si este numero es menor (para alguna cola) que el que esta corriendo. lanzar los que faltan
#   si este numero es mayor (para alguna cola) que el que esta corriendo. matar los que sobran
#   en este ultimo caso, limpiar la DB central
  #print cmd
  
import time, sys

from spg.pool import ProcessPool, DataExchanger
from spg.utils import newline_msg, inline_msg



if __name__ == "__main__":
    parser = optparse.OptionParser(usage = "usage: %prog [options] project_id1 ")
    parser.add_option("--sleep", type="int", action='store', dest="sleep",
                            default = 120 , help = "waiting time before refresh" )
    parser.add_option("--populate", type="int", action='store', dest="populate",
                            default = 50 , help = "how many processes to populate" )
    parser.add_option("--skip-queue", action='store_true', dest="skip_queue",
                            help = "do not process queues" )
    parser.add_option("--skip-harvest", action='store_true', dest="skip_harvest",
                            help = "do not harvest data" )
    parser.add_option("--skip-init", action='store_true', dest="skip_init",
                            help = "do not initialise files" )
    parser.add_option("--skip-sync", action='store_true', dest="skip_sync",
                            help = "do not sync dbs" )

    options, args = parser.parse_args()
    pp = ProcessPool()
    pp.waiting_processes = options.populate
    pp.update_worker_info()
    pex = DataExchanger( pp.db_master, pp.cur_master )

    while True:
       inline_msg("INF", "awaken @%s.........................."%time.ctime())
       
       inline_msg("INF", "process pool.........................",indent = 2)
       
       pp.update_worker_info()
       if not options.skip_queue :
          for i_j in pp.queues:
              inline_msg("INF", "%s - queue.normalise_processes()"%pp.queues[i_j].name,indent = 4)
              pp.queues[i_j].normalise_processes()

       pex.update_dbs()

       inline_msg("INF", "populate/harvest data.......................",indent = 2)
       if not options.skip_init:
  #       newline_msg("INF", "initialise_infiles()")
         pex.initialise_infiles()
#       newline_msg("INF", "harvesting_data()")
       if not options.skip_harvest:
         pex.harvest_data()

       if not options.skip_sync:
         inline_msg("INF", "syncing..........(s:%d - h:%d)..................."%(pex.seeded_atoms, pex.harvested_atoms), indent = 2)
         pex.synchronise_master()

       newline_msg("INF", "sleep %s"%options.sleep,indent = 2)
       if options.sleep < 0:
           sys.exit(0)
       time.sleep(options.sleep)
