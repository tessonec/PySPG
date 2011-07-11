#!/usr/bin/python

from spg import utils, params


import numpy as n
import math as m


import os.path, os, sys
from subprocess import Popen, PIPE
import sqlite3 as sql

VAR_PATH = os.path.abspath(params.CONFIG_DIR+"/../var/spg")
BINARY_PATH = os.path.abspath(params.CONFIG_DIR+"/../bin")
TIMEOUT = 120



class ParameterSet:
    def __init__(self, full_name = ""):
        self.full_name = full_name
        self.path, self.db_name = os.path.split(full_name)

        self.values = {}
        self.directory_vars = None
        self.__init_db()

    def __init_db(self):

        self.connection = sql.connect(self.full_name, timeout = TIMEOUT)
        self.cursor = self.connection.cursor()
        #:::~ Table with the name of the executable
        (self.command, ) = self.cursor.execute( "SELECT name FROM executable " ).fetchone()
        #:::~ get the names of the columns
        sel = self.cursor.execute("SELECT name FROM entities ORDER BY id")
        self.entities = [ i[0] for i in sel ]
        #:::~ get the names of the columns
        sel = self.cursor.execute("SELECT name FROM entities WHERE varies = 1 ORDER BY id")
        self.variables = [ i[0] for i in sel ]
        #:::~ get the names of the outputs
        fa = self.cursor.execute("PRAGMA table_info(results)")
        self.output_column = [ i[1] for i in fa ]
        self.output_column = self.output_column[1:]

    def close_db(self):
        self.connection.commit()
        self.connection.close()
        del self.cursor
        del self.connection

    def __iter__(self):
        return self


    def next(self):
        res = self.cursor.execute(
                    "SELECT r.id, r.values_set_id, %s FROM run_status AS r, values_set AS v "% ", ".join(["v.%s"%i for i in self.entities]) +
                    "WHERE r.status = 'N' AND v.id = r.values_set_id ORDER BY r.id LIMIT 1" 
                   ).fetchone()
        if res == None:
            utils.newline_msg("WRN","db '%s' did not return any new data point"%self.full_name)
            return None

        self.current_run_id  = res[0]
        self.current_valuesset_id = res[1]
        self.cursor.execute( 'UPDATE run_status SET status ="R" WHERE id = %d'%self.current_run_id  )
        self.connection.commit()
        for i in range( len(self.entities) ):
            self.values[ self.entities[i] ] = res[i+2]

        return self.values

    def create_trees(self):
        ret = self.cursor.execute("SELECT * FROM entities WHERE name LIKE 'store_%'").fetchone()
        return ret is not None


    def generate_tree(self, dir_vars = None):
        if type(dir_vars) == type(""):
            self.directory_vars = dir_vars.split(",")
        elif type(dir_vars) == type([]):
            self.directory_vars = dir_vars
        else:
            self.directory_vars  = self.variables


################################################################################
################################################################################



class WeightedParameterSet(ParameterSet):
    normalising = 0.
    def __init__(self, full_name = "", id=-1, weight=1.,queue = 'any'):
       ParameterSet.__init__(self, full_name)
       self.weight = weight
       self.id = id
       self.queue = 'any'
       WeightedParameterSet.normalising += weight
       
    def update_weight(self,weight):
       self.weight = weight
       WeightedParameterSet.normalising += weight



################################################################################
################################################################################

class ParameterSetExecutor(ParameterSet):
    def __init__(self, full_name = ""):
        ParameterSet.__init__(self, full_name)
        os.chdir(self.path)
           
    def launch_process(self):
        pwd = os.path.abspath(".")
        if self.directory_vars or self.create_trees():
            dir = utils.replace_list(self.directory_vars, self.values, separator = "/")
            if not os.path.exists(dir): os.makedirs(dir)
            os.chdir(dir)
        configuration_filename = "input_%s_%d.dat"%(self.db_name, self.current_run_id)
        fconf = open(configuration_filename,"w")
        
        for k in self.values.keys():
            print >> fconf, k, utils.replace_string(self.values[k], self.values) 
        fconf.close()
        
        cmd = "%s/%s -i %s"%(BINARY_PATH, self.command, configuration_filename )
        proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
        proc.wait()
        ret_code = proc.returncode
        output = [i.strip() for i in proc.stdout.readline().split()]
        os.remove(configuration_filename)
        if self.directory_vars:
            os.chdir(pwd)
        if ret_code == 0:
           self.cursor.execute( 'UPDATE run_status SET status ="D" WHERE id = %d'%self.current_run_id )
           all_d = [self.current_variables_id]
           all_d.extend( output )
           cc = 'INSERT INTO results ( %s) VALUES (%s) '%( ", ".join(self.output_column) , ", ".join([str(i) for i in all_d]) )
           self.cursor.execute( cc )
        else:
           #:::~ status can be either 
           #:::~    'N': not run
           #:::~    'R': running
           #:::~    'D': successfully run (done)
           #:::~    'E': run but with non-zero error code
           self.cursor.execute( 'UPDATE run_status SET status ="E" WHERE id = %d'%self.current_run_id )
        
        self.connection.commit()


################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################

class ResultsDBQuery(ParameterSet):
    def __init__(self, full_name = ""):
       ParameterSet.__init__(self, full_name)
       self.coalesce = []
    
    def result_table(self, col_name, table_vars = None):
        if not table_vars:
          table_vars = list(self.variables)
          
        if self.directory_vars:
            for iv in self.directory_vars:
                try:
                    table_vars.remove(iv)
                except: pass
        
        query = "SELECT %s,AVG(r.%s) FROM results AS r, values_set AS v WHERE r.values_set_id = v.id GROUP BY r.values_set_id"%(",".join(["v.%s"%v for v in table_vars]), col_name)
        
        self.cursor.execute(query)
        
        return n.array( [ map(float,i) for i in self.cursor ] )

    def full_result_table(self, table_vars = None):
        if not table_vars:
          table_vars = list(self.variables)
          
        if self.directory_vars:
            for iv in self.directory_vars:
                try:
                    table_vars.remove(iv)
                except: pass
        
        query = "SELECT %s,%s FROM results AS r, values_set AS v WHERE r.values_set_id = v.id GROUP BY r.values_set_id"%(",".join(["v.%s"%v for v in table_vars]), ",".join(["r.%s"%v for v in self.output_column]))
  #      print self.output_column
  #      print query
        self.cursor.execute(query)
        
        return n.array( [ map(float,i) for i in self.cursor ] )


    def __iter__(self):
      if len(self.coalesce) == 0:  
        self.coalesce = self.variables
      query = "SELECT DISTINCT %s FROM values_set "%(",".join([v for v in self.coalesce] ))
      self.cursor.execute(query)
      pairs = [ i for i in self.cursor ]
      for i in pairs:
          d = {}
          for j in range( len( self.coalesce ) ):
              d[self.coalesce[j] ] = float( i[j] )
          yield d
    
  #     if self.not_in_table_vars:
 #        yield self.full_result_table()
         
#         raise StopIteration







