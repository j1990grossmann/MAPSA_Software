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

#include "TROOT.h"
static constexpr int MEMORY=96;
static constexpr int CHANNELS=48;
static constexpr int COLUMNS=16;
static constexpr int ROWS=3;
static constexpr int ASSEMBLY=3;

namespace PRODUCER{
    
    struct MemoryNoProcessingBranch_t 
    {
        ULong64_t       pixelMatrix[MEMORY];
        UShort_t        bunchCrossingId[MEMORY];
        UChar_t         header[MEMORY];
        UChar_t         numEvents;
        UChar_t         corrupt;
    };
    struct GlobalHit 
    {
        double  x;
        double  y;
    };
    struct Strip_Coordinate
    {
//         unsigned char  x;
//         unsigned char  y;
        unsigned int x;
        unsigned int y;
    };
    struct GlobalClusterHit 
    {
        double  x;
        double  y;
    };
    struct Counter_Event{
        std::vector<GlobalHit> Hits;
        std::vector<GlobalClusterHit> Clusters;
        std::vector<GlobalClusterHit> CMS_Clusters;
    };
    struct Memory_Event{
        std::vector<GlobalHit> Hits;
        std::vector<GlobalClusterHit> Clusters;
        std::vector<GlobalClusterHit> CMS_Clusters;
        std::vector<unsigned short> BX_ID;
        std::vector<unsigned char>  Header;
        std::vector<unsigned char>  NumEvents;
    };
    class Producer
    {
    public:
        Producer():
//         This have to be set before Construction
        geometryMask({ true,false,false,true, false, false }),
        pixelMask(CHANNELS, true),
        MaPSAMask(ASSEMBLY,pixelMask)
        {
        }
        Strip_Coordinate GetStripCoordinate(int channel, int mpa_no);
        GlobalHit GetHitCoordinate(Strip_Coordinate);
        
        void SetGeometry(const std::vector<bool>& geometryMask_f);
        void Set_PixelMaskMPA(int MPA_no, const std::vector<bool>& pixelMask_f);
        void Print_GeometryMaskMPA();
        void Print_PixelMaskMPA();
        void SetFile(const std::string& root_file_f);
        
        void ProduceGlobalHit();
        void ProduceCluster();
        void ProduceDQM_Hits();
        void ProduceDQM_Cluster_Hits();
    private:
//         Geometry information
        std::vector<bool> pixelMask;
        std::vector<bool> geometryMask;
        std::vector<std::vector<bool>> MaPSAMask;

        std::vector<uint64_t> counter_channels;
        std::vector<uint64_t> memory_channels;

        std::vector<GlobalClusterHit> Event_GlobalClusterHit_vec;
        std::vector<GlobalHit>        Event_GlobalHit_vec;

        std::vector<GlobalClusterHit> GlobalClusterHit_vec;
        std::vector<GlobalHit>        GlobalHit_vec;
        
        Strip_Coordinate MapCounterLocal(int Channel_f);
        Strip_Coordinate MapGlobal(const Strip_Coordinate& LocCoord_f,int MPA_no_x, int MPA_no_y);
        
    protected:
    };
}
#endif // PRODUCER_H
