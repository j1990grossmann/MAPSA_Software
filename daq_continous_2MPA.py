import pdb
import errno
import sys
import os
#from classes import *
from array import array
import numpy as np
from ROOT import TGraph, TCanvas, TLine, TTree, TFile, TBranch, TFile
import time
import datetime
from optparse import OptionParser

class daq_coninous_2MPA:
    def __init__(self):
        self._Result_Dict=[]
        self._Keys=[]
        self._Values=[]
        self._assembly = []
        self._number_mpa_light=len(self._assembly)
        #Get Workingdir, DataDir, Config Dir
        self._datapath, self._runNumber, self._config_dir = self._create_data_dir()
        self.timestr = datetime.datetime.now().time().isoformat().replace(":","").replace(".","")
        self._tfile = TFile()
        self._tree  = TTree()
        self._create_tree()
        ##filepath = os.path.dirname(os.path.realpath(__file__))
        ##create ttree and open root file
        #create_ttree(tree_vars, number_mpa_light, assembly, datapath)
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
    def _create_tree(self):
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
        #self._assembly = [2,5]
        #self._number_mpa_light=len(self._assembly)
        for i in range(0,6):
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
        self._tfile = TFile(self._datapath+'/data.root','recreate')
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
        self._tree.Write()
        self._tfile.Close()
    def _fill_tree (memmode, threshold, vararr, F, tree, no_mpa_light,mpa ):
        for ev_i, ev in enumerate(vararr):
            if ev_i%20==0:
                print ev
                mem={}
                for impa in range(0,no_mpa_light):
                    #print ev["SR_UN_MPA_"+str(impa)]
                    #print len(ev["SR_UN_MPA_"+str(impa)])
                    mem[impa] = mpa[impa].daq().formatmem(ev["SR_UN_MPA_"+str(impa)])
                    memo = mpa[impa].daq().read_memory(mem[impa],memmode)
                    for p in range(0,96):
                        if p>len(memo[0]):
                            memo[0].append(int(0))
                            memo[1].append('0')
                            
                            BXmemo = np.array(memo[0])
                            DATAmemo = np.array(memo[1])
                            
                            DATAmemoint = []
                            for DATAmem in DATAmemo:
                                DATAmemoint.append(long(DATAmem,2)) 

                            ev["SR_BX_MPA_"+str(impa)] = BXmemo
                            ev["SR_MPA_"+str(impa)] = DATAmemoint

                            for tv in tree_vars.keys():
                                if 'SR_UN_MPA' in tv:
                                    continue 
                                for i in range(0,len(ev[tv])):
                                    tree_vars[tv][i] = ev[tv][i]
                                    
                                    # tree.Fill()
#def start_daq (memmode, threshold):
    #assembly = [2,5]
    #number_mpa_light=len(assembly)
    #tree_vars = {}
    ##Get current workingdir
    #datapath, runNumber, config_dir = create_data_dir()
    #print datapath, runNumber, config_dir
    #timestr = datetime.datetime.now().time().isoformat().replace(":","").replace(".","")
    #print timestr
    ##filepath = os.path.dirname(os.path.realpath(__file__))
    ##create ttree and open root file
    #create_ttree(tree_vars, number_mpa_light, assembly, datapath)


    ## Connection and GLIB 
    #a = uasic(connection="file://connections_test.xml",device="board0")
    #glib = a._hw 
    #firmver = glib.getNode("Control").getNode('firm_ver').read()
    #glib.dispatch()
    ## Enable clock on MPA
    #glib.getNode("Control").getNode("MPA_clock_enable").write(0x1)
    #glib.dispatch()
    
    ## Reset all logic on GLIB
    #glib.getNode("Control").getNode("logic_reset").write(0x1)
    #glib.dispatch()
    
    ## Source all classes
    #mapsaClasses = MAPSA(a)
    
    #conf = []
    #mpa = []
    #for iMPA, nMPA  in enumerate(assembly):
        #mpa.append(MPA(glib, iMPA+1)) # List of instances of MPA, one for each MPA. SPI-chain numbering!
        #conf.append(mpa[iMPA].config(config_dir+"/Conf_calibrated_MPA" + str(nMPA)+ "_config1.xml")) # Use trimcalibrated config

    ## Define default config
    #for iMPA in range(0,len(assembly)):
        #conf[iMPA].modifyperiphery('THDAC',threshold) # Write threshold to MPA 'iMPA'
        #conf[iMPA].modifyperiphery('OM',memmode) # Change the aquisition mode
        #conf[iMPA].modifypixel(range(1,25), 'SR', 1) # Enable synchronous readout on all pixels
        #conf[iMPA].upload() # Push configuration to GLIB
    #glib.getNode("Configuration").getNode("mode").write(len(assembly) - 1)
    #conf[iMPA]._spi_wait() # includes dispatch
    
    #glib.getNode("Configuration").getNode("num_MPA").write(len(assembly))
    #glib.getNode("Configuration").getNode("mode").write(len(assembly) - 1) # This is a 'write' and pushes the configuration to the glib. Write must happen before starting the sequencer.
    #conf[0]._spi_wait() # includes dispatch
    
    #glib.getNode("Control").getNode('testbeam_clock').write(0x1) # Enable external clock 
    #glib.getNode("Configuration").getNode("mode").write(len(assembly) - 1)
    #glib.dispatch()
    
    #shutterDur = 0xFFFFFFFF #0xFFFFFFFF is maximum, in clock cycles
    ## shutterDur = 0xA280 #0xFFFFFFFF is maximum, in clock cycles
    ## shutterDur = 0x27100 #0xFFFFFFFF is maximum, in clock cycles
    ## shutterDur = 0xFFFFF #0xFFFFFFFF is maximum, in clock cycles
    
    ## pdb.set_trace()
    #mapsaClasses.daq().Sequencer_init(0x1,shutterDur, mem=1) # Start sequencer in continous daq mode. Already contains the 'write'
    
    #ibuffer = 1
    #shutterCounter = 0
    #counterArray = []
    #memoryArray = []
    #frequency = "Wait"
    
    #triggerStop = 10000
    
    #try:
        #vararr = []
        #while True:
            #freeBuffers = glib.getNode("Control").getNode('Sequencer').getNode('buffers_num').read()
            #glib.dispatch()
            #if freeBuffers < 3: # When set to 4 this produces duplicate entries, 3 (= 2 full buffers) avoids this.  
                #if shutterCounter%2000 == 0:
                    #print "2000 events taken"
                    #startTime = time.time()
                    #shutterTimeStart = shutterCounter

                #if shutterCounter%100 == 0 and (shutterCounter - shutterTimeStart) >= 0.1:
                    #frequency = (shutterCounter - shutterTimeStart)/(time.time() - startTime)

                #MAPSACounter = []
                #MAPSAMemory = []
                ##here one reads the pix and memory
                #pix, mem = mapsaClasses.daq().read_data(ibuffer,False,True,number_mpa_light)
		## print "pix", pix
		## print "mem", mem
		#parray = []
		#marray = []
		#cntspershutter = 0
		#for i in range(0,number_mpa_light):
                    #pix[i].pop(0)
                    #pix[i].pop(0)
                    #parray.append(pix[i])
                    ##marray.append(mpa[i].daq().read_memory(mem[i],memmode))
                    #marray.append(mem[i])
                ## temp_vars_sr_un_mpa = []
                ## temp_vars_ar_mpa = []
                ## for imemo,memo in enumerate(marray):
                ##     temp_vars_sr_un_mpa[imemo]=memo
                ## for ip, p in enumerate(parray):
                ##     temp_vars["AR_MPA_"+str(ip)]=p
                #vararr.append([[marray],[parray]])
                ##counterData1=[]
                ##memoryData1=[]
                ##counterData1 = array('d',pix[1])
                ##memoryData1 = array('d',mem[1])

                #for iMPA, nMPA in enumerate(assembly):
                    #counterData  = glib.getNode("Readout").getNode("Counter").getNode("MPA"+str(iMPA + 1)).getNode("buffer_"+str(ibuffer)).readBlock(25)
                    #memoryData = glib.getNode("Readout").getNode("Memory").getNode("MPA"+str(nMPA)).getNode("buffer_"+str(ibuffer)).readBlock(216)
                    #glib.dispatch()
    
                    ## print "Buffer: %s iMPA: %s nMPA: %s" %(ibuffer, iMPA, nMPA)
                    ## print counterData
                    ## print '{0:032b}'.format(counterData[0])
                    ## print memoryData
                    ## print "\n"
                    
                    #MAPSACounter.append(counterData)
                    #MAPSAMemory.append(memoryData)
    
                #ibuffer += 1
                #if ibuffer > 4:
                    #ibuffer = 1
    
                #shutterCounter+=1
                
                ## Only contains valVectors:
                ##print "mapsa counter"
                ##for count,pix  in enumerate( MAPSACounter):
                    ##print count, array('d',pix)
                ## counterData1 = array('d',MAPSACounter[0])
                ##print "memory"
                ##for count,pix  in enumerate( MAPSAMemory ):
                    ##print count, array('d',pix)
                ## memoryData1 = array('d',MAPSAMemory[0])

                #counterArray.append(MAPSACounter) 
                #memoryArray.append(MAPSAMemory)

                ##numpyarray1 = np.array(counterData1[:][:])
                ##numpyarray2 = np.array(memoryData1[:][:])
                ##print ("counterData "   , len(counterData1))
                ##print ("memoryData"     , len(memoryData1))
                ##print ("counterData ", numpyarray1.shape)
                ##print ("memoryData"  , numpyarray2.shape)

                #if(shutterCounter%100==0):
                    #print "Shutter counter: %s Free buffers: %s Frequency: %s " %(shutterCounter, freeBuffers, frequency)
    
    
                ############### Continuous operation in bash loop
    
                #if shutterCounter == triggerStop:
                    #endTimeStamp = time.time()
                #if shutterCounter > triggerStop:
                    #if time.time() - endTimeStamp > 2:
                        #break
            
    #except KeyboardInterrupt:
        #pass
    
    ##finally:
    ##    while ibuffer <= 4:
    ##
    ##        freeBuffers = glib.getNode("Control").getNode('Sequencer').getNode('buffers_num').read()
    ##        glib.dispatch()
    ##        if freeBuffers < 3:    
    ##            MAPSACounter = []
    ##            MAPSAMemory = []
    ##            for iMPA, nMPA in enumerate(assembly):
    ##               counterData  = glib.getNode("Readout").getNode("Counter").getNode("MPA"+str(iMPA + 1)).getNode("buffer_"+str(ibuffer)).readBlock(25)
    ##               memoryData = glib.getNode("Readout").getNode("Memory").getNode("MPA"+str(nMPA)).getNode("buffer_"+str(ibuffer)).readBlock(216)
    ##                glib.dispatch()
    ##                
    ##                MAPSACounter.append(counterData)
    ##                MAPSAMemory.append(memoryData)
    ##
    ##            shutterCounter += 1        
    ##            ibuffer += 1
    ##
    ##            # Only contains valVectors:
    ##            counterArray.append(MAPSACounter) 
    ##            memoryArray.append(MAPSAMemory)
    ##            print "Shutter counter: %s Buffers num: %s " %(shutterCounter, freeBuffers)
    ##
    
    
    
    #print "End of Run %s" %runNumber
                   
    #memoryFile = open(datapath+'memory.txt', 'w')
    #counterFile = open(datapath+'counter.txt', 'w')
    
    #for i, shutter in enumerate(counterArray):
        #for j,mpa in enumerate(shutter):
            #counterFile.write(str(mpa.value())+"\n")
            #memoryFile.write(str(memoryArray[i][j].value())+"\n")
    
    #counterFile.close()
    #memoryFile.close()
    
    #print "All files saved"

    # nHitMax = 95
    # nPixMax = 48
    # nMPA = 2
    
    # # Create File
    
    # tFile = TFile("output.root","RECREATE")
    
    # # Initialize trees
    
    # treeMPA1 = TTree("MPA1","MPA1 event tree")
    # treeMPA2 = TTree("MPA2","MPA2 event tree")
    
    # nEvents = [array('i',[0]) for x in range(0,nMPA)]
    # nHits = [array('i',[0]) for x in range(0,nMPA)]
    # headerArray = [array('i',[0 for x in range(0,nHitMax)]) for x in range(0,nMPA)]
    # bxArray = [array('i',[0 for x in range(0,nHitMax)]) for x in range(0,nMPA)]
    # hitArrayMemory = [array('i',[0 for x in range(0,nPixMax)]) for x in range(0,nMPA)]
    # hitArrayCounter = [array('i',[0 for x in range(0,nPixMax)]) for x in range(0,nMPA)]
    
    
    # print("Hd: %s" %len(headerArray[0]))
    # print("Bx: %s" %len(bxArray[0]))
    # print("Px: %s" %len(hitArrayMemory[0]))
    
    # treeMPA1.Branch("nEvents", nEvents[0], "nEvents/I")
    # treeMPA1.Branch("nHits", nHits[0], "nHits/I")
    # treeMPA1.Branch("header", headerArray[0], "header[nHits]/I")
    # treeMPA1.Branch("bx", bxArray[0], "bx[nHits]/I")
    # treeMPA1.Branch("pixelHits", hitArrayMemory[0], "pixelHits[nHits]/I")
    # treeMPA1.Branch("pixelCounter",hitArrayCounter[0],"pixelCounter[nHits]/I")
    
    # treeMPA2.Branch("nEvents", nEvents[1], "nEvents/I")
    # treeMPA2.Branch("nHits", nHits[1], "nHits/I")
    # treeMPA2.Branch("header", headerArray[1], "header[nHits]/I")
    # treeMPA2.Branch("bx", bxArray[1], "bx[nHits]/I")
    # treeMPA2.Branch("pixelHits", hitArrayMemory[1], "pixelHits[nHits]/I")
    # treeMPA2.Branch("pixelCounter",hitArrayCounter[1],"pixelCounter[nHits]/I")
    
    # ###############
    
    # counter = 0
    
    # for k, event in enumerate(memoryArray):
    #     for i,mpa in enumerate(event):
    
    #         #############################################
    #         ### Counter: Array[24] -> Array[48] (int) ###
    #         #############################################
    #         counterData = []
    
    #         for x in range(1,len(counterArray[k][i])): # Skip header at [0]
    #             counterData.append(counterArray[k][i][x] & 0x7FFF) # Mask to select left pixel. First bit is not considered as this seems sometimes to be set erronously. (Lots of entries with 0b1000000000000000) 
    #             counterData.append((counterArray[k][i][x] >> 16) & 0x7FFF) # Mask to select right pixel. Same as above.
    
    #         ##########################################################################################
    #         ### Memory: 216x  32-Bit Words -> Array of Hits (Header,BunchCrossing,Pixarray) (Bits) ### 
    #         ##########################################################################################
            
    #         # Mem integer array to binary string in readable order (header,bx,pix) 
    #         binMemStr= ""
    #         for j in range(0,216):
    #             binMemStr = binMemStr + '{0:032b}'.format(mpa[215-j])
    
    #         # String to binary array
    #         binMem = [binMemStr[x:x+72] for x in range(0,len(binMemStr),72)]
    
    #         # Get elements of binary string
    #         hd = []
    #         bx = []
    #         pix = []
    
    #         for entry in binMem[:-1]: # Discard last entry in memory as here the 48th - pixel is always showing a hit, even if pixel is disabled. This is intended as a workaround, the maximum number of hits per pixel and memory is now 95.
    #             hd.append(entry[:8])
    #             bx.append(entry[8:24])
    #             pix.append(entry[24:])
    
    #         #####################################################################
            
    #         # Tree stuff
            
    #         nHitsTmp = 0
    #         for hit in hd:
    #             if hit == "11111111":
    #                 nHitsTmp+=1
                
    #         nHits[i][0] = 95
    #         headerArray[i]=[int(ihd,2) for ihd in hd]
    #         bxArray[i]=[int(ibx,2) for ibx in bx]
    #         hitArrayMemory[i]=pix
    #         hitArrayCounter[i]=counterData
            
            
    #     treeMPA1.Fill()
    #     treeMPA2.Fill()
    
    # tFile.Write()
    # tFile.Close()


parser = OptionParser()

parser.add_option('-s', '--setting', metavar='F', type='string', action='store',
default =       'default',
dest    =       'setting',
help    =       'settings ie default,  testbeam etc')

parser.add_option('-C', '--calib', metavar='F', type='string', action='store',
default =       'False',
dest    =       'calib',
help    =       'calibration')

parser.add_option('-r', '--readout', metavar='F', type='string', action='store',
default =       'both',
dest    =       'readout',
help    =       'readout which data ie counters, memory, both')

parser.add_option('-f', '--format', metavar='F', type='string', action='store',
default =       'noprocessing',
dest    =       'format',
help    =       'memout format noprocessing, stubfinding, centroid, stripemulator ')

parser.add_option('-m', '--mpa', metavar='F', type='int', action='store',
default =       0,
dest    =       'mpa',
help    =       'mpa to configure (0 for all)')

parser.add_option('-c', '--charge', metavar='F', type='int', action='store',
default =       0,
dest    =       'charge',
help    =       'Charge for caldac')

parser.add_option('-t', '--thresh', metavar='F', type='int', action='store',
default =       180,
dest    =       'thresh',
help    =       'threshold')


parser.add_option('-T', '--testclock', metavar='F', type='string', action='store',
default =       'glib',
dest    =       'testclock',
help    =       'test beam clock')



parser.add_option('-n', '--number', metavar='F', type='int', action='store',
default =       0x0,
dest    =       'number',
help    =       'number of calcstrobe pulses to send')




parser.add_option('-x', '--record', metavar='F', type='string', action='store',
default =       'True',
dest    =       'record',
help    =       'record this daq cycle')

parser.add_option('-y', '--daqstring', metavar='F', type='string', action='store',
default =       'none',
dest    =       'daqstring',
help    =       'string to append on daq folder name')

parser.add_option('-z', '--monitor', metavar='F', type='string', action='store',
default =       'False',
dest    =       'monitor',
help    =       'start event monitor in background')


parser.add_option('-w', '--shutterdur', metavar='F', type='int', action='store',
default =       0xFFFFF,
dest    =       'shutterdur',
help    =       'shutter duration')


parser.add_option('-v', '--skip', metavar='F', type='string', action='store',
default =       'True',
dest    =       'skip',
help    =       'skip zero counts')

parser.add_option('-u', '--autospill', metavar='F', type='string', action='store',
default =       'True',
dest    =       'autospill',
help    =       'write every spill')

parser.add_option('-N', '--norm', metavar='F', type='string', action='store',
default =       'False',
dest    =       'norm',
help    =       'use normalization mpa scheme')

parser.add_option('-D', '--direction', metavar='F', type='string', action='store',
default =       'glib',
dest    =       'direction',
help    =       'strip direction (glib or mpa)')

parser.add_option('-L', '--loops', metavar='F', type='int', action='store',
default =       -1,
dest    =       'loops',
help    =       'number of daq loops')


parser.add_option('-p', '--phase', metavar='F', type='int', action='store',
default =       0,
dest    =       'phase',
help    =       'beam phase offset')


(options, args) = parser.parse_args()
formarr = ['stubfinding','stripemulator' ,'centroid','noprocessing']
memmode = formarr.index(options.format)
threshold = options.thresh

#start_daq(memmode,threshold)
DAQ = daq_coninous_2MPA()
DAQ.write_close()
print "imported"
