from spg import utils
from spg import BINARY_PATH, TIMEOUT

#import os.path, os, sys
import os
from subprocess import Popen, PIPE
import sqlite3 as sql

import numpy as n
#import math as m


#TIMEOUT = 120





class ParameterEnsemble:
    
    def __init__(self, full_name = "", id=-1, weight=1., queue = '*', status = 'R', repeat = 1, init_db = True):
        self.full_name = full_name
        self.path, self.db_name = os.path.split(full_name)

        self.values = {}
        self.directory_vars = None

        
        self.stat_processes_done = 0
        self.stat_processes_not_run = 0
        self.stat_processes_running = 0
        self.stat_processes_error = 0
        self.stat_values_set_with_rep = 0
        self.stat_values_set = 0

        self.weight = weight
        self.id = id
        self.queue = queue
        self.status = status
        self.repeat = repeat
        
        if init_db:
            self.init_db()

    def __connect_db(self):
        self.connection = sql.connect(self.full_name, timeout = TIMEOUT)
        self.cursor = self.connection.cursor()


    def __close_db(self):
        self.connection.commit()
        self.connection.close()
        del self.cursor
        del self.connection



    def execute_query(self, query, *args):
        self.__connect_db()
        ret = [i for i in self.cursor.execute(query, args)]
        self.__close_db()
        return ret 


    def execute_query_fetchone(self, query, *args):
        self.__connect_db()
        ret = self.cursor.execute(query, args).fetchone()
        self.__close_db()
        return ret 


    def init_db(self):
        self.__connect_db()
        #:::~ Table with the name of the executable
#        (self.command, ) = self.cursor.execute( "SELECT name FROM executable " ).fetchone()
        (self.command, ) = self.execute_query_fetchone( "SELECT name FROM executable " )
        #:::~ get the names of the columns
        sel = self.execute_query("SELECT name FROM entities ORDER BY id")
        self.entities = [ i[0] for i in sel ]
        #:::~ get the names of the columns
        sel = self.execute_query("SELECT name FROM entities WHERE varies = 1 ORDER BY id")
        self.variables = [ i[0] for i in sel ]
        #:::~ get the names of the outputs
        fa = self.execute_query("PRAGMA table_info(results)")
        self.output_column = [ i[1] for i in fa ]
        self.output_column = self.output_column[2:]
        self.directory_vars = self.variables[:-1]
#        self.__close_db()



    def __iter__(self):
        return self


    def reset(self):     
        self.execute_query( 'UPDATE run_status SET status ="N" WHERE id>0 '  )

    def next(self):
        query = "SELECT r.id, r.values_set_id, %s FROM run_status AS r, values_set AS v "% ", ".join( ["v.%s"%i for i in self.entities] )  +"WHERE r.status = 'N' AND v.id = r.values_set_id ORDER BY r.id LIMIT 1" 
#       print query
        res = self.execute_query_fetchone(query)
#        print res
        if res == None:
            # utils.newline_msg("WRN","db '%s' did not return any new data point"%self.full_name)
            raise StopIteration

        self.current_run_id  = res[0]
        self.current_valuesset_id = res[1]
        self.execute_query( 'UPDATE run_status SET status ="R" WHERE id = %d'%self.current_run_id  )
        
        for i in range( len(self.entities) ):
            self.values[ self.entities[i] ] = res[i+2]

        return self.values

    def create_trees(self):
#        self.__connect_db()
        if not self.directory_vars: return False
        ret = self.execute_query_fetchone("SELECT * FROM entities WHERE name LIKE 'store_%'")
        
#        self.__close_db()
        return ret is not None


    def generate_tree(self, dir_vars = None):
        
        if type(dir_vars) == type(""):
            self.directory_vars = dir_vars.split(",")
        elif type(dir_vars) == type([]):
            self.directory_vars = dir_vars
        else:
            self.directory_vars  = self.variables

    def update_status(self):
        #:::~    'N': not run yet
        #:::~    'R': running
        #:::~    'D': successfully run (done)
        #:::~    'E': run but with non-zero error code

        (self.stat_values_set_with_rep , ) = self.execute_query_fetchone("SELECT COUNT(*) FROM run_status ;")
        (self.stat_values_set, ) = self.execute_query_fetchone("SELECT COUNT(*) FROM values_set ;")
        
        ret = self.execute_query("SELECT status, COUNT(*) FROM run_status GROUP BY status")
#        self.stat_done, self.stat_not_run, self.stat_running,self.stat_error = 0,0,0,0
        for (k,v) in ret:
            if k == "D":
                self.stat_processes_done = v
            elif k == "N":
                self.stat_processes_not_run = v
            elif k == "R":
                self.stat_processes_running = v
            elif k == "E":
                self.stat_processes_error = v
 
 
#    def update_weight(self,weight):
#        ParameterEnsemble.normalising -= self.weight  
#        self.weight = weight
#        ParameterEnsemble.normalising += self.weight
 
        
#
#class ParameterEnsemble:
#    def __init__(self, full_name = ""):
#        self.full_name = full_name
#        self.path, self.db_name = os.path.split(full_name)
#
#        self.values = {}
#        self.directory_vars = None
#        self.__init_db()
#
#        
#    def query_db(self, query):
#        self.connection = sql.connect(self.full_name, timeout = TIMEOUT)
#        self.cursor = self.connection.cursor()
#
#        ret = [i for i in self.cursor.execute(query)]
#        
#        self.connection.commit()
#        self.connection.close()
#        
#        return ret
#
#    def query_db_fetchone(self, query):
#        self.connection = sql.connect(self.full_name, timeout = TIMEOUT)
#        self.cursor = self.connection.cursor()
#
#        ret = self.cursor.execute(query).fetchone()
#        
#        self.connection.commit()
#        self.connection.close()
#        
#        return ret
#
#
#
#    def __init_db(self):
#
#        self.connection = sql.connect(self.full_name, timeout = TIMEOUT)
#        self.cursor = self.connection.cursor()
#        #:::~ Table with the name of the executable
#        (self.command, ) = self.cursor.execute( "SELECT name FROM executable " ).fetchone()
#        #:::~ get the names of the columns
#        sel = self.cursor.execute("SELECT name FROM entities ORDER BY id")
#        self.entities = [ i[0] for i in sel ]
#        #:::~ get the names of the columns
#        sel = self.cursor.execute("SELECT name FROM entities WHERE varies = 1 ORDER BY id")
#        self.variables = [ i[0] for i in sel ]
#        #:::~ get the names of the outputs
#        fa = self.cursor.execute("PRAGMA table_info(results)")
#        self.output_column = [ i[1] for i in fa ]
#        self.output_column = self.output_column[1:]
#
#    def close_db(self):
#        self.connection.commit()
#        self.connection.close()
#        del self.cursor
#        del self.connection
#
#    def __iter__(self):
#        return self
#
#
#    def next(self):
#        res = self.cursor.execute(
#                    "SELECT r.id, r.values_set_id, %s FROM run_status AS r, values_set AS v "% ", ".join(["v.%s"%i for i in self.entities]) +
#                    "WHERE r.status = 'N' AND v.id = r.values_set_id ORDER BY r.id LIMIT 1" 
#                   ).fetchone()
#        if res == None:
#            utils.newline_msg("WRN","db '%s' did not return any new data point"%self.full_name)
#            return None
#
#        self.current_run_id  = res[0]
#        self.current_valuesset_id = res[1]
#        self.cursor.execute( 'UPDATE run_status SET status ="R" WHERE id = %d'%self.current_run_id  )
#        self.connection.commit()
#        for i in range( len(self.entities) ):
#            self.values[ self.entities[i] ] = res[i+2]
#
#        return self.values
#
#    def create_trees(self):
#        ret = self.cursor.execute("SELECT * FROM entities WHERE name LIKE 'store_%'").fetchone()
#        return ret is not None
#
#
#    def generate_tree(self, dir_vars = None):
#        
#        if type(dir_vars) == type(""):
#            self.directory_vars = dir_vars.split(",")
#        elif type(dir_vars) == type([]):
#            self.directory_vars = dir_vars
#        else:
#            self.directory_vars  = self.variables







################################################################################
################################################################################















################################################################################
################################################################################

class ParameterEnsembleExecutor(ParameterEnsemble):
    def __init__(self, full_name = "", id=-1, weight=1., queue = '*', status = 'R', repeat = 1, init_db = True):
        ParameterEnsemble.__init__(self, full_name , id, weight, queue , status , repeat  , init_db )
        self.generate_tree()
        self.directory_vars = self.variables[:]
        os.chdir(self.path)
           
    def launch_process(self):
        pwd = os.path.abspath(".")
        if self.create_trees():
            
            dir = utils.generate_string(self.values,self.directory_vars, joining_string = "/")
            if not os.path.exists(dir): os.makedirs(dir)
            os.chdir(dir)
        configuration_filename = "input_%.8d.dat"%(self.current_run_id)
        output_filename = "output_%.8d.dat"%(self.current_run_id)
    #   print configuration_filename
        fconf = open(configuration_filename,"w")
        for k in self.values.keys():
            print >> fconf, k, utils.replace_values(self.values[k], self.values) 
        fconf.close()
        #except:
        #      utils.newline_msg("WRN", "could not load '%s'"%configuration_filename)
        #      return

        cmd = "%s/%s -i %s > %s"%(BINARY_PATH, self.command, configuration_filename, output_filename )
        os.system(cmd)
        ret_code = 0
#        proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
#        proc.wait()
 #       ret_code = proc.returncode
        try:
            output = [i.strip() for i in open(output_filename).readline().split()]
            os.remove(configuration_filename)
            os.remove(output_filename)
        except:
            utils.newline_msg("WRN", "could not read '%s' -  may it be other process accessed it"%output_filename)
            return
        if self.directory_vars:
            os.chdir(pwd)
#        if ret_code == 0:
            
        all_d = [self.current_valuesset_id]
        all_d.extend( output )
#            print self.output_column, all_d
        cc = 'INSERT INTO results (values_set_id, %s) VALUES (%s) '%( ", ".join(self.output_column) , ", ".join([str(i) for i in all_d]) )
        flog = open(self.full_name.replace("sqlite", "log"), "aw") 
        print >> flog, "%.8d: %s --> %s"%(self.current_valuesset_id, self.values, output)

        try:
            self.execute_query( cc )
            self.execute_query( 'UPDATE run_status SET status ="D" WHERE id = %d'%self.current_run_id )           
        except:
            self.execute_query( 'UPDATE run_status SET status ="E" WHERE id = %d'%self.current_run_id )

            

#        else:
            #:::~ status can be either 
            #:::~    'N': not run
            #:::~    'R': running
            #:::~    'D': successfully run (done)
            #:::~    'E': run but with non-zero error code
        
#       self.connection.commit()




class ParameterEnsembleInputFilesGenerator(ParameterEnsemble):
    def __init__(self, full_name = "", id=-1, weight=1., queue = '*', status = 'R', repeat = 1, init_db = True):
        ParameterEnsemble.__init__(self, full_name , id, weight, queue , status , repeat  , init_db )
        os.chdir(self.path)
           
    def launch_process(self):
#        pwd = os.path.abspath(".")
   #     if self.directory_vars or self.create_trees():
   #         dir = utils.generate_string(self.values,self.directory_vars, joining_string = "/")
   #         if not os.path.exists(dir): os.makedirs(dir)
    #        os.chdir(dir)
        configuration_filename = "input_%.8d.dat"%(self.current_valuesset_id)
        fconf = open(configuration_filename,"w")
        
        for k in self.values.keys():
            print >> fconf, k, utils.replace_values(self.values[k], self.values) 
        fconf.close()
   




################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################

class ResultsDBQuery(ParameterEnsemble):
    def __init__(self, full_name = "", id=-1, weight=1., queue = '*', status = 'R', repeat = 1, init_db = True):
        ParameterEnsemble.__init__(self, full_name , id, weight, queue , status , repeat  , init_db )
        self.separated_vars = self.variables[:-2]
        self.coalesced_vars = self.variables[-2:-1]
        self.in_table_vars =  self.variables[-1:]


    def setup_output_table(self, conf):
        """which are the variables that are inside of the output file, orphaned variables are sent into the coalesced ones"""
        if conf.strip() != "" :
            in_table_vars = conf.split(",")
        else:
            in_table_vars = []
        if set(in_table_vars).issubset( set(self.variables) ):
            self.in_table_vars = in_table_vars
            self.coalesced_vars = [ i for i in self.coalesced_vars if ( i not in self.in_table_vars ) ]
            self.separated_vars = [ i for i in self.separated_vars if ( i not in self.in_table_vars ) ]
            
            orphaned = set(self.variables) - set(self.separated_vars) - set( self.in_table_vars ) - set( self.coalesced_vars )
            if len(orphaned) > 0:
                utils.newline_msg("VAR", "orphaned variables '%s' added to separated variables"%orphaned, indent=4)
                for i in orphaned: self.coalesced_vars.append(i)
            print "    structure = %s - %s - %s "%(self.separated_vars, self.coalesced_vars, self.in_table_vars)
        else:
            print in_table_vars, conf
            utils.newline_msg("VAR", "the variables '%s' are not recognised"%set(in_table_vars)-set(self.variables) )
        
                
    def setup_separated_output(self, conf):
        """Which variables are separated in different directories, orphaned variables are sent into the coalesced ones"""
        if conf.strip() != "" :
            separated = conf.split(",")
        else:
            separated = []
        if set(separated).issubset( set(self.variables) ):
            self.separated_vars = separated
            self.coalesced_vars = [ i for i in self.coalesced_vars if ( i not in self.separated_vars )  ]
            self.in_table_vars = [ i for i in self.in_table_vars if ( i not in self.separated_vars )  ]
            orphaned = set(self.variables) - set(self.separated_vars) - set( self.in_table_vars ) - set( self.coalesced_vars )
            if len(orphaned) > 0:
                utils.newline_msg("VAR", "orphaned variables '%s' added to separated variables"%orphaned, indent=4)
                for i in orphaned: self.coalesced_vars.append(i)
            print "    structure = %s - %s - %s "%(self.separated_vars, self.coalesced_vars, self.in_table_vars)
        else:
            utils.newline_msg("VAR", "the variables '%s' are not recognised"%set(separated)-set(self.variables) )

    def setup_coalesced_output(self, conf):
        """Which variables are coalesced into the same files, orphaned variables are sent into the separated ones"""
        if conf.strip() != "" :
            coalesced = conf.split(",")
        else:
            coalesced = []
        if set(coalesced).issubset( set(self.variables) ):
            self.coalesced_vars = coalesced
            self.separated_vars = [ i for i in self.separated_vars if ( i not in self.coalesced_vars ) ]
            self.in_table_vars = [ i for i in self.in_table_vars if ( i not in self.coalesced_vars ) ]
            orphaned = set(self.variables) - set(self.separated_vars) - set( self.in_table_vars ) - set( self.coalesced_vars )
            if len(orphaned) > 0:
                utils.newline_msg("VAR", "orphaned variables '%s' added to separated variables"%orphaned, indent=4)
                for i in orphaned: self.separated_vars.append(i)
            print "    structure = %s - %s - %s "%(self.separated_vars, self.coalesced_vars, self.in_table_vars)
        else:
            utils.newline_msg("VAR", "the variables '%s' are not recognised"%set(coalesced)-set(self.variables) )



    def clean_dict(self,dict_to_clean):
        """ adds quotes to strings """
        for i in dict_to_clean:  
            try:
                float( dict_to_clean[i] ) 
            except:
                dict_to_clean[ i ] = "'%s'"%( dict_to_clean[i ].replace("'","").replace('"',"") )

    
    def table_from_query(self, query):
        """ print query """
#        self.__connect_db()
        
        ret = n.array( [ map(float,i) for i in self.execute_query(query) ] )
#        self.__close_db()
        return ret



    def result_table(self, restrict_to_values = {}, raw_data = False, restrict_by_val = False, output_column = []):
   
        self.clean_dict(restrict_to_values)

        if len(self.in_table_vars) == 0:
            var_cols = ""
        elif len(self.in_table_vars) == 1:
            var_cols = "v.%s, "%self.in_table_vars[0]
        elif len(self.in_table_vars) > 1:
            var_cols = "%s, "%",".join(["v.%s"%v for v in self.in_table_vars])
        if not output_column:
            output_column = self.output_column[:]
        if "values_set_id" in output_column: 
                output_column.remove("values_set_id")

        out_cols = ""
        if not raw_data :
            if len(output_column ) == 1:
                out_cols = "AVG(r.%s) "%output_column[0]
            elif len(output_column) > 1:
                out_cols = " %s"%",".join(["AVG(r.%s)"%v for v in output_column])
        else:
            if len(output_column ) == 1:
                out_cols = "r.%s "%output_column[0]
            elif len(output_column) > 1:
                out_cols = " %s"%",".join(["r.%s"%v for v in output_column])
          
        query = "SELECT %s %s FROM results AS r, values_set AS v WHERE r.values_set_id = v.id "%(var_cols, out_cols)
        #:::~ This command was needed only because of a mistake in the id stores in the results table
        restrict_cols = ""
        if restrict_to_values:
            restrict_cols = " AND ".join(["v.%s = '%s'"%(v, restrict_to_values[v]) for v in restrict_to_values.keys()])
            if restrict_cols :
                restrict_cols = "AND %s"%restrict_cols 
        query = "%s  %s "%(query, restrict_cols)
        if not raw_data :
            if restrict_by_val:
                query = "%s  GROUP BY %s"%(query, var_cols.strip(", "))
            else:  
                query = "%s %s GROUP BY v.id"%(query, restrict_cols)
        query=query.replace("''", "'").replace("'\"", "'")
#        print query
        return self.table_from_query(query)        


    def __iter__(self):
#        self.__connect_db()
        vars_to_separate = self.separated_vars[:]
        vars_to_separate.extend(self.coalesced_vars)

        if not vars_to_separate:
            yield {}
            return
        elif len(vars_to_separate) == 1:
            query = "SELECT DISTINCT %s FROM values_set "%( vars_to_separate[0] )
        elif len(vars_to_separate) > 1:
            query = "SELECT DISTINCT %s FROM values_set "%(",".join([v for v in vars_to_separate] ))

        pairs = self.execute_query(query)
#        pairs = [ i for i in self.cursor ]
#        self.__close_db()
        d = {}
        for i in pairs:
            d.clear()
            for j in range( len( vars_to_separate ) ):
                d[vars_to_separate[j] ] = i[j]
            yield d
