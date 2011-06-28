from spg import utils, params



import os.path
from subprocess import Popen, PIPE
import sqlite3 as sql

VAR_PATH = os.path.abspath(params.CONFIG_DIR+"/../var/spg")
BINARY_PATH = os.path.abspath(params.CONFIG_DIR+"/../bin")
TIMEOUT = 120




class ParameterExtractor:
    def __init__(self, full_name = "", path = "", db_name = ""):
        self.full_name = full_name
        self.path = path
        self.db_name = db_name
        

        self.values = {}
        self.directory_vars = None
        self.__init_db()

    def __init_db(self):

        sql_db = sql.connect(self.full_name, timeout = TIMEOUT)
        cur_db = sql_db.cursor()
        #:::~ Table with the name of the executable
        (self.command, ) = cur_db.execute( "SELECT name FROM executable " ).fetchone()
        #:::~ get the names of the columns
        sel = cur_db.execute("SELECT name FROM entities ORDER BY id")
        self.entities = [ i[0] for i in sel ]
        #:::~ get the names of the outputs
        fa = cur_db.execute("PRAGMA table_info(results)")
        self.output_column = [ i[1] for i in fa ]
        self.output_column = self.output_column[1:]
        del cur_db
        sql_db.close()
        del sql_db

    def __iter__(self):
        return self


    def next(self):
        sql_db = sql.connect(self.full_name, timeout = TIMEOUT)
        cur_db = sql_db.cursor()
    #   print self.db_name
        res = cur_db.execute(
                    "SELECT r.id, r.values_set_id, %s FROM run_status AS r, values_set AS v "% ", ".join(["v.%s"%i for i in self.entities]) +
                    "WHERE r.status = 'N' AND v.id = r.values_set_id ORDER BY r.id LIMIT 1" 
                   ).fetchone()
        if res == None:
          raise StopIteration

        self.current_run_id  = res[0]
        self.current_variables_id  = res[1]
        cur_db.execute( 'UPDATE run_status SET status ="R" WHERE id = %d'%self.current_run_id  )
        sql_db.commit()
        for i in range( len(self.entities) ):
            self.values[ self.entities[i] ] = res[i+2]

        sql_db.close()
        del sql_db
        return self.values

    def store_pickleddata_in_db(self, pd):
        conn = sql.connect("%s/%s"%(self.db_name))
        cursor = conn.cursor()

        #:::~ get the names of the outputs
        fa = cursor.execute("PRAGMA table_info(results)")
        self.output_column = [ i[1] for i in fa ]
        self.output_column = self.output_column[1:]

        if self.return_code == 0:
             cursor.execute( 'UPDATE run_status SET status ="D" WHERE id = %d'%self.current_run_id )
             all_d = [self.current_run_id]
             all_d.extend( pd.output )
             cc = 'INSERT INTO results ( %s) VALUES (%s) '%( ", ".join(self.output_column) , ", ".join([str(i) for i in all_d]) )
             cursor.execute( cc )
        else:
             #:::~ status can be either 
             #:::~    'N': not run
             #:::~    'R': running
             #:::~    'D': successfully run (done)
             #:::~    'E': run but with non-zero error code
             cursor.execute( 'UPDATE run_status SET status ="E" WHERE id = %d'%pd.id )
             #self.connection.commit()
        conn.commit()
        conn.close()
        del cursor
        del conn



################################################################################
################################################################################



class ParameterDB(ParameterExtractor):
    normalising = 0.
    def __init__(self, full_name = "", path= "", db_name= "", id=-1, weight=1.,queue = 'any'):
       ParameterExtractor.__init__(self, full_name , path, db_name)
       self.weight = weight
       #self.current_run_id = current_run_id 
       self.id = id
       self.queue = 'any'
       ParameterDB.normalising += weight



################################################################################
################################################################################

class DBExecutor(ParameterExtractor):
    def __init__(self, full_name = "", path= "", db_name= ""):
        ParameterExtractor.__init__(self, full_name , path, db_name)
           
    def launch_process(self):
        pwd = os.path.abspath(".")
        if self.directory_vars:
            dir = utils.replace_list(self.directory_vars, self.values, separator = "/")
            if not os.path.exists(dir): os.makedirs(dir)
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
        
        sql_db = sql.connect(self.db_name, timeout = TIMEOUT)
        cur_db = sql_db.cursor()
        if ret_code == 0:
           cur_db.execute( 'UPDATE run_status SET status ="D" WHERE id = %d'%self.current_run_id )
           all_d = [self.current_variables_id]
           all_d.extend( output )
           cc = 'INSERT INTO results ( %s) VALUES (%s) '%( ", ".join(self.output_column) , ", ".join([str(i) for i in all_d]) )
           cur_db.execute( cc )
        else:
           #:::~ status can be either 
           #:::~    'N': not run
           #:::~    'R': running
           #:::~    'D': successfully run (done)
           #:::~    'E': run but with non-zero error code
           cur_db.execute( 'UPDATE run_status SET status ="E" WHERE id = %d'%self.current_run_id )
        
        sql_db.commit()
        sql_db.close()
        del sql_db


    def create_trees(self):
        sql_db = sql.connect(self.db_name, timeout = TIMEOUT)
        ret = sql_db.select("SELECT * FROM entities WHERE name LIKE 'store_%'").fetchone()
        
        sql_db.close()
        del sql_db
        return ret is not None


    def generate_tree(self, dir_vars = None):
        sql_db = sql.connect(self.db_name, timeout = TIMEOUT)
        if dir_vars:
           self.directory_vars = dir_vars
        else:
           res = self.sql_db.execute("SELECT name FROM entities WHERE varies = 1 ORDER BY id")
           self.directory_vars  = [ i[0] for i in res ]
        sql_db.close()
        del sql_db
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
