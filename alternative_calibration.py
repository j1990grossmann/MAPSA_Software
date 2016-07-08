
from classes import *
import xml.etree.ElementTree
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment
#import ROOT
#from ROOT import TGraph
import sys, select, os, array
from array import array
import ROOT
from ROOT import TGraph,  TGraphErrors, TCanvas, gPad, TFile, TLine, THStack, TH1I, TH1F, TMath, TF1, TString, TObject, TMultiGraph, TPaveText

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.pyplot import show, plot

from optparse import OptionParser



scalefac = 1.456/3.75

#The current fast trimming procedure for data of one pixel
def traditional_trim( xvec, yvec, prev_trim, i):
	"The traditional fast trimming algorithm, which looks for a center of gravity between the two nearest points to halfmax"
	halfmax = max(yvec)/2.0
	# if i==0:
		# print yvec
		# print 'halfmax', halfmax
	maxbin = np.where(yvec==max(yvec))
	for ibin in range(0,len(xvec)-1):		
		xval = xvec[ibin]
		xval1 = xvec[ibin+1]
		yval = yvec[ibin]
		yval1 = yvec[ibin+1]
		#if xdacval<1000:
			#print "maxbin" + str(maxbin[0][0])
			#print "iy1 "+str(iy1)+" ibin " + str(ibin) + " xdacval "+ str(xdacval)
		if (yval1-halfmax)<0.0 and ibin>maxbin[0][0]:
			# if i==0:
				# print "ibin " + str(ibin)
			xdacval = (abs(yval-halfmax)*xval + abs(yval1-halfmax)*xval1)/(abs(yval-halfmax) + abs(yval1-halfmax))
			#print "ptrim " + str(prev_trim) 
			#print "halfmax " +  str(halfmax) + " xvec " + str(xvec[maxbin])
			#if abs(yval-halfmax)<abs(yval1-halfmax):
			#	xdacval = xval
			#else:
			#	xdacval = xval1
			#print "xdacval " + str(xdacval)
			trimdac = 31 + prev_trim - int(round(xdacval*scalefac))
			xdacval = xdacval*scalefac
			#print trimdac
			break	
		if ibin==len(xvec)-2:
			xdacval = 0
			trimdac = int(prev_trim)
			print "UNTRIMMED"
			break
	return (xdacval,trimdac)

def peak1d(y,i,j,count):
	m=(i+j)/2
	if y[m-1]<y[m] and y[m+1]<y[m]:
		return m
	elif y[m]<=y[m-1]:
		count+=1
		return peak1d(y,i,m-1,count)
	elif y[m]<=y[m+1]:
		count+=1
		return peak1d(y,m+1, j,count)
	elif count ==255:
		return 0


def new_trim1( xvec, yvec, prev_trim, i, mean):
	"The new trimming algorithm, which uses the divide and conquer algorithm"
	count = 0
	# xdacval = peak1d(yvec,0,256,count)
	# xdacval = (np.where(yvec==max(yvec)))[0][0]
	# xdacval = ROOT.TMath.Median(256,array('d',xvec),array('d',yvec))
	xdacval=mean
	if xdacval > 0:
		trimdac = 31 + prev_trim - int(round(xdacval*scalefac))
		xdacval = xdacval*scalefac
	else:
		trimdac = int(prev_trim)
		print "UNTRIMMED"
	return (xdacval,trimdac)

def new_trim( xvec, yvec, prev_trim, i):
	"The new trimming algorithm, which uses the divide and conquer algorithm"
	count = 0
	# xdacval = peak1d(yvec,0,256,count)
	# xdacval = (np.where(yvec==max(yvec)))[0][0]
	xdacval = ROOT.TMath.Median(256,array('d',xvec),array('d',yvec))
	if xdacval > 0:
		trimdac = 31 + prev_trim - int(round(xdacval*scalefac))
		xdacval = xdacval*scalefac
	else:
		trimdac = int(prev_trim)
		print "UNTRIMMED"
	return (xdacval,trimdac)

def take_data(config, rangeval, mapsa, buffnum, x1, y1):
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
			pix,mem = mapsa.daq().read_data(buffnum)
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


def plot_results(switch_pre_post, no_mpa_light,x1,y1,calibconfsxmlroot, prev_fit_mat):
	drawstr = ""
	savestr =''
	col=1
	if switch_pre_post==0:
		  savestr='pre'
	else :
		  savestr='post'
		  col=2
		  drawstr=" same"

	xvec =  np.array(x1, dtype='uint16')
	xdacval = 0.
	thdacvv = []
	yarrv = []
	xdvals = []
	linearr = []
	stackarr = []
	fitfuncarr = []
	fitparameterarray = []
	c1 = TCanvas('c1', 'Pixel Monitor '+savestr, 700, 900)
	c1.Divide(3,2)
	for i in range(0,no_mpa_light):
		backup=TFile("plots/backup_"+savestr+"Calibration_"+options.string+"_MPA"+str(i)+".root","recreate")
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
		# hstack = THStack('a','pixel curves;DAC Value (1.456 mV);Counts (1/1.456)')
		for iy1 in range(0,len(yarr[0,:])):
			yvec = yarr[:,iy1]
			if max(yvec)==0:
				print "zero"
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
			if gr1[iy1].GetMaximum()>1:
				gr1[iy1].Fit(fitfuncs[iy1],'rq +rob=0.95','same',0,256)
				fitparams[iy1].append(fitfuncs[iy1].GetParameter(0))
				fitparams[iy1].append(fitfuncs[iy1].GetParameter(1))
				fitparams[iy1].append(fitfuncs[iy1].GetParameter(2))
				fitparams[iy1].append(fitfuncs[iy1].GetParError(0))
				fitparams[iy1].append(fitfuncs[iy1].GetParError(1))
				fitparams[iy1].append(fitfuncs[iy1].GetParError(2))
				fitparams[iy1].append(fitfuncs[iy1].GetChisquare()/fitfuncs[iy1].GetNDF())
				mean=fitfuncs[iy1].GetParameter(1)
			else:
				for kk in range(0,7):
					fitparams[iy1].append(0)
			fitparameterarray[i].append(fitparams[iy1])
			fitfuncarr[i].append(fitfuncs[iy1])
			stackarr[i].Add(cloned)
			if iy1==(len(yarr[0,:])-1):
				stackarr[i].Draw('nostack hist e1 x0')
				for fitfuncs1 in fitfuncarr[i]:
					fitfuncs1.Draw("same")
				# for lines1 in linearr[i]:
					# lines1.Draw("same")
				if(stackarr[i].GetMaximum()>1):
					Maximum = TMath.Power(10,(round(TMath.Log10(stackarr[i].GetMaximum()))))
					stackarr[i].SetMinimum(.1)
					stackarr[i].SetMaximum(Maximum)
					gPad.SetLogy()
				gPad.Update()
			gr1[iy1].SetLineColor(1)
			gr1[iy1].SetMarkerColor(1)
			gr1[iy1].SetFillColor(1)
			gr1[iy1].Write(str(iy1))
			fitfuncs[iy1].Write(str(iy1)+'fit')
			#Get prevous trim value for the channel
			if iy1%2==0:
				prev_trim = int(calibconfxmlroot[(iy1)/2+1].find('TRIMDACL').text)
			else:
				prev_trim = int(calibconfxmlroot[(iy1+1)/2].find('TRIMDACR').text)
			trimdac = 0
			# Now we have the routine to find the midpoint
			# dummy = []
			# dummy = traditional_trim(xvec,yvec,prev_trim,i)
			dummy = new_trim1(xvec,yvec,prev_trim,i,mean)
			# xdacval = dummy[0]
			# trimdac = dummy[1]
			xdacval = dummy[0]
			trimdac = dummy[1]
			xdvals[i]= xdacval
			thdacv.append(trimdac)
			lines.append(TLine(xdacval/scalefac,.1,xdacval/scalefac,cloned.GetMaximum()))
			linearr[i].append(lines[iy1])
			linearr[i][iy1].SetLineColor(2)
		thdacvv.append(thdacv)
		# print thdacv
	c1.SaveAs('plots/Scurve_Calibration'+options.string+'_'+savestr+'.root', 'root')
	c1.SaveAs('plots/Scurve_Calibration'+options.string+'_'+savestr+'.pdf', 'pdf')
	c1.SaveAs('plots/Scurve_Calibration'+options.string+'_'+savestr+'.png', 'png')
	backup.Close()
	objarr= []
	normgraph      = TGraphErrors(no_mpa_light*48)
	meangraph      = TGraphErrors(no_mpa_light*48) 
	sigmagraph     = TGraphErrors(no_mpa_light*48) 
	chisquaregraph = TGraphErrors(no_mpa_light*48)
	mean_corrgraph = TGraphErrors(no_mpa_light*48)
	normgraph      .SetName('normgraph_' +savestr)
	meangraph      .SetName('meangraph_' +savestr)
	sigmagraph     .SetName('sigmagraph_'+savestr)
	chisquaregraph .SetName('chisquare_' +savestr)
	mean_corrgraph .SetName('mean_corr_' +savestr)
	meanhist       = TH1F('meanhist_'+savestr,'Mean DAC; DAC Value (1.456 mV); counts', 256,0,255)
	sigmahist      = TH1F('sigmahist_'+savestr,'Sigma DAC; DAC Value (1.456 mV); counts', 250,0,10)
	normgraph.SetTitle('Normalization; Channel; Normalization')
	meangraph.SetTitle('Mean; Channel; DAC Value (1.456 mV)')
	sigmagraph.SetTitle('Sigma; Channel; DAC Value (1.456 mV)')
	chisquaregraph.SetTitle('Chisquared/NDF; Channel; Chisquared/NDF ')
	mean_corrgraph.SetTitle('Correction; chann; DAC Value (1.456 mV)')
	objarr.append([normgraph,meangraph,sigmagraph,chisquaregraph,meanhist,sigmahist,mean_corrgraph])
	A = np.array(fitparameterarray)
	pointno = 0
	for j in range(0,A.shape[0]):
		for j1 in range (0, A.shape[1]):
			# print A[j][j1][2]
			normgraph.SetPoint(pointno, pointno+1,A[j][j1][0])
			normgraph.SetPointError(pointno, 0,A[j][j1][3])	  
			meangraph.SetPoint(pointno, pointno+1,A[j][j1][1])
			meangraph.SetPointError(pointno, 0,A[j][j1][4])	  
			sigmagraph.SetPoint(pointno, pointno+1,A[j][j1][2])
			sigmagraph.SetPointError(pointno, 0,A[j][j1][5])
			chisquaregraph.SetPoint(pointno, pointno+1,A[j][j1][6])
			chisquaregraph.SetPointError(pointno, 0 ,0)
			if(switch_pre_post==1):
				mean_corrgraph.SetPoint(pointno,pointno+1,A[j][j1][1]-prev_fit_mat[j][j1][1])
				mean_corrgraph.SetPointError(pointno,0,A[j][j1][4]-prev_fit_mat[j][j1][4])
			if(A[j][j1][1]>0):
				meanhist.Fill(A[j][j1][1])
			if(A[j][j1][2]>0):
				sigmahist.Fill(A[j][j1][2])
			pointno+=1
	length = len(yarrv[0][0,:])
	return thdacvv, xdvals, A, length, objarr

parser = OptionParser()
parser.add_option('-s', '--setting', metavar='F', type='string', action='store',
default	=	'none',
dest	=	'setting',
help	=	'settings ie default, calibration, testbeam etc')

parser.add_option('-c', '--charge', metavar='F', type='int', action='store',
default	=	70,
dest	=	'charge',
help	=	'Charge for caldac')

parser.add_option('-w', '--shutterdur', metavar='F', type='int', action='store',
default	=	0xFFFFF,
dest	=	'shutterdur',
help	=	'shutter duration')


parser.add_option('-n', '--number', metavar='F', type='int', action='store',
default	=	0x5,
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
help	=	'K repetions of aquisitions with shutterduration s')


(options, args) = parser.parse_args()



a = uasic(connection="file://connections_test.xml",device="board0")
mapsa = MAPSA(a)
read = a._hw.getNode("Control").getNode('firm_ver').read()
a._hw.dispatch()
print "Running firmware version " + str(read)


#a._hw.getNode("Control").getNode("logic_reset").write(0x1)
#a._hw.dispatch()
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


config = mapsa.config(Config=1,string='default')
config.upload()


confdict = {'OM':[3]*6,'RT':[0]*6,'SCW':[0]*6,'SH2':[0]*6,'SH1':[0]*6,'THDAC':[0]*6,'CALDAC':[options.charge]*6,'PML':[1]*6,'ARL':[1]*6,'CEL':[CE]*6,'CW':[0]*6,'PMR':[1]*6,'ARR':[1]*6,'CER':[CE]*6,'SP':[SP]*6,'SR':[1]*6,'TRIMDACL':[31]*6,'TRIMDACR':[31]*6}
# confdict = {'OM':[3]*6,'RT':[0]*6,'SCW':[0]*6,'SH2':[0]*6,'SH1':[0]*6,'THDAC':[0]*6,'CALDAC':[options.charge]*6,'PML':[1]*6,'ARL':[1]*6,'CEL':[CE]*6,'CW':[0]*6,'PMR':[1]*6,'ARR':[1]*6,'CER':[CE]*6,'SP':[SP]*6,'SR':[1]*6}
config.modifyfull(confdict) 

mapsa.daq().Strobe_settings(snum,sdel,slen,sdist,cal=CE)

x1 = array('d')
y1 = []
rangeval = options.k_reps
# Take data now 
take_data(config, rangeval, mapsa, buffnum, x1, y1)
	
calibconfs = config._confs
calibconfsxmlroot = config._confsxmlroot

c3 = TCanvas('c3', 'Calibration Monitor', 700, 900)
c3.Divide(3,3)
prev_fit_mat = []
# Plot the Results 
dummyarr = plot_results(0, no_mpa_light,x1,y1,calibconfsxmlroot, prev_fit_mat)

thdacvv = dummyarr[0]
xdvals = dummyarr[1]
prev_fit_mat = dummyarr[2]
length = dummyarr[3]

ave = 0
for x in xdvals:
	ave+=x/48.
ave/=6.

offset = []
avearr = []
mpacorr = []
for i in range(0,no_mpa_light):
	thdacv = thdacvv[i]
	ave15 = 0
	for j in thdacvv[i]:
		ave15+=j
	ave15/=len(thdacvv[i])
	avearr.append(ave15)
	mpacorr.append(xdvals[i]/48.-ave)
	
print 'average correction'
print avearr
print mpacorr
for i in range(0,no_mpa_light):
	thdacv = thdacvv[i]
	range1 = min(thdacv)	
	range2 = max(thdacv)	
	offset.append(15-int(round(avearr[i]+mpacorr[i])))
# print offset

thdacvvorg = []
cols = [[],[],[],[],[],[]]
# for iy1 in range(0,len(yarrv[0][0,:])):
for iy1 in range(0,length):
	thdacvvorg.append(np.array(thdacvv)[:,iy1])
	upldac = []
	for i in range(0,no_mpa_light):
		thdacv = thdacvv[i]
		upldac.append(thdacv[iy1]+offset[i])


	for u in range(0,len(upldac)):
		upldac[u] = max(0,upldac[u])
		upldac[u] = min(31,upldac[u])
		if upldac[u]==31:
			cols[u].append(2)
		elif upldac[u]==0:
			cols[u].append(4)
		else:
			cols[u].append(1)
	#print upldac

	if iy1%2==0:
		config.modifypixel((iy1)/2+1,'TRIMDACL',upldac)
	else:
		config.modifypixel((iy1+1)/2,'TRIMDACR',upldac)


config.modifyperiphery('THDAC',[100]*6)
#config.upload()
#config.write()
for i in range(0,no_mpa_light):
	xmlrootfile = config._confsxmltree[i]
	print xmlrootfile
	a = config._confsxmlroot[i]
	print "writing data/Conf_calibrated_MPA"+str(i+1)+"_config1.xml"
	xmlrootfile.write("data/Conf_calibrated_MPA"+str(i+1)+"_config1.xml")


print "Testing Calibration"


config1 = mapsa.config(Config=1,string='calibrated')
config1.upload()

config1.modifyperiphery('OM',[3]*6)
config1.modifyperiphery('RT',[0]*6)
config1.modifyperiphery('SCW',[0]*6)
config1.modifyperiphery('SH2',[0]*6)
config1.modifyperiphery('SH1',[0]*6)
config1.modifyperiphery('THDAC',[0]*6)
config1.modifyperiphery('CALDAC', [options.charge]*6)
for x in range(1,25):
	config1.modifypixel(x,'PML', [1]*6)
	config1.modifypixel(x,'ARL', [1]*6)
	config1.modifypixel(x,'CEL', [CE]*6)
	config1.modifypixel(x,'CW', [0]*6)
	config1.modifypixel(x,'PMR', [1]*6)
	config1.modifypixel(x,'ARR', [1]*6)
	config1.modifypixel(x,'CER', [CE]*6)
	config1.modifypixel(x,'SP',  [SP]*6) 
	config1.modifypixel(x,'SR',  [1]*6) 

config1.write()


x1 = array('d')
y1 = []

take_data(config, rangeval, mapsa, buffnum, x1, y1)

xvec =  np.array(x1)
yarrv = []

dummyarr1 = plot_results(1, no_mpa_light,x1,y1,calibconfsxmlroot, prev_fit_mat)

objarr=[]
objarr.append([])
objarr.append([])
objarr[0]=dummyarr[4]
objarr[1]=dummyarr1[4]

mglist = []
stacklist = []
listind=0
stackind=0

ROOT.gStyle.SetOptStat('1111')
for index1,objs1 in enumerate(objarr[0]):
	for index,objs in enumerate(objs1):
		objs.SetLineColor(1)
		objs.SetMarkerColor(1)
		objs.SetMarkerStyle(6)
		objarr[1][0][index].SetLineColor(2)  
		objarr[1][0][index].SetMarkerColor(2)
		objarr[1][0][index].SetMarkerStyle(6)
		c3.cd(index+1)
		print objs.GetName()
		if objs.InheritsFrom("TGraph"):
			mglist.append(TMultiGraph('mg_'+str(listind),objs.GetTitle()))
			mglist[listind].Add(objarr[1][0][index],'p')
			mglist[listind].Add(objs,'p')
			mglist[listind].Draw('a')
			listind+=1
		elif objs.InheritsFrom("TH1"):
			stacklist.append(THStack('stack_'+str(stackind),objs.GetTitle()))
			stacklist[stackind].Add(objarr[1][0][index])
			stacklist[stackind].Add(objs)
			stacklist[stackind].Draw('nostack hist x0')
			stackind+=1
c3.Update()
c3.cd(8)
text = TPaveText(.05,.1,.95,.8);
RMS1=ROOT.TMath.RMS(240,array('d',objarr[0][0][1].GetY()))
RMS2=ROOT.TMath.RMS(240,array('d',objarr[1][0][1].GetY()))
text.AddText("RMS (Mean) before calibration = "+str(RMS1));
text.AddText("RMS (Mean) after  calibration = "+str(RMS2));
text.Draw()


c3.Update()
c3.Modified()
c3.SaveAs('plots/Scurve_Calibration'+options.string+'_results'+'.png' , 'png')
c3.SaveAs('plots/Scurve_Calibration'+options.string+'_results'+'.pdf' , 'pdf')
c3.SaveAs('plots/Scurve_Calibration'+options.string+'_results'+'.root', 'root')

print ""
print "Done"
