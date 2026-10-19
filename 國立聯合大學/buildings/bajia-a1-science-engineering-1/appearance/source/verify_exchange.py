"""Independent XML/NumPy and installed lib3mf import/edit checks; no geometry repair.
Run: python appearance/source/verify_exchange.py (numpy + lib3mf).
The SDK exposes float32 vertices: exact source XML is checked separately.
"""
from pathlib import Path
import collections,hashlib,json,subprocess,sys,tempfile,zipfile,xml.etree.ElementTree as ET
import numpy as np
import lib3mf

OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parent
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def xml(p):
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None and set(z.namelist())=={'[Content_Types].xml','_rels/.rels','3D/3dmodel.model'}
        return ET.fromstring(z.read('3D/3dmodel.model'))
def geometry(tree):
    result={}
    for o in tree.findall('m:resources/m:object',NS):
        mesh=o.find('m:mesh',NS)
        if mesh is None:continue
        vs=[dict(v.attrib) for v in mesh.findall('m:vertices/m:vertex',NS)]
        fs=[{k:t.get(k) for k in ['v1','v2','v3']} for t in mesh.findall('m:triangles/m:triangle',NS)]
        result[o.get('name')]=(vs,fs)
    return result
def meshes(model):
    it=model.GetMeshObjects();result={}
    while it.MoveNext():
        ob=it.GetCurrentMeshObject();result[ob.GetName()]=ob
    return result
def group(model):
    it=model.GetBaseMaterialGroups();assert it.Count()==1 and it.MoveNext();return it.GetCurrentBaseMaterialGroup()
def read(w,p):
    m=w.CreateModel();r=m.QueryReader('3mf');r.SetStrictModeActive(True);r.ReadFromFile(str(p));assert r.GetWarningCount()==0;return m

def main():
    source=ROOT/'multicolor/a1-four-tool-core.3mf';target=OUT/'a1-appearance-core.3mf'
    a,b=xml(source),xml(target);original,current=geometry(a),geometry(b);assert current==original
    assert b.get('unit')=='millimeter' and len(original)==8
    oldobjs=a.findall('m:resources/m:object',NS);newobjs=b.findall('m:resources/m:object',NS)
    assert len(oldobjs)==len(newobjs)==9
    for x,y in zip(oldobjs,newobjs):
        assert {k:v for k,v in x.attrib.items() if k not in ['pid','pindex']}=={k:v for k,v in y.attrib.items() if k not in ['pid','pindex']}
        xc,yc=x.find('m:components',NS),y.find('m:components',NS)
        if xc is not None:assert ET.tostring(xc)==ET.tostring(yc)
    assert ET.tostring(a.find('m:build',NS))==ET.tostring(b.find('m:build',NS))
    palette=json.loads((OUT/'palette.json').read_text());pal=palette['materials'];names=[m['id'] for m in pal]
    evidence=json.loads((ROOT/'multicolor/color-evidence.json').read_text())['fine_material_identities']
    assert [(p['id'],p['srgb']) for p in pal]==[(e['id'],'#'+''.join(f'{c:02X}' for c in e['candidate_rgb'])) for e in evidence]
    appearance=json.loads((OUT/'validation.json').read_text())
    assert {p['mesh']:p['material'] for p in appearance['parts']}==palette['mesh_materials']
    mats=b.findall('m:resources/m:basematerials/m:base',NS)
    assert [(m.get('name'),m.get('displaycolor')) for m in mats]==[(p['id'],p['srgb']+'FF') for p in pal]
    for o in newobjs:
        triangles=o.findall('m:mesh/m:triangles/m:triangle',NS)
        if not triangles:continue
        i=str(names.index(palette['mesh_materials'][o.get('name')]))
        assert o.get('pid')=='20' and o.get('pindex')==i
        assert all(t.get('pid')=='20' and t.get('p1')==t.get('p2')==t.get('p3')==i for t in triangles)
    wrapper=lib3mf.get_wrapper();base=read(wrapper,source);model=read(wrapper,target);g=group(model)
    assert [g.GetName(i) for i in g.GetAllPropertyIDs()]==names
    for i,p in zip(g.GetAllPropertyIDs(),pal):
        c=g.GetDisplayColor(i);assert [c.Red,c.Green,c.Blue,c.Alpha]==[int(p['srgb'][j:j+2],16) for j in [1,3,5]]+[255]
    imported,baseline=meshes(model),meshes(base);rows=[];points=[];facecounts=collections.Counter()
    for name,(vattrs,fattrs) in original.items():
        v=np.array([[float(v[k]) for k in ['x','y','z']] for v in vattrs]);f=np.array([[int(f[k]) for k in ['v1','v2','v3']] for f in fattrs]);points.append(v)
        ob=imported[name];old=baseline[name]
        actual=np.array([list(x.Coordinates) for x in ob.GetVertices()]);indices=np.array([list(t.Indices) for t in ob.GetTriangleIndices()]);assert np.array_equal(actual,v.astype('float32').astype('float64')) and np.array_equal(indices,f)
        assert np.array_equal(actual,[list(x.Coordinates) for x in old.GetVertices()]) and ob.IsValid() and ob.IsManifoldAndOriented()
        mid=palette['mesh_materials'][name]
        for t in ob.GetAllTriangleProperties():assert t.ResourceID==g.GetResourceID() and len(set(t.PropertyIDs))==1 and g.GetName(t.PropertyIDs[0])==mid
        facecounts[mid]+=len(f)
        def zero_count(coords):
            t=coords[f];return int(np.count_nonzero(np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)==0))
        rows.append({'mesh':name,'vertices':len(v),'triangles':len(f),'material':mid,'XML_coordinate_strings_and_triangle_indices_exact':True,'lib3mf_matches_source_float32_import':True,'lib3mf_valid_manifold_oriented':True,'SDK_float32_coordinate_max_difference_mm':float(np.max(np.abs(actual-v))),'exact_zero_area_triangles_source_double':zero_count(v),'exact_zero_area_triangles_SDK_float32':zero_count(actual)})
    assert len(facecounts)==7
    bit=model.GetBuildItems();assert bit.Count()==1 and bit.MoveNext();assembly=bit.GetCurrent().GetObjectResource();assert assembly.GetComponentCount()==8
    identity=np.array([[1,0,0],[0,1,0],[0,0,1],[0,0,0]])
    assert np.array_equal(np.array([list(v) for v in bit.GetCurrent().GetObjectTransform().Fields]),identity)
    for i,o in enumerate(newobjs[:8]):
        c=assembly.GetComponent(i);assert c.GetObjectResource().GetName()==o.get('name') and np.array_equal(np.array([list(v) for v in c.GetTransform().Fields]),identity)
    # Rebuild and edit a single material with the lossless XML-copy builder.
    with tempfile.TemporaryDirectory() as td:
        td=Path(td);rebuilt=td/'rebuilt.3mf';script=OUT/'source/build_exchange.py'
        subprocess.run([sys.executable,str(script),'--output',str(rebuilt)],check=True,capture_output=True);assert sha(rebuilt)==sha(target)
        edited=json.loads(json.dumps(palette));edited['materials'][3]['srgb']='#123456';ep=td/'palette.json';ep.write_text(json.dumps(edited));ef=td/'edited.3mf'
        subprocess.run([sys.executable,str(script),'--palette',str(ep),'--output',str(ef)],check=True,capture_output=True)
        assert geometry(xml(ef))==original
        em=read(wrapper,ef);eg=group(em)
        for i,p in zip(eg.GetAllPropertyIDs(),edited['materials']):
            c=eg.GetDisplayColor(i);assert [c.Red,c.Green,c.Blue]==[int(p['srgb'][j:j+2],16) for j in [1,3,5]]
        for name,ob in meshes(em).items():assert all(eg.GetName(t.PropertyIDs[0])==palette['mesh_materials'][name] for t in ob.GetAllTriangleProperties())
    pts=np.concatenate(points)
    report={'status':'Conditional GO for editable appearance exchange only','source':str(source.relative_to(ROOT)),'source_sha256':sha(source),'file':target.name,'sha256':sha(target),'bytes':target.stat().st_size,'unit':'millimeter','mesh_resources':8,'component_instances':8,'build_items':1,'display_material_count':7,'color_count_limit':None,'geometry_changed':False,'exact_source_XML_coordinates_triangle_indices_and_component_transforms':True,'deterministic_rebuild_SHA256_identical':True,'single_palette_edit_test_geometry_exact_other_colors_and_face_assignments_preserved':True,'lib3mf_version':list(wrapper.GetLibraryVersion()),'lib3mf_strict_import_warnings':0,'lib3mf_all_meshes_valid_manifold_oriented':True,'lib3mf_coordinate_representation':'float32; not exact original double precision. XML geometry comparison above is exact.','parts':rows,'material_triangle_counts':dict(facecounts),'bounds_mm':[pts.min(axis=0).tolist(),pts.max(axis=0).tolist()],'dimensions_mm':np.ptp(pts,axis=0).tolist(),'retained_quantization_limits':'Four PV/roof interface triangles collapse under float32, as documented in the unchanged editable QA. Source double-precision triangles and all eight meshes are retained. This seven-material file now gives PV and roof distinct display materials; no multi-tool interface or deposition validation is implied.','existing_interface_evidence':'../multicolor/qa/prusaslicer-editable-r2/independent-interface-probe.json','printer_profile_or_tool_mapping':None,'GUI_import_tested':False,'slicing_repeated':False,'physical_print_or_support_removal_tested':False,'support_off':'Existing NO-GO retained; floating bridge anchors and long bridging warning.','preview_images_rerendered':False,'reference_photo_pixels_embedded':False,'scope':'Appearance exchange only. Surface display colors do not guarantee printed color; eight semantic meshes are not eight bed-separated printable assembly pieces. Original four-tool PRINT remains a separate option.'}
    (OUT/'qa/exchange-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='parts'},ensure_ascii=False))
if __name__=='__main__':main()
