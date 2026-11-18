"""Build the Connected Authors pages (read-only, data embedded).

Usage:
  python -I code/build_share.py data code/share_template.html site/index.html --standalone          full page
  python -I code/build_share.py data code/embed_template.html site/embed.html --standalone --caption  website embed
  python -I code/build_share.py data code/share_template.html out.html                              Claude artifact body
--standalone wraps the page in a full HTML document for static hosting (GitHub Pages).
embed_template.html is the plot area only (no title, panel or footer); it fills its frame.
--caption prints the caption that goes under the embed on the homepage.
"""
import json,glob,os,sys
def caption(g):
    n=sum(1 for v in g['nodes'].values() if v>0)
    return (f"{n} people with papers, {len(g['edges'])} co-author links, from {g['papers']} PDFs (built {g['built']}). "
            "Click a bubble to see their co-authors in the collection. Drag bubbles, scroll or pinch to zoom, click empty space to clear.")
args=[a for a in sys.argv[1:] if not a.startswith('--')]; standalone='--standalone' in sys.argv
D,tpl,out=args
g=json.load(open(os.path.join(D,'graph.json'),encoding='utf8'))
names={os.path.basename(f)[:-5]:json.load(open(f,encoding='utf8'))['name'] for f in glob.glob(os.path.join(D,'friends','*.json'))}
people=[{"id":k,"name":names[k],"papers":v} for k,v in g['nodes'].items() if k in names]
data={"people":people,"edges":g['edges'],"papers":g['papers'],"built":g['built']}
html=open(tpl,encoding='utf8').read().replace('/*DATA*/null',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
if standalone:
    i=min(x for x in (html.find('<div class="wrap">'),html.find('<div class="stage"')) if x>=0)
    html=('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
          '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
          '<style>*,*::before,*::after{box-sizing:border-box}body{margin:0;font-size:14px}[hidden]{display:none!important}</style>\n'
          + html[:i] + '\n</head>\n<body>\n' + html[i:] + '\n</body>\n</html>\n')
open(out,'w',encoding='utf8').write(html)
if '--caption' in sys.argv: print('CAPTION:',caption(g))
print('people',len(people),'edges',len(g['edges']),'->',out)
