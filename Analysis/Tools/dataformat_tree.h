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

static constexpr int MEMORY=96;
static constexpr int CHANNELS=48;
static constexpr int COLUMNS=16;
static constexpr int ROWS=3;
static constexpr int ASSEMBLY=2;
static constexpr int TIMESTAMP_RANGE=65536;
static constexpr int THRESHOLD_RANGE=256;

static constexpr float PITCH_STD__X=100E-6;
static constexpr float PITCH_EDGE_X=200E-6;
static constexpr float PITCH_STD_Y=1746E-6;
static constexpr float PITCH_STD_EDGE_Y=1446E-6;
// Weights for COG calculation
static constexpr float WEIGHT_DEFAULT=1446;
static constexpr float WEIGHT_STD_EDGE=2892;
static constexpr float WEIGHT_LOWER_ROW=1746;
static constexpr float WEIGHT_LOWER_CORNER=3492;

static constexpr float LOWER_ROW=873E-6;
static constexpr float ROW_1=1446E-6;
static constexpr float ROW_2=2892E-6;



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
     Float_t cog_x;
     Float_t cog_y;
     Float_t area;
     UShort_t size_x;
     UShort_t size_y;
     UShort_t clustersize;
     Int_t Chip_Position_Mask;
     Int_t IntraChipPosition;
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
