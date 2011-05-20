#!/usr/bin/python


import spg

import spg.params as params

import sqlite3 as sql
import sys


class DBBuilder(spg.MultIteratorParser):
    def __init__(self, stream=None, db_name = "results.sqlite"):
        spg.parser.MultIteratorParser.__init__(self, stream)
        self.connection =  sql.connect(db_name)
#        connection.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        self.cursor = self.connection.cursor()
#        self.__init_db()
#        self.__init_db()
        
    def init_db(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS constants "
                            "(id INTEGER PRIMARY KEY, name CHAR(64), value CHAR(64))"
                            )
        for k in self.constant_items():
            self.cursor.execute( "SELECT value FROM constants WHERE name = '%s'"%k)
            prev_val = self.cursor.fetchone()
            if prev_val is not None:
                if prev_val[0] != self[k]:
                    spg.utils.newline_msg("ERR", "conficting values for parameter '%s' (was %s, is %s)"%(k, self[k], prev_val[0]))
                    sys.exit(1)
            else:
                self.cursor.execute( "INSERT INTO constants (name, value) VALUES (?,?)",(k, self[k]) )
            
        self.connection.commit()
        vi = self.varying_items()
        elements = "CREATE TABLE IF NOT EXISTS varying (id INTEGER PRIMARY KEY,  %s )"%( ", ".join([ "%s CHAR(64)"%i for i in vi ] ) )
#        print elements
        self.cursor.execute(elements)
         
        elements = "INSERT INTO varying ( %s ) VALUES (%s)"%(   ", ".join([ "%s "%i for i in vi ] ), ", ".join( "?" for i in vi) )
        
        for i in self:
            self.cursor.execute( elements, [ self[i] for i in vi] )
        self.connection.commit()
         
        params.check_consistency(self.command, self)        
        #cursor.execute("ALTER TABLE projects ADD COLUMN downloaded INTEGER")
        #cursor.execute("ALTER TABLE projects ADD COLUMN error INTEGER") 
        #connection.commit()

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










parser = DBBuilder( stream = open("param.dat") )

parser.init_db()

