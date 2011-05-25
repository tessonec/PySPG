#!/usr/bin/python


import spg
import spg.params as params
import spg.utils as utils

import sqlite3 as sql
import sys, optparse


class DBExecutor():
    def __init__(self, db_name, timeout = 60):
        self.connection =  sql.connect(db_name, timeout = timeout)
        self.cursor = self.connection.cursor()

        self.constants = {}
        self.__init_db()

        self.stdout_contents = params.contents_in_output(self.command)


    def __init_db(self):

        #:::~ Table with the name of the executable
        self.cursor.execute( "SELECT name FROM executable " )
        self.command = self.cursor.fetchone()[0]

        #:::~ Table with the constant values
        self.cursor.execute( "SELECT name,value FROM constants " )
        for k, v in self.cursor:
            self.constants[k] = v

        #:::~ get the names of the columns
        self.cursor.execute("PRAGMA table_info(variables)")
        self.variables = [ i[1] for i in self.cursor.fetchall() ]
        print self.variables
        
    def __iter__(self):
        return self

    def next(self):
        
        self.cursor("SELECT * FROM ")
        try:
          self.value = self.data[ self.__index ]
        except:
          raise StopIteration
    
        return self.value

#        self.cursor.execute("CREATE TABLE IF NOT EXISTS constants "
#                            "(id INTEGER PRIMARY KEY, name CHAR(64), value CHAR(64))"
#                            )
#        for k in self.constant_items():
#            self.cursor.execute( "SELECT value FROM constants WHERE name = '%s'"%k)
#            prev_val = self.cursor.fetchone()
#            if prev_val is not None:
#                if prev_val[0] != self[k]:
#                    spg.utils.newline_msg("ERR", "conficting values for parameter '%s' (was %s, is %s)"%(k, self[k], prev_val[0]))
#                    sys.exit(1)
#            else:
#                self.cursor.execute( "INSERT INTO constants (name, value) VALUES (?,?)",(k, self[k]) )
#            
#        self.connection.commit()
#        vi = self.varying_items()
#        elements = "CREATE TABLE IF NOT EXISTS varying (id INTEGER PRIMARY KEY,  %s )"%( ", ".join([ "%s CHAR(64)"%i for i in vi ] ) )
##        print elements
#        self.cursor.execute(elements)
#        
#        elements = "INSERT INTO varying ( %s ) VALUES (%s)"%(   ", ".join([ "%s "%i for i in vi ] ), ", ".join( "?" for i in vi) )
#        query_elements = "SELECT COUNT(*) FROM varying WHERE "%(   "AND ".join([ "%s "%i for i in vi ] ) , ", ".join( "?" for i in vi) )
#        print query_elements
#        self.possible_varying_ids = []
#        for i in self:
#            
#            self.cursor.execute( elements, [ self[i] for i in vi] )
#            self.possible_varying_ids.append(self.cursor.lastrowid)
#          
##        print self.possible_varying_ids
#        self.connection.commit()
#        self.number_of_columns = 0
#        for ic, iv in self.stdout_contents:
#            if iv["type"] == "xy":
#                self.number_of_columns += 1
#            if iv["type"] == "xydy":
#                self.number_of_columns += 2
#
#
#        results = "CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, varying_id INTEGER,  %s , FOREIGN KEY(varying_id) REFERENCES varying(id))"%( ", ".join([ "%s CHAR(64)"%ic for ic, iv in self.stdout_contents ] ) )
##        print results
#        self.cursor.execute(results)
#        self.connection.commit()
#        
#        
#        self.cursor.execute("CREATE TABLE IF NOT EXISTS run_status (id INTEGER PRIMARY KEY, varying_id INTEGER, status CHAR(1), "
#                            "FOREIGN KEY (varying_id ) REFERENCES varying(id) )")
#                            
#        self.connection.commit()
#
#
#    def fill_status(self, repeat = 1):
#
#
#       for i_repeat in range(repeat):
#
#           for i_id in self.possible_varying_ids:
#                self.cursor.execute( "INSERT INTO run_status ( varying_id ) VALUES (%s)"%(i_id) )
#
#       self.connection.commit()
#
#
#    def clean_status(self):
#       self.cursor.execute('UPDATE run_status SET status = "" WHERE status ="R"')
#       self.connection.commit()
#
#    def clean_all_status(self):
#       self.cursor.execute('UPDATE run_status SET status = ""')
#       self.connection.commit()
#
##===============================================================================
##     cursor.execute("CREATE TABLE IF NOT EXISTS revision_history "
##                "( id INTEGER PRIMARY KEY, revision INTEGER, author CHAR(64), date CHAR(64), "
##                "  size INTEGER, number_of_files INTEGER, modified_files INTEGER, "
##                "  affected_lines_previous INTEGER , affected_lines_next INTEGER, "
##                "  removed_lines INTEGER, added_lines INTEGER, "
##                "  affected_bytes_previous INTEGER, affected_bytes_next INTEGER"
##                "   )"
##                )
## 
## 
##     cursor.execute("CREATE TABLE IF NOT EXISTS modified_files "
##                "( id INTEGER PRIMARY KEY, revision INTEGER, file_name CHAR(256))"
##                )
## 
## 
##===============================================================================
#
#
#
#




if __name__ == "__main__":
  


    
    parser = optparse.OptionParser(usage = "usage: %prog [options] project_id1 project_id2 project_id3... ")
    parser.add_option("--timeout", type="int", action='store', dest="timeout",
                            default = 60 , help = "timeout for database connection" )
    
    options, args = parser.parse_args()
    
    if len(args) == 0:
        args = ["results.sqlite"]
    
    for i_arg in args:
      if ".sqlite" not in i_arg:
          db_name = i_arg.replace("parameters","").replace(".dat","")
          db_name = "results%s.sqlite"%db_name
      else:
          db_name = i_arg

      parser = DBExecutor( db_name , timeout = options.timeout)
#      parser.init_db()
#          parser.fill_status(repeat = options.repeat )

