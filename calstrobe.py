from classes import *
import xml.etree.ElementTree
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment
import sys, select, os, array
from array import array
import ROOT
from ROOT import TGraph, TDirectory, TGraphErrors, TCanvas, gPad, TFile, TLine, THStack, TH1I, TH1F, TMath, TF1, TString, TObject, TMultiGraph, TPaveText

import numpy as np
import time 

import matplotlib.pyplot as plt
from matplotlib.pyplot import show, plot

from optparse import OptionParser



scalefac = 1.456/3.75

def take_data(caldac,config, rangeval, mapsa, buffnum, x1, y1, daq, strobe_sets):
	daq.Strobe_settings(strobe_sets[0],strobe_sets[1],strobe_sets[2],strobe_sets[3],strobe_sets[4])

	count_arr=np.zeros((no_mpa_light,256,48))
	
	for xx in range(0,256):
		x = xx
		if x%options.res!=0:
			continue
		if x%10==0:
			print "THDAC " + str(x)

		config.modifyperiphery('THDAC',[x]*6)
		config.upload()
		config.write()
		for z in range (0,rangeval):
			mapsa.daq().Sequencer_init(smode,sdur)
			time.sleep(0.002)
			pix,mem = mapsa.daq().read_data(buffnum)
			time.sleep(0.002)
			ipix=0
			for p in pix:
				p.pop(0)
				p.pop(0)
				count_arr[ipix][x]=count_arr[ipix][x]+np.array(array('d',p))
				# if (x==75 and ipix==0):
				# 	print ipix
				# 	print count_arr[ipix][x]
				if z ==(rangeval-1):
					y1.append([])
					y1[ipix].append(array('d',count_arr[ipix][x]))
				ipix+=1
		x1.append(x)


def plot_results(caldac,no_mpa_light,x1,y1, c1, backup):
	savestr =str(caldac)
	col=1
	xvec =  np.array(x1, dtype='uint16')
	xdacval = 0.
	thdacvv = []
	yarrv = []
	xdvals = []
	linearr = []
	stackarr = []
	fitfuncarr = []
	fitparameterarray = []
	for i in range(0,no_mpa_light):
		if(backup.GetDirectory("MPA_"+str(i))):
			backup.cd("MPA_"+str(i))
		else:
			backup.mkdir("MPA_"+str(i))
			backup.cd("MPA_"+str(i))
		calibconfxmlroot	=	calibconfsxmlroot[i]
		xdvals.append(0.)
		c1.cd(i+1)
		thdacv = []
		yarr =  np.array(y1[i])
		linearr.append([])
		gr1 = []
		lines = []
		fitfuncarr.append([])
		fitfuncs = []
		fitparameterarray.append([])
		fitparams = []
		yarrv.append(yarr)
		stackarr.append(THStack('a','pixel curves;DAC Value (1.456 mV);Counts (1/1.456)'))
		for iy1 in range(0,len(yarr[0,:])):
			yvec = yarr[:,iy1]
			# if max(yvec)==0:
				# print "zero"
			gr1.append(TH1I(str(iy1),';DAC Value (1.456 mV);Counts (1/1.456)',len(x1),0,x1[-1]))
			gr1[iy1].Sumw2(ROOT.kFALSE)
			for j in np.nditer(xvec):
				gr1[iy1].SetBinContent(gr1[iy1].FindBin(j),(np.array(yvec,dtype='int')[j]))
			gr1[iy1].Sumw2(ROOT.kTRUE)
			color=iy1%9+1
			gr1[iy1].SetLineColor(color)
			gr1[iy1].SetMarkerColor(color)
			gr1[iy1].SetFillColor(color)
			gr1[iy1].SetLineStyle(1)
			gr1[iy1].SetLineWidth(1)
			gr1[iy1].SetFillStyle(1)
			gr1[iy1].SetMarkerStyle(1)
			gr1[iy1].SetMarkerSize(.5)
			gr1[iy1].SetMarkerStyle(20)
			fitfuncs.append(TF1('gaus','gaus', 0,256))
			fitfuncs[iy1].SetNpx(256)
			fitfuncs[iy1].SetParameters(gr1[iy1].GetMaximum(),gr1[iy1].GetMean(),gr1[iy1].GetRMS());
			cloned = gr1[iy1].Clone()
			cloned.SetDirectory(0)
			fitparams.append([])
			mean=0
			if gr1[iy1].GetMaximum()<-1:
				gr1[iy1].Fit(fitfuncs[iy1],'rq +rob=0.95','',0,256)
				fitparams[iy1].append(fitfuncs[iy1].GetParameter(0))
				fitparams[iy1].append(fitfuncs[iy1].GetParameter(1))
				fitparams[iy1].append(fitfuncs[iy1].GetParameter(2))
				fitparams[iy1].append(fitfuncs[iy1].GetParError(0))
				fitparams[iy1].append(fitfuncs[iy1].GetParError(1))
				fitparams[iy1].append(fitfuncs[iy1].GetParError(2))
				if(fitfuncs[iy1].GetNDF()>0):
					fitparams[iy1].append(fitfuncs[iy1].GetChisquare()/fitfuncs[iy1].GetNDF())
				else:
					fitparams[iy1].append(0)
				mean=fitfuncs[iy1].GetParameter(1)
			else:
				for kk in range(0,7):
					fitparams[iy1].append(0)
			fitparameterarray[i].append(fitparams[iy1])
			fitfuncarr[i].append(fitfuncs[iy1])
			stackarr[i].Add(cloned)
			if iy1==(len(yarr[0,:])-1):
				stackarr[i].Draw('nostack hist e1 x0')
				# for fitfuncs1 in fitfuncarr[i]:
				# 	fitfuncs1.Draw("same")
				# for lines1 in linearr[i]:
				# 	lines1.Draw("same")
				if(stackarr[i].GetMaximum()>1):
					Maximum = TMath.Power(10,(round(TMath.Log10(stackarr[i].GetMaximum()))-1))
					stackarr[i].SetMinimum(.1)
					stackarr[i].SetMaximum(Maximum)
					# gPad.SetLogy()
				gPad.Modified()
				gPad.Update()
			gr1[iy1].SetLineColor(1)
			gr1[iy1].SetMarkerColor(1)
			gr1[iy1].SetFillColor(1)
			gr1[iy1].Write(str(iy1)+'CAL'+savestr)
			# fitfuncs[iy1].Write(str(iy1)+savestr+'fit')
		# print thdacv
	backup.cd()
	if(backup.GetDirectory("Canvas")):
		backup.cd("Canvas")
	else:
		backup.mkdir("Canvas")
		backup.cd("Canvas")
	c1.Write('CALDAC_'+savestr)
	c1.Clear('D')
	return 0

parser = OptionParser()
parser.add_option('-s', '--setting', metavar='F', type='string', action='store',
# default	=	'none',
default	=	'calibration',
dest	=	'setting',
help	=	'settings ie default, calibration, testbeam etc')

parser.add_option('-c', '--charge', metavar='F', type='int', action='store',
default	=	70,
dest	=	'charge',
help	=	'Charge for caldac')

parser.add_option('-w', '--shutterdur', metavar='F', type='int', action='store',
default	=	0xFFFE,
dest	=	'shutterdur',
help	=	'shutter duration')


parser.add_option('-n', '--number', metavar='F', type='int', action='store',
default	=	0xFFE,
dest	=	'number',
help	=	'number of calstrobe pulses to send')

parser.add_option('-r', '--res', metavar='F', type='int', action='store',
default	=	1,
dest	=	'res',
help	=	'resolution 1,2,3... 1 is best')

parser.add_option('-y', '--string ', metavar='F', type='string', action='store',
default	=	'',
dest	=	'string',
help	=	'extra string')

parser.add_option('-t', '--type', metavar='TYPE', type='int', action='store',
default	=	0,
dest	=	'cal_type',
help	=	'Type of fast calibration to be performed: 0 standard, 1 experimental')

parser.add_option('-k', '--k_repetiions', metavar='REPETIONS', type='int', action='store',
default	=	1,
dest	=	'k_reps',
help	=	'k repetions of aquisitions with shutterduration s')


(options, args) = parser.parse_args()


a = uasic(connection="file://connections_test.xml",device="board0")
mapsa = MAPSA(a)
read = a._hw.getNode("Control").getNode('firm_ver').read()
a._hw.dispatch()
print "Running firmware version " + str(read)


a._hw.getNode("Control").getNode("logic_reset").write(0x1)
a._hw.dispatch()

a._hw.getNode("Control").getNode("MPA_clock_enable").write(0x1)
a._hw.dispatch()


no_mpa_light = 6
smode = 0x0
sdur = options.shutterdur


snum = options.number
sdel = 0xF
slen = 0xF
sdist = 0xFF

dcindex=1
buffnum=1
	
mpa = []  
for i in range(1,no_mpa_light+1):
		mpa.append(mapsa.getMPA(i))

Confnum=1
configarr = []
if options.setting=='calibration':
	CE=1
else:
	CE=0
SP=0

nshut = 1

iterarr=[]
backup=TFile("plots/Caldac_"+options.string+".root","recreate")

c1 = TCanvas('c1', 'Pixel Monitor ', 700, 900)
c1.Divide(3,2)

for it in range (0,5):
	confstr='calibrated'
	config = mapsa.config(Config=1,string=confstr)
	config.upload()
	
	charge = it*10

	# confdict = {'OM':[3]*6,'RT':[0]*6,'SCW':[0]*6,'SH2':[0]*6,'SH1':[0]*6,'THDAC':[0]*6,'CALDAC':[options.charge]*6,'PML':[1]*6,'ARL':[1]*6,'CEL':[CE]*6,'CW':[0]*6,'PMR':[1]*6,'ARR':[1]*6,'CER':[CE]*6,'SP':[SP]*6,'SR':[1]*6,'TRIMDACL':[31]*6,'TRIMDACR':[31]*6}
	confdict = {'OM':[3]*6,'RT':[0]*6,'SCW':[0]*6,'SH2':[0]*6,'SH1':[0]*6,'THDAC':[0]*6,'CALDAC':[charge]*6,'PML':[1]*6,'ARL':[1]*6,'CEL':[CE]*6,'CW':[0]*6,'PMR':[1]*6,'ARR':[1]*6,'CER':[CE]*6,'SP':[SP]*6,'SR':[1]*6}
	config.modifyfull(confdict)
	
	strobe_sets = [snum,sdel,slen,sdist,1]
	# mapsa.daq().Strobe_settings(snum,sdel,slen,sdist,1)
	daq = mapsa.daq()
	# .Strobe_settings(snum,sdel,slen,sdist,cal=CE)
	
	x1 = array('d')
	y1 = []
	rangeval = options.k_reps
	# Take data now 
	take_data(it,config, rangeval, mapsa, buffnum, x1, y1, daq, strobe_sets)
		
	calibconfs = config._confs
	calibconfsxmlroot = config._confsxmlroot
	
	# Plot the Results 
	dummyarr = plot_results(charge, no_mpa_light,x1,y1, c1, backup)
backup.Close()
print ([31]*6)
print ""
print "Done"
