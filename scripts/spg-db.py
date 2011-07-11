#!/usr/bin/python


#import spg.params as params
import spg.utils as utils
from spg.db import DBBuilder


import sqlite3 as sql
import sys, optparse
import os, os.path





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
      parser.fill_status(repeat = int(repeat))


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
    connection = sql.connect("%s/spg_pool.sqlite"%utils.VAR_PATH)
    cursor = connection.cursor()
    cursor.execute( "DELETE FROM dbs WHERE full_name = ?",(os.path.realpath(db_name),) )

    connection.commit()

def translate_name(st):
    full_name = st
    if not os.path.exists(full_name):
       full_name = os.path.expanduser( "~/%s"%st )
    if not os.path.exists(full_name):
        utils.newline_msg("ERR","database '%s' does not exist"%st)
        sys.exit(2)
  #  print ">", full_name
    path, st = os.path.split(full_name)
    if path:
      os.chdir(path)
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



dict_functions = { "init":init_db, "clean": clean_db, "clean-all": clean_all_db , "remove": remove_db}

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


