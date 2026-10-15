"""Fresh NYCU Graduate Dormitory 3 bounded exterior model, never old-byte recovery.
Read parameters.json. Metre-space derived footprint / estimated interior edges are
explicitly distinguished there. No hidden 3F bridge or southern facade is invented.
"""
from pathlib import Path
import argparse, json, hashlib
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, OpType
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
R=Path(__file__).resolve().parent

def union(parts):
    return Manifold.batch_boolean(parts, OpType.Add)
def box(x0,x1,y0,y1,z0,z1):
    assert x1>x0 and y1>y0 and z1>z0
    return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def prism(coords,z0,z1):
    p=orient(Polygon(coords),sign=1.0)
    assert p.is_valid and p.area>0 and z1>z0
    return CrossSection([list(p.exterior.coords)[:-1]]).extrude(z1-z0).translate((0,0,z0))
def facade_box(a,b,t0,t1,d0,d1,z0,z1):
    a=np.array(a,dtype=float);u=np.array(b,dtype=float)-a;u/=np.linalg.norm(u)
    n=np.array([-u[1],u[0]])
    return prism([a+u*t0+n*d0,a+u*t1+n*d0,a+u*t1+n*d1,a+u*t0+n*d1],z0,z1)
def decorate(body,f,P):
    a,b=f['a'],f['b'];L=float(np.linalg.norm(np.array(b)-a));q=P['facade_parameters_m'];cuts=[];add=[]
    portals=f.get('portals',[])
    for t0,t1,z0,z1 in portals:
        assert 1.0<t0<t1<L-1.0
        cuts.append(facade_box(a,b,t0,t1,-3.0,0.3,z0,z1))
    for t in np.arange(q['end_margin'],L-q['end_margin']-q['window_width']+1e-6,f['bay_pitch_m']):
        for row in f['rows']:
            z0=(row+1)*q['floor_pitch']+q['window_bottom_margin'];z1=(row+2)*q['floor_pitch']-q['window_top_margin']
            roof=P['north_low_terminal_roof_m'] if f['mass']=='lower' else P['main_roof_m']
            z1=min(z1,roof-q['window_top_margin'])
            if f['mass']=='lower':z0=max(z0,max(x['height'] for x in P['terminal_pilotis'])+q['window_top_margin'])
            if f['mass']=='upper':z0=max(z0,P['north_upper_terminal_bottom_m']+q['window_top_margin'])
            assert z1-z0>=0.8
            if any(t<pt1+0.7 and t+q['window_width']>pt0-0.7 and z0<pz1+0.7 and z1>pz0-0.7 for pt0,pt1,pz0,pz1 in portals):continue
            cuts.append(facade_box(a,b,t,t+q['window_width'],-q['recess_depth'],0.3,z0,z1))
            # Substantial, fully backed louver box. Individual fine slats are omitted.
            add.append(facade_box(a,b,t+0.2,t+0.2+q['screen_width'],-q['recess_depth']-0.25,q['screen_projection'],z0,min(z0+q['screen_height'],z1)))
    if cuts:body=body-union(cuts)
    return union([body]+add)
def make_model(P):
    h=P['main_roof_m']
    masses={'north':prism(P['north_polygon_m'],0,h),'south':prism(P['south_polygon_m'],0,h),
            'lower':prism(P['north_low_terminal_polygon_m'],0,P['north_low_terminal_roof_m']),
            'upper':prism(P['north_upper_terminal_polygon_m'],P['north_upper_terminal_bottom_m'],h)}
    for f in P['facades']:masses[f['mass']]=decorate(masses[f['mass']],f,P)
    # The documented terminal pilotis is a backed exterior recess, not the hidden 3F connection.
    pilotis_columns=[]
    for f in P.get('terminal_pilotis',[]):
        a,b=np.array(f['a'],float),np.array(f['b'],float);u=b-a;L=np.linalg.norm(u);u/=L;n=np.array([-u[1],u[0]])
        masses['lower']-=facade_box(a,b,f.get('end_margin_start',f['end_margin']),L-f.get('end_margin_end',f['end_margin']),-f['depth'],0.3,0,f['height'])
        for t in f['column_t']:
            x,y=a+u*t+n*f['column_depth']
            pilotis_columns.append(Manifold.cylinder(f['height']+0.15,f['column_radius'],f['column_radius'],32).translate((x,y,0)))
    # Source-visible west-sector ends have sparse vertical glazing rather than mirrored bays.
    for key,a,b in [('north',[-36.5,12.0],[-37.7788516,25.893032]),('south',[-45.42962495,-29.733572],[-58.44705697,-12.478972])]:
        L=np.linalg.norm(np.array(b)-a);cuts=[]
        for row in range(9):
            z0=3.59*(row+1)+0.7;z1=3.59*(row+2)-0.8
            cuts.append(facade_box(a,b,L*.36,L*.64,-0.6,0.25,z0,z1))
        masses[key]-=union(cuts)
    parts=list(masses.values())+pilotis_columns
    for x0,x1,y0,y1,top in P['roof_cores_m']:parts.append(box(x0,x1,y0,y1,h-0.3,top))
    e=P['entrance_m'];lobby=box(*e['lobby_box'])
    # Entrance glazing has a solid back, and broad uninterrupted frame members.
    for x0,x1 in [(10.8,13.1),(14.0,16.2),(17.1,19.2)]:
        for z0,z1 in [(3.7,5.8)]:lobby-=box(x0,x1,20.9,21.8,z0,z1)
    # Lower center is occupied by the stair; do not seal glazing pockets behind it.
    for x0,x1 in [(10.8,11.8),(18.2,19.2)]:lobby-=box(x0,x1,20.9,21.8,0.8,2.8)
    parts+=[lobby,box(*e['canopy_box'])]
    for x,y in e['column_xy']:parts.append(Manifold.cylinder(7.0,e['column_radius'],e['column_radius'],32).translate((x,y,0)))
    x0,x1=e['stair_x'];ya,yb=e['stair_y'];N=e['stair_steps']
    for i in range(N):
        # The high end is at the lobby; each solid tread is rooted all the way down.
        parts.append(box(x0,x1,ya+(yb-ya)*i/N,ya+(yb-ya)*(i+1)/N,0,e['stair_rise']*(N-i)/N))
    body=union(parts)
    S=P['scale_mm_per_m'];ox,oy=P['xy_origin_m'];base=P['base_mm']
    body=body.translate((-ox,-oy,0)).scale((S,S,S)).translate((0,0,base[2]-0.05))
    final=union([body,box(-base[0]/2,base[0]/2,-base[1]/2,base[1]/2,0,base[2])])
    assert final.status().name=='NoError',str(final.status())
    M=final.to_mesh();t=trimesh.Trimesh(np.asarray(M.vert_properties)[:,:3],np.asarray(M.tri_verts),process=False)
    return t

def main():
    a=argparse.ArgumentParser();a.add_argument('--output',type=Path,default=R/'model.stl');a.add_argument('--parameters',type=Path,default=R/'parameters.json');q=a.parse_args()
    P=json.loads(q.parameters.read_text());t=make_model(P);t.export(q.output)
    print(json.dumps({'triangles':len(t.faces),'bounds_mm':t.bounds.tolist(),'extents_mm':t.extents.tolist(),'sha256':hashlib.sha256(q.output.read_bytes()).hexdigest(),'construction_watertight_hint':bool(t.is_watertight),'fresh_replacement':True}))
if __name__=='__main__':main()
