"""Use Python with lib3mf==2.5.0 and numpy. One mesh, one neutral preview material.
python export_3mf.py [--out DIRECTORY]. Not a source-faithful color restoration.
"""
import argparse,pathlib,json,zipfile,uuid,hashlib
import numpy as np
import lib3mf
ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);a=ap.parse_args();r=a.out;d=np.load(r/'mesh-data.npz');p=json.loads((r/'params.json').read_text());w=lib3mf.get_wrapper();m=w.CreateModel();m.SetUnit(lib3mf.ModelUnit.MilliMeter);g=m.AddBaseMaterialGroup();c=lib3mf.Color();c.Red,c.Green,c.Blue,c.Alpha=[round(x*255) for x in p['neutral_preview_rgba']];mi=g.AddMaterial('Neutral preview only - not restored facade color',c);o=m.AddMeshObject();o.SetName('NSYSU Library corrected existing main block');vs=[];fs=[];ps=[]
for v in d['vertices']:
 q=lib3mf.Position();q.Coordinates[:]=[float(x) for x in v];vs.append(q)
for f in d['faces']:
 q=lib3mf.Triangle();q.Indices[:]=[int(x) for x in f];fs.append(q);q=lib3mf.TriangleProperties();q.ResourceID=g.GetResourceID();q.PropertyIDs[:]=[mi]*3;ps.append(q)
o.SetGeometry(vs,fs);o.SetAllTriangleProperties(ps);t=lib3mf.Transform();t.Fields[0][0]=t.Fields[1][1]=t.Fields[2][2]=1;item=m.AddBuildItem(o,t)
# Stable production-extension identifiers derived only from public geometry, not random writer UUIDs.
identity=hashlib.sha256(d['vertices'].tobytes()+d['faces'].tobytes()).hexdigest()
for obj,label in [(o,'mesh'),(item,'item')]:obj.SetUUID(str(uuid.uuid5(uuid.NAMESPACE_URL,'nsysu-library-main-block/'+identity+'/'+label)))
m.SetBuildUUID(str(uuid.uuid5(uuid.NAMESPACE_URL,'nsysu-library-main-block/'+identity+'/build')))
path=r/'model.3mf';m.QueryWriter('3mf').WriteToFile(str(path))
# ZIP timestamps/compression are normalized for reproducible public bytes.
with zipfile.ZipFile(path) as z:members={n:z.read(n) for n in z.namelist()}
with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for n,b in sorted(members.items()):
  i=zipfile.ZipInfo(n,date_time=(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o644<<16;z.writestr(i,b,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
reader=w.CreateModel().QueryReader('3mf');reader.SetStrictModeActive(True);reader.ReadFromFile(str(path));assert reader.GetWarningCount()==0
print('3MF strict read PASS, one preview material, millimetres')
