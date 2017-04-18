find_package (Threads REQUIRED)
find_package(ROOT REQUIRED COMPONENTS MathCore RIO Net Hist Tree TreePlayer RooFit REQUIRED)

include_directories(${ROOT_INCLUDE_DIRS})

include_directories(${CMAKE_CURRENT_SOURCE_DIR})
include(${ROOT_USE_FILE})
ROOT_GENERATE_DICTIONARY(dataformat_treelib_Dict dataformat_tree.h LINKDEF dataformat_tree_LinkDef.h)

add_library(dataformat_tree SHARED dataformat_tree.cpp dataformat_treelib_Dict.cxx)
target_link_libraries(dataformat_tree ${ROOT_LIBRARIES})
# target_link_libraries(roottest my ${ROOT_LIBRARIES})
add_library (Scan Scan.cpp)
target_include_directories (Scan PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

add_library (Producer Producer.cpp)
target_include_directories (Producer PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries( Producer dataformat_tree ${ROOT_LIBRARIES})


set(lib_thread_pool
    ThreadPool.cpp
)

add_library(ThreadPool SHARED ${lib_thread_pool})
# add_library (ThreadPool SHARED ThreadPool.h)
target_include_directories (ThreadPool PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})


# message("TEST" ${ROOT_USE_FILE})
