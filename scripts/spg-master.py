#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 16:20:26 2011

@author: -
"""

# logica del programa
#   leer la cantidad de procesos a ejecutar de la DB central
#   si este numero es menor (para alguna cola) que el que esta corriendo. lanzar los que faltan
#   si este numero es mayor (para alguna cola) que el que esta corriendo. matar los que sobran
#   en este ultimo caso, limpiar la DB central
  #print cmd
  


from spg.pool import ProcessPool

    

if __name__ == "__main__":
    
     pp = ProcessPool()
     pp.update_process_list()
     
     
     
     for i_j in pp.queues:
         print i_j.normalise_processes()
     