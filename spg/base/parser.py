#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Parses the parameters.dat into something meaningful"""

###########################################################################
# :::~ Copyright (C) 2003-2011 by Claudio J. Tessone <claudio.tessone@uzh.ch>
# 
# Modified on: v2.9.2 14 May 2011
# Modified on: v2.9.1 30 May 2010
# Modified on: v2.9   15 Sep 2008
# Created  on: v0.1   09 Jan 2005
# 
# License: Distributed according to GNU/GPL Version 2 
#          (see http://www.gnu.org)
#
###########################################################################



import iterator 

from math import * 

import re
import fnmatch, os, os.path



class Execute(iterator.IterConstant):
  def __init__(self, cl):
    """ name: the label to be assigned to this iterator
      data: the set of values can be assigned to this iterator
    """
    iterator.IterConstant.__init__("",)

    self.command = cl
    

  def __call__(self):
    print "function being called"
    
  



class MultIteratorParser(iterator.MultIterator):
    """
      a param iterator with functionality added
    """

    def __init__(self, stream = None):
        iterator.MultIterator.__init__(self)
        self.regexp = re.compile('\\w')
        
        if stream is not None:
            self.fetch(stream)


    def output_conf(self):
        ret = ""
        for i in self.data:
            if i.__class__ == iterator.Iterator:
                ret += ".%s  %s\n"%(i.name, " ".join(i.data))
            if i.__class__ == iterator.IterConstant:
                ret += ":%s  %s\n"%(i.name, " ".join(i.data))
            if i.__class__ == iterator.IterOperator:
                ret += "%s%s  %s  %s  %s\n"%(i.type, i.name, i.xmin, i.xmax, i.xstep)
        return ret



    def fetch(self, stream):
        for l in stream:
            linea = l.strip()
            if len(linea) == 0:
                continue

            symbol_end = self.regexp.search(linea).start()
            symbol = linea[:symbol_end].strip()
            rest = linea[symbol_end:].strip().split()

            if (symbol is '@' and rest[0]=="execute"):
              self.command = rest[1]

            if symbol is '#': continue #line is a comment

            if (symbol in ('!')): # reserved for the future
              continue

            if (symbol in ['+', '-', '*', '/', '**']):
              self.add( \
                iterator.IterOperator( rest[0], symbol, \
                       (eval(rest[1] ), eval( rest[2]), eval(rest[3]) ) ) )
            if (symbol == '.'):
              self.add(
                 iterator.Iterator(rest[0], rest[1:]) )

            if (symbol == '<'):
                ls_files = []
                for rgx in ls_files:
                    base_path, rx = os.path.split(rgx)
                    if base_path == "":
                        base_path == "."
                    ls_files.extend( fnmatch.filter(os.listdir(base_path), rx) )


                self.add( iterator.Iterator(rest[0], rest[1:]))

            if (symbol == ':'):
              self.add( iterator.IterConstant( name = rest[0], data = rest[1:] )  )




class MultIteratorParserExt(MultIteratorParser):
    """
        a param iterator with functionality added
    """

    def __init__(self, stream = None):
        MultIteratorParser.__init__(self, stream)
        self.add_ins = {}
        
        if stream is not None:
            self.fetch(stream)

    def add_plugin(self, rw, manip):
        self.add_ins[rw] = manip

    def parse_reserved_word(self, rest):
        if rest[0] in self.add_ins.keys():
            self.add( self.add_ins[ rest[0] ]( rest[1:] ) )


    def fetch(self, stream):
        for l in stream:
            linea = l.strip()

            symbol_end = self.regexp.search(linea).start()
            symbol = linea[:symbol_end].strip()
            rest = linea[symbol_end:].strip().split()

            if symbol is '#': continue #line is a comment

            if (symbol in ('!')): # reserved for the future
                continue

            if (symbol is '@' and rest[0]=="execute"):
                self.command = rest[1]

            if (symbol in ['+', '-', '*', '/', '**']):
                self.add( \
                 iterator.IterOperator( rest[0], symbol, \
                       (eval(rest[1] ), eval( rest[2]), eval(rest[3]) ) ) )

            if (symbol == '.'):
                self.add( \
                 iterator.Iterator(rest[0], rest[1:]) )

            if (symbol == ':'):
                self.add( iterator.Iterator( name = "".join(rest) ) )




#
#if __name__ == '__main__':
#    pp = MultIteratorParser()
#    pp.fetch(['+D 0. 10 1',' *r 2 16 2','**e 2 32 2', ':HELLO', '.bar 6 4 3','# this is a comment'])
##    pp.fetch(['+D 0. 10 1',' *r 2 16 8'])
#    print pp.items()
#    print pp.output_conf()
##    for i in pp:
##        print i


