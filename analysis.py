#!/usr/bin/python
import numpy as np
from ROOT import gROOT, TCanvas, TF1, TH1F, TTree, TFile, TTreeReader, TTreeReaderValue, TTreeReaderArray, TH2I, TString, THStack, TGraphErrors, TList, TListIter, TIter, TObject, TH1I, TMath
import ROOT
import array as array
import time
no_mpa_light=6

def error_function(x,par):
    # """
    # Norm:par[0]
    # Mean:par[1]
    # Sigma:par[2]
    # """
    return 0.5*par[0]*(1-ROOT.TMath.Erf((x[0]-par[1])/(par[2]*ROOT.TMath.Sqrt2())))
def combined(x,par):
	return 0.5*par[0]*((1-ROOT.TMath.Erf((x[0]-par[1])/(par[2]*ROOT.TMath.Sqrt2())))-(1-ROOT.TMath.Erf((x[0]-par[3])/(par[4]*ROOT.TMath.Sqrt2()))))
def combined_mean(x,par):
	return 0.5*par[0]*((1-ROOT.TMath.Erf((x[0]-par[1])/(par[2]*ROOT.TMath.Sqrt2())))-(1-ROOT.TMath.Erf((x[0]-par[1])/(par[3]*ROOT.TMath.Sqrt2()))))
def double_gauss(x,par):
	return par[0]*ROOT.TMath.Gaus(x[0],par[1],par[2])+par[3]*ROOT.TMath.Gaus(x[0],par[1],par[4])



filelist = [
    # Bias Scan
    
    # "sourcetestinv_000V_SR_90_not_top_ffffe_rep_10_l_0_u_255_16_09_13.root                             ",
    # "sourcetestinv_000V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_13.root                              ",
    # "sourcetestinv_010V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_13.root                              ",
    # "sourcetestinv_020V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_13.root                              ",
    # "sourcetestinv_030V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_13.root                              ",
    # "sourcetestinv_040V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_13.root                              ",
    # "sourcetestinv_050V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_13.root                              ",
    # "sourcetestinv_060V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_13.root                              ",
    # "sourcetestinv_070V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_13.root                              ",
    # "sourcetestinv_080V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_13.root                              ",
    # "sourcetestinv_090V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_13.root                              ",
	# "sourcetestinv_100V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_13.root                              ",
	# "sourcetestinv_110V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_13.root                              ",
	# "sourcetestinv_120V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_13.root                              ",

	# "sourcetestsourcetest_inv__000V_SR_90_not_top_ffffe_rep_100_l_0_u_255_16_09_16.root                ",
       # single pixels vs normal
	"sourcetestsingle_pixel_inv_100V_SR_90_not_top_ffffe_rep_10_l_0_u_80_16_09_13.root                 ",
        "sourcetestinv_100V_SR_90_not_top_ffffe_rep_10_l_0_u_255_16_09_13.root                             ",

        # Source vs Noise inverted
	# "sourcetestsourcetest_inv_100V_SR_90_not_top_ffffe_rep_10_l_0_u_100_single_pixel_16_09_10.root     ",
	"sourcetestsourcetest_inv__100V_SR_90_not_top_ffffe_rep_100_l_0_u_255_16_08_12.root                ",
	# "sourcetestsourcetest_inv__100V_SR_90_on_top_ffffe_rep_100_l_0_u_255_16_08_12_1_1.root             ",
        "sourcetestsourcetest_inv__100V_SR_90_on_top_ffffe_rep_100_l_0_u_255_16_08_16.root",
	# # "sourcetestsourcetest_inv_100V_SR_90_not_top_ffffe_rep_10_l_0_u_255_16_09_10.root                  ",
	# # "sourcetestsourcetest_inv__100V_SR_90_not_top_ffffe_rep_1_l_0_u_255_16_09_10.root                  ",
	# # "sourcetestsourcetest_inv_SR_90_not_on_top_ffffe_rep_1000_l_0_u_255.root                           ",
	"sourcetestsourcetest_norm__100V_SR_90_on_top_ffffe_rep_100_l_0_u_255_16_08_12.root                "
	# "sourcetestSR_90_not_on_top_ffffe_rep_10000_l_0_u_255.root                                         ",
	# "sourcetestSR_90_not_on_top_ffffe_rep_10_l_0_u_255.root                                            ",
	# "sourcetestSR_90_on_top_ffffe_rep_100_l_0_u_255.root                                               ",
	# "sourcetestSR_90_on_top_ffffe_rep_100_l_40_u_255.root                                              ",
	# "sourcetestSR_90_on_top_ffffe_rep_100.root                                                         ",
	# "sourcetestSR_90_on_top_ffffe_rep_25.root                                                          ",
	# "sourcetestSR_90_on_top.root                                                                       ",
	# "sourcetesttestlaser.root                                                                          ",
	# "sourcetesttest.root                                                                               "

]
ROOT.gROOT.SetBatch()
g = TFile("analysis.root","RECREATE")
c1 = TCanvas('c1', 'Pixel Monitor ', 700, 900)
c2 = TCanvas('c2', 'Pixel Monitor ', 1280, 720)
c3 = TCanvas('c3', 'Pixel Monitor ', 1280, 720)
for files in filelist:
        # channels = 288    	
        channels = 250    	
    	if "inv_" in files:
            channels=96
	c2.Clear()
	c2.Divide(2,1)
        c3.Clear()
	for i in range(1,4):
		c2.cd(i)
		ROOT.gPad.SetGridx()
		ROOT.gPad.SetGridy()
    
	c1.Clear()
	c1.Divide(3,2)
	for i in range(1,7):
		c1.cd(i)
		ROOT.gPad.SetGridx()
		ROOT.gPad.SetGridy()

	f = TFile(files,'READ')
	f.ls()
	tree = f.Get('tree')
	# tree.ls()
	# tree.Print()
        outfile = TString(files)
        outfile.ReplaceAll(".root","")
        outfile.ReplaceAll(" ","")
	# print outfile
	g.mkdir(str(outfile))
	g.cd(str(outfile))
	channelcounts = TH2I('HitMap','Counts; Channel; DAC Value (1.456 mV)', 288, .5,288.5,256, .5, 256.5)
	normgraph      = TGraphErrors()
	meangraph      = TGraphErrors() 
	sigmagraph     = TGraphErrors() 
	chisquaregraph = TGraphErrors()
	mean_corrgraph = TGraphErrors()
	objarr=[]
	objarr.append(normgraph      )
	objarr.append(meangraph      )
	objarr.append(sigmagraph     )
	objarr.append(chisquaregraph )
	objarr.append(mean_corrgraph )
	for objs in objarr:
		objs.SetMarkerColor(2)
		objs.SetMarkerStyle(20)
		objs.SetMarkerSize(1)
	normgraph      .SetName('normgraph' )
	meangraph      .SetName('meangraph' )
	sigmagraph     .SetName('sigmagraph')
	chisquaregraph .SetName('chisquare')
	mean_corrgraph .SetName('mean_corr')
	# meanhist       = TH1F('meanhist_'+savestr,'Mean DAC; DAC Value (1.456 mV); counts', 256,0,255)
	# sigmahist      = TH1F('sigmahist_'+savestr,'Sigma DAC; DAC Value (1.456 mV); counts', 250,0,10)
	normgraph.SetTitle('Normalization; Channel; Normalization')
	# meangraph.SetTitle('Mean; Channel; DAC Value (1.456 mV)')
	meangraph.SetTitle('Mean; Channel; DAC Value (a.u.)')
	# sigmagraph.SetTitle('Sigma; Channel; DAC Value (1.456 mV)')
	sigmagraph.SetTitle('Sigma; Channel; DAC Value (a.u.)')
	chisquaregraph.SetTitle('Chisquared/NDF; Channel; Chisquared/NDF ')
	ROOT.gStyle.SetOptFit(1111)
	# stack = THStack('a','Pixel Curves;DAC Value (1.456 mV);Counts (1/1.456)')
	stack = THStack('a','Pixel Curves;DAC Value (a.u.);Counts ')
	fitfuncs = []
	fitparams = []
	gr1 = []
	for pixel in range(0, channels):
		# gr1.append(TH1I(str(pixel),str(pixel+1)+';DAC Value (1.456 mV);Counts (1/1.456)',256,0.5,256.5))
		gr1.append(TH1I(str(pixel),str(pixel+1)+';DAC Value (a.u.);Counts ',256,0.5,256.5))
		color=pixel%9+1
		gr1[pixel].SetLineColor(color)
		gr1[pixel].SetMarkerColor(color)
		gr1[pixel].SetFillColor(color)
		gr1[pixel].SetLineStyle(1)
		gr1[pixel].SetLineWidth(1)
		gr1[pixel].SetFillStyle(1)
		gr1[pixel].SetMarkerStyle(1)
		gr1[pixel].SetMarkerSize(.5)
		gr1[pixel].SetMarkerStyle(20)
		gr1[pixel].Sumw2(ROOT.kFALSE)
		stack.Add(gr1[pixel])
		fitfuncs.append(TF1('gauss'+str(pixel+1),'gaus(0)',0,256))
		fitfuncs[pixel].SetNpx(2560)
		fitfuncs[pixel].SetLineColor(color)
	
	#Here we read the data and fill the histogram
	for event in tree :
	    eventstr = []
	    for counter, vals in enumerate(tree.AR_MPA):
	        # eventstr.append(vals)
	        channelcounts.Fill(counter+1,tree.THRESHOLD,vals)
                if(counter<channels):
                    gr1[counter].Fill(tree.THRESHOLD,vals)
                    gr1[counter].SetBinError(gr1[counter].GetBin(tree.THRESHOLD),TMath.Sqrt(gr1[counter].GetBinContent(gr1[counter].GetBin(tree.THRESHOLD))))
		# print eventstr
	    if tree.THRESHOLD%10==0 and tree.REPETITION==0:
		    print tree.THRESHOLD
		    # print tree.AR_MPA
	
	#now we make a small analysis of the curves fitting different functions to it:
	#first create a THStack with histograms:
	iterator = stack.GetHists()
	for idx,it in enumerate(iterator):
		fitparams.append([])
		# if(it.Integral() >1):
		if(idx<channels):
			# fitfuncs.append(TF1('combined'+str(idx),combined, 0,256,5))
			# fitfuncs.append(TF1('combined_same_mean'+str(idx),combined_mean, 0,256,4))
			# fitfuncs.append(TF1('double_gauss'+str(idx),'gaus(0)+gaus(3)',0,256))
			# fitfuncs.append(TF1('gauss'+str(idx),'gaus(0)',0,256))
			# fitfuncs.append(TF1('double_gauss_same_mean'+str(idx),double_gauss, 0,256,5))
			# print it.GetName(), idx
			# fitfuncs[idx].SetParameters(it.GetMaximum(),it.GetMean()+1,it.GetRMS(),it.GetMean()-1,it.GetRMS());
			# fitfuncs[idx].SetParameters(it.GetMaximum(),it.GetMean(),it.GetRMS()*0.1,it.GetRMS()*0.1);
			fitfuncs[idx].SetParameters(it.GetMaximum(),it.GetMean(),it.GetRMS());
			# fitfuncs[idx].SetParameters(0.999*it.GetMaximum(),it.GetMean(),.7*it.GetRMS(),0.001*it.GetMaximum(),it.GetMean(),10*it.GetRMS());
			# fitfuncs[idx].SetParameters(0.999*it.GetMaximum(),it.GetMean(),.7*it.GetRMS(),0.001*it.GetMaximum(),10*it.GetRMS());
			# it.Fit(fitfuncs[idx],'lr0 rob=0.95','same',0,256)
			it.Fit(fitfuncs[idx],'lrq0 ','',0,256)
			fitparams[idx].append(fitfuncs[idx].GetParameter(0))
			fitparams[idx].append(fitfuncs[idx].GetParameter(1))
			fitparams[idx].append(fitfuncs[idx].GetParameter(2))
			fitparams[idx].append(fitfuncs[idx].GetParError(0))
			fitparams[idx].append(fitfuncs[idx].GetParError(1))
			fitparams[idx].append(fitfuncs[idx].GetParError(2))
			if(fitfuncs[idx].GetNDF()>0):
				fitparams[idx].append(fitfuncs[idx].GetChisquare()/fitfuncs[idx].GetNDF())
		else:
			for kk in range(0,7):
				fitparams[idx].append(0)
	print "fitparamarray"
	fitarray = np.array(fitparams)
	# print fitarray
	for pointno,it in enumerate(fitarray):
		if(fitarray[pointno][0]>0):
			normgraph.SetPoint(pointno, pointno+1,fitarray[pointno][0])
			normgraph.SetPointError(pointno, 0,fitarray[pointno][3])	 
			meangraph.SetPoint(pointno, pointno+1,fitarray[pointno][1])
			meangraph.SetPointError(pointno, 0,fitarray[pointno][4])	  
			sigmagraph.SetPoint(pointno, pointno+1,fitarray[pointno][2])
			sigmagraph.SetPointError(pointno, 0,fitarray[pointno][5])
			chisquaregraph.SetPoint(pointno, pointno+1,fitarray[pointno][6])
			chisquaregraph.SetPointError(pointno, 0 ,0)
	# iterator.ls()
	g.cd(str(outfile))
	g.mkdir(str(outfile)+"/Channels")
	g.cd(str(outfile)+"/Channels")
	iterator.Write()
	# iterator.First().Print("all")
	Maximum = TMath.Power(10,(round(TMath.Log10(stack.GetMaximum()))-1))

        ROOT.gStyle.SetLabelSize(0.06,"xyz");
        ROOT.gStyle.SetTitleSize(0.06,"xyz");
        ROOT.gStyle.SetTitleOffset(1.2,"y");
        ROOT.gStyle.SetTitleOffset(.825,"x");
        ROOT.gStyle.SetPadGridX(1);
        ROOT.gStyle.SetPadGridY(1);
        ROOT.gStyle.SetOptStat(0);
        # ROOT.gStyle.SetPadLeftMargin(.2);
        # ROOT.gStyle.SetPadRightMargin(.1);

	c1.cd(1)

	stack.Draw("nostack hist e1 x0")
	stack.GetXaxis().SetRangeUser(0,256)
	stack.SetMinimum(.1)
	stack.SetMaximum(Maximum)
	ROOT.gPad.SetLogy()
        c2.cd(1)
	stack.Draw("nostack hist e1 x0")
	stack.GetXaxis().SetRangeUser(0,256)
	stack.SetMinimum(.1)
	stack.SetMaximum(Maximum)
        ROOT.gPad.SetLeftMargin(.15);
        ROOT.gPad.SetRightMargin(.05);

	ROOT.gPad.SetLogy()
	ROOT.gPad.Update()
	for idx, it in enumerate(fitfuncs):
		# if idx>0 and idx<7:
            c1.cd(1)
            fitfuncs[idx].Draw("same")
            c2.cd(1)
            fitfuncs[idx].DrawCopy("psame")
            
		# it.SetLineColor(idx%9+1)
		# it.Draw("same")
            g.cd(str(outfile)+"/Channels")
            it.Write("HitMap_py_"+str(idx+1)+"_fit")
	c1.cd(2)
	chisquaregraph.Draw("ap")
	c1.cd(3)
	normgraph.Draw("ap")
	c1.cd(4)
	sigmagraph.Draw("ap")
	sigmagraph.GetYaxis().SetRangeUser(0,5)
	sigmagraph.GetXaxis().SetRangeUser(0,channels+1)
        c2.cd(2)
	sigmagraph.Draw("ap")
        ROOT.gPad.SetLeftMargin(.15);
        ROOT.gPad.SetRightMargin(.05);

	c1.cd(5)
	meangraph.Draw("ap")
	c1.cd(6)
	channelcounts.Draw("colz")
	channelcounts.GetXaxis().SetRangeUser(0,channels+1)
        ROOT.gPad.SetLogy()

        # c2.cd(3)
        c3.cd(0)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gPad.SetRightMargin(.15)
        ROOT.gPad.SetLeftMargin(.15)
        ROOT.gPad.SetGrid(0)
	copy = channelcounts.DrawCopy("colz")
        if(outfile.Contains("SR_90_on_top")):
            copy.SetMaximum(100)
            copy.SetMinimum(1)
        copy.GetYaxis().SetTitle("DAC Value (a.u.)")
        # else:
            # ROOT.gPad.SetLogz()
        # copy.GetYaxis().SetTitleOffset(1.5)
        
	c1.Update()
	c1.Modified()
	c2.Update()
	c2.Modified()
	c3.Update()
	c3.Modified()
	
	# c1.SaveAs("double_gauss_same_mean.pdf")
	# time.sleep(2)
	g.cd(str(outfile))
	for objs in objarr:
		objs.Write(objs.GetTitle())

	c1.Write("c1")
        outfile1=outfile+TString(".pdf")
        c2.SaveAs(str(outfile1))
        c2.Write("c2")
        c3.SaveAs("c3"+str(outfile1))
        c3.Write("c3")
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
	
