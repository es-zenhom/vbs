#ifndef PILOT_H
#define PILOT_H

// RAPIDO
#include "arbol.h"
#include "looper.h"
#include "cutflow.h"
// ROOT
#include "TString.h"
#include "Math/VectorUtil.h"
// NanoCORE
#include "Nano.h"
#include "Config.h"
#include "ElectronSelections.h"
#include "MuonSelections.h"

typedef std::vector<LorentzVector> LorentzVectors;
typedef std::vector<int> Integers;
typedef std::vector<unsigned int> Indices;

enum DeepJetTag
{
    NoTag = 0,
    LooseTag = 1,
    MediumTag = 2,
    TightTag = 3
};
typedef std::vector<DeepJetTag> DeepJetTags;

class VBS3LepCuts
{
public:
    Cut* bookkeeping;
    Cut* has_3leps_presel;
    Cut* select_leps;
    Cut* select_jets;
    Cut* geq_2_jets;
    Cut* no_tight_b_jets;
    Cut* trigger;
    Cut* select_vbs_jets_maxE;
    Cut* has_3leps;
    Cut* has_3leps_0SFOS;
    Cut* has_3leps_1SFOS;
    Cut* Z_veto;
    Cut* has_3leps_2SFOS;
    Cut* dummy;
    
    VBS3LepCuts(Arbol& arbol, Nano& nt, HEPCLI& cli, Cutflow& cutflow);
    void initBranches(Arbol& arbol);
    void initGlobals(Cutflow& cutflow);
    bool isSFOS(int pdgID_1, int pdgID_2);
};

#include "cuts.icc"

#endif
