"""NCCU public center, whole-complex exterior approximation (2021–2022 sources).
All CSG construction is in approximate architectural metres, uniformly scaled.
Exact CSG triangles are exported with no repair, coordinate rounding or face removal.
"""
from pathlib import Path
import argparse, hashlib, json, struct
import numpy as np
from manifold3d import Manifold, CrossSection, OpType
R=Path(__file__).resolve().parent

def require(value,message):
    if not value: raise RuntimeError(message)
def box(a,b,c,d,e,f):
    require(b>a and d>c and f>e, f'Nonpositive box {(a,b,c,d,e,f)}')
    return Manifold.cube((b-a,d-c,f-e)).translate((a,c,e))
def union(parts): return Manifold.batch_boolean(parts,OpType.Add)

def make_model(p):
    s=p['scale_mm_per_m']; base=p['base_thickness_mm']; colors=[]; features=[]
    Z=lambda z:base+s*z
    B=lambda a,b,c,d,e,f:box(s*a,s*b,s*c,s*d,Z(e),Z(f))
    def region(name,a,b,c,d,e,f):
        colors.append(dict(material=name,bounds_mm=[s*a,s*b,s*c,s*d,Z(e),Z(f)]))
    def P(points,z0,z1):
        cs=CrossSection([np.asarray(points)*s]);rad=p['print_corner_radius_mm']
        # Constructive fillets in the source design, never mesh repair/rounding in QA.
        cs=cs.offset(-rad).offset(rad,circular_segments=32)
        return cs.extrude(s*(z1-z0)).translate((0,0,Z(z0)))
    def cut_panel(obj,side,face,a,b,z0,z1,depth=None,material='glass'):
        depth=p['glazing_recess_mm']/s if depth is None else depth
        if side=='south':q=(a,b,face-depth,face+.02,z0,z1)
        elif side=='north':q=(a,b,face-.02,face+depth,z0,z1)
        elif side=='east':q=(face-depth,face+.02,a,b,z0,z1)
        else:q=(face-.02,face+depth,a,b,z0,z1)
        region(material,*q)
        return obj-B(*q)
    def grid(obj,side,face,a,b,z0,z1,pitch=2.5,zpitch=3.2,depth=None):
        # Recessed panes leave solid, well-rooted mullions, never loose wire frames.
        margin=.24; outer=.60; depth=min(.18, p['glazing_recess_mm']/s if depth is None else depth)
        for u in np.arange(a,b-.2,pitch):
            for z in np.arange(z0,z1-.2,zpitch):
                lo=max(u+margin,a+outer); hi=min(u+pitch-margin,b-outer)
                za=max(z+margin,z0+outer);zb=min(z+zpitch-margin,z1-outer)
                if hi>lo and zb>za:obj=cut_panel(obj,side,face,lo,hi,za,zb,depth)
        return obj
    def roof_recess(obj,a,b,c,d,top,drop=.65):
        obj-=B(a,b,c,d,top-drop,top+.1)
        region('roof_green',a,b,c,d,top-drop-.01,top-drop+.02)
        return obj
    a,b,c,d=p['base_bounds_mm'];parts=[box(a,b,c,d,0,base)]
    colors.append(dict(material='base',bounds_mm=[a,b,c,d,0,base+.001]))
    # Lodging main block, exact major plan dimensions from 20 m scale bar.
    a,b,c,d=p['hotel_body_bounds_m']; H=p['hotel_parapet_m']
    hotel=B(a,b,c,d,-.03,H)
    win_dep=p['window_recess_mm']/s
    for side,face in [('south',d),('north',c)]:
        for z in p['hotel_window_bottoms_m']:
            for x in p['hotel_window_centers_x_m']:
                hotel=cut_panel(hotel,side,face,x-.79,x+.79,z,z+2.25,win_dep)
                # Yellow sunshades are thickened to 1 mm, attached across full root.
                zz=z+1.61;ty=p['shade_thickness_mm']/s
                if side=='south':r=(x-.80,x+.80,face-win_dep-.04,face+.28,zz,zz+ty)
                else:r=(x-.80,x+.80,face-.28,face+win_dep+.04,zz,zz+ty)
                parts.append(B(*r));region('yellow',*r)
    hotel=grid(hotel,'south',d,4.2,b-.1,.2,8.3,2.3,3.9)
    hotel=grid(hotel,'north',c,8.4,b-.1,.2,7.8,2.4,3.8)
    # Hotel west stair/elevator seam and near-south vertical strip.
    hotel=grid(hotel,'south',d,1.50,3.25,.2,H-.6,1.75,3.2)
    hotel=grid(hotel,'west',a,10.2,12.6,.2,H-.3,2.4,3.2)
    hotel=grid(hotel,'east',b,9.0,25.15,.2,18.0,2.5,3.5)
    hotel=roof_recess(hotel,.65,26.45,15.3,24.78,H,.65)
    parts.append(hotel)
    core=B(.15,7.8,5.57,9.1,-.02,p['hotel_rooftop_max_m'])
    core=grid(core,'west',.15,6.0,8.8,8.0,H+8.2,2.8,3.5)
    core=cut_panel(core,'north',5.57,1.1,6.8,.7,5.2,.4)
    parts.append(core)
    # Lodging rooftop: stepped lift core, service block and screened cooling deck.
    parts += [B(.15,7.8,8.7,15.2,H-.8,p['hotel_rooftop_max_m']),B(7.75,16.2,8.75,14.8,H-.8,H+6.8)]
    cool=B(17.6,26.1,8.8,14.5,H-.8,H+8.2)
    for side,face,lo,hi in [('north',8.8,17.9,25.8),('south',14.5,17.9,25.8),('east',26.1,9.1,14.2)]:
        
        for zz in np.arange(H+.4,H+7.9,.75):
            cool=cut_panel(cool,side,face,lo+.6,hi-.6,zz,min(zz+.28,H+7.9),.14,'metal')
    region('metal',17.5,26.2,8.7,14.6,H-.5,H+8.3)
    cool-=B(18.3,25.4,9.5,13.8,H+6.8,H+8.3)
    parts.append(cool)
    for x in [19.8,23.8]:
        parts.append(Manifold.cylinder(s*1.0,s*1.3,s*1.3,24).translate((s*x,s*11.6,Z(H+6.6))))
    for x in [5.8,11.4,15.6]:parts.append(B(x,x+2.0,15.0,16.6,H-.8,H+.5))
    # Entrance canopy (thickened plate) attached directly into the main facade.
    parts.append(B(8.5,18.8,25.2,28.8,3.7,4.4));region('metal',8.5,18.8,25.2,28.8,3.7,4.4)
    # Exhibition: north classroom block, east service spine, lower central atrium body.
    EH=p['exhibition_parapet_m']; GH=p['exhibition_central_garden_m']; LT=p['exhibition_lower_terrace_m']
    expo=B(37.65,62.08,0,34.3,-.02,EH)
    # Real depressed roof garden, open on its west edge, not a filled upper cuboid.
    expo-=B(37.64,49.75,15.85,33.7,GH,EH+.1)
    region('roof_green',37.64,49.75,15.85,33.7,GH-.01,GH+.02)
    # North facade has four vertical segmented bands, not horizontal ribbon windows.
    north_bands=[(39.15,41.35),(47.05,47.95),(49.25,50.15),(58.5,60.7)]
    for aa,bb in north_bands:
        for z in np.arange(.5,EH-1.1,4.35):expo=cut_panel(expo,'north',0,aa,bb,z,min(z+3.7,EH-.7),.38)
    # West glass wall of central atrium and the north-block south garden return.
    expo=grid(expo,'west',37.65,8.8,34.0,.2,GH-.3,2.5,3.85,.4)
    expo=grid(expo,'south',15.85,37.8,49.5,GH+.1,EH-.4,2.35,2.3,.35)
    expo=grid(expo,'west',49.75,16.0,33.4,GH+.1,EH-.4,2.5,2.3,.35)
    # East service spine: two distinct stacks of protruding, mostly glazed boxes.
    for ya,yb in [(15.0,18.5),(33.3,37.0)]:
        # Main receiving structure overlaps solid spine and southern block.
        for z in [5.0,9.4,13.8,18.2,22.6,27.0,31.4,35.8,40.2]:
            ht=min(z+3.45,EH-.5)
            q=B(61.75,65.55,ya,yb,z,ht)
            q=grid(q,'east',65.55,ya,yb,z,ht,1.75,3.45,.38)
            q=grid(q,'north',ya,62.2,65.55,z,ht,1.7,3.45,.3)
            q=grid(q,'south',yb,62.2,65.55,z,ht,1.7,3.45,.3)
            region('glass_frame',61.75,65.55,ya,yb,z,ht)
            parts.append(q)
    for ya,yb in [(9.0,14.0),(19.3,25.9),(27.3,32.6)]:
        for z in np.arange(6.2,EH-1.0,4.4):expo=cut_panel(expo,'east',62.08,ya+.6,min(ya+2.0,yb-.3),z,z+2.5,.3)
    expo=roof_recess(expo,38.3,61.4,.65,8.1,EH,.65)
    parts.append(expo)
    # Glazed western garden screen visible in the roof and west-side photos.
    # 1.28 mm gross thickness, with only a 0.32 mm exterior recess: rooted, not wire glass.
    screen_top=GH+p['central_garden_screen_height_m']
    screen=B(37.65,38.25,15.85,33.7,GH-.12,screen_top)
    screen=grid(screen,'west',37.65,16.05,33.5,GH+.1,screen_top-.05,2.5,3.9,.15)
    parts.append(screen);region('glass_frame',37.64,38.26,15.84,33.71,GH,screen_top+.01)
    # Southern main stone mass with 9F terrace, upper auditorium and diagonal roofbox.
    south=B(35.3,64.16,34.3,55.7,3.8,LT)
    # Ground-floor setback and visible pillars rather than a wall to the ground.
    ground=B(37.0,62.9,34.3,53.7,-.03,4.0)
    ground=grid(ground,'south',53.7,37.1,62.6,.2,3.8,3.2,3.8,.4)
    ground=grid(ground,'west',37.0,34.6,53.5,.2,3.8,3,3.8,.4)
    parts.append(ground)
    for x,y in [(36.3,54.5),(63.0,54.5),(35.8,36.2)]:
        rad=p['print_corner_radius_mm'];cs=CrossSection.square((.84*s-2*rad,.84*s-2*rad),True).offset(rad,circular_segments=32)
        parts.append(cs.extrude(s*4.13).translate((s*x,s*y,Z(-.03))))
    # Large upper glazed ribbon wraps west and south; pane recesses are backed.
    south=grid(south,'west',35.3,34.6,55.3,31.0,34.8,2.8,3.8,.45)
    south=grid(south,'south',55.7,35.6,63.8,31.0,34.8,2.8,3.8,.45)
    # Six staggered protruding windows: four south, two west.
    # South glazing faces west; the diagonal stone wing grows from its eastern root.
    for side,u,z in [('south',40.2,15.0),('south',47.6,22.5),('south',54.8,12.5),('south',61.2,20.2),('west',43.0,14.1),('west',51.0,21.2)]:
        face=55.7 if side=='south' else 35.3
        if side=='south':pts=[(u-.8,face-.60),(u+.8,face-.60),(u+.8,face+.28),(u-.8,face+1.2)]
        else:pts=[(face+.12,u-.7),(face+.12,u+.7),(face-.88,u+.7),(face-.22,u-.7)]
        q=P(pts,z,z+4.2)
        if side=='south':
            # A thick, full-root wedge carries a shallow west-facing glazing recess.
            # Projection is print-thickened to 2.55 mm; never a knife-edge cutout.
            q=cut_panel(q,'west',u-.8,face-.10,face+.38,z+.60,z+3.60,.12,'glass')
        else:region('glass_frame',face-.9,face+.1,u+.45,u+.71,z+.2,z+4.0)
        parts.append(q)
    # West low yellow reveal, actual major opening expressed in relief.
    south=cut_panel(south,'west',35.3,36.3,39.5,6.2,11.8,.55,'yellow')
    south=cut_panel(south,'west',35.3,37.0,39.1,6.6,11.4,.75)
    # East large southern glazing and yellow low-level volume.
    south=grid(south,'east',64.16,43.3,55.4,13.7,34.8,2.4,3.8,.42)
    parts.append(south)
    yellow=B(60.8,64.6,42.4,55.7,3.85,13.6)
    parts.append(yellow);region('yellow',60.8,64.6,42.4,55.7,3.85,13.6)
    # South terrace has a shallow setback, upper auditorium is shorter in N/S.
    auditorium=B(37.2,64.16,34.3,51.4,LT-.05,EH)
    auditorium=cut_panel(auditorium,'south',51.4,40.5,58.5,LT+.4,LT+2.8,.42)
    auditorium=roof_recess(auditorium,37.9,63.5,35.0,50.75,EH,.65)
    parts.append(auditorium)
    # Guard parapet at the lower south roof garden, 1.2 mm thick.
    rim=p['minimum_rim_mm']/s
    parts += [B(35.3,64.16,55.7-rim,55.7,LT-.08,LT+.85),B(35.3,35.3+rim,34.3,55.7,LT-.08,LT+.85)]
    region('roof_green',36.1,63.4,51.5,55.0,LT-.01,LT+.02)
    # Diagonal upper west gallery and projecting glass end preserve its plan angle.
    # Local rectangular gallery is rotated as one solid with recessed panes.
    # Its diagonal wall is not represented by a blank blue plate.
    gallery=B(0,3.05,0,17.25,LT-.1,EH-.35)
    region_start=len(colors)
    gallery=grid(gallery,'west',0,13.5,17.1,LT+.1,EH-.55,3.6,3.7,.32)
    gallery=grid(gallery,'south',17.25,.1,2.95,LT+.1,EH-.55,2.85,3.7,.32)
    for q in colors[region_start:]:q['local_xy_frame']={'origin_mm':[s*36.0,s*34.3],'angle_degrees':10.7}
    gallery=gallery.translate((0,0,-base)).rotate((0,0,10.7)).translate((s*36.0,s*34.3,base))
    region('glass_frame',32.5,36.5,47.5,52.0,LT-.1,EH-.35)
    parts.append(gallery)
    # Tall stepped eastern roof core plus two visible cooling fans.
    house=B(52.0,61.4,12.4,25.7,EH-.7,p['exhibition_rooftop_max_m'])
    house=cut_panel(house,'west',52,15.0,16.3,EH+.3,EH+2.6,.28)
    house=cut_panel(house,'west',52,21.0,22.3,EH+.3,EH+2.6,.28)
    parts.append(house)
    cooler=B(54.0,64.0,25.5,34.4,EH-.7,EH+5.7)
    cooler-=B(54.6,63.4,26.1,33.8,EH+4.5,EH+5.8)
    region('metal',53.95,64.05,25.45,34.45,EH-.6,EH+5.75)
    for side,face,lo,hi in [('east',64.0,25.8,34.1),('west',54.0,25.8,34.1),('south',34.4,54.3,63.7)]:
        for zz in np.arange(EH+.3,EH+5.4,.75):
            cooler=cut_panel(cooler,side,face,lo+.6,hi-.6,zz,min(zz+.28,EH+5.4),.14,'metal')
    parts.append(cooler)
    for yy in [28.2,31.7]:parts.append(Manifold.cylinder(s*.9,s*1.5,s*1.5,24).translate((s*59.0,s*yy,Z(EH+4.3))))
    # PV major array, backed solid relief. Small real rails/wiring are omitted.
    panel=B(40.8,62.4,41.0,49.8,EH-.75,EH+.28)
    region('pv',40.8,62.4,41.0,49.8,EH-.75,EH+.43)
    parts.append(panel)
    # 12 x 6 relief panels on a continuous thick backing plate. Their corners
    # are constructed with 0.5 mm fillets, so no narrow rectangular islands form.
    rad=p['print_corner_radius_mm']
    for ix in range(12):
        for iy in range(6):
            x=40.8+ix*1.8+.05;y=41.0+iy*(8.8/6)+.05
            w=1.7*s;h=(8.8/6-.1)*s
            cell=CrossSection.square((w-2*rad,h-2*rad)).offset(rad,circular_segments=32).translate((x*s+rad,y*s+rad))
            parts.append(cell.extrude(s*.16).translate((0,0,Z(EH+.27))))
    for xx in [42.0,49.0,56.0]:parts.append(B(xx,xx+2.5,36.6,38.1,EH-.65,EH+.55))
    # Roof-garden skylights: deliberately blunt rooted trapezoids, not needle tips.
    for x,y in [(44.3,20.2),(42.1,22.8),(46.2,25.9)]:
        q=P([(x-1.0,y-.7),(x+.75,y-.5),(x+.55,y+.9),(x-.75,y+.7)],GH-.1,GH+1.1)
        parts.append(q);region('glass_frame',x-1.01,x+.76,y-.71,y+.91,GH,GH+1.11)
    # AD15 / AD21: large oblique roofed stair volume projecting north into the
    # upper court. It is distinct from the external south diagonal gallery.
    # The east end overlaps the service spine; a solid base supports the roof.
    stair=P([(39.4,27.5),(50.1,30.0),(50.1,34.35),(38.6,31.8)],GH-.1,EH-1.0)
    parts.append(stair)
    region('metal',38.5,50.2,27.4,34.4,EH-1.02,EH-.98)
    # Public connection: low platform, elevated garden and two physically open spans.
    podium=B(26.5,38.15,8.72,25.44,-.03,7.8)
    podium=grid(podium,'south',25.44,27.1,37.6,.2,7.5,2.6,3.6,.4)
    podium=grid(podium,'north',8.72,27.1,37.6,.2,7.5,2.6,3.6,.4)
    parts.append(podium)
    # Narrow north service connection carries the elevated terrace without filling gap.
    back=B(26.5,38.15,8.72,11.1,7.7,p['connecting_garden_m']+.1)
    back=grid(back,'north',8.72,27.2,37.5,8,p['connecting_garden_m'],2.5,3.3,.35);parts.append(back)
    terrace=B(26.5,38.15,8.72,25.44,p['connecting_garden_m']-.8,p['connecting_garden_m'])
    region('roof_green',27.1,37.6,11.2,25.2,p['connecting_garden_m']-.01,p['connecting_garden_m']+.01)
    parts.append(terrace)
    low=p['connecting_lower_garden_m']
    parts.append(B(26.5,38.15,14.0,25.44,low-.8,low))
    region('roof_green',27.1,37.6,14.1,25.2,low-.01,low+.01)
    for x,y in [(32.8,12.3),(30.4,17.6),(33.0,21.7)]:
        q=P([(x-1.0,y-.7),(x+.75,y-.5),(x+.55,y+.9),(x-.75,y+.7)],p['connecting_garden_m']-.1,p['connecting_garden_m']+1.1)
        parts.append(q);region('glass_frame',x-1.01,x+.76,y-.71,y+.91,p['connecting_garden_m'],p['connecting_garden_m']+1.11)
    for z0,z1 in [p['bridge_lower_m'],p['bridge_upper_m']]:
        br=B(18.0,38.15,24.1,26.8,z0,z1)
        br=grid(br,'south',26.8,18.2,37.7,z0,z1,2.2,z1-z0,.35)
        br=grid(br,'north',24.1,27.3,37.7,z0,z1,2.2,z1-z0,.35)
        region('glass_frame',18.0,37.9,24.1,26.8,z0,z1)
        parts.append(br)
    # Plaza is a plain base; unsupported paving and planter geometry is omitted.
    result=union(parts)
    require(str(result.status()).endswith('NoError'),str(result.status()))
    require(len(result.decompose())==1, f'CSG has {[(q.volume(),q.bounding_box()) for q in result.decompose()]} solids')
    return result, colors

def save_stl(solid,path):
    m=solid.to_mesh();v=np.asarray(m.vert_properties[:,:3],dtype=np.float32).copy();v[:,1]*=-1
    f=np.asarray(m.tri_verts,dtype=np.int64)[:,[0,2,1]];t=v[f]
    raw=bytearray(b'NCCU public center | 2021-2022 exterior approximation | mm'.ljust(80,b'\0')+struct.pack('<I',len(t)))
    for q in t:
        n=np.cross(q[1].astype(float)-q[0],q[2].astype(float)-q[0]);length=np.linalg.norm(n)
        require(length>0,'Degenerate raw export triangle');n/=length
        raw+=struct.pack('<12fH',*n,*q.ravel(),0)
    path.write_bytes(raw);return len(t)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=R);args=ap.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    p=json.loads((R/'parameters.json').read_text());m,regions=make_model(p);f=args.output_dir/'model.stl';n=save_stl(m,f)
    (args.output_dir/'color-regions.json').write_text(json.dumps(regions,indent=2)+'\n')
    report=dict(triangles=n,stl_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),manifold_status=str(m.status()),components=len(m.decompose()),volume_mm3=m.volume(),csg_bounds_before_y_reflection_mm=m.bounding_box(),export_axes='+X east, +Y north, +Z up',notes='Construction only; original-mesh checks and appearance review are separate.')
    (args.output_dir/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
