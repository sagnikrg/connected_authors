# connected_authors

**Connected Authors: Sagnik Edition**: an interactive co-author graph of the physicists whose papers are in my collection.

- Bubble size: number of their papers in my collection.
- Line thickness: number of papers in my collection the two wrote together.
- Live page: <https://sagnikrg.github.io/connected-authors/>

## Layout

| path | what |
|---|---|
| `code/build_graph.py` | scans the paper PDFs, matches each to a bib entry (DOI / arXiv / PhysRev id, checked against the page-1 title), else reads the page-1 author line; writes `papers.csv` and `graph.json` |
| `code/build_share.py` | embeds `graph.json` + names into `share_template.html` |
| `code/share_template.html` | the graph page (d3 v7 force layout) |
| `data/friends/*.json` | the people on the list (name, folder, co-author note); file name = id |
| `data/papers.csv` | every PDF scanned: file, how it was matched, people on it, year |
| `data/graph.json` | nodes (id → paper count) and edges (id, id, shared papers) |
| `site/index.html` | full standalone page, copied to `sagnikrg.github.io/connected-authors/` |
| `site/embed.html` | graph area only, no panel, no scrolling; embedded at 776:547 on the homepage (`--embed`); `--caption` prints the homepage caption |
| `artifact/friends_page.html` | source of the private friends page (Claude artifact) |

The PDFs themselves stay in Dropbox (`MIPT/`, `Quantum circuit/`) and are not part of this repo.

## Update when new papers come in

```sh
# 1. rescan (bib dir = Thesis bib files)
python -I code/build_graph.py data "<Thesis>/tex/.src/.bib" "<Dropbox>/MIPT" "<Dropbox>/Quantum circuit"
# 2. rebuild the standalone page
python -I code/build_share.py data code/share_template.html site/index.html --standalone
python -I code/build_share.py data code/share_template.html site/embed.html --standalone --embed --caption
# 3. copy site/index.html and site/embed.html to sagnikrg.github.io/connected-authors/,
#    paste the --caption line into the <sub> under the iframe in its README.md, commit + push both repos
```

New people go into `data/friends/<id>.json` (`{"name": ...}`) before step 1.
