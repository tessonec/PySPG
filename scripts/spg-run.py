#!/usr/bin/python


import spg
import spg.params as params
import spg.utils as utils

import sqlite3 as sql
import sys, optparse


class DBExecutor(spg.MultIteratorParser):
    def __init__(self, stream=None, db_name = "results.sqlite"):
        self.multi_iter = spg.parser.MultIteratorParser(stream)
        if not params.check_consistency(self.multi_iter.command, self.multi_iter):
            utils.newline_msg("ERR","data not consistent.")
            sys.exit(1)
        self.stdout_contents = params.contents_in_output(self.multi_iter.command)

        self.connection =  sql.connect(db_name)
        self.cursor = self.connection.cursor()

  def __iter__(self):
    return self

  def next(self):
    if self.__index == None:
       self.__index = 0
    else:
      self.__index += 1
       
    try:
      self.value = self.data[ self.__index ]
    except:
      raise StopIteration
    
    return self.value

        self.cursor.execute("CREATE TABLE IF NOT EXISTS constants "
                            "(id INTEGER PRIMARY KEY, name CHAR(64), value CHAR(64))"
                            )
        for k in self.constant_items():
            self.cursor.execute( "SELECT value FROM constants WHERE name = '%s'"%k)
            prev_val = self.cursor.fetchone()
            if prev_val is not None:
                if prev_val[0] != self[k]:
                    spg.utils.newline_msg("ERR", "conficting values for parameter '%s' (was %s, is %s)"%(k, self[k], prev_val[0]))
                    sys.exit(1)
            else:
                self.cursor.execute( "INSERT INTO constants (name, value) VALUES (?,?)",(k, self[k]) )
            
        self.connection.commit()
        vi = self.varying_items()
        elements = "CREATE TABLE IF NOT EXISTS varying (id INTEGER PRIMARY KEY,  %s )"%( ", ".join([ "%s CHAR(64)"%i for i in vi ] ) )
#        print elements
        self.cursor.execute(elements)
        
        elements = "INSERT INTO varying ( %s ) VALUES (%s)"%(   ", ".join([ "%s "%i for i in vi ] ), ", ".join( "?" for i in vi) )
        query_elements = "SELECT COUNT(*) FROM varying WHERE "%(   "AND ".join([ "%s "%i for i in vi ] ) , ", ".join( "?" for i in vi) )
        print query_elements
        self.possible_varying_ids = []
        for i in self:
            
            self.cursor.execute( elements, [ self[i] for i in vi] )
            self.possible_varying_ids.append(self.cursor.lastrowid)
          
#        print self.possible_varying_ids
        self.connection.commit()
        self.number_of_columns = 0
        for ic, iv in self.stdout_contents:
            if iv["type"] == "xy":
                self.number_of_columns += 1
            if iv["type"] == "xydy":
                self.number_of_columns += 2


        results = "CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, varying_id INTEGER,  %s , FOREIGN KEY(varying_id) REFERENCES varying(id))"%( ", ".join([ "%s CHAR(64)"%ic for ic, iv in self.stdout_contents ] ) )
#        print results
        self.cursor.execute(results)
        self.connection.commit()
        
        
        self.cursor.execute("CREATE TABLE IF NOT EXISTS run_status (id INTEGER PRIMARY KEY, varying_id INTEGER, status CHAR(1), "
                            "FOREIGN KEY (varying_id ) REFERENCES varying(id) )")
                            
        self.connection.commit()


    def fill_status(self, repeat = 1):


       for i_repeat in range(repeat):

           for i_id in self.possible_varying_ids:
                self.cursor.execute( "INSERT INTO run_status ( varying_id ) VALUES (%s)"%(i_id) )

       self.connection.commit()


    def clean_status(self):
       self.cursor.execute('UPDATE run_status SET status = "" WHERE status ="R"')
       self.connection.commit()

    def clean_all_status(self):
       self.cursor.execute('UPDATE run_status SET status = ""')
       self.connection.commit()

#===============================================================================
#     cursor.execute("CREATE TABLE IF NOT EXISTS revision_history "
#                "( id INTEGER PRIMARY KEY, revision INTEGER, author CHAR(64), date CHAR(64), "
#                "  size INTEGER, number_of_files INTEGER, modified_files INTEGER, "
#                "  affected_lines_previous INTEGER , affected_lines_next INTEGER, "
#                "  removed_lines INTEGER, added_lines INTEGER, "
#                "  affected_bytes_previous INTEGER, affected_bytes_next INTEGER"
#                "   )"
#                )
# 
# 
#     cursor.execute("CREATE TABLE IF NOT EXISTS modified_files "
#                "( id INTEGER PRIMARY KEY, revision INTEGER, file_name CHAR(256))"
#                )
# 
# 
#===============================================================================








if __name__ == "__main__":
  


    
    parser = optparse.OptionParser(usage = "usage: %prog [options] project_id1 project_id2 project_id3... ")
    
    parser.add_option("--exe", type="string", action='store', dest="executable",
                            default = None, help = "The program to be run" )
    
    parser.add_option("-r","--repeat", type="int", action='store', dest="repeat",
                            default = 1 , help = "how many times the simulation is to be run" )
    
    parser.add_option("--clean", action='store_true', dest = "clean",
                          help = 'cleans the running status in the database of the running processes')
    
    parser.add_option("--clean-all", action='store_true', dest = "clean_all",
                          help = 'clean the all the running status information')
    
    options, args = parser.parse_args()
    
    if len(args) == 0:
        args = ["parameters.dat"]
    
    for i_arg in args:
      parser = DBBuilder( stream = open(i_arg) )
      db_name = i_arg.replace("parameters","").replace(".dat","")
      db_name = "results%s.sqlite"%db_name
      if options.executable is not None:
          parser.command = options.executable
      if options.clean_all:
          parser.clean_all()
      elif parser.clean():
          parser.clean()
      else:
          parser.init_db()
          parser.fill_status(repeat = options.repeat )

