#include <iostream>
#include <thread>
#include <forward_list>

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
#include "TProcPool.h"
#include "TArray.h"
#include "TArrayI.h"

#include "../Tools/Producer.h"

#define CHANNELS 48

namespace fs =boost::filesystem;
// using namespace std;
namespace po = boost::program_options;


bool check_file_path(const std::string& file_path_str, fs::path& p);
std::vector<std::string>get_list_of_files(std::string const& run_file, std::string const& path);
int  read_ttree(std::string const& root_file);

int main(int argc, char **argv) {
    std::string path;
    std::string run_file;
    std::string out_file;
    std::string mask_file;
    std::string geo_file;
    std::vector<std::string> filenames;
    bool mask_toggle;
    try{
        po::options_description desc("Allowed options");
        desc.add_options()
        ("help,h", "A programm to produce the clustered TTrees and Generate prompt offline Visual feedback from 2 MAPSA-light TTree data.")
        ("path,p",            po::value<std::string>(&path)     ->default_value("./"),             "Default path for run files")
        ("signal_files,s",    po::value<std::string>(&run_file) ->default_value("signal.txt"),     "A file with list of run files ROOT")
        ("out_file,o",        po::value<std::string>(&out_file) ->default_value("analysis.root"),  "Destination file")
        ("pixel_mask_file,m", po::value<std::string>(&mask_file)->default_value("pixel_mask.txt"), "Pixel mask file")
        ("geometry_file,g",   po::value<std::string>(&geo_file )->default_value("geo_file.txt"),   "Geometry   file")
        ("mask_toggle,t",     po::value<bool>(&mask_toggle)     ->default_value(false), "Toggle pixel mask")
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
            std::cout<<line<<std::endl;
        }
    }
    catch(po::error& e)
    {
        std::cout << e.what()<<std::endl;
        return 0;
    }
    PRODUCER::Producer t;
// Read Geo File
    fs::path geo_f,mask_f;
    if(check_file_path(geo_file,geo_f)){
        std::vector<bool> geom_vec(6,false);
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
//     for(const auto &i : filenames.begin())
    for(auto it(filenames.begin()+28); it != filenames.begin()+29; ++it)
    {
//         std::cout<<i<<"\n";
        t.SetFile(*it);
    }
    std::flush(std::cout);

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

int read_ttree(const std::string& root_file)
{
    const Int_t Workers = 4;
//     const Int_t Events  = 1000000;
//     const Int_t N_events  = Events/Workers;
//     ROOT::EnableThreadSafety();
    TFile *file = new TFile();
    file->Open("DEPPER","READ");
    if(file->IsZombie()){
        std::cout<<"Error opening file"<<std::endl;
        return 0;
    }
    else
        std::cout<<"Error opening file\t"<<root_file<<std::endl;
    TTree *tree = (TTree*)file->Get("Tree");
    tree->Print();
    file->Close();
//     TRandom rndm;
//     //       Workers are defined;
//     std::forward_list<UInt_t> workerIDs(Workers);
//     std::iota(std::begin(workerIDs), std::end(workerIDs), 0);
//     // Parameters:
//     //     Single Channel Noise, Common Mode Noise, Vector Of Bad/Sick Channels, 
//     const int channels = 288;
//     Int_t channelInt_t;
//     double sigma_channel=1;
//     double s_channel=2;
//     double offset_spread=0;
//     double threshold=0;
//     std::vector<float> OffsetChannel;
//     std::vector<float> SigmaChannel;
//     std::vector<float> CommonMode;
//     
//     double sigma_channel_min  =0;
//     double sigma_channel_max  =5.1;
//     int sigma_channel_int  =51;
//     double sigma_channel_fac= (sigma_channel_max-sigma_channel_min)/sigma_channel_int;
//     
//     
//     double offset_spread_min  =0.00;
//     double offset_spread_max  =2.20;
//     int offset_spread_int  =11;
//     double offset_spread_fac= (offset_spread_max-offset_spread_min)/offset_spread_int;
//     
//     double s_channel_min =0;
//     double s_channel_max =4.1;
//     int s_channel_int =41;
//     double s_channel_fac = (s_channel_max-s_channel_min)/s_channel_int;
//     
//     double threshold_min=-0.1;
//     double threshold_max=0.2;
//     int threshold_int=3;
//     double threshold_fac=(threshold_max-threshold_min)/threshold_int;
//     
//     
//     std::vector<TH1I> histograms;
//     std::vector<TRandom3> randoms;
//     histograms.reserve(Workers);
//     randoms.reserve(Workers);
//     for (auto workerID : workerIDs){
//         histograms.emplace_back(TH1I(Form("NumberOfHits_%u", workerID), Form("NumberOfHits_%u",workerID), channels, 0, channels));
//         randoms.emplace_back(TRandom3(workerID));
//     }
//     
//     TH1I *NumberOfHits = new TH1I("numberofhits","numberofhits", channels, 0, channels);
//     channelInt_t = (Int_t)NumberOfHits->GetSize();
//     Int_t *numberofhits_arr = new Int_t[channelInt_t];
//     
//     //   Generate initial channel offsets vector
//     TBits *bits = new TBits(channels);
//     //     tree->Branch("bits","TBits",&bits,32000,0);
//     tree->Branch("sigma_channel", &sigma_channel,32000);
//     tree->Branch("s_channel", &s_channel, 32000);
//     tree->Branch("offset_spread", &offset_spread, 32000);
//     tree->Branch("threshold", &threshold, 32000);
//     tree->Branch("NumberOfHits","TH1I",&NumberOfHits,32000);
//     tree->Branch("channelInt_t",&channelInt_t,"channelInt_t/I");
//     tree->Branch("NumberOfHits_Arr",&numberofhits_arr,"numberofhits_arr[channelInt_t]/I",32000);
//     //       tree->Branch("BitArrayEvents","TBits",&bits,32000);
//     
//     OffsetChannel.resize(channels);
//     SigmaChannel.resize(channels);
//     CommonMode.resize(channels);
//     
//     uint allcounter =0;
//     for(int i=0; i<channels; i++){
//         OffsetChannel.at(i)=rndm.Rndm()*2*offset_spread-.5*offset_spread;
//         //                                   OffsetChannel.at(i)=rndm.Uniform((-1)*offset_spread,offset_spread);
//         numberofhits_arr[i]=0;
//         // OffsetChannel.at(i)=0;
//         SigmaChannel.at(i)=sigma_channel;
//         //                                   CommonMode.at(i)=s_channel;
//     }
//     
//     for(int i3=0; i3<sigma_channel_int; i3++)
//     {
//         sigma_channel=i3*sigma_channel_fac+sigma_channel_min;
//         for(int i4=0; i4<channels; i4++)
//             SigmaChannel.at(i4)=sigma_channel;
//         for(int i0=0; i0<threshold_int; i0++)
//         {
//             threshold=i0*threshold_fac+threshold_min;
//             //                       for(int i1=0; i1<offset_spread_int; i1++)
//             //                       {
//             //                               offset_spread=i1*offset_spread_fac+offset_spread_min;
//             for(int i2=0; i2<s_channel_int; i2++)
//             {
//                 s_channel=i2*s_channel_fac+s_channel_min;
//                 printf("generate distribution: threshold %f s_channel %f sigma_channel %f\n",threshold, s_channel, sigma_channel);
//                 std::fflush(stdout);
//                 // We define our work item
//                 auto workItem = [&histograms, &randoms, SigmaChannel, &CommonMode, OffsetChannel, N_events, channels, threshold, s_channel](UInt_t workerID) {
//                     TH1I& histo  = histograms.at(workerID);
//                     histo.Reset();
//                     TRandom3& random = randoms.at(workerID);
//                     u_int counter=0;
//                     for(u_int indey = 0; indey  < N_events; indey++){
//                         counter=0;
//                         double cm = random.Gaus(0,s_channel);
//                         for(u_int index = 0; index  < channels; index++)
//                         {
//                             CommonMode.at(index)=cm;
//                         }
//                         for(u_int index = 0; index  < channels; index++)
//                         {
//                             if(random.Gaus(0,SigmaChannel.at(index))+OffsetChannel.at(index)+CommonMode.at(index)>threshold)
//                             {
//                                 counter++;
//                                 //                       bits->SetBitNumber(j);
//                             }
//                             //                                                       histo.Fill(counter);
//                             
//                         };
//                         histo.Fill(counter);
//                     }
//                 };
//                 // Spawn workers
//                 // Fill the "pool" with workers
//                 // Create the collection which will hold the threads, our "pool"
//                 std::vector<std::thread> workers;
//                 for (auto workerID : workerIDs) {
//                     workers.emplace_back(workItem, workerID);
//                 }
//                 //                   joind 
//                 for (auto&& worker : workers) worker.join();
//                 NumberOfHits->Reset();
//                 std::for_each(std::begin(histograms), std::end(histograms),
//                               [&NumberOfHits,allcounter](const TH1I & h) {
//                                   NumberOfHits->Add(&h);
//                                   //                                                       h.Print("base");
//                                   //                                                       h.Write(Form("allcountericd_%u",allcounter));
//                               });
//                 allcounter++;
//                 numberofhits_arr = (NumberOfHits->GetArray());
//                 //                           std::copy(std::begin(varray),std::end(varray),std::begin(numberofhits_arr));
//                 //                           NumberOfHits->Write(Form("allcounter_%u",allcounter));
//                 //                           NumberOfHits->SetDirectory(0);
//                 tree->Fill();
//                 // And reduce
//                 
//                 //                                                   tree->Fill();
//             }
//             //                       }
//         }
//     }
//     
//     tree->Write("tree");
//     file->Write();
    file->Close();
    return 0;
}
