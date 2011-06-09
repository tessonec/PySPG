#!/usr/bin/python


import spg
import spg.params as params
import spg.utils as utils

import sqlite3 as sql
from subprocess import Popen, PIPE
import sys, os, os.path
import optparse

BINARY_PATH = os.path.abspath(params.CONFIG_DIR+"/../bin")

class DBExecutor():
    def __init__(self, db_name, timeout = 60):
        self.connection =  sql.connect(db_name, timeout = timeout)
#        self.connection.row_factory = sql.Row
        self.cursor = self.connection.cursor()
        self.db_name = db_name

        self.values = {}
        self.directory_vars = None
        self.__init_db()

        self.stdout_contents = params.contents_in_output(self.command)


    def __init_db(self):

        #:::~ Table with the name of the executable
        self.cursor.execute( "SELECT name FROM executable " )
        self.command = self.cursor.fetchone()[0]

#        #:::~ Table with the constant values
#        self.cursor.execute( "SELECT name,value FROM constants " )
#        for k, v in self.cursor:
#        #    self.constants[k] = v
#            self.values[k] = v
#            
        
#        #:::~ get the names of the columns
#        self.cursor.execute("PRAGMA table_info(variables)")
#        self.entities = [ i[1] for i in self.cursor.fetchall() ]
#        self.entities = self.entities[1:]

        #:::~ get the names of the columns
        self.cursor.execute("SELECT name FROM entities ORDER BY id")
        self.entities = [ i[0] for i in self.cursor ]
#        self.entities = self.entities[1:]


        #:::~ get the names of the outputs
        self.cursor.execute("PRAGMA table_info(results)")
        self.output_column = [ i[1] for i in self.cursor.fetchall() ]
        self.output_column = self.output_column[1:]
        
#        print self.entities
        
    def __iter__(self):
        return self

    def next(self):
        
        self.cursor.execute(
                    "SELECT r.id, r.values_set_id, %s FROM run_status AS r, values_set AS v "% ", ".join(["v.%s"%i for i in self.entities]) +
                    "WHERE r.status = 'N' AND v.id = r.values_set_id ORDER BY r.id LIMIT 1" 
                   )
                   
        res = self.cursor.fetchone()
        if res == None:
          raise StopIteration
#        print res    
#        res = list(res)
        self.current_run_id  = res[0]
        self.current_variables_id  = res[1]
        self.cursor.execute( 'UPDATE run_status SET status ="R" WHERE id = %d'%self.current_run_id  )
        self.connection.commit()          
#        print res.keys(), dir(res)
        for i in range(len(self.entities)):
            self.values[ self.entities[i] ] = res[i+2]
        return self.values

    def generate_tree(self, dir_vars = None):
        if dir_vars:
            self.directory_vars = dir_vars
        else:
            self.directory_vars =  self.entities 

    def launch_process(self):
        pwd = os.path.abspath(".")
        if self.directory_vars:
            dir = utils.replace_list(self.directory_vars, self.values, separator = "/")
            if not os.path.exists(dir): os.makedirs(dir)
            os.chdir(dir)
        configuration_filename = "input_%s_%d.dat"%(self.db_name, self.current_run_id)
        fconf = open(configuration_filename,"w")
        
        for k in self.values.keys():
            print >> fconf, k, utils.replace_string(self.values[k], self.values) 
        fconf.close()
        
        cmd = "%s/%s -i %s"%(BINARY_PATH, self.command, configuration_filename )
#        print cmd
        proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
        proc.wait()
        ret_code = proc.returncode
#        ret_code = 0
        output = [i.strip() for i in proc.stdout.readline().split()]
#        output = ["1" for i in self.output_column[1:] ]
#        print ret_code, "-->", output
        os.remove(configuration_filename)
        if self.directory_vars:
            os.chdir(pwd)
#        print self.output_column
        if ret_code == 0:
           self.cursor.execute( 'UPDATE run_status SET status ="D" WHERE id = %d'%self.current_run_id )
           all_d = [self.current_variables_id]
           all_d.extend( output )
           cc = 'INSERT INTO results ( %s) VALUES (%s) '%( ", ".join(self.output_column) , ", ".join([str(i) for i in all_d]) )
 #          print cc
           self.cursor.execute( cc )
           self.connection.commit()
        else:
           #:::~ status can be either 
           #:::~    'N': not run
           #:::~    'R': running
           #:::~    'D': successfully run (done)
           #:::~    'E': run but with non-zero error code
           self.cursor.execute( 'UPDATE run_status SET status ="E" WHERE id = %d'%self.current_run_id )
           self.connection.commit()


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

      executor = DBExecutor( db_name, timeout = options.timeout)
      
      if options.tree:
          executor.generate_tree( options.directory_vars )

      for values in executor:
          executor.launch_process()
          
          #      parser.init_db()
#          parser.fill_status(repeat = options.repeat )

