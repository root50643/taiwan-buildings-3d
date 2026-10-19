"""Independent XML/NumPy + installed lib3mf importer checks; no slicing or mesh repair.
Run: python appearance/source/verify_exchange.py (numpy, lib3mf already available).
"""
from pathlib import Path
import collections,hashlib,json,struct,tempfile,zipfile,xml.etree.ElementTree as ET
import numpy as np
import lib3mf

OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parent
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def raw_stl(path):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0];assert len(data)==84+50*n
    record=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')])
    return np.frombuffer(data,dtype=record,count=n,offset=84)['vertices'].copy().astype(np.float64)
def meshes(model):
    it=model.GetMeshObjects();result={}
    while it.MoveNext():
        ob=it.GetCurrentMeshObject();result[ob.GetName()]=ob
    return result
def palette_group(model):
    it=model.GetBaseMaterialGroups();assert it.Count()==1;assert it.MoveNext();return it.GetCurrentBaseMaterialGroup()
def lib_geometry(ob):
    v=np.array([list(x.Coordinates) for x in ob.GetVertices()],dtype=np.float64)
    f=np.array([list(x.Indices) for x in ob.GetTriangleIndices()],dtype=int)
    return v,f
def main():
    assembly=json.loads((ROOT/'assembly.json').read_text());pal=json.loads((OUT/'palette.json').read_text())['materials']
    prototypes={Path(p['stl']).stem:p for p in assembly['parts']};references={n:raw_stl(ROOT/p['stl']) for n,p in prototypes.items()}
    expected_names=[p['id'] for p in pal];wrapper=lib3mf.get_wrapper();records=[];all_counts=collections.Counter();master=None
    for path in [OUT/'npu-appearance-ASSEMBLED.3mf',*sorted((OUT/'parts').glob('*.3mf'))]:
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            assert set(z.namelist())=={'[Content_Types].xml','_rels/.rels','3D/3dmodel.model'}
            tree=ET.fromstring(z.read('3D/3dmodel.model'))
        assert tree.get('unit')=='millimeter'
        mats=tree.findall('m:resources/m:basematerials/m:base',NS)
        assert [(x.get('name'),x.get('displaycolor')) for x in mats]==[(x['id'],x['srgb']+'FF') for x in pal]
        xmlobjects={int(o.get('id')):o for o in tree.findall('m:resources/m:object',NS)}
        surface_checks={}
        for ob in xmlobjects.values():
            mesh=ob.find('m:mesh',NS)
            if mesh is None:continue
            name=ob.get('name');p=prototypes[name]
            verts=np.array([[float(v.get(k)) for k in ['x','y','z']] for v in mesh.findall('m:vertices/m:vertex',NS)])
            triangles=mesh.findall('m:triangles/m:triangle',NS);faces=np.array([[int(t.get(k)) for k in ['v1','v2','v3']] for t in triangles])
            assert np.array_equal(verts[faces],references[name]),name
            indices=np.array([int(t.get('p1')) for t in triangles]);assert all(t.get('pid')=='20' and t.get('p1')==t.get('p2')==t.get('p3') for t in triangles)
            T=np.array(p['assembly_transform']);centers=references[name].mean(axis=1)@T[:3,:3].T+T[:3,3]
            expected=np.zeros(len(triangles),dtype=int)
            for reg in assembly['color_regions']:
                if reg['part']!=p['id']:continue
                a,b=np.asarray(reg['bounds_mm']);mask=np.all((centers>=a-1e-4)&(centers<=b+1e-4),axis=1)
                index=2 if 'stair tower glazed' in reg['reason'] else {'slate':1,'ochre':3,'terracotta':4}[reg['color']]
                expected[mask]=index
            assert np.array_equal(indices,expected),name
            counts=collections.Counter(expected_names[i] for i in indices);surface_checks[name]={'triangles':len(triangles),'source_STL_triangles_exact':True,'source_SHA256':hashlib.sha256((ROOT/p['stl']).read_bytes()).hexdigest(),'independent_selector_match':True,'material_faces':dict(counts)}
            if path.name=='npu-appearance-ASSEMBLED.3mf':all_counts.update(counts)
        model=wrapper.CreateModel();reader=model.QueryReader('3mf');reader.SetStrictModeActive(True);reader.ReadFromFile(str(path));assert reader.GetWarningCount()==0
        group=palette_group(model);ids=group.GetAllPropertyIDs();assert [group.GetName(i) for i in ids]==expected_names
        for i,p in zip(ids,pal):
            c=group.GetDisplayColor(i);assert [c.Red,c.Green,c.Blue,c.Alpha]==[int(p['srgb'][k:k+2],16) for k in [1,3,5]]+[255]
        imported=meshes(model);assert set(imported)==set(surface_checks)
        for name,ob in imported.items():
            assert ob.IsValid() and ob.IsManifoldAndOriented(),name
            verts,faces=lib_geometry(ob);assert np.array_equal(verts[faces],references[name]),name
            counts=collections.Counter()
            for t in ob.GetAllTriangleProperties():
                assert t.ResourceID==group.GetResourceID() and len(set(t.PropertyIDs))==1
                counts[group.GetName(t.PropertyIDs[0])]+=1
            assert dict(counts)==surface_checks[name]['material_faces']
        rec={'file':str(path.relative_to(OUT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'XML_CRC_and_resource_checks':True,'lib3mf_strict_warnings':0,'all_meshes_valid_manifold_oriented':True,'exact_source_vertex_triangle_roundtrip':True,'per_face_material_names_and_sRGB_preserved':True,'parts':surface_checks}
        if path.name=='npu-appearance-ASSEMBLED.3mf':
            cs=xmlobjects[100].findall('m:components/m:component',NS);assert len(cs)==10
            for c,p in zip(cs,assembly['parts']):
                assert xmlobjects[int(c.get('objectid'))].get('name')==Path(p['stl']).stem
                assert np.array_equal(np.array([float(x) for x in c.get('transform').split()]).reshape(4,3).T,np.asarray(p['assembly_transform'])[:3,:])
            bit=model.GetBuildItems();assert bit.Count()==1 and bit.MoveNext();component=bit.GetCurrent().GetObjectResource();assert component.GetComponentCount()==10
            errors=[];points=[]
            for j,p in enumerate(assembly['parts']):
                c=component.GetComponent(j);T=np.array([list(row) for row in c.GetTransform().Fields]);original=np.asarray(p['assembly_transform']);name=c.GetObjectResource().GetName();vertices,faces=lib_geometry(imported[name])
                points.append(vertices@original[:3,:3].T+original[:3,3]);errors.append(float(np.max(np.abs(vertices@T[:3,:]+T[3,:]-(vertices@original[:3,:3].T+original[:3,3])))))
            assert max(errors)<1e-5
            points=np.concatenate(points);rec.update(physical_instances=10,assembly_XML_transforms_exact=True,lib3mf_float32_transform_max_mm=max(errors),bounds_mm=[points.min(axis=0).tolist(),points.max(axis=0).tolist()],dimensions_mm=np.ptp(points,axis=0).tolist())
            master=model
        else:
            assert model.GetBuildItems().Count()==1
            verts,_=lib_geometry(next(iter(imported.values())));assert np.array_equal(verts.min(axis=0),[0,0,0])
            rec['original_native_part_orientation_minXYZ_zero']=True
        records.append(rec)
    assert len(records)==9 and all(all_counts[x]>0 for x in expected_names)
    # Exercise actual SDK material editing and serialization in a temporary, unpublished file.
    g=palette_group(master);ids=g.GetAllPropertyIDs();changed=ids[2];c=lib3mf.Color();c.Red=12;c.Green=34;c.Blue=56;c.Alpha=255;g.SetDisplayColor(changed,c)
    quantization={}
    with tempfile.TemporaryDirectory() as tmp:
        f=Path(tmp)/'editable-roundtrip.3mf';writer=master.QueryWriter('3mf');precision=writer.GetDecimalPrecision();writer.WriteToFile(str(f));check=wrapper.CreateModel();r=check.QueryReader('3mf');r.SetStrictModeActive(True);r.ReadFromFile(str(f));assert r.GetWarningCount()==0
        g2=palette_group(check);newids=g2.GetAllPropertyIDs()
        for k,pid in enumerate(newids):
            color=g2.GetDisplayColor(pid);actual=[color.Red,color.Green,color.Blue,color.Alpha]
            assert actual==([12,34,56,255] if k==2 else [int(pal[k]['srgb'][i:i+2],16) for i in [1,3,5]]+[255])
        for name,ob in meshes(check).items():
            v,f=lib_geometry(ob);assert v[f].shape==references[name].shape
            quantization[name]=float(np.max(np.abs(v[f]-references[name])));assert quantization[name]<1e-5
            assert collections.Counter(g2.GetName(t.PropertyIDs[0]) for t in ob.GetAllTriangleProperties())==records[0]['parts'][name]['material_faces']
    report={'lib3mf_version':list(wrapper.GetLibraryVersion()),'files_verified':records,'five_materials_all_used':dict(all_counts),'SDK_single_material_edit_roundtrip_preserves_other_palette_and_face_assignments':True,'SDK_roundtrip_default_decimal_precision':precision,'SDK_edited_roundtrip_coordinate_quantization_mm':quantization,'SDK_edited_roundtrip_geometry_byte_exact':False,'SDK_edited_test_file_distributed':False,'recommended_edit':'Change palette.json and rerun the standard-library builder to re-use original STL values; do not assume third-party reserialization is byte-exact.','source_STL_and_assembly_unchanged':True,'GUI_import_tested':False,'closed_color_volumes_created':False,'printer_tool_mapping_validated':False,'slicing_repeated':False,'physical_print_or_fit_verified':False,'scope':'Appearance exchange and exact-mesh packaging only; unchanged prior geometric and slicing limitations remain.'}
    (OUT/'qa/exchange-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='files_verified'},ensure_ascii=False))
if __name__=='__main__':main()
