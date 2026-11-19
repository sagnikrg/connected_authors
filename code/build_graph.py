import os,re,glob,json,sys,subprocess,unicodedata,csv
# Friends co-author graph from Tony's paper collection.
# Usage: python -I build_graph.py <graph_dir> <bib_dir> <root1> [<root2> ...]
#   <graph_dir>/friends/*.json : friend docs exported from the friends artifact (name per slug)
# Writes <graph_dir>/papers.csv (file, matched_by, friends, year) and <graph_dir>/graph.json
S=sys.argv[1]; BIB=sys.argv[2]; ROOTS=sys.argv[3:]
A=lambda s: unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode()
core=[json.load(open(f,encoding='utf8'))['name'] for f in glob.glob(S+'/friends/*.json')]
special={"Andrea De Luca":("De Luca","a"),"Sankar Das Sarma":("Das Sarma","s"),"Mari Carmen Bañuls":("Banuls","m"),"G. J. Sreejith":("Sreejith","g"),"Sid Parameswaran":("Parameswaran","s"),"Yevgeny Bar Lev":("Bar Lev","y"),"Wojciech De Roeck":("De Roeck","w"),"Curt W. von Keyserlingk":("von Keyserlingk","c"),"Thomas Klein Kvorning":("Klein Kvorning","t"),"David Aceituno Chavez":("Aceituno Chavez","d")}
C={}
for n in core:
    last,ini=special.get(n,(A(n).split()[-1],A(n)[0].lower()))
    C[(A(last).lower().replace(' ','').replace('-',''),ini)]=(A(last),n)
def key(last,first): return (A(last).lower().replace(' ','').replace('-',''),(A(first).strip()[:1] or '?').lower())
# bib index
ent=[]
for f in glob.glob(BIB+'/*.bib'):
    for m in re.finditer(r'@\w+\s*\{[^,]+,(.*?)(?=\n@|\Z)',open(f,encoding='utf8',errors='ignore').read(),re.S):
        b=m.group(1)
        am=re.search(r'\bauthor\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}',b,re.S)
        if not am: continue
        g=lambda k:(re.search(r'\b'+k+r'\s*=\s*[{"]([^}"]*)',b) or [None,''])[1]
        t=re.search(r'\btitle\s*=\s*[{"](.*?)[}"]\s*,?\s*\n',b,re.S)
        au=[]
        for x in re.split(r'\s+and\s+',' '.join(re.sub(r'[{}\\"]','',am.group(1)).split())):
            if ',' in x: l,fi=[y.strip() for y in x.split(',',1)]
            else: p=x.split(); l,fi=(p[-1],' '.join(p[:-1])) if p else ('','')
            au.append(key(l,fi))
        yr=(re.search(r'(?:year|date)\s*=\s*[{"]?(\d{4})',b) or [None,''])[1]
        ent.append(dict(title=' '.join(re.sub(r'[{}\\]','',t.group(1)).split()) if t else '',yr=yr,doi=g('doi').lower(),ep=re.sub(r'v\d+$','',g('eprint').lower()),t=set(w for w in re.findall(r'[a-z0-9]+',A(t.group(1) if t else '').lower()) if len(w)>3),au=au))
import collections as _c
_y=_c.defaultdict(str)
for e in ent:
    for kk in (e['doi'],e['ep']):
        if kk and e['yr'] and not _y[kk]: _y[kk]=e['yr']
for e in ent:
    if not e['yr']: e['yr']=_y.get(e['doi'],'') or _y.get(e['ep'],'')
D={};E={}
for e in sorted(ent,key=lambda e:bool(e['yr'])):
    if e['doi']: D[e['doi']]=e
    if e['ep']: E[e['ep']]=e
def fromtext(t):
    head=t[:900]
    found=[]
    for (lk,ini),(last,n) in C.items():
        first=A(n).split()[0]
        pat=r'\b(?:'+re.escape(first)+r'|'+ini.upper()+r'\.)(?:\s+[A-Z][a-z]*\.?)*\s+'+r'\s*'.join(re.escape(x) for x in last.split())+r'(?![A-Za-z])'
        mm=re.search(pat,A(head))
        if mm: found.append((mm.start(),n))
    return [l for _,l in sorted(found)]
rows=[]; META={}
def ftitle(f):
    x=re.sub(r'\.pdf$','',f,flags=re.I); x=re.sub(r'(?:arXiv:)?\d{4}\.\d{4,5}(v\d+)?','',x); x=re.sub(r'Phys[A-Za-z]*\.\d+\.\w+','',x)
    x=re.sub(r'[_]+',' ',x); x=re.sub(r'^[\s\-.,]+|[\s\-.,]+$','',x); return ' '.join(x.split()) or f
for R in ROOTS:
    for dp,_,fs in os.walk(R):
        for f in fs:
            if not f.lower().endswith('.pdf'): continue
            p=os.path.join(dp,f)
            f=re.sub(r' \[[^\]]*\](?=\.pdf$)','',f)
            t=subprocess.run(['pdftotext','-l','1','-q',p,'-'],capture_output=True,timeout=60).stdout.decode('utf8','ignore')
            ids=re.findall(r'(\d{4}\.\d{4,5})',f+' '+t[:3000])
            dois=[d.lower().rstrip('.') for d in re.findall(r'10\.\d{4,}/[^\s,;]+',t[:4000])]
            pr=re.findall(r'(Phys[A-Za-z]*\.\d+\.\w+)',f)
            e=None;how=''
            for d in dois:
                if d in D: e=D[d];how='doi';break
            if not e:
                for i in ids:
                    if i in E: e=E[i];how='arxiv';break
            if not e:
                for x in pr:
                    for d in D:
                        if d.endswith(x.lower()): e=D[d];how='physrev';break
                    if e: break
            if not e:
                w=set(w for w in re.findall(r'[a-z0-9]+',A(re.sub(r'\.pdf$','',f)).lower()) if len(w)>3)
                best=max(ent,key=lambda e:len(w&e['t'])/max(len(e['t']),1)) if w else None
                if best and best['t'] and len(w&best['t'])/len(best['t'])>=0.8 and len(best['t'])>=3: e=best;how='title'
            if e and how in('doi','arxiv','physrev'):
                tw=set(w for w in re.findall(r'[a-z0-9]+',A(t[:4000]).lower()) if len(w)>3)
                fw=set(w for w in re.findall(r'[a-z0-9]+',A(f).lower()) if len(w)>3)
                ov=len(e['t']&(tw|fw))/max(len(e['t']),1)
                if ov<0.6: rows.append(('#REJECT '+os.path.relpath(p,os.path.dirname(R)),how,f'{ov:.2f}')); e=None
            if e:
                tags=[]
                for k in e['au']:
                    if k in C and C[k][1] not in tags: tags.append(C[k][1])
                year=e['yr']
            else:
                year=''
                how='text'; tags=[]
                for x in fromtext(t):
                    if x not in tags: tags.append(x)
            if not year:
                m2=re.search(r'(?<![\d.])([0-2]\d)(0[1-9]|1[0-2])\.\d{4,5}',f) or re.search(r'(?<![\d.])([0-2]\d)(0[1-9]|1[0-2])\.\d{4,5}',t[:1500])
                if m2: year='20'+m2.group(1)
                else:
                    m3=re.search(r'(?<!\d)(19[5-9]\d|20[0-2]\d)(?!\d)',f)
                    year=m3.group(1) if m3 else ''
            rel=os.path.relpath(p,os.path.dirname(R))
            link=('https://doi.org/'+e['doi']) if e and e['doi'] else ('https://arxiv.org/abs/'+e['ep']) if e and e['ep'] else ('https://arxiv.org/abs/'+ids[0]) if ids and re.search(re.escape(ids[0]),f) else ''
            META[rel]=((e['title'] if e and e['title'] else ftitle(f)),link)
            rows.append((rel,how,'|'.join(tags),year))
with open(S+'/papers.csv','w',newline='',encoding='utf8') as fh: csv.writer(fh).writerows(rows)
import collections
rows=[r for r in rows];print(len(rows),collections.Counter(r[1] for r in rows),'tagged:',sum(1 for r in rows if r[2]))

# ---- graph ----
import itertools,datetime
slug={json.load(open(f,encoding='utf8'))['name']:os.path.basename(f)[:-5] for f in glob.glob(S+'/friends/*.json')}
cnt=collections.Counter(); ed=collections.Counter(); seen=set()
for r in rows:
    if r[0].startswith('#') or len(r)<3 or not r[2]: continue
    ids=sorted(set(slug[n] for n in r[2].split('|') if n in slug))
    for i in ids: cnt[i]+=1
    for a,b in itertools.combinations(ids,2): ed[(a,b)]+=1
g={"nodes":{k:cnt.get(k,0) for k in slug.values()},"edges":[[a,b,w] for (a,b),w in sorted(ed.items())],
   "papers":sum(1 for r in rows if not r[0].startswith('#')),"built":datetime.date.today().isoformat(),
   "source":"Dropbox/MIPT + Dropbox/Quantum circuit"}
json.dump(g,open(S+'/graph.json','w',encoding='utf8'))
# per-paper list for the paper lists in the graph pages: t title, y year, f file (relative to Dropbox), a friend slugs, u link
PL=[]
for r in rows:
    if r[0].startswith('#') or not r[2]: continue
    ids_=sorted(set(slug[n] for n in r[2].split('|') if n in slug))
    if ids_: PL.append({"t":META[r[0]][0],"y":r[3],"f":r[0].replace(os.sep,"/"),"a":ids_,"u":META[r[0]][1]})
json.dump({"papers":PL,"built":g['built']},open(S+'/papers.json','w',encoding='utf8'),ensure_ascii=False)
print('paper list',len(PL))
print('nodes',len(g['nodes']),'edges',len(g['edges']),'max edge',max((e[2] for e in g['edges']),default=0))
