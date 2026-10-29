import pathlib,json,numpy as np,zipfile,xml.etree.ElementTree as ET,hashlib,struct,sys
import trimesh,manifold3d as mf

root=pathlib.Path(sys.argv[1]); target=pathlib.Path(sys.argv[2])
d=np.load(root/'mesh-data.npz'); v=d['vertices']; f=d['faces']; mi=d['materials']
checks={}; details={}
def component_count(mesh):
    parent=list(range(len(mesh.vertices)))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]];x=parent[x]
        return x
    for a,b in mesh.edges:
        a=find(int(a));b=find(int(b))
        if a!=b:parent[a]=b
    return len({find(i) for i in range(len(parent))})
checks['finite_vertices']=bool(np.isfinite(v).all())
checks['valid_triangle_indices']=bool(f.ndim==2 and f.shape[1]==3 and f.min()>=0 and f.max()<len(v))
t=trimesh.Trimesh(v,f,process=False)
checks['watertight_original']=bool(t.is_watertight)
checks['consistent_winding']=bool(t.is_winding_consistent)
checks['positive_volume']=bool(t.volume>0)
checks['no_degenerate_faces']=bool((t.area_faces>1e-8).all())
checks['one_component']=component_count(t)==1
e=np.sort(t.edges,axis=1);_,counts=np.unique(e,axis=0,return_counts=True)
checks['all_undirected_edges_have_two_incident_faces']=bool((counts==2).all())
b=(root/'model.stl').read_bytes(); n=struct.unpack('<I',b[80:84])[0]
st=np.frombuffer(b,dtype=np.dtype([('normals','<f4',(3,)),('vertices','<f4',(3,3)),('attributes','<u2')]),offset=84,count=n)
checks['binary_stl_length_exact']=len(b)==84+50*n
checks['stl_triangle_vertices_float32_exact']=np.array_equal(st['vertices'],v[f].astype('<f4'))
stl=trimesh.load(root/'model.stl',force='mesh')
checks['reopened_stl_watertight']=bool(stl.is_watertight)
checks['reopened_stl_one_component']=component_count(stl)==1
checks['reopened_stl_winding_consistent']=bool(stl.is_winding_consistent)
checks['reopened_stl_no_zero_area']=bool((stl.area_faces>1e-8).all())
pal=json.loads((root/'editable-parts.json').read_text())['palette']
with zipfile.ZipFile(root/'model.3mf') as z:
    checks['3mf_contains_only_package_xml']=set(z.namelist())=={'[Content_Types].xml','_rels/.rels','3D/3dmodel.model'}
    tree=ET.fromstring(z.read('3D/3dmodel.model'));ns={'m':tree.tag.split('}')[0][1:]}
    vv=np.asarray([[float(x.attrib[a]) for a in 'xyz'] for x in tree.findall('.//m:vertex',ns)])
    triangles=tree.findall('.//m:triangle',ns)
    ff=np.asarray([[int(x.attrib[a]) for a in ('v1','v2','v3')] for x in triangles])
    mids=np.asarray([[int(x.attrib[a]) for a in ('p1','p2','p3')] for x in triangles])
    checks['3mf_vertices_match_8dp']=bool(np.allclose(vv,v,rtol=0,atol=5.1e-9))
    checks['3mf_faces_exact']=np.array_equal(ff,f)
    checks['3mf_all_three_corner_material_indices_exact']=np.array_equal(mids,np.repeat(mi[:,None],3,axis=1))
    checks['3mf_all_material_resource_refs_valid']=all(x.attrib.get('pid')=='1' for x in triangles)
    checks['3mf_palette_exact']=[(x.attrib['name'],x.attrib['displaycolor']) for x in tree.findall('.//m:base',ns)]==[(x['name'],x['hex']+'FF') for x in pal]
    checks['3mf_mm_units']=tree.attrib.get('unit')=='millimeter'
parts=json.loads((root/'construction-parts.json').read_text())
checks['all_part_source_evidence_present']=all(isinstance(p.get('evidence'),str) and p['evidence'].strip() for p in parts)
checks['part_material_indices_valid']=all(0<=p['material']<len(pal) for p in parts)
checks['no_source_images_or_pdfs_in_package']=not any(p.suffix.lower() in ('.pdf','.jpg','.jpeg','.tiff','.tif','.webp') for p in root.rglob('*'))
details.update({'vertices':len(v),'triangles':len(f),'component_count':component_count(t),'dimensions_mm':t.extents.tolist(),'volume_mm3':float(t.volume),'minimum_face_area_mm2':float(t.area_faces.min()),'editable_parts':len(parts),'file_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'model.stl',root/'model.3mf',root/'mesh-data.npz',root/'construction-parts.json',root/'build_model.py',root/'render_model.py']}})
report={'checks':checks,'details':details,'passed':all(checks.values()),'scope':'Independently recomputed format/geometry checks, not a source-accuracy or trial-print certification.'}
target.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps(report,indent=2,ensure_ascii=False));assert report['passed']
