cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
project(bt_analysis)
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_CXX_STANDARD 11)
# set(CMAKE_BUILD_TYPE Debug)
# set(CMAKE_BUILD_TYPE Release)

list(APPEND CMAKE_PREFIX_PATH $ENV{ROOTSYS})
# MESSAGE( STATUS "CMAKE_PREFIX_PATH:         " ${CMAKE_PREFIX_PATH} )
# MESSAGE( STATUS "CMAKE_MODULE_PATH:         " ${CMAKE_MODULE_PATH} )

find_package (Threads REQUIRED)
find_package(Boost COMPONENTS program_options filesystem REQUIRED )
find_package(ROOT REQUIRED COMPONENTS MathCore RIO Net Hist Tree TreePlayer RooFit REQUIRED)

message(${ROOT_INCLUDE_DIRS})
message(${Boost_VERSION})

# include(${ROOT_USE_FILE})

message (${ROOT_USE_FILE})

add_subdirectory(Tools)

if(Boost_FOUND)
message(${CMAKE_SOURCE_DIR})
include_directories(  ${Boost_INCLUDE_DIR} ${ROOT_INCLUDE_DIRS})
add_executable(clusterproducer main.cpp)
# target_link_libraries(clusterproducer LINK_PUBLIC   ${ROOT_LIBRARIES} ${Boost_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT} Producer dataformat_tree)
target_link_libraries(clusterproducer LINK_PUBLIC dataformat_tree Producer  ${ROOT_LIBRARIES} ${Boost_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
# target_link_libraries(roottest LINK_PUBLIC my ${ROOT_LIBRARIES} ${Boost_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
endif()


install(TARGETS clusterproducer RUNTIME DESTINATION bin)