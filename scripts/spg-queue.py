#!/usr/bin/python

import cmd
import sys

from spg.master import MasterDB


class QueueCommandParser(cmd.Cmd):
    """command processor for the queues."""

    FRIENDS = [ 'Alice', 'Adam', 'Barbara', 'Bob' ]
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "| spg-queue :::~ "
        self.current_queue = None 
        self.master_db =  MasterDB()
        self.possible_keys = ['max_jobs', 'status']

    def __update_queue_list(self):
        self.queues = self.master_db.execute_query("SELECT * FROM queues ORDER BY id")
        

    def do_ls(self, c):
        """lists the queues in the master database """
        self.__update_queue_list()
        for (id, name, max_jobs, status) in self.queues:
            print "%5d: %16s  - J: %2d - S: '%s'"%(id, name, max_jobs, status)
###  CREATE TABLE IF NOT EXISTS queues 
###           ( id INTEGER PRIMARY KEY, name CHAR(64), max_jobs INTEGER, 
###           status CHAR(1) )


    def do_init(self, c):
        """adds queue queue"""
        c = c.split()
        queue = c[0]
        self.__update_queue_list()
        for (id, name, max_jobs, status) in self.queues:
            if name == queue: 
                utils.newline_msg("ERR", "queue '%s' already exists"%queue, 2)
                return 
        self.master_db.execute_query( "INSERT INTO queues (name, max_jobs, status) VALUES (?,?,?)",(queue,  1, 'S'))
        self.current_queue = queue
        if len(c) >1: self.do_set( ":".join( c[1:] ) )


    def do_set(self, c):
        """sets a VAR1=VALUE1[:VAR2=VALUE2]
        sets a value in the currently loaded database """
        ret = utils.parse_to_dict(c, allowed_keys=self.possible_keys)
#        for k in ret:
#            self.values[k] = ret[k]
#            print "%s = %s" %(k,ret[k])
        if self.current_queue:
            if ret.has_key('max_jobs'):
                self.master_db.execute_query( 'UPDATE queues SET max_jobs= ? WHERE name = ?', self.current_queue  )
            if ret.has_key('status'):
                self.master_db.execute_query( 'UPDATE queues SET status= ? WHERE name = ?', self.current_queue  )
#                self.master_db.execute( 'UPDATE dbs SET status="%s" WHERE id = %s'% ( self.current_param_db.status, self.current_param_db.id ) )
           
#        self.doc_header = "default values: %s"%(self.values )

    def __set_status(self, name, st):
        self.master_db.execute_query( 'UPDATE queues SET status= ? WHERE name = ?', name , st )

    def do_stop(self, c):
        """stops the currently loaded registered database"""
        self.__set_status(self.current_queue , 'S')
                
    def do_start(self, c):
        """starts the currently loaded registered database"""
        self.__set_status(self.current_queue , 'R')
                
    def do_pause(self, c):
         """pauses the currently loaded registered database"""
         self.__set_status(self.current_queue , 'P')

    

    def do_EOF(self, line):
        return True



if __name__ == '__main__':
    cmd_line = QueueCommandParser()
    if len(sys.argv) == 1:
        cmd_line.cmdloop()
    else:
        cmd_line.onecmd(" ".join(sys.argv[1:]))

