#include <iostream>
#include <thread>
#include <forward_list>
#include <mutex>
#include <vector>
#include <chrono>


#include <boost/program_options.hpp>
#include <boost/program_options/options_description.hpp>
#include <boost/program_options/option.hpp>
#include "boost/filesystem.hpp"   // includes all needed Boost.Filesystem declarations


#include "Riostream.h"
#include "TApplication.h"
// #include "TAttLine.h"
// #include "TAttMarker.h"
// #include "TAxis.h"
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
// #include "TGraph.h"
#include "TH1.h"
// #include "TH2.h"
// #include "TKey.h"
// #include "TLatex.h"
// #include "TLegend.h"
// #include "TList.h"
// #include "TMath.h"
// #include "TMultiGraph.h"
// #include "TObject.h"
// #include "TPad.h"
#include "TRandom3.h"
#include "TROOT.h"
#include "TString.h"
// #include "TStyle.h"
#include "TSystem.h"
#include "TString.h"
#include "TTree.h"
#include "TBits.h"
#include "TArray.h"
#include "TArrayI.h"

#include "../Tools/dataformat_tree.h"
#include "../Tools/Producer.h"
#include "../Tools/ThreadPool.cpp"
#include "../Tools/Scan.h"


namespace fs =boost::filesystem;
// using namespace std;
namespace po = boost::program_options;


bool check_file_path(const std::string& file_path_str, fs::path& p);
std::vector<std::string>get_list_of_files(std::string const& run_file, std::string const& path);

int main(int argc, char **argv) {
    std::string path;
    std::string run_file;
    std::string out_file;
    std::string mask_file;
    std::string geo_file;
    std::string result_file;
    std::vector<std::string> filenames;
    bool mask_toggle;
    try{
        po::options_description desc("Allowed options");
        desc.add_options()
        ("help,h", "A programm to produce the clustered TTrees and Generate prompt offline Visual feedback from 2 MAPSA-light TTree data.")
        ("path,p",            po::value<std::string>(&path)     ->default_value("./"),             "Default path for run files")
        ("signal_files,s",    po::value<std::string>(&run_file) ->default_value("signal.txt"),     "A file with list of run files ROOT")
        ("out_file_path,o",        po::value<std::string>(&out_file) ->default_value("./"),  "Destination file")
        ("pixel_mask_file,m", po::value<std::string>(&mask_file)->default_value("pixel_mask.txt"), "Pixel mask file")
        ("geometry_file,g",   po::value<std::string>(&geo_file )->default_value("geo_file.txt"),   "Geometry   file")
        ("mask_toggle,t",     po::value<bool>(&mask_toggle)     ->default_value(false), "Toggle pixel mask")
        ("result_file,r",     po::value<std::string>(&result_file)->default_value("Results.root"), "Result root file")
        ;
        po::variables_map vm;
        po::store(po::parse_command_line(argc, argv, desc), vm);
        po::notify(vm);
        
        if (vm.count("help")) {
            std::cout << desc << "\n";
            return 0;
        }else
        {
            //              std::cout << desc << "\n";
            const std::string line(40, '-');
            std::cout<<std::left<<"\nOptions:\n";
            std::cout<<line<<std::endl;
            std::cout<<std::setw(20)<<std::left<<"Path:"<<std::right<<path<<"\n";
            std::cout<<std::setw(20)<<std::left<<"Run list:"<<std::right<<run_file<<"\n";
            std::cout<<std::setw(20)<<std::left<<"Destination file:"<<std::right<<out_file<<"\n";
            std::cout<<std::setw(20)<<std::left<<"Pixel Mask  file:"<<std::right<<mask_file<<"\n";
            std::cout<<std::setw(20)<<std::left<<"Geometry    file:"<<std::right<<geo_file<<"\n";
            std::cout<<std::setw(20)<<std::left<<"Mask  toggle:"<<std::right<<mask_toggle<<"\n";
            std::cout<<std::setw(20)<<std::left<<"Result root file:"<<std::right<<result_file<<"\n";
            std::cout<<line<<std::endl;
        }
    }
    catch(po::error& e)
    {
        std::cout << e.what()<<std::endl;
        return 0;
    }
    
    PRODUCER::Producer t(out_file);
    // Read Geo File
    std::vector<bool> geom_vec(6,false);
    fs::path geo_f,mask_f;
    if(check_file_path(geo_file,geo_f)){
        std::ifstream input( geo_f.string());
        int line_c=0;
        for( std::string line; std::getline( input, line ); )
        {
            if(line_c<2)
                for(auto i = 0; i < line.length(); ++i)
                    if(i<3 && line[i]=='1')
                        geom_vec.at(i+line_c*3)=true;
                    line_c++;
        }
        std::cout<<"set geometry"<<std::endl;
        t.SetGeometry(geom_vec);
        input.close();
    }
    //     Read Mask Files
    if(check_file_path(mask_file,mask_f)){
        std::ifstream input( mask_f.string());
        int line_c=0;
        for( std::string line; std::getline( input, line ); )
        {
            std::vector<bool> mask_vec(CHANNELS,false);
            for(auto i = 0; i < line.length(); ++i)
                if(i<CHANNELS && line[i]=='1')
                    mask_vec.at(i)=true;
                t.Set_PixelMaskMPA(line_c,mask_vec);
            line_c++;
        }
        input.close();
    }
    t.Print_GeometryMaskMPA();
    t.Print_PixelMaskMPA();
    filenames=get_list_of_files(run_file,path);
    std::cout<<"Files for processing:\n";
    
    //     ThreadPool pool(4);
    //     std::vector< std::future<int> > results;
    //     int thread_no=0;
    //     for(auto it(filenames.begin()); it != filenames.end(); ++it)
    //     {
    //         thread_no++;
    //         auto outfile_tmp=out_file+std::to_string(thread_no);
    //         pool.enqueue([outfile_tmp,it,geom_vec] {
    //             PRODUCER::Producer t1(outfile_tmp);
    //             t1.SetGeometry(geom_vec);
    //             std::cout<<*it<<std::endl;
    //             t1.SetFile(*it);
    //             t1.SaveResetHists(fs::path(*it).stem().c_str());
    //         });
    //     }
    // 
    //     for(auto && result: results)
    //         std::cout << result.get() << ' ';
    //     std::cout << std::endl;
    SafeCounter ScanResults;
    for(auto it(filenames.begin()); it != filenames.end(); ++it)
        //     for(auto it(filenames.begin()+28); it != filenames.begin()+35; ++it)
    {
        std::cout<<*it<<"\n";
        Counter tmpcounter;
        t.SetFile(*it, tmpcounter,fs::path(*it).stem().c_str(),out_file);
        ScanResults.append(tmpcounter);
        t.SaveResetHists();
    }
    std::flush(std::cout);    
    //     t.~Producer();
    TFile * result = new TFile(result_file.c_str(),"RECREATE");
    result->mkdir("Results");
    result->cd("Results");
    
    TH1F* Glob_Hits_vs_Treshold = new TH1F("Glob_Hits_vs_Treshold","Glob_Hits_vs_Treshold",THRESHOLD_RANGE,-.5,THRESHOLD_RANGE-.5);
    TH2F* Glob_Hits_vs_Channel_vs_Treshold= new TH2F("Hits_vs_Channel_vs_Treshold","Hits_vs_Channel_vs_Treshold",CHANNELS*ASSEMBLY,.5, CHANNELS*ASSEMBLY+.5,THRESHOLD_RANGE,-.5,THRESHOLD_RANGE-.5);
    TH2F* Glob_Hits_vs_Channel_vs_Treshold_MEM= new TH2F("Hits_vs_Channel_vs_Treshold_MEM","Hits_vs_Channel_vs_Treshold_MEM",CHANNELS*ASSEMBLY,.5, CHANNELS*ASSEMBLY+.5,THRESHOLD_RANGE,-.5,THRESHOLD_RANGE-.5);
    TH2I* TDC_vs_Channel_vs_Treshold= new TH2I("TDC_vs_Channel_vs_Treshold","TDC_vs_Channel_vs_Treshold",CHANNELS*ASSEMBLY,.5, CHANNELS*ASSEMBLY+.5,THRESHOLD_RANGE,-.5,THRESHOLD_RANGE-.5);
    for(auto it(ScanResults.count_vec.begin()); it != ScanResults.count_vec.end(); ++it)
    {
        Counter tmp=Counter(*it);
        Glob_Hits_vs_Treshold->Fill(tmp.threshold,tmp.mean_hits);
        //         Glob_Hits_vs_Treshold->SetBinError(Glob_Hits_vs_Treshold->FindBin(tmp.threshold),tmp.stdev_hits);
        for(int i=0; i<CHANNELS*ASSEMBLY+2; i++)
        {
            Glob_Hits_vs_Channel_vs_Treshold->Fill(i-1,tmp.threshold,tmp.pixel_counter[i]/tmp.no_shutter);
            Glob_Hits_vs_Channel_vs_Treshold_MEM->Fill(i-1,tmp.threshold,tmp.pixel_memory[i]/tmp.no_shutter);
            //             Glob_Hits_vs_Channel_vs_Treshold->SetBinError(Glob_Hits_vs_Channel_vs_Treshold->FindBin(i-1,tmp.threshold),1/TMath::Sqrt(tmp.pixel_counter[i]));
        }
    }
    Glob_Hits_vs_Channel_vs_Treshold->Write();
    Glob_Hits_vs_Channel_vs_Treshold_MEM->Write();
    Glob_Hits_vs_Treshold->Write();
    result->Close();
    
    return 0;
}
bool check_file_path(const std::string& file_path_str, fs::path& p){
    p=fs::path(file_path_str);
    try
    {
        if (exists(p))    // does p actually exist?
        {
            if (is_regular_file(p)){        // is p a regular file?
                //                 std::cout << p << " size is " << fs::file_size(p) << '\n';
                return true;
            }
            else{
                std::cout << p << " exists, but is neither a regular file nor a directory\n";
                exit(1);
            }
        }
        else{
            std::cout << p << " does not exist\n";
            exit(1);
        }
    }
    catch (const fs::filesystem_error& ex)
    {
        std::cout << ex.what() << '\n';
    }
    return false;
}
std::vector<std::string>get_list_of_files(std::string const& run_file, std::string const& path)
{
    fs::path p;
    std::vector<std::string> result;
    if(check_file_path(run_file,p)){
        fs::path data_file_path;
        std::ifstream input( p.string());
        for( std::string line; std::getline( input, line ); )
        {
            if(line!="" && check_file_path(path+line,data_file_path))
                result.push_back(data_file_path.string());
        }
        input.close();
    }
    return result;
}

