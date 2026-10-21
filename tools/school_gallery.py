#!/usr/bin/env python3
"""Audit/sync PRIMARY school/campus galleries, never publication-history footers.

Run before publishing: python tools/school_gallery.py --check --report report.json
To insert new packages: python tools/school_gallery.py --sync, review diff, then --check.
Uses the complete Git index plus untracked package files, so sparse checkout works.
Model identity is buildings/<slug>, not an STL/version/appearance file count.
"""
import argparse, collections, hashlib, html, json, os, pathlib, posixpath, re, subprocess, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
# Never trigger an implicit large promisor fetch during a navigation check.
os.environ['GIT_NO_LAZY_FETCH'] = '1'

def git(*args):
    return subprocess.check_output(['git', '-c', 'core.quotepath=false', *args])

def inventory():
    return set(git('ls-files', '-z').decode().split('\0')) | set(git('ls-files', '--others', '--exclude-standard', '-z').decode().split('\0')) - {''}

FILES = inventory()
CACHE = {}
def read(path):
    if (ROOT/path).is_file(): return (ROOT/path).read_text()
    if path not in CACHE: CACHE[path] = git('show', ':'+path).decode()
    return CACHE[path]

REGISTRY = json.loads(read('model-packages.json'))
SCHOOLS = set(REGISTRY['schools']) | {'國立聯合大學'}
ROOTS = sorted({p.split('/buildings/')[0]+'/buildings/'+p.split('/buildings/')[1].split('/')[0]
                for p in FILES if '/buildings/' in p and p.split('/')[0] in SCHOOLS})
# The church is a legacy package, not a new-catalog package; include it in THU navigation once.
LEGACY = {'東海大學': ['臺灣地標/luce-chapel']}
BY_SCHOOL = {s:[r for r in ROOTS if r.startswith(s+'/')]+LEGACY.get(s,[]) for s in sorted(SCHOOLS)}
OTHER_ROOTS = {
    '國家衛生研究院竹南院區/README.md': sorted({p.split('/buildings/')[0]+'/buildings/'+p.split('/buildings/')[1].split('/')[0] for p in FILES if p.startswith('國家衛生研究院竹南院區/') and '/buildings/' in p}),
    '臺灣地標/README.md': sorted({'/'.join(p.split('/')[:2]) for p in FILES if p.startswith('臺灣地標/') and p.count('/')>=2})
}
URL = re.compile(r'\]\(([^\n]*?)\)|(?:src|href)=[\"\']([^\"\']+)[\"\']')
def urls(text):
    return [a or b for a,b in URL.findall(text)]
def resolve(url,page):
    url=html.unescape(urllib.parse.unquote(url.strip('<>'))).split('#')[0].split('?')[0]
    if not url or re.match(r'\w+:',url): return None
    return posixpath.normpath(posixpath.join(posixpath.dirname(page),url))
def identities(text,page,expected):
    found=[]
    for u in urls(text):
        target=resolve(u,page)
        if target:
            for r in expected:
                if target==r or target.startswith(r+'/'): found.append(r)
    return set(found)
def table(text,page,expected):
    # Adjacent tables separated only by blank lines form one primary gallery.
    lines=text.splitlines(keepends=True); start=None
    for i,line in enumerate(lines+['STOP']):
        if line.startswith('|'):
            if start is None: start=i
        elif start is not None and line.strip():
            end=i
            while end>start and not lines[end-1].strip():end-=1
            if identities(''.join(lines[start:end]),page,expected): return lines,start,end
            start=None
    return lines,None,None

def gallery_cells(lines,a,b,page,expected):
    # Skip each repeated table heading/alignment row, retain genuine cards and padding.
    cells=[]
    for line in lines[a:b]:
        if line.startswith('|') and identities(line,page,expected):cells.extend(splitrow(line))
    return cells

def splitrow(row):
    return [x.strip() for x in re.split(r'(?<!\\)\|',row.strip())[1:-1]]

def exists(path):
    return path in FILES or any(p.startswith(path.rstrip('/')+'/') for p in FILES)

def new_card(root,page):
    candidates=[root+'/README.md',root+'/README.zh-TW.md']
    rd=next((p for p in candidates if p in FILES),None)
    if not rd: raise ValueError('No model README: '+root)
    text=read(rd)
    title=next((l[2:].strip() for l in text.splitlines() if l.startswith('# ')),root.rsplit('/',1)[-1])
    title=re.sub(r'\s*[｜|]?\s*3D\s*(?:列印|模型).*$', '',title).strip() or title
    title=html.escape(title.replace('|','｜'))
    # Preserve an explicitly chosen special preview from existing page/model docs when standard front is absent.
    preview=next((p for p in [root+'/appearance/previews/front.png',root+'/previews/front.png'] if p in FILES),None)
    if not preview:
        for source,source_page in [(read(page),page),(text,rd)]:
            for u in urls(source):
                p=resolve(u,source_page)
                if p and p.startswith(root+'/') and re.search(r'\.(png|jpg|webp)$',p,re.I) and p in FILES:
                    preview=p;break
            if preview:break
    if not preview: raise ValueError('No existing preview: '+root)
    base=posixpath.dirname(page); link=posixpath.relpath(rd,base); image=posixpath.relpath(preview,base)
    return f'[<img src="{image}" alt="{title}：實際模型預覽" width="220">]({link})<br>**[{title}]({link})**'

def pages():
    result={s+'/README.md':rs for s,rs in BY_SCHOOL.items()}
    result.update(OTHER_ROOTS)
    for r in ROOTS:
        prefix=r.split('/buildings/')[0]
        if prefix.count('/')==1:
            if prefix+'/README.md' in FILES:result.setdefault(prefix+'/README.md',[]).append(r)
    return result

def primary_list(text,page,expected):
    # Preserve complete non-table catalogs; appended 'new/update' logs are not the primary list.
    primary=re.split(r'(?m)^#{1,3}\s*(?:(?:最新|本次)?新增|補建|更新紀錄|歷史紀錄)',text,maxsplit=1)[0]
    return primary,identities(primary,page,expected)

def sync(page,expected):
    text=read(page); lines,a,b=table(text,page,expected)
    original=text
    if a is None:
        primary,present=primary_list(text,page,expected)
        if present==set(expected):return False
    else:present=identities(''.join(lines[a:b]),page,expected)
    missing=sorted(set(expected)-present)
    if missing:
        # Keep historical/specialized multi-view tables verbatim; add only missing package cards
        # INSIDE the same primary gallery group, before the following narrative/section.
        cells=[new_card(r,page) for r in missing]
        cells+=['']*((-len(cells))%3)
        body='| 建築模型 | 建築模型 | 建築模型 |\n| :---: | :---: | :---: |\n'+''.join('| '+' | '.join(cells[i:i+3])+' |\n' for i in range(0,len(cells),3))
        if a is None:
            insert=next((i+1 for i,l in enumerate(lines) if l.startswith('# ')),0)
            # Only previously incomplete non-table pages get a primary gallery.
            cells=[new_card(r,page) for r in sorted(expected)]
            cells+=['']*((-len(cells))%3)
            body='| 建築模型 | 建築模型 | 建築模型 |\n| :---: | :---: | :---: |\n'+''.join('| '+' | '.join(cells[i:i+3])+' |\n' for i in range(0,len(cells),3))
            lines[insert:insert]=['\n## 現行完整模型圖鑑\n\n'+f'現行收錄 **{len(expected)} 套**；套件不等於整棟建築，亦非全校／校區完成。\n\n'+body+'\n## 既有說明與更新紀錄\n\n']
        else:lines[b:b]=['\n'+body]
        text=''.join(lines)
    # Match angle-for-angle appearance previews, rather than demanding front for a rear-view cell.
    lines,a,b=table(text,page,expected)
    if a is not None:
        group=''.join(lines[a:b])
        for u in urls(group):
            target=resolve(u,page)
            if not target:continue
            for r in expected:
                if target.startswith(r+'/previews/'):
                    preferred=r+'/appearance/'+target[len(r)+1:]
                    if preferred in FILES:
                        group=group.replace(u,posixpath.relpath(preferred,posixpath.dirname(page)))
        lines[a:b]=[group];text=''.join(lines)
    if text==original:return False
    p=ROOT/page;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);return True

def duplicate_new_footer_entries(text,page,expected):
    """Reject new-model footer cards once the same model is in the primary gallery.

    Existing detailed <details> documentation and explicitly labeled QA/revision
    records are not duplicate catalog cards and must not be deleted automatically.
    """
    lines,a,b=table(text,page,expected)
    if a is None:return []
    primary=identities(''.join(lines[a:b]),page,expected)
    offset=len(''.join(lines[:b]));heads=list(re.finditer(r'(?m)^(#{1,4})\s+[^\n]+',text));duplicates=[]
    for i,h in enumerate(heads):
        if h.start()<offset or not re.search('新增|補建',h[0]):continue
        if re.search('覆核|驗證|修版|歷史紀錄',h[0]):continue
        end=next((n.start() for n in heads[i+1:] if len(n[1])<=len(h[1])),len(text))
        section=text[h.start():end]
        if '<details>' in section:continue
        # Match root-level model navigation, not unrelated appearance/QA footnotes.
        roots=set()
        for u in urls(section):
            target=resolve(u,page)
            for root in expected:
                if target in (root,root+'/README.md',root+'/README.zh-TW.md'):roots.add(root)
        duplicates.extend(sorted(roots & primary))
    return sorted(set(duplicates))

def audit(page,expected):
    text=read(page);lines,a,b=table(text,page,expected);errors=[]
    if a is None:
        primary,found=primary_list(text,page,expected);kind='existing_non_table_catalog'
    else:primary=''.join(lines[a:b]);found=identities(primary,page,expected);kind='primary_table_group'
    missing=sorted(set(expected)-found)
    all_roots=set(ROOTS).union(*(set(v) for v in OTHER_ROOTS.values()))
    extra=sorted(identities(primary,page,all_roots)-set(expected))
    if extra:errors.append('out_of_scope_packages')
    if missing:errors.append('missing_packages')
    broken=[];stale=[]
    for u in urls(primary):
        p=resolve(u,page)
        if p and not exists(p):broken.append(u)
        if p:
            for r in expected:
                if p.startswith(r+'/previews/') and r+'/appearance/'+p[len(r)+1:] in FILES:stale.append(p)
    if broken:errors.append('broken_relative_links')
    if stale:errors.append('stale_preview')
    # Validate each table against its own column schema. Existing two-angle/row catalogs
    # are intentional; the generated catalog blocks always have three columns.
    structural=[];new_cards=[]
    blocks=re.findall(r'(?m)(?:^\|.*\n?)+',primary)
    for block in blocks:
        rows=block.splitlines();cols=len(splitrow(rows[0]))
        if any(len(splitrow(row))!=cols for row in rows):structural.append('inconsistent_columns')
        if rows[0]=='| 建築模型 | 建築模型 | 建築模型 |':
            cells=[c for row in rows[2:] for c in splitrow(row)]
            nonblank=[c for c in cells if c]
            if cols!=3 or len(cells)%3:structural.append('generated_not_three_columns')
            if cells[:len(nonblank)]!=nonblank:structural.append('non_terminal_padding')
            for c in nonblank:
                ids=identities(c,page,expected)
                if len(ids)!=1:structural.append('generated_card_not_one_package')
                new_cards.extend(ids)
    duplicate_cards=sorted(k for k,n in collections.Counter(new_cards).items() if n>1)
    if duplicate_cards:errors.append('duplicate_generated_cards')
    repeated_footer=duplicate_new_footer_entries(text,page,expected)
    if repeated_footer:errors.append('duplicate_new_model_footer')
    errors+=structural
    return dict(path=page,primary_kind=kind,expected_count=len(expected),primary_count=len(found),missing=missing,extra=extra,duplicates=duplicate_cards,duplicate_new_footer_packages=repeated_footer,broken_links=sorted(set(broken)),stale_previews=sorted(set(stale)),errors=sorted(set(errors)))

def main():
    ap=argparse.ArgumentParser(__doc__);ap.add_argument('--sync',action='store_true');ap.add_argument('--check',action='store_true');ap.add_argument('--report');ap.add_argument('--text-cache', help='Optional UTF-8 JSON path→text cache at the same reviewed Git ref (for offline sparse checkout)');args=ap.parse_args()
    if args.text_cache:
        cached=json.loads(pathlib.Path(args.text_cache).read_text())
        indexed={}
        for row in git('ls-files','-s','-z').decode().split('\0'):
            if row:
                meta,name=row.split('\t',1);indexed[name]=meta.split()[1]
        for name,txt in cached.items():
            if (ROOT/name).is_file():continue
            raw=txt.encode();sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            if indexed.get(name)!=sha:raise ValueError('Text cache does not match Git index: '+name)
            CACHE[name]=txt
    changed=[];results=[]
    for page,expected in pages().items():
        if page not in FILES:
            if not args.sync:raise ValueError('Missing canonical navigation README: '+page)
            p=ROOT/page;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text('# '+posixpath.dirname(page).replace('/', '｜')+'\n\n[回學校圖鑑](../README.md)\n')
            FILES.add(page)
        if args.sync and sync(page,expected):changed.append(page)
        results.append(audit(page,expected))
    count_errors=[]
    actual_all=len(set(ROOTS).union(*(set(v) for v in OTHER_ROOTS.values())))
    actual_higher=sum(map(len,BY_SCHOOL.values()))
    if REGISTRY.get('total_packages')!=actual_all:count_errors.append('registry_total_packages')
    if REGISTRY.get('higher_education_model_packages')!=actual_higher:count_errors.append('registry_higher_education_packages')
    for school,roots in BY_SCHOOL.items():
        if school in REGISTRY['schools'] and REGISTRY['schools'][school]['count']!=len(roots)-len(LEGACY.get(school,[])):count_errors.append('registry_school_count:'+school)
    report={'count_errors':count_errors,'scope':'primary school/campus galleries; exact package-root equality, not full-page mentions','school_count':len(SCHOOLS),'higher_education_packages':sum(map(len,BY_SCHOOL.values())),'all_repository_packages':len(set(ROOTS).union(*(set(v) for v in OTHER_ROOTS.values()))),'pages':results,'changed':changed,'passed':not count_errors and all(not r['errors'] for r in results)}
    if args.report:pathlib.Path(args.report).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'schools':len(SCHOOLS),'pages':len(results),'packages':report['higher_education_packages'],'changed':len(changed),'count_errors':count_errors,'failures':[r for r in results if r['errors']]},ensure_ascii=False,indent=2))
    return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
