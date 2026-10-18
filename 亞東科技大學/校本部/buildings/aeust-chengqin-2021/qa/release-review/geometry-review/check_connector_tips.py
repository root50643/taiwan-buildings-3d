from pathlib import Path
import json,math,sys,os
from shapely.geometry import LineString,Point
from shapely.ops import polygonize_full,unary_union
import check_chengqin_independent as m

root=Path(__file__).parent
data,v,f,*_=m.read_binary_stl(Path(os.environ['CHENGQIN_PACKAGE']).resolve()/'models/v1/model.stl')

def section(z):
    segments=[]
    for face in f:
        t=[v[j] for j in face]; hits=[]
        for a,b in zip(t,t[1:]+t[:1]):
            if (a[2]<z<b[2]) or (b[2]<z<a[2]):
                u=(z-a[2])/(b[2]-a[2]);hits.append(tuple(round(a[k]+u*(b[k]-a[k]),8) for k in (0,1)))
        if len(hits)==2 and hits[0]!=hits[1]:segments.append(hits)
    polygons,cuts,dangles,invalid=polygonize_full(unary_union([LineString(s) for s in segments]))
    material=[]
    for p in polygons.geoms:
        x,y=p.representative_point().coords[0]; crossings=0
        for a,b in segments:
            if (a[1]>y)!=(b[1]>y):
                ix=a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1])
                if ix>x: crossings+=1
        if crossings%2:material.append(p)
    assert not any(len(g.geoms) for g in [cuts,dangles,invalid])
    return unary_union(material).simplify(1e-7,preserve_topology=True)

rows=[]
for z in (4.,7.,10.5,120.):
    geom=section(z); assert geom.geom_type=='Polygon'; coords=list(geom.exterior.coords)[:-1]
    core=geom.buffer(-.4,join_style=2)
    tips=[]
    for label,expected in [('A',(90.8,-31.4)),('B',(96.3,-22.6))]:
        i=min(range(len(coords)),key=lambda k:math.dist(coords[k],expected));p=coords[i];a=coords[i-1];c=coords[(i+1)%len(coords)]
        va=m.sub(a,p);vc=m.sub(c,p)
        angle=math.degrees(math.acos(max(-1,min(1,m.dot(va,vc)/(m.norm(va)*m.norm(vc))))))
        turn=m.orient2(a,p,c)
        if (turn>0)!=geom.exterior.is_ccw:angle=360-angle
        tips.append({'label':label,'nearest_actual_boundary_vertex_mm':p,'distance_from_declared_endpoint_mm':math.dist(p,expected),
          'interior_angle_deg':angle,'distance_to_0_8mm_core_mm':Point(p).distance(core),
          'adjacent_boundary_vertices_mm':[a,c]})
    rows.append({'z_mm':z,'material_components':1,'tips':tips})
result={'method':'Own STL slice polygons at representative full and recessed connector levels; only redundant collinear coordinates simplified by 1e-7 mm for corner-angle readability, not used in STL QA. No candidate source generator/QA geometry is imported.',
 'stl_sha256':'4e73e7094c83de47c19bcc6121fee575c1360b285d597773d983a873f46b7f5a',
 'rows':rows,
 'interpretation':'The explicit Yuanzhi cut has attached convex corners; B is acute. They have mathematically tapered local tips and may be rounded or omitted locally by nozzle paths. These are ends of a broad filled connector, not detached thin walls, unsupported appendages or a second STL component. Every independently sampled material component has a surviving single 0.8 mm eroded core. This does not prove a global positive pointwise minimum thickness, especially at corner tips.',
 'requires_slicer_review':'Inspect the cut-end tips and connector-to-main joining corner, shallow horizontal relief and tall-body adhesion/stability at target nozzle/layer size; no G-code or actual print was tested.'}
(root/'connector-tip-review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,indent=2))
