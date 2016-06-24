#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 16:20:26 2011

@author: -
"""


from spg.runner import SPGRunningPool
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
                            default = 1 , help = "waiting time before refresh" )
 #   parser.add_option("--populate", type="int", action='store', dest="populate",
 #                           default = 50 , help = "how many processes to populate" )
#    parser.add_option("--queue-type", type='string', dest="queue",default="base",
#                            help = "type of queue: can be base, torque" )
#    parser.add_option("--skip-harvest", action='store_true', dest="skip_harvest",
#                            help = "do not harvest data" )
 #   parser.add_option("--skip-init", action='store_true', dest="skip_init",
 #                           help = "do not initialise files" )
    parser.add_option("--skip-sync", action='store_true', dest="skip_sync",
                            help = "do not sync dbs" )
    parser.add_option("--kill-workers", action='store', default = False, dest="kill_workers_after", type = "int",
                            help = "kills workers if no results after ARG harvests (sounds dictatorial, but does exactly this)" )
    parser.add_option("--workers-sleep", action='store', default = 5, dest="workers_sleep", type = "int",
                            help = "Workers sleeping time. If set to 0, the workers die after one run" )

    options, args = parser.parse_args()
    
#    newline_msg("@@@", "starting session: %s"% time.ctime(), stream = file_log)

    
    run_pool = SPGRunningPool(  )


    while True:
                number_of_jobs, = master_db.query_master_fetchone('SELECT max_jobs FROM queues WHERE name = "default"')

                run_pool.launch_workers( target_jobs = number_of_jobs)
                time.sleep(options.sleep)

        #         seeded_atoms_ac.append(pex.seeded_atoms )
        #
        #
        #
        # if not options.skip_harvest:
        #     inline_msg("INF", "harvest data..................",indent = 2)
        #     pex.harvest_atoms()
        #
        # newline_msg("INF", "syncing..................(s:%s - h:%d)"%(seeded_atoms_ac, pex.harvested_atoms), indent = 2)
        # newline_msg("INF", "syncing (s:%s - h:%d)"%(seeded_atoms_ac, pex.harvested_atoms), stream = file_log)
        #
        # if pex.harvested_atoms == 0:
        #     harvests_without_results += 1
        # else:
        #     harvests_without_results = 0
        #
        # if options.kill_workers_after and harvests_without_results > options.kill_workers_after :
        #      newline_msg("WRN", "killing workers", indent = 2)
        #      for (name, max_jobs) in ls_queues:
        #         all_queues[name].kill_workers()
        #      harvests_without_results = 0
        #
        # if not options.skip_sync:
        #     pex.synchronise_master()
        #
        # newline_msg("INF", "[%d] sleep %s"%(harvests_without_results, options.sleep),indent = 2)
        #
        # if options.sleep < 0:  sys.exit(0)
        #
