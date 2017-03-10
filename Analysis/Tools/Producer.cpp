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
void Producer::Set_PixelMaskMPA(int MPA_no, const std::vector< bool >& pixelMask)
{

}
void Producer::SetGeometry(const std::vector< bool >& geometryMask_f)
{
    geometryMask=geometryMask_f;
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
    bool MPA_GEO_GLOB[COLUMNS*3][ROWS*2]={0};
    for(auto i = 0; i < MaPSAMask.size(); ++i){
//         bool MPA_GEO[COLUMNS][ROWS]={0};
        for(auto j = 0; j < MaPSAMask[i].size(); ++j){
//             if(MaPSAMask[i][j]){
                auto tmp(MapGlobal(MapCounterLocal(j),i%2,0));
//                 MPA_GEO_GLOB[tmp.x][tmp.y]=true;
//                 std::cout<<j<<" ";
                std::cout<<tmp.x<<" "<<tmp.y<<"  ";
//             }
//             else
//                 std::cout<<"  ";
        }
            std::cout<<"mpa_\n";
    }
    std::cout<<std::endl;
    std::cout<<"Global Pixel Mask:\n";
    for(int j=0; j<ROWS*2; j++){
        for(int i=0; i<COLUMNS*3; i++){
            std::cout<<MPA_GEO_GLOB[i][j]<<" ";
            if(i%16==0 && i>0)
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
        Glob_Coord.x=LocCoord_f.x+CHANNELS*MPA_no_x;
        Glob_Coord.y=LocCoord_f.y;
        return Glob_Coord;
    }else if(MPA_no_y==1){
        Glob_Coord.x=(COLUMNS-1-LocCoord_f.x)+CHANNELS*MPA_no_x;
        Glob_Coord.y=(ROWS-1-LocCoord_f.y)+MPA_no_y;
        return Glob_Coord;
    }else{ 
        std::cout<<"no valid glob coordinate\n";
        exit(1);
    }
}
void Producer::SetFile(const std::__cxx11::string& root_file_f)
{

}


}