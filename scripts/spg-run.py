#!/usr/bin/python


from spg.parameter import *
import spg.utils as utils

import os, os.path, optparse, sys

def translate_name(st):
    """translates the parameters filename and the  database name
       into the other and viceversa (returns a duple: param_name, db_name)"""
    full_name = os.path.realpath(st)

    if not os.path.exists(full_name):
        utils.newline_msg("ERR", "database '%s' does not exist" % full_name)
        return None

    path, st = os.path.split(full_name)
    base_name, ext = os.path.splitext(st)

    return full_name, path, base_name, ext

if __name__ == "__main__":

    parser = optparse.OptionParser(usage = "usage: %prog [options] project_id1 project_id2 project_id3... ")

    parser.add_option("--init", action='store_true', dest="initialise",
                      help="initialise the database ")

    parser.add_option("--repeat", action='store', dest="repeat", default=1, type=int,
                      help="initialise the database ")

    parser.add_option("--purge", action='store_true', dest="purge",
                      help="removes any old database.  IMPLIES DATA LOSS")

    parser.add_option("--dummy", action='store_true', dest="dummy",
                      help="generates the input files, only")

    parser.add_option("--verbose", action='store_true', dest="verbose",
                      help="more verbose output")

    parser.add_option("-d","--directory-var", action='store', type = "string", dest="directory_vars",
                       default = False, help = "which variables to store as directories, only if tree" )


    options, args = parser.parse_args()
    

    for i_arg in args:
      full_name, path, base_name, extension = translate_name(i_arg)

      db_name = "%s/%s.sqlite" % (path, base_name)
      sim_name = "%s/%s.spg" % (path, base_name)
      if options.purge and os.path.exists( db_name ):
          os.remove( db_name )
      if options.initialise:
          utils.newline_msg("MSG", "initialising database")
          parser = EnsembleBuilder(stream=open(sim_name), db_name=db_name)
          parser.init_db()
          parser.fill_status(repeat=options.repeat)
          del parser

      utils.newline_msg("MSG", "running simulations")
      if options.dummy:
          executor = ParameterEnsembleInputFilesGenerator( db_name )
      else:
          executor = ParameterEnsembleExecutor( db_name )

      executor.init_db()
      for values in executor:
          if options.verbose:
              utils.inline_msg("RUN", "[%s] %s"%(executor.current_run_id,executor.values) )
          try:
             executor.launch_process()
          except (KeyboardInterrupt,):
              executor.restore_last_run()
              print >> sys.stderr
              utils.newline_msg("SYS", "keyboard interrupted, exiting")
              sys.exit(1)

      if options.tree:
          os.chdir(path)
      
      if options.dummy:
          executor.reset()


