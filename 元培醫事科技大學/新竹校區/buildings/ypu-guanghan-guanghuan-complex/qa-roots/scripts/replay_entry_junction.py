"""Replay the actual shared convex edge at the current entrance junction."""
from pathlib import Path
import argparse,json,numpy as np
from original_geometry import OriginalGeometry,output_directory,EXPECTED_SHA
P=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--model',type=Path,required=True)
parser.add_argument('--ray-evidence',type=Path,default=P/'evidence/representative-original-normal-rays.json')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
R=output_directory(args.output,P/'evidence');SHA=EXPECTED_SHA
geometry=OriginalGeometry(args.model,SHA)
m=geometry.m
nn,fa,ee=geometry.nn,geometry.fa,geometry.ee
cast,inside=geometry.cast,geometry.inside
d=json.loads(args.ray_evidence.read_text());assert d['stl_sha256']==SHA;r=next(r for r in d['samples']if r['sample_original_face_id']==1311);fid=1311;xf=r['all_intersection_hits'][1]['original_face_id'];p=np.array(r['inside_first_chord_midpoint_mm']);di=-(nn[fid]+nn[xf]);di/=np.linalg.norm(di);hs=cast(p,di);shared=[i for i,(a,b)in enumerate(fa)if set([int(a),int(b)])==set([fid,xf])];assert len(shared)==1;i=shared[0];span=hs[0]['distance_mm'];out={'stl_sha256':SHA,'source_original_face_id':fid,'first_exit_original_face_id':xf,'surface_point_mm':r['original_surface_point_mm'],'first_solid_normal_chord_mm':r['first_solid_normal_chord_mm'],'shared_original_edge':{'adjacency_id':i,'original_faces':fa[i].tolist(),'endpoints_mm':ee[i].tolist(),'convex':bool(m.face_adjacency_convex[i]),'normal_angle_degrees':float(np.degrees(m.face_adjacency_angles[i]))},'first_solid_midpoint_mm':p.tolist(),'common_inward_bisector_direction':di.tolist(),'dot_bisector_source_exit_normals':(nn[[fid,xf]]@di).tolist(),'connected_bisector_first_exit_mm':span,'all_bisector_hits':hs,'controls':{'origin_inside':inside(p),'at_0_8mm_inside':inside(p+di*.8),'root_midpoint_inside':inside(p+di*span/2),'air_after_first_exit':inside(p+di*(span+1e-5))},'interpretation':'Actual source and first-exit triangles meet directly at one convex edge. The generic nearest-G-segment direction crosses a recess and re-enters, so it is NOT a continuous backing root. The actual local source/exit inward bisector is separate connected-root evidence.','limitations':['Does not replace the original short normal chord with a thicker value or prove a global minimum wall thickness.','No longest-axis fallback, no repair.']};(R/'current-entry-junction-convex-corner.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
