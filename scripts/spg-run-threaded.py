#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 16:20:26 2011

@author: -
"""


from spg.runner import SPGRunningPool
import spg.utils as utils


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

    parser.add_option("--test-run", action='store_true', dest="test_run",
                      help="runs once and preserves the temporary files")

    options, args = parser.parse_args()

    
    run_pool = SPGRunningPool(  )

    run_pool.master_db.test_run = options.test_run


    while True:
        try:
            run_pool.launch_workers(  )
            time.sleep(options.sleep)
        except (KeyboardInterrupt,):
            print
            utils.newline_msg("SYSTEM", "keyboard interrupted, exiting...")
            sys.exit(1)
