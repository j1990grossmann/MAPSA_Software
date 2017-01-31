#!/usr/bin/python
import numpy as np
import os.path
import sys
import ROOT
from ROOT import gROOT, TCanvas, TGraphAsymmErrors, TH1, TF1, TH1F, TH1D, TTree, TFile, TTreeReader, TTreeReaderValue, TTreeReaderArray, TH2I, TH2F, TString, THStack, TGraphErrors, TList, TListIter, TIter, TObject, TH1I, TMath, TDirectory, TEfficiency, TF1Convolution, RooFit, TRandom,TAxis, TSpectrum, TPolyMarker
import array as array
import time

points = 2560*2
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

def get_gpeaks(h,lrange=[0,100],sigma=1,opt="",thres=0.01,niter=10):
    s = TSpectrum(niter,3)
    h.GetXaxis().SetRangeUser(lrange[0],lrange[1])
    npeaks=s.Search(h,sigma,opt,thres)
    bufX, bufY = s.GetPositionX(), s.GetPositionY()
    pos = []
    for i in range(s.GetNPeaks()):
        pos.append([bufX[i], bufY[i]])
    print pos
    pos.sort()
    return npeaks,pos


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
data.SetMarkerColor(1)
data.SetMarkerStyle(20)
data.SetMarkerSize(1)
data.SetLineColor(1)
#data.Scale(1./data.Integral())

x1    =ROOT.RooRealVar("x","TDAC",-256.5,256.5,"a.u.")
mean =ROOT.RooRealVar("mean","mean of gaussian",0)
sigma=ROOT.RooRealVar("sigma","width of gaussian",1,0.01,5)

gauss =ROOT.RooGaussian("gauss","gaussian PDF",x1,mean,sigma)
kernel=gauss.createHistogram("x",256*2)

xframe = x1.frame(ROOT.RooFit.Title("d(Gauss)/dx"))

c =  TCanvas("c1","Find Peak",10,10,1600,1200)
c.Divide(2,2)

arglist=ROOT.RooArgList(x1)
argset=ROOT.RooArgSet(x1)

RData =  ROOT.RooDataHist("RData", "Experimental Data", arglist, data)
RKernel =  ROOT.RooDataHist("RKernel", " ", arglist, kernel)

pdf_data =  ROOT.RooHistPdf("pdf_data", "pdf_data", argset,  RData,0)
pdf_data.setInterpolationOrder(0)
pdf_kernel =  ROOT.RooHistPdf("pdf_kernel", "pdf_kernel", argset, RKernel, 0)
pdf_kernel.setInterpolationOrder(0)

x1.setBins(points,"cache")
pdf_conv=ROOT.RooFFTConvPdf("pdf_conv", "pdf_conv", x1, gauss,pdf_data,0)
pdf_conv.setInterpolationOrder(0)

derived_smooth   =pdf_conv.derivative(x1,1)
#derived_no_smooth=pdf_data.derivative(x1,1)
derivative_histo=derived_smooth.createHistogram("x",points)
derivative_histo.Scale(-1./(points1*points/points1))

frame = x1.frame(ROOT.RooFit.Bins(points))
frame1 = x1.frame(ROOT.RooFit.Bins(points))
frame2 = x1.frame(ROOT.RooFit.Bins(points1))


#pdf_data.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kBlack),ROOT.RooFit.Normalization(data.Integral()*points/points1,ROOT.RooAbsReal.NumEvent))
#pdf_conv.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.Normalization(data.Integral()*points/points1,ROOT.RooAbsReal.NumEvent))
#derived1.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kBlue))
RData.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kBlack))
#RData.statOn(frame,ROOT.RooFit.Layout(0.55,0.99,0.8))

gauss.plotOn(frame1,ROOT.RooFit.LineColor(ROOT.kBlue))

norm=1./(points*points/points1)
#derived_smooth.plotOn(frame2,ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.Normalization(25600,ROOT.RooAbsReal.NumEvent))
derived_smooth.plotOn(frame2,ROOT.RooFit.LineColor(ROOT.kGreen),ROOT.RooFit.Normalization(norm,ROOT.RooAbsReal.NumEvent))

#print get_gpeaks(data,lrange=[40,100],sigma=1,opt="",thres=0.01,niter=2)
peaks1=get_gpeaks(data)
peaks2=[]
if peaks1[0]>0:
    interval =[peaks1[1][0][0]+2,100]
    peaks2 = get_gpeaks(derivative_histo,interval,4,"",1e-5,5)
    print peaks2[1][-1][0]

#simultaneous fit
#[peaks1[1][0][0]
total=TF1('total',signal_fit, 0,256,7)
total.SetNpx(points)
total.SetLineColor(ROOT.kOrange)
G_Mean=peaks1[1][-1][0]
C_Start=peaks1[1][-1][0]
C_End=peaks2[1][-1][0]
Height=peaks2[1][-1][1]*2
Sigma=1
Height_Noise=peaks1[1][-1][1]
Mean_Noise=peaks1[1][-1][0]
Sigm_Noise=3

total.SetParameters(Height,C_End,Sigma,C_Start,Height_Noise,Mean_Noise,Sigm_Noise)
#for i,j in enumerate(pars):
    #signal.SetParameter(i,j)
data.Fit(total,"l+","", 0,256)

#sig_norm  =ROOT.RooRealVar("sig_norm"   ,"Signal Normalization",Height/(ROOT.TMath.Pi()*2)**2)
sig_norm  =ROOT.RooRealVar("sig_norm"   ,"Signal Normalization",Height/2.,1E-5,1E-2)
sig_mean  =ROOT.RooRealVar("sig_mean"   ,"Signal Mean"         ,C_End,C_End-5,C_End+5)
sig_sigma =ROOT.RooRealVar("sig_sigma"  ,"Signal Sigma"        ,2.5,0.5,20)
ped_norm  =ROOT.RooRealVar("ped_norm" ,"Pedestal Normalization",Height_Noise,.8*Height_Noise,1.1*Height_Noise)
#ped_norm  =ROOT.RooRealVar("ped_norm" ,"Pedestal Normalization",Height_Noise,Height/2.,1)
ped_mean  =ROOT.RooRealVar("ped_mean" ,"Pedestal Mean"         ,C_Start,C_Start-5,C_Start+5)
#ped_mean  =ROOT.RooRealVar("ped_mean" ,"Pedestal Mean"         ,C_Start)
ped_sigma =ROOT.RooRealVar("ped_sigma","Pedestal Sigma",2,0.5,20)
#ped_alpha =ROOT.RooRealVar("ped_alpha","Pedestal Alpha"        ,-10,-20,0)
#ped_n =ROOT.RooRealVar("ped_n","Pedestal N"        ,1,0.01,10)


#x1.setRange("R1",0,C_Start)
#x1.setRange("R2",C_End-10,C_End+10)
#coeff     =ROOT.RooRealVar("coeff","Coefficient"        ,)
#RooCBShape CBShape("CBShape", "Cystal Ball Function", x, m, s, a, n); 
ped_dist      =ROOT.RooGaussian("ped_dist","Pedestal",x1,ped_mean,ped_sigma)
#ped_dist      =ROOT.RooCBShape("ped_dist","Pedestal",x1,ped_mean,ped_sigma,ped_alpha,ped_n)
#signal_dist   =ROOT.RooFormulaVar("signal_dist",
                             #"0.5*(TMath::Erf((x-sig_mean)/(sig_sigma*TMath::Sqrt2()))-TMath::Erf((x-ped_mean)/(sig_sigma*TMath::Sqrt2())))",
                             #ROOT.RooArgList(x1,ped_mean,sig_sigma,sig_mean))
signal_dist   =ROOT.RooGenericPdf("signal_dist",
                                  "signal_dist",
                                  "0.5*(TMath::Erf((x-ped_mean)/(sig_sigma*TMath::Sqrt2()))-TMath::Erf((x-sig_mean)/(sig_sigma*TMath::Sqrt2())))",
                             ROOT.RooArgList(x1,ped_mean,sig_sigma,sig_mean))
ped_dist_ext     =ROOT.RooExtendPdf("ped_dist_ext","ped_dist_ext",ped_dist,ped_norm)
signal_dist_ext  =ROOT.RooExtendPdf("signal_dist_ext","signal_dist_ext",signal_dist,sig_norm)
#overlap          =ROOT.RooProdPdf("overlap","overlap",ped_dist_ext,signal_dist_ext)
#total_dist    =ROOT.RooAddPdf("model","ped_dist+sig_dist",ROOT.RooArgList(ped_dist,signal_dist),ROOT.RooArgList(ped_norm,sig_norm))
total_dist    =ROOT.RooAddPdf("model","ped_dist+sig_dist",ROOT.RooArgList(ped_dist_ext,signal_dist_ext))

#result = ROOT.RooFitResult(total_dist.fitTo(RData,ROOT.RooFit.Extended(1),ROOT.RooFit.Save(),ROOT.RooFit.SumW2Error(ROOT.kTRUE),
#ROOT.RooFit.Range("R2")))
result = ROOT.RooFitResult(total_dist.fitTo(RData,ROOT.RooFit.Extended(1),ROOT.RooFit.Save(),ROOT.RooFit.SumW2Error(ROOT.kTRUE)))
#corr_hist= result.correlationHist("matrix")
#result.Print("v")

total_dist.plotOn(frame,ROOT.RooFit.Components("ped_dist_ext"),ROOT.RooFit.LineColor(ROOT.kGreen))
total_dist.plotOn(frame,ROOT.RooFit.Components("signal_dist_ext"),ROOT.RooFit.LineColor(ROOT.kRed))
#total_dist.plotOn(frame,ROOT.RooFit.Components("overlap"),ROOT.RooFit.LineColor(ROOT.kAzure))
total_dist.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kBlue))
total_dist.paramOn(frame, ROOT.RooFit.Format("NELU", ROOT.RooFit.AutoPrecision(3)), ROOT.RooFit.Layout(0.6, 0.9,0.9))
RData.Print("all")
#print "chisquare\t",frame.chiSquare("model_Norm","RData",0)
frame.Print("all")
#frame.chiSquare()
#chiquadrat und residuen
#chi2 =ROOT.RooChi2Var("chi2","chi2",total_dist,RData,ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
#hresid = ROOT.RooHist(frame.residHist())
print "find obj"
frame.findObject("model_Norm[x]")
hresid = ROOT.RooHist(frame.residHist("h_RData","model_Norm[x]",ROOT.kTRUE))
#test = basic_ostream()
#test = sys.stdout()
#print test
#hresid.Print("all")
hpull = ROOT.RooHist(frame.pullHist())
frame_res = x1.frame(ROOT.RooFit.Bins(points))
frame_pull = x1.frame(ROOT.RooFit.Bins(points))
#frame_res = x1.frame()
#frame_pull = x1.frame()
frame_res.addPlotable(hresid,"P")
frame_pull.addPlotable(hpull,"P")

frame.SetAxisRange(40,100,"X")
frame.SetMinimum(1E-8)
frame1.SetAxisRange(-5,5,"X")
frame2.SetAxisRange(40,100,"X")
frame_res.SetAxisRange(40,100,"X")
#frame_pull.SetAxisRange(40,100,"X")


c.cd(1)
frame.Draw()
c.cd(2)
data.Draw()
total.Draw("same")
c.cd(3)
#frame1.Draw()
#frame_res.Draw()
c.cd(4)
#frame2.Draw()
derivative_histo.Draw("p")
derivative_histo.SetMarkerStyle(20)
derivative_histo.GetXaxis().SetRangeUser(40,100)
c.Update()
c.SaveAs("overview.pdf")
file= TFile("test.root","RECREATE")
data.Write("data")
derivative_histo.Write("smoothed_derivative")
c.Write("overview")
c2 = TCanvas("c2","c2",10,10,500,500)
c2.Divide(1,2)
c2.cd(1)
ROOT.gPad.SetGrid(1)
ROOT.gPad.SetLogy()
frame.Draw()
c2.cd(2)
ROOT.gPad.SetGrid(1)
frame_res.Draw()
#c2.cd(2)
#frame_pull.Draw()
#corr_hist.Draw("colz")
#frame_res.Draw()
#c2.cd(3)
#frame_pull.Draw()
c2.Write("frame")
#c2.Write("frame_res")
#c2.Clear()
#c2.Clear()
#derivative_histo.Draw("p")
#derivative_histo.SetMarkerStyle(20)
#derivative_histo.GetXaxis().SetRangeUser(40,100)
#c2.Write("frame1")
c2.Close()

file.Close()
time.sleep(1)

#ROOT.gApplication.Run()
#ROOT.gApplication.Terminate(0)
exit(0)