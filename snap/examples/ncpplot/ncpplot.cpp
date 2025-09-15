#include "stdafx.h"
#include "ncp.h"
#include <vector>
#include <queue>
#include <utility>
#include <fstream>
#include "Snap.h"
#include <cstdio>

// --- Helper: get cluster nodes for a given target size ---
TVec<TInt> GetClusterNodesBySize(const PUNGraph& Graph, double Alpha,
                                 int targetSize, const THash<TInt,TInt>& IdMap) {
    TVec<TInt> OutCluster;

    for (TUNGraph::TNodeI NI = Graph->BegNI(); NI < Graph->EndNI(); NI++) {
        TLocClust LC(Graph, Alpha);
        LC.FindBestCut(NI.GetId(), targetSize*10, 0.1); // maxVolume = targetSize*10, epsilon = 0.1
        const TIntV& NIdV = LC.GetNIdV();

        if (NIdV.Len() == targetSize) {
            OutCluster.Clr();
            for (int i = 0; i < NIdV.Len(); i++) {
                OutCluster.Add(IdMap.GetDat(NIdV[i])); // map to original ID
            }
            break; // first matching cluster
        }
    }

    return OutCluster;
}
// Cluster info struct
struct ClusterInfo {
    double Phi;
    int Vol;
    TIntV Nodes;
};

// Comparator must be **after** the struct definition
struct ClusterCmp {
    bool operator()(const ClusterInfo& a, const ClusterInfo& b) const {
        return a.Phi < b.Phi; // smallest phi survives
    }
};

void SaveClustersToFile(const TLocClustStat& ClusStat, const TStr& OutFNm) {
    const TStr ClustFNm = TStr::Fmt("ncp.%s.perbin.clusters.tab", OutFNm.CStr());
    FILE* F = fopen(ClustFNm.CStr(), "wt");
    fprintf(F, "#Bin\tSize\tVol\tPhi\tNodes\n");

    // Pre-C++11 style: fill vector using push_back
    std::vector<std::pair<int,int> > SizeBins;
    SizeBins.push_back(std::make_pair(1,10));
    SizeBins.push_back(std::make_pair(11,50));
    SizeBins.push_back(std::make_pair(51,100));
    SizeBins.push_back(std::make_pair(101,500));
    SizeBins.push_back(std::make_pair(501,1000));
    SizeBins.push_back(std::make_pair(1001,5000));
    SizeBins.push_back(std::make_pair(5001,INT_MAX));

    const int TopNPerBin = 20;

    typedef std::priority_queue<ClusterInfo, std::vector<ClusterInfo>, ClusterCmp> ClusterHeap;
    std::vector<ClusterHeap> BinHeaps(SizeBins.size());

    // --- process all clusters ---
    for (int i = 0; i < ClusStat.BestCutH.Len(); i++) {
        const TLocClustStat::TCutInfo& Cut = ClusStat.BestCutH[i];
        int sz = Cut.CutNIdV.Len();
        double phi = Cut.GetPhi();
        int vol = Cut.GetVol();
        if (sz == 0) continue;

        // find bin
        for (size_t b = 0; b < SizeBins.size(); b++) {
            if (sz >= SizeBins[b].first && sz <= SizeBins[b].second) {
                ClusterHeap& heap = BinHeaps[b];
                if ((int)heap.size() < TopNPerBin) {
                    heap.push((ClusterInfo){phi, vol, Cut.CutNIdV});
                } else if (phi < heap.top().Phi) {
                    heap.pop();
                    heap.push((ClusterInfo){phi, vol, Cut.CutNIdV});
                }
                break;
            }
        }
    }

    // --- dump results ---
    for (size_t b=0; b<SizeBins.size(); b++) {
        ClusterHeap heapCopy = BinHeaps[b]; // copy to pop
        while (!heapCopy.empty()) {
            const ClusterInfo& cluster = heapCopy.top();
            double phi = cluster.Phi;
            int vol = cluster.Vol;
            const TIntV& NIdV = cluster.Nodes;

            fprintf(F, "[%d-%d]\t%d\t%d\t%f\t",
                SizeBins[b].first, SizeBins[b].second, NIdV.Len(), vol, phi);
            for (int n=0; n<NIdV.Len(); n++) {
                fprintf(F, "%d ", (int)NIdV[n]);
            }
            fprintf(F, "\n");
            heapCopy.pop();
        }
    }

    fclose(F);
    printf("Clusters saved to: %s\n", ClustFNm.CStr());
}




int main(int argc, char* argv[]) {
    Env = TEnv(argc, argv, TNotify::StdNotify);
    Env.PrepArgs(TStr::Fmt("Network Community Profile Plot. build: %s, %s. Time: %s",
        __TIME__, __DATE__, TExeTm::GetCurTm()));

    TExeTm ExeTm;

    Try
    // --- input arguments ---
    const TStr InFNm  = Env.GetIfArgPrefixStr("-i:", "../as20graph.txt", "Input undirected graph");
    TStr OutFNm       = Env.GetIfArgPrefixStr("-o:", "", "Output file name");
    TStr Desc         = Env.GetIfArgPrefixStr("-d:", "", "Description");
    const int DrawWhisk = Env.GetIfArgPrefixInt("-d:", -1, "Draw largest D whiskers");
    const bool TakeCore = Env.GetIfArgPrefixBool("-k:", false, "Take core");
    const bool DoWhisk  = Env.GetIfArgPrefixBool("-w:", false, "Do bag of whiskers");
    const bool DoRewire = Env.GetIfArgPrefixBool("-r:", false, "Do rewired network");
    const bool SaveInfo = Env.GetIfArgPrefixBool("-s:", true, "Save info file");
    const int KMin = Env.GetIfArgPrefixInt("-kmin:", 1000, "minimum K (volume)");
    const int KMax = Env.GetIfArgPrefixInt("-kmax:", Mega(100), "maximum K (volume)");
    const int Coverage = Env.GetIfArgPrefixInt("-c:", 10, "coverage");
    TLocClust::Verbose = Env.GetIfArgPrefixBool("-v:", true, "Verbose output");

    if (OutFNm.Empty()) { OutFNm = InFNm.GetFMid(); }
    if (Desc.Empty()) { Desc = OutFNm; }

    // --- load graph ---
    PUNGraph Graph = TSnap::GetMxWcc(TSnap::LoadEdgeList<PUNGraph>(InFNm,0,1));

    // --- build mapping from SNAP internal IDs to original IDs ---
    THash<TInt,TInt> SnapIdToOrigId;
    for (TUNGraph::TNodeI NI = Graph->BegNI(); NI < Graph->EndNI(); NI++) {
        SnapIdToOrigId.AddDat(NI.GetId(), NI.GetId()); // adjust if SNAP remaps IDs
    }

    // --- optional preprocessing ---
    if (DrawWhisk > 0) {
        printf("*** Drawing whiskers\n");
        TLocClust::DrawWhiskers(Graph, OutFNm, DrawWhisk);
    }

    if (TakeCore) {
        printf("Take bi-connected core: (%d, %d) -> ", Graph->GetNodes(), Graph->GetEdges());
        Graph = TSnap::GetMxBiCon(Graph);
        printf("(%d, %d)\n", Graph->GetNodes(), Graph->GetEdges());
    }

    printf("*** Plotting network community profile (NCP)\n");
    printf("----------------SaveInfo: %s", SaveInfo ? "true\n" : "false\n");

    // --- run NCP ---
    const double Alpha = 0.001, KFac = 1.5, SizeFrac = 0.001;
    TLocClust::PlotNCP(Graph, OutFNm, "Graph: "+InFNm+" -> "+OutFNm+" "+Desc,
                        DoWhisk, DoRewire, KMin, KMax, Coverage, SaveInfo);

    // --- extract clusters and write single .clusters.tab file ---
    TLocClustStat ClusStat(Alpha, KMin, KMax, KFac, Coverage, SizeFrac);
    // ClusStat.Run(Graph, false, false, SaveInfo);  // run to populate BestCutH
    ClusStat.Run(Graph, false, false, true);  // run to populate BestCutH
    SaveClustersToFile(ClusStat, OutFNm);


    // const TStr ClustFNm = TStr::Fmt("ncp.%s.clusters.tab", OutFNm.CStr());
    // FILE* F = fopen(ClustFNm.CStr(), "wt");
    // fprintf(F, "#Size\tPhi\tNodes\n");

    // for (int i = 0; i < ClusStat.BestCutH.Len(); i++) {
    //     const TLocClustStat::TCutInfo& Cut = ClusStat.BestCutH[i];

    //     TVec<TInt> ClusterNodes = GetClusterNodesBySize(Graph, Alpha, Cut.GetNodes(), SnapIdToOrigId);

    //     if (ClusterNodes.Len() == 0) {
    //         printf("Warning: could not find cluster of size %d\n", Cut.GetNodes());
    //         continue;
    //     }

    //     fprintf(F, "%d\t%f\t", Cut.GetNodes(), Cut.GetPhi());
    //     for (int n = 0; n < ClusterNodes.Len(); n++)
    //         fprintf(F, "%d ", ClusterNodes[n]());
    //     fprintf(F, "\n");
    // }

    // fclose(F);

    Catch
    printf("\nrun time: %s (%s)\n", ExeTm.GetTmStr(), TSecTm::GetCurTm().GetTmStr().CStr());

    return 0;
}
