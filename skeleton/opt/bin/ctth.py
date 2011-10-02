#! /usr/bin/python
version_number = "2.1.0"
release_date   = "Wed Ago 21 2006"
# :::~ Author: Claudio Juan Tessone <tessonec@imedea.uib.es> (c) 2002-2003
# Distributed According to GNU Generic Purpose License (GPL)
# Please visit www.gnu.org
################################################################################
#
# Changelog
# 2.1.0 (21/08/06) better ordered the output
# 2.0.1 (14/08/06) simplified warning messages
# 2.0.0 (10/07/06) splitted fortran,doc,c versions
# 1.2.1 (14/09/05) Added column output
# 1.2.1 (05/09/07) Added support for changelog file
# 1.2.0 (05/08/10) Now, randomseed is incremental, better htmldoc
# 1.1.2 (03/10/15) Fixed randomseed behavior
# 1.1.1 (03/08/16) added "include" keyword
# 1.1   (03/08/07) Generates simple HTML documentation, added namespaces
# 1.0   (03/02/03) Generates C++ code for parsing a .ct file
#
#
################################################################################
#
# TODO LIST
# *   Add language support
# *** documentation of .ct files
# *** cleanup of python code (too messy) to make it easily extendable
# **  generate Fortran, (Python?), Ansi C, (Java?) Code
# *** use of getopt in order to receive parameters from command-line arguments
#
################################################################################
#
included_files=[]
import os.path
def search_for_includes(com):
  for l in com:
    if l[0]=="include":

      if os.path.abspath(l[1]) in included_files:
        print "error!!!! %s already included in .ct file"%l[1]
        sys.exit(4)
      print "including: %s..."%l[1]
      included_files.append(os.path.abspath(l[1]))

      mascoms= [ linea.strip().split(":")
                 for linea in open(l[1],"r").readlines()
                 if len(linea) > 1
               ];
      com.remove(l)
      com+=mascoms
      search_for_includes(com)



def printTable(lsCTX,title=None):
  print "<table><tbody>"
  print "<tr>"
  if title:
	 print '<td align="center"><b>%s</b></td>'%title.upper()
  for ii in range(len(lsCTX)):
    i=lsCTX[ii]
    print "<td>"
    print "<a href=#%s>%s</a>"%(i,i)
    print "</td>"
    if ii % 5 == 3:
      print "</tr>" 
      print "<tr>"
  print "</tr>"
 
  print "</tbody></table>"


def html_help(v):
  if v[0] == "flag":
    print '  <br> <p class="param">',v[1],' </p>',
    print '   <p id=%s></p>'%v[1]
    print "      <ul> "
    print "        <li> Flag </li> "
    print "        <li> <b>Explanation:</b>",v[2],"</li>"
    print "        <li> <b>Default value:</b> <tt>false</tt> </li>"
    print "      </ul> "

  if v[0] == "val":
    print '   <p id=%s></p>'%v[2]
    print '  <br> <p class="param">',v[2],'</p>',
    print "      <ul> "
    print "        <li> Free Parameter </li> "
    print "        <li> <b>Data type:</b>",v[1], "</li> "
    print "        <li> <b>Explanation:</b>",v[4],"</li>"
    print "        <li> <b>Default value:</b> <tt>",v[3],"</tt> </li>"
    print "      </ul> "


  if v[0] == "choice":
    print '   <p id=%s></p>'%v[2]
    posValues=v[3].split(",")
    print '  <br> <p class="param">',v[2],'</p>',
    print "      <ul> "
    print "        <li> CHOICE BETWEEN VALUES </li> "
    print "        <li> <b>Data type:</b>",v[1], "</li> "
    print "        <li> <b>Explanation:</b>",v[4],"</li>"
    print "        <li> <b>Possible values:</b><br> "
    print "         <div align='center'>   <table>"
    print "            <tbody >"
    print "              <tr>"
    for i in posValues:
      print "                <td>",i.strip('"'), "</td>"
    print "            </tr></table>"
    print "            </tbody></div>"
    print 
    print "      </ul> "


def backendize(infile):
  fin = open(infile, "r")
  output = []
  ls_output = []
  for line in fin.readlines():
    if line.strip()[0] == "@":
      vec = line.strip()[1:].split()
      try:
        backend = vec[0]
	try:
          var_name = vec[1]
	except:
	  var_name = ""
      except:
        sys.stderr.write("[ctt - ERROR] when unfolding line '%s'\n"%(line) )
        sys.exit()
      try:
        new_stuff = [
                    i.replace("%ARG%",var_name).replace("%ARG1%",var_name)
                    for i in open( os.path.expanduser("~/opt/etc/ctt/%s.be"%backend), "r" ).readlines()
                  ]
      except:
        sys.stderr.write("[ctt - ERROR] when loading backend '%s' and variable '%s'\n"%(backend,var_name) )
        sys.exit()
      output.extend (new_stuff)
      ls_output.append( (backend, var_name)  )
    else:
      output.append(line)
  return ls_output,output



if __name__=="__main__":

   import getopt, sys

   import os.path

   createDocummentation=False

   try:
        opts, args = getopt.getopt(sys.argv[1:], "hv")
   except getopt.GetoptError:
        # print help information and exit:
        print "Unknown Option!!"
        print "Help and getopt not implemented yet! Sorry!"
        sys.exit(2)

   if len(args)>1:
     print "Error: solo se puede procesar un file a la vez!!!"
     sys.exit(2)

   for o, a in opts:
        if o == "-d":
          createDocummentation=True
        if o == "-v":
          print "This is %s, version: %s\nrelease date: %s"%(os.path.split(sys.argv[0])[1],version_number,release_date)
	  sys.exit()
        if o == "-h":
          print "Usage is %s [OPTIONS] base.ct"%os.path.split(sys.argv[0])[1]

	  sys.exit()

   original_stdout=sys.stdout


   backends,lineas= backendize(args[0])
   comandos = [ linea.strip().split(":")
                 for linea in
                 lineas
                 if len(linea) > 1
               ];
   comandos.append(["val","long","randomseed","0","semilla de los numeros aleatorios"])
   included_files.append(os.path.abspath(args[0]))
   search_for_includes(comandos)

   fname=os.path.splitext(args[0])[0]

#
#
#  HTML Code Generation
#
#
   if True:
        comandos.sort()
	sys.stdout=original_stdout
	sys.stderr.write( "[ctt - MSG] generating html for %s...\n"%fname)
	sys.stdout=open(fname+".html","w" )
	
	try:
	  chg = [ i.strip() for i in open("./Changelog","r").readlines()]
	except:
	  sys.stderr.write("[ctt - WARNING] 'Changelog' not found! skipping...\n")
	  chg = [""]

	print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'

	print """<style type="text/css">
                 <!--
                 @import url(./cjt-doc.css);
                 -->
                 </style>
              """
	print '<title>ctx-%s documentation</title>'% \
	             os.path.split(os.path.split(os.path.abspath(args[0]))[0])[1]
	print '<link rel="shortcut icon" href="cjt.png">'
	print "<html>"


	print "<!--  :::~                                                      -->"
	print "<!--  File automaticamente generado por",os.path.split(sys.argv[0])[1]," NO EDITAR-->"
	print "<!--:::~ -->"
	print "<body>"
	print
	print "<h1 class='header'>",
	print 'ctx-%s'%os.path.split(os.path.split(os.path.abspath(args[0]))[0])[1],' </div>'
	print '</h1>'
	print '<div id="links">'
	print '  <ul>'
	print '  <li><a class="index"  href="index.html"><i>progs. docs</i></a></li>'
	print '  <li><a href="#general">General Info</a></li>'
	print '  <li><a href="#cline">Command-line opts</a></li>'
	print '  <li><a href="#synopsis">Synopsis</a></li>'
	print '  <li class="sub"><a href="#flags">Flags</a>'
	print '    <ul>'
        for i in [ j for j in comandos if j[0]=='flag']:
           print '      <li><a href="#%s">%s</a></li>'%(i[1],i[1])
	print '    </ul>'
	print '  </li>'
	print ''
	print '  <li class="sub"><a href="#val">Variables</a>'
	print ''
	print '    <ul>'
        for i in [ j for j in comandos if j[0]=='val']:
           print '      <li><a href="#%s">%s</a></li>'%(i[2],i[2])
	print '    </ul>'
	print '  </li>'
	print '  '
	print '  <li class="sub"><a href="#choice">Choices</a>'
	print '    <ul>'
        for i in [ j for j in comandos if j[0]=='choice']:
           print '      <li><a href="#%s">%s</a></li>'%(i[2],i[2])
	print '    </ul>'
	print '  </li>'
	print ''
	print '  <li><a href="#output">Output</a>'
	print ' '
	print '  <li 	><a href="#changelog">Changelog</a>'
	print ' '
	print '  </ul>'
	print '</div>'

	print '</div>'
	print '<div id="info">'
	import time
	print "<b>last update:</b> ", time.strftime("%d/%m/%y"), "<br>"
	import posix
	print "<b>host:</b> ", posix.uname()[1], "<br>"
	print "<b>OS:</b> ", posix.uname()[0], "<br>"
        print '</div>'
	print '<div id="content">'
	print '<p id="general"></p>'
	print '<H2 >General information</H2>'
	try:
	  lastVersion = filter( lambda x:
		       x.lower().find("version")!=-1 ,
		       chg)[0].split()
          versionNo = lastVersion[1]
          releasedOn = lastVersion[-1]
	  print '<p>'
          print "<b>Version number:</b> %s <br>"%versionNo
          print "<b>Released on:</b> %s <br>"%releasedOn
	except:
	  pass
	try:
	  filein = open("conf.in").readline()

          print "<b>Default input file:</b>  <tt> %s</tt> <br>"%filein
	except:
	  pass
	print '</p>'

        print '<p id="synopsis"></p>'
	print '<H2>Parameter Synopsis</H2>'
	lsCTX=[ j[2] for j in comandos if j[0] == "choice"] 
        printTable(lsCTX,"choice")
	lsCTX=[ j[1] for j in comandos if j[0] == "flag"] 
        printTable(lsCTX,"flag")
	
	lsCTX=[ j[2] for j in comandos if j[0] == "val" and j[1] == "string"] 
        printTable(lsCTX,"val: string")
	
	lsCTX=[ j[2] for j in comandos if j[0] == "val" and (j[1] == "double" or "real" in j[1].lower() ) ]  
        printTable(lsCTX,"val: double")
	
	lsCTX=[ j[2] for j in comandos if j[0] == "val" and ( "int" in j[1]  or "long" in j[1] or "sign" in j[1])  ] 
        printTable(lsCTX,"val: int")
	
	print '<p id="choice"></p>'
	print "<H2>Input file parameters: CHOICE</H2>"
	print "<dl>"
	print
	print
	for i in [ j for j in comandos if j[0] == "choice"] :
	  html_help(i)
	print
	print "</dl>"

	print '<p id="flag"></p>'
	print "<H2>Input file parameters: FLAG</H2>"
	print "<dl>"
	print
	print
	for i in [ j for j in comandos if j[0] == "flag"] :
	  html_help(i)
	print
	print "</dl>"

	print '<p id="val"></p>'
	print "<H2>Input file parameters: VAL</H2>"
	print "<dl>"
	print
	print
	for i in [ j for j in comandos if j[0] == "val"] :
	  html_help(i)
	print
	print "</dl>"


	#try:

        try:
            BINARYPATH=os.path.expanduser("~/opt/")
            sys.path.append(BINARYPATH+"/lib/")
        except:
            sys.stderr.write("--> error... '%s' directory not found! exiting...\n"%BINARYPATH)
            sys.exit(2)

        try:
            from PySPG import *
        except:
            sys.stderr.write("Couldn't import PySPG package, check PySPGPATH variable\n")
            sys.stderr.write("And verify that PySPG lives there\n")
            sys.stderr.write("actual value: '%s'\n"%BINARYPATH)


	print '<p id="output"></p>'

	print "<h2 >General Output</h2>"
	try:

	  cols = ColumnInterpreter.loadConfigurationFile("./conf.output")[1]

	  for actualCommand in generateListofValues(cols,ColumnInterpreter.keysColumns):
	    try:
	      print "<p class='param'>%s</p>"%actualCommand["parameter"]
	    except:
	      print "<p class='param'>%s</p>"%actualCommand["basename"]
	    print "<ul>"

	    print "<li>Base Output Name: <b>%s</b></li>"%actualCommand["basename"]
	    repeat_on = 1
	    try:
              repeat_on = int(actualCommand["repeat_on"])
	      print "<li> It is repeated in <b>%s</b> consecutive columns... </li>"%repeat_on
	    except:
	      pass
	    numberCols = 2
	    if actualCommand["type"] in ["xy"]:
	      numberCols = 1
	    if repeat_on>1:
	        print "<li>Plot type:  <b>%s</b>// Columns:  <b>%i</b> * <b>%i</b> </li>"%(actualCommand["type"],numberCols,repeat_on)
            else:
	        print "<li>Plot type:  <b>%s</b> // Columns: <b>%i</b></li>"%(actualCommand["type"],numberCols)
	    try:
	      print "<li>Only plotted if flags: '<b>%s</b>' is/are active</li>"%actualCommand["flags"]
	    except:
	      pass
	    try:
	      print "<li>Scale: '<b>%s</b>' "%actualCommand["scale"]
	    except:
	      pass
	#    print "<li>%s</li>"%str(actualCommand)
	    print "</ul>"
          # print cols

	except:
	  sys.stderr.write("--> warning... error processing 'conf.output'! skipping...\n")

	try:

	  cols =  ColumnInterpreter.loadConfigurationFile("./conf.output")[2]
          print "<h2 >File Output</h2>"
          #print cols
          ColumnInterpreter.keysColumns.append("baseoutput")
	  for actualCommand in generateListofValues(cols,ColumnInterpreter.keysColumns):
	    try:
	      print "<p class='param'>%s</p>"%actualCommand["baseoutput"]
	    except:
	      print "<p class='param'>%s</p>"%actualCommand['basename']
	    print "<ul>"

	    print "<li>Base Output Name: <b>%s</b></li>"%actualCommand['basename']
	    repeat_on = 1
	    try:
              repeat_on = int(actualCommand["repeat_on"])
	      print "<li> It is repeated in <b>%s</b> consecutive columns... </li>"%repeat_on
	    except:
	      pass
	    numberCols = 2
	    if actualCommand["type"] in ["xy"]:
	      numberCols = 1
	    if repeat_on>1:
	        print "<li>Plot type:  <b>%s</b>// Columns:  <b>%i</b> * <b>%i</b> </li>"%(actualCommand["type"],numberCols,repeat_on)
            else:
	        print "<li>Plot type:  <b>%s</b> // Columns: <b>%i</b></li>"%(actualCommand["type"],numberCols)
	    try:
	      print "<li>Only plotted if flags: '<b>%s</b>' is/are active</li>"%actualCommand["flags"]
	    except:
	      pass
	    try:
	      print "<li>Scale: '<b>%s</b>' "%actualCommand["scale"]
	    except:
	      pass
	#    print "<li>%s</li>"%str(actualCommand)
	    print "</ul>"
          # print cols

	except:
	  pass

	print '<p id="cline"></p>'
	print '<H2 >Command-line options</H2>'

	print '<p> <tt>-h</tt>: Prints available help </p>'
	print '<p> <tt>-i [filename]</tt>: Sets the input file to <tt>[filename]</tt> </p>'
	print '<p> <tt>-v</tt>: Prints version and release number and exits </p>'
	print '<p> <tt>-</tt>: Reads configuration from stdin </p>'


	try:
	  print '<h2 id="changelog">Changelog</h2>'
	  for iline in chg:
	    print '<p>%s</p>'%iline
	#    print "<br>"
	except:
	  pass


	print '<div align="right">Automagically generated por <tt>',os.path.split(sys.argv[0])[1],
	print '</tt>on %s</div>'%time.strftime("%d/%m/%y")


	print '</div >'
	print "</body>"
	print "</html>"
	print

	sys.stdout.close()


