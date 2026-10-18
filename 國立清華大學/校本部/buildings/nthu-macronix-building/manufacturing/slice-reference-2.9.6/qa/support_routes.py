"""Finite path audit for actual support deposition; consumes the fixed G-code parse.

No physical adhesion, filament sag or support fragmentation is simulated. Tests
below only prove straight outward *kinematic* clearance for independently cut
support portions or identify a positive obstruction needing another process.
"""
import csv,gzip,json,math
from pathlib import Path
import numpy as np
from shapely.geometry import LineString,box
from shapely.ops import unary_union
import trimesh,manifold3d as m
from audit_supports import ROOT,OUT,WORK,REGIONS,in_box,stats

def sweep_linear(polygon,dx=0,dy=0):
    """Exact planar segment Minkowski sweep; retains concave gaps/holes.

    A convex hull of an entire connected U-shaped patch would falsely fill its
    central void and report wall collisions. Sweep each boundary edge instead.
    """
    from shapely.geometry import Polygon
    from shapely.affinity import translate
    pieces=list(polygon.geoms) if hasattr(polygon,'geoms') else [polygon]
    swept=[]
    for p in pieces:
        if p.is_empty:continue
        swept.extend([p,translate(p,xoff=dx,yoff=dy)])
        for ring in [p.exterior,*p.interiors]:
            coords=list(ring.coords)
            for a,b in zip(coords,coords[1:]):
                q=Polygon([a,b,(b[0]+dx,b[1]+dy),(a[0]+dx,a[1]+dy)]).convex_hull
                if q.area>1e-14:swept.append(q)
    return unary_union(swept)

segs=[]
with gzip.open(OUT/'positive-extrusion-segments.jsonl.gz','rt',encoding='utf8') as f:
    for line in f:
        s=json.loads(line)
        if s['role'] in ('Support material','Support material interface'):segs.append(s)
regions=json.loads(REGIONS.read_text(encoding='utf8'))
result={}

def subset(bbox):return [s for s in segs if in_box(s,bbox)]

# Distinguish the broad façade region from finite open-bay interior.
result['C_depth_bands']=[]
for y0,y1,label in [(-22.5,-21.95,'front_lip_to_fin_front'),
   (-21.95,-20.9,'front_fin_depth_band'),(-20.9,-19.1,'recess_behind_fin_back')]:
    for z0,z1 in [(25,32),(34,41),(43,50)]:
        bbox=[[37.5,y0,z0],[60,y1,z1]]
        hit=subset(bbox)
        result['C_depth_bands'].append(dict(label=label,bbox=bbox,**stats(hit)))

# Build exact mesh cross-section using Manifold's slice (not float graph join).
mesh=trimesh.load(WORK/'input-model.stl',force='mesh',process=True)
solid=m.Manifold(m.Mesh64(np.asarray(mesh.vertices,dtype=np.float64),np.asarray(mesh.faces,dtype=np.uint64)))
assert solid.status()==m.Error.NoError
def polys(z):
    contours=solid.slice(z).to_polygons()
    # Manifold contours include orientation; non-zero winding is represented by
    # union positive-area rings minus negative rings. Check winding first.
    from shapely.geometry import Polygon
    pos=[];neg=[]
    for c in contours:
        p=Polygon(c)
        if p.exterior.is_ccw:pos.append(p)
        else:neg.append(p)
    return unary_union(pos).difference(unary_union(neg))

# For each actual support segment in the narrow C inner-mouth band, intersect
# its deposited-width footprint with the true open bay and sweep -Y to exterior.
# Inspect bottom/mid/top within each deposition stratum, so only testing the
# top plane cannot miss a modeled sill or step obstruction.
checks=[]
for z0,z1 in [(25,32),(34,41),(43,50)]:
  for xmin,xmax in [(37.5,42.5),(43.5,48.5),(49.5,54.5),(55.5,60)]:
    bbox=[[xmin,-21.95,z0],[xmax,-19.1,z1]]
    hit=subset(bbox)
    layerdata=[]
    for ztop in sorted(set(s['p1'][2] for s in hit)):
        group=[s for s in hit if s['p1'][2]==ztop]
        strokes=unary_union([LineString([s['p0'][:2],s['p1'][:2]]).buffer(s['width']/2,
                            cap_style='round',join_style='round') for s in group])
        patch=strokes.intersection(box(xmin,-21.95,xmax,-19.1))
        # Exact planar sweep of each patch through -Y 8 mm (to y<-29).
        from shapely.affinity import translate
        pieces=list(patch.geoms) if hasattr(patch,'geoms') else [patch]
        sweep=sweep_linear(patch,dy=-8)
        h=max(s['height'] for s in group)
        zs=[max(z0,ztop-h)+1e-5,(max(z0,ztop-h)+min(z1,ztop))/2,min(z1,ztop)-1e-5]
        areas=[float(sweep.intersection(polys(z)).area) for z in zs]
        patchbounds=list(patch.bounds) if not patch.is_empty else None
        layerdata.append(dict(z_top=ztop,z_samples=zs,actual_patch_bbox=patchbounds,
           patch_area_mm2=patch.area,outward_Y_sweep_mm=8,
           model_obstruction_area_at_z_mm2=areas,
           straight_outward_patch_clear=max(areas)<1e-7))
    checks.append(dict(bay_x=[xmin,xmax],bay_z=[z0,z1],segments=len(hit),layers=layerdata,
       interpretation='This tests the portion clipped inside the mouth only. It does not assert the whole connected support tree fits through this bay or breaks into this portion.'))
result['C_mouth_outward_patch_clearance']=checks

# B shallow slot: no conflation of cap-under-eave support with the slot itself.
b=next(r for r in regions['regions'] if r['id']=='B')
result['B_shallow_slot_actual_support']=dict(bbox=b['slot_bbox'],**stats(subset(b['slot_bbox'])))

# Actual cap-rear and front-slot support. These tests keep the finite stroke
# width and test the *entire* clipped component, not zero-radius sample rays.
# They still require a separating cut: the whole support body may join other
# external supports at another height. Clear swept pieces do not prove cutting
# access or break-force safety.
from shapely.affinity import translate
result['B_finite_patch_sweeps']=[]
for label,bbox,shift in [
    ('rear_cap_+Y', [[-40,-7.5,50.8],[-4,-4.3,54.1]],(0,8)),
    ('rear_cap_full_height_+Y', [[-40,-7.5,32.8],[-4,-4.3,54.1]],(0,8)),
    ('shallow_front_slot_-Y',b['slot_bbox'],(0,-8))]:
    hit=subset(bbox); tests=[]
    for ztop in sorted(set(s['p1'][2] for s in hit)):
        group=[s for s in hit if s['p1'][2]==ztop]
        strokes=unary_union([LineString([s['p0'][:2],s['p1'][:2]]).buffer(s['width']/2)
                            for s in group])
        patch=strokes.intersection(box(*bbox[0][:2],*bbox[1][:2]))
        pieces=list(patch.geoms) if hasattr(patch,'geoms') else [patch]
        sweep=sweep_linear(patch,dx=shift[0],dy=shift[1])
        h=max(s['height'] for s in group)
        zs=[max(bbox[0][2],ztop-h)+1e-5,
           (max(bbox[0][2],ztop-h)+min(bbox[1][2],ztop))/2,
           min(bbox[1][2],ztop)-1e-5]
        areas=[float(sweep.intersection(polys(z)).area) for z in zs]
        tests.append(dict(z_top=ztop,z_samples=zs,patch_bbox=list(patch.bounds),
          patch_area_mm2=patch.area,components=len(pieces),
          model_obstruction_area_at_z_mm2=areas,straight_outward_patch_clear=max(areas)<1e-7))
    result['B_finite_patch_sweeps'].append(dict(label=label,bbox=bbox,shift_mm=shift,
       support=stats(hit),layers=tests,
       all_tested_patch_strata_clear=all(t['straight_outward_patch_clear'] for t in tests),
       operation_limit='Clipped support piece requires verified separation from the rest of the support body; tool access and adhesion/force are not simulated.'))

# G: check actual support unions for sheets spanning adjacent grille bays.
# Connected 2D patches at one deposition Z are positive evidence of joined
# material. No absence of such patches establishes full 3D disconnection.
g=next(r for r in regions['regions'] if r['id']=='G')
ghit=subset(g['view_bbox']);glayers=[]
gbays=[(18.4,22.6),(23.4,27.6),(28.4,32.6)]
for ztop in sorted(set(s['p1'][2] for s in ghit)):
    group=[s for s in ghit if s['p1'][2]==ztop]
    strokes=unary_union([LineString([s['p0'][:2],s['p1'][:2]]).buffer(s['width']/2)
                        for s in group]).intersection(box(16.5,-20.1,33.5,-18.1))
    pieces=list(strokes.geoms) if hasattr(strokes,'geoms') else [strokes]
    for p in pieces:
        if p.is_empty:continue
        bays=[i+1 for i,(x0,x1) in enumerate(gbays)
              if p.intersection(box(x0,-20.1,x1,-18.3)).area>1e-8]
        if len(bays)<2:continue
        glayers.append(dict(z_top=ztop,bbox=list(p.bounds),area_mm2=p.area,bays=bays))
result['G_joined_multi_bay_patches']=dict(actual_support=stats(ghit),
    connected_inside_grille_at_one_z=glayers,
    interpretation='A listed joined patch is an actual same-layer union, not proof of safe pull force. Zero joined patches would not prove 3D disconnection; outside-front support can join the same bay supports.')

# External support can connect bay pieces in front of the relief, so also test
# the whole nearby façade slab, including the positive support-width fringe.
gwider=subset([[16.1,-20.8,7],[33.9,-18.1,38]])
joined_front=[]
for ztop in sorted(set(s['p1'][2] for s in gwider)):
    group=[s for s in gwider if s['p1'][2]==ztop]
    strokes=unary_union([LineString([s['p0'][:2],s['p1'][:2]]).buffer(s['width']/2)
                        for s in group]).intersection(box(16.1,-20.8,33.9,-18.1))
    pieces=list(strokes.geoms) if hasattr(strokes,'geoms') else [strokes]
    for p in pieces:
        if p.is_empty:continue
        bays=[i+1 for i,(x0,x1) in enumerate(gbays)
              if p.intersection(box(x0,-20.8,x1,-18.3)).area>1e-8]
        if len(bays)>=2:joined_front.append(dict(z_top=ztop,bbox=list(p.bounds),area_mm2=p.area,bays=bays))
result['G_joined_multi_bay_patches']['connected_including_external_front_fringe']=joined_front
result['G_finite_bay_outward_sweeps']=[]
for baynum,(xmin,xmax) in enumerate(gbays,1):
    bbox=[[xmin,-20.1,7],[xmax,-18.3,38]]
    hit=subset(bbox);tests=[]
    for ztop in sorted(set(s['p1'][2] for s in hit)):
        group=[s for s in hit if s['p1'][2]==ztop]
        patch=unary_union([LineString([s['p0'][:2],s['p1'][:2]]).buffer(s['width']/2)
                          for s in group]).intersection(box(xmin,-20.1,xmax,-18.3))
        h=max(s['height'] for s in group)
        zs=[ztop-h+1e-5,ztop-h/2,ztop-1e-5]
        sweep=sweep_linear(patch,dy=-8)
        areas=[float(sweep.intersection(polys(z)).area) for z in zs]
        tests.append(dict(z_top=ztop,patch_bbox=list(patch.bounds),
          model_obstruction_area_at_z_mm2=areas,
          straight_outward_patch_clear=max(areas)<1e-7))
    result['G_finite_bay_outward_sweeps'].append(dict(bay=baynum,bbox=bbox,support=stats(hit),
        layers=tests,all_tested_patch_strata_clear=all(t['straight_outward_patch_clear'] for t in tests),
        operation_limit='Only separated bay support portions. No jaw/tool thickness, grip or break-force validation; never lever against a 0.8mm rib.'))

# After the cap-rear pieces move +Y 8mm, use a conservative projection of all
# mesh triangles above the terrace to test an unobstructed vertical lift.
# Projecting every such triangle (not just sampled horizontal sections) may
# overestimate obstruction; a zero intersection is therefore a useful result.
from shapely.geometry import Polygon
high_mesh_projection=unary_union([Polygon(t[:,:2]) for t in mesh.triangles
                                  if t[:,2].max()>32.80001 and Polygon(t[:,:2]).area>1e-12])
bfull=next(q for q in result['B_finite_patch_sweeps'] if q['label']=='rear_cap_full_height_+Y')
bb=bfull['bbox'];bsegs=subset(bb);translated=[]
for ztop in sorted(set(s['p1'][2] for s in bsegs)):
    group=[s for s in bsegs if s['p1'][2]==ztop]
    p=unary_union([LineString([s['p0'][:2],s['p1'][:2]]).buffer(s['width']/2)
                  for s in group]).intersection(box(*bb[0][:2],*bb[1][:2]))
    translated.append(translate(p,yoff=8))
footprint=unary_union(translated)
lift_obstruction=float(footprint.intersection(high_mesh_projection).area)
result['B_after_Y8_vertical_lift']=dict(translated_actual_support_xy_bbox=list(footprint.bounds),
    projection_obstruction_area_mm2=lift_obstruction,
    no_mesh_projection_above_z32_80001=lift_obstruction<1e-7,
    candidate_operation='Once separated, shift cap-rear portions +Y 8mm, then raise the lowest point beyond Z55.4mm (cap top) in the intervening free strip.',
    operation_limit='Projection proves no model in the translated XY footprint above the terrace; it does not prove the initial cuts, tool access, adhesion release or that uncut connected support follows this footprint.')

# Report actual finite support near each original 40 flag bbox without calling
# any result trapped. These exact original face points are no longer identities
# in the remeshed variant. We test only the documented group envelopes.
result['original_flag_group_envelopes']={}
for r in regions['regions']:
    if r.get('flag_bbox'):
        lo,hi=r['flag_bbox']; bbox=[list(lo),list(hi)]
        # Support upper face is separated .2 mm; inspect 1 mm below flag envelope.
        bbox[0][2]-=1.0;bbox[1][2]+=1e-4
        result['original_flag_group_envelopes'][r['id']]=dict(
          meaning='Support within 1 mm below original triangle envelope; not one-to-one source-point or trapping claim.',
          bbox=bbox,**stats(subset(bbox)))
result['method_limits']=['Finite width swept capsules use comment WIDTH/HEIGHT; line footprint is a geometric approximation.',
 'pre-correction-convex-envelope-routes.json preserves the original over-conservative whole-patch convex sweep output; current sweep uses individual boundary-edge quads to retain concave gaps and holes.',
 'Cross-section sweep checks only independently separated patch portions at three deposition heights, not a connected support removal simulation.',
 'No print, break-force, tool-thickness, calibration or wash test occurred.',
 'A collision-free outward patch is an operation candidate only after cutting support into that patch without damaging model.',
 'C bays with no positive interior extrusion require no interior-support removal for this one slice. External skirts and ledge supports still require removal.']
u=unary_union([box(-3,2,3,3),box(-3,-2,-2,3),box(2,-2,3,3)])
probe=box(-1,-1,1,1)
correct=float(sweep_linear(u,dy=2).intersection(probe).area)
convex=float(unary_union([u,translate(u,yoff=2)]).convex_hull.intersection(probe).area)
assert correct==0.0 and convex==4.0
result['concave_sweep_control']=dict(passed=True,exact_boundary_edge_sweep_probe_area_mm2=correct,
    whole_patch_convex_hull_probe_area_mm2=convex,
    explanation='U-shaped control translated toward its closed outer side preserves its concave gap; whole-patch convex envelope fills it falsely.')
(OUT/'actual-support-routes.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(Cbands=[(r['label'],r['bbox'][0][2],r['segments']) for r in result['C_depth_bands']],
 Bslot=result['B_shallow_slot_actual_support']['segments'],
 Cmouth=[dict(x=c['bay_x'],z=c['bay_z'],segments=c['segments'],layers=c['layers']) for c in checks]),indent=2))
