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

parser.add_argument('-s', '--setting',   action='store',
default =       'default',
dest    =       'setting',
help    =       'settings ie default,  testbeam etc')

parser.add_argument('-C', '--calib',   action='store',
default =       'False',
dest    =       'calib',
help    =       'calibration')

parser.add_argument('-r', '--readout',   action='store',
default =       'both',
dest    =       'readout',
help    =       'readout which data ie counters, memory, both')

parser.add_argument('-f', '--format',   action='store',
default =       'noprocessing',
dest    =       'format',
help    =       'memout format noprocessing, stubfinding, centroid, stripemulator ')

parser.add_argument('-m', '--mpa',  type=int, action='store',
default =       0,
dest    =       'mpa',
help    =       'mpa to configure (0 for all)')

parser.add_argument('-t', '--threshold',  type=int, action='store',
default =       180,
dest    =       'threshold',
help    =       'threshold as int a Number between 0 and 255')

parser.add_argument('-T', '--testclock',   action='store',
default =       'glib',
dest    =       'testclock',
help    =       'test beam clock')

# parser.add_argument('-x', '--record',   action='store',
# default =       'True',
# dest    =       'record',
# help    =       'record this daq cycle')

parser.add_argument('-y', '--daqstring',   action='store',
default =       'none',
dest    =       'daqstring',
help    =       'string to append on daq folder name')

parser.add_argument('-z', '--monitor',   action='store',
default =       'False',
dest    =       'monitor',
help    =       'start event monitor in background')

parser.add_argument('-w', '--shutterdur',  type=int, action='store',
default =       0xFFFFF,
dest    =       'shutterdur',
help    =       'shutter duration')

parser.add_argument('-v', '--skip',   action='store',
default =       'True',
dest    =       'skip',
help    =       'skip zero counts')

parser.add_argument('-u', '--autospill',   action='store',
default =       'True',
dest    =       'autospill',
help    =       'write every spill')

# parser.add_argument('-N', '--norm',   action='store',
# default =       'False',
# dest    =       'norm',
# help    =       'use normalization mpa scheme')

parser.add_argument('-D', '--direction',   action='store',
default =       'glib',
dest    =       'direction',
help    =       'strip direction (glib or mpa)')

parser.add_argument('-L', '--loops',  type=int, action='store',
default =       -1,
dest    =       'loops',
help    =       'number of daq loops')

parser.add_argument('-p', '--phase',  type=int, action='store',
default =       0,
dest    =       'phase',
help    =       'beam phase offset')

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
default =       [],
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
        self._memmode=''
        self._threshold=100
        #Get Workingdir, DataDir, Config Dir
        self._datapath, self._runNumber, self._config_dir = self._create_data_dir()
        self.timestr = datetime.datetime.now().time().isoformat().replace(":","").replace(".","")
        self._args = self._parse_args()
        self._tfile = TFile()
        self._tree  = TTree()
        self.create_tree()
        self._a= uasic(connection="file://connections_test.xml", device="board0")
        self._glib = self._a._hw

        ##filepath = os.path.dirname(os.path.realpath(__file__))
        ##create ttree and open root file
        #create_ttree(tree_vars, number_mpa_light, assembly, datapath)
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
            "COND_VOLTAGE"             ,
            "TRIG_COUNTS_SHUTTER"      ,
            "TRIG_COUNTS_TOTAL_SHUTTER",
            "TRIG_COUNTS_TOTAL"        ,
            "TRIG_OFFSET_BEAM"         ,
            "TRIG_OFFSET_MPA"
            ]
        # self._assembly = [2,5]
        self._number_mpa_light=len(self._assembly)
        for i in range(0,self._number_mpa_light):
            self._Keys.append("AR_MPA_"+str(i))
            self._Keys.append("SR_BX_MPA_"+str(i))
            self._Keys.append("SR_MPA_"+str(i))
        for key in self._Keys:
            if "COND" in key:
                self._Values.append(array('L',[0]))
            if "TRIG_COUNTS" in key:
                self._Values.append(array('L',[0]))
            if "TRIG_OFFSET" in key:
                self._Values.append(array('L',[0]*2048))
            if "AR_MPA" in key:
                self._Values.append(array('L',[0]*48))
            if "SR" in key:
                self._Values.append(array('L',[0]*96))
        self._Result_Dict=zip(self._Keys,self._Values)
        self._tfile = TFile(self._datapath+'/{:09d}'.format(self._runNumber)+'.root','recreate')
        self._tree = TTree("Tree","Tree")
        for key in self._Result_Dict:
            if "COND" in key[0]:
                self._tree.Branch(key[0],key[1],key[0]+"[1]/l")
            if "TRIG_COUNTS" in key[0]:
                self._tree.Branch(key[0],key[1],key[0]+"[1]/l")
            if "TRIG_OFFSET" in key[0]:
                self._tree.Branch(key[0],key[1],key[0]+"[2048]/l")
            if "AR_MPA" in key[0]:
                self._tree.Branch(key[0],key[1],key[0]+"[48]/l")
            if "SR" in key[0]:
                self._tree.Branch(key[0],key[1],key[0]+"[96]/l")
    def write_close(self):
        #self._tree.Write('tree',ROOT.TObject.kOverwrite)
        #self._tfile.Write()
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
	
	if self._args.external_clock:
	    self._glib.getNode("Control").getNode('testbeam_clock').write(0x1)
	else:
	    self._glib.getNode("Control").getNode('testbeam_clock').write(0x0)
	self._glib.getNode("Configuration").getNode("mode").write(len(self._assembly) - 1)
	self._glib.dispatch()
	
	# shutterDur = 0xFFFFFFFF #0xFFFFFFFF is maximum, in clock cycles
	shutterDur = 0xFFFFFF  # 0xFFFFFFFF is maximum, in clock cycles
	# Start sequencer in continous daq mode. Already contains the 'write'
	mapsaClasses.daq().Sequencer_init(0x1, shutterDur, mem=1)
	
	
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
        ibuffer = 0
        shutterCounter = 0
        frequency = float("NaN")
        while True:
            freeBuffers = self._glib.getNode("Control").getNode('Sequencer').getNode('buffers_num').read()
            self._glib.dispatch()
            # When set to 4 this produces duplicate entries, 3 (= 2 full buffers)
            # avoids this.
            if freeBuffers < 3:
                if shutterCounter % 2000 == 0:
                    startTime = time.time()
                    shutterTimeStart = shutterCounter
                if shutterCounter % 100 == 0 and (shutterCounter - shutterTimeStart) >= 0.1:
                    frequency = (shutterCounter - shutterTimeStart) / \
                        (time.time() - startTime)
                MAPSACounter = []
                MAPSAMemory = []
                for iMPA, nMPA in enumerate(self._assembly):
                    counterData = self._glib.getNode("Readout").getNode("Counter").getNode(
                        "MPA" + str(iMPA + 1)).getNode("buffer_" + str(ibuffer+1)).readBlock(25)
                    memoryData = self._glib.getNode("Readout").getNode("Memory").getNode(
                        "MPA" + str(nMPA)).getNode("buffer_" + str(ibuffer+1)).readBlock(216)
                    self._glib.dispatch()
                    MAPSACounter.append(counterData)
                    MAPSAMemory.append(memoryData)
                ibuffer = (ibuffer + 1) % 4
                shutterCounter += 1
                yield shutterCounter, MAPSACounter, MAPSAMemory, freeBuffers, frequency
    
                # Continuous operation in bash loop
                if shutterCounter == numTriggers:
                    endTimeStamp = time.time()
                # Required for automation! Do not stop DAQ until at least
                # 2 seconds after reaching the num trigger limit
                if shutterCounter > numTriggers:
                    if time.time() - endTimeStamp > stopDelay:
                        break
    def recordPlaintext(self):
        counterArray = []
        memoryArray = []
        try:
            for shutter, counter, memory, freeBuffers, frequency in self._acquire(self._args.num_triggers):
                counterArray.append(counter)
                memoryArray.append(memory)
                print "Shutter counter: %s Free buffers: %s Frequency: %s " % (shutter, freeBuffers, frequency)
        except KeyboardInterrupt:
            pass
        if len(counterArray):
            print "End of Run %s" % self._runNumber
            memoryFile = open(os.path.join(
                self._args.output_dir, 'run%s_memory.txt' % ('{0:04d}'.format(self._runNumber))), 'w')
            counterFile = open(os.path.join(
                self._args.output_dir, 'run%s_counter.txt' % ('{0:04d}'.format(self._runNumber))), 'w')
            for i, shutter in enumerate(counterArray):
                for j, mpa in enumerate(shutter):
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
        self._tfile = TFile(filename, "RECREATE")
        trees = []
        counterFormat = "pixel[48]/s"
        noProcessingFormat = "pixels[96]/l:bunchCrossingId[96]/s:header[96]/b:numEvents/b:corrupt/b"
        flood = [{
            "counter": RippleCounterBranch(),
            "noProcessing": MemoryNoProcessingBranch(),
        }]*len(self._assembly)
        for i, mpa in enumerate(self._assembly):
            tree = TTree("mpa{0}".format(mpa), "MPA{0} event tree".format(mpa))
            trees.append(tree)
            tree.Branch("rippleCounter", flood[i]["counter"], counterFormat)
            tree.Branch("memoryNoProcessing", flood[i]["noProcessing"], noProcessingFormat)
        try:
            totalEvents = 0
            for shutter, counters, memories, freeBuffers, frequency in self._acquire(self._args.num_triggers):
                for data, tree, counter, memory in zip(flood, trees, counters, memories):
                    for i, val in enumerate(itertools.islice(counter, 1, len(counter))):
                        # According to Moritz:
                        # "Mask to select left pixel. First bit is not
                        # considered as this seems sometimes to be set
                        # erronously. (Lots of entries with
                        # 0b1000000000000000)"
                        data["counter"].pixels[i*2 + 0] = val & 0x7FFF # left
                        data["counter"].pixels[i*2 + 1] = (val >> 16) & 0x7FFF # right
                    # convert memory from uhal-format to ctype bytes array
                    memory_ints = (c_uint*216)(*memory)
                    memory_bytes = cast(memory_ints, POINTER(c_ubyte))
                    # reset fill array
                    data["noProcessing"].pixelMatrix = (c_ulonglong*96)(0)
                    data["noProcessing"].bunchCrossingId = (c_ushort*96)(0)
                    data["noProcessing"].header = (c_ubyte*96)(0)
                    data["noProcessing"].corrupt = c_ubyte(0)
                    # iterate over memory in multipletts of 9 bytes (one 72 bit event)
                    evtIdx = 0
                    numEvents = 0
                    for evtIdx in reversed(xrange(0, 96)):
                        evtData = tuple(
                            itertools.islice(memory_bytes,
                                evtIdx*9, evtIdx*9 + 9))
                        data["noProcessing"].header[95-evtIdx] = evtData[8]
                        if data["noProcessing"].header[95-evtIdx] == 0x00:
                            break
                        elif data["noProcessing"].header[95-evtIdx] != 0xFF:
                            data["noProcessing"].corrupt = c_ubyte(evtIdx + 1)
                            break
                        numEvents += 1
                        # bytes 1-8 as 64 bit integer, 1&2 are buch crossing id
                        pixelMatrix = ((evtData[5] << 40) | (evtData[4] << 32) |
                                       (evtData[3] << 24) | (evtData[2] << 16) |
                                       (evtData[1] << 8) | evtData[0])
                        bxid = ((evtData[7] << 8) | evtData[6])
                        data["noProcessing"].bunchCrossingId[95-evtIdx] = bxid
                        data["noProcessing"].pixelMatrix[95-evtIdx] = pixelMatrix
                    totalEvents += numEvents
                    data["noProcessing"].numEvents = c_ubyte(numEvents)
                    tree.Fill()
                # Fancy shmancy visual output
                progress[int(len(progress)*float(shutter)/float(self._args.num_triggers)) % len(progress)] = "#"
                sys.stdout.write("\r\x1b[K [{3}] Shutter={0}  Free bufs={1}  freq={2:.0f} Hz  #events={6}  [{4}] {5:.0f}%".format(
                    shutter, freeBuffers, frequency,
                    spinner[shutter % len(spinner)],
                    "".join(progress),
                    float(shutter) / float(self._args.num_triggers) * 100,
                    totalEvents
                ))
                sys.stdout.flush()
        except KeyboardInterrupt:
            pass
        sys.stdout.write("\n")
        self._tfile.Write()
        self._tfile.Close()
        print "End of Run", self._runNumber	
		
daq= daq_continous_2MPA(parser)

daq.create_tree()
daq.acquisition_start()
daq.write_close()





