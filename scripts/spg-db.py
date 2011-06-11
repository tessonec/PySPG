#!/usr/bin/python


import spg
import spg.params as params
import spg.utils as utils

import sqlite3 as sql
import sys, optparse
import time, os, os.path


VAR_PATH = os.path.abspath(params.CONFIG_DIR+"/../var/spg")

class DBBuilder(spg.MultIteratorParser):
    def __init__(self, stream=None, db_name = "results.sqlite", timeout = 5):
        spg.parser.MultIteratorParser.__init__(self, stream)
        if not params.check_consistency(self.command, self):
            utils.newline_msg("ERR","data not consistent.")
            sys.exit(1)
        self.stdout_contents = params.contents_in_output(self.command)
                
        self.connection =  sql.connect(db_name, timeout = timeout)
        self.cursor = self.connection.cursor()

    def init_db(self, retry=1):
        #:::~ Table with the name of the executable
        self.cursor.execute("CREATE TABLE IF NOT EXISTS executable "
                            "(id INTEGER PRIMARY KEY, name CHAR(64))"
                            )
        self.cursor.execute( "SELECT name FROM executable " )
        prev_val = self.cursor.fetchone()
        
        
        if prev_val :
            if prev_val[0] != self.command:
                utils.newline_msg("ERR","conflict in executable name (in db '%s', in param '%s')"%(prev_val, self.command))
        else:
            self.cursor.execute("INSERT INTO executable (name) VALUES ('%s')"%self.command)
            self.connection.commit()

        #:::~ Table with the defined entities
        self.cursor.execute("CREATE TABLE IF NOT EXISTS entities "
                            "(id INTEGER PRIMARY KEY, name CHAR(64), varies INTEGER)"
                            )

        self.cursor.execute( "SELECT COUNT(*) FROM entities ")
        n_items = self.cursor.fetchone()
        if n_items[0] == 0: # table has not been filled
            for i in self.data:
                varies = 1 if (i.__class__ != spg.IterConstant) else 0
                self.cursor.execute( "INSERT INTO entities (name, varies) VALUES (?,?)",(i.name,  varies) )
        else:
            self.cursor.execute( "SELECT name FROM entities ")
            entities = set([i[0] for i in self.cursor])
            s_names = set(self.names)
            if entities != set(self.names):
                spg.utils.newline_msg("ERR", "parameter (was %s, is %s)"%(entities, s_names))
                sys.exit(1)
            
        self.connection.commit()


#        #:::~ Table with the constant values
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
            
#        self.connection.commit()
#        vi = self.varying_items()
#        print self.data
#        print self.data
        elements = "CREATE TABLE IF NOT EXISTS values_set (id INTEGER PRIMARY KEY,  %s )"%( ", ".join([ "%s CHAR(64)"%i for i in self.names ] ) )
#        print elements
        self.cursor.execute(elements)
        
        elements = "INSERT INTO values_set ( %s ) VALUES (%s)"%(   ", ".join([ "%s "%i for i in self.names ] ), ", ".join( "?" for i in self.names ) )
        #query_elements = "SELECT COUNT(*) FROM variables WHERE "%(   "AND ".join([ "%s "%i for i in vi ] ) , ", ".join( "?" for i in vi) )
        #print query_elements
        self.possible_varying_ids = []
        i_try = 0
        commited = False
        while i_try < retry and not commited:
#          try:   
            i_try += 1
            for i in self:
#                print elements
                self.cursor.execute( elements, [ self[i] for i in self.names] )
                self.possible_varying_ids.append(self.cursor.lastrowid)
          
#        print self.possible_varying_ids
            self.connection.commit()
            commited = True
#          except sql.OperationalError:  
#              utils.newline_msg("DB", "database is locked (%d/%d)"%(i_try, retry))
              
        if not commited:
              utils.newline_msg("ERR", "database didn't unlock, exiting")
          
        self.number_of_columns = 0
        for ic, iv in self.stdout_contents:
            if iv["type"] == "xy":
                self.number_of_columns += 1
            if iv["type"] == "xydy":
                self.number_of_columns += 2


        results = "CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, values_set_id INTEGER,  %s , FOREIGN KEY(values_set_id) REFERENCES values_set(id))"%( ", ".join([ "%s CHAR(64)"%ic for ic, iv in self.stdout_contents ] ) )
#        print results
        self.cursor.execute(results)
        self.connection.commit()
        
        
        self.cursor.execute("CREATE TABLE IF NOT EXISTS run_status (id INTEGER PRIMARY KEY, values_set_id INTEGER, status CHAR(1), "
                            "FOREIGN KEY (values_set_id ) REFERENCES values_set(id) )")
                            
        self.connection.commit()


    def fill_status(self, repeat = 1):


       for i_repeat in range(repeat):

           for i_id in self.possible_varying_ids:
                #:::~ status can be either 
                #:::~    'N': not run
                #:::~    'R': running
                #:::~    'D': successfully run (done)
                #:::~    'E': run but with non-zero error code
                self.cursor.execute( "INSERT INTO run_status ( values_set_id, status ) VALUES (%s,'N')"%(i_id) )

       self.connection.commit()


    def clean_status(self):
       self.cursor.execute('UPDATE run_status SET status = "N" WHERE status ="R"')
       self.connection.commit()

    def clean_all_status(self):
       self.cursor.execute('UPDATE run_status SET status = "N"')
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



def init_db(i_arg,params,options):
      i_arg, db_name = translate_name(i_arg)
      parser = DBBuilder( stream = open(i_arg), db_name=db_name , timeout = options.timeout )
      repeat = 1
      if 'repeat' in params:
         repeat = params['repeat']
      sql_retries = 1
      if 'sql_retries' in params:
         sql_retries = params['sql_retries']
      if 'executable' in params:
          parser.command = repeat = params['executable']
      parser.init_db(retry = sql_retries)
      parser.fill_status(repeat = repeat)


def clean_all_db(i_arg,params,options):
          i_arg, db_name = translate_name(i_arg)
          parser = DBBuilder( stream = open(i_arg), db_name=db_name , timeout = options.timeout )

          parser.clean_all_status()


def clean_db(i_arg,params,options):
      i_arg, db_name = translate_name(i_arg)
      parser = DBBuilder( stream = open(i_arg), db_name=db_name , timeout = options.timeout )

      parser.clean_status()



def remove_db(i_arg,params,parser):
    i_arg, db_name = translate_name(i_arg)
    connection = sql.connect("%s/running.sqlite"%VAR_PATH)
    cursor = connection.cursor()
    cursor.execute( "DELETE FROM dbs WHERE full_name = ?",(os.path.realpath(db_name),) )

    connection.commit()

def translate_name(st):
    if ".sqlite" in st:
      par_name = st.replace("results","").replace(".sqlite","")
      par_name = "parameters%s.dat"%par_name
      return par_name, st
    else:
      db_name = st.replace("parameters","").replace(".dat","")
      db_name = "results%s.sqlite"%db_name
      return st,db_name
        


def get_parameters(arg):
    ret = {}
    
    for i in arg.split(":"):
        [k,v] = i.split("=")
        ret[k] = v

    return ret



dict_functions = { "init":init_db, "clean": clean_db, "clean_all": clean_all_db , "remove": remove_db}

def execute_command( arguments , options):
#    if len( arguments ) <3 :
#        return
    params = {}
    
    full_command = arguments[0]

    i_arg, db_name = translate_name( arguments[1] ) 
    if len(arguments) > 2 :
        params = get_parameters( arguments[2] )
    else:
        params = {}

    f = dict_functions[ full_command ] 

#      print db_name

    f(i_arg, params, options)






if __name__ == "__main__":
  


    
    parser = optparse.OptionParser(usage = "usage: %prog [options] CMD VERB NAME {params}\n"
                                      "commands NAME {params}: \n"
                                      "   init PARAMETERS_NAME|DB_NAME \n"
                                      "        params :: executable=EXE_NAME , repeat=REPEAT, sql_retries=1\n"
                                      "   clean-all PARAMETERS_NAME|DB_NAME \n"
                                      "   clean PARAMETERS_NAME|DB_NAME \n"
                                      "   remove PARAMETERS_NAME|DB_NAME \n"
                                  )
    
    parser.add_option("--timeout", type="int", action='store', dest="timeout",
                            default = 5 , help = "timeout for database connection" )
    
    options, args = parser.parse_args()

    execute_command(args, options)


