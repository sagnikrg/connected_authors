"""Topic labels for the papers in the graph, from the title first, then the page-1 abstract.
Usage: python -I code/topics.py data <Dropbox root>
Reads data/papers.json, writes data/topics_auto.json {file: [labels]} (the review starts from it).
Final labels live in data/topics.json {file: [labels]}; manual entries there win over the automatic ones."""
import json,os,re,subprocess,sys
D,ROOT=sys.argv[1],sys.argv[2]
P=json.load(open(os.path.join(D,'papers.json'),encoding='utf8'))['papers']
R=lambda *ps: re.compile('|'.join(ps),re.I)
RULES=[
 ('dtc',    R(r'time[- ]crystal',r'time-crystalline',r'period[- ]doubl',r'discrete time[- ]translation',r'subharmonic',r'\bDTCs?\b')),
 ('pi-SG',  R(r'(π|pi)[- ]?spin[- ]?glass',r'\bπ-?SG\b',r'\bpi-?SG\b')),
 ('scar',   R(r'\bscar(s|red|ring)?\b')),
 ('majorana',R(r'majorana')),
 ('SFF',    R(r'spectral form factor',r'\bSFF\b')),
 ('mbl-eth',R(r'many[- ]body locali[sz]',r'\bMBL\b',r'eigenstate thermali[sz]ation',r'\bETH\b',r'thermali[sz]',r'ergodic',r'locali[sz]ation',r'level statistics',r'level spacing',r'quantum chaos',r'chaotic',r'avalanche',r'prethermal')),
]
EXP_T=R(r'observation of',r'observing',r'experimental',r'experiment',r'realization of',r'realisation of',r'demonstrat',r'on a quantum processor',r'superconducting qubits',r'trapped[- ]ion',r'NV cent',r'quantum simulator')
EXP_A=R(r'we (experimentally|observe|demonstrate|report the observation|realize|realise|implement)',r'here we report',r'in this experiment')
PLAT=R(r'qubit',r'trapped[- ]ion',r'\bions?\b',r'atoms?\b',r'processor',r'NV',r'diamond',r'spins? in',r'rydberg',r'superconducting')
def text(f):
    try: return subprocess.run(['pdftotext','-l','1','-q',os.path.join(ROOT,f),'-'],capture_output=True,timeout=60).stdout.decode('utf8','ignore')
    except Exception: return ''
out={}
for p in P:
    t=p['t']; a=' '.join(text(p['f'])[:2500].split())
    lab=[k for k,r in RULES if r.search(t)]
    if not lab: lab=[k for k,r in RULES if r.search(a)]
    if 'dtc' in lab or 'scar' in lab: lab=[x for x in lab if x!='mbl-eth']
    if EXP_T.search(t) and PLAT.search(t+' '+a) or (EXP_A.search(a) and PLAT.search(a)): lab.append('experiment')
    out[p['f']]=lab
json.dump(out,open(os.path.join(D,'topics_auto.json'),'w',encoding='utf8'),indent=0,ensure_ascii=False)
import collections; print(len(out),collections.Counter(x for v in out.values() for x in v),'untagged',sum(1 for v in out.values() if not v))
