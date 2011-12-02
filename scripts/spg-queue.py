#!/usr/bin/python


from spg import VAR_PATH
from spg.master import MasterDB
from spg.utils import newline_msg

import cmd, sys, fnmatch, os
from subprocess import Popen, PIPE


class QueueCommandParser(cmd.Cmd):
    """command processor for the queues."""
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "| spg-queue :::~ "
        self.current_queue = None 
        self.master_db =  MasterDB()
        #self.possible_keys = ['max_jobs', 'status']
        self.__update_queue_list()

    def __update_queue_list(self):
        self.queues = self.master_db.execute_query("SELECT * FROM queues ORDER BY id")
        

    def do_load(self,c):
        """loads a queue as active one"""
        self.__update_queue_list()
        if len( filter(lambda x: x[1] == c, self.queues) ):
           self.current_queue = c
        else:
           newline_msg("ERR", "queue '%s' not found"%c)
        print "loaded '%s'"%self.current_queue
                
    def completedefault(self, text, line, begidx, endidx):    
        self.__update_queue_list()
        completions = [ name for  (id, name, max_jobs, status) in self.queues]

        if text:
            completions = [ f
                            for f in completions
                            if f.startswith(text)
                            ]
        return completions
            
        

    def do_ls(self, c):
        """lists the queues in the master database """
        self.__update_queue_list()
        for (id, name, max_jobs, status) in self.queues:
            print "   %16s  - J: %2d - S: '%s'"%( name, max_jobs, status)
###  CREATE TABLE IF NOT EXISTS queues 
###           ( id INTEGER PRIMARY KEY, name CHAR(64), max_jobs INTEGER, 
###           status CHAR(1) )


    def do_add(self, c):
        """adds queue queue"""
        self.__update_queue_list()
        
        if len( filter(lambda x: x[1] == c, self.queues) ):
                newline_msg("ERR", "queue '%s' already exists"%queue, 2)
                return 
        self.master_db.execute_query( "INSERT INTO queues (name, max_jobs, status) VALUES (?,?,?)",c,  1, 'S')
        os.makedirs("%s/queue/%s"%(VAR_PATH,c))
        self.current_queue = c


    def do_set_max_jobs(self, c):
        """sets the maximum number of jobs in the given queue 
           usage: [regexp] N_JOBS"""
        c = c.split()
        if len(c) == 1 and self.current_queue:
            max_jobs = int(c[0])
            self.master_db.execute_query( 'UPDATE queues SET max_jobs= ? WHERE name = ?', max_jobs, self.current_queue )
        elif len(c) == 2:
            re = c[0]
            max_jobs = int(c[1])
#            print re, max_jobs
            lsq = [ n for  (id, n, mj, s) in self.queues ]
            lsq = fnmatch.filter(lsq, re)
#        print lsq
            for q in lsq:
                #print status, q
                self.master_db.execute_query( 'UPDATE queues SET max_jobs= ? WHERE name = ?',  max_jobs, q )



    def do_clean_pool(self, cmd): 
        """cleans all the hanging pickled input/output files"""
        
        proc = Popen("rm -f %s/run/*"%VAR_PATH, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
        proc.wait()
        self.__update_queue_list()
        
        for (id, name, max_jobs, status) in self.queues:
            proc = Popen("rm -f %s/queue/%s/*"%(VAR_PATH,name), shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
            proc.wait()




    def do_remove(self, c):
        """sets the maximum number of jobs in the given queue 
           usage: [regexp] N_JOBS"""
        c = c.split()
        if len(c) == 0 and self.current_queue:
            self.master_db.execute_query( 'DELETE FROM queues WHERE name = ?', self.current_queue  )
        elif len(c) == 1:
            re = c[0]
#            print re, max_jobs
            lsq = [ n for  (id, n, mj, s) in self.queues ]
            lsq = fnmatch.filter(lsq, re)
#        print lsq
            for q in lsq:
                #print status, q
                self.master_db.execute_query( 'DELETE FROM queues WHERE name = ?', q  )        


#        ret = utils.parse_to_dict(c, allowed_keys=self.possible_keys)
#        for k in ret:
#            self.values[k] = ret[k]
#            print "%s = %s" %(k,ret[k])
#        if self.current_queue:
#            if ret.has_key('max_jobs'):
#            if ret.has_key('status'):
#                self.master_db.execute_query( 'UPDATE queues SET status= ? WHERE name = ?', self.current_queue  )
#                self.master_db.execute( 'UPDATE dbs SET status="%s" WHERE id = %s'% ( self.current_param_db.status, self.current_param_db.id ) )
           
#        self.doc_header = "default values: %s"%(self.values )

    def __set_status(self, status, name = None):
        #print name, status
        if not name and self.current_queue:
#            print  'UPDATE queues SET status= ? WHERE name = ?'
            self.master_db.execute_query( 'UPDATE queues SET status= ? WHERE name = ?', status, self.current_queue  )
            return
        lsq = [ n for  (id, n, max_jobs, s) in self.queues ]
        if name:
            lsq = fnmatch.filter(lsq, name)
#        print lsq
        for q in lsq:
#            print status, q
            self.master_db.execute_query( 'UPDATE queues SET status= ? WHERE name = ?',  status, q )

    def do_stop(self, c):
        """stops the currently loaded registered database"""
        self.__set_status('S', c)
                        
    def do_start(self, c):
        """starts the currently loaded registered database"""
        self.__set_status('R', c)
                
    def do_pause(self, c):
         """pauses the currently loaded registered database"""
         self.__set_status('P', c)

    

    def do_EOF(self, line):
        return True



if __name__ == '__main__':
    cmd_line = QueueCommandParser()
    if len(sys.argv) == 1:
        cmd_line.cmdloop()
    else:
        cmd_line.onecmd(" ".join(sys.argv[1:]))

