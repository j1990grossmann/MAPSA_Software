import pdb
import errno
import sys
import os
from array import array
import numpy as np
import time
import datetime
import argparse
from argparse import ArgumentParser
from classes import *
from ctypes import *
import errno
import itertools

parser = ArgumentParser()

parser.add_argument('-f', '--format',   action='store',
default =       'noprocessing',
dest    =       'format',
help    =       'memout format noprocessing, stubfinding, centroid, stripemulator ')

parser.add_argument('-m', '--mpa',  type=int, action='store',
default =       0,
dest    =       'mpa',
help    =       'mpa to configure (0 for all)')

parser.add_argument('-w', '--shutterdur',  type=int, action='store',
default =       0xFFFFF,
dest    =       'shutterdur',
help    =       'shutter duration')


parser.add_argument('-x', '--external-clock',  type=int, action='store',
default =       0,
dest    =       'external_clock',
help    =       'Use external 40MHz clock, e.g. for testbeam operation.')

parser.add_argument('-a', '--assembly',   action='store',
default =       0,
dest    =       'assembly',
help    =       'Name of the assembly, used to differentiate trimming configurations.')

parser.add_argument('-i', '--mpa-index',  type=int, choices=range(1,7), nargs='+', action='store',
# parser.add_argument('-i', '--mpa-index',  type=int, choices=range(1,7), action='store',
default =       [1,2],
dest    =       'mpa_index',
help    =       'Specify the indices of the MPAs in the SPI chain.')

parser.add_argument('-o', '--output-dir', metavar='DIR',  action='store',
default =       './readout_data',
dest    =       'output_dir',
help    =       'Directory where run data is stored')

parser.add_argument('-c', '--config', metavar='FILEFORMAT',  action='store',
#default =       'Conf-{assembly}_MPA-{mpa}.xml',
default =       'Conf_calibrated_MPA{mpa}_config1.xml',
dest    =       'config',
help    =       'Filename format string for trimming and masking MPA configuration. The variables {assembly} and {mpa} are available.')

parser.add_argument('--config-dir', metavar='DIR',  action='store',
default =       'data/',
dest    =       'output_dir',
help    =       'Filename format string for trimming and masking MPA configuration. The variables {assembly} and {mpa} are available.')

parser.add_argument('-n', '--num-triggers', metavar='NTRIG', type=int, action='store',
default =       10000,
dest    =       'num_triggers',
help    =       'Filename format string for trimming and masking MPA configuration. The variables {assembly} and {mpa} are available.')

parser.add_argument('-R', '--root',  type=int, action='store',
default =       1,
dest    =       'root',
help    =       'If set, write data to root file instead of plaintext output. '
                'It is written into the directory specified with --output-dir, '
                'while the name is specified with --root-fmt. '
                'The run numbering is used as with    "the plaintext output.')

parser.add_argument('-F', '--root-fmt', metavar='ROOTFILE',  action='store',
default =       'run{number:04d}.root',
dest    =       'root_fmt',
help    =       'Format of the filename for ROOT file output. You can use the variables {number} and {assembly}.')

parser.add_argument('-t', '--threshold',  type=int, action='store',
default =       180,
dest    =       'threshold',
help    =       'threshold as int a Number between 0 and 255')

parser.add_argument('--x_pos',  type=float, action='store',
default =       10,
dest    =       'x_pos',
help    =       'x_position')

parser.add_argument('--y_pos',  type=float, action='store',
default =       10,
dest    =       'y_pos',
help    =       'y_position')

parser.add_argument('--z_pos',  type=float, action='store',
default =       10,
dest    =       'z_pos',
help    =       'z_position')

parser.add_argument('--angle',  type=float, action='store',
default =       360,
dest    =       'angle',
help    =       'angle')

parser.add_argument('--voltage',  type=float, action='store',
default =       10,
dest    =       'voltage',
help    =       'voltage')

parser.add_argument('--delay',  type=int, action='store',
default =       0,
dest    =       'delay',
help    =       'shutter delay')


args1 = parser.parse_args()
from ROOT import TGraph, TCanvas, TTree, TFile, TBranch

print str(args1)

class RippleCounterBranch(Structure):
    _fields_ = [
            ("header", c_uint),
            ("pixels", c_ushort*48)
        ]

class MemoryNoProcessingBranch(Structure):
    _fields_ = [
            ("pixelMatrix", c_ulonglong*96),
            ("bunchCrossingId", c_ushort*96),
            ("header", c_ubyte*96),
            ("numEvents", c_ubyte),
            ("corrupt", c_ubyte),
        ]

class daq_continous_2MPA:
    def __init__(self,parser):
        self._Result_Dict=[]
        self._Keys=[]
        self._Values=[]
        self._Parser=parser
        self._assembly = []
        self._number_mpa_light=0
        self._number_of_cond_vars=0
        self._memmode=''
        self._threshold=100
        #Get Workingdir, DataDir, Config Dir
        self._datapath, self._runNumber, self._config_dir = self._create_data_dir()
        self.timestr = datetime.datetime.now().time().isoformat().replace(":","").replace(".","")
        self._args = self._parse_args()
        self._a= uasic(connection="file://connections_test.xml", device="board0")
        self._glib = self._a._hw
        self._tree , self._tfile = self.create_tree()
        #self._tree = self.create_tree()

        ##filepath = os.path.dirname(os.path.realpath(__file__))
        ##create ttree and open root file
    def _parse_args(self):
        args=self._Parser.parse_args()

        # print str(args)
        # (options, args) =
        formarr = ['stubfinding','stripemulator' ,'centroid','noprocessing']
        self._memmode = formarr.index(args.format)
        self._threshold = args.threshold
        if len(args.mpa_index)>6:
            print "Specify a valid MPA configuration"
            exit
        if args.mpa_index:
            self._assembly = list(sorted(args.mpa_index))
        else:
            self._assembly = [2, 5]
        return args
    def _create_data_dir(self):
        cwd = os.getcwd()
        #Create directory for new run
        data_dir=cwd+"/readout_data"
        self._make_sure_path_exists(data_dir)
        runNumber = 0
        runNumberFile = cwd+'/.currentRun.txt'
        with open(runNumberFile,'r') as runFile:
            runNumber = int(runFile.read())
            with open(runNumberFile,'w') as newRunFile:
                newRunFile.write(str(runNumber+1))
                subdir ="/%09d" %runNumber
                datapath = data_dir+subdir
                self._make_sure_path_exists(datapath)
                #check if config dir is there
                config_dir=cwd+"/data"
                self._make_sure_path_exists(config_dir)
        return datapath, runNumber, config_dir
    def _make_sure_path_exists(self,path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
    def create_tree(self):
        self._Keys = [
            "COND_NO_MPA_LIGHT"        ,
            "COND_SPILL"               ,
            "COND_THRESHOLD"           ,
            "COND_TIMESTAMP"           ,
            "COND_ANGLE"               ,
            "COND_X_POS"               ,
            "COND_Y_POS"               ,
            "COND_Z_POS"               ,
            "COND_VOLTAGE"             ,
            "TRIG_COUNTS_SHUTTER"      ,
            "TRIG_COUNTS_TOTAL_SHUTTER",
            "TRIG_COUNTS_TOTAL"        ,
            "TRIG_OFFSET_BEAM"         ,
            "TRIG_OFFSET_MPA"
            ]
        self._number_of_cond_vars=len(self._Keys)
        self._number_mpa_light=len(self._assembly)
        for i in range(0,self._number_mpa_light):
            self._Keys.append("counter_mpa_"+str(i))
        for i in range(0,self._number_mpa_light):
            self._Keys.append("noprocessing_mpa_"+str(i))
        for key in self._Keys:
            if "COND_THRESHOLD" in key:
                self._Values.append(array('H',[0]))
            if "COND" in key and not "COND_THRESHOLD" in key:
                self._Values.append(array('f',[0]))
            if "TRIG_COUNTS" in key:
                self._Values.append(array('L',[0]))
            if "TRIG_OFFSET" in key:
                #self._Values.append(array('L',[0]*2048))
                self._Values.append(array('L',[0]))
            if "counter" in key:
                self._Values.append(RippleCounterBranch())
            if "noprocessing" in key:
                self._Values.append(MemoryNoProcessingBranch())

        self._Result_Dict=zip(self._Keys,self._Values)
        tfile = TFile(self._datapath+'/{:09d}'.format(self._runNumber)+'.root','recreate')
        tfile.SetCompressionLevel(1)
        ttree = TTree("Tree","Tree")

        counterFormat = "header[1]/i:pixel[48]/s"
        noProcessingFormat = "pixels[96]/l:bunchCrossingId[96]/s:header[96]/b:numEvents/b:corrupt/b"

        for key in self._Result_Dict:
            if "COND_THRESHOLD" in key[0]:
                ttree.Branch(key[0],key[1],key[0]+"[1]/s")
            if "COND" in key and not "COND_THRESHOLD" in key:
                ttree.Branch(key[0],key[1],key[0]+"[1]/F")
            if "TRIG_COUNTS" in key[0]:
                ttree.Branch(key[0],key[1],key[0]+"[1]/i")
            if "TRIG_OFFSET" in key[0]:
                #ttree.Branch(key[0],key[1],key[0]+"[2048]/l")
                ttree.Branch(key[0],key[1],key[0]+"[1]/i")
            if "counter" in key[0]:
                ttree.Branch(key[0],key[1],counterFormat)
            if "noprocessing" in key[0]:
                ttree.Branch(key[0],key[1],noProcessingFormat)
        return ttree, tfile
    def write_close(self):
        self._tree.Write()
        self._tfile.Close()
    def acquisition_start(self):
        # Connection and GLIB
	
	# Enable clock on MPA
	self._glib.getNode("Control").getNode("MPA_clock_enable").write(0x1)
	self._glib.dispatch()
	
	# Reset all logic on GLIB
	self._glib.getNode("Control").getNode("logic_reset").write(0x1)
	self._glib.dispatch()
	
	# Source all classes
	mapsaClasses = MAPSA(self._a)
	
	conf = []
	mpa = []
	try:
	    for iMPA, nMPA in enumerate(self._assembly):
	        # List of instances of MPA, one for each MPA. SPI-chain numbering!
	        mpa.append(MPA(self._glib, iMPA + 1))
	        # conf.append(mpa[iMPA].config("data/Conf_trimcalib_MPA" + str(nMPA)+
	        # "_masked.xml")) # Use trimcalibrated config
                print str(os.path.join(self._config_dir,self._args.config.format(mpa=nMPA, assembly=self._args.assembly)))
	        conf.append(mpa[iMPA].config(
	            os.path.join(
	                self._config_dir,
	                self._args.config.format(mpa=nMPA, assembly=self._args.assembly))))
	except IOError, e:
	    if e.filename and e.errno == errno.ENOENT:
	        parser.error(
	            "Cannot open MPA configuration '{0}'.\nCheck --config and --assembly settings, or perform trimming.".format(e.filename))
	    else:
	        raise
	
	# Define default config
	NO_MPA=len(self._assembly)
	for iMPA in range(0, NO_MPA):
	    # Write threshold to MPA 'iMPA'
	    conf[iMPA].modifyperiphery('THDAC', self._args.threshold)
	    # Enable synchronous readout on all pixels
	    conf[iMPA].modifypixel(range(1, 25), 'SR', 1)
	    conf[iMPA].upload()  # Push configuration to GLIB
	self._glib.getNode("Configuration").getNode("mode").write(NO_MPA - 1)
	print str(conf[iMPA])
	conf[iMPA]._spi_wait()  # includes dispatch
	
	self._glib.getNode("Configuration").getNode("num_MPA").write(NO_MPA)
	# This is a 'write' and pushes the configuration to the glib. Write must
	# happen before starting the sequencer.
	self._glib.getNode("Configuration").getNode("mode").write(NO_MPA - 1)
	conf[0]._spi_wait()  # includes dispatch
        if self._args.delay:
	    self._glib.getNode("Control").getNode('shutter_delay').write(self._args.delay)	
	if self._args.external_clock:
	    self._glib.getNode("Control").getNode('testbeam_clock').write(0x1)
	else:
	    self._glib.getNode("Control").getNode('testbeam_clock').write(0x0)
	self._glib.getNode("Configuration").getNode("mode").write(len(self._assembly) - 1)
	self._glib.dispatch()
	
	# shutterDur = 0xFFFFFFFF #0xFFFFFFFF is maximum, in clock cycles
	# shutterDur = 0xFFFFFF  # 0xFFFFFFFF is maximum, in clock cycles
	# Start sequencer in continous daq mode. Already contains the 'write'
	mapsaClasses.daq().Sequencer_init(0x1, self._args.shutterdur, mem=1)
	
	
	print """Command Line Configuration
	--------------------------
	  Clock source is \x1b[1m{0}\x1b[m
	  Threshold     = \x1b[1m{1}\x1b[m
	  MPA Indices   = \x1b[1m{2}\x1b[m
	  Assembly Name = \x1b[1m{3}\x1b[m
	  Output Dir    = \x1b[1m{4}\x1b[m
          Num Triggers  = \x1b[1m{5}\x1b[m
          Run Number    = \x1b[1m{6}\x1b[m
	""".format("external" if self._args.external_clock else "internal",
	           self._args.threshold,
	           self._assembly,
	           self._args.assembly,
	           os.path.abspath(self._args.output_dir),
	           self._args.num_triggers,
	           self._runNumber
	           )
	if self._args.root:
	    self.recordRoot()
	else:
	    self.recordPlaintext()


    def _acquire(self,numTriggers, stopDelay=2):
        # ibuffer = 0
        readoutCounter = 0
        frequency = float("NaN")
        exceptioncounter=0
        while True:
            freeBuffers  = self._glib.getNode("Control").getNode('Sequencer').getNode('buffers_num').read()
            buffers_index = self._glib.getNode("Control").getNode('Sequencer').getNode('buffers_index').read()
            self._glib.dispatch()
            # time.sleep(.5)
            # print "free Buffers", freeBuffers, "buffers_index", buffers_index
            if freeBuffers ==0:
                # if buffers_index !=3:
                    # print "free Buffers Readout 4 Buffers! freeBuffers", freeBuffers,"Buffers_index", buffers_index,"readout Counter", readoutCounter
                # time.sleep(.5)
                if readoutCounter % 2000 == 0:
                    startTime = time.time()
                    shutterTimeStart = readoutCounter
                if readoutCounter % 100 == 0 and readoutCounter % 2000 !=0:
                    frequency = (readoutCounter - shutterTimeStart) / \
                        (time.time() - startTime)
                MAPSACounter = []
                MAPSAMemory = []
                # print "free Buffers", freeBuffers, "readoutCounter", readoutCounter
                for ibuffer in range(0,4):
                    for iMPA, nMPA in enumerate([2,5]):
                        # print "read ibuffer ",(ibuffer+1), "iMPA", iMPA, "nMPA", nMPA
                        counterData = self._glib.getNode("Readout").getNode("Counter").getNode(
                            "MPA" + str(iMPA + 1)).getNode("buffer_" + str(ibuffer+1)).readBlock(25)
                        memoryData = self._glib.getNode("Readout").getNode("Memory").getNode(
                            "MPA" + str(nMPA)).getNode("buffer_" + str(ibuffer+1)).readBlock(216)
                        MAPSACounter.append(counterData)
                        MAPSAMemory.append(memoryData)
                freeBuffers1  = self._glib.getNode("Control").getNode('Sequencer').getNode('buffers_num').read()
                buffers_index1  = self._glib.getNode("Control").getNode('Sequencer').getNode('buffers_index').read()
                self._glib.dispatch()
                while freeBuffers1<2:
                    exceptioncounter+=1
                    # print "freebuffers1  ", freeBuffers1,  " buffers_index1 ", buffers_index1
                    # print "readoutCounter", readoutCounter," buffers_index  ", buffers_index
                    print "exception _no",  exceptioncounter
                    # print "free Buffers before", freeBuffers, 
                    for ibuffer in range(0,4-freeBuffers1):
                        for iMPA, nMPA in enumerate([2,5]):
                            counterData = self._glib.getNode("Readout").getNode("Counter").getNode(
                                "MPA" + str(iMPA + 1)).getNode("buffer_" + str(ibuffer+1)).readBlock(25)
                            memoryData = self._glib.getNode("Readout").getNode("Memory").getNode(
                                "MPA" + str(nMPA)).getNode("buffer_" + str(ibuffer+1)).readBlock(216)
                            MAPSACounter.append(counterData)
                            MAPSAMemory.append(memoryData)
                    freeBuffers1  = self._glib.getNode("Control").getNode('Sequencer').getNode('buffers_num').read()
                    self._glib.dispatch()
                # print "Readout", readoutCounter
                # for i in range(0,len(MAPSACounter)):
                #     print str(MAPSACounter[i])
                # for i in range(0,len(MAPSAMemory)):
                #     print str(MAPSAMemory[i])
                readoutCounter += 1
                yield readoutCounter, MAPSACounter, MAPSAMemory, freeBuffers, frequency
                # Continuous operation in bash loop
                if readoutCounter == math.ceil(numTriggers/4):
                    print "total no of exception",  exceptioncounter                    
                    endTimeStamp = time.time()
                    break
                # Required for automation! Do not stop DAQ until at least
                # 2 seconds after reaching the num trigger limit
                # if readoutCounter > math.ceil(numTriggers/4):
                #     if time.time() - endTimeStamp > stopDelay:
                #         break
    def recordPlaintext(self):
        counterArray = []
        memoryArray = []
        try:
            for readout_counter, counter, memory, freeBuffers, frequency in self._acquire(self._args.num_triggers):
                counterArray.append(counter)
                memoryArray.append(memory)
                if readout_counter%100==0:
                    print "Event counter: %s Free buffers: %s Frequency: %s " % (readout_counter*4, freeBuffers, frequency)
        except KeyboardInterrupt:
            pass
        if len(counterArray):
            print "End of Run %s" % self._runNumber
            memoryFile = open(os.path.join(
                self._args.output_dir, 'run%s_memory.txt' % ('{0:04d}'.format(self._runNumber))), 'w')
            counterFile = open(os.path.join(
                self._args.output_dir, 'run%s_counter.txt' % ('{0:04d}'.format(self._runNumber))), 'w')
            for i, readout in enumerate(counterArray):
                for j, mpa in enumerate(readout):
                    counterFile.write(str(mpa.value()) + "\n")
                    memoryFile.write(str(memoryArray[i][j].value()) + "\n")
            counterFile.close()
            memoryFile.close()
            print "All files saved"
        else:
            print "\x1b[1mNo data acquired, ignore.\x1b[m"
            
    def recordRoot(self):
        spinner = "--\\\\||//"
        progress = ["-"]*20
        filename = os.path.join(self._args.output_dir,
                self._args.root_fmt.format(number=self._runNumber, assembly=self._args.assembly))
        #self._tfile = TFile(filename, "RECREATE")
        counterArray = []
        memoryArray = []
        try:
            for readout_counter, counter, memory, freeBuffers, frequency in self._acquire(self._args.num_triggers):
                counterArray.append(counter)
                memoryArray.append(memory)
                if readout_counter%100==0:
                    print "Event counter: %s Free buffers: %s Frequency: %s " % (readout_counter*4, freeBuffers, frequency)
        except KeyboardInterrupt:
            pass
        if len(counterArray):
            print "End of Run %s write raw file" % self._runNumber
            memoryFile = open(self._datapath+'/{:09d}'.format(self._runNumber)+'_memory.txt', 'w')
            counterFile = open(self._datapath+'/{:09d}'.format(self._runNumber)+'_counter.txt', 'w')
            for i, readout in enumerate(counterArray):
                for j, mpa in enumerate(readout):
                    counterFile.write(str(mpa.value()) + "\n")
                    memoryFile.write(str(memoryArray[i][j].value()) + "\n")
            counterFile.close()
            memoryFile.close()
            print "Fill the tree"
            try:
                #"COND_NO_MPA_LIGHT"        ,
                self._Values[0][0]=self._number_mpa_light                
                #"COND_SPILL"               ,
                self._Values[1][0]=0
                #"COND_THRESHOLD"           ,
                self._Values[2][0]=(int)(self._threshold)
                #"COND_TIMESTAMP"           ,
                self._Values[3][0]=0
                #"COND_ANGLE"               ,
                self._Values[4][0]=(float)(self._args.angle)
                #"COND_X_POS"               ,
                self._Values[5][0]=(float)(self._args.x_pos)
                #"COND_Y_POS"               ,
                self._Values[6][0]=(float)(self._args.y_pos)
                #"COND_Z_POS"               ,
                self._Values[7][0]=(float)(self._args.z_pos)
                #"COND_VOLTAGE"             ,
                self._Values[8][0]=(float)(self._args.voltage)
                #"TRIG_COUNTS_SHUTTER"      ,
                self._Values[9][0]=0
                #"TRIG_COUNTS_TOTAL_SHUTTER",
                self._Values[10][0]=0
                #"TRIG_COUNTS_TOTAL"        ,
                self._Values[11][0]=0
                #"TRIG_OFFSET_BEAM"         ,
                self._Values[12][0]=0
                #"TRIG_OFFSET_MPA"
                self._Values[13][0]=0
                for i in range(self._number_mpa_light):
                    #print self._Result_Dict[self._number_of_cond_vars+i]
                    #print self._Result_Dict[self._number_of_cond_vars+i+self._number_mpa_light]
                    self._Values[self._number_of_cond_vars+self._number_mpa_light+i].pixelMatrix = (c_ulonglong*96)(0)
                    self._Values[self._number_of_cond_vars+self._number_mpa_light+i].bunchCrossingId = (c_ushort*96)(0)
                    self._Values[self._number_of_cond_vars+self._number_mpa_light+i].header = (c_ubyte*96)(0)
                    self._Values[self._number_of_cond_vars+self._number_mpa_light+i].corrupt = c_ubyte(0)
                for readout in range(len(counterArray)):
                    # Loop over chunks of usually 4 (buffers readout)
                    if readout==0:
                        print "standard length", len(counterArray[readout])/self._number_mpa_light
                    if len(counterArray[readout])/self._number_mpa_light !=4:
                        print "Possible overflow at", len(counterArray[readout])/self._number_mpa_light
                    for l in range (0,len(counterArray[readout])/self._number_mpa_light):
                        if len(counterArray[readout])/self._number_mpa_light !=4:                        
                            self._Values[9][0]=len(counterArray[readout])/self._number_mpa_light
                        else:
                            self._Values[9][0]=0
                        # Loop over all MPA-light
                        # Fill the counters
                        for k, val in enumerate(itertools.islice(counterArray[readout],(l*self._number_mpa_light),((l+1)*self._number_mpa_light))):
                            # Loop over all pixels 
                            self._Values[self._number_of_cond_vars+k].header=c_uint(0)
                            for k1, val1 in enumerate (itertools.islice(val,1,None)):
                                self._Values[self._number_of_cond_vars+k].pixels[k1*2 + 0] = val1 & 0x7FFF # left
                                self._Values[self._number_of_cond_vars+k].pixels[k1*2 + 1] = (val1 >> 16) & 0x7FFF # right
                            # print self._Values[self._number_of_cond_vars+k].pixels[:]
                        # Loop over all MPA-light
                        # Fill the memory structs
                        for j, val in enumerate(itertools.islice(memoryArray[readout],(l*self._number_mpa_light),((l+1)*self._number_mpa_light))):
                            memory_ints = (c_uint*216)(*val)
                            memory_bytes = cast(memory_ints, POINTER(c_ubyte))
                            # iterate over memory in multipletts of 9 bytes (one 72 bit readout)
                            evtIdx = 0
                            numEvents = 0
                            for evtIdx in reversed(xrange(0, 96)):
                                evtData = tuple(
                                    itertools.islice(memory_bytes,
                                                     evtIdx*9, evtIdx*9 + 9))
                                self._Values[self._number_of_cond_vars+self._number_mpa_light+j].header[95-evtIdx] = evtData[8]
                                if self._Values[self._number_of_cond_vars+self._number_mpa_light+j].header[95-evtIdx] == 0x00:
                                    break
                                elif self._Values[self._number_of_cond_vars+self._number_mpa_light+j].header[95-evtIdx] != 0xFF:
                                    self._Values[self._number_of_cond_vars+self._number_mpa_light+j].corrupt = c_ubyte(evtIdx + 1)
                                    break
                                numEvents += 1
                                # bytes 1-8 as 64 bit integer, 1&2 are buch crossing id
                                pixelMatrix = ((evtData[5] << 40) | (evtData[4] << 32) |
                                               (evtData[3] << 24) | (evtData[2] << 16) |
                                               (evtData[1] << 8) | evtData[0])
                                bxid = ((evtData[7] << 8) | evtData[6])
                                self._Values[self._number_of_cond_vars+self._number_mpa_light+j].bunchCrossingId[95-evtIdx] = bxid
                                self._Values[self._number_of_cond_vars+self._number_mpa_light+j].pixelMatrix[95-evtIdx] = pixelMatrix
                                self._Values[self._number_of_cond_vars+self._number_mpa_light+j].numEvents = c_ubyte(numEvents)
                            # print self._Values[self._number_of_cond_vars+self._number_mpa_light+j].pixelMatrix[:]
                        self._tree.Fill()
                        # Spinner
                        if readout%25==0:
                            progress[int(len(progress)*float(readout*4)/float(self._args.num_triggers)) % len(progress)] = "#"
                            sys.stdout.write("\r\x1b[K [{1}] Event={0}  #events={4}  [{2}] {3:.0f}%".format(
                                readout*4,
                                spinner[readout*4 % len(spinner)],
                                "".join(progress),
                                float(readout*4) / float(self._args.num_triggers) * 100,
                                readout*4
                                ))
                            sys.stdout.flush()

                print "All files saved"
            except KeyboardInterrupt:
                pass
        else:
            print "\x1b[1mNo data acquired, ignore.\x1b[m"

        print "End of Run", self._runNumber	
		
daq= daq_continous_2MPA(parser)
daq.acquisition_start()
daq.write_close()





