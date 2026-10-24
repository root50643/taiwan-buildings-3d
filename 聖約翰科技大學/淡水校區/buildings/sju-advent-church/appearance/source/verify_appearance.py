"""Independent STL topology, finite assignments and genuine 3MF material readback.
Requires Python 3 + lib3mf 2.5. No repair, remesh or tolerance-based replacement.
"""
from pathlib import Path
import json,math,collections,hashlib,zipfile,xml.etree.ElementTree as ET
import lib3mf
from geometry_io import read_original,triangle_coordinate_sha,area
OUT=Path(__file__).resolve().parents[1]

def check():
    v,f=read_original(OUT.parent/'model.stl');ann=json.loads((OUT/'face-materials.json').read_text());man=json.loads((OUT/'material-manifest.json').read_text())
    assert len(f)==3972 and len(v)==1980
    edges=collections.defaultdict(list);adj=[set() for _ in v];links=[[] for _ in v];volume=0
    assert len({tuple(sorted(face)) for face in f})==len(f)
    for fi,(a,b,c) in enumerate(f):
        assert len({a,b,c})==3 and area([v[a],v[b],v[c]])>0
        for x,y in [(a,b),(b,c),(c,a)]:edges[tuple(sorted((x,y)))].append((x,y));adj[x].add(y);adj[y].add(x)
        links[a].append((b,c));links[b].append((c,a));links[c].append((a,b))
        p,q,r=v[a],v[b],v[c];volume+=(p[0]*(q[1]*r[2]-q[2]*r[1])+p[1]*(q[2]*r[0]-q[0]*r[2])+p[2]*(q[0]*r[1]-q[1]*r[0]))/6
    assert all(len(es)==2 and es[0]==es[1][::-1] for es in edges.values())
    def connected(graph):
        seen=set();stack=[next(iter(graph))]
        while stack:
            x=stack.pop()
            if x in seen:continue
            seen.add(x);stack.extend(graph[x]-seen)
        return len(seen)==len(graph)
    assert connected(dict(enumerate(adj))) and volume>0
    for link in links:
        graph=collections.defaultdict(set)
        for a,b in link:graph[a].add(b);graph[b].add(a)
        assert all(len(n)==2 for n in graph.values()) and connected(graph)
    assert len(ann['material_indices'])==len(f)==len(ann['region_by_face'])
    assert ann['triangle_coordinate_sha256']==triangle_coordinate_sha(v,f)
    counts=collections.Counter(ann['material_indices']);matids=[m['id'] for m in man['materials']]
    covered=[]
    for key,region in man['regions'].items():
        assert len(region['face_ids'])==region['face_count']
        if region['material'] not in ['unknown_neutral','base_neutral']:assert region['sources']
        for i in region['face_ids']:
            assert ann['region_by_face'][i]==key
            assert matids[ann['material_indices'][i]]==region['material']
        covered.extend(region['face_ids'])
    assert sorted(covered)==list(range(len(f)))
    for m in man['materials']:assert m['face_count']==counts[m['index']]
    for key in ['cross_unresolved','crown_top_unseen','rear_door_unregistered','undersides_unseen']:
        assert all(ann['material_indices'][i]==0 for i in man['regions'][key]['face_ids'])
    archive=zipfile.ZipFile(OUT/'sju-advent-church-materials.3mf');assert archive.testzip() is None
    assert sorted(archive.namelist())==['3D/3dmodel.model','[Content_Types].xml','_rels/.rels']
    root=ET.fromstring(archive.read('3D/3dmodel.model'));ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    assert root.get('unit')=='millimeter'
    objects=root.findall('./m:resources/m:object',ns);assert len(objects)==1
    xv=[tuple(float(e.get(k)) for k in ['x','y','z']) for e in root.findall('.//m:vertex',ns)]
    xt=root.findall('.//m:triangle',ns);xf=[[int(e.get(k)) for k in ['v1','v2','v3']] for e in xt]
    assert xv==v and xf==f
    bases=root.findall('./m:resources/m:basematerials',ns);assert len(bases)==1
    bm=bases[0];assert [b.get('name') for b in bm]==matids
    assert [b.get('displaycolor') for b in bm]==[m['hex']+'FF' for m in man['materials']]
    for i,t in enumerate(xt):
        assert t.get('pid',objects[0].get('pid'))==bm.get('id')
        actual=[int(t.get(k,t.get('p1',objects[0].get('pindex')))) for k in ['p1','p2','p3']]
        assert actual==[ann['material_indices'][i]]*3
    assert len(root.findall('./m:build/m:item',ns))==1
    w=lib3mf.get_wrapper();model=w.CreateModel();reader=model.QueryReader('3mf');reader.SetStrictModeActive(True);reader.ReadFromFile(str(OUT/'sju-advent-church-materials.3mf'))
    assert reader.GetWarningCount()==0
    it=model.GetMeshObjects();assert it.MoveNext();mesh=it.GetCurrentMeshObject();assert not it.MoveNext()
    lv=[tuple(x.Coordinates) for x in mesh.GetVertices()];lf=[list(x.Indices) for x in mesh.GetTriangleIndices()]
    assert lv==v and lf==f and mesh.IsManifoldAndOriented()
    # Reader may renumber resource/property IDs; compare semantic material names.
    for i in range(len(f)):
        props=mesh.GetTriangleProperties(i);group=model.GetBaseMaterialGroupByID(props.ResourceID)
        assert [group.GetName(pid) for pid in props.PropertyIDs]==[matids[ann['material_indices'][i]]]*3
    report={'pass':True,'original_stl_sha256':ann['source_stl_sha256'],'triangle_coordinate_sha256':triangle_coordinate_sha(v,f),'triangles':len(f),'exact_deduplicated_vertices':len(v),'edges':len(edges),'single_connected_component':True,'each_edge_two_oppositely_oriented_faces':True,'vertex_links_single_cycle':True,'duplicate_faces':0,'degenerate_faces':0,'volume_mm3':volume,'euler_characteristic':len(v)-len(edges)+len(f),'bounds_mm':[[min(p[k] for p in v) for k in range(3)],[max(p[k] for p in v) for k in range(3)]],'unknown_faces_including_base':man['unknown_faces'],'source_backed_faces':man['known_color_faces'],'all_materials_referenced':all(counts[i]>0 for i in range(len(matids))),'all_regions_complete_nonoverlapping':True,'cross_crown_top_undersides_rear_door_unknown':True,'three_mf':{'real_core_base_materials':len(bm),'all_triangles_have_uniform_three_corner_material':True,'exact_xml_coordinates_and_indices':True,'lib3mf_strict_read_warnings':reader.GetWarningCount(),'lib3mf_version':list(w.GetLibraryVersion()),'exact_lib3mf_readback_geometry':True,'semantic_material_names_exact':True,'textures':0},'limits':['No real print or slicer toolpath performed.','No new global minimum wall or support claim.','Original geometric/FFF limitations and 52 high-loss layers / 436 high-loss cross-layer polygon samples remain unchanged.','Appearance QA does not replace original full geometry QA; byte-identical geometry is the transfer evidence.']}
    (OUT/'appearance-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':check()
