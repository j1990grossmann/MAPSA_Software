#ifndef DATAFORMAT_TREE_H
#define DATAFORMAT_TREE_H

// c++
#include <iostream>
#include <sstream>
#include <fstream>

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
// class MemoryNoProcessingBranch: public TObject {
//  public:
//    ULong64_t       pixelMatrix[MEMORY];
//    UShort_t        bunchCrossingId[MEMORY];
//    UChar_t         header[MEMORY];
//    UChar_t         numEvents;
//    UChar_t         corrupt;
//   //! my_utilities constructor
//   MemoryNoProcessingBranch();
//   //! my_utilities destructor
//   ~MemoryNoProcessingBranch();
// 
//   //! my return
// //   Float_t myReturn(Float_t input);
//   
//   ClassDef(MemoryNoProcessingBranch,1)  
// 
// };
// class RippleCounterBranch: public TObject {
// public:
//  UInt_t   header;
//  UShort_t pixel[CHANNELS];
//   //! my_utilities constructor
//  RippleCounterBranch();
//   //! my_utilities destructor
//  ~RippleCounterBranch();
// 
//   //! my return
// //   Float_t myReturn(Float_t input);
//   
//  ClassDef(RippleCounterBranch,1)  
// 
// };
#endif // MY_UTILITIES_H
