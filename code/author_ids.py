"""ORCID and Google Scholar ids of the friends -> data/author_ids.json {slug: {orcid, scholar}}.
ORCID: from Crossref records of the friend's own papers in the collection (DOI links of data/papers.json), author matched by surname.
Scholar + ORCID fallback: Wikidata (P496 ORCID, P1960 Google Scholar author id), person found by exact name + a physicist-ish description.
Existing entries are kept (hand fixes stay); run: python -I code/author_ids.py data"""
import json,glob,os,sys,re,unicodedata,urllib.request,urllib.parse,collections,time
D=sys.argv[1]; OUT=os.path.join(D,'author_ids.json')
A=lambda s: unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
UA={'User-Agent':'connected-authors/1.0 (research co-author graph)'}
def get(u):
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
        except Exception as e: err=e; time.sleep(2)
    print('fail',u,err); return None
names={os.path.basename(f)[:-5]:json.load(open(f,encoding='utf8'))['name'] for f in glob.glob(os.path.join(D,'friends','*.json'))}
ids=json.load(open(OUT,encoding='utf8')) if os.path.exists(OUT) else {}
P=json.load(open(os.path.join(D,'papers.json'),encoding='utf8'))['papers']
for s,n in sorted(names.items()):
    e=ids.setdefault(s,{})
    if not e.get('orcid'):
        votes=collections.Counter(); last=A(n.split()[-1])
        for p in [p for p in P if s in p['a'] and 'doi.org/' in p['u']][:6]:
            r=get('https://api.crossref.org/works/'+urllib.parse.quote(p['u'].split('doi.org/')[1]))
            for a in (r or {}).get('message',{}).get('author',[]):
                if a.get('ORCID') and A(a.get('family','')).endswith(last) and A(a.get('given',''))[:1]==A(n)[:1]:
                    votes[a['ORCID'].split('/')[-1]]+=1
        if votes: e['orcid']=votes.most_common(1)[0][0]; e['orcid_src']='crossref'
    if not e.get('scholar') or not e.get('orcid'):
        q='SELECT ?p ?o ?g ?d WHERE { ?p rdfs:label "%s"@en . ?p wdt:P31 wd:Q5 . OPTIONAL{?p wdt:P496 ?o} OPTIONAL{?p wdt:P1960 ?g} OPTIONAL{?p schema:description ?d FILTER(lang(?d)="en")} }'%n
        r=get('https://query.wikidata.org/sparql?format=json&query='+urllib.parse.quote(q))
        b=[x for x in (r or {}).get('results',{}).get('bindings',[]) if re.search('physic|scien|research|professor|mathematic',x.get('d',{}).get('value',''),re.I) or 'o' in x or 'g' in x]
        if e.get('orcid'): b=[x for x in b if x.get('o',{}).get('value')==e['orcid']] or b
        if len({x['p']['value'] for x in b})==1:
            x=b[0]
            if not e.get('orcid') and 'o' in x: e['orcid']=x['o']['value']; e['orcid_src']='wikidata'
            if not e.get('scholar') and 'g' in x: e['scholar']=x['g']['value']
        time.sleep(0.5)
    print(s,e)
json.dump(ids,open(OUT,'w',encoding='utf8'),indent=1,sort_keys=True)
print('orcid',sum(1 for e in ids.values() if e.get('orcid')),'scholar',sum(1 for e in ids.values() if e.get('scholar')),'of',len(ids))
