#!/usr/bin/python


from spg.parameter import ParameterEnsembleExecutor, ParameterEnsembleInputFilesGenerator
from spg import BINARY_PATH, ROOT_DIR


import os, os.path
import optparse


if __name__ == "__main__":

    parser = optparse.OptionParser(usage = "usage: %prog [options] project_id1 project_id2 project_id3... ")
    parser.add_option("--timeout", type="int", action='store', dest="timeout",
                            default = 60 , help = "timeout for database connection" )

    parser.add_option("--tree", action='store_true', dest="tree",
                       help = "whether to create a directory tree with the key-value pairs" )

    parser.add_option("--dummy", action='store_true', dest="dummy",
                       help = "generates the input files, only" )

    parser.add_option("-d","--directory-var", action='store', type = "string", dest="directory_vars",
                       default = False, help = "which variables to store as directories, only if tree" )

    parser.add_option("--root", action='store', type = "string", dest="root_dir",
                       default = False, help = "whether to change the global RUN_DIR environment variable" )    

    options, args = parser.parse_args()
    
    if options.root_dir:
        ROOT_DIR = os.path.abspath(options.root_dir)
        
    
    if len(args) == 0:
        args = ["results.sqlite"]
    
    for i_arg in args:
      if ".sqlite" not in i_arg:
          db_name = i_arg.replace("parameters","").replace(".dat","")
          db_name = "results%s.sqlite"%db_name
      else:
          db_name = i_arg
      full_name = os.path.realpath(db_name)
      path, out = os.path.split(full_name)
      if options.dummy:
          executor = ParameterEnsembleInputFilesGenerator( full_name )
      else:
          executor = ParameterEnsembleExecutor( full_name )
      if options.tree:
          executor.generate_tree( options.directory_vars )
      

      for values in executor:
      #    print values
              executor.launch_process()

      if options.tree:
          os.chdir(path)
      
      if options.dummy:
          executor.reset()
          #      parser.init_db()
#          parser.fill_status(repeat = options.repeat )

