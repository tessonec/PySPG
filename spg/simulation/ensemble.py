from spg import utils
from spg import TIMEOUT, BINARY_PATH, ROOT_DIR

import os, sys, os.path, time
from subprocess import Popen, PIPE
import sqlite3 as sql
import spg.utils as utils
import signal
# import numpy as n



import csv 



class ParameterEnsemble:
    
    def __init__(self, full_name = "", id=-1, weight=1., queue = '*',
                 status = 'R', repeat = 1, init_db = False):

        self.full_name, self.path, self.base_name, ext = utils.translate_name(full_name)

        self.db_name = "%s.spgql"%self.base_name
        self.full_name = "%s/%s.spgql"%(self.path,self.base_name)
        self.id = id
        self.values = {}
        # self.directory_vars = None

        self.weight = weight
        self.current_spg_uid = 0
        self.queue = queue
        self.status = status
        self.repeat = repeat

        if init_db  :
            self.init_db()
#            print self.output_column
          #  sys.exit(1)

    def __connect_db(self):
        try:
           self.connection = sql.connect(self.full_name, timeout = TIMEOUT)
        except:
            utils.newline_msg("ERR", "database '%s' does not exist... exiting"%self.full_name)
        self.cursor = self.connection.cursor()
         


    def __close_db(self):

        self.cursor.close()
        del self.cursor
        self.connection.commit()
        self.connection.close()
        del self.connection
#

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

    def parse_output_line(self,  output_line):
        """ parses a line from output. Returns a tuple containing: table of output, column names of output,  output values to be inserted in table"""
        output_columns = output_line.strip().split()
        table_name = "results"

        if output_columns[0][0] == "@":
            table_name = output_columns[0][1:] 
            output_columns.pop(0)

        if not self.table_columns.has_key(table_name):
            utils.newline_msg("ERR", "DB does not contain table named '%s'"%table_name)
            sys.exit(1)
        # try:
        #     output_column_names = [ i[0] for i in self.execute_query("SELECT column FROM output_tables WHERE name = '%s'"%(table_name)) ]
        # except:
        #     utils.newline_msg("ERR", "DB does not contain table named '%s'"%table_name)
        #     sys.exit(1)
        
        return table_name, output_columns

    def __getitem__(self, item):
        if item in self.values:
            return self.values[item]
        if item == 'spg_uid':
            return self.current_spg_uid
        if item == 'spg_rep':
            return self.current_spg_rep
        if item == 'spg_vsid':
            return self.current_spg_vsid

    def init_db(self):
        try:
            (self.command, ) = self.execute_query_fetchone( "SELECT value FROM information WHERE key = 'command'" )
        except:
            utils.newline_msg("FATAL",  "Cannot retreive information from database '%s'..."%utils.shorten_name(self.db_name))
            sys.exit(2)
        #:::~ get the names of the columns
        sel = self.execute_query("SELECT name FROM entities ORDER BY id")
        self.entities = [ i[0] for i in sel ]
        #:::~ get the names of the columns
        sel = self.execute_query("SELECT name FROM entities WHERE varies = 1 ORDER BY id")
        self.variables = [ i[0] for i in sel ]
        #:::~ get the names of the outputs
        
        self.table_columns = {}
        
        table_names = [i[0] for i in self.execute_query("SELECT DISTINCT name from output_tables")]
     ###   print table_names
        for table in table_names:
            fa = self.execute_query("SELECT column FROM output_tables WHERE name = '%s';"%table)
            
            self.table_columns[table] = ["spg_uid", "spg_vsid", "spg_rep"] + [i[0] for i in fa]

        # self.directory_vars = self.variables[:-1]


    def query_set_run_status(self, status, id = None, run_time = None):
        if id == None:
            id = self.current_spg_uid
        if run_time:
            self.execute_query( 'UPDATE run_status SET status ="%s", run_time=%f WHERE id = %d'% (status, run_time, id)  )
        else:
            self.execute_query( 'UPDATE run_status  SET status ="%s" WHERE id = %d'% (status,id)  )

    def __iter__(self):
        return self


    def next(self):

        query = "SELECT r.id, r.spg_vsid, r.spg_rep, %s FROM run_status AS r, values_set AS v "% ", ".join( ["v.%s"%i for i in self.entities] )  + \
                "WHERE r.status = 'N' AND v.id = r.spg_vsid ORDER BY r.id LIMIT 1"
        res = self.execute_query_fetchone(query)
        if res == None:
            raise StopIteration

        # print res, self.entities
        self.current_spg_uid  = res[0]
        self.current_spg_vsid   = res[1]
        self.current_spg_rep    = res[2]

        self.query_set_run_status("R", self.current_spg_uid)


        for (pos, ent)  in enumerate(self.entities):
            self.values[ ent ] = res[pos+3] # There are three parameters we get from the table, the others are the entities

        return self.values


    def variable_values(self):
        ret = {}
        for v in self.variables:
            ret[ v ] = self.values[v]

        return ret

    # def create_trees(self):
    #     if not self.directory_vars: return False
    #     ret = self.execute_query_fetchone("SELECT * FROM entities WHERE name LIKE 'store_%'")
    #
    #     return ret is not None
    #

    def get_updated_status(self):
        #:::~    'N': not run yet
        #:::~    'R': running
        #:::~    'D': successfully run (done)
        #:::~    'E': run but with non-zero error code
        ret_dict = {}
        ret_dict['value_set_with_rep'], = self.execute_query_fetchone("SELECT COUNT(*) FROM run_status ;")
        ret_dict['value_set'],  = self.execute_query_fetchone("SELECT COUNT(*) FROM values_set ;")
        ret_dict['process_done'] = 0
        ret_dict['process_not_run'] = 0
        ret_dict['process_running'] = 0
        ret_dict['process_error'] = 0
        ret_dict['max_run_time'], = self.execute_query_fetchone("SELECT max(run_time) FROM run_status WHERE status = 'D';")
        ret_dict['min_run_time'], = self.execute_query_fetchone("SELECT min(run_time) FROM run_status WHERE status = 'D';")
        ret_dict['avg_run_time'], = self.execute_query_fetchone("SELECT avg(run_time) FROM run_status WHERE status = 'D';")
        ret_dict['total_run_time'], = self.execute_query_fetchone("SELECT sum(run_time) FROM run_status WHERE status = 'D';")

        ret = self.execute_query("SELECT status, COUNT(*) FROM run_status GROUP BY status")
#        self.stat_done, self.stat_not_run, self.stat_running,self.stat_error = 0,0,0,0
        for (k,v) in ret:
            if k == "D":
                ret_dict['process_done']= v
            elif k == "N":
                ret_dict['process_not_run'] = v
            elif k == "R":
                ret_dict['process_running'] = v
            elif k == "E":
                ret_dict['process_error'] = v

        return ret_dict




################################################################################
################################################################################















################################################################################
################################################################################

class ParameterEnsembleExecutor(ParameterEnsemble):
    def __init__(self, full_name = "", id=-1, weight=1., queue = '*', status = 'R', repeat = 1, init_db = True):
        ParameterEnsemble.__init__(self, full_name , id, weight, queue , status , repeat , init_db )
#        self.init_db()
        os.chdir(self.path)

        if os.path.exists("./%s" % self.command):
            self.bin_dir = "."
        elif os.path.exists("%s%/bin/%s" % (BINARY_PATH, self.command)):
            self.bin_dir = "%s%/bin" % (BINARY_PATH)
        else:
            utils.newline_msg("ERR", "Fatal, binary '%s' not found" % self.command)
            sys.exit(1)

    def launch_process(self, remove_files = True):
         os.chdir(self.path)

         configuration_filename = "%s_%d.tmp_input" % (self.base_name, self.current_spg_uid)
         fconf = open(configuration_filename, "w")
         for k in self.values.keys():
                print >> fconf, k, utils.replace_values(self.values[k], self)
         fconf.close()

         fname_stdout = "%s_%s.tmp_stdout"% (self.base_name, self.current_spg_uid)
         fname_stderr = "%s_%s.tmp_stderr"% (self.base_name, self.current_spg_uid)
         file_stdout = open(fname_stdout, "w")
         file_stderr = open(fname_stderr, "w")

         cmd = "%s/%s %s" % (self.bin_dir, self.command, configuration_filename)

         started_time = time.time()
         proc = Popen(cmd, shell=True, stdin=PIPE, stdout=file_stdout, stderr=file_stderr, cwd=self.path, preexec_fn = preexec_function) #, env = {'PYTHONPATH':"${PYTHONPATH}:%s"%ROOT_DIR})
         self.return_code = proc.wait()
         finish_time = time.time()

         file_stdout.close()
         file_stderr.close()

         self.output = [i.strip() for i in open(fname_stdout, "r")]
         self.stderr = [i.strip() for i in open(fname_stderr, "r")]
         if remove_files:
             os.remove(configuration_filename)
             os.remove( fname_stdout )
             os.remove( fname_stderr )

         self.run_time = finish_time - started_time
         if self.run_time < 0: self.run_time = None

         # try:
         #     self.dump_result()
         # except:
         #    self.query_set_run_status("E")


    def dump_result(self):
         """ loads the next parameter atom from a parameter ensemble"""


         #:::~ status can be either
         #:::~    'N': not run
         #:::~    'R': running
         #:::~    'D': successfully run (done)
         #:::~    'E': run but with non-zero error code

         if self.return_code != 0:
             self.query_set_run_status("E")
             return

         for line in self.output:
             table_name, output_columns = self.parse_output_line(line)
             output_columns = [self.current_spg_uid, self.current_spg_vsid, self.current_spg_rep] + output_columns

             cc = 'INSERT INTO %s (%s) VALUES (%s) ' % (table_name, ", ".join(self.table_columns[table_name]),
                                                                   ", ".join(["'%s'" % str(i) for i in output_columns]))

#             print cc
#
             try:
                 self.execute_query(cc)
                 self.query_set_run_status("D", self.current_spg_uid, self.run_time)
             except sql.OperationalError as e:
                 v = str(e).split()
                 nv, nc = int(v[0]), int(v[3])
                 utils.newline_msg("DB", "Fatal, '%d' values for the '%d' output columns %s expected " % (nv-3,nc-3, self.table_columns[table_name][3:]))
                 sys.exit(1)
             #     self.query_set_run_status("E")

################################################################################
################################################################################
################################################################################



def preexec_function():
    # Ignore the SIGINT signal by setting the handler to the standard
    # signal handler SIG_IGN.
    signal.signal(signal.SIGINT, signal.SIG_IGN)







################################################################################
################################################################################

class ParameterEnsembleThreaded(ParameterEnsemble):
    def __init__(self, full_name="", id=-1, weight=1., queue='*', status='R', repeat=1, init_db=True):
        ParameterEnsemble.__init__(self, full_name, id, weight, queue, status, repeat, init_db)
        #        self.init_db()
        os.chdir(self.path)

        self.test_run = False

        if os.path.exists("./%s" % self.command):
            self.bin_dir = "."
        elif os.path.exists("%s%/bin/%s" % (BINARY_PATH, self.command)):
            self.bin_dir = "%s%/bin" % (BINARY_PATH)
        else:
            utils.newline_msg("ERR", "Fatal, binary '%s' not found" % self.command)
            sys.exit(1)

    def get_current_information(self):
        return self.current_spg_uid, self.current_spg_vsid, self.current_spg_rep, self.values

    def launch_process(self, current_run_id, current_vsid, current_rep, values):
        os.chdir(self.path)

        configuration_filename = "%s_%d.tmp_input" % (self.base_name,current_run_id)
        fconf = open(configuration_filename, "w")
        for k in self.values.keys():
            print >> fconf, k, utils.replace_values(values[k], self)
        fconf.close()

        fname_stdout = "%s_%s.tmp_stdout" % (self.base_name, current_run_id)
        fname_stderr = "%s_%s.tmp_stderr" % (self.base_name, current_run_id)
        file_stdout = open(fname_stdout, "w")
        file_stderr = open(fname_stderr, "w")

        started_time = time.time()
        cmd = "%s/%s  %s" % (self.bin_dir, self.command, configuration_filename)

        proc = Popen(cmd, shell=True, stdin=PIPE, stdout=file_stdout, stderr=file_stderr, cwd=self.path,  preexec_fn = preexec_function)
        return_code = proc.wait()
        finish_time = time.time()

        file_stdout.close()
        file_stderr.close()

        output = [i.strip() for i in open(fname_stdout, "r")]
        stderr = [i.strip() for i in open(fname_stderr, "r")]

        if self.test_run:
            if not os.path.exists("configuration-%s"%self.base_name):
                os.mkdir("configuration-%s"%self.base_name)
            os.rename(configuration_filename, "configuration-%s/%s"%(self.base_name,configuration_filename))
            os.rename(fname_stdout, "configuration-%s/%s" % (self.base_name, fname_stdout))
            os.rename(fname_stderr, "configuration-%s/%s" % (self.base_name, fname_stderr))

        else:
            os.remove(configuration_filename)
            os.remove(fname_stdout)
            os.remove(fname_stderr)

        run_time = finish_time - started_time
        if run_time < 0: run_time = None

        return current_run_id, current_vsid, current_rep, output, stderr, run_time, return_code


    def dump_result(self, current_uid, current_vsid, current_rep, output, stderr, run_time, return_code):
        """ loads the next parameter atom from a parameter ensemble"""

        if return_code != 0:
            #:::~ status can be either
            #:::~    'N': not run
            #:::~    'R': running
            #:::~    'D': successfully run (done)
            #:::~    'E': run but with non-zero error code
            self.query_set_run_status("E", current_uid)
            return

        for line in output:
            table_name, output_columns = self.parse_output_line(line)

            output_columns = [current_uid, current_vsid, current_rep] + output_columns
            cc = 'INSERT INTO %s (%s) VALUES (%s) ' % (table_name, ", ".join(self.table_columns[table_name]),
                                                           ", ".join(["'%s'" % str(i) for i in output_columns]))

            self.execute_query(cc)
#            self.query_set_run_status("D", current_uid, run_time)
















################################################################################
################################################################################
################################################################################
################################################################################

class ResultsDBQuery(ParameterEnsemble):
    def __init__(self, full_name = "", id=-1, weight=1., queue = '*', status = 'R', repeat = 1, init_db = True):

        ParameterEnsemble.__init__(self, full_name , id, weight, queue , status , repeat  , init_db )
        # self.separated_vars = self.variables[:-2]
        # self.coalesced_vars = self.variables[-2:-1]
        # self.in_table_vars =  self.variables[-1:]

        self.separated_vars = []
        self.coalesced_vars = []
        self.vars_in_table = self.variables[:]

    def setup_vars_in_table(self, conf):
        """which are the variables that are inside of the output file, orphaned variables are sent into the coalesced ones"""
        if conf.strip() != "" :
            in_table_vars = conf.split(",")
        else:
            in_table_vars = []
        if set(in_table_vars).issubset( set(self.variables) ):
            self.vars_in_table = in_table_vars
            self.coalesced_vars = [i for i in self.coalesced_vars if (i not in self.vars_in_table)]
            self.separated_vars = [i for i in self.separated_vars if (i not in self.vars_in_table)]
            
            orphaned = set(self.variables) - set(self.separated_vars) - set(self.vars_in_table) - set(self.coalesced_vars)
            if len(orphaned) > 0:
                utils.newline_msg("VAR", "orphaned variables '%s' added to separated variables"%orphaned, indent=4)
                for i in orphaned: self.coalesced_vars.append(i)
            print "  +- structure = %s - %s - %s "%(self.separated_vars, self.coalesced_vars, self.vars_in_table)
        else:
        #    print in_table_vars, conf
            utils.newline_msg("VAR", "the variables '%s' are not recognised"%set(in_table_vars)-set(self.variables) )
        
                
    def setup_vars_separated(self, conf):
        """Which variables are separated in different directories, orphaned variables are sent into the coalesced ones"""
        if conf.strip() != "" :
            separated = conf.split(",")
        else:
            separated = []
        if set(separated).issubset( set(self.variables) ):
            self.separated_vars = separated
            self.coalesced_vars = [ i for i in self.coalesced_vars if ( i not in self.separated_vars )  ]
            self.vars_in_table = [i for i in self.vars_in_table if (i not in self.separated_vars)]
            orphaned = set(self.variables) - set(self.separated_vars) - set(self.vars_in_table) - set(self.coalesced_vars)
            if len(orphaned) > 0:
                utils.newline_msg("VAR", "orphaned variables '%s' added to separated variables"%orphaned, indent=4)
                for i in orphaned: self.coalesced_vars.append(i)
            print "  +- structure = %s - %s - %s "%(self.separated_vars, self.coalesced_vars, self.vars_in_table)
        else:
            utils.newline_msg("VAR", "the variables '%s' are not recognised"%set(separated)-set(self.variables) )

    def setup_vars_coalesced(self, conf):
        """Which variables are coalesced into the same files, orphaned variables are sent into the separated ones"""
        if conf.strip() != "" :
            coalesced = conf.split(",")
        else:
            coalesced = []
        if set(coalesced).issubset( set(self.variables) ):
            self.coalesced_vars = coalesced
            self.separated_vars = [ i for i in self.separated_vars if ( i not in self.coalesced_vars ) ]
            self.vars_in_table = [i for i in self.vars_in_table if (i not in self.coalesced_vars)]
            orphaned = set(self.variables) - set(self.separated_vars) - set(self.vars_in_table) - set(self.coalesced_vars)
            if len(orphaned) > 0:
                utils.newline_msg("VAR", "orphaned variables '%s' added to separated variables"%orphaned, indent=4)
                for i in orphaned: self.separated_vars.append(i)
            print "  +- structure = %s - %s - %s "%(self.separated_vars, self.coalesced_vars, self.vars_in_table)
        else:
            utils.newline_msg("VAR", "the variables '%s' are not recognised"%set(coalesced)-set(self.variables) )



    def clean_dict(self,dict_to_clean):
        """ adds quotes to strings """
        for i in dict_to_clean:  
            try:
                float( dict_to_clean[i] ) 
            except:
                dict_to_clean[ i ] = "'%s'"%( dict_to_clean[i ].replace("'","").replace('"',"") )



    def values_set_table(self):

        id_cols = ["spg_uid"]
        local_vars_in_table = self.entities

        local_var_query = ""
        if len(local_vars_in_table) > 0:
            local_var_query = "%s " % ",".join(["v.%s" % v for v in local_vars_in_table])

        query = "SELECT rs.spg_vsid, rs.spg_rep, rs.id, %s FROM run_status AS rs, values_set AS v WHERE rs.spg_vsid = v.id " % (local_var_query)

        query = query.replace("''", "'").replace("'\"", "'")
#        print query

        base_table = self.execute_query(query)
        query_cols = ["spg_vsid", "spg_rep", "spg_uid"] + local_vars_in_table

        ret_table = [
            [ utils.replace_values(el, dict( zip( query_cols, row ) ) ) for el in row[2:] ]
            for row in base_table ]



        header = id_cols + local_vars_in_table
        return header, ret_table

    def result_table(self, table="results", table_selector = "grouped_vars", restrict_to_values={}):
        """
        Args:
            table: the table in the database
            column_selector: possible values ... "grouped_vars" only the variables (grouped by value) are put in the output table
                                                 "raw_vars"     only the variables are put in the output table
                                                 "only_uid"     only the uid is output
                                                 "full"         all ids and variables are output in table

            restrict_to_values: a dictionary of variable values which act as filter

        Returns: a 2-tuple... the header and the actual table

        """



        if table_selector == "grouped_vars" or table_selector == "raw_vars":
            id_cols = []
            local_vars_in_table = self.vars_in_table
            output_columns = self.table_columns[table][3:]  #:::~ skips the spg_uid, spg_vsid and spg_rep columns ...
        elif table_selector == "only_uid":
            id_cols = self.table_columns[table][:1]
            local_vars_in_table = []
            output_columns =  self.table_columns[table][3:]
        elif table_selector == "full":
            id_cols = self.table_columns[table][:3]
            local_vars_in_table = self.vars_in_table
            output_columns = self.table_columns[table][3:]
        else:
            utils.newline_msg("ERR", "table selector ''")


        # print table_selector, id_cols, local_vars_in_table,output_columns

        id_cols_query = ""
        if len(id_cols) > 0:
            id_cols_query = "%s, " % ",".join(["r.%s" % v for v in id_cols])

        local_var_query = ""
        if len(local_vars_in_table) > 0:
            local_var_query = "%s, " % ",".join(["v.%s" % v for v in local_vars_in_table])

        if table_selector == "grouped_vars":
            output_columns_query = " %s" % ",".join(["AVG(r.%s)" % v for v in output_columns])
        else:
            output_columns_query = " %s" % ",".join(["r.%s" % v for v in output_columns])

        query = "SELECT %s %s %s FROM %s AS r, values_set AS v WHERE r.spg_vsid = v.id " % (id_cols_query, local_var_query, output_columns_query, table)

        if restrict_to_values:
            self.clean_dict(restrict_to_values)
            restrict_to_values_query = " AND ".join(["v.%s = '%s'"%(v, restrict_to_values[v]) for v in restrict_to_values.keys()])
            query = "%s AND %s "%(query, restrict_to_values_query)

        if table_selector == "grouped_vars":
            query = "%s GROUP BY v.id" % (query)
        if table_selector == "full" or table_selector == "only_uid":
            query = "%s ORDER BY r.spg_uid" % (query)

        query = query.replace("''", "'").replace("'\"", "'")
        header =  id_cols + local_vars_in_table + output_columns

#        print query
        return header, self.execute_query(query)



    def __iter__(self):
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
        d = {}
        for i in pairs:
            d.clear()
            for j in range( len( vars_to_separate ) ):
                d[vars_to_separate[j] ] = i[j]
            yield d


    def update_results_from_data(self, table_file, table_name = "results", sep = "," ):
        table = csv.reader(open(table_file), delimiter=sep, lineterminator="\n")

        header = table.next()
        header = header[:1] + ['spg_vsid', 'spg_rep'] + header[1:]
        for row in table:
            uid = int(row[0])
            (vsid, rep) =self.execute_query_fetchone("SELECT spg_vsid, spg_rep FROM run_status WHERE id = %s"%uid)
            vals = row[1:]
            full_row = [uid,vsid, rep] + row[1:]
            cc = 'INSERT INTO %s (%s) VALUES (%s) ' % (table_name, ", ".join(header),
                                                   ", ".join(["'%s'" % str(i) for i in full_row]))

            self.execute_query(cc)

            self.query_set_run_status( "D", uid)


            # def result_table(self, table="results", restrict_to_values={}, raw_data=False):
            #     # def result_table(self, table="results", restrict_to_values={}, raw_data=False, restrict_by_val=False,
            #     #                  output_columns=[]):
            #
            #     # print restrict_to_values
            #     self.clean_dict(restrict_to_values)
            #
            #     local_var_query = ""
            #     if len(self.in_table_vars) > 0:
            #         local_var_query = "%s, " % ",".join(["v.%s" % v for v in self.in_table_vars])
            #
            #     output_columns = self.table_columns[table][2:]  #:::~ skips the spg_uid and spg_vsid columns ...
            #
            #     # if "spg_runid" in output_columns:
            #     #         output_columns.remove("spg_runid")
            #     # if "spg_vsid" in output_columns:
            #     #         output_columns.remove("spg_vsid")
            #     output_columns_query = ""
            #
            #     if not raw_data:
            #         # if len(output_columns ) == 1:
            #         #     output_columns_query = "AVG(r.%s) "%output_columns[0]
            #         # elif len(output_columns) > 1:
            #         output_columns_query = " %s" % ",".join(["AVG(r.%s)" % v for v in output_columns])
            #     else:
            #         # if len(output_columns ) == 1:
            #         #     output_columns_query = "r.%s "%output_columns[0]
            #         # elif len(output_columns) > 1:
            #         output_columns_query = " %s" % ",".join(["r.%s" % v for v in output_columns])
            #
            #     query = "SELECT %s %s FROM %s AS r, values_set AS v WHERE r.spg_vsid = v.id " % (local_var_query, output_columns_query, table)
            #
            #     if not raw_data:
            #         query = "%s GROUP BY v.id" % (query)
            #
            # :::~ This command was needed only because of a mistake in the id stores in the results table
            # restrict_to_values_query = ""
            # if restrict_to_values:
            #     restrict_to_values_query = " AND ".join(["v.%s = '%s'"%(v, restrict_to_values[v]) for v in restrict_to_values.keys()])
            #     if restrict_to_values_query :
            #         restrict_to_values_query = "AND %s"%restrict_to_values_query
            # query = "%s  %s "%(query, restrict_to_values_query)
            # if not raw_data :
            #     query = "%s GROUP BY v.id" % (query)
            #     if restrict_by_val:
            #         query = "%s  GROUP BY %s"%(query, local_var_query.strip(", "))
            #         #     else:
            #         query=query.replace("''", "'").replace("'\"", "'")
            #         header = self.in_table_vars + output_columns
            #
            # #        print header, query
            #         return header, self.execute_query(query)

            # def result_id_table(self, table="results"):
            #     query = "SELECT %s FROM %s ORDER BY id " % (",".join(self.table_columns[table]), table)
            #
            #     return self.table_columns[table], self.execute_query(query)

            # def table_header(self, table='results',output_column = []):
            #
            #     var_cols = self.in_table_vars
            #
            #     if not output_column:
            #         output_column = self.table_columns[table][:]
            #     if "vsid" in output_column:
            #         output_column.remove("vsid")
            #     return var_cols+output_column


# class ParameterEnsembleInputFilesGenerator(ParameterEnsemble):
#     def __init__(self, full_name="", id=-1, weight=1., queue='*', status='R', repeat=1, init_db=False):
#         ParameterEnsemble.__init__(self, full_name, id, weight, queue, status, repeat, init_db)
#         os.chdir(self.path)
#
#     def launch_process(self):
#         #        pwd = os.path.abspath(".")
#         #     if self.directory_vars or self.create_trees():
#         #         dir = utils.generate_string(self.values,self.directory_vars, joining_string = "/")
#         #         if not os.path.exists(dir): os.makedirs(dir)
#         #        os.chdir(dir)
#         configuration_filename = "input_%.8d.dat" % (self.current_valuesset_id)
#         fconf = open(configuration_filename, "w")
#
#         for k in self.values.keys():
#             print >> fconf, k, utils.replace_values(self.values[k], skip_id=False)
#         fconf.close()


################################################################################
################################################################################
################################################################################

