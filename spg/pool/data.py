from spg import utils, params



import os.path
import pickle 
from subprocess import Popen, PIPE
import sqlite3 as sql

VAR_PATH = os.path.abspath(params.CONFIG_DIR+"/../var/spg")
BINARY_PATH = os.path.abspath(params.CONFIG_DIR+"/../bin")
TIMEOUT = 120


################################################################################
################################################################################
################################################################################

class AtomData:
    def __init__(self, fname, full_db_name = None):
        self.command = None
        
        self.full_db_name = full_db_name 
        if self.full_db_name :
           self.path, db_name = os.path.split(self.full_db_name)

        self.in_name = fname
        self.values = {}
        self.entities = []
        self.output = ""
        self.return_code  = None
        self.current_run_id  = None
        self.current_valuesset_id = None


    def load(self, src = 'queued', no_rm = False):
        full_inname = "%s/%s/%s"%(VAR_PATH,src,self.in_name) 
        vals = pickle.load( open(full_inname)  )
        self.__dict__ = vals.__dict__
#        try:
#          self.path = self.full_name[:self.full_name.rfind("/")]
#          self.db_name = self.full_name[self.full_name.rfind("/")+1:]
#        except:
#          pass
        if no_rm: return
        os.remove( full_inname )

    def dump(self,src = 'run'):
          full_name = "%s/%s/%s"%(VAR_PATH,src,self.in_name)
          pickle.dump( self, open(full_name, "w" ) )


    def load_next_from_db(self, connection=None, cursor=None):
        if not connection:
            connection = sql.connect(self.full_name, timeout = TIMEOUT)
        if not cursor:
            cursor = connection.cursor()

        #:::~ Table with the name of the executable
        (self.command, ) = cursor.execute( "SELECT name FROM executable " ).fetchone()
        #:::~ get the names of the columns
        sel = cursor.execute("SELECT name FROM entities ORDER BY id")
        self.entities = [ i[0] for i in sel ]

        res = cursor.execute(
                    "SELECT r.id, r.values_set_id, %s FROM run_status AS r, values_set AS v "% ", ".join(["v.%s"%i for i in self.entities]) +
                    "WHERE r.status = 'N' AND v.id = r.values_set_id ORDER BY r.id LIMIT 1" 
                   ).fetchone()
   #     print res
        if res == None:
          return None

        self.current_run_id  = res[0]
        self.current_valuesset_id= res[1]
        cursor.execute( 'UPDATE run_status SET status ="R" WHERE id = %d'%self.current_run_id  )
        connection.commit()
        for i in range( len(self.entities) ):
            self.values[ self.entities[i] ] = res[i+2]

#        sql_db.close()
#        del sql_db
        return self.values


    def dump_in_db(self, connection=None, cursor=None):
        if not connection:
            connection = sql.connect(self.full_db_name, timeout = TIMEOUT)
        if not cursor:
            cursor = connection.cursor()

        #:::~ get the names of the outputs
        fa = cursor.execute("PRAGMA table_info(results)")
        self.output_column = [ i[1] for i in fa ]
        self.output_column = self.output_column[1:]
        utils.newline_msg("PRT","{%s} %s -- %s,%s -- %s"%( self.in_name, self.return_code , self.current_run_id, self.current_valuesset_id, self.output) )
#        print self.return_code 
        if self.return_code == 0:
             all_d = [self.current_run_id]
             all_d.extend( self.output )
             cc = 'INSERT INTO results (%s) VALUES (%s) '%( ", ".join(self.output_column) , ", ".join([str(i) for i in all_d]) )
#             print cc, self.current_run_id 
#             try:
             cursor.execute( cc )
             cursor.execute( 'UPDATE run_status SET status ="D" WHERE id = %d'%self.current_run_id )
#             except:
#                 cursor.execute( 'UPDATE run_status SET status ="E" WHERE id = %d'%self.current_run_id )
                 
        else:
             #:::~ status can be either 
             #:::~    'N': not run
             #:::~    'R': running
             #:::~    'D': successfully run (done)
             #:::~    'E': run but with non-zero error code
             cursor.execute( 'UPDATE run_status SET status ="E" WHERE id = %d'%self.current_run_id )
             #self.connection.commit()
        connection.commit()
        #conn.close()
        #del cursor
        #del conn



################################################################################
################################################################################

class AtomDataExecutor(AtomData):
    def __init__(self, fname, full_db_name = None):
        AtomData.__init__(self, fname, full_db_name )

    def create_tree(self):
        for k in self.values:
          if k.find("store_") != -1: return True
        return False

    def launch_process(self, configuration_filename):
        os.chdir(self.path)

        if self.create_tree():
            dir_n = utils.replace_list(self.entities, self.values, separator = "/")
            if not os.path.exists(dir_n): 
                os.makedirs(dir_n)
            os.chdir(dir_n)

  #      configuration_filename = "input_%s_%d.dat"%(self.db_name, self.current_run_id)
        fconf = open(configuration_filename,"w")
        for k in self.values.keys():
            print >> fconf, k, utils.replace_string(self.values[k], self.values) 
        fconf.close()

        cmd = "%s/%s -i %s"%(BINARY_PATH, self.command, configuration_filename )
        proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
        proc.wait()
#        print self.command,  self.path, self.db_name,  configuration_filename  , self.values, <$$$$$$$
#        print self.current_run_id, self.current_variables_id, self.entities, configuration_filename
        self.return_code = proc.returncode
        self.output = [i.strip() for i in proc.stdout.readline().split()]
#        self.return_code = 0
#        self.output = ""
        os.remove(configuration_filename)
