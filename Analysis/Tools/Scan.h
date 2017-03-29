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

#ifndef SCAN_H
#define SCAN_H

#include <thread>
#include <iostream>
#include <vector>
#include <mutex>

#include "dataformat_tree.h"

struct Counter {
    unsigned int threshold;
    unsigned int no_shutter;
    unsigned int no_events;
    float timestamp;
    float angle;
    float pos_x;
    float pos_y;
    float pos_z;
    float voltage;
    float mean_hits;
    float stdev_hits;
    float mean_cluster;
    float stdev_cluster;
    float mean_clustersize;
    float stdev_clustersize;
    float mean_centroid_cluster;
    float stdev_centroid_cluster;
    float pixel_counter[CHANNELS*ASSEMBLY+2];
    float pixel_memory[CHANNELS*ASSEMBLY+2];
    

    Counter() : 
    threshold(0),
    no_shutter(0),
    no_events(0),
    timestamp(0),
    angle(0),
    pos_x(0),
    pos_y(0),
    pos_z(0),
    voltage(0),
    mean_hits(0),
    stdev_hits(0),
    mean_cluster(0),
    stdev_cluster(0),
    mean_clustersize(0),
    stdev_clustersize(0),
    mean_centroid_cluster(0),
    stdev_centroid_cluster(0),
    pixel_counter(),
    pixel_memory()
    {}
};

struct SafeCounter {
    std::mutex mutex;
    std::vector<Counter> count_vec;

    void append(const Counter& f_counter){
        std::lock_guard<std::mutex> guard(mutex);
        count_vec.emplace_back(f_counter);
    }
    void safe(const std::string& out_file){
//      TFile* f  = new TFile(out_file.c_str(),"RECREATE");
     
    }
};



class Scan
{
public:
 Scan();
 ~Scan();
};

#endif // SCAN_H
