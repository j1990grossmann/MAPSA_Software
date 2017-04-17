/*
 * A ClusterProducer Class for the MapsaLight Test System
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

#ifndef PRODUCER_H
#define PRODUCER_H

#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

#include "Riostream.h"
#include "TApplication.h"
#include "TArray.h"
#include "TArrayI.h"
// #include "TAttLine.h"
// #include "TAttMarker.h"
// #include "TAxis.h"
#include "TBits.h"
// #include "TCanvas.h"
// #include "TClass.h"
// #include "TColor.h"
// #include "TDirectory.h"
// #include "TExec.h"
// #include "TF1.h"
// #include "TF2.h"
#include "TFile.h"
// #include "TFormula.h"
// #include "TGaxis.h"
// #include "TGraphErrors.h"
#include "TGraph.h"
#include "TH1.h"
#include "TH2.h"
// #include "TKey.h"
// #include "TLatex.h"
// #include "TLegend.h"
// #include "TList.h"
// #include "TMath.h"
// #include "TMultiGraph.h"
// #include "TObject.h"
// #include "TPad.h"
#include "TProcPool.h"
#include "TRandom3.h"
#include "TROOT.h"
#include "TROOT.h"
#include "TString.h"
// #include "TStyle.h"
#include "TSystem.h"
#include "TTree.h"
#include "TTreeReader.h"
#include "TTreeReaderValue.h"
#include "TTreeReaderArray.h"
#include "TMap.h"
#include "TObject.h"
#include "TDirectoryFile.h"

// TTreeReaderValueArray
// #include "TTreeReaderValueArray.h"
// #include "TTreeReaderValueBase.h"

#include "dataformat_tree.h"
#include "Scan.h"

namespace PRODUCER{
    //     struct RippleCounterBranch_t{
    //             UShort_t pixels[CHANNELS];
    //     };
    enum Mapsa_TH1{
        k_counter_Hits_per_Event,
        k_counter_Cluster_per_Event,
        k_counter_Hits_vs_Channel,
        k_counter_Hits_vs_Row,
        k_counter_Centroid_Cluster,
        k_memory_Hits_per_Event,
        k_memory_Cluster_per_Event,
        k_memory_Hits_vs_Channel,
        k_memory_Hits_vs_Row,
        k_memory_Centroid_Cluster,
        k_memory_vs_counter_Efficiency,
        k_memory_TDC_specrum,
        k_memory_Hits_vs_Timestamp
    };
    static const char* th_names[] = {
        "Counter_Hits_per_Event"   , 
        "Counter_Cluster_per_Event",
        "Counter_Hits_vs_Channel"  ,
        "Counter_Hits_vs_Row"      ,
        "Counter_Centroid_Cluster" , 
        "Memory_Hits_per_Event"   , 
        "Memory_Cluster_per_Event",
        "Memory_Hits_vs_Channel"  ,
        "Memory_Hits_vs_Row"      ,
        "Memory_Centroid_Cluster" ,
        "Memory_Counter_Efficiency" ,
        "Memory_TDC_spectrum"     ,
        "Memory_Hits_vs_Timestamp"  
    };
    static const char* th_title_ax[] = {
        "Counter Hits; # Hits; # Events; "     , 
        "Counter Clusters; # Events; # Clusters",
        "Counter Hits; # Channel; # Hits"       ,
        "Counter Hits; # Row;  # Hits; "        ,
        "Counter Centroids; #Centroid_Clusters; #Event",
        "Memory Hits; # Hits; # Events; "     , 
        "Memory Clusters; # Events; # Clusters",
        "Memory Hits; # Channel; # Hits"       ,
        "Memory Hits; # Row;  # Hits; "        ,
        "Memory Centroids; #Centroid_Clusters; #Event",
        "Memory vs Counter Efficiency; Counts; Efficiency",
        "#DeltaT; #DeltaT (25ns); Counts"    ,
        "Hits; Timestamp (25ns); #Hits"
    };
    enum Mapsa_TH2{
        k_counter_Hits_vs_Channel_2d,
        k_counter_Centroid_Cluster_2d,
        k_memory_Hits_vs_Channel_2d,
        k_memory_Centroid_Cluster_2d,
        k_counter_counter_cor_2d,
        k_memory_counter_cor_2d,
        k_memory_Hits_vs_Timestamp_2d
    };
    static const char* th_names_2d[] = {
        "Counter_Hits_vs_Channel_2D"  ,
        "Counter_Centroid_Cluster_2D" , 
        "Memory_Hits_vs_Channel_2D"  ,
        "Memory_Centroid_Cluster_2D" , 
        "Counter_Counter_Corr_2D" , 
        "Memory_Counter_Corr_Eff_2D" , 
        "Memory_Hits_vs_Timestamp_2D"
    };
    static const char* th_title_ax_2d[] = {
        "Counter_Hits_vs_Channel_2D ; Column; Row",
        "Counter_Centroid_Cluster_2D; Column; Row",
        "Memory_Hits_vs_Channel_2D  ; Column; Row",
        "Memory_Centroid_Cluster_2D ; Column; Row",
        "Counter_Counter_Corr_2D ; Counter Channel #; Counter Channel #",
        "Memory_Counter_Corr_Eff_2D ; Counter; Memory",
        "Memory_Hits_vs_Timestamp_2D; t(25ns), #Channel"
    };
    enum Mapsa_TGraph{
        TGraph_Hits_vs_Event,
        TGraph_Cluster_vs_Event
    };
    static const char* th_title_ax_tgr[] = {
        "Counter Hits Graph   ; # Events; # Hits",
        "Counter Cluster Graph; # Events; # Cluster"
    }; 
    enum MaskCases: unsigned char{
        no_edge = 0,
        limit_top = 1,
        limit_bottom = 2,
        limit_right  = 4,
        limit_left   = 8,
        corner_upper_left=16,
        corner_upper_right=32,
        corner_lower_left=64,
        corner_lower_right=128
    };
    enum class MapsaMask{
        Mapsa_2 = 1,
        Mapsa_5 = 2
    };
    struct LocalHitCor 
    {
        float  x;
        float  y;
        float  area;
    };
    struct Strip_Coordinate
    {
        //         unsigned char  x;
        //         unsigned char  y;
        unsigned int x;
        unsigned int y;
    };
    struct Loc_Strip_Coordinate
    {
        //         unsigned char  x;
        //         unsigned char  y;
        UShort_t x;
        UShort_t y;
    };
    struct GlobalClusterHit 
    {
        double  x;
        double  y;
    };
    struct Counter_Event{
        std::vector<LocalHitCor> Hits;
        std::vector<GlobalClusterHit> Clusters;
        std::vector<GlobalClusterHit> CMS_Clusters;
    };
    struct Memory_Event{
        std::vector<LocalHitCor> Hits;
        std::vector<GlobalClusterHit> Clusters;
        std::vector<GlobalClusterHit> CMS_Clusters;
        std::vector<unsigned short> BX_ID;
        std::vector<unsigned char>  Header;
        std::vector<unsigned char>  NumEvents;
    };
    struct CounterCluster{
        Float_t cog_x;
        Float_t cog_y;
        Float_t size_x;
        Float_t size_y;
        UShort_t clustersize;
        Short_t Chip_Position_Mask;
        Short_t IntraChipPosition;
    };
    struct MemoryCluster{
        Float_t cog_x;
        Float_t cog_y;
        UShort_t size_x;
        UShort_t size_y;
        UShort_t clustersize;
        Int_t Chip_Position_Mask;
        Int_t IntraChipPosition;
        unsigned short BX_ID;
    };
    class Producer
    {
    public:
        Producer(const std::string& prod_root_file_f):
        //         This have to be set before Construction
        geometryMask({ true,false,false,true, false, false }),
        pixelMask(CHANNELS, true),
        MaPSAMask(ASSEMBLY,pixelMask),
        no_MPA_light(0),
        Pixel_Matrix_Arr({{0}}),
        Pixel_Matrix_Labels({{0}})
        {
            ROOT::EnableThreadSafety();
            //          ResetPixelMatrix();
        }
        ~Producer()
        {
            DeleteHists();
            prod_root_file->Close();
        };
        
        Strip_Coordinate GetStripCoordinate(int channel, int mpa_no);
        LocalHitCor GetHitCoordinate(const unsigned x, const MaskCases mask);
        
        void SetGeometry(const std::vector<bool>& geometryMask_f);
        void Set_PixelMaskMPA(int MPA_no, const std::vector<bool>& pixelMask_f);
        void Print_GeometryMaskMPA();
        void Print_PixelMaskMPA();
        void SetFile(const std::string& root_file_f, Counter& counter);
        void SaveResetHists(const std::string& in_file_f, const std::string& path);
        
        void ProduceGlobalHit();
        
        void ProduceDQM_Hits();
        void ProduceDQM_Cluster_Hits();
        
    private:
        
        //         Geometry information
        std::array<std::array<unsigned short, ROWS+2>, COLUMNS+2> Pixel_Matrix_Arr;
        std::array<std::array<unsigned short, ROWS+2>, COLUMNS+2> Pixel_Matrix_Labels;
        
        std::array<std::array<unsigned short, ROWS*ASSEMBLY>, COLUMNS> Counter_Pixel_Matrix;
        std::array<std::array<unsigned short, ROWS*ASSEMBLY>, COLUMNS> Memory_Pixel_Matrix;
        std::vector<std::set<unsigned int>> f_linked;

        //         unsigned short Pixel_Matrix_Arr[COLUMNS][ROWS];
        //         unsigned short Pixel_Matrix_Labels[COLUMNS][ROWS];
        
        int no_MPA_light;
        std::vector<bool> pixelMask;
        std::vector<bool> geometryMask;
        std::vector<std::vector<bool>> MaPSAMask;
        std::vector<PRODUCER::Strip_Coordinate> GeometryInfo;
        
        std::vector<std::string> histos;
        std::vector<std::vector<TH1*> >   hists_1d;
        std::vector<std::vector<TH2*> >   hists_2d;
        std::vector<std::vector<TGraph> > tgraphs;
        TFile* prod_root_file;
        
        std::vector<GlobalClusterHit> Event_GlobalClusterHit_vec;
        std::vector<LocalHitCor>        Event_GlobalHit_vec;
        
        std::vector<GlobalClusterHit> GlobalClusterHit_vec;
        std::vector<LocalHitCor>        GlobalHit_vec;
        TMap Map;
        
        Strip_Coordinate MapCounterLocal(int Channel_f);
        int MapCounterLocal_X(int Channel_f);
        int MapCounterLocal_Y(int Channel_f);
        
        Strip_Coordinate MapMemoryLocal(int Channel_f);
        int MapMemoryLocal_X(int Channel_f);
        int MapMemoryLocal_Y(int Channel_f);
        
        
        Strip_Coordinate MapGlobal(const Strip_Coordinate& LocCoord_f,int MPA_no_x, int MPA_no_y);
        int MapGlobal_X(const Strip_Coordinate& LocCoord_f,int MPA_no_x, int MPA_no_y);
        int MapGlobal_Y(const Strip_Coordinate& LocCoord_f,int MPA_no_x, int MPA_no_y);
        
        Strip_Coordinate MapGeometry(int MPA_no);
        
        
        bool CheckValue(ROOT::Internal::TTreeReaderValueBase& value);
        void InitializeHists();
        void FillCounterHists_Run();
        void FillMemoryHists_Run();
        void DeleteHists();
        void RecreateRootFile(const std::string& prod_root_file_f);
        void FillMemoryHists(const MemoryNoProcessingBranch_t& MemoryNoProcessingBranch, int MPA_no);
        void ResetPixelMatrix();
        void ResetMemoryEfficiency();
        void GetMemoryEfficiency(unsigned int total_counter_hits);
        void ProduceCluster(int MPA_no, int hits_per_event, UShort_t BX_ID);
        MaskCases GetCase(int x, int y);
        
        
    protected:
    };
}
#endif // PRODUCER_H
