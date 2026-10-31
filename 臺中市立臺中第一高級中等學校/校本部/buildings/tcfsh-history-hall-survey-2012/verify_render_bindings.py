from pathlib import Path
import hashlib,json,struct
p=Path(__file__).resolve().parent
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
records=[]
for view in json.loads((p/'render-manifest.json').read_text())['views']:
 n=view['name'];q=p/'previews'/f'{n}.png';b=json.loads((p/'previews'/f'{n}.render.json').read_text())
 w,h=struct.unpack('>II',q.read_bytes()[16:24])
 checks={'png_hash':sha(q)==b['png_sha256'],'mesh_hash':sha(p/'mesh-data.npz')==b['mesh_sha256'],'script_hash':sha(p/'render_model.py')==b['renderer_script_sha256'],'dimensions':[w,h]==b['resolution'],'camera':view['camera']==b['camera'],'target':view['target']==b['target'],'scale':view['ortho_scale']==b['ortho_scale']}
 records.append({'view':n,'checks':checks,'passed':all(checks.values()),'png_sha256':sha(q),'rendered_at_utc':b['rendered_at_utc']})
r={'checks':records,'passed':all(x['passed']for x in records)}
(p/'RENDER-BINDING-QA.json').write_text(json.dumps(r,indent=2));print(r['passed']);assert r['passed']
