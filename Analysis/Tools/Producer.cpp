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
                GeometryInfo.push_back(tmp);
                std::cout<<tmp.x<<"-"<<tmp.y<<" Pushed_back";
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
        //     Find cluster in rows
        std::cout<<"pixelmatrix"<<std::endl;
        for(auto j=0; j<ROWS; j++){
            for(auto i=0; i<COLUMNS; i++){
                std::cout<<Pixel_Matrix_Arr[i][j];
            }
            std::cout<<std::endl;
        }
        std::cout<<std::endl;
        //    Two pass connected component labeling
        std::vector<std::set<unsigned int>> linked;
        unsigned short NextLabel=1;
        bool neighbours_empty=true;
        unsigned short LabelMin=0;
        for(auto j=0; j<ROWS; j++){
            for(auto i=0; i<COLUMNS; i++){
                if(Pixel_Matrix_Arr[i][j])
                {
                    std::cout<<"Hit at: "<<i<<"-"<<j<<"\n";
                    //                 std::cout<<"Pixel: "<<i<<j<<"\t";
                    neighbours_empty=true;
                    switch (GetCase(j,i)) {
                        case MaskCases::corner_upper_left:
                            neighbours_empty=true;
                            break;
                        case MaskCases::limit_top:
                            if(Pixel_Matrix_Arr[i-1][j])
                            {
                                neighbours_empty=false;
                                //                             LabelMin=std::min({Pixel_Matrix_Labels[i-1][j]});
                                if(Pixel_Matrix_Labels[i-1][j]>0)
                                    Pixel_Matrix_Labels[i][j]=Pixel_Matrix_Labels[i-1][j];
                                std::set<unsigned int>::iterator it;
                                std::cout<<"size"<<std::endl;
                                std::cout<<linked.size()<<std::endl;
                                if(linked.size()==0){
                                    std::set<unsigned int> tmp;
                                    tmp.insert(NextLabel);
                                    linked.push_back(tmp);
                                    NextLabel++;
                                }
                                linked.at(Pixel_Matrix_Labels[i-1][j]).insert(Pixel_Matrix_Labels[i-1][j]);
                                for (it=linked.at(LabelMin).begin(); it!=linked.at(LabelMin).end(); ++it)
                                    std::cout << ' ' << *it;
                                std::cout << '\n';
                            }
                            //                         std::cout << "\tlimit_top";
                            break;
                        default:
                            if(Pixel_Matrix_Arr[i-1][j] || Pixel_Matrix_Arr[i][j-1])
                            {
                                neighbours_empty=false;
                                LabelMin=std::min({Pixel_Matrix_Labels[i-1][j],Pixel_Matrix_Labels[i][j-1]});
                                if(LabelMin>0)
                                    Pixel_Matrix_Labels[i][j]=LabelMin;
                                std::set<unsigned int>::iterator it;
                                std::cout<<"size"<<std::endl;
                                std::cout<<linked.size()<<std::endl;
                                if(linked.size()==0){
                                    std::set<unsigned int> tmp;
                                    tmp.insert(NextLabel);
                                    linked.push_back(tmp);
                                    NextLabel++;
                                }
                                linked.at(Pixel_Matrix_Labels[i-1][j]).insert(Pixel_Matrix_Labels[i-1][j]);
                                linked.at(Pixel_Matrix_Labels[i][j-1]).insert(Pixel_Matrix_Labels[i][j-1]);
                                for (it=linked.at(LabelMin).begin(); it!=linked.at(LabelMin).end(); ++it)
                                    std::cout << ' ' << *it;
                                std::cout << '\n';
                            }
                            //                         std::cout << "\tno_edge";
                            break;
                    }
                    if(neighbours_empty)
                    {
                        std::set<unsigned int> tmp_set;
                        tmp_set.insert(NextLabel);
                        //                     std::vector<unsigned int> tmp_set;
                        //                     tmp_set.push_back(NextLabel);
                        //                     linked.resize(NextLabel);
                        linked.emplace_back(tmp_set);
                        Pixel_Matrix_Labels[i][j]=NextLabel;
                        std::cout<<"neighbours_empty "<<NextLabel<<std::endl;
                        NextLabel++;
                    }else {
                        std::cout<<"linked.at(LabelMin)"<<LabelMin<<std::endl;
                        //                     std::cout<<"linked.at(LabelMin)"<<linked[0][0]<<std::endl;
                        //                     std::ostream_iterator< int > output( std::cout, " " );
                        //                     std::copy(linked.at(LabelMin).begin(), linked.at(LabelMin).end(), output );
                        //                     for label in L
                        //                        linked[label] = union(linked[label], L)
                    }
                    std::cout<<"Labels\n";
                    for(auto j1=0; j1<ROWS; j1++)
                    {
                        for(auto i1=0; i1<COLUMNS; i1++)
                        {
                            std::cout<<Pixel_Matrix_Labels[i1][j1];
                        }
                        std::cout<<std::endl;
                    }
                }
            }
        }
        //     std::cout<<std::endl;
    }
    MaskCases Producer::GetCase(int x, int y)
    {
        if(x>0 && y>0 && x<(ROWS-1) && y<(COLUMNS-1))
            return MaskCases::no_edge;
        else if(x==0 && y>0 && y<(COLUMNS-1))
            return MaskCases::limit_top;
        else if(x==(ROWS-1) && y>0 && y<(COLUMNS-1))
            return MaskCases::limit_bottom;
        else if(x>0 && y==0 && x<(ROWS-1))
            return MaskCases::limit_left;
        else if(x>0 && y==(COLUMNS-1) && x<(ROWS-1))
            return MaskCases::limit_right;
        else if(x==0 && y==0)
            return MaskCases::corner_upper_left;
        else if(x==0 && y==(COLUMNS-1))
            return MaskCases::corner_upper_right;
        else if(x==(ROWS-1) && y==(COLUMNS-1))
            return MaskCases::corner_lower_right;
        else if(x==(ROWS-1) && y==0)
            return MaskCases::corner_lower_left;
        else
            std::cout<<"Did not provide a valid case for GetCase"<<std::endl;
        exit(1);
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
    Strip_Coordinate Producer::MapMemoryLocal(int Channel_f)
    {
        Strip_Coordinate Hit;
        if(0<=Channel_f && Channel_f<16){
            Hit.y=2;Hit.x=15-Channel_f;
            return Hit;
        }else if (16<=Channel_f && Channel_f<32){
            Hit.y=1;Hit.x=Channel_f%16;
            return Hit;
        }else if (32<=Channel_f && Channel_f<48){
            Hit.y=0;Hit.x=15-(Channel_f%16);
            return Hit;
        }else{ 
            std::cout<<"no valid loc coordinate\n";
            exit(1);
        }
    }
    int Producer::MapMemoryLocal_X(int Channel_f)
    {
        return 0;
    }
    int Producer::MapMemoryLocal_Y(int Channel_f)
    {
        return 0;
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
    void Producer::SetFile(const std::string& root_file_f, Counter& counter)
    {
        TFile *file = new TFile(root_file_f.c_str(),"READ");
        if(file->TObject::IsZombie()){
            std::cout<<"Error opening file "<<root_file_f<<std::endl;
            exit(1);
        }
        else
            std::cout<<"Process file\t"<<root_file_f<<std::endl;
        TTree* const tree = static_cast<TTree* const>(file->TDirectoryFile::Get("Tree"));
        MemoryNoProcessingBranch_t memory_arr[ASSEMBLY];
        RippleCounterBranch_t ripplecounter_arr[ASSEMBLY];
        for(int i=0; i<ASSEMBLY; i++)
        {
            auto tmp_mem    = MemoryNoProcessingBranch_t();
            auto tmp_ripple = RippleCounterBranch_t();
            memory_arr[i]=tmp_mem;
            ripplecounter_arr[i]=tmp_ripple;
        }
        tree->SetBranchAddress("noprocessing_mpa_2",&memory_arr[0]);
        tree->SetBranchAddress("noprocessing_mpa_5",&memory_arr[1]);
        tree->SetBranchAddress("counter_mpa_2",&ripplecounter_arr[0]);
        tree->SetBranchAddress("counter_mpa_5",&ripplecounter_arr[1]);
        
        unsigned long long     t_COND_NO_MPA_LIGHT;
        unsigned long long            t_COND_SPILL;
        //         unsigned short            t_COND_THRESHOLD;
        int                 t_COND_THRESHOLD;
        //         ULong64_t                 t_COND_THRESHOLD;
        unsigned long long        t_COND_TIMESTAMP;
        int            t_COND_ANGLE;
        int            t_COND_X_POS;
        int            t_COND_Y_POS;
        int            t_COND_Z_POS;
        int          t_COND_VOLTAGE;
        int         t_TRIG_COUNTS_SHUTTER;
        int   t_TRIG_COUNTS_TOTAL_SHUTTER;
        int           t_TRIG_COUNTS_TOTAL;
        int            t_TRIG_OFFSET_BEAM;
        int             t_TRIG_OFFSET_MPA;
        
        //     tree->SetBranchAddress("COND_NO_MPA_LIGHT",&t_COND_NO_MPA_LIGHT);
        //     tree->SetBranchAddress("COND_SPILL",&t_COND_SPILL);
        tree->SetBranchAddress("COND_THRESHOLD",&t_COND_THRESHOLD);
        //     tree->SetBranchAddress("COND_TIMESTAMP",&t_COND_TIMESTAMP);
        tree->SetBranchAddress("COND_ANGLE",&t_COND_ANGLE);
        tree->SetBranchAddress("COND_X_POS",&t_COND_X_POS);
        tree->SetBranchAddress("COND_Y_POS",&t_COND_Y_POS);
        tree->SetBranchAddress("COND_Z_POS",&t_COND_Z_POS);
        tree->SetBranchAddress("COND_VOLTAGE",&t_COND_VOLTAGE);
        tree->SetBranchAddress("TRIG_COUNTS_SHUTTER",&t_TRIG_COUNTS_SHUTTER);
        tree->SetBranchAddress("TRIG_COUNTS_TOTAL_SHUTTER",&t_TRIG_COUNTS_TOTAL_SHUTTER);
        tree->SetBranchAddress("TRIG_COUNTS_TOTAL",&t_TRIG_COUNTS_TOTAL);
        tree->SetBranchAddress("TRIG_OFFSET_BEAM",&t_TRIG_OFFSET_BEAM);
        tree->SetBranchAddress("TRIG_OFFSET_MPA",&t_TRIG_OFFSET_MPA);
        #ifndef DEBUG
        //     reader.GetTree()->Print();
        // auto tree1=reader.GetTree();
        
        std::cout<<"Processing "<<tree->GetEntries()<<" Events"<<std::endl;
        unsigned int event=0;
        unsigned int counter_hits_per_event=0;
        unsigned int counter_hits_per_event_0=0;
        unsigned int counter_hits_per_event_1=0;
        int nEntries = tree->GetEntries(); // Get the number of entries in this tree
        int cut_low =10;
        int cut_up=10;
        int lower =( nEntries-cut_low> 0) ? cut_low : 0;
        int upper =( nEntries-cut_up> 0) ? (nEntries-cut_up) : nEntries;
        for (int event = 0; event< nEntries; event++) {
//         for (int event = 0; event< 100; event++) {
            tree->GetEntry(event);
            //     while (reader.Next()) {
            //         Conditions
//             Reset all the arrays
            ResetMemoryEfficiency();
            if(event==0)
            {
                //             counter.angle      = t_COND_ANGLE;
                //             counter.no_events  = ;
                counter.no_shutter = tree->GetEntries();
                //             counter.pos_x      = t_COND_X_POS;
                //             counter.pos_y      = t_COND_Y_POS;
                //             counter.pos_z      = t_COND_Z_POS;
                counter.threshold  = t_COND_THRESHOLD;
                std::cout<<"Threshold"<<counter.threshold<<std::endl;
                //             counter.timestamp  =;
                //             counter.voltage = t_COND_VOLTAGE;
            }
            counter_hits_per_event=0;
            counter_hits_per_event_0=0;
            counter_hits_per_event_1=0;
            for(auto i=0; i<CHANNELS; i++){
                if(ripplecounter_arr[0].pixel[i])
                {
                    counter_hits_per_event+=ripplecounter_arr[0].pixel[i];
                    counter_hits_per_event_0+=ripplecounter_arr[0].pixel[i];
                    auto tmp = this->MapCounterLocal(i);
                    auto glob= this->MapGlobal(tmp,this->GeometryInfo.at(0).x-1,this->GeometryInfo.at(0).y);
                    Counter_Pixel_Matrix[glob.x][glob.y]+=(float)ripplecounter_arr[0].pixel[i];
                    if(event>lower && event<upper)
                    {
                        hists_1d[0][k_counter_Hits_vs_Channel]->Fill(i+1,(float)ripplecounter_arr[0].pixel[i]);
                        hists_1d[2][k_counter_Hits_vs_Channel]->Fill(i+1,(float)ripplecounter_arr[0].pixel[i]);
                        hists_2d[0][k_counter_Hits_vs_Channel_2d]->Fill(tmp.x+1,tmp.y+1,(float)ripplecounter_arr[0].pixel[i]);
                        hists_2d[2][k_counter_Hits_vs_Channel_2d]->Fill(glob.x+1,glob.y+1,(float)ripplecounter_arr[0].pixel[i]);
                    }
                }
                if(ripplecounter_arr[1].pixel[i])
                {
                    counter_hits_per_event+=ripplecounter_arr[1].pixel[i]; 
                    counter_hits_per_event_1+=ripplecounter_arr[1].pixel[i];
                    auto tmp = this->MapCounterLocal(i);
                    auto glob= this->MapGlobal(tmp,this->GeometryInfo.at(1).x-1,this->GeometryInfo.at(1).y);
                    Counter_Pixel_Matrix[glob.x][glob.y]+=(float)ripplecounter_arr[1].pixel[i];
                    if(event>lower && event<upper)
                    {
                    hists_1d[1][k_counter_Hits_vs_Channel]->Fill(i+1,(float)ripplecounter_arr[1].pixel[i]);
                    hists_1d[2][k_counter_Hits_vs_Channel]->Fill(i+1+CHANNELS,(float)ripplecounter_arr[1].pixel[i]);
                    hists_2d[1][k_counter_Hits_vs_Channel_2d]->Fill(tmp.x+1,tmp.y+1,(float)ripplecounter_arr[1].pixel[i]);
                    hists_2d[2][k_counter_Hits_vs_Channel_2d]->Fill(glob.x+1,glob.y+1,(float)ripplecounter_arr[1].pixel[i]);
                    }
                }
            }
            if(event>lower && event<upper)
            {
                hists_1d[0][k_counter_Hits_per_Event]->Fill(counter_hits_per_event_0);
                hists_1d[1][k_counter_Hits_per_Event]->Fill(counter_hits_per_event_1);
                hists_1d[2][k_counter_Hits_per_Event]->Fill(counter_hits_per_event);
                this->FillMemoryHists(memory_arr[0],0);
                this->FillMemoryHists(memory_arr[1],1);
                GetMemoryEfficiency(counter_hits_per_event);
            }
            tgraphs[0][Mapsa_TGraph::TGraph_Hits_vs_Event].SetPoint(event,event,counter_hits_per_event_0);
            tgraphs[1][Mapsa_TGraph::TGraph_Hits_vs_Event].SetPoint(event,event,counter_hits_per_event_1);
            tgraphs[2][Mapsa_TGraph::TGraph_Hits_vs_Event].SetPoint(event,event,counter_hits_per_event);
            if(event%500==0)
//                 std::cout<<"Progress:\t"<<std::setprecision(3)<<100*(float)(event)/(float)(nEntries)<<" % of\t "<<nEntries<<" events \r"<<std::flush;
                std::cout<<"Progress:\t"<<std::setw(5)<<std::setprecision(1)<<std::fixed<<100*(float)(event)/(float)(nEntries)<<" % of\t "<<nEntries<<" events \r"<<std::flush;
        }
        std::cout<<std::endl;
        #endif
        // counter.mean_centroid_cluster =hists_1d[2][Mapsa_TH1::k_counter_Centroid_Cluster]->GetMean(0);
        // counter.mean_cluster          =hists_1d[2][Mapsa_TH1::k_counter_Cluster_per_Event]->GetMean(0);
        // counter.mean_clustersize      =hists_1d[2][]->GetMean(0);
        counter.mean_hits             =hists_1d[2][Mapsa_TH1::k_counter_Hits_per_Event]->GetMean(1);
        // counter.stdev_centroid_cluster=hists_1d[2][Mapsa_TH1::k_counter_Centroid_Cluster]->GetStdDev(0);
        // counter.stdev_cluster         =hists_1d[2][Mapsa_TH1::k_counter_Cluster_per_Event]->GetStdDev(0);
        // counter.stdev_clustersize     =hists_1d[2][]->GetStdDev(0);
        counter.stdev_hits            =hists_1d[2][Mapsa_TH1::k_counter_Hits_per_Event]->GetStdDev(1);
        for(auto i=0; i<(CHANNELS*ASSEMBLY+2); i++){
            counter.pixel_counter[i]=hists_1d[2][Mapsa_TH1::k_counter_Hits_vs_Channel]->GetBinContent(i);
            counter.pixel_memory[i]=hists_1d[2][Mapsa_TH1::k_memory_Hits_vs_Channel]->GetBinContent(i);
            //     counter.pixel_memory[i]=hists_1d[2][Mapsa_TH1::k_memory_Hits_vs_Channel]->GetBinContent(i);
        }
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
            hists_1d[i].resize(Mapsa_TH1::k_memory_Hits_vs_Timestamp+1);
            hists_2d[i].resize(Mapsa_TH2::k_memory_Hits_vs_Timestamp_2d+1);
            tgraphs[i].resize(Mapsa_TGraph::TGraph_Cluster_vs_Event+1);
            for(int type=0; type<Mapsa_TGraph::TGraph_Cluster_vs_Event+1; ++type){
                tgraphs[i][type]=TGraph();
                tgraphs[i][type].SetTitle(th_title_ax_tgr[type]);
            }
            for(int type=0; type<Mapsa_TH1::k_memory_Hits_vs_Timestamp+1; ++type)
            {
                if(i<(no_MPA_light))
                {
                    if(type==Mapsa_TH1::k_memory_Hits_vs_Timestamp || type==Mapsa_TH1::k_memory_TDC_specrum){
//                         std::cout<<i<<"\t"<<type<<"\t"<<TString(th_names[type])+"_mpa_"+std::to_string(i).c_str()<<std::endl;
                        hists_1d[i][type] = new TH1F(TString(th_names[type])+"_mpa_"+std::to_string(i).c_str(),
                                                     TString(th_title_ax[type])+"_mpa_"+std::to_string(i).c_str(),
                                                     TIMESTAMP_RANGE,.5,TIMESTAMP_RANGE+.5);
                    }else if(type==Mapsa_TH1::k_memory_vs_counter_Efficiency)
                    {
//                         std::cout<<i<<"\t"<<type<<"\t"<<TString(th_names[type])+"_mpa_"+std::to_string(i).c_str()<<std::endl;
                        hists_1d[i][type] = new TH1F(TString(th_names[type])+"_mpa_"+std::to_string(i).c_str(),
                                                     TString(th_title_ax[type])+"_mpa_"+std::to_string(i).c_str()
                                                     ,2,-.5,1.5);
                    }else
                    {
//                         std::cout<<i<<"\t"<<type<<"\t"<<TString(th_names[type])+"_mpa_"+std::to_string(i).c_str()<<std::endl;
                        hists_1d[i][type] = new TH1F(TString(th_names[type])+"_mpa_"+std::to_string(i).c_str(),
                                                     TString(th_title_ax[type])+"_mpa_"+std::to_string(i).c_str()
                                                     ,CHANNELS+1,-.5,CHANNELS+.5);
                    }
                }
                if(i==no_MPA_light){
                    if(type==Mapsa_TH1::k_memory_Hits_vs_Timestamp || type==Mapsa_TH1::k_memory_TDC_specrum){
                        hists_1d[i][type] = new TH1F(TString(th_names[type])+"_glob",
                                                     TString(th_title_ax[type])+"_glob",
                                                     TIMESTAMP_RANGE,.5,TIMESTAMP_RANGE+.5);
                    }else if(type==Mapsa_TH1::k_memory_vs_counter_Efficiency)
                    {
//                         std::cout<<i<<"\t"<<type<<"\t"<<TString(th_names[type])+"_glob"+std::to_string(i).c_str()<<std::endl;
                        hists_1d[i][type] = new TH1F(TString(th_names[type])+"_glob",
                                                     TString(th_title_ax[type])+"_glob"
                                                     ,2,-.5,1.5);
                    }else
                    {
                        hists_1d[i][type] = new TH1F(TString(th_names[type])+"_glob",
                                                     TString(th_title_ax[type])+"_glob",
                                                     CHANNELS*no_MPA_light+1,-.5,CHANNELS*no_MPA_light+.5);
                    }
                }
            }
            if(i<(no_MPA_light))
            {
                hists_2d[i][Mapsa_TH2::k_counter_Hits_vs_Channel_2d] = new TH2I(TString(th_names_2d[Mapsa_TH2::k_counter_Hits_vs_Channel_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                                TString(th_title_ax_2d[Mapsa_TH2::k_counter_Hits_vs_Channel_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                                COLUMNS,.5,COLUMNS+.5,ROWS,.5,ROWS+.5);
                hists_2d[i][Mapsa_TH2::k_counter_Centroid_Cluster_2d] = new TH2I(TString(th_names_2d[Mapsa_TH2::k_counter_Centroid_Cluster_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                                 TString(th_title_ax_2d[Mapsa_TH2::k_counter_Centroid_Cluster_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                                 COLUMNS,.5,COLUMNS+.5,ROWS,.5,ROWS+.5);
                hists_2d[i][Mapsa_TH2::k_memory_Hits_vs_Channel_2d] = new TH2I(TString(th_names_2d[Mapsa_TH2::k_memory_Hits_vs_Channel_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                               TString(th_title_ax_2d[Mapsa_TH2::k_memory_Hits_vs_Channel_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                               COLUMNS,.5,COLUMNS+.5,ROWS,.5,ROWS+.5);
                hists_2d[i][Mapsa_TH2::k_memory_Centroid_Cluster_2d] = new TH2I(TString(th_names_2d[Mapsa_TH2::k_memory_Centroid_Cluster_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                                TString(th_title_ax_2d[Mapsa_TH2::k_memory_Centroid_Cluster_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                                COLUMNS,.5,COLUMNS+.5,ROWS,.5,ROWS+.5);
                hists_2d[i][Mapsa_TH2::k_counter_counter_cor_2d] = new TH2I(TString(th_names_2d[Mapsa_TH2::k_counter_counter_cor_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                                TString(th_title_ax_2d[Mapsa_TH2::k_counter_counter_cor_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                                COLUMNS*ROWS,-.5,COLUMNS*ROWS-.5,COLUMNS*ROWS,-.5,COLUMNS*ROWS-.5);
                hists_2d[i][Mapsa_TH2::k_memory_counter_cor_2d] = new TH2I(TString(th_names_2d[Mapsa_TH2::k_memory_counter_cor_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                                TString(th_title_ax_2d[Mapsa_TH2::k_memory_counter_cor_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                                COLUMNS*ROWS,-.5,COLUMNS*ROWS-.5,COLUMNS*ROWS,-.5,COLUMNS*ROWS-.5);
                hists_2d[i][Mapsa_TH2::k_memory_Hits_vs_Timestamp_2d] = new TH2I(TString(th_names_2d[Mapsa_TH2::k_memory_Hits_vs_Timestamp_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                                 TString(th_title_ax_2d[Mapsa_TH2::k_memory_Hits_vs_Timestamp_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                                 TIMESTAMP_RANGE,.5,TIMESTAMP_RANGE+.5,CHANNELS,.5,CHANNELS+.5);
            } 
            if(i==no_MPA_light){
                hists_2d[i][Mapsa_TH2::k_counter_Hits_vs_Channel_2d] = new TH2I(TString(th_names_2d[Mapsa_TH2::k_counter_Hits_vs_Channel_2d])+"_glob",
                                                                                TString(th_title_ax_2d[Mapsa_TH2::k_counter_Hits_vs_Channel_2d])+"_glob",
                                                                                COLUMNS,.5,COLUMNS+.5,ROWS*ASSEMBLY,.5,ROWS*ASSEMBLY+.5);
                hists_2d[i][Mapsa_TH2::k_counter_Centroid_Cluster_2d] = new TH2I(TString(th_names_2d[Mapsa_TH2::k_counter_Centroid_Cluster_2d])+"_glob",
                                                                                 TString(th_title_ax_2d[Mapsa_TH2::k_counter_Centroid_Cluster_2d])+"_mpa_"+std::to_string(i).c_str(),
                                                                                 COLUMNS,.5,COLUMNS+.5,ROWS*ASSEMBLY,.5,ROWS*ASSEMBLY+.5);
                hists_2d[i][Mapsa_TH2::k_memory_Hits_vs_Channel_2d] = new TH2I(TString(th_names_2d[Mapsa_TH2::k_memory_Hits_vs_Channel_2d])+"_glob",
                                                                               TString(th_title_ax_2d[Mapsa_TH2::k_memory_Hits_vs_Channel_2d])+"_glob",
                                                                               COLUMNS,.5,COLUMNS+.5,ROWS*ASSEMBLY,.5,ROWS*ASSEMBLY+.5);
                hists_2d[i][Mapsa_TH2::k_counter_counter_cor_2d] = new TH2I(TString(th_names_2d[Mapsa_TH2::k_counter_counter_cor_2d])+"_glob",
                                                                                TString(th_title_ax_2d[Mapsa_TH2::k_counter_counter_cor_2d])+"_glob",
                                                                                COLUMNS*ROWS*ASSEMBLY,-.5,COLUMNS*ROWS*ASSEMBLY-.5,COLUMNS*ROWS*ASSEMBLY,-.5,COLUMNS*ROWS*ASSEMBLY-.5);
                hists_2d[i][Mapsa_TH2::k_memory_counter_cor_2d] = new TH2I(TString(th_names_2d[Mapsa_TH2::k_memory_counter_cor_2d])+"_glob",
                                                                                TString(th_title_ax_2d[Mapsa_TH2::k_memory_counter_cor_2d])+"_glob",
                                                                                COLUMNS*ROWS*ASSEMBLY,-.5,COLUMNS*ROWS*ASSEMBLY-.5,COLUMNS*ROWS*ASSEMBLY,-.5,COLUMNS*ROWS*ASSEMBLY-.5);
                hists_2d[i][Mapsa_TH2::k_memory_Centroid_Cluster_2d] = new TH2I(TString(th_names_2d[Mapsa_TH2::k_memory_Centroid_Cluster_2d])+"_glob",
                                                                                TString(th_title_ax_2d[Mapsa_TH2::k_memory_Centroid_Cluster_2d])+"_glob",
                                                                                COLUMNS,.5,COLUMNS+.5,ROWS*ASSEMBLY,.5,ROWS*ASSEMBLY+.5);
                hists_2d[i][Mapsa_TH2::k_memory_Hits_vs_Timestamp_2d] = new TH2I(TString(th_names_2d[Mapsa_TH2::k_memory_Hits_vs_Timestamp_2d])+"_glob",
                                                                                 TString(th_title_ax_2d[Mapsa_TH2::k_memory_Hits_vs_Timestamp_2d])+"_glob",
                                                                                 TIMESTAMP_RANGE,.5,TIMESTAMP_RANGE+.5,CHANNELS,.5,CHANNELS+.5);
            }
        }
    }
    // This is called after one run is completely analyzed
    void Producer::SaveResetHists(const std::string& in_file_f, const std::string& path)
    {
        std::string tmp(path);
        tmp+=in_file_f;tmp+=".root";
        RecreateRootFile(tmp);
        //     Make a new dir for each run and save the files in the directory
//         prod_root_file->mkdir(in_file_f.c_str());
        //  Make a new dir in for each MPA and Global and Save histos
        for(auto i=0; i<no_MPA_light+1; i++){
//             prod_root_file->cd(in_file_f.c_str());
            prod_root_file->cd();
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
        prod_root_file->Close();
        //     return 0;
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
        std::cout<<"Write to file "<<prod_root_file_f<<std::endl;
        this->prod_root_file =new TFile(prod_root_file_f.c_str(),"RECREATE");
        //     prod_root_file =new TFile("test_1.root","RECREATE");
    }
    void Producer::FillMemoryHists(const MemoryNoProcessingBranch_t& MemoryNoProcessingBranch, int MPA_no)
    {
        //     MemoryNoProcessingBranch.bunchCrossingId;
        //     MemoryNoProcessingBranch.corrupt;
        //     MemoryNoProcessingBranch.header;
        //     MemoryNoProcessingBranch.numEvents;
        //     MemoryNoProcessingBranch.pixelMatrix;
        //     MemoryNoProcessingBranch.bunchCrossingId;
        unsigned int hits_per_event=0;
        Strip_Coordinate strip_cor;
        Strip_Coordinate glob;
        for(auto i=0; i<MEMORY; i++){
//             ResetPixelMatrix();
            hits_per_event=0;
            for(auto j=0; j<CHANNELS; j++){
                if(MemoryNoProcessingBranch.pixelMatrix[i] >> j & 1){
                    //                 std::cout<<"1";
                    hits_per_event++;
                    strip_cor=MapMemoryLocal(j);
                    glob=MapGlobal(strip_cor,GeometryInfo.at(MPA_no).x-1,GeometryInfo.at(MPA_no).y);
                    Pixel_Matrix_Arr[strip_cor.x][strip_cor.y]=1;
                    Memory_Pixel_Matrix[glob.x][glob.y]+=1;
                    hists_1d[MPA_no][Mapsa_TH1::k_memory_Hits_vs_Channel]->Fill(j+1);
                    hists_1d[2][Mapsa_TH1::k_memory_Hits_vs_Channel]->Fill(j+MPA_no*CHANNELS+1);
                    hists_2d[MPA_no][Mapsa_TH2::k_memory_Hits_vs_Channel_2d]->Fill(strip_cor.x+1,strip_cor.y+1);
                    hists_2d[2][Mapsa_TH2::k_memory_Hits_vs_Channel_2d]->Fill(glob.x+1,glob.y+1);
                }
            }
            hists_1d[MPA_no][Mapsa_TH1::k_memory_Hits_per_Event]->Fill(hits_per_event);
            if(i>0)
                hists_1d[MPA_no][Mapsa_TH1::k_memory_TDC_specrum]->Fill(MemoryNoProcessingBranch.bunchCrossingId[i]-MemoryNoProcessingBranch.bunchCrossingId[i-1]);
            hists_1d[2][Mapsa_TH1::k_memory_TDC_specrum]->Fill(std::abs(MemoryNoProcessingBranch.bunchCrossingId[i]-MemoryNoProcessingBranch.bunchCrossingId[i-1]));
            hists_1d[MPA_no][Mapsa_TH1::k_memory_Hits_vs_Timestamp]->Fill(MemoryNoProcessingBranch.bunchCrossingId[i],hits_per_event);
            hists_1d[2][Mapsa_TH1::k_memory_Hits_vs_Timestamp]->Fill(MemoryNoProcessingBranch.bunchCrossingId[i],hits_per_event);
            //             if(hits_per_event>1){
            //                 ProduceCluster();
            //             }
        }
    }
    void Producer::ResetPixelMatrix()
    {
        for(auto i=0; i<COLUMNS; i++){
            Pixel_Matrix_Arr[i].fill(0);
            Pixel_Matrix_Labels[i].fill(0);
        }
    }
    void Producer::ResetMemoryEfficiency()
    {
        for(auto i=0; i<COLUMNS; i++){
            Counter_Pixel_Matrix[i].fill(0);
            Memory_Pixel_Matrix[i].fill(0);
        }
    }
    void Producer::GetMemoryEfficiency(unsigned int total_counter_hits)
    {
        int memory_hit=0;
        bool inefficient_memory=true;
        for(auto j=0; j<COLUMNS; j++){
            for(auto i=0; i<ROWS*ASSEMBLY; i++){
                for(auto j1=0; j1<COLUMNS; j1++){
                    for(auto i1=0; i1<ROWS*ASSEMBLY; i1++){
                        if(Counter_Pixel_Matrix[i][j]!=0 && Memory_Pixel_Matrix[i1][j1]!=0)
                        {
                            hists_2d[2][Mapsa_TH2::k_memory_counter_cor_2d]->Fill(j*ROWS*ASSEMBLY+i, j1*ROWS*ASSEMBLY+i1);
//                             if(Counter_Pixel_Matrix[i][j]==1)
//                                 hists_2d[2][Mapsa_TH2::k_memory_counter_eff_2d]->Fill(j*ROWS*ASSEMBLY+i, j1*ROWS*ASSEMBLY+i);
                            if(total_counter_hits==1)
                            {
                                hists_1d[2][Mapsa_TH1::k_memory_vs_counter_Efficiency]->Fill(1);
                                inefficient_memory=false;
                            }
                        }
                        if(Counter_Pixel_Matrix[i][j]!=0 && Counter_Pixel_Matrix[i1][j1]!=0)
                            hists_2d[2][Mapsa_TH2::k_counter_counter_cor_2d]->Fill(j*ROWS*ASSEMBLY+i, j1*ROWS*ASSEMBLY+i1);
                    }
                }
            }
        }
        if(inefficient_memory=true && total_counter_hits==1)
            hists_1d[2][Mapsa_TH1::k_memory_vs_counter_Efficiency]->Fill(0);
    }
}