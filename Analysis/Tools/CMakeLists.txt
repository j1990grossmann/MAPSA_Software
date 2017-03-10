find_package (Threads REQUIRED)
find_package(ROOT REQUIRED COMPONENTS MathCore RIO Net Hist Tree TreePlayer RooFit REQUIRED)

include_directories(${ROOT_INCLUDE_DIRS})

add_library (Producer Producer.cpp)
target_include_directories (Producer PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
