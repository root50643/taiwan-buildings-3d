#!/usr/bin/env python3
"""Check every building/landmark main README: H1, first-section gallery, local image targets.
Run from a checkout: python tools/validate_readme_galleries.py --root .
For an exact remote-tree audit, supply --tree tree.json and ordered --overlay paths.
QA, source, batch and archived nested READMEs are not building landing pages.
"""
import argparse,json,re,posixpath,urllib.parse
from pathlib import Path
MODEL=re.compile(r'(?:.*/buildings/[^/]+|臺灣地標/[^/]+)/README(?:\.[^/]+)?\.md$')
def image_urls(text):
 return re.findall(r'!\[[^\]]*\]\(([^\n]+?)\)',text)+re.findall(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\']',text,re.I)
def inspect(path,text,known):
 errors=[];heads=list(re.finditer(r'(?m)^#{1,2} [^\n]+',text))
 if not heads or not heads[0].group().startswith('# '):errors.append('missing initial H1')
 h2=list(re.finditer(r'(?m)^## ([^\n]+)',text))
 if not h2:errors.append('missing first section');section=''
 else:
  section=text[h2[0].end():h2[1].start()if len(h2)>1 else len(text)]
  if h2[0].group(1)!='模型預覽':errors.append('first section is not 模型預覽')
 tables=[m.group()for m in re.finditer(r'(?m)^\|.*\n(?:\|[^\n]*\n?)+',section)if image_urls(m.group())]
 if not tables:errors.append('first section lacks image table')
 else:
  lines=tables[0].splitlines()
  if any(len(line.strip().strip('|').split('|'))!=3 for line in lines):errors.append('gallery must have three columns')
  if len(lines)<3 or not all(re.fullmatch(r'\s*:?-{3,}:?\s*',x)for x in lines[1].strip().strip('|').split('|')):errors.append('invalid Markdown table separator')
 urls=image_urls(text)
 if not urls:errors.append('no embedded image')
 for u in urls:
  u=u.strip('<>').split(' "')[0]
  if re.match(r'https?://|data:',u):continue
  target=posixpath.normpath(posixpath.join(posixpath.dirname(path),urllib.parse.unquote(u.split('#')[0].split('?')[0])))
  if target not in known:errors.append('missing image: '+u)
 return errors
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--tree',type=Path);p.add_argument('--overlay',type=Path,action='append',default=[]);p.add_argument('--report',type=Path);a=p.parse_args()
 known={x['path']for x in json.loads(a.tree.read_text())['tree']}if a.tree else {x.relative_to(a.root).as_posix()for x in a.root.rglob('*')if x.is_file()}
 rows=[]
 for rel in sorted(x for x in known if MODEL.fullmatch(x)):
  candidates=[d/rel for d in a.overlay]+[a.root/rel];source=next((p for p in candidates if p.exists()),None)
  errors=inspect(rel,source.read_text(),known)if source else ['README unavailable']
  rows.append({'path':rel,'errors':errors})
 report={'pages':len(rows),'model_directories':len({x['path'].rsplit('/',1)[0]for x in rows}),'failures':[x for x in rows if x['errors']]}
 if a.report:a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False,indent=2));return bool(report['failures'])
if __name__=='__main__':raise SystemExit(main())
