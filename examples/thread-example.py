#!/usr/bin/python

import threading
import time

exitFlag = 0

import random as rnd

class SPGRunningAtom(threading.Thread):
    n_threads = 0
    def __init__(self, lock ):
        SPGRunningAtom.n_threads += 1
        threading.Thread.__init__(self)
        self.thread_id = SPGRunningAtom.n_threads
        self.name = "thread-%.2d"%self.thread_id
        self.counter = rnd.randint( 5,10 )

        self.lock = lock

    def run(self):
#        print "Starting " + self.name
        self.print_time(2)
#        print "Exiting " + self.name

    def print_time(self,delay):
        while self.counter:
#            if exitFlag:
#                threadName.exit()
            time.sleep(delay)
            self.lock.acquire()
            print "-------- %s [%d] " % (self.name, self.counter )
            self.lock.release()
            self.counter -= 1

# Create new threads

class SPGRunningPool():
    def __init__(self, count, check_delay):
        self.total_threads = count
        self.check_delay = check_delay
        self.db_lock = threading.Lock()
        self.lot = set()



    def run(self):

        while SPGRunningAtom.n_threads < 100:
            current_count = threading.active_count()
            to_launch = self.total_threads - current_count + 1
            print "%d:%d [%d]"%(current_count, to_launch, SPGRunningAtom.n_threads)
            for i_t in range(to_launch):
                nt =  SPGRunningAtom( lock = self.db_lock)
                nt.start()
            time.sleep(self.check_delay)








rp = SPGRunningPool(50, 2)
rp.run()