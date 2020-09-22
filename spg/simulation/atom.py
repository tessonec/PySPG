from spg import utils
#from spg import ROOT_DIR



import os.path, sys, time
import pickle 
from subprocess import Popen, PIPE
import sqlite3 as sql



################################################################################
################################################################################
################################################################################
#
# class ParameterAtom:
#     def __init__(self, fname, full_db_name = None):
#         self.command = None
#
#         self.full_db_name = full_db_name
#         if self.full_db_name :
#             self.path, db_name = os.path.split(self.full_db_name)
#
#         self.in_name = fname
#         self.values = {}
#         self.entities = []
#         self.output = ""
#         self.return_code  = None
#         self.current_run_id  = None
#         self.current_valuesset_id = None
#
#
#     def load(self, src = 'queue', no_rm = False):
#         full_inname = "%s/%s"%(src,self.in_name)
#         vals = pickle.load( open(full_inname)  )
#         self.__dict__ = vals.__dict__
# #        try:
# #          self.path = self.full_name[:self.full_name.rfind("/")]
# #          self.db_name = self.full_name[self.full_name.rfind("/")+1:]
# #        except:
# #          pass
#         if no_rm: return
#         os.remove( full_inname )
#
#     def dump(self,src = 'run'):
#         full_name = "%s/%s"%(src,self.in_name)
#         pickle.dump( self, open(full_name, "w" ) )
#
#
#     def load_next_from_ensemble(self, param_ens):
#         """ loads the next parameter atom from a parameter ensemble"""
#
#         #:::~ Table with the name of the executable
#
#         (self.command, ) = param_ens.query_master_fetchone("SELECT value FROM information WHERE key = 'command' ")
#         #:::~ get the names of the columns
#         sel = param_ens.query_master_db("SELECT name FROM entities ORDER BY id")
#         self.entities = [ i[0] for i in sel ]
#
#         sel = param_ens.query_master_db("SELECT name FROM entities WHERE varies = 1 ORDER BY id")
#         self.variables = [ i[0] for i in sel ]
#
#         res = param_ens.query_master_fetchone(
#                     "SELECT r.id, r.vsid, %s FROM run_status AS r, values_set AS v "% ", ".join(["v.%s"%i for i in self.entities]) +
#                     "WHERE r.status = 'N' AND v.id = r.vsid ORDER BY r.id LIMIT 1"
#                    )
#         #     print res
#         if res == None:
#             return None
#
#         self.current_run_id  = res[0]
#         self.current_valuesset_id= res[1]
#         param_ens.query_master_db('UPDATE run_status SET status ="R" WHERE id = %d' % self.current_run_id)
# #        connection.commit()
#         for i in range( len(self.entities) ):
#             self.values[ self.entities[i] ] = res[i+2]
#
# #        sql_db.close()
# #        del sql_db
#         return self.values
#
#
#     def dump_result_in_ensemble(self, param_ens):
#         """ loads the next parameter atom from a parameter ensemble"""
#
#         if self.return_code == 0:
#      #       print self.output
#             for line in self.output:
#
#                 table_name, output_column_names, output_columns = param_ens.parse_output_line( line )
#         #        print output_column_names
#                 output_columns.insert(0, self.current_valuesset_id) # WARNING: MZ FOUND THAT BEFORE WE HAVE BEEN SETTING current_run_id
#                 cc = 'INSERT INTO %s (%s) VALUES (%s) ' % (table_name, ", ".join(output_column_names) , ", ".join(["'%s'" % str(i) for i in output_columns ]))
#                 #print cc
#                 try:
#                     param_ens.query_master_db(cc)
#                     param_ens.query_master_db('UPDATE run_status SET status ="D" WHERE id = %d' % self.current_run_id)
#                 except:
#                     param_ens.query_master_db('UPDATE run_status SET status ="E" WHERE id = %d' % self.current_run_id)
#             flog = open(self.full_db_name.replace("spgql", "log"), "aw")
#             flog_err = open(self.full_db_name.replace("spgql", "err"), "aw")
#             if not hasattr(self,'run_time'):
#                 self.run_time = -1
#             utils.newline_msg( "INF",  "{%s} %s: ret=%s -- %s,%s -- run_time=%s"  % (self.command, self.in_name, self.return_code , self.current_run_id, self.current_valuesset_id,  self.run_time ) , stream = flog )
#             print >> flog,  "     values: ", self.values
#             print >> flog,  "OUT--  ","       \n ".join( self.output )
#
#             try:
#                 print >> flog_err,  "     \n ".join( self.stderr )
#             except:
#                 utils.newline_msg( "WRN", "NO_STDERR", stream = flog_err)
#             flog.close()
#             flog_err.close()
#
#         else:
#             #:::~ status can be either
#             #:::~    'N': not run
#             #:::~    'R': running
#             #:::~    'D': successfully run (done)
#             #:::~    'E': run but with non-zero error code
#             param_ens.query_master_db('UPDATE run_status SET status ="E" WHERE id = %d' % self.current_run_id)
#
#             flog = open(self.full_db_name.replace("spgql", "log"), "aw")
#             flog_err = open(self.full_db_name.replace("spgql", "err"), "aw")
#             if not hasattr(self,'run_time'):
#                 self.run_time = -1
#             utils.newline_msg( "INF",  "{%s} %s: ret=%s -- %s,%s -- run_time=%s"  % (self.command, self.in_name, self.return_code , self.current_run_id, self.current_valuesset_id,  self.run_time ) , stream = flog )
#             print >> flog,  "     values: ", self.values
#             print >> flog,  "OUT--  ","       ".join( self.output )
#
#             try:
#                 print >> flog_err,  "     \n ".join( self.stderr )
#             except:
#                 utils.newline_msg( "WRN", "NO_STDERR", stream = flog_err)
#             flog.close()
#             flog_err.close()
#
# #        connection.commit()
#         #conn.close()
#         #del cursor
#         #del conn
#
#
#
# ################################################################################
# ################################################################################
#
# class ParameterAtomExecutor(ParameterAtom):
#     def __init__(self, fname, full_db_name = None):
#         ParameterAtom.__init__(self, fname, full_db_name )
#         if os.path.exists("./%s"%self.command):
#             self.bin_dir = "."
#         elif os.path.exists("%s%/bin/%s"%(ROOT_DIR, self.command)):
#             self.bin_dir = "%s%/bin"%(ROOT_DIR)
#         else:
#             utils.newline_msg("ERR","Fatal, binary '%s' not found"%self.command)
#             sys.exit(1)
#
#     def create_tree(self):
#         for k in self.values:
#             if k.find("store") != -1: return True
#         return False
#
#     def launch_process(self, configuration_filename):
#         os.chdir(self.path)
#         started_time = time.time()
#         if self.create_tree():
#             dir_n = utils.generate_string(self.values, self.variables, joining_string = "/")
#             if not os.path.exists(dir_n):
#                 os.makedirs(dir_n)
#             os.chdir(dir_n)
#
# #      configuration_filename = "input_%s_%d.dat"%(self.db_name, self.current_run_id)
#         fconf = open(configuration_filename,"w")
#         for k in self.values.keys():
#             print >> fconf, k, utils.replace_values(self.values[k], self)
#         fconf.close()
#
#
#         file_stdout = open("%s.tmp_stdout"%self.current_run_id, "w")
#         file_stderr = open("%s.tmp_stderr"%self.current_run_id, "w")
#
#
#         cmd = "%s/%s -i %s"%(self.bin_dir , self.command, configuration_filename )
#
#         proc = Popen(cmd, shell = True, stdin = PIPE, stdout = file_stdout, stderr = file_stderr )
#         self.return_code = proc.wait()
#
#         file_stdout.close()
#         file_stderr.close()
#         finish_time = time.time()
#
#         self.output =  [i.strip() for i in open("%s.tmp_stdout"%self.current_run_id, "r")]
#         self.stderr =  [i.strip() for i in open("%s.tmp_stderr"%self.current_run_id, "r")]
#
#
#         os.remove(configuration_filename)
#
#         self.run_time = finish_time - started_time