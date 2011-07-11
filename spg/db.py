# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 11:23:41 2011

@author: Claudio Tessone <tessonec@ethz.ch>
"""

import utils
import params
import parser 
import iterator

import sys
import sqlite3 as sql

class DBBuilder(parser.MultIteratorParser):
    def __init__(self, stream=None, db_name = "results.sqlite", timeout = 5):
        parser.MultIteratorParser.__init__(self, stream)
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
            self.cursor.execute("INSERT INTO executable (name) VALUES (?)",(self.command,))
            self.connection.commit()

        #:::~ Table with the defined entities
        self.cursor.execute("CREATE TABLE IF NOT EXISTS entities "
                            "(id INTEGER PRIMARY KEY, name CHAR(64), varies INTEGER)"
                            )

        self.cursor.execute( "SELECT COUNT(*) FROM entities ")
        n_items = self.cursor.fetchone()
        if n_items[0] == 0: # table has not been filled
            for i in self.data:
                varies = 1 if (i.__class__ != iterator.IterConstant) else 0
                self.cursor.execute( "INSERT INTO entities (name, varies) VALUES (?,?)",(i.name,  varies) )
        else:
            self.cursor.execute( "SELECT name FROM entities ")
            entities = set([i[0] for i in self.cursor])
            s_names = set(self.names)
            if entities != set(self.names):
                utils.newline_msg("ERR", "parameter (was %s, is %s)"%(entities, s_names))
                sys.exit(1)
            
        self.connection.commit()

        elements = "CREATE TABLE IF NOT EXISTS values_set (id INTEGER PRIMARY KEY,  %s )"%( ", ".join([ "%s CHAR(64)"%i for i in self.names ] ) )
        self.cursor.execute(elements)
        
        elements = "INSERT INTO values_set ( %s ) VALUES (%s)"%(   ", ".join([ "%s "%i for i in self.names ] ), ", ".join( "?" for i in self.names ) )

        self.possible_varying_ids = []
        i_try = 0
        commited = False
        while i_try < retry and not commited:
            i_try += 1
            for i in self:
                self.cursor.execute( elements, [ self[i] for i in self.names] )
                self.possible_varying_ids.append(self.cursor.lastrowid)
            self.connection.commit()
            commited = True
              
        if not commited:
              utils.newline_msg("ERR", "database didn't unlock, exiting")
          
        self.number_of_columns = 0
        for ic, iv in self.stdout_contents:
            if iv["type"] == "xy":
                self.number_of_columns += 1
            if iv["type"] == "xydy":
                self.number_of_columns += 2


        results = "CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, values_set_id INTEGER,  %s , FOREIGN KEY(values_set_id) REFERENCES values_set(id))"%( ", ".join([ "%s CHAR(64)"%ic for ic, iv in self.stdout_contents ] ) )
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
       self.cursor.execute('UPDATE run_status SET status = "N" ')
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

