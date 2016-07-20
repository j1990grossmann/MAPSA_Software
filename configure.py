
from classes import *
import sys, select, os, array
import numpy as np
from array import array
#import ROOT
#from ROOT import TGraph

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-s', '--setting', metavar='F', type='string', action='store',
default	=	'default',
dest	=	'setting',
help	=	'configuration setting ie default')

parser.add_option('-n', '--number', metavar='F', type='int', action='store',
default	=	1,
dest	=	'number',
help	=	'configuration number')

parser.add_option('-m', '--mpa', metavar='F', type='int', action='store',
default	=	0,
dest	=	'mpa',
help	=	'mpa to configure (0 for all)')

(options, args) = parser.parse_args()



a = uasic(connection="file://connections_test.xml",device="board0")
mapsa = MAPSA(a)
read = a._hw.getNode("Control").getNode('firm_ver').read()
a._hw.dispatch()
print "Running firmware version " + str(read)

a._hw.getNode("Configuration").getNode('num_MPA').write(5)
a._hw.dispatch()
read = a._hw.getNode("Configuration").getNode('num_MPA').read()
a._hw.dispatch()
print "num_MPA " + str(read)

mpa_number = options.mpa
if mpa_number ==0:
	config = mapsa.config(Config=options.number,string=options.setting)
	cur = config.upload()
	print "current config"
	print cur
	config.write()
	print ""
	print "checking config"
	prev = []
	for i in range(1,7):
		print i
		print "read the other end of the spi daisy chain"
		# print type(a._hw.getNode("Configuration").getNode("Memory_OutConf").getNode("MPA"+str(i)).getNode("config_1")), "------------------------"
		read = []
       		# read = a._hw.getNode("Configuration").getNode("Memory_OutConf").getNode("MPA"+str(i)).getNode("config_1").read(i)	
       		read = a._hw.getNode("Configuration").getNode("Memory_OutConf").getNode("MPA"+str(i)).getNode("config_1").readBlock(25)
		a._hw.dispatch()
		# print read
		prev.append(array('i',read))
	print prev
else:
	mpa_index = mpa_number-1
	
	mpa = []  
	for i in range(1,7):
		mpa.append(mapsa.getMPA(i))

	Confnum=options.number
	configarr = []

	writesetting=6-mpa_number

	print "Configuring MPA number " + str(mpa_number)

	curconf = mpa[mpa_index].config(xmlfile="data/Conf_"+options.setting+"_MPA"+str(mpa_number)+"_config"+str(Confnum)+".xml")
	curconf.upload()
	a._hw.dispatch()
	
	print ""
	print "Done"
