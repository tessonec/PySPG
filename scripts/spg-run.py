#!/usr/bin/python


from spg import SPGParser

  
parser = SPGParser()

parser.fetch( open("param.dat") )

for i in parser:
        print i
