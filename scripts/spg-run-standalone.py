#!/usr/bin/python


from spg.simulation import *
import spg.utils as utils

import os, os.path, optparse, sys



if __name__ == "__main__":

    parser = optparse.OptionParser(usage = "usage: %prog [options] project_id1 project_id2 project_id3... ")

    parser.add_option("--init", action='store_true', dest="initialise",
                      help="initialise the database ")

    parser.add_option("--repeat", action='store', dest="repeat", default=1, type=int,
                      help="initialise the database ")

    parser.add_option("--purge", action='store_true', dest="purge",
                      help="removes any old database.  IMPLIES DATA LOSS")
    #
    # parser.add_option("--dummy", action='store_true', dest="dummy",
    #                   help="generates the input files, only")

    parser.add_option("--verbose", action='store_true', dest="verbose",
                      help="more verbose output")

    parser.add_option("--test-run", action='store_true', dest="test_run",
                      help="runs once and preserves the temporary files")

#    parser.add_option("-d","--directory-var", action='store', type = "string", dest="directory_vars",
#                       default = False, help = "which variables to store as directories, only if tree" )


    options, args = parser.parse_args()
    

    for i_arg in args:
      full_name, path, base_name, extension = utils.translate_name(i_arg)

      db_name = "%s/%s.spgql" % (path, base_name)
     # sim_name = "%s/%s.spg" % (path, base_name)
      if options.purge and os.path.exists( db_name ):
          os.remove( db_name )
      if options.initialise or not os.path.exists( db_name ):
          utils.newline_msg("MSG", "initialising database")
          parser = MultIteratorDBBuilder(db_name=db_name)
          parser.init_db()
          parser.fill_status(repeat=options.repeat)
          del parser

      utils.newline_msg("MSG", "running simulation")
 #     if options.dummy:
 #         executor = ParameterEnsembleInputFilesGenerator( db_name )
 #     else:
      executor = ParameterEnsembleExecutor( db_name )

      executor.init_db()
      if options.test_run:
          executor.next()
          executor.launch_process( remove_files=False)

          executor.dump_result()
          continue

      for values in executor:
          if options.verbose:
              utils.inline_msg("RUN", "[%s] %s" % (executor.current_spg_uid, executor.variable_values()))
          # executor.launch_process()
          try:
             executor.launch_process()
             executor.dump_result()
          except (KeyboardInterrupt,):
              print >> sys.stderr
              utils.newline_msg("SYS", "keyboard interrupted, exiting")
              executor.query_set_run_status("N")
              sys.exit(1)

 #     if options.tree:
 #         os.chdir(path)
      
#      if options.dummy:
#          executor.reset()


