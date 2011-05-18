#!/usr/bin/python


import sqlite3 as sql

from spg import Parser

class Launcher(Parser):
    def __init__(self, stream=None, db_name = "results.sqlite"):
        Parser.__init__(self, stream)
        self.connection =  sqlite3.connect(db_name)
#        connection.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        self.cursor = self.connection.cursor()
        self.__init_db()
        
    def __init_db(self):
        cursor.execute("CREATE TABLE values ADD COLUMN groupid INTEGER") 
        #cursor.execute("ALTER TABLE projects ADD COLUMN downloaded INTEGER")
        #cursor.execute("ALTER TABLE projects ADD COLUMN error INTEGER") 
        #connection.commit()











parser = Launcher()

parser.fetch( open("param.dat") )

for i in parser:
    print i
