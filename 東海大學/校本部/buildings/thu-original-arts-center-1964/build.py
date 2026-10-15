#!/usr/bin/env python3
"""Independently authored historical exterior study. All output coordinates are mm.
Run with pinned requirements.txt. No source photographs are embedded in outputs.
"""
from pathlib import Path
import argparse, json, struct, hashlib, importlib.metadata
import numpy as np
import manifold3d as md
import trimesh

HERE=Path(__file__).resolve().parent
P=json.loads((HERE/'parameters.json').read_text())
S=P['source_era']; F=P['fabrication']; K=F['mm_per_plan_pixel']
M=K*S['nominal_pixels_per_metre']; B=F['base_thickness_mm']
DATUM=B+S['courtyard_depth_m']*M
PARTS=[]; RECORD=[]
def xp(x): return (x-S['base_bounds_px'][0])*K
def yp(y): return (S['base_bounds_px'][3]-y)*K
def zm(m): return DATUM+m*M
def cubemm(x0,x1,y0,y1,z0,z1):
    return md.Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0])
def box(x0,x1,y0,y1,z0,z1): return cubemm(xp(x0),xp(x1),yp(y1),yp(y0),z0,z1)
def rounded_box(x0,x1,y0,y1,z0,z1,radius):
    xa,xb,ya,yb=xp(x0),xp(x1),yp(y1),yp(y0)
    r=min(radius,(xb-xa)/2-.001,(yb-ya)/2-.001)
    cs=md.CrossSection.square([xb-xa-2*r,yb-ya-2*r],center=True).offset(r,md.JoinType.Round,circular_segments=32)
    return cs.extrude(z1-z0).translate([(xa+xb)/2,(ya+yb)/2,z0])
def add(name,solid,kind):
    if solid.status()!=md.Error.NoError or solid.is_empty(): raise RuntimeError((name,solid.status()))
    PARTS.append(solid); RECORD.append({'name':name,'kind':kind,'volume_mm3':solid.volume()})
def union(parts): return md.Manifold.batch_boolean(parts,md.OpType.Add)
def wallx(name,x,y0,y1,top,bottom=DATUM,width=None):
    half=(width or F['wall_thickness_mm'])/(2*K); add(name,box(x-half,x+half,y0,y1,bottom-.08,top),'wall')
def wally(name,y,x0,x1,top,bottom=DATUM,width=None):
    half=(width or F['wall_thickness_mm'])/(2*K); add(name,box(x0,x1,y-half,y+half,bottom-.08,top),'wall')
def column(name,x,y,top,bottom=DATUM):
    a=F['column_side_mm'];r=F['column_corner_radius_mm'];cs=md.CrossSection.square([a-2*r,a-2*r],center=True).offset(r,md.JoinType.Round,circular_segments=32);q=cs.extrude(top-bottom+.1).translate([0,0,bottom-.05]).rotate([0,0,45]).translate([xp(x),yp(y),0]); add(name,q,'column')
def glazed_x(name,x,y0,y1,top,posts=4):
    wallx(name+' sill',x,y0,y1,DATUM+1.1)
    wallx(name+' lintel',x,y0,y1,top,top-1.2)
    for j,y in enumerate(np.linspace(y0,y1,posts)):
        half=F['wall_thickness_mm']/(2*K);add(name+f' mullion {j}',rounded_box(x-half,x+half,float(y)-half,float(y)+half,DATUM-.08,top,.42),'window_mullion')
def glazed_y(name,y,x0,x1,top,posts=4):
    wally(name+' sill',y,x0,x1,DATUM+1.1)
    wally(name+' lintel',y,x0,x1,top,top-1.2)
    for j,x in enumerate(np.linspace(x0,x1,posts)):
        half=F['wall_thickness_mm']/(2*K);add(name+f' mullion {j}',rounded_box(float(x)-half,float(x)+half,y-half,y+half,DATUM-.08,top,.42),'window_mullion')

def umbrella(name,bounds,cx,cy,valley,rim):
    """A closed thickness solid, with independently unequal quadrant spans.
    1.1 mm flattened high rim is a recorded print adaptation, not source geometry.
    """
    x0,x1,y0,y1=bounds; n=F['roof_subdivisions_per_quadrant']; r=F['roof_flat_rim_width_mm']
    # Exact head and rim-band transitions are in the mesh grid.
    xs=np.unique(np.r_[np.linspace(xp(x0),xp(cx),n+1),np.linspace(xp(cx),xp(x1),n+1),xp(x0)+r,xp(x1)-r])
    ys=np.unique(np.r_[np.linspace(yp(y1),yp(cy),n+1),np.linspace(yp(cy),yp(y0),n+1),yp(y1)+r,yp(y0)-r])
    X,Y=np.meshgrid(xs,ys)
    U=np.where(X<=xp(cx),(xp(cx)-X)/(xp(cx)-xp(x0)-r),(X-xp(cx))/(xp(x1)-r-xp(cx)))
    V=np.where(Y<=yp(cy),(yp(cy)-Y)/(yp(cy)-yp(y1)-r),(Y-yp(cy))/(yp(y0)-r-yp(cy)))
    U=np.clip(U,0,1); V=np.clip(V,0,1)
    Z=valley+(rim-valley)*(U+V-U*V)
    top=np.column_stack([X.ravel(),Y.ravel(),Z.ravel()]); verts=np.vstack([top,top-[0,0,F['roof_vertical_thickness_mm']]])
    ny,nx=X.shape; N=nx*ny; faces=[]
    for j in range(ny-1):
        for i in range(nx-1):
            a=j*nx+i; b=a+1; c=a+nx; d=c+1
            faces.extend([(a,b,d),(a,d,c),(a+N,d+N,b+N),(a+N,c+N,d+N)])
    boundary=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range((ny-1)*nx+nx-2,(ny-1)*nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]): faces.extend([(a,b+N,b),(a,a+N,b+N)])
    mesh=md.Mesh64(np.asarray(verts,dtype=np.float64),np.asarray(faces,dtype=np.uint64))
    roof=md.Manifold(mesh)
    add(name,roof,'curved_roof')
    column(name+' diamond support',cx,cy,valley+.15)
    return {'name':name,'bounds_px':bounds,'head_px':[cx,cy],'valley_mm':valley,'rim_mm':rim}

def deterministic_stl(t,path):
    # Sort cyclically canonicalized oriented float32 triangles; do not heal or reverse normals.
    tri=np.asarray(t.triangles,dtype='<f4')
    for i,v in enumerate(tri):
        a=min(range(3),key=lambda j: tuple(v[j])); tri[i]=np.roll(v,-a,axis=0)
    order=np.lexsort(tuple(tri.reshape(-1,9)[:,i] for i in range(8,-1,-1))); tri=tri[order]
    dt=tri.astype(np.float64)
    norms=np.cross(dt[:,1]-dt[:,0],dt[:,2]-dt[:,0]); lens=np.linalg.norm(norms,axis=1)
    if np.any(lens==0): raise ValueError(f'Float32 STL serialization would create {np.sum(lens==0)} zero-area faces')
    norms/=lens[:,None]
    data=np.zeros(len(tri),dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]);data['n']=norms;data['v']=tri
    path.write_bytes(b'THU historical arts center; deterministic mm; independently authored'.ljust(80,b' ')+struct.pack('<I',len(tri))+data.tobytes())


def build(out):
    out.mkdir(parents=True,exist_ok=True)
    add('connected rectangular base',box(*S['base_bounds_px'],0,B),'base')
    # Continuous podium, open sunken court, three surrounding tiers.
    podium=box(110,609,20,384,B-.1,DATUM)
    court=[(244,351,114,242,DATUM-1.85),(254,344,124,234,DATUM-3.70),(266,338,134,228,B)]
    for x0,x1,y0,y1,z in court: podium=podium-box(x0,x1,y0,y1,z,DATUM+1)
    add('three-tier sunken courtyard podium',podium,'landscape')
    # Uphill access platform and stair flight beside hall; eleven roughly 0.23 m risers.
    add('west upper entry ground',box(587,609,97,365,B-.05,zm(2.5)),'landscape')
    for i in range(11):
        x0=464+i*(123/11);add(f'entrance stair {i+1:02d}',box(x0,587,281,309,DATUM-.08,zm(2.5)*(0)+DATUM+(i+1)*2.5*M/11),'stair')
    # Room walls stop below shell, leaving saddle-shaped clerestories.
    low=zm(2.5)-.95
    wallx('classroom east exterior',127,107,246,low)
    wally('classroom south exterior',108,127,220,low)
    wally('classroom room partition',178,127,220,low)
    wally('classroom north exterior',246,127,220,low)
    glazed_x('classroom court glazing',220,110,245,low,7)
    # Practice room rear wall and eight narrow rooms; projecting fins are explicit plan interpretation.
    wally('practice rear enclosure',43,185,463,low)
    glazed_y('practice court glazing',102,185,463,low,9)
    for i,x in enumerate(np.linspace(185,463,9)):
        wallx(f'practice partition {i+1:02d}',float(x),24,102,low)
    # Gallery and classroom-to-gallery connection.
    wallx('gallery east exterior',116,275,367,low)
    wally('gallery north exterior',367,116,463,low)
    wallx('gallery west exterior',463,309,367,low)
    wally('gallery court wall west section',275,116,188,low)
    glazed_y('gallery court glazing',275,254,394,low,5)
    wally('vestibule gallery screen',309,394,463,low)
    wallx('gallery music room partition',186,275,367,low)
    # Toilet enclosure read from plan; interior partitions omitted at this exterior-study scale.
    for y in [275,309]: wally(f'gallery service enclosure {y}',y,188,254,low)
    for x in [188,254]: wallx(f'gallery service enclosure {x}',x,275,309,low)
    # Historic entrance wall with a single round moon gate. Gate location remains photographic inference.
    x=S['moon_gate_center_px'][0]; half=F['wall_thickness_mm']/(2*K)
    gatewall=box(x-half,x+half,248,310,DATUM-.08,zm(3.1))
    gatecenter=[xp(x),yp(S['moon_gate_center_px'][1]),DATUM+4.1]; radius=S['moon_gate_radius_mm_fabricated']
    cutter=md.Manifold.cylinder(5,radius,radius,F['round_gate_segments'],center=True).rotate([0,90,0]).translate(gatecenter)
    add('single entrance moon gate',gatewall-cutter,'wall_with_round_opening')
    # Raised hall; source low-point columns are deliberately eccentric inside roof cells.
    halllow=zm(5.8)-1.05
    for y in [104,247]:wally(f'hall long outer wall {y}',y,364,600,halllow)
    glazed_x('hall courtyard glazing',364,104,247,halllow,7)
    wallx('hall upper rear wall',599,105,247,halllow,bottom=zm(2.5))
    # Tiered audience floor and rear control booth in plan; no invented audience furniture.
    for i in range(10):
        x0=478+i*9.6;add(f'hall seating floor tier {i+1:02d}',box(x0,580,107,245,DATUM-.08,DATUM+(i+1)*2.5*M/10),'stair')
    booth=box(568,599,149,209,zm(2.5)-.05,zm(4.65))
    booth=booth-box(567,595,153,205,zm(2.5)+1.2,zm(4.65)-1.2)
    add('rear projecting control booth',booth,'wall')
    # Local underside tie at the practice-shell/hall-wall interface; stays below the source roof surface.
    add('practice hall underside connection reinforcement',rounded_box(*F['targeted_practice_hall_tie_px'],zm(2.5)-.6,zm(2.5)+1.2,.42),'fabrication_reinforcement')
    roofs=[]
    x0,x1,y0,y1=S['classroom_roof_bounds_px'];dx=(x1-x0)/2;dy=(y1-y0)/2
    for row,cy in enumerate(S['classroom_support_y_px']):
        for col,cx in enumerate(S['classroom_support_x_px']):
            roofs.append(umbrella(f'classroom roof {row+1}-{col+1}',[x0+dx*col,x0+dx*(col+1),y0+dy*row,y0+dy*(row+1)],cx,cy,zm(S['low_roof_valley_m']),zm(S['low_roof_rim_m'])))
    x0,x1,y0,y1=S['practice_roof_bounds_px'];dx=(x1-x0)/4
    for i,cx in enumerate(S['practice_support_x_px']):
        roofs.append(umbrella(f'practice roof {i+1}',[x0+dx*i,x0+dx*(i+1),y0,y1],cx,S['practice_support_y_px'],zm(S['low_roof_valley_m']),zm(S['low_roof_rim_m'])))
    x0,x1,y0,y1=S['gallery_roof_bounds_px'];dx=(x1-x0)/5;dy=(y1-y0)/2
    for row,cy in enumerate(S['gallery_support_y_px']):
        for col,cx in enumerate(S['gallery_support_x_px']):
            roofs.append(umbrella(f'gallery vestibule roof {row+1}-{col+1}',[x0+dx*col,x0+dx*(col+1),y0+dy*row,y0+dy*(row+1)],cx,cy,zm(S['low_roof_valley_m']),zm(S['low_roof_rim_m'])))
    x0,x1,y0,y1=S['hall_roof_bounds_px'];xs=S['hall_support_x_px'];ys=S['hall_support_y_px']
    edges=[x0]+[(a+b)/2 for a,b in zip(xs,xs[1:])]+[x1];yedges=[y0,(ys[0]+ys[1])/2,y1]
    for row,cy in enumerate(ys):
        for col,cx in enumerate(xs):
            roofs.append(umbrella(f'hall roof {row+1}-{col+1}',[edges[col],edges[col+1],yedges[row],yedges[row+1]],cx,cy,zm(S['hall_roof_valley_m']),zm(S['hall_roof_rim_m'])))
    model=union(PARTS).as_original().simplify(F['boolean_simplification_tolerance_mm'])
    if model.status()!=md.Error.NoError: raise RuntimeError(model.status())
    raw=model.to_mesh64(); mesh=trimesh.Trimesh(np.asarray(raw.vert_properties)[:,:3],np.asarray(raw.tri_verts),process=False)
    deterministic_stl(mesh,out/'model.stl')
    np.savez(out/'raw-mesh.npz',vertices=np.asarray(mesh.vertices),faces=np.asarray(mesh.faces))
    meta={'stl_sha256':hashlib.sha256((out/'model.stl').read_bytes()).hexdigest(),'title':P['title'],'dimensions_mm':mesh.extents.tolist(),'bounds_mm':mesh.bounds.tolist(),'volume_mm3':float(mesh.volume),'triangles':len(mesh.faces),'vertices':len(mesh.vertices),'umbrella_count':len(roofs),'roofs':roofs,'components':RECORD,'mm_per_source_metre':M,'nominal_scale_denominator':1000/M,'manifold_status':str(model.status()),'dependencies':{p:importlib.metadata.version(p) for p in ['numpy','trimesh','manifold3d','shapely','scipy','rtree','pillow']}}
    (out/'build-manifest.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:meta[k] for k in ['dimensions_mm','volume_mm3','triangles','vertices','umbrella_count','manifold_status']},indent=2))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,default=HERE/'output'); args=a.parse_args();build(args.out)
