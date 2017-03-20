/*
 * <one line to give the program's name and a brief idea of what it does.>
 * Copyright (C) 2017  <copyright holder> <email>
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * 
 */

#include "Producer.h"


namespace PRODUCER{
GlobalHit Producer::GetHitCoordinate(Strip_Coordinate)
{

}
Strip_Coordinate Producer::GetStripCoordinate(int channel, int mpa_no)
{
    

}
void Producer::Set_PixelMaskMPA(int MPA_no, const std::vector<bool>& pixelMask_f)
{
    if(MPA_no<MaPSAMask.size())
        MaPSAMask.at(MPA_no)=pixelMask_f;
    else{
        std::cout<<"Incorrect MPA-light in the pixel mask file"<<std::endl;
        exit(1);
    }
}
void Producer::SetGeometry(const std::vector< bool >& geometryMask_f)
{
    geometryMask=geometryMask_f;
    no_MPA_light = std::count(geometryMask.begin(), geometryMask.end(), true);
    MaPSAMask.clear();
    MaPSAMask.resize(no_MPA_light);
    #ifndef DEBUG
    std::cout<<"MaPSAMask size "<<MaPSAMask.size()<<std::endl;
    #endif
    this->InitializeHists();
}
void Producer::Print_GeometryMaskMPA()
{
    std::cout<<"Geometry Mask:";    
    for(auto i = 0; i < geometryMask.size(); ++i){
        if(i%3==0)
            std::cout<<"\n";
        std::cout<<geometryMask.at(i)<<"\t";
    }
    std::cout<<std::endl;
//         pixelMask.at(i);
}
void Producer::Print_PixelMaskMPA()
{
    std::cout<<"Global Pixel Mask Serialized:\n";
    bool MPA_GEO_GLOB[COLUMNS*ROWS][ROWS*ASSEMBLY]={};
    int mpa_no = 0;
//     bool MPA_GEO[COLUMNS][ROWS]={0};
    for(auto i = 0; i < geometryMask.size(); ++i){
        if(geometryMask.at(i)){
            auto tmp=MapGeometry(i);
            for(auto j = 0; j < MaPSAMask[mpa_no].size(); ++j){
                auto tmp_cor(MapGlobal(MapCounterLocal(j),tmp.x,tmp.y));
//                 auto tmp_cor(MapCounterLocal(j));
//                 std::cout<<tmp_cor.x<<"-"<<tmp_cor.y<<" ";
                std::cout<<tmp_cor.x<<"-"<<tmp_cor.y<<" ";
                if(MaPSAMask[mpa_no][j]){
                    //                 auto tmp(MapCounterLocal(j));
                    MPA_GEO_GLOB[tmp_cor.x][tmp_cor.y]=true;
                    //                 std::cout<<j<<" ";
                    //                 std::cout<<tmp.x<<" "<<tmp.y<<"  ";
                    //                 std::cout<<tmp.x<<"_"<<tmp.y<<"  ";
                }
                //             else
                //                 std::cout<<"  ";
            }
            mpa_no++;
            std::cout<<"mpa_\n";
        }
    }
    std::cout<<std::endl;
    std::cout<<"Global Pixel Mask:\n";
    for(int j=0; j<ROWS*2; j++){
        for(int i=0; i<COLUMNS*3; i++){
            std::cout<<MPA_GEO_GLOB[i][j]<<" ";
            if((i+1)%16==0 && i>0)
                std::cout<<"  ";
        }
        std::cout<<"\n";
        if((j+1)%ROWS==0 && j>0)
            std::cout<<"\n";
    }
    std::flush(std::cout);
    
}
void Producer::ProduceCluster()
{

}
void Producer::ProduceDQM_Cluster_Hits()
{

}
void Producer::ProduceDQM_Hits()
{

}
void Producer::ProduceGlobalHit()
{

}
Strip_Coordinate Producer::MapCounterLocal(int Channel_f)
{
//         1. Row 3: From Pixel 48 to Pixel 33.
//         2. Row 2: From Pixel 17 to 32.
//         3. Row 1: From Pixel 16 to Pixel 1.
    Strip_Coordinate Hit;
    if(0<=Channel_f && Channel_f<16){
        Hit.y=0;Hit.x=Channel_f;
        return Hit;
    }else if (16<=Channel_f && Channel_f<32){
        Hit.y=1;Hit.x=Channel_f%16;
        return Hit;
    }else if (32<=Channel_f && Channel_f<48){
        Hit.y=2;Hit.x=Channel_f%16;
        return Hit;
    }else{ 
        std::cout<<"no valid loc coordinate\n";
        exit(1);
    }
}
int Producer::MapCounterLocal_X(int Channel_f)
{
//         1. Row 3: From Pixel 48 to Pixel 33.
//         2. Row 2: From Pixel 17 to 32.
//         3. Row 1: From Pixel 16 to Pixel 1.
    if(0<=Channel_f && Channel_f<16){
        return  Channel_f;
    }else if (16<=Channel_f && Channel_f<32){
        return Channel_f%16;
    }else if (32<=Channel_f && Channel_f<48){
        return Channel_f%16;
    }else{ 
        std::cout<<"no valid loc x coordinate\n";
        exit(1);
    }
}
int Producer::MapCounterLocal_Y(int Channel_f)
{
//         1. Row 3: From Pixel 48 to Pixel 33.
//         2. Row 2: From Pixel 17 to 32.
//         3. Row 1: From Pixel 16 to Pixel 1.
    if(0<=Channel_f && Channel_f<16){
        return 0;
    }else if (16<=Channel_f && Channel_f<32){
        return 1;
    }else if (32<=Channel_f && Channel_f<48){
        return 2;
    }else{ 
        std::cout<<"no valid loc coordinate\n";
        exit(1);
    }
}

Strip_Coordinate Producer::MapGlobal(const Strip_Coordinate& LocCoord_f, int MPA_no_x, int MPA_no_y)
{
    //  Asssembly has Max 6 MPA-lights in two rows and three columns
    //  Upper row is flipped
    Strip_Coordinate Glob_Coord;
    if(MPA_no_y==0){
        Glob_Coord.x=LocCoord_f.x+COLUMNS*MPA_no_x;
        Glob_Coord.y=LocCoord_f.y;
        return Glob_Coord;
    }else if(MPA_no_y==1){
        Glob_Coord.x=(COLUMNS-1-LocCoord_f.x)+COLUMNS*MPA_no_x;
        Glob_Coord.y=(ROWS-1-LocCoord_f.y)+MPA_no_y*ROWS;
        return Glob_Coord;
    }else{ 
        std::cout<<"no valid glob coordinate\n";
        exit(1);
    }
}
void Producer::SetFile(const std::string& root_file_f)
{
    
    TFile *file = new TFile(root_file_f.c_str(),"READ");
    if(file->IsZombie()){
        std::cout<<"Error opening file "<<root_file_f<<std::endl;
        exit(1);
    }
    else
        std::cout<<"Process file\t"<<root_file_f<<std::endl;
    
    TTree *tree = (TTree*)file->Get("Tree");
    TTreeReader reader(tree);
// Condition Data
    
//     TTreeReaderValue<unsigned long long> t_COND_NO_MPA_LIGHT(reader, "COND_NO_MPA_LIGHT");
//     TTreeReaderValue<unsigned long long> t_COND_SPILL       (reader, "COND_SPILL");
    TTreeReaderValue<unsigned short> t_COND_THRESHOLD   (reader, "COND_THRESHOLD");
//     TTreeReaderValue<unsigned long long> t_COND_TIMESTAMP   (reader, "COND_TIMESTAMP");
//     TTreeReaderValue<unsigned long long> t_COND_ANGLE       (reader, "COND_ANGLE");
//     TTreeReaderValue<unsigned long long> t_COND_X_POS       (reader, "COND_X_POS");
//     TTreeReaderValue<unsigned long long> t_COND_Y_POS       (reader, "COND_Y_POS");
//     TTreeReaderValue<unsigned long long> t_COND_Z_POS       (reader, "COND_Z_POS");
//     TTreeReaderValue<unsigned long long> t_COND_VOLTAGE     (reader, "COND_VOLTAGE");
    TTreeReaderValue<unsigned int> t_TRIG_COUNTS_SHUTTER      (reader, "TRIG_COUNTS_SHUTTER");
    TTreeReaderValue<unsigned int> t_TRIG_COUNTS_TOTAL_SHUTTER(reader, "TRIG_COUNTS_TOTAL_SHUTTER");
    TTreeReaderValue<unsigned int> t_TRIG_COUNTS_TOTAL        (reader, "TRIG_COUNTS_TOTAL");
    TTreeReaderValue<unsigned int> t_TRIG_OFFSET_BEAM         (reader, "TRIG_OFFSET_BEAM");
    TTreeReaderValue<unsigned int> t_TRIG_OFFSET_MPA          (reader, "TRIG_OFFSET_MPA");
//     if (!CheckValue(t_COND_NO_MPA_LIGHT)) exit(1);
//     if (!CheckValue(t_COND_SPILL)) exit(1);
    if (!CheckValue(t_COND_THRESHOLD)) exit(1);
//     if (!CheckValue(t_COND_TIMESTAMP)) exit(1);
//     if (!CheckValue(t_COND_ANGLE)) exit(1);
//     if (!CheckValue(t_COND_X_POS)) exit(1);
//     if (!CheckValue(t_COND_Y_POS)) exit(1);
//     if (!CheckValue(t_COND_Z_POS)) exit(1);
//     if (!CheckValue(t_COND_VOLTAGE)) exit(1);
    if (!CheckValue(t_TRIG_COUNTS_SHUTTER)) exit(1);
    if (!CheckValue(t_TRIG_COUNTS_TOTAL_SHUTTER)) exit(1);
    if (!CheckValue(t_TRIG_COUNTS_TOTAL)) exit(1);
    if (!CheckValue(t_TRIG_OFFSET_BEAM)) exit(1);
    if (!CheckValue(t_TRIG_OFFSET_MPA)) exit(1);
// // MPA_DATA!
//     std::vector<TTreeReaderValue<RippleCounterBranch_t>> MPA_counter;
//     std::vector<TTreeReaderValue<MemoryNoProcessingBranch_t>> MPA_memory;
    
//     TTreeReaderValue<RippleCounterBranch_t> t_counter1(reader, ("counter_mpa_0"));
    TTreeReaderArray<UShort_t> t_counter0_pixel (reader, ("counter_mpa_0.pixel"));
    TTreeReaderArray<UInt_t>   t_counter0_header(reader, ("counter_mpa_0.header"));
    TTreeReaderArray<UShort_t> t_counter1_pixel (reader, ("counter_mpa_1.pixel"));
    TTreeReaderArray<UInt_t>   t_counter1_header(reader, ("counter_mpa_1.header"));
 
//     TTreeReaderArray<ULong_t>   t_0_MemoryNoProcessing_pixelMatrix(reader,     ("noprocessing_mpa_0.pixels"));
//     TTreeReaderArray<UShort_t>  t_0_MemoryNoProcessing_bunchCrossingId(reader, ("noprocessing_mpa_0.bunchCrossingId"));
//     TTreeReaderArray<UChar_t>   t_0_MemoryNoProcessing_header(reader,          ("noprocessing_mpa_0.header"));
//     TTreeReaderValue<UChar_t>   t_0_MemoryNoProcessing_numEvents(reader,       ("noprocessing_mpa_0.numEvents"));
//     TTreeReaderValue<UChar_t>   t_0_MemoryNoProcessing_corrupt(reader,         ("noprocessing_mpa_0.corrupt"));
// 
//     TTreeReaderArray<ULong64_t> t_1_MemoryNoProcessing_pixelMatrix(reader,     ("noprocessing_mpa_1.pixels"));
//     TTreeReaderArray<UShort_t>  t_1_MemoryNoProcessing_bunchCrossingId(reader, ("noprocessing_mpa_1.bunchCrossingId"));
//     TTreeReaderArray<UChar_t>   t_1_MemoryNoProcessing_header(reader,          ("noprocessing_mpa_1.header"));
//     TTreeReaderValue<UChar_t>   t_1_MemoryNoProcessing_numEvents(reader,       ("noprocessing_mpa_1.numEvents"));
//     TTreeReaderValue<UChar_t>   t_1_MemoryNoProcessing_corrupt(reader,         ("noprocessing_mpa_1.corrupt"));

    
    //     TTreeReaderValue<RippleCounterBranch_t> t_counter2(reader, ("counter_mpa_1"));
//     for(auto i=0; i<no_MPA_light;i++) {
//         TTreeReaderValue<RippleCounterBranch_t> t_counter(reader, ("counter_mpa_"+std::to_string(i)).c_str());
//         TTreeReaderValue<MemoryNoProcessingBranch_t> t_memory(reader, ("noprocessing_mpa_"+std::to_string(i)).c_str());
//         MPA_counter.push_back(t_counter);
//         MPA_memory.push_back(t_memory);
//         if (!CheckValue(t_counter)) exit(1);
//         if (!CheckValue(t_memory)) exit(1);
//     }
#ifndef DEBUG
//     reader.GetTree()->Print();
// auto tree1=reader.GetTree();

    std::cout<<"Processing "<<reader.GetEntries(kTRUE)<<" Events"<<std::endl;
    unsigned int event=0;
    unsigned int counter_hits_per_event=0;
    unsigned int counter_hits_per_event_0=0;
    unsigned int counter_hits_per_event_1=0;
    while (reader.Next()) {
//         std::cout<<"event"<<event<<std::endl;
        //        t_counter1.GetLeaf();
        //        std::cout<<*t_COND_THRESHOLD.Get()<<std::endl;
        //        std::cout<<*t_TRIG_OFFSET_BEAM.Get()<<std::endl;
        //        auto tmp = RippleCounterBranch_t(*MPA_counter.at(0).Get());
        counter_hits_per_event=0;
        counter_hits_per_event_0=0;
        counter_hits_per_event_1=0;
        for(auto i=0; i<CHANNELS; i++){
            //            std::cout<<t_counter1.Get()->pixel[i]<<" ";
            //            std::cout<<t_0_MemoryNoProcessing_pixelMatrix.At(i)<<" ";
            if(t_counter0_pixel.At(i))
            {
                counter_hits_per_event+=t_counter0_pixel.At(i);
                counter_hits_per_event_0+=t_counter0_pixel.At(i);
                hists_1d[0][k_counter_Hits_vs_Channel]->Fill(i+1,(float)t_counter0_pixel.At(i));
                hists_1d[2][k_counter_Hits_vs_Channel]->Fill(i+1,(float)t_counter0_pixel.At(i));
                auto tmp = this->MapCounterLocal(i);
                auto glob= this->MapGlobal(tmp,0,0);
                hists_2d[0][k_counter_Hits_vs_Channel_2d]->Fill(tmp.x+1,tmp.y+1,(float)t_counter0_pixel.At(i));
                hists_2d[2][k_counter_Hits_vs_Channel_2d]->Fill(glob.x+1,glob.y+1,(float)t_counter0_pixel.At(i));
//                 auto tmp=MapCounterLocal(i);
//                 hists_2d[[0]
//                 this->MapGlobal();
//                 this->MapGeometry();
//                 hists_2d[0][k_counter_Hits_vs_Channel_2d]->Fill(
            }
            if(t_counter1_pixel.At(i))
            {
                counter_hits_per_event+=t_counter1_pixel.At(i); 
                counter_hits_per_event_1+=t_counter1_pixel.At(i);
                hists_1d[1][k_counter_Hits_vs_Channel]->Fill(i+1,(float)t_counter1_pixel.At(i));
                hists_1d[2][k_counter_Hits_vs_Channel]->Fill(i+1,(float)t_counter1_pixel.At(i));
                auto tmp = this->MapCounterLocal(i);
                auto glob= this->MapGlobal(tmp,0,1);
                hists_2d[1][k_counter_Hits_vs_Channel_2d]->Fill(tmp.x+1,tmp.y+1,(float)t_counter0_pixel.At(i));
                hists_2d[2][k_counter_Hits_vs_Channel_2d]->Fill(glob.x+1,glob.y+1,(float)t_counter0_pixel.At(i));
            }
        }
        hists_1d[0][k_counter_Hits_per_Event]->Fill(counter_hits_per_event_0);
        hists_1d[1][k_counter_Hits_per_Event]->Fill(counter_hits_per_event_1);
        hists_1d[2][k_counter_Hits_per_Event]->Fill(counter_hits_per_event);
        tgraphs[0][Mapsa_TGraph::TGraph_Hits_vs_Event].SetPoint(event,event,counter_hits_per_event_0);
        tgraphs[1][Mapsa_TGraph::TGraph_Hits_vs_Event].SetPoint(event,event,counter_hits_per_event_1);
        tgraphs[2][Mapsa_TGraph::TGraph_Hits_vs_Event].SetPoint(event,event,counter_hits_per_event);
        ++event;

//         TGraph::SetPoint();
        
        //        std::cout<<std::endl;
        
       
//        for(auto it(t_counter1.begin());it!=t_counter1.end();++it){
//            std::cout<<it.fArray<<" ";
//        }
//            std::cout<<t_counter1<<" ";
//        
   } // TTree entry / event loop
//     tree->Print();/*
//     file->ls();*/
#endif
    file->Close();
}
Strip_Coordinate Producer::MapGeometry ( int MPA_no )
{
    Strip_Coordinate tmp;
    if(0<=MPA_no && MPA_no<3)
    {
        tmp.x=MPA_no;
        tmp.y=0;
    }
    else if (3<=MPA_no && MPA_no<6)
    {
        tmp.x=MPA_no-3;
        tmp.y=1;
    }
    else{
        std::cout<<"MapGeometry: No valid MPA_no given"<<std::endl;
        exit(1);
    }
    return tmp;
}
bool Producer::CheckValue (ROOT::Internal::TTreeReaderValueBase& value)
{
   if (value.GetSetupStatus() != 0 && value.GetSetupStatus() != -7) {
      std::cerr << "Error " << value.GetSetupStatus()
                << "setting up reader for " << value.GetBranchName() << '\n';
      return false;
   }
   return true;
}

void Producer::InitializeHists()
{
    hists_1d.resize((no_MPA_light+1));
    hists_2d.resize((no_MPA_light+1));
    tgraphs.resize((no_MPA_light+1));
    for(int i=0; i<(no_MPA_light+1); i++)
    {
        tgraphs[i].resize(Mapsa_TGraph::TGraph_Cluster_vs_Event+1);
        hists_1d[i].resize(Mapsa_TH1::k_memory_Hits_vs_Timestamp+1);
        hists_2d[i].resize(Mapsa_TH2::k_memory_Hits_vs_Timestamp_2d+1);
        for(int type=0; type<Mapsa_TGraph::TGraph_Cluster_vs_Event+1; ++type){
            tgraphs[i][type]=TGraph();
            tgraphs[i][type].SetTitle(th_title_ax_tgr[type]);
        }
        for(int type=0; type<Mapsa_TH1::k_memory_Hits_vs_Timestamp+1; ++type)
        {
            std::cout<<i<<type<<"\t"<<TString(th_names[type])+"_counter_mpa_"+std::to_string(i).c_str()<<std::endl;
            if(i<(no_MPA_light))
            {
                if(type!=k_memory_Hits_vs_Timestamp){
                    hists_1d[i][type] = new TH1F(TString(th_names[type])+"_mpa_"+std::to_string(i).c_str(),
                                                 TString(th_title_ax[type])+"_mpa_"+std::to_string(i).c_str()
                                                 ,CHANNELS,.5,CHANNELS+.5);
                }else{
                    hists_1d[i][type] = new TH1F(TString(th_names[type])+"_mpa_"+std::to_string(i).c_str(),
                                                 TString(th_title_ax[type])+"_mpa_"+std::to_string(i).c_str(),
                                                 TIMESTAMP_RANGE,.5,TIMESTAMP_RANGE+.5);
                }
            } 
            if(i==no_MPA_light){
                if(type!=k_memory_Hits_vs_Timestamp){
                    hists_1d[i][type] = new TH1F(TString(th_names[type])+"_glob",
                                                 TString(th_title_ax[type])+"_glob",
                                                 CHANNELS*no_MPA_light,.5,CHANNELS*no_MPA_light+.5);
                }else{
                    hists_1d[i][type] = new TH1F(TString(th_names[type])+"_glob",
                                                 TString(th_title_ax[type])+"_glob",
                                                 TIMESTAMP_RANGE,.5,TIMESTAMP_RANGE+.5);
                }
            }
        }
        if(i<(no_MPA_light))
        {
            hists_2d[i][Mapsa_TH2::k_counter_Hits_vs_Channel_2d] = new TH2F(TString(th_names[Mapsa_TH1::k_counter_Hits_vs_Channel])+"_mpa_"+std::to_string(i).c_str(),
                                                 TString(th_title_ax[Mapsa_TH1::k_counter_Hits_vs_Channel])+"_mpa_"+std::to_string(i).c_str()
                                                 ,COLUMNS,.5,COLUMNS+.5,ROWS,.5,ROWS+.5);
            hists_2d[i][Mapsa_TH2::k_counter_Centroid_Cluster_2d] = new TH2F(TString(th_names[Mapsa_TH1::k_counter_Centroid_Cluster])+"_mpa_"+std::to_string(i).c_str(),
                                                 TString(th_title_ax[Mapsa_TH1::k_counter_Centroid_Cluster])+"_mpa_"+std::to_string(i).c_str()
                                                 ,COLUMNS,.5,COLUMNS+.5,ROWS,.5,ROWS+.5);
            hists_2d[i][Mapsa_TH2::k_memory_Hits_vs_Channel_2d] = new TH2F(TString(th_names[Mapsa_TH1::k_memory_Hits_vs_Channel])+"_mpa_"+std::to_string(i).c_str(),
                                                 TString(th_title_ax[Mapsa_TH1::k_memory_Hits_vs_Channel])+"_mpa_"+std::to_string(i).c_str(),
                                                 COLUMNS,.5,COLUMNS+.5,ROWS,.5,ROWS+.5);
            hists_2d[i][Mapsa_TH2::k_memory_Hits_vs_Timestamp_2d] = new TH2F(TString(th_names[Mapsa_TH1::k_memory_Hits_vs_Timestamp])+"_mpa_"+std::to_string(i).c_str(),
                                                 TString(th_title_ax[Mapsa_TH1::k_memory_Hits_vs_Timestamp])+"_mpa_"+std::to_string(i).c_str(),
                                                 TIMESTAMP_RANGE,.5,TIMESTAMP_RANGE+.5,CHANNELS,.5,CHANNELS+.5);
        } 
        if(i==no_MPA_light){
            hists_2d[i][Mapsa_TH2::k_counter_Hits_vs_Channel_2d] = new TH2F(TString(th_names[Mapsa_TH1::k_counter_Hits_vs_Channel])+"_glob"+std::to_string(i).c_str(),
                                                 TString(th_title_ax[Mapsa_TH1::k_counter_Hits_vs_Channel])+"_glob"+std::to_string(i).c_str()
                                                 ,COLUMNS*ROWS,.5,COLUMNS*ROWS+.5,ROWS*ASSEMBLY,.5,ROWS*ASSEMBLY+.5);
            hists_2d[i][Mapsa_TH2::k_counter_Centroid_Cluster_2d] = new TH2F(TString(th_names[Mapsa_TH1::k_counter_Centroid_Cluster])+"_glob"+std::to_string(i).c_str(),
                                                 TString(th_title_ax[Mapsa_TH1::k_counter_Centroid_Cluster])+"_glob"+std::to_string(i).c_str()
                                                 ,COLUMNS*ROWS,.5,COLUMNS*ROWS+.5,ROWS*ASSEMBLY,.5,ROWS*ASSEMBLY+.5);
            hists_2d[i][Mapsa_TH2::k_memory_Hits_vs_Channel_2d] = new TH2F(TString(th_names[Mapsa_TH1::k_memory_Hits_vs_Channel])+"_glob"+std::to_string(i).c_str(),
                                                 TString(th_title_ax[Mapsa_TH1::k_memory_Hits_vs_Channel])+"_glob"+std::to_string(i).c_str(),
                                                 COLUMNS*ROWS,.5,COLUMNS*ROWS+.5,ROWS*ASSEMBLY,.5,ROWS*ASSEMBLY+.5);
            hists_2d[i][Mapsa_TH2::k_memory_Hits_vs_Timestamp_2d] = new TH2F(TString(th_names[Mapsa_TH1::k_memory_Hits_vs_Timestamp])+"_glob"+std::to_string(i).c_str(),
                                                 TString(th_title_ax[Mapsa_TH1::k_memory_Hits_vs_Timestamp])+"_glob"+std::to_string(i).c_str(),
                                                 TIMESTAMP_RANGE,.5,TIMESTAMP_RANGE+.5,CHANNELS*ASSEMBLY,.5,CHANNELS*ASSEMBLY+.5);
        }
    }
//     for(const auto& i:hists_1d)
//     {
//         for(const auto& j: i)
//             Map.Add(j);
// //             std::cout<<j->GetName()<<j->GetTitle()<<j->GetXaxis()->GetTitle()<<std::endl;
//     }
}
// This is called after one run is completely analyzed
void Producer::SaveResetHists(const std::string& in_file_f)
{
//     Make a new dir for each run and save the files in the directory
    prod_root_file->mkdir(in_file_f.c_str());
//  Make a new dir in for each MPA and Global and Save histos
    for(auto i=0; i<no_MPA_light+1; i++){
        prod_root_file->cd(in_file_f.c_str());
        char buffer [50];
        if(i<no_MPA_light){
            std::snprintf ( buffer, 50, "MPA_%d", i );
        }else{
            std::snprintf ( buffer, 50, "Global");
        }
        gDirectory->mkdir(buffer);
        gDirectory->cd(buffer);
        gDirectory->mkdir("th1");
        gDirectory->cd("th1");
        for(const auto& j: hists_1d[i])
        {
            j->Write();
            j->SetDirectory(0);
            j->Reset();
        }
        gDirectory->cd("..");
        gDirectory->mkdir("th2");
        gDirectory->cd("th2");
        for(const auto& j: hists_2d[i])
        {
            j->Write();
            j->SetDirectory(0);
            j->Reset();
        }
        gDirectory->cd("..");
        gDirectory->mkdir("tgraph");
        gDirectory->cd("tgraph");
        for(auto& j: tgraphs[i])
        {
            j.Write(j.GetTitle());
            j.Set(0);
        }
    }        
}
void Producer::DeleteHists()
{
//     Map.DeleteAll();
    for(const auto& i:hists_1d)
    {
        for(const auto& j: i)
        {
//             j->Write();
            delete j;
        }
        //             std::cout<<j->GetName()<<j->GetTitle()<<j->GetXaxis()->GetTitle()<<std::endl;
    }
    for(const auto& i:hists_2d)
    {
        for(const auto& j: i)
        {
//             j->Write();
            delete j;
        }
        //             std::cout<<j->GetName()<<j->GetTitle()<<j->GetXaxis()->GetTitle()<<std::endl;
    }
}
void Producer::RecreateRootFile(const std::string& prod_root_file_f)
{
    prod_root_file =new TFile(prod_root_file_f.c_str(),"RECREATE");
}

}