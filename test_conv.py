#!/usr/bin/python
import numpy as np
import os.path
import sys
import ROOT
from ROOT import gROOT, TCanvas, TGraphAsymmErrors, TH1, TF1, TH1F, TH1D, TTree, TFile, TTreeReader, TTreeReaderValue, TTreeReaderArray, TH2I, TH2F, TString, THStack, TGraphErrors, TList, TListIter, TIter, TObject, TH1I, TMath, TDirectory, TEfficiency, TF1Convolution, RooFit, TRandom,TAxis, TSpectrum, TPolyMarker, TVirtualFFT
import array as array
import time

points = 2560*2
points1=int(256*2)

SQRT2=ROOT.TMath.Sqrt2()
subpixel_resolution=5
#Width of the central excitatory region 2*Sqrt(2)*Sigma filter constant

def match_predicator(x,n):
  for i in range(1,n-1):
    x[i]
  
  return matches


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
def signal_only(x,par):
    erf = par[0]*0.5*(1-ROOT.TMath.Erf((x[0]-par[1])/(par[2]*SQRT2)))
    gausx=par[4]*ROOT.TMath.Gaus(x[0],par[5],par[6],ROOT.kFALSE)
    if (gausx<=par[0] and par[5]<x[0]):
        return erf-gausx
    else:
        return 0
def signal_and_noise(x,par):
    erf = par[0]*0.5*(1-ROOT.TMath.Erf((x[0]-par[1])/(par[2]*SQRT2)))
    gausx=par[3]*ROOT.TMath.Gaus(x[0],par[4],par[5],ROOT.kFALSE)
    if (gausx<=par[0] and par[4]<x[0]):
        return erf+gausx
    #elif(par[4]<x[0]):
    elif (par[4]<x[0]):
        return gausx +erf
    else:
        return gausx

        ##return gausx
        #return 0
#def signal_and_noise(x,par):
    #gausat_x=par[4]*ROOT.TMath.Gaus(x[0],par[5],par[6],ROOT.kFALSE)
    #if gausat_x<=par[0]*0.9999999 and x[0]<par[1]:
        #return par[0]*(-0.5)*ROOT.TMath.Erf((x[0]-par[1])/(par[2]*SQRT2))+par[4]*ROOT.TMath.Gaus(x[0],par[5],par[6],ROOT.kFALSE)
    #else:
        #return par[0]*(-0.5)*ROOT.TMath.Erf((x[0]-par[1])/(par[2]*SQRT2))    

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
    return par[0]*ROOT.TMath.Gaus(x[0],par[1],par[2],ROOT.kFALSE)
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

g = TFile("test.root","READ")
g.cd("Signal")
#for pixel in range(13, 14):
    #tmp = ROOT.gDirectory.Get(str(pixel).zfill(3))
    #print ("%s\t%d" % (tmp.GetTitle(), tmp.GetNbinsX()))
    #gr2.append(tmp)
tmp = (TH1D)(ROOT.gDirectory.Get(str("020_resid")))
tmp.ClearUnderflowAndOverflow()
#data.Print("all")
#for i in range (0,tmp.GetNbinsX())
data=ROOT.TH1D("datahist","datahist",257,.5,257.5)
data.Sumw2()
data.ClearUnderflowAndOverflow()
data.Add(tmp,1)
data.SetMarkerColor(1)
data.SetMarkerStyle(20)
data.SetMarkerSize(1)
data.SetLineColor(1)
#data.Print("all")
#data.Scale(1./data.Integral())

filter_constant_sigma=1
excitatory_region_width=2*SQRT2*filter_constant_sigma
size_of_operator=3*excitatory_region_width
subpixel_resolution=1
bins_mask=(int)(round(size_of_operator/subpixel_resolution,1))
if(bins_mask%2==0):
    bins_mask=bins_mask+1
    size_of_operator=subpixel_resolution*bins_mask
else:
    size_of_operator=subpixel_resolution*bins_mask

filter_size    =ROOT.RooRealVar("x","TDAC",-.5*size_of_operator,.5*size_of_operator,"a.u.")
mean =ROOT.RooRealVar("mean","mean of gaussian",0)
sigma=ROOT.RooRealVar("sigma","width of gaussian",filter_constant_sigma)
gauss =ROOT.RooGaussian("gauss","gaussian PDF",filter_size,mean,sigma)
LoG_Mask   =gauss.derivative(filter_size,2)
#xframe = filter_size.frame(ROOT.RooFit.Title("LoG Mask"),ROOT.RooFit.Bins(3))
#x1frame = x1.frame(ROOT.RooFit.Title("LoG Mask"),ROOT.RooFit.Bins(257))
#gauss.plotOn(xframe,ROOT.RooFit.LineColor(ROOT.kBlue),ROOT.RooFit.Normalization(1))
#LoG_Mask.plotOn(xframe,ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.Normalization(1))
LoG_Mask_histo=LoG_Mask.createHistogram("x",bins_mask)
hm_n       = LoG_Mask_histo.GetNbinsX()
hm_data       = data.GetNbinsX()
Kernel = array.array( 'd', [0]*hm_n)
#Data   = array.array( 'd', [0]*hm_n)
Data= ROOT.std.vector('double')(hm_data)
Convolve=TH1D(data)
Convolve.Reset()

for i in range(1,hm_data+1):
    #print ("%d sumover" %i)
    summe=0
    for j in range(1,hm_n+1):
      if (i-j)>=0:
        summe+=data.GetBinContent(i-j)*LoG_Mask_histo.GetBinContent(j)
        if(i==60):
            print data.GetBinContent((i-j)%hm_data),LoG_Mask_histo.GetBinContent(j)
    print i, summe
    Convolve.SetBinContent(i,summe)
    

#for i in Data:
    #print "array" ,i



hm=TH1F(LoG_Mask_histo)
#LoG_Mask_histo.Print("all")
#hm = ROOT.TH1D()
ROOT.TVirtualFFT.SetTransform(0)
hm = LoG_Mask_histo.FFT(hm, "R2C MAG M")
hm.SetTitle("Magnitude of the 1st transform")

#hm_n       = LoG_Mask_histo.GetNbinsX()
hm_re_full = array.array( 'd', [0]*hm_n)
hm_im_full = array.array( 'd', [0]*hm_n)
fft = ROOT.TVirtualFFT.GetCurrentTransform()
fft.GetPointsComplex(hm_re_full,hm_im_full)
#for i in range(0,hm_n):
    #print hm_re_full[i], hm_im_full[i]

hm1_n       = data.GetNbinsX()
hm1_im_full = array.array( 'd', [0]*hm1_n)
hm1_re_full = array.array( 'd', [0]*hm1_n)

hm1=TH1D(data)
#hm = ROOT.TH1D()
ROOT.TVirtualFFT.SetTransform(0)
hm1 = data.FFT(hm1, "R2C Mag M")
fft1 = ROOT.TVirtualFFT.GetCurrentTransform()
fft1.GetPointsComplex(hm1_re_full,hm1_im_full)

#for i in range(0,hm1_n):
    #print hm1_re_full[i], hm1_im_full[i]
hm1.SetTitle("Magnitude of the 1st transform of data")
hm1_im_mult= array.array( 'd', [0]*hm_n)
hm1_re_mult= array.array( 'd', [0]*hm_n)

size_arr= array.array( 'i', [0])
size_arr[0]=hm_n


back_re_mult= array.array( 'd', [0]*hm_n)

mult=TH1F(LoG_Mask_histo)
mult.Reset()

for i in range(0,hm_n):
    hm1_re_mult[i]=hm1_re_full[(i+(1+hm1_n)/2)%hm1_n]*hm_re_full[i]-hm_im_full[i]*hm1_im_full[(i+(1+hm1_n)/2)%hm1_n]
    hm1_im_mult[i]=hm1_re_full[(i+(1+hm1_n)/2)%hm1_n]*hm_im_full[i]+hm1_im_full[(i+(1+hm1_n)/2)%hm1_n]*hm_re_full[i]
fft2= ROOT.TVirtualFFT.FFT(1, size_arr, "C2R")
fft2.SetPointsComplex(hm1_re_mult,hm1_im_mult)
fft2.Transform()

fft2.GetPoints(back_re_mult)
for i in range(0, len(back_re_mult)):
    #print back_re_mult[i]
    mult.SetBinContent(i,back_re_mult[i])


#LoG_Mask_histo.plotOn(xframe,ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.Normalization(1))


#LoG_Mask_histo.Draw()
#time.sleep(1)


#arglist=ROOT.RooArgList(x1)
#argset=ROOT.RooArgSet(x1)

#RData =  ROOT.RooDataHist("RData", "Experimental Data", arglist, data)
#RData.plotOn(x1frame,ROOT.RooFit.LineColor(ROOT.kBlack))

#LoG_Data =  ROOT.RooDataHist("LoG_Data", "LoG_Data", arglist, LoG_Mask_histo)
#LoG_Data.plotOn(x1frame,ROOT.RooFit.LineColor(ROOT.kGreen),ROOT.RooFit.Bins(bins_mask))

#pdf_data =  ROOT.RooHistPdf("pdf_data", "pdf_data", argset,  RData,0)
#pdf_data.setInterpolationOrder(0)
#pdf_data.plotOn(x1frame,ROOT.RooFit.LineColor(ROOT.kRed))



#x1.setBins(points,"cache")
#pdf_conv=ROOT.RooFFTConvPdf("pdf_conv", "pdf_conv", x1, LoG_Mask,pdf_data,0)
#pdf_conv.setInterpolationOrder(0)

#pdf_conv.plotOn(x1frame,ROOT.RooFit.LineColor(ROOT.kGreen))
c =  TCanvas("c1","Find Peak",10,10,1600,1200)
c.Divide(3,3)
c.cd(1)
ROOT.gPad.SetGrid()
LoG_Mask_histo.Draw()
c.cd(2)
hm.Draw();
c.cd(3)
data.Draw()
c.cd(4)
hm1.Draw()
c.cd(5)
mult.Draw()
c.cd(6)
Convolve.Draw()
#x1frame.Draw()
c.SaveAs("canvas.root")

##derived_no_smooth=pdf_data.derivative(x1,1)
#derivative_histo=derived_smooth.createHistogram("x",points)
#derivative_histo.Scale(-1./(points1*points/points1))
##derivative_histo.Scale(-4./(1000000))
#pdf_conv_histo=pdf_conv.createHistogram("x",points)
##pdf_conv_histo.Scale(2.)

#frame = x1.frame(ROOT.RooFit.Bins(points))
#frame1 = x1.frame(ROOT.RooFit.Bins(points))
#frame2 = x1.frame(ROOT.RooFit.Bins(points1))


##pdf_data.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kBlack),ROOT.RooFit.Normalization(data.Integral()*points/points1,ROOT.RooAbsReal.NumEvent))
##pdf_conv.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.Normalization(data.Integral()*points/points1,ROOT.RooAbsReal.NumEvent))
##derived1.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kBlue))
#RData.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kBlack))
##RData.statOn(frame,ROOT.RooFit.Layout(0.55,0.99,0.8))

#gauss.plotOn(frame1,ROOT.RooFit.LineColor(ROOT.kBlue))

#norm=1./(points*points/points1)
##derived_smooth.plotOn(frame2,ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.Normalization(25600,ROOT.RooAbsReal.NumEvent))
#derived_smooth.plotOn(frame2,ROOT.RooFit.LineColor(ROOT.kGreen),ROOT.RooFit.Normalization(norm,ROOT.RooAbsReal.NumEvent))
#derived_smooth.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kMagenta),ROOT.RooFit.Normalization((-.125)*norm,ROOT.RooAbsReal.NumEvent))

##print get_gpeaks(data,lrange=[40,100],sigma=1,opt="",thres=0.01,niter=2)
#peaks1=get_gpeaks(data)
#peaks2=[]
#if peaks1[0]>0:
    #interval =[peaks1[1][0][0]+1,100]
    #peaks2 = get_gpeaks(derivative_histo,interval,2,"",1e-5,5)
    #print peaks2[1][-1][0]

##simultaneous fit
##[peaks1[1][0][0]
#total=TF1('total',signal_fit, 0,256,7)
#total.SetNpx(points)
#total.SetLineColor(ROOT.kOrange)
#total_signal_only=TF1('total_signal_only',signal_only, 0,256,8)
#total_signal_only.SetNpx(points)
#total_signal_only.SetLineColor(ROOT.kGreen)
#total_signal_and_noise=TF1('signal_and_noise',signal_and_noise, 0,256,7)
#total_signal_and_noise.SetNpx(points)
#total_signal_and_noise.SetLineColor(ROOT.kAzure)
#total_noise=TF1('noise',gaussian, 0,256,3)
#total_noise.SetNpx(points)
#total_noise.SetLineColor(ROOT.kMagenta)
#G_Mean=peaks1[1][-1][0]
#C_Start=peaks1[1][-1][0]
#C_End=peaks2[1][-1][0]
#Height=peaks2[1][-1][1]*2
#Sigma=1.6
#Height_Noise=peaks1[1][-1][1]
#Mean_Noise=peaks1[1][-1][0]
#Sigm_Noise=1.5

#total.SetParameters(Height,C_End,Sigma,C_Start,Height_Noise,Mean_Noise,Sigm_Noise)
##for i,j in enumerate(pars):
    ##signal.SetParameter(i,j)
#bin_fwhm= data.FindLastBinAbove(Height/10*1.2)
#signal_low=data.GetXaxis().GetBinCenter(bin_fwhm)+total.GetParameter(2) 
#print "height",Height
#print "signal_low",signal_low

#data.Fit(total,"l+","", 0,256)
#data.GetXaxis().SetRangeUser(0,256)
#total_signal_only.SetParameters(Height/10,C_End,Sigma,C_Start,Height_Noise,Mean_Noise,Sigm_Noise,signal_low)
#total_signal_and_noise.SetParameters(Height/10,C_End,Sigma,Height_Noise,Mean_Noise,Sigm_Noise,signal_low)
#total_noise.SetParameters(Height_Noise,Mean_Noise,Sigm_Noise)
#data.Fit(total_signal_and_noise,"l","",0,256)
#data.GetListOfFunctions().Add(total_signal_only)
#data.GetListOfFunctions().Add(total_signal_and_noise)
#data.GetListOfFunctions().Add(total_noise)

##sig_norm  =ROOT.RooRealVar("sig_norm"   ,"Signal Normalization",Height/(ROOT.TMath.Pi()*2)**2)
#sig_norm  =ROOT.RooRealVar("sig_norm"   ,"Signal Normalization",Height,1E-6,1E6)
##sig_norm        =ROOT.RooRealVar("sig_norm"   ,"Signal Normalization",6E-3)
#sig_mean        =ROOT.RooRealVar("sig_mean"   ,"Signal Mean"         ,C_End,C_End-5,C_End+5)
#sig_only_start  =ROOT.RooRealVar("sig_only_start"   ,"Signal Mean"         ,50,40,60)
#sig_sigma =ROOT.RooRealVar("sig_sigma"  ,"Signal Sigma"        ,2.5,0.1,20)
#sig_sigma2 =ROOT.RooRealVar("sig_sigma2"  ,"Signal Sigma"        ,.2,0.1,20)
#ped_norm  =ROOT.RooRealVar("ped_norm" ,"Pedestal Normalization",Height_Noise,.1*Height_Noise,10*Height_Noise)
#ped_norm_der  =ROOT.RooRealVar("ped_norm_der" ,"Pedestal Normalization Der",1E-4,0,.5)
##ped_norm  =ROOT.RooRealVar("ped_norm" ,"Pedestal Normalization",Height_Noise,Height/2.,1)
#ped_mean  =ROOT.RooRealVar("ped_mean" ,"Pedestal Mean"         ,C_Start,C_Start-5,C_Start+5)
##ped_mean  =ROOT.RooRealVar("ped_mean" ,"Pedestal Mean"         ,C_Start)
#ped_sigma =ROOT.RooRealVar("ped_sigma","Pedestal Sigma",2,0.5,20)
#ped_skew =ROOT.RooRealVar("ped_skew","Pedestal Skew",.5,-1,1)
##ped_skew =ROOT.RooRealVar("ped_skew","Pedestal Skew",-.08)
##ped_alpha =ROOT.RooRealVar("ped_alpha","Pedestal Alpha"        ,-10,-20,0)
##ped_n =ROOT.RooRealVar("ped_n","Pedestal N"        ,1,0.01,10)


#x1.setRange("R1",C_Start-5,C_Start+5)
##x1.setRange("R2",C_End-10,C_End+10)
#ped_dist      =ROOT.RooGaussian("ped_dist","Pedestal",x1,ped_mean,ped_sigma)
#ped_dist1      =ROOT.RooGaussian("ped_dist1","Pedestal",x1,ped_mean,ped_sigma)

##ped_dist      =ROOT.RooCBShape("ped_dist","Pedestal",x1,ped_mean,ped_sigma,ped_alpha,ped_n)
##signal_dist   =ROOT.RooGenericPdf("signal_dist",
                                  ##"signal_dist",
                                  ##"0.5*(TMath::Erf((x-ped_mean)/(sig_sigma*TMath::Sqrt2()))-TMath::Erf((x-sig_mean)/(sig_sigma*TMath::Sqrt2())))",
                             ##ROOT.RooArgList(x1,ped_mean,sig_sigma,sig_mean))
#signal_dist   =ROOT.RooGenericPdf("signal_dist",
                                  #"signal_dist",
                                  #"0.5*(TMath::Erf((x-ped_mean)/(sig_sigma2*TMath::Sqrt2()))-TMath::Erf((x-sig_mean)/(sig_sigma*TMath::Sqrt2())))",
                             #ROOT.RooArgList(x1,ped_mean,sig_sigma2,sig_mean,sig_sigma))
#ped_dist_ext     =ROOT.RooExtendPdf("ped_dist_ext","ped_dist_ext",ped_dist,ped_norm)
#ped_dist_ext1     =ROOT.RooExtendPdf("ped_dist_ext1","ped_dist_ext1",ped_dist1,ped_norm)
#signal_dist_ext  =ROOT.RooExtendPdf("signal_dist_ext","signal_dist_ext",signal_dist,sig_norm)
##total_dist    =ROOT.RooAddPdf("model","ped_dist+sig_dist",ROOT.RooArgList(ped_dist,signal_dist),ROOT.RooArgList(ped_norm,sig_norm))
#total_dist    =ROOT.RooAddPdf("model","ped_dist+sig_dist",ROOT.RooArgList(ped_dist_ext,signal_dist_ext))
##ped_dist_special    =ROOT.RooGenericPdf("ped_dist_special",
                                        ##"ped_dist_special",
                                        ##"ped_skew/2.*TMath::Exp(ped_skew/2.*(2.*ped_mean*ped_skew*ped_sigma**2-2.*x))*TMath::Erfc((ped_mean+ped_skew*ped_sigma**2-x)/(TMath::Sqrt2()*ped_sigma))",
                                        ##ROOT.RooArgList(x1,ped_skew,ped_mean,ped_sigma))
#ped_dist_special    =ROOT.RooGenericPdf("ped_dist_special",
                                        #"ped_dist_special",
                                        #"TMath::Gaus(x, ped_mean, ped_sigma,1)*(1+TMath::Erf(ped_skew*(x-ped_mean)/(TMath::Sqrt2()*ped_sigma)))",
                                        #ROOT.RooArgList(x1,ped_mean,ped_sigma,ped_skew))
##result = ROOT.RooFitResult(total_dist.fitTo(RData,ROOT.RooFit.Extended(1),ROOT.RooFit.Save(),ROOT.RooFit.SumW2Error(ROOT.kTRUE),
##ROOT.RooFit.Range("R2")))
#result = ROOT.RooFitResult(total_dist.fitTo(RData,ROOT.RooFit.Extended(1),ROOT.RooFit.Save(),ROOT.RooFit.SumW2Error(ROOT.kTRUE)))
#result1 = ROOT.RooFitResult(ped_dist_special.fitTo(RData,ROOT.RooFit.Save(),ROOT.RooFit.SumW2Error(ROOT.kTRUE),ROOT.RooFit.Range("R1")))
#result2 = ROOT.RooFitResult(ped_dist_ext.fitTo(RData,ROOT.RooFit.Save(),ROOT.RooFit.SumW2Error(ROOT.kTRUE),ROOT.RooFit.Range("R1")))
##corr_hist= result.correlationHist("matrix")
##result.Print("v")

##total_dist.plotOn(frame,ROOT.RooFit.Components("ped_dist_ext"),ROOT.RooFit.LineColor(ROOT.kGreen))
##total_dist.plotOn(frame,ROOT.RooFit.Components("signal_dist_ext"),ROOT.RooFit.LineColor(ROOT.kRed))
##total_dist.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kBlue))
##total_dist.paramOn(frame, ROOT.RooFit.Format("NELU", ROOT.RooFit.AutoPrecision(3)), ROOT.RooFit.Layout(0.6, 0.9,0.9))
#ped_dist_ext.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kRed))
#ped_dist_special.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kOrange))
#ped_dist_special.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kOrange),ROOT.RooFit.Range("Full"),ROOT.RooFit.LineStyle(ROOT.kDashed))
#ped_dist_ext.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.Range("Full"),ROOT.RooFit.LineStyle(ROOT.kDashed))
#ped_dist_special.paramOn(frame, ROOT.RooFit.Format("NELU", ROOT.RooFit.AutoPrecision(3)), ROOT.RooFit.Layout(0.6, 0.9,0.9))

#RData.Print("all")
##print "chisquare\t",frame.chiSquare("model_Norm","RData",0)
#frame.Print("all")
##chiquadrat und residuen
##chi2 =ROOT.RooChi2Var("chi2","chi2",total_dist,RData,ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
##hresid = ROOT.RooHist(frame.residHist())
#print "find obj"
##frame.findObject("model_Norm[x]")
##hresid = ROOT.RooHist(frame.residHist("h_RData","model_Norm[x]",ROOT.kTRUE))
#hresid = ROOT.RooHist(frame.residHist("h_RData","ped_dist_special_Norm[x]_Range[Full]_NormRange[Full]",ROOT.kFALSE))
#hresid1 = ROOT.RooHist(frame.residHist("h_RData","ped_dist_ext_Norm[x]_Range[Full]_NormRange[Full]",ROOT.kFALSE))
#hresid.SetLineColor(ROOT.kOrange)
#hresid.SetMarkerColor(ROOT.kOrange)
#hresid1.SetLineColor(ROOT.kRed)
#hresid1.SetMarkerColor(ROOT.kRed)

##hpull = ROOT.RooHist(frame.pullHist())
#frame_res = x1.frame(ROOT.RooFit.Bins(points))
#frame_pull = x1.frame(ROOT.RooFit.Bins(points))
##frame_res = x1.frame()
##frame_pull = x1.frame()
#frame_res.addPlotable(hresid,"PL")
#frame_res.addPlotable(hresid1,"PL")
##frame_pull.addPlotable(hpull,"P")

#frame.SetAxisRange(40,100,"X")
#frame.SetMinimum(1E-8)
#frame1.SetAxisRange(-5,5,"X")
#frame2.SetAxisRange(40,100,"X")
#frame_res.SetAxisRange(40,100,"X")
##frame_pull.SetAxisRange(40,100,"X")


#c.cd(1)
#frame.Draw()
#c.cd(2)
#data.Draw()
#total.Draw("same")
#c.cd(3)
##frame1.Draw()
#frame_res.Draw()
#c.cd(4)
##frame2.Draw()
#derivative_histo.Draw("p")
#derivative_histo.SetMarkerStyle(20)
#derivative_histo.GetXaxis().SetRangeUser(40,100)
#pdf_conv_histo.Draw("psame")
#pdf_conv_histo.SetMarkerStyle(22)
#c.Update()
#file= TFile("test.root","RECREATE")
#data.Write("data")
#derivative_histo.Write("smoothed_derivative")
#c.Write("overview")
#c2 = TCanvas("c2","c2",10,10,500,500)
#c2.Divide(1,2)
#c2.cd(1)
#ROOT.gPad.SetGrid(1)
#ROOT.gPad.SetLogy()
#frame.Draw()
#c2.cd(2)
#ROOT.gPad.SetGrid(1)
#frame_res.Draw()
##hresid.Write("reisdu")
##hresid_hist.Write("reisdu")
##c2.cd(2)
##frame_pull.Draw()
##corr_hist.Draw("colz")
##frame_res.Draw()
##c2.cd(3)
##frame_pull.Draw()
#c2.Write("frame")
##c2.Write("frame_res")
##c2.Clear()
##c2.Clear()
##derivative_histo.Draw("p")
##derivative_histo.SetMarkerStyle(20)
##derivative_histo.GetXaxis().SetRangeUser(40,100)
##c2.Write("frame1")
#c2.Close()

g.Close()


#ROOT.gApplication.Run()
#ROOT.gApplication.Terminate(0)
exit(0)