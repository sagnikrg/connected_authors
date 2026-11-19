"""Exact titles in filenames + one copy per paper, for the papers in the graph.
Usage: python -I code/dedupe_titles.py data <Dropbox root> <friends dir (db export)> [--apply] [--log out.csv]
Without --apply it only prints the plan.

Same paper = same bib entry / link, or the same normalised exact title (arXiv and journal copies count as one).
Exception kept on purpose: Lazarides 2403.01912 v1 and v2 (Tony).
Which copy survives (location first, then content):
  0. author-named folders beat topic folders;
  1. folders of Luis, Dominik, Maurits first; a paper of theirs that sits only in David's folder moves to theirs;
  2. otherwise the folder owner closest in the co-author graph to a seed (Luis/Dominik/Maurits, or Deepak Dhar/
     Katarzyna Macieszczak/Marzena Szymanska for the other cluster);
  3. otherwise the folder with fewer PDFs.
  The file that survives is the annotated copy if any (most annotations), else the larger one, placed at that location.
Filenames become  <id>_<Exact Title> [tags].pdf  (id = arXiv id or journal id already in the name, else the arXiv id)."""
import json,os,re,sys,csv,glob,collections,urllib.request,urllib.parse,time,unicodedata
D,ROOT,FR=sys.argv[1:4]; APPLY='--apply' in sys.argv
LOG=sys.argv[sys.argv.index('--log')+1] if '--log' in sys.argv else None
A=lambda s: unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode()
norm=lambda t: ' '.join(re.findall(r'[a-z0-9]+',A(re.sub(r'\$[^$]*\$','',t)).lower()))
P=json.load(open(os.path.join(D,'papers.json'),encoding='utf8'))['papers']
SUPP=re.compile(r'supp|SM|_SM|appendi|supplement|material',re.I)
P=[p for p in P if not SUPP.search(os.path.basename(p['f']))]  # supplementary files are separate documents: never pruned or renamed
HOW={r[0].replace('\\','/'):r[1] for r in csv.reader(open(os.path.join(D,'papers.csv'),encoding='utf8')) if r and not r[0].startswith('#')}
ORDER={r[0].replace('\\','/'):r[2].split('|') for r in csv.reader(open(os.path.join(D,'papers.csv'),encoding='utf8')) if len(r)>2 and not r[0].startswith('#')}  # friends in author order
G=json.load(open(os.path.join(D,'graph.json'),encoding='utf8'))
# friends: slug -> folders
FOLD=collections.defaultdict(set)
for f in glob.glob(os.path.join(FR,'*.json')):
    d=json.load(open(f,encoding='utf8')); d=d.get('data',d)
    for x in (d.get('folder') or '').split(','):
        if x.strip(): FOLD[x.strip()].add(os.path.basename(f)[:-5])
SEED1={'luis-colmenarez','dominik-hahn','maurits-tepaske'}; SEED2={'deepak-dhar','katarzyna-macieszczak','marzena-szymanska'}
NB=collections.defaultdict(set)
for a,b,w in G['edges']: NB[a].add(b); NB[b].add(a)
dist={s:0 for s in SEED1|SEED2}; q=list(dist)
while q:
    x=q.pop(0)
    for y in NB[x]:
        if y not in dist: dist[y]=dist[x]+1; q.append(y)
def top(f):  # top folder below MIPT, or the root folder
    p=f.split('/'); return p[1] if p[0]=='MIPT' and len(p)>2 else p[0]
NPDF=collections.Counter()
for dp,_,fs in os.walk(ROOT):
    for fn in fs:
        if fn.lower().endswith('.pdf'): NPDF[top(os.path.relpath(os.path.join(dp,fn),ROOT).replace('\\','/'))]+=1
def rank(f,authors):
    owners=FOLD.get(top(f),set())
    if not owners: return (9,99,NPDF[top(f)])
    if owners&SEED1&authors: return (0,0,NPDF[top(f)])
    if owners&SEED1: return (1,0,NPDF[top(f)])
    return (2,min(dist.get(o,50) for o in owners),NPDF[top(f)])
def annots(f):
    try: b=open(os.path.join(ROOT,f),'rb').read()
    except Exception: return 0
    return len(re.findall(rb'/Subtype\s*/(?:Highlight|Ink|Text|FreeText|Underline|StrikeOut|Square|Circle|Line|Polygon|PolyLine|Squiggly)\b',b))
# exact titles: bib title if the PDF matched a bib entry, else arXiv's title
def arxiv_id(f,u):
    m=re.search(r'(\d{4}\.\d{4,5})(v\d+)?',os.path.basename(f)) or re.search(r'arxiv.org/abs/(\d{4}\.\d{4,5})',u or '')
    return m.group(1) if m else None
need=[arxiv_id(p['f'],p['u']) for p in P if HOW.get(p['f']) not in ('doi','arxiv','physrev','title')]
need=sorted(set(x for x in need if x)); AX={}
for i in range(0,len(need),40):
    u='http://export.arxiv.org/api/query?'+urllib.parse.urlencode({'id_list':','.join(need[i:i+40]),'max_results':40})
    for k in range(4):
        try: x=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'paper-fetch/1.0'}),timeout=60).read().decode(); break
        except Exception as e: time.sleep(15*(k+1)); x=''
    for e in re.findall(r'<entry>(.*?)</entry>',x,re.S):
        m=re.search(r'<id>http://arxiv.org/abs/([\d.]+)',e); t=re.search(r'<title>(.*?)</title>',e,re.S)
        if m and t: AX[m.group(1)]=' '.join(t.group(1).split())
    time.sleep(3)
for p in P:
    if HOW.get(p['f']) in ('doi','arxiv','physrev','title'): p['T']=p['t']
    else: p['T']=AX.get(arxiv_id(p['f'],p['u']) or '-')
# group copies of the same paper (union-find over link and exact title)
par=list(range(len(P)))
def fnd(i):
    while par[i]!=i: par[i]=par[par[i]]; i=par[i]
    return i
seen={}
for i,p in enumerate(P):
    keys=[]
    if p['u']: keys.append('u:'+p['u'].lower())
    if p.get('T'): keys.append('t:'+norm(p['T']))
    for k in keys:
        if k in seen: par[fnd(i)]=fnd(seen[k])
        else: seen[k]=i
groups=collections.defaultdict(list)
for i,p in enumerate(P): groups[fnd(i)].append(p)
def clean(t):
    t=re.sub(r'[‐-―]','-',t)
    t=re.sub(r'\$([^$]*)\$',lambda m:re.sub(r'[\\{}^_]','',m.group(1)),t); t=re.sub(r'[{}\\]','',t)
    t=t.replace(':',' -').replace('/','-'); t=re.sub(r'[*?"<>|]','',t); return ' '.join(t.split())
def newname(p,keep_dir):
    n=os.path.basename(p['f']); m=re.match(r'(.*?)( \[[^\]]*\])?\.pdf$',n,re.I); stem,tag=m.group(1),m.group(2) or ''
    idm=re.search(r'(\d{4}\.\d{4,5}(?:v\d+)?)',stem) or re.search(r'(Phys[A-Za-z]*\.\d+\.[A-Za-z0-9]+)',stem)
    idp=idm.group(1) if idm else (arxiv_id(p['f'],p['u']) or '')
    if not p.get('T'): return keep_dir+'/'+n
    t=clean(p['T'])[:140]
    room=235-len(ROOT)-len(keep_dir)-len(idp)-len(tag)-6; t=t[:max(40,room)].rstrip(' ,.-')  # stay under the 260-char path limit
    return keep_dir+'/'+(idp+'_' if idp else '')+t+tag+'.pdf'
ops=[]  # (kind, src, dst)
for g in groups.values():
    if any('2403.01912' in p['f'] for p in g) and len(g)>1: g=g[:1]+[]  # Lazarides v1+v2 stay (Tony)
    authors=set(g[0]['a'])
    best=min(g,key=lambda p:(rank(p['f'],authors),p['f']))
    loc=os.path.dirname(best['f'])
    if top(best['f'])=='David' and authors&SEED1 and not (FOLD.get('David',set())&authors&SEED1):
        NAME2SLUG={json.load(open(f,encoding='utf8')).get('data',{}).get('name') or json.load(open(f,encoding='utf8')).get('name'):os.path.basename(f)[:-5] for f in glob.glob(os.path.join(FR,'*.json'))}
        who=[NAME2SLUG.get(n) for n in ORDER.get(g[0]['f'],[]) if NAME2SLUG.get(n) in SEED1][0]  # first in author order
        own=[k for k,v in FOLD.items() if v=={who}]
        if own: loc='MIPT/'+own[0]
    content=max(g,key=lambda p:(annots(p['f']),os.path.getsize(os.path.join(ROOT,p['f']))))
    if top(content['f'])==top(loc+'/x') and loc==os.path.dirname(best['f']): loc=os.path.dirname(content['f'])  # same top folder: leave the file in its subfolder
    dst=newname(content,loc)
    for p in g:
        if p is not content: ops.append(('delete',p['f'],content['f']))
    if dst!=content['f']: ops.append(('rename',content['f'],dst))
for k,s,d in ops: print(k.upper(),'|',s,'->',d)
print(collections.Counter(k for k,_,_ in ops),'groups with copies:',sum(1 for g in groups.values() if len(g)>1),'no exact title:',sum(1 for p in P if not p.get('T')))
if APPLY:
    for k,s,d in ops:
        if k=='delete': os.remove(os.path.join(ROOT,s))
    for k,s,d in ops:
        if k=='rename':
            os.makedirs(os.path.dirname(os.path.join(ROOT,d)),exist_ok=True)
            assert not os.path.exists(os.path.join(ROOT,d)),d
            os.rename(os.path.join(ROOT,s),os.path.join(ROOT,d))
    if LOG:
        with open(LOG,'w',newline='',encoding='utf8') as fh: csv.writer(fh).writerows([('action','old','new_or_kept')]+ops)
    print('applied')
