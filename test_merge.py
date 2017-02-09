#!/usr/bin/python
import numpy as np
import os.path
import sys
import ROOT
from ROOT import gROOT, TCanvas, TGraphAsymmErrors, TH1, TF1, TH1F, TH1D, TTree, TFile, TTreeReader, TTreeReaderValue, TTreeReaderArray, TH2I, TH2F, TString, THStack, TGraphErrors, TList, TListIter, TIter, TObject, TH1I, TMath, TDirectory, TEfficiency, TF1Convolution, RooFit, TRandom,TAxis, TSpectrum, TPolyMarker
import array as array
import time
import merge_anal
from merge_anal import *

d= merge_anal()

