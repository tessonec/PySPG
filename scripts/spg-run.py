#!/usr/bin/python


import sqlite3 as sql

from spg import Parser
import spg

class Launcher(Parser):
    def __init__(self, stream=None, db_name = "results.sqlite"):
        Parser.__init__(self, stream)
        self.connection =  sql.connect(db_name)
#        connection.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        self.cursor = self.connection.cursor()
        self.__init_db()
        
    def __init_db(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS constants "
                            "(id INTEGER PRIMARY KEY, name CHAR(64), value CHAR(64))"
                            )
       
        for k in self.constant_items():
            self.cursor.execute( "INSERT INTO constants (name, value) VALUES (?,?)",(k, self[k]) )
            
        vi = self.varying_items()
        elements = "CREATE TABLE IF NOT EXISTS varying (id INTEGER PRIMARY KEY,  %s )"%( ", ".join([ "%s CHAR(64)"%i for i in vi ] ) )
#        print elements
        self.cursor.execute(elements)
         
                  
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










parser = Launcher( stream = open("param.dat") )

#for i in parser:
#    print i
