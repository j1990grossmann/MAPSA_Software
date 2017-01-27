#!/usr/bin/python
import numpy as np
import os.path
import sys
import ROOT
from ROOT import gROOT, TCanvas, TGraphAsymmErrors, TH1, TF1, TH1F, TH1D, TTree, TFile, TTreeReader, TTreeReaderValue, TTreeReaderArray, TH2I, TH2F, TString, THStack, TGraphErrors, TList, TListIter, TIter, TObject, TH1I, TMath, TDirectory, TEfficiency, TF1Convolution, RooFit, TRandom,TAxis
import array as array
import time

points = 2560
points1=int(256*2)
SQRT2=ROOT.TMath.Sqrt2()

def heavyside_function(x,par):
    if x[0]>par[0]:
        return 1
    else:
        return 0
def error_function(x,par):
    return 0.5*(1-ROOT.TMath.Erf((x[0]-par[0])/(par[1]*SQRT2)))
def smoothed_box(x,par):
    return par[0]*0.5*(ROOT.TMath.Erf((x[0]-par[3])/(par[2]*SQRT2))-ROOT.TMath.Erf((x[0]-par[1])/(par[2]*SQRT2)))
def signal_fit(x,par):
    return par[0]*0.5*(ROOT.TMath.Erf((x[0]-par[3])/(par[2]*SQRT2))-ROOT.TMath.Erf((x[0]-par[1])/(par[2]*SQRT2)))+par[4]*ROOT.TMath.Gaus(x[0],par[5],par[6],ROOT.kFALSE)
def signal(x,par):
    if x[0]>par[1]+par[2]:
        return par[3]*0.5*(1-ROOT.TMath.Erf((x[0]-par[4])/((par[2]+par[5])*SQRT2)))
    else:
        return par[3]*0.5*(1+ROOT.TMath.Erf((x[0]-par[1]+par[2])/((par[2]+par[5])*SQRT2)))
def totale(x,par):
    #if x[0]>par[1]:
        #return par[0]*ROOT.TMath.Gaus(x[0],par[1],par[2])+par[3]*0.5*(1-ROOT.TMath.Erf((x[0]-par[4])/((par[2]+par[5])*SQRT2)))
    #else:
        #return par[0]*ROOT.TMath.Gaus(x[0],par[1],par[2])+par[3]*0.5*(1+ROOT.TMath.Erf((x[0]-par[1])/((par[2])*SQRT2)))
    if x[0]>par[1]:
        return par[0]*ROOT.TMath.Gaus(x[0],par[1],par[2])+par[3]*0.5*(1-ROOT.TMath.Erf((x[0]-par[4])/((par[2]+par[5])*SQRT2)))
    else:
        return par[0]*ROOT.TMath.Gaus(x[0],par[1],par[2])+par[3]*0.5*(1+ROOT.TMath.Erf((x[0]-par[1]+par[2])/((par[2])*SQRT2)))
def combined_mean(x,par):
        return 0.5*par[0]*((1-ROOT.TMath.Erf((x[0]-par[1])/(par[2]*SQRT2)))-(1-ROOT.TMath.Erf((x[0]+par[1])/(par[3]*SQRT2))))
def double_gauss(x,par):
        return par[0]*ROOT.TMath.Gaus(x[0],par[1],par[2])+par[3]*ROOT.TMath.Gaus(x[0],par[1],par[4])
def box(x,par):
    if (par[0]<x[0] and x[0]<par[1]):
        return par[2]
    else:
        return 0
def gaussian(x,par):
    return par[0]*ROOT.TMath.Gaus(x[0],par[1],par[2],ROOT.kTRUE)
def gaussian_der(x,par):
    return (-1.)*x[0]/(ROOT.TMath.Power(par[0],2))*ROOT.TMath.Gaus(x[0],0,par[0],ROOT.kTRUE)

g = TFile("analysis.root","READ")
tester = TFile("testile.root","RECREATE")
g.cd("pedestal/Channels")
gr2=[]
g.cd("laser_17_23_01_k_100_w_30D400/Channels")
for pixel in range(20, 21):
    tmp = ROOT.gDirectory.Get(str(pixel).zfill(3))
    print ("%s\t%d" % (tmp.GetTitle(), tmp.GetNbinsX()))
    gr2.append(tmp)
data=TH1D("datahist","datahist",points1+1,-256.5,256.5)
data.Sumw2()
data.Add(gr2[0],1.)
#data = TH1D(gr2[0])
data.SetMarkerColor(1)
data.SetMarkerSize(.5)
data.SetLineColor(1)

data.Scale(1./data.Integral())
#kernel =  TH1F("gaussian_der", "Gaussian Derivative Kernel; TDAC (a.u.); frequency" ,20000, 0., 60000.)

x1    =ROOT.RooRealVar("TDAC","TDAC",-256.5,256.5,"a.u.")
#y    =ROOT.RooRealVar("y","y",0.5,256.5)
mean =ROOT.RooRealVar("mean","mean of gaussian",0)
sigma=ROOT.RooRealVar("sigma","width of gaussian",1,0.01,5)

gauss =ROOT.RooGaussian("gauss","gaussian PDF",x1,mean,sigma)
dgdx=gauss.derivative(x1,1) ;
kernel=gauss.createHistogram("TDAC",256*2)
#kernel1=dgdx.createHistogram("TDAC",points*2)
    
xframe = x1.frame(ROOT.RooFit.Title("d(Gauss)/dx"))
dgdx.plotOn(xframe,ROOT.RooFit.Precision(1e-6))

#kernel = TH1D(gaussian_der_f.GetHistogram())
c =  TCanvas("c1","Fits",10,10,1600,1200)
c.Divide(2,2)

arglist=ROOT.RooArgList(x1)
argset=ROOT.RooArgSet(x1)

arglist1=ROOT.RooArgList(x1)
argset1=ROOT.RooArgSet(x1)


RData =  ROOT.RooDataHist("RData", "Experimental Data", arglist1, data)
#RData.printMultiline(streams,1)
sigma.Print()
RKernel =  ROOT.RooDataHist("RKernel", " ", arglist1, kernel)

pdf_data =  ROOT.RooHistPdf("pdf_data", "pdf_data", argset1,  RData,0)
pdf_data.setInterpolationOrder(0)
pdf_kernel =  ROOT.RooHistPdf("pdf_kernel", "pdf_kernel", argset1, RKernel, 0)
pdf_kernel.setInterpolationOrder(0)
#abspdf1 = ROOT.RooAbsRealPdf(pdfh2)
#abspdf2 = ROOT.RooAbsRealPdf(pdfaccPulse)
#pdf_conv=ROOT.RooNumConvPdf("ExpTOF", "ExpTOF", x,pdfh2 ,pdfaccPulse)
x1.setBins(points,"cache")
pdf_conv=ROOT.RooFFTConvPdf("pdf_conv", "pdf_conv", x1, gauss,pdf_data,0)
pdf_conv.setInterpolationOrder(0)
#pdf_conv1=ROOT.RooFFTConvPdf("pdf_conv", "pdf_conv", x1, pdf_kernel,pdf_data,0)
x1.setBins(points,"cache")
derived_smooth   =pdf_conv.derivative(x1,1)
derived_no_smooth=pdf_data.derivative(x1,1)
test_histo=derived_smooth.createHistogram("TDAC",points)
print str(test_histo)
test_histo.Scale(-1./(points1*points/points1))

#derived_smooth_histo= derived_smooth.createHistogram("derived_smooth",25600)

#frame = x.frame(ROOT.RooFit.Bins(256))
#x1.setRange("Subrange",40,100)

frame = x1.frame(ROOT.RooFit.Bins(points1))
#frame1 = x1.frame(ROOT.RooFit.Bins(points*2))
frame1 = x1.frame(ROOT.RooFit.Bins(points))
#frame2 = x1.frame(ROOT.RooFit.Bins(256*2*5))
frame2 = x1.frame(ROOT.RooFit.Bins(points1))
#plot=ROOT.RooPlot(frame)
#frame1.GetXaxis.SetRange(40,100)
#pdf_kernel.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kMagenta))
#gauss.plotOn(frame,ROOT.RooFit.Precision(1e-6),ROOT.RooFit.LineColor(ROOT.kAzure))
pdf_data.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kBlack))
pdf_conv.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kRed))
#derived1.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kBlue))
RData.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kGreen))
gauss.plotOn(frame1,ROOT.RooFit.LineColor(ROOT.kBlue))
norm=1./(points*points/points1)
#derived_smooth.plotOn(frame2,ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.Normalization(25600,ROOT.RooAbsReal.NumEvent))
derived_smooth.plotOn(frame2,ROOT.RooFit.LineColor(ROOT.kGreen),ROOT.RooFit.Normalization(norm,ROOT.RooAbsReal.NumEvent))

#dgdx.plotOn(frame2,ROOT.RooFit.LineColor(ROOT.kGreen))
#derived_no_smooth.plotOn(frame2,ROOT.RooFit.LineColor(ROOT.kBlue))

c.cd(1)
frame.Draw()
frame.SetAxisRange(40,100,"X")
print "hratio is " + str(frame)
#xaxis.Print()

c.cd(2)
data.Draw()
c.cd(3)
frame1.Draw()
frame1.SetAxisRange(40,100,"X")
#kernel.Draw()

c.cd(4)
#frame2.Draw()
test_histo.Draw("p")
test_histo.SetMarkerStyle(20)
test_histo.GetXaxis().SetRangeUser(40,100)
c.Update()
c.SaveAs("test.pdf")
file= TFile("test.root","RECREATE")
kernel.Write()
data.Write()
c.Write("testW")

file.Close()
time.sleep(1)

#ROOT.gApplication.Run()
#ROOT.gApplication.Terminate(0)
exit(0)