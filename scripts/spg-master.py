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
  


import os, os.path
from subprocess import Popen, PIPE

import sqlite3 as sql

import spg
import spg.params as params
import spg.utils as utils 

VAR_PATH = os.path.abspath(params.CONFIG_DIR+"/../var/spg")
BINARY_PATH = os.path.abspath(params.CONFIG_DIR+"/../bin")

class DBInfo:
   normalising = 0.
   def __init__(self, full_name = "", path= "", db_name= "", id=-1, weight=1.):
       self.full_name = full_name
       self.path = full_name
       self.db_name = db_name
       self.weight = weight
       self.id = id
       
       DBInfo.normalising += weight


class Queue:
    def __init__(self, name, max_jobs):
        self.name = name
        self.jobs = max_jobs
        self.processes = []

    def set_db(self, db):
        self.connection = db
        self.cursor = db.cursor()
        
    def populate_processes( self, new_jobs ):
        for i in range(new_jobs):
            cmd = "qsub -q %s %s/spg-worker.py"%(self.name, BINARY_PATH)
            proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
            output = proc.stdout
            proc.wait()

    def kill_processes( self, n_jobs ):
        for i in sorted(self.processes)[:n_jobs] :
            cmd = "qdel "%(i)
            proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
            output = proc.stdout
            proc.wait()
            self.cursor.execute("DELETE FROM running WHERE job_id = ?" , i)
        self.connection.commit()


    def normalise_processes(self):
        running_proc = len( self.processes )
        if running_proc > self.jobs :
            self.kill_processes( running_proc - self.jobs )
        elif running_proc < self.jobs :
            self.populate_processes( self.jobs - running_proc  )

###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
    
class ProcessPool:
    def __init__(self):
        
        self.dbs = {} 
        self.queues = {}
        self.reload_master_info()
        self.update_process_list()

    def reload_master_info(self):
        
       self.conn_master = sql.connect("%s/running.sqlite"%VAR_PATH)
       self.cur_master  = self.conn_master.cursor()
       
       res = self.cur_master.execute("SELECT name, max_jobs FROM queues WHERE status = 'R'")

       for (name, max_jobs) in res:
           
           self.queues[name] = Queue(name, max_jobs)
           self.queues[name].set_db(self.conn_master)

       res = self.cur_master.execute("SELECT id, full_name, path, db_name, weight FROM dbs WHERE status = 'R'")

       for (id, full_name, path, db_name, weight) in res:
           self.dbs[full_name] = DBInfo(full_name, path, db_name,id, weight)


    def update_process_list(self):

        proc = Popen("qstat", shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
        output = proc.stdout
        proc.wait()

        for i_q in self.queues:
            self.queues[i_q].processes = []

        for l in output:
            content = l.split()
            try:
                job_id = int( content[0].split(".")[0] )
                status = content[4]
                queue =  content[5]
                if status == "R":
                    self.queues[queue].processes.append( job_id ) 
            except: 
                continue



if __name__ == "__main__":
    
     pp = ProcessPool()
     pp.update_process_list()
     
     
     
     for i_j in pp.queues:
         print i_j.normalise_processes()
     