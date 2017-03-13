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
//     tree->Print();
    TTreeReader reader(tree);
//     reader.GetTree()->Print();
// // Condition Data
    
//     unsigned long t_COND_NO_MPA_LIGHT=0;
//     unsigned long t_COND_SPILL       =0;
//     unsigned long t_COND_THRESHOLD   =0;
//     unsigned long t_COND_TIMESTAMP   =0;
//     unsigned long t_COND_ANGLE       =0;
//     unsigned long t_COND_X_POS       =0;
//     unsigned long t_COND_Y_POS       =0;
//     unsigned long t_COND_Z_POS       =0;
//     unsigned long t_COND_VOLTAGE     =0;
//     unsigned long t_TRIG_COUNTS_SHUTTER      =0;
//     unsigned long t_TRIG_COUNTS_TOTAL_SHUTTER=0;
//     unsigned long t_TRIG_COUNTS_TOTAL        =0;
//     unsigned long t_TRIG_OFFSET_BEAM         =0;
//     unsigned long t_TRIG_OFFSET_MPA          =0;
    TTreeReaderValue<unsigned long long> t_COND_NO_MPA_LIGHT(reader, "COND_NO_MPA_LIGHT");
    TTreeReaderValue<unsigned long long> t_COND_SPILL       (reader, "COND_SPILL");
    TTreeReaderValue<unsigned long long> t_COND_THRESHOLD   (reader, "COND_THRESHOLD");
    TTreeReaderValue<unsigned long long> t_COND_TIMESTAMP   (reader, "COND_TIMESTAMP");
    TTreeReaderValue<unsigned long long> t_COND_ANGLE       (reader, "COND_ANGLE");
    TTreeReaderValue<unsigned long long> t_COND_X_POS       (reader, "COND_X_POS");
    TTreeReaderValue<unsigned long long> t_COND_Y_POS       (reader, "COND_Y_POS");
    TTreeReaderValue<unsigned long long> t_COND_Z_POS       (reader, "COND_Z_POS");
    TTreeReaderValue<unsigned long long> t_COND_VOLTAGE     (reader, "COND_VOLTAGE");
    TTreeReaderValue<unsigned long long> t_TRIG_COUNTS_SHUTTER      (reader, "TRIG_COUNTS_SHUTTER");
    TTreeReaderValue<unsigned long long> t_TRIG_COUNTS_TOTAL_SHUTTER(reader, "TRIG_COUNTS_TOTAL_SHUTTER");
    TTreeReaderValue<unsigned long long> t_TRIG_COUNTS_TOTAL        (reader, "TRIG_COUNTS_TOTAL");
    TTreeReaderValue<unsigned long long> t_TRIG_OFFSET_BEAM         (reader, "TRIG_OFFSET_BEAM");
    TTreeReaderValue<unsigned long long> t_TRIG_OFFSET_MPA          (reader, "TRIG_OFFSET_MPA");
    if (!CheckValue(t_COND_NO_MPA_LIGHT)) exit(1);
    if (!CheckValue(t_COND_SPILL)) exit(1);
    if (!CheckValue(t_COND_THRESHOLD)) exit(1);
    if (!CheckValue(t_COND_TIMESTAMP)) exit(1);
    if (!CheckValue(t_COND_ANGLE)) exit(1);
    if (!CheckValue(t_COND_X_POS)) exit(1);
    if (!CheckValue(t_COND_Y_POS)) exit(1);
    if (!CheckValue(t_COND_Z_POS)) exit(1);
    if (!CheckValue(t_COND_VOLTAGE)) exit(1);
    if (!CheckValue(t_TRIG_COUNTS_SHUTTER)) exit(1);
    if (!CheckValue(t_TRIG_COUNTS_TOTAL_SHUTTER)) exit(1);
    if (!CheckValue(t_TRIG_COUNTS_TOTAL)) exit(1);
    if (!CheckValue(t_TRIG_OFFSET_BEAM)) exit(1);
    if (!CheckValue(t_TRIG_OFFSET_MPA)) exit(1);
// // MPA_DATA!
//     std::vector<TTreeReaderValue<RippleCounterBranch_t>> MPA_counter;
//     std::vector<TTreeReaderValue<MemoryNoProcessingBranch_t>> MPA_memory;
    TTreeReaderArray<RippleCounterBranch_t> t_counter1(reader, ("counter_mpa_0"));
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

// std::cout<<"Processing "<<reader.GetEntries(kTRUE)<<" Events"<<std::endl;
   while (reader.Next()) {
//        std::cout<<*t_COND_THRESHOLD.Get()<<std::endl;
//        std::cout<<*t_TRIG_OFFSET_BEAM.Get()<<std::endl;
//        auto tmp = RippleCounterBranch_t(*MPA_counter.at(0).Get());
       for(auto i=0; i<CHANNELS; i++){
           std::cout<<t_counter1.At(i).pixels<<" ";
       }
       std::cout<<std::endl;
           
       
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


}