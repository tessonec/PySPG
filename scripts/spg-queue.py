#!/usr/bin/python

import cmd
import sys


class QueueCommandParser(cmd.Cmd):
    """command processor for the queues."""

    FRIENDS = [ 'Alice', 'Adam', 'Barbara', 'Bob' ]
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "| spg-queue :::~ "
        self.current_queue = None 
        self.master_db =  MasterDB()

    def 

    
    def do_greet(self, person):
        "Greet the person"
        if person and person in self.FRIENDS:
            greeting = 'hi, %s!' % person
        elif person:
            greeting = "hello, " + person
        else:
            greeting = 'hello'
        print greeting
    
    def complete_greet(self, text, line, begidx, endidx):
        if not text:
            completions = self.FRIENDS[:]
        else:
            completions = [ f
                            for f in self.FRIENDS
                            if f.startswith(text)
                            ]
        return completions

    def do_EOF(self, line):
        return True



if __name__ == '__main__':
    cmd_line = QueueCommandParser()
    if len(sys.argv) == 1:
        cmd_line.cmdloop()
    else:
        cmd_line.onecmd(" ".join(sys.argv[1:]))

