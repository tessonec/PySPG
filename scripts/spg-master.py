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
  
import time

from spg.pool import ProcessPool, DataExchanger
from spg.utils import newline_msg

if __name__ == "__main__":
  #  parser = optparse.OptionParser(usage = "usage: %prog [options] project_id1 ")
 #   parser.add_option("--sleep", type="int", action='store', dest="sleep",
       #                     default = 1800 , help = "waiting time before refresh" )

 #   options, args = parser.parse_args()

#    while True:
       pp = ProcessPool()
  #     pp.update_worker_info()
  #     for i_j in pp.queues:
   #       print pp.queues[i_j].normalise_processes()
       
  #     pp.update_worker_info()

       pex = DataExchanger( pp.db_master, pp.cur_master )
     #  newline_msg("INF", "initialise_infiles()")
       pex.initialise_infiles()
     #  newline_msg("INF", "harvesting_data()")
       pex.harvest_data()

     #  newline_msg("INF", "synchronise_master()")
       pex.synchronise_master()
#       time.sleep(options.sleep)
