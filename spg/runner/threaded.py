#!/usr/bin/python


import random as rnd
import threading, time
import spg.utils as utils


from spg.master import SPGMasterDB

class SPGRunningAtom(threading.Thread):
    n_threads = 0
    def __init__(self, lock ):

        SPGRunningAtom.n_threads += 1
        threading.Thread.__init__(self)
        self.thread_id = SPGRunningAtom.n_threads
        self.lock = lock

    def run(self):
        self.lock.acquire()
        print "-------- thread %5d START " % (self.thread_id)
        self.lock.release()

        time.sleep( rnd.randint( 2, 15 ) )

        self.lock.acquire()
        print "-------- thread %5d EXIT " % (self.thread_id)
        self.lock.release()






class SPGRunningPool():
    def __init__(self):
        self.master_db = SPGMasterDB()

        self.db_lock = threading.Lock()



    def launch_workers(self):
        target_jobs, = self.master_db.query_master_fetchone('SELECT max_jobs FROM queues WHERE name = "default"')

        current_count = self.active_threads()
        to_launch = target_jobs - current_count
        utils.newline_msg( "STAT", "[%3d::%3d:%3d]" % (target_jobs,current_count, to_launch ) )

        for i_t in range(to_launch):
            nt = SPGRunningAtom(lock=self.db_lock)
            nt.start()

    def active_threads(self):
        return threading.active_count() - 1











#rp = SPGRunningPool(50, 2)
#rp.run()