#!/usr/bin/python
import numpy as np
import os.path
import sys
import ROOT
from ROOT import gROOT, TCanvas, TGraphAsymmErrors, TH1, TF1, TH1F, TH1D, TTree, TFile, TTreeReader, TTreeReaderValue, TTreeReaderArray, TH2I, TH2F, TString, THStack, TGraphErrors, TList, TListIter, TIter, TObject, TH1I, TMath, TDirectory, TEfficiency, TF1Convolution, RooFit, TRandom,TAxis, TSpectrum, TPolyMarker
import array as array
import time
from optparse import OptionParser

class merge_anal:
    def __init__(self,fit_tree, position_tree, destination_file):
        self._gaussian_f1 = TF1('gauss_f1','[0]*TMath::Gaus(x,[1],[2],1)',0,256,3)
        self._gaussian_f1.SetNpx(2560)
        self._gaussian_f1.SetTitle("Gaussian")
        self._gaussian_f1.SetMarkerColor(ROOT.kRed)
        self._gaussian_f1.SetLineColor(ROOT.kRed)

        self._erf_f1 = TF1('Erf_f1','[0]*.5*(1+TMath::Erf(([1]-x)/[2]))',0,256,3)
        self._erf_f1.SetNpx(2560)
        self._erf_f1.SetTitle("Erf")
        self._erf_f1.SetMarkerColor(ROOT.kOrange)
        self._erf_f1.SetLineColor(ROOT.kOrange)

        self._threshold=1
        self._initial_expt_signal=0.0025

        self.file=TFile(str(fit_tree),"READ")
        self._tree = self.file.Get("tree")
        self._tree.SetName("extract_tree")
        # self.file_1=TFile("~/LaserScanData/Log_Thu20170209-140334.root","READ")
        self.file_1=TFile(position_tree,"READ")
        # self.file_1=TFile("Log_Tue20170207-172450.root","READ")
        self._tree1 = self.file_1.Get("tree")
        self._tree1.SetName("pos_tree")
        self._destination_file=destination_file
        #self._Print_First()
        self.graphs= []
        #self._init_graphs()

        self._Max_X=0
        self._Max_Y=0
        self._Max_Z=0

        self._Min_X=0
        self._Min_Y=0
        self._Min_Z=0

        self._Spac_X=0
        self._Spac_Y=0
        self._Spac_Z=0

        self._Dir_X=0
        self._Dir_Y=0
        self._Dir_Z=0
        
        self._Bins_X=0
        self._Bins_Y=0
        self._Bins_Z=0

        self._Max_Hist_X=0
        self._Max_Hist_Y=0
        self._Max_Hist_Z=0

        self._Min_Hist_X=0
        self._Min_Hist_Y=0
        self._Min_Hist_Z=0

        
        self._Get_Spacing()
        self._Get_Min_Max()
        self._Get_Binning()
        self._Print_Run_Info()

        self.th1d_x=ROOT.TH1D()
        self.th1d_y=ROOT.TH1D()
        self.th1d_z=ROOT.TH1D()
        self.th1_hists_x = []
        self.th1_hists_y = []
        self.th1_hists_z = []

        self.th1d_x_r_p_l=ROOT.TH1D()
        self.th1d_x_r_m_l=ROOT.TH1D()
        self.th1d_x_r_g=ROOT.TH1D()
        self.th1d_x_l_g=ROOT.TH1D()
        self.th1d_x_r_m_l_g=ROOT.TH1D()

        self.th1_hists_x_anal = []


        self.th2d_xy=ROOT.TH2D()
        self.th2d_xz=ROOT.TH2D()
        self.th2d_yz=ROOT.TH2D()
        self.th2_hists_xy = []
        self.th2_hists_xz = []
        self.th2_hists_yz = []
        
        self._Initialize_Hists()
        self._Fill_Hists()
        self._Analyze_Hists()
        self._Write_Hists()
        #self._Channel_range()
    def _Get_Min_Max(self):
        self._Max_X = self._tree1.GetMaximum("X")
        self._Max_Y = self._tree1.GetMaximum("Y")
        self._Max_Z = self._tree1.GetMaximum("Z")
        self._Min_X = self._tree1.GetMinimum("X")
        self._Min_Y = self._tree1.GetMinimum("Y")
        self._Min_Z = self._tree1.GetMinimum("Z")
        self._Get_Spacing()
    def _Channel_range(self):
        print self._tree.GetMaximum("Channel_No")
        print self._tree.GetMinimum("Channel_No")

    def _Get_Spacing(self):
        x=0
        y=0
        z=0
        x_start=0
        y_start=0
        z_start=0
        for event1 in range(0,self._tree1.GetEntries()):
            self._tree1.GetEntry(event1)
            x_start=self._tree1.X
            y_start=self._tree1.Y
            z_start=self._tree1.Z
            for event2 in range(event1,self._tree1.GetEntries()-event1):
                self._tree1.GetEntry(event2)
                x=self._tree1.X
                y=self._tree1.Y
                z=self._tree1.Z
                if (x_start!=x and self._Dir_X==0):
                    self._Spac_X = abs(x-x_start)
                    print "space x ", self._Spac_X
                    self._Dir_X=1
                if (y_start!=y and self._Dir_Y==0):
                    self._Spac_Y =abs(y-y_start)
                    print "space y ", self._Spac_Y
                    self._Dir_Y=1
                if (z_start!=z and self._Dir_Z==0):
                    self._Spac_Z =abs(z-z_start)
                    print "space z ", self._Spac_Z 
                    self._Dir_Z=1
                if (self._Dir_X==1 and self._Dir_Y==1 and self._Dir_Z==1):
                    break
            break
    def _Get_Binning(self):
        self._Spac_X=round(self._Spac_X,3)
        self._Spac_Y=round(self._Spac_Y,3)
        self._Spac_Z=round(self._Spac_Z,3)
        if self._Spac_X!=0:
            self._Bins_X=(int)(round((self._Max_X-self._Min_X)/self._Spac_X,1)+1)
            self._Max_Hist_X=self._Max_X+self._Spac_X/2.
            self._Min_Hist_X=self._Min_X-self._Spac_X/2.
        if self._Spac_Y!=0:
            self._Bins_Y=(int)(round((self._Max_Y-self._Min_Y)/self._Spac_Y,1)+1)
            self._Max_Hist_Y=self._Max_Y+self._Spac_Y/2.
            self._Min_Hist_Y=self._Min_Y-self._Spac_Y/2.
        if self._Spac_Z!=0:
            self._Bins_Z=(int)(round((self._Max_Z-self._Min_Z)/self._Spac_Z,1)+1)
            self._Max_Hist_Z=self._Max_Z+self._Spac_Z/2.
            self._Min_Hist_Z=self._Min_Z-self._Spac_Z/2.
    def _Print_Run_Info(self):
        print "Run Information:"
        print "Spacing:"
        print "dx\tdy\tdz"
        print "%.4f\t%.4f\t%.4f"%(self._Spac_X,self._Spac_Y,self._Spac_Z)
        print "Volume:"
        print "x\ty\tz"
        print "%.4f\t%.4f\t%.4f"%(self._Max_X-self._Min_X,self._Max_Y-self._Min_Y,self._Max_Z-self._Min_Z)
        print "Start Point (Min)"
        print "x\ty\tz"
        print "%.4f\t%.4f\t%.4f"%(self._Min_X,self._Min_Y,self._Min_Z)
        print "End Point (Max)"
        print "x\ty\tz"
        print "%.4f\t%.4f\t%.4f"%(self._Max_X,self._Max_Y,self._Max_Z)
        print "Hist_X:"
        print "%.4f\t%.4f\t%.4f"%(self._Bins_X,self._Min_Hist_X,self._Max_Hist_X)
        print "Hist_Y:"
        print "%.4f\t%.4f\t%.4f"%(self._Bins_Y,self._Min_Hist_Y,self._Max_Hist_Y)
        print "Hist_Z:"
        print "%.4f\t%.4f\t%.4f"%(self._Bins_Z,self._Min_Hist_Z,self._Max_Hist_Z)
    def _Initialize_Hists(self):
        no_pixel=97
        if(self._Dir_X>0):
            self.th1d_x=ROOT.TH1D("X_HIST","X_HIST",self._Bins_X,self._Min_Hist_X,self._Max_Hist_X)
            for i in range(1,no_pixel):
                tmp=ROOT.TH1D(self.th1d_x)
                tmp.SetName("X_HIST_"+str(i).zfill(3))
                tmp.SetTitle("X_HIST_"+str(i).zfill(3))
                self.th1_hists_x.append(tmp)
                tmp1=[]
                tmp=ROOT.TH1D(self.th1d_x)
                tmp.SetName("X_HIST_r_p_l_"+str(i).zfill(3))
                tmp.SetTitle("X_HIST Sum"+str(i).zfill(3))
                tmp1.append(tmp)
                tmp=ROOT.TH1D(self.th1d_x)
                tmp.SetName("X_HIST_r_m_l_"+str(i).zfill(3))
                tmp.SetTitle("X_HIST Diff"+str(i).zfill(3))
                tmp1.append(tmp)
                tmp=ROOT.TH1D(self.th1d_x)
                tmp.SetName("X_HIST_r_g_"+str(i).zfill(3))
                tmp.SetTitle("X_HIST R over Sum"+str(i).zfill(3))
                tmp1.append(tmp)
                tmp=ROOT.TH1D(self.th1d_x)
                tmp.SetName("X_HIST_l_g_"+str(i).zfill(3))
                tmp.SetTitle("X_HIST L over Sum"+str(i).zfill(3))
                tmp1.append(tmp)
                tmp=ROOT.TH1D(self.th1d_x)
                tmp.SetName("X_HIST_d_g_"+str(i).zfill(3))
                tmp.SetTitle("X_HIST Diff over Sum"+str(i).zfill(3))
                tmp1.append(tmp)
                self.th1_hists_x_anal.append(tmp1)
        if(self._Dir_Y>0):
            self.th1d_y=ROOT.TH1D("Y_HIST","Y_HIST",self._Bins_Y,self._Min_Hist_Y,self._Max_Hist_Y)
            for i in range(1,no_pixel):
                tmp=ROOT.TH1D(self.th1d_y)
                tmp.SetName("Y_HIST_"+str(i).zfill(3))
                tmp.SetTitle("Y_HIST_"+str(i).zfill(3))
                self.th1_hists_y.append(tmp)
        if(self._Dir_Z>0):
            self.th1d_Z=ROOT.TH1D("Z_HIST","Z_HIST",self._Bins_Z,self._Min_Hist_Z,self._Max_Hist_Z)
            for i in range(1,no_pixel):
                tmp=ROOT.TH1D(self.th1d_z)
                tmp.SetName("Z_HIST_"+str(i).zfill(3))
                tmp.SetTitle("Z_HIST_"+str(i).zfill(3))
                self.th1_hists_z.append(tmp)
        if(self._Dir_X>0 and self._Dir_Y>0):
            self.th2d_xy=ROOT.TH2D("XY_HIST","XY_HIST",self._Bins_X,self._Min_Hist_X,self._Max_Hist_X,self._Bins_Y,self._Min_Hist_Y,self._Max_Hist_Y)
            self.th2d_xy.SetMaximum(256)
            self.th2d_xy.SetMinimum(0)
            for i in range(1,no_pixel):
                tmp=ROOT.TH2D(self.th2d_xy)
                tmp.SetName("XY_HIST_"+str(i).zfill(3))
                tmp.SetTitle("XY_HIST_"+str(i).zfill(3))
                self.th2_hists_xy.append(tmp)
        if(self._Dir_X>0 and self._Dir_Z>0):
            self.th2d_xz=ROOT.TH2D("XZ_HIST","XZ_HIST",self._Bins_X,self._Min_Hist_X,self._Max_Hist_X,self._Bins_Z,self._Min_Hist_Z,self._Max_Hist_Z)
            self.th2d_xz.SetMaximum(256)
            self.th2d_xz.SetMinimum(0)
            for i in range(1,no_pixel):
                tmp=ROOT.TH2D(self.th2d_xz)
                tmp.SetName("XZ_HIST_"+str(i).zfill(3))
                tmp.SetTitle("XZ_HIST_"+str(i).zfill(3))
                self.th2_hists_xz.append(tmp)
        if(self._Dir_Y>0 and self._Dir_Z>0):
            self.th2d_yz=ROOT.TH2D("YZ_HIST","YZ_HIST",self._Bins_Y,self._Min_Hist_Y,self._Max_Hist_Y,self._Bins_Z,self._Min_Hist_Z,self._Max_Hist_Z)
            self.th2d_yz.SetMaximum(256)
            self.th2d_yz.SetMinimum(0)
            for i in range(1,no_pixel):
                tmp=ROOT.TH2D(self.th2d_yz)
                tmp.SetName("YZ_HIST_"+str(i).zfill(3))
                tmp.SetTitle("YZ_HIST_"+str(i).zfill(3))
                self.th2_hists_yz.append(tmp)
    def _Write_Hists(self):
        r_file=TFile(self._destination_file,"RECREATE")
        r_file.mkdir("dir_x")
        ROOT.gDirectory.cd("dir_x")
        if(self._Dir_X):
            #self.th2d_xy.Write()
            for it in self.th1_hists_x:
                it.Write()
        r_file.cd()
        r_file.mkdir("dir_y")
        ROOT.gDirectory.cd("dir_y")
        if(self._Dir_Y):
            #self.th2d_xy.Write()
            for it in self.th1_hists_y:
                it.Write()
        r_file.cd()
        r_file.mkdir("dir_z")
        ROOT.gDirectory.cd("dir_z")
        if(self._Dir_Z):
            #self.th2d_xy.Write()
            for it in self.th1_hists_z:
                it.Write()
        r_file.cd()
        r_file.mkdir("dir_xy")
        ROOT.gDirectory.cd("dir_xy")
        if(self._Dir_X>0 and self._Dir_Y>0):
            #self.th2d_xy.Write()
            for it in self.th2_hists_xy:
                it.Write()
        r_file.cd()
        r_file.mkdir("dir_xz")
        ROOT.gDirectory.cd("dir_xz")
        if(self._Dir_X>0 and self._Dir_Z>0):
            #self.th2d_xz.Write()
            for it in self.th2_hists_xz:
                it.Write()
        r_file.cd()
        r_file.mkdir("dir_yz")
        ROOT.gDirectory.cd("dir_yz")
        if(self._Dir_Y>0 and self._Dir_Z>0):
            #self.th2d_yz.Write()
            for it in self.th2_hists_yz:
                it.Write()
        r_file.cd()
        r_file.mkdir("strip_anal")
        ROOT.gDirectory.cd("strip_anal")
        if(self._Dir_X>0 and self._Dir_Y==0 and self._Dir_Z==0):
            for num,it in enumerate(self.th1_hists_x_anal):
                ROOT.gDirectory.mkdir("strip_"+str(num).zfill(3))
                ROOT.gDirectory.cd("strip_"+str(num).zfill(3))
                for bla in it:
                    bla.Write()
                ROOT.gDirectory.cd("..")
        r_file.cd()

        r_file.mkdir("total")
        ROOT.gDirectory.cd("total")
        if( self.th2d_xy.GetEntries()>0):
            self.th2d_xy.Write()
        if( self.th2d_xz.GetEntries()>0):
            self.th2d_xz.Write()
        if( self.th2d_yz.GetEntries()>0):
            self.th2d_yz.Write()
        if( self.th1d_x.GetEntries()>0):
            self.th1d_x.Write()
        if( self.th1d_y.GetEntries()>0):
            self.th1d_y.Write()
        if( self.th1d_z.GetEntries()>0):
            self.th1d_z.Write()
        r_file.Close()
    def _Fill_Hists(self):
        for event in xrange(self._tree.GetEntries()):
            self._tree.GetEntry(event)
            #self._tree.Noise_Mean
            #self._tree.Noise_Norm      
            #self._tree.Noise_Mean      
            #self._tree.Noise_Sigma     
            #self._tree.Noise_Chisqrndf 
            #self._tree.Noise_Fit_Error 
            #self._tree.Err_Noise_Norm  
            #self._tree.Err_Noise_Mean  
            #self._tree.Err_Noise_Sigma 
            #self._tree.Signal_Norm     
            #self._tree.Signal_Mean     
            #self._tree.Signal_Sigma    
            #self._tree.Signal_Chisqrndf
            #self._tree.Signal_Fit_Error
            #self._tree.Err_Signal_Norm 
            #self._tree.Err_Signal_Mean 
            #self._tree.Err_Signal_Sigma
            #self._tree.Found_Signal    
            #self._tree.Channel_No
            #if (
            #self._tree.Signal_Mean >0 and 
            #self._tree.Signal_Mean <256):
                #self._tree.Signal_Chisqrndf<1000 and 
                #self._tree.Noise_Mean<self._tree.Signal_Mean):
            
            signal=self._tree.Signal_Mean -self._tree.Noise_Mean
            #print self._tree.Signal_Mean -self._tree.Noise_Mean, self._tree.Err_Noise_Mean+self._tree.Err_Signal_Mean, self._tree.FILENAME
            tmp=int((str(self._tree.FILENAME))[2:])
            self._tree1.GetEntry(tmp)
            #print (
                #self._tree1.X,
                #self._tree1.Y,
                #self._tree1.Z,
                #self._tree1.FILENAME,
                ##self._tree1.RUN
                #)
                #self.th2_hists_xy[(int)(self._tree.Channel_No)].Fill(self._tree1.X,self._tree1.Y,signal)
                #self.th2_hists_xz[(int)(self._tree.Channel_No)].Fill(self._tree1.X,self._tree1.Z,signal)
            # if(signal>0 and signal < 256 and self._tree.Signal_Chisqrndf < 1000 and  self._tree.Noise_Chisqrndf < 100 ):
            if(signal>0 and signal < 256):
                if(self._Dir_X>0):
                    self.th1_hists_x[(int)(self._tree.Channel_No)].Fill(self._tree1.X,signal)
                if(self._Dir_Y>0):
                    self.th1_hists_y[(int)(self._tree.Channel_No)].Fill(self._tree1.Y,signal)
                if(self._Dir_Z>0):
                    self.th1_hists_z[(int)(self._tree.Channel_No)].Fill(self._tree1.Z,signal)
                if(self._Dir_X>0 and self._Dir_Y>0):
                    self.th2_hists_xy[(int)(self._tree.Channel_No)].Fill(self._tree1.X,self._tree1.Y,signal)
                if(self._Dir_X>0 and self._Dir_Z>0):
                    self.th2_hists_xz[(int)(self._tree.Channel_No)].Fill(self._tree1.X,self._tree1.Z,signal)
                if(self._Dir_Y>0 and self._Dir_Z>0):
                    self.th2_hists_yz[(int)(self._tree.Channel_No)].Fill(self._tree1.Y,self._tree1.Z,signal)
        for hist in self.th1_hists_x:
            self.th1d_x.Add(hist,1)
        for hist in self.th1_hists_y:
            self.th1d_y.Add(hist,1)
        for hist in self.th1_hists_z:
            self.th1d_z.Add(hist,1)
        
        # for event1 in xrange(0,self._tree1.GetEntries()):
        #     self._tree1.GetEntry(event1)        
        #     #if(self._tree1.X>66.7 and self._tree1.X<70 and self._tree1.Z<121 and self._tree1.Z>120.0):
        #     if(self._tree1.Y>66.7 and self._tree1.Y<66.8 and self._tree1.Z<121 and self._tree1.Z>120.8):
        #         print self._tree1.FILENAME,self._tree1.Y,self._tree1.Z
        #         #self.th2d_xy.Fill(self._tree1.X,self._tree1.Y,signal)
        #         #self.th2d_xz.Fill(self._tree1.X,self._tree1.Z,signal)

    def _Analyze_Hists(self):
        for num,i in enumerate(self.th1_hists_x):
            if(num>0 and num<len(self.th1_hists_x)-1):
                self.th1_hists_x_anal[num][0].Add(self.th1_hists_x[num],1)
                self.th1_hists_x_anal[num][0].Add(self.th1_hists_x[num+1],1)
                self.th1_hists_x_anal[num][1].Add(self.th1_hists_x[num],1)
                self.th1_hists_x_anal[num][1].Add(self.th1_hists_x[num+1],-1)
                self.th1_hists_x_anal[num][2].Add(self.th1_hists_x[num+1],1)
                self.th1_hists_x_anal[num][2].Divide(self.th1_hists_x_anal[num][0])
                self.th1_hists_x_anal[num][3].Add(self.th1_hists_x[num],1)
                self.th1_hists_x_anal[num][3].Divide(self.th1_hists_x_anal[num][0])
                self.th1_hists_x_anal[num][4].Add(self.th1_hists_x_anal[num][1],1)
                self.th1_hists_x_anal[num][4].Divide(self.th1_hists_x_anal[num][0])
                
                # print num ,str(i.GetTitle())
                

    def _Print_First(self):
        bla =0
        for event in xrange(self._tree.GetEntries()):
            self._tree.GetEntry(event)
            #self._tree.Noise_Mean
            #self._tree.Noise_Norm      
            #self._tree.Noise_Mean      
            #self._tree.Noise_Sigma     
            #self._tree.Noise_Chisqrndf 
            #self._tree.Noise_Fit_Error 
            #self._tree.Err_Noise_Norm  
            #self._tree.Err_Noise_Mean  
            #self._tree.Err_Noise_Sigma 
            #self._tree.Signal_Norm     
            #self._tree.Signal_Mean     
            #self._tree.Signal_Sigma    
            #self._tree.Signal_Chisqrndf
            #self._tree.Signal_Fit_Error
            #self._tree.Err_Signal_Norm 
            #self._tree.Err_Signal_Mean 
            #self._tree.Err_Signal_Sigma
            #self._tree.Found_Signal    
            #self._tree.Channel_No
            
            if (self._tree.Channel_No==20 and 
                self._tree.Signal_Mean >0 and 
                self._tree.Signal_Chisqrndf<10 and 
                self._tree.Noise_Mean<self._tree.Signal_Mean):
                print self._tree.Signal_Mean -self._tree.Noise_Mean, self._tree.Err_Noise_Mean+self._tree.Err_Signal_Mean, self._tree.FILENAME
                tmp=int((str(self._tree.FILENAME))[2:])
                self._tree1.GetEntry(tmp)
                print (
                    self._tree1.X,
                    self._tree1.Y,
                    self._tree1.Z,
                    self._tree1.FILENAME,
                    #self._tree1.RUN
                    )


        #for event1 in xrange(self._tree1.GetEntries()):
            #self._tree1.GetEntry(event1)
            #bla+=1
            #if bla>200:
                #break

            #print (
            #self._tree1.X,
            #self._tree1.Y,
            #self._tree1.Z,
            #self._tree1.FILENAME,
            #self._tree1.RUN
            #)
            

parser = OptionParser()
parser.add_option('-e', '--extracted_signals', metavar='F', type='string', action='store',
# default       =       'none',
default =       'Intensity.root',
dest    =       'fit_tree',
help    =       'File with fit parameters')

parser.add_option('-p', '--position_tree', metavar='F', type='string', action='store',
default =       '/home/silicon/LaserScanData/Log_Thu20170209-140334.root',
dest    =       'position_tree',
help    =       'File with xyz Runno information')

parser.add_option('-o', '--out_file', metavar='F', type='string', action='store',
default =       'Output_analysis.root',
dest    =       'out_file',
help    =       'Destination File')

(options, args) = parser.parse_args()

fit_tree = options.fit_tree
position_tree = options.position_tree
destination_file = options.out_file

ROOT.gROOT.SetBatch()

d= merge_anal(fit_tree, position_tree, destination_file)
