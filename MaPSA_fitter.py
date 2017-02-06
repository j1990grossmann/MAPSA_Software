#!/usr/bin/python
import numpy as np
import os.path
import sys
import ROOT
from ROOT import gROOT, TCanvas, TGraphAsymmErrors, TH1, TF1, TH1F, TH1D, TTree, TFile, TTreeReader, TTreeReaderValue, TTreeReaderArray, TH2I, TH2F, TString, THStack, TGraphErrors, TList, TListIter, TIter, TObject, TH1I, TMath, TDirectory, TEfficiency, TF1Convolution, RooFit, TRandom,TAxis, TSpectrum, TPolyMarker
import array as array
import time

class MaPSA_fitter:
    def __init__(self):
        self._gaussian_f1 = TF1('gauss_f1','[0]*TMath::Gaus(x,[1],[2],1)',0,256,3)
        self._gaussian_f1.SetNpx(2560)
        self._gaussian_f1.SetTitle("Gaussian")
        self._gaussian_f1.SetMarkerColor(ROOT.kRed)
        self._gaussian_f1.SetLineColor(ROOT.kRed)
        self._gaussian_f1_extended=TF1('gauss_f1_ext',
                                       #'[0]*TMath::Gaus(x,[1],[2],0)',
                                       '[0]*TMath::Gaus(x,[1],[2],1)*(1-[3]*1/[2]**4*(x-[1]-[2])*(x-[1]+[2]))',
                                       0,256,4)
        self._gaussian_f1_extended.SetTitle("Extended_Gaussian")
        self._gaussian_f1_extended.SetNpx(2560)
        self._gaussian_f1_extended.SetMarkerColor(ROOT.kGreen)
        self._gaussian_f1_extended.SetLineColor(ROOT.kGreen)

        self._erf_f1 = TF1('Erf_f1','[0]*.5*(1+TMath::Erf(([1]-x)/[2]))',0,256,3)
        self._erf_f1.SetNpx(2560)
        self._erf_f1.SetTitle("Erf")
        self._erf_f1.SetMarkerColor(ROOT.kOrange)
        self._erf_f1.SetLineColor(ROOT.kOrange)

        self._s=ROOT.TSpectrum(10,3)
        self._threshold=1
        self._initial_expt_signal=0.0025

        self._run_no=ROOT.std.string()

        self._Noise_Norm =0
        self._Noise_Mean =0
        self._Noise_Sigma=0
        self._Noise_Chisqrndf=0
        self._Noise_Fit_Error=0
        self._Found_Signal=0
        self._Signal_Norm =0
        self._Signal_Mean =0
        self._Signal_Sigma=0
        self._Signal_Chisqrndf=0
        self._Signal_Fit_Error=0
        self._Err_Noise_Norm =0
        self._Err_Noise_Mean =0
        self._Err_Noise_Sigma=0
        self._Err_Signal_Norm =0
        self._Err_Signal_Mean =0
        self._Err_Signal_Sigma=0
        self._Channel_No=0

        self._Result_Dict=[]
        self._build_dict()
        self._tree = TTree( 'datatree', 'datatree' )
        self._treevars={}
        self._initialize_ttree()
    def Print_Result_Dict(self):
        for k, v in self._Result_Dict:
            print k, v
    def Return_Result_Dict(self):
        return self._Result_Dict
    def Find_signal_in_res(self,h,h1,minimum):
        upper_lim=h.GetBinCenter(h.GetNbinsX())
        h.SetAxisRange(minimum,upper_lim,"X")
        maximum = h.GetMaximum()
        maximum_x = h.GetBinCenter(h.GetMaximumBin())
        tmpbin = h.FindLastBinAbove(h.GetMaximum()/2)
        bin1 = tmpbin if (tmpbin>0) else 0
        half_max = h.GetBinCenter(bin1)
        bin2 = h.FindLastBinAbove(h.GetMaximum()/4)
        q_max = h.GetBinCenter(bin2)
        sigma=abs(q_max-half_max)*2
        tmp_range=[maximum_x+self._threshold,upper_lim]
        if(half_max-maximum_x-self._threshold>0):
            print "Signal peak found"
            self._Found_Signal=1
            tmp=self._fit_erf(h1,tmp_range,self._initial_expt_signal,half_max,sigma)
            self._Signal_Norm     =tmp[0]
            self._Signal_Mean     =tmp[1]
            self._Signal_Sigma    =tmp[2]
            self._Err_Signal_Norm     =tmp[3]
            self._Err_Signal_Mean     =tmp[4]
            self._Err_Signal_Sigma    =tmp[5]
            self._Signal_Chisqrndf=tmp[6]
            self._Signal_Fit_Error=tmp[7]
    def Find_signal(self,h,channel,initial_expt_signal=0.0025,threshold=1):
        self._reset()
        self._initial_expt_signal=initial_expt_signal
        self._threshold=threshold
        self._Channel_No=channel
        fwhm=10
        bin1 = h.FindFirstBinAbove(h.GetMaximum()/fwhm)
        bin2 = h.FindLastBinAbove(h.GetMaximum()/fwhm)
        tmp_norm=h.GetMaximum()/2
        tmp_mean=h.GetBinCenter(h.GetMaximumBin())
        tmp_sigma=2.3548*(bin2-bin1)
        tmp_range=[h.GetBinCenter(bin1)-.5,h.GetBinCenter(bin2)+.5]
        results=self._fit_gauss(h,tmp_range,tmp_norm,tmp_mean,tmp_sigma)
        self._Noise_Norm =results[0]
        self._Noise_Mean =results[1]
        self._Noise_Sigma=results[2]
        self._Err_Noise_Norm =results[3]
        self._Err_Noise_Mean =results[4]
        self._Err_Noise_Sigma=results[5]
        self._Noise_Chisqrndf=results[6]
        self._Noise_Fit_Error=results[7]
        if results[7]==0:
            #self._Noise_Chisqrndf=results[6]
            resid_hist=self._residual_hist(h,self._gaussian_f1,1)
            resid_hist1=self._residual_hist(h,self._gaussian_f1,0)
            #resid_hist=self._residual_hist(h,self._gaussian_f1_extended,1)
            self.Find_signal_in_res(resid_hist,resid_hist1,self._Err_Noise_Mean+self._Err_Noise_Sigma)
            if self._Found_Signal>0:
                self.Write_signal(resid_hist1,resid_hist,self._gaussian_f1,self._erf_f1,channel)
        self._build_dict()
        self._fill_tree()
    def Set_run_no(self,run_no):
        self._run_no.replace(0, ROOT.std.string.npos, str(run_no))
    def Make_dirs(self):
        #print ROOT.gDirectory.GetPathStatic()
        ROOT.gDirectory.mkdir("Signal")
    def Write_signal(self,resid, resid_norm, gaussian_tf1,erf_tf1,channel):
        ROOT.gDirectory.cd("Signal")
        pixel=str(channel).zfill(3)
        resid.Write(pixel+"_resid")
        resid_norm.Write(pixel+"_resid_norm")
        gaussian_tf1.Write(pixel+"_resid_gaussian_tf1")
        tmperf=erf_tf1.Clone()
        tmperf.Write(pixel+"_resid_erf_tf1")
        ROOT.gDirectory.cd("..")
    def Write_tree(self):
        self._tree.Write('tree',ROOT.TObject.kOverwrite)
    def _initialize_ttree(self):
        for k, v in self._Result_Dict:
            self._treevars[k] = array.array('f',[0])
        for key in self._treevars.keys():
            self._tree.Branch(key,self._treevars[key],key+"[1]/f")
        self._tree.Branch('FILENAME',self._run_no)
    def _reset(self):
        self._Noise_Norm =0
        self._Noise_Mean =0
        self._Noise_Sigma=0
        self._Noise_Chisqrndf=0
        self._Noise_Fit_Error=0
        self._Found_Signal=0
        self._Signal_Norm =0
        self._Signal_Mean =0
        self._Signal_Sigma=0
        self._Signal_Chisqrndf=0
        self._Signal_Fit_Error=0
        self._Err_Noise_Norm =0
        self._Err_Noise_Mean =0
        self._Err_Noise_Sigma=0
        self._Err_Signal_Norm =0
        self._Err_Signal_Mean =0
        self._Err_Signal_Sigma=0
        self._Channel_No=0
    def _build_dict(self):
        _Keys= [
            'Noise_Norm',       
            'Noise_Mean',       
            'Noise_Sigma',      
            'Noise_Chisqrndf',  
            'Noise_Fit_Error',  
            'Err_Noise_Norm',   
            'Err_Noise_Mean',   
            'Err_Noise_Sigma',  
            'Signal_Norm',      
            'Signal_Mean',      
            'Signal_Sigma',     
            'Signal_Chisqrndf', 
            'Signal_Fit_Error', 
            'Err_Signal_Norm',  
            'Err_Signal_Mean',  
            'Err_Signal_Sigma', 
            'Found_Signal',
            'Channel_No'
            ]
        _Values=[
            self._Noise_Norm,
            self._Noise_Mean,
            self._Noise_Sigma,
            self._Noise_Chisqrndf,
            self._Noise_Fit_Error,
            self._Err_Noise_Norm,
            self._Err_Noise_Mean,
            self._Err_Noise_Sigma,
            self._Signal_Norm,
            self._Signal_Mean,
            self._Signal_Sigma,
            self._Signal_Chisqrndf,
            self._Signal_Fit_Error,
            self._Err_Signal_Norm,
            self._Err_Signal_Mean,
            self._Err_Signal_Sigma,
            self._Found_Signal,
            self._Channel_No
        ]
        self._Result_Dict=zip(_Keys,_Values)
    def _fill_tree(self):
        for k, v in self._Result_Dict:
            self._treevars[k][0] = v
        self._tree.Fill()
    def _get_peaks(self,h,lrange=[0,100],sigma=1,opt="goff",thres=0.01,niter=10):
        self._s.SetDeconIterations(niter)
        h.GetXaxis().SetRangeUser(lrange[0],lrange[1])
        npeaks=self._s.Search(h,sigma,opt,thres)
        bufX, bufY =self._s.GetPositionX(),self._s.GetPositionY()
        pos = []
        for i in range(self._s.GetNPeaks()):
            pos.append([bufX[i], bufY[i]])
            print pos
        pos.sort()
        return npeaks,pos
    def _fit_gauss(self,h,lrange=[0,100],norm=1,mean=1,sigma=1):
        self._gaussian_f1.SetParameters(norm,mean,sigma)
        #self._gaussian_f1_extended.SetParameters(norm,mean,sigma)
        self._gaussian_f1.SetRange(lrange[0],lrange[1])
        #self._gaussian_f1_extended.SetRange(lrange[0],lrange[1])
        #fit_ptr=h.Fit(self._gaussian_f1,'rWL0q+','',lrange[0],lrange[1])
        fit_ptr=h.Fit(self._gaussian_f1,'r0q','',lrange[0],lrange[1])
        fit_error=ROOT.gMinuit.GetStatus()
        #h.Fit(self._gaussian_f1_extended,'r0q','',lrange[0],lrange[1])
        norm = self._gaussian_f1.GetParameter(0)
        mean = self._gaussian_f1.GetParameter(1)
        sigma= self._gaussian_f1.GetParameter(2)
        err_norm = self._gaussian_f1.GetParError(0)
        err_mean = self._gaussian_f1.GetParError(1)
        err_sigma= self._gaussian_f1.GetParError(2)
        chisquare_ndf=0
        if(self._erf_f1.GetChisquare()>0 and self._erf_f1.GetNDF()>0):
            chisquare_ndf=self._erf_f1.GetChisquare()/self._erf_f1.GetNDF()
        return norm,mean,sigma,err_norm,err_mean,err_sigma,chisquare_ndf,fit_error

    def _fit_erf(self,h,lrange=[0,100],norm=1,mean=1,sigma=1):
        self._erf_f1.SetParameters(norm,mean,sigma)
        self._erf_f1.SetRange(lrange[0],lrange[1])
        #h.Fit(self._erf_f1,'rWL0q+','',lrange[0],lrange[1])
        h.Fit(self._erf_f1,'r0q+','',lrange[0],lrange[1])
        fit_error=ROOT.gMinuit.GetStatus()
        norm = self._erf_f1.GetParameter(0)
        mean = self._erf_f1.GetParameter(1)
        sigma= self._erf_f1.GetParameter(2)
        err_norm = self._erf_f1.GetParError(0)
        err_mean = self._erf_f1.GetParError(1)
        err_sigma= self._erf_f1.GetParError(2)
        chisquare_ndf=0
        if(self._erf_f1.GetChisquare()>0 and self._erf_f1.GetNDF()>0):
            chisquare_ndf=self._erf_f1.GetChisquare()/self._erf_f1.GetNDF()
        return norm,mean,sigma,err_norm,err_mean,err_sigma,chisquare_ndf,fit_error

    def _residual_hist(self,h,fitfunc,knormalize):
        resid_hist=h.Clone()
        resid_hist.Reset()
        resid_hist.SetName(fitfunc.GetTitle())
        if(knormalize==0):
            resid_hist.SetTitle(str("Residuals_"+fitfunc.GetTitle()))
        else:
            resid_hist.SetTitle(str("Residuals_"+fitfunc.GetTitle()))
        resid_hist.SetMarkerColor(fitfunc.GetMarkerColor())
        resid_hist.SetLineColor(fitfunc.GetLineColor())
        tmp_arr=np.zeros((h.GetSize(),), dtype=np.double)
        buffer  = array.array('f', tmp_arr)
        #print str(buffer)
        #buffer=[]
        if(knormalize==0):
            for i in range(0,h.GetSize()):
                res = h.GetBinContent(i) - fitfunc.Eval(h.GetBinCenter(i))
                res_err = h.GetBinError(i)
                resid_hist.SetBinContent(i,res)
                resid_hist.SetBinError(i,res_err)
        if(knormalize==1):
            for i in range(0,h.GetSize()):
                res = h.GetBinContent(i) - fitfunc.Eval(h.GetBinCenter(i))
                res_err = h.GetBinError(i)
                if(res_err>0):
                    resid_hist.SetBinContent(i,res/res_err)
                    resid_hist.SetBinError(i,res_err)
        return resid_hist