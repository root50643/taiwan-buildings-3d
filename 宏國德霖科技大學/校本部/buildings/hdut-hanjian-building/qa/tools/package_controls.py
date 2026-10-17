"""Package only fresh synthetic evidence and its exact tool sources; verify/rebuild."""
from pathlib import Path
import argparse,json,shutil,tempfile
from build_controls_archive import FORMAT,make_archive,digest
from archive_verify import verify
from run_full_qa import QA,source_inventory
from qa_common import require,sha256,write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--observed',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();require(not a.out.exists(),'Package output must be new');a.out.mkdir(parents=True);summary=json.loads((a.observed/'controls-suite-summary.json').read_text());require(summary.get('passed') is True and summary.get('tool_sources_sha256')==source_inventory(),'Control suite failed or tool sources changed')
    with tempfile.TemporaryDirectory(dir=a.out,prefix='package-work-') as tmp:
        root=Path(tmp)
        for name in source_inventory():
            dst=root/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(QA/name,dst)
        omitted=[]
        for path in sorted(a.observed.rglob('*')):
            rel=path.relative_to(a.observed)
            # Archive verifier controls deliberately create symlinks and extracted
            # fixtures. The indexed profile only permits ordinary file members.
            if path.is_symlink():omitted.append(str(rel));continue
            if not path.is_file():continue
            dst=root/'observed'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dst)
        write_json(root/'ARCHIVE-SCOPE.json',{'scope':'Fresh synthetic fixtures, observed evidence, and exact reusable source. No project model, old model results, counts, exceptions or waivers.','omitted_nonregular_symlinks':omitted,'replay':'python -B tools/run_control_suite.py --out replay-results','archive_reproducibility':'Observed bytes reproduce exactly; elapsed times/runtime platform fields mean a new execution need not be byte-identical.'})
        members=sorted([{'path':str(x.relative_to(root)),'bytes':x.stat().st_size,'sha256':sha256(x)} for x in root.rglob('*') if x.is_file()],key=lambda row:row['path'])
        raw,compressed=make_archive(root,members);(a.out/'controls.tar.xz').write_bytes(compressed);write_json(a.out/'controls-index.json',{'format':FORMAT,'archive_sha256':digest(compressed),'tar_sha256':digest(raw),'members':members})
        verified,tar,records=verify(a.out/'controls.tar.xz',a.out/'controls-index.json')
        raw2,compressed2=make_archive(root,members);require(raw2==raw and compressed2==compressed,'Deterministic rebuild differs')
        write_json(a.out/'packaging-result.json',dict(verified,bitwise_rebuild_verified=True,ordinary_files_only=True))
    print(json.dumps({'passed':True,'archive':str(a.out/'controls.tar.xz'),'members':len(members),'archive_sha256':digest(compressed)}))
if __name__=='__main__':main()
