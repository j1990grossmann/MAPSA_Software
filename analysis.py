#!/usr/bin/python
import numpy as np
from ROOT import gROOT, TCanvas, TF1, TH1F, TTree, TFile, TTreeReader, TTreeReaderValue, TTreeReaderArray, TH2I, TString, THStack, TGraphErrors, TList, TListIter, TIter, TObject
import array as array
no_mpa_light=2
filelist = [
	# "sourcetestsourcetest_inv_100V_SR_90_not_top_ffffe_rep_10_l_0_u_255_16_09_10.root",
	# "sourcetestsourcetest_inv_100V_SR_90_not_top_ffffe_rep_10_l_0_u_100_single_pixel_16_09_10.root"
	"sourcetesttest.root"
    # "sourcetestsourcetest_inv__100V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_10.root"
    # "sourcetestno_2.root",
    # "sourcetestnoise.root",
    # "sourcetestno_source_2.root",
    # "sourcetestsourcetest_norm__100V_SR_90_on_top_ffffe_rep_100_l_0_u_255_16_08_12.root",
    # "sourcetestsourcetest_inv__100V_SR_90_on_top_ffffe_rep_10_l_0_u_255_16_08_12.root",
    # "sourcetestsourcetest_inv__100V_SR_90_on_top_ffffe_rep_50_l_0_u_255_16_08_12_1.root"
    # "sourcetestsourcetest_norm_SR_90_on_top_ffffe_rep_10_l_0_u_255_16_08_12.root",
    # "sourcetest_norm__100V_SR_90_on_top_ffffe_rep_100_l_0_u_255_16_08_12.root",
    # "sourcetestsourcetest_norm__100V_SR_90_on_top_ffffe_rep_100_l_0_u_255_16_08_12.root",
    # "sourcetest.root",
    # "sourcetesttest.root"
]

for files in filelist:
	f = TFile(files,'READ')
	f.ls()
	tree = f.Get('tree')
	tree.ls()
	# tree.Print()
        
        outfile = TString(files)
        outfile.ReplaceAll(".root","")
	print outfile
	g = TFile("analysis.root","RECREATE")
	g.mkdir(str(outfile))
	g.cd(str(outfile))
	channelcounts = TH2I('HitMap','Totalcounts; channel; DAC Value (1.456 mV)', 288, .5,288.5,256, .5, 256.5)
	normgraph      = TGraphErrors(no_mpa_light*48)
	meangraph      = TGraphErrors(no_mpa_light*48) 
	sigmagraph     = TGraphErrors(no_mpa_light*48) 
	chisquaregraph = TGraphErrors(no_mpa_light*48)
	mean_corrgraph = TGraphErrors(no_mpa_light*48)
	normgraph      .SetName('normgraph' )
	meangraph      .SetName('meangraph' )
	sigmagraph     .SetName('sigmagraph')
	chisquaregraph .SetName('chisquare')
	mean_corrgraph .SetName('mean_corr')
	# meanhist       = TH1F('meanhist_'+savestr,'Mean DAC; DAC Value (1.456 mV); counts', 256,0,255)
	# sigmahist      = TH1F('sigmahist_'+savestr,'Sigma DAC; DAC Value (1.456 mV); counts', 250,0,10)
	normgraph.SetTitle('Normalization; Channel; Normalization')
	meangraph.SetTitle('Mean; Channel; DAC Value (1.456 mV)')
	sigmagraph.SetTitle('Sigma; Channel; DAC Value (1.456 mV)')
	chisquaregraph.SetTitle('Chisquared/NDF; Channel; Chisquared/NDF ')
	
	fitfuncs = []
	gr1 = []
	for iy1 in range(0,no_mpa_light*48):
		fitfuncs.append(TF1('gaus','gaus', 0,256))
		# gr1[iy1].Fit(fitfuncs[iy1],'rq +rob=0.8','',0,256)
		
	#Here we read the data and fill the histogram
	for event in tree :
	    eventstr = []
	    for counter, vals in enumerate(tree.AR_MPA):
	        # eventstr.append(vals)
	        channelcounts.Fill(counter+1,tree.THRESHOLD,vals)
		# print eventstr
	    if tree.THRESHOLD%10==0 and tree.REPETITION==0:
		    print tree.THRESHOLD
		    print tree.AR_MPA
	    # print tree.REPETITION
	# g.cd()
	
	#now we make a small analysis of the curves fitting different functions to it:
	#first create a THStack with histograms:
	stack = THStack(channelcounts, 'y', 'channel','channel')
	iterator = stack.GetHists()
	# iterator.ls()
	g.cd(str(outfile))
	g.mkdir(str(outfile)+"/Channels")
	g.cd(str(outfile)+"/Channels")
	iterator.Write()
	# while (TObject(iterator.Next())): 
	# 	print iterator.Next().Title()
		
			
	# stack.Write("stack")
	g.cd(str(outfile))
	channelcounts.Write(str(outfile))
	f.Close()    
	g.Close()
	    
	    # print 'Counter_Value', tree.AR_MPA
	    # print 'Threshold', tree.THRESHOLD
	    # print 'Repetition', tree.REPETITION
	    # print ''
	# myReader  = TTreeReader ("tree", f);
	# # CounterDataArray     = TTreeReaderArray<> (myReader,'tree.AR_MPA')
	# threshold = TTreeReaderValue<int> (myReader, 'THRESHOLD')
	# repetition = TTreeReaderValue<int> (myReader, 'REPETITION')
	# reader = TTreeReader("EventTree", f)
	# TTreeReaderValue<int> eventSize(reader, "fEventSize");
	# while (myReader.Next()):
	#            print threshold
	#            print repetition
	
