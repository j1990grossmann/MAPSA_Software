#ifndef DATAFORMAT_TREE_H
#define DATAFORMAT_TREE_H

// c++
#include <iostream>
#include <sstream>
#include <fstream>
#include <set>
#include <vector>

// Root
#include "TObject.h"
#include "TMath.h"

static const int MEMORY=96;
static const int CHANNELS=48;
static const int COLUMNS=16;
static const int ROWS=3;
static const int ASSEMBLY=2;
static const int TIMESTAMP_RANGE=65536;
static const int THRESHOLD_RANGE=256;

static const float PITCH_STD__X=100;
static const float PITCH_EDGE_X=200;
static const float PITCH_STD_Y=1746;
static const float PITCH_STD_EDGE_Y=1446;
// Weights for COG calculation
static const float WEIGHT_DEFAULT=144600;
static const float WEIGHT_STD_EDGE=289200;
static const float WEIGHT_LOWER_ROW=174600;
static const float WEIGHT_LOWER_CORNER=349200;

static const float LOWER_ROW=873;
static const float ROW_1=1446;
static const float ROW_2=2892;



// 
struct MemoryNoProcessingBranch_t {
   ULong64_t       pixelMatrix[MEMORY];
   UShort_t        bunchCrossingId[MEMORY];
   UChar_t         header[MEMORY];
   UChar_t         numEvents;
   UChar_t         corrupt;
};


struct RippleCounterBranch_t{
 UInt_t   header;
 UShort_t pixel[CHANNELS];
};
//! my_utilities class
class MemoryCluster: public TObject {
 public:
     float cog_x;
     float cog_y;
     float area;
     unsigned int size_x;
     unsigned int size_y;
     unsigned int clustersize;
     int Chip_Position_Mask;
     int IntraChipPosition;
     unsigned short BX_ID;
     std::set<unsigned int> x_pixel;
     std::set<unsigned int> y_pixel;
  //! my_utilities constructor
  MemoryCluster():
  cog_x(0),
  cog_y(0),
  area(0),
  size_x(0),
  size_y(0),
  clustersize(0),
  Chip_Position_Mask(0),
  IntraChipPosition(0),
  BX_ID(0)
  {};
  ~MemoryCluster(){};
  ClassDef(MemoryCluster,1)
};
// class MemoryClusterVec: public TObject {
//  public:
//      std::vector<MemoryCluster> ClusterVec;
//   //! my_utilities constructor
//   MemoryClusterVec()
//   {
//       this->ClusterVec=std::vector<MemoryCluster>({});
//   };
//   ~MemoryClusterVec(){};
//   ClassDef(MemoryClusterVec,1)
// };
// ClassDef(std::vector<MemoryCluster>,1)

class CounterCluster: public TObject {
 public:
     Float_t cog_x;
     Float_t cog_y;
     Float_t size_x;
     Float_t size_y;
     UShort_t clustersize;
     Short_t Chip_Position_Mask;
     Short_t IntraChipPosition;

  //! my_utilities constructor
  CounterCluster():
  cog_x(0),
  cog_y(0),
  size_x(0),
  size_y(0),
  clustersize(0),
  Chip_Position_Mask(0),
  IntraChipPosition(0)
  {};
  ~CounterCluster(){};
  ClassDef(CounterCluster,1)
};
#endif // MY_UTILITIES_H
