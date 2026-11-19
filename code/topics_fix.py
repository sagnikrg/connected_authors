"""Hand review of topics_auto.json (2026-11-19) -> data/topics.json. Keys are title substrings; value = final labels."""
import json,os,sys,re
D=sys.argv[1]
P=json.load(open(os.path.join(D,'papers.json'),encoding='utf8'))['papers']; T=json.load(open(os.path.join(D,'topics_auto.json'),encoding='utf8'))
SET={  # title substring -> labels (replaces the automatic ones)
 "Random matrix theory for quantum and classical metastability":[],
 "Polynomial filter diagonalization":["mbl-eth"],
 "Discrete Time Crystals: Rigidity, Criticality":["dtc"],
 "Quantum Entanglement Growth under Random Unitary":["mbl-eth"],
 "Measurement and Entanglement Phase Transitions in All-To-All":[],
 "Environment assisted superballistic":[],
 "Efficient Tensor Network Simulation of IBM":[],
 "Scrambling Transition in a Radiative":["mbl-eth"],
 "Constrained Dynamics and Directed Percolation":["mbl-eth"],
 "Statistics of Correlation Functions in the Random Heisenberg":["mbl-eth"],
 "Classical algorithms for many-body quantum systems at finite":["mbl-eth"],
 "Yao Observation of Prethermal TC":["dtc","experiment"],
 "Random matrix spectral form factor in kicked":["SFF","mbl-eth"],
 "Quantum optimization of maximum independent set":["experiment"],
 "Simulating quantum many-body dynamics on a current digital":["experiment"],
 "Kinetically constrained freezing transition":["mbl-eth"],
 "Topological Quantum Spin Glass Order":[],
 "Scalable Probes of Measurement-Induced":[],
 "Quantum Zeno effect and the many-body entanglement":[],
 "Theory of Measurement-Altered Criticality":[],
 "Entanglement in a fermion chain under continuous monitoring":[],
 "Quantum Error Correction in Scrambling Dynamics":[],
 "Self-organized error correction":[],
 "Measurement-driven entanglement transition in hybrid":[],
 "Entanglement transitions via space-time rotation":[],
 "Entanglement Dynamics in Hybrid Quantum Circuits":[],
 "Entanglement transitions from holographic":[],
 "Measurement-Driven Phase Transition within a Volume-Law":[],
 "Critical properties of the measurement-induced transition":[],
 "Information propagation in isolated quantum systems":["mbl-eth"],
 "Hierarchy of Relaxation Timescales":[],
 "Long-Range Prethermal Phases":["dtc"],
 "Floquet Phases of Matter via Classical Prethermalization":["dtc"],
 "Phase Structure of Driven Quantum Systems":["dtc","pi-SG"],
 "Absolute stability and spatiotemporal long-range order":["dtc","pi-SG"],
 "Equilibration and order in quantum Floquet matter":["dtc","pi-SG"],
 "Equilibration and Order in Qunatum Floquet":["dtc","pi-SG"],
 "Floquet quantum criticality":["dtc","pi-SG"],
 "Time-crystalline eigenstate order on a quantum processor":["dtc","pi-SG","experiment"],
 "nphys3783 SM":["mbl-eth","experiment"],
 "Szymanska Dynamical Critical Exponents Material":[],
}
out={}
for p in P:
    lab=T[p['f']]
    for k,v in SET.items():
        if k.lower() in p['t'].lower(): lab=v
    out[p['f']]=lab
json.dump(out,open(os.path.join(D,'topics.json'),'w',encoding='utf8'),indent=0,ensure_ascii=False)
import collections; print(collections.Counter(x for v in out.values() for x in v),'untagged',sum(1 for v in out.values() if not v),'of',len(out))
used={k for k in SET for p in P if k.lower() in p['t'].lower()}; print('unused overrides:',set(SET)-used)
