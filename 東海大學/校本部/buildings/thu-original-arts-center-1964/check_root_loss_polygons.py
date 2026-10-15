#!/usr/bin/env python3
"""Exact-instance radial root evidence for every retained strict opening loss.
This does not change strict morphology results or create an exemption.
The original section polygon must contain one declared head, a radius >=0.4 mm
center disk, and the complete fan from every original boundary edge to that
head. Original-triangle radial rays verify each boundary edge midpoint.
Every loss piece, including tiny numerical pieces, remains in the evidence.
"""
from check_root_supports import *
from shapely import from_wkb
from shapely.geometry import Polygon,Point


def original_section_faces(tri,z):
    result={};bad=[]
    ix=np.where((tri[:,:,2].min(1)<=z)&(tri[:,:,2].max(1)>=z))[0]
    for fi in ix:
        f=tri[fi];pts=[]
        for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
            if tuple(a)>tuple(b):a,b=b,a
            if a[2]==z and b[2]==z:bad.append(int(fi));continue
            if a[2]==z:pts.append(tuple(a[:2]))
            elif b[2]==z:pts.append(tuple(b[:2]))
            elif min(a[2],b[2])<z<max(a[2],b[2]):pts.append(tuple((a+(b-a)*(z-a[2])/(b[2]-a[2]))[:2]))
        pts=list(dict.fromkeys(pts))
        if len(pts)==2 and pts[0]!=pts[1]:result.setdefault(tuple(sorted(pts)),[]).append(int(fi))
    return result,bad

def parts(g):return list(g.geoms)if hasattr(g,'geoms')else[g]
def audit_losses(stl,root_report,source_sections,out):
    start=time.time();out.mkdir(exist_ok=True,parents=True);stlsha=sha(stl);cert=json.loads(root_report.read_text());details=json.load(gzip.open(root_report.parent/cert['detail_file'],'rt'));source=json.load(gzip.open(source_sections,'rt'))
    if source['stl_sha256']!=stlsha or cert['stl_sha256']!=stlsha:raise ValueError('Source SHA mismatch')
    if not cert['passed']:raise ValueError('Root certificate is not passed')
    raw,tri,normals=raw_read(stl);failures=[c for c in source['components']if not c['passed']];rows=[];queries=[];unclassified=[];sections={};piece_rows=[]
    roots=details['roots']
    for ci,record in enumerate(failures):
        poly=from_wkb(bytes.fromhex(record['original_wkb_hex']));lost=from_wkb(bytes.fromhex(record['lost_wkb_hex']));z=record['z_mm'];centers=[r for r in roots if poly.contains(Point(r['actual_head_xy_mm'])) and abs(z-r['source_valley_mm'])<1.2]
        reasons=[]
        if len(centers)!=1:
            unclassified.append({'component_record_index':ci,'record':record,'reason':'not_exactly_one_source_head_inside_failed_component'});continue
        root=centers[0];center=np.array(root['actual_head_xy_mm']);cp=Point(center);radius=float(poly.boundary.distance(cp));radii=[];fan_loss=0;edge_rows=[]
        if z not in sections:sections[z]=original_section_faces(tri,z)
        mapping,coplanars=sections[z]
        if poly.interiors:reasons.append('root_polygon_has_holes')
        coords=list(poly.exterior.coords)
        for ei,(a,b) in enumerate(zip(coords,coords[1:])):
            key=tuple(sorted([tuple(a),tuple(b)]));faces=mapping.get(key,[]);line=LineString([a,b]);fan=Polygon([center,a,b]);exterior_area=float(fan.difference(poly).area);fan_loss+=exterior_area
            if not faces:reasons.append('original_boundary_edge_not_mapped_to_original_triangle')
            p=(np.array(a)+np.array(b))/2;direction=center-p;dist=float(np.linalg.norm(direction));radii.append(dist)
            if dist<1e-10:reasons.append('boundary_edge_midpoint_at_source_head');continue
            direction=np.r_[direction/dist,0.];p3=np.r_[p,z];origin=p3-200*direction;target=p3+direction*(dist/2);qid=len(queries)
            queries.append({'root_index':root['root_index'],'root_name':root['name'],'component_record_index':ci,'component_key':[record['grid'],z,record['component']],'boundary_edge_index':ei,'role':'source_head_radial_original_boundary_midpoint','source_original_face_ids':faces,'source_boundary_midpoint_mm':p3.tolist(),'source_original_face_normals':[normals[f].tolist()for f in faces],'origin_mm':origin.tolist(),'direction':direction.tolist(),'target_point_mm':target.tolist(),'target_t_mm':200+dist/2,'expected_original_entry_t_mm':200.})
            edge_rows.append({'boundary_edge_index':ei,'original_face_ids':faces,'original_triangle_vertices_mm':[tri[f].tolist()for f in faces],'segment_xy_mm':[a,b],'fan_outside_original_polygon_area_mm2':exterior_area,'midpoint_radial_query_id':qid})
        if radius-1e-7<.4:reasons.append('source_head_center_disk_radius_below_0p4')
        if fan_loss>1e-9:reasons.append('complete_original_boundary_fan_not_inside_original_polygon')
        # All pieces are retained. Intersection is against exact original boundary
        # lines, not against a buffered stand-in for the original polygon.
        prow=[]
        for pi,piece in enumerate(parts(lost)):
            edge_ids=[];source_faces=set();boundary_length=0
            for e in edge_rows:
                line=LineString(e['segment_xy_mm']);shared=line.intersection(piece);length=float(shared.length)
                if length>0:
                    edge_ids.append(e['boundary_edge_index']);source_faces.update(e['original_face_ids']);boundary_length+=length
            outside=float(piece.difference(poly).area)
            q={'component_record_index':ci,'loss_piece_index':pi,'root_index':root['root_index'],'root_name':root['name'],'geometry_type':piece.geom_type,'loss_piece_wkb_hex':piece.wkb_hex,'area_mm2':float(piece.area),'bounds_mm':list(piece.bounds),'original_boundary_edge_indices':edge_ids,'original_face_ids':sorted(source_faces),'original_boundary_overlap_length_mm':boundary_length,'outside_original_component_area_mm2':outside,'candidate_classification':'source_bound_radial_root_boundary_piece'if edge_ids and outside<1e-9 else'unclassified_no_positive_original_boundary_overlap'}
            prow.append(len(piece_rows));piece_rows.append(q)
        rows.append({'component_record_index':ci,'strict_original_record':record,'strict_morphology_passed':False,'source_root_index':root['root_index'],'source_root_name':root['name'],'source_head_xy_mm':center.tolist(),'z_relative_to_declared_valley_mm':z-root['source_valley_mm'],'exact_instance_neighborhood_xyz_bounds_mm':[[poly.bounds[0],poly.bounds[1],z],[poly.bounds[2],poly.bounds[3],z]],'root_core_certificate_minimum_diameter_mm':root['minimum_certified_core_diameter_mm'],'source_head_inscribed_disk_radius_lower_bound_mm':radius-1e-7,'complete_radial_chord_lower_bound_mm':2*(radius-1e-7),'sum_boundary_fan_outside_area_mm2':fan_loss,'proof':'Every original boundary edge and source head forms a triangle contained in this exact original section polygon. The source-head disk of the certified radius lies in the polygon by minimum distance to its complete boundary. Therefore every radial segment from every point on every boundary edge reaches the disk and continues through it for a continuous first material chord at least twice that radius. Actual all-original-triangle BVH and winding witnesses are retained for each original boundary edge midpoint.','original_boundary_edges':edge_rows,'loss_piece_ids':prow,'geometric_failure_reasons':sorted(set(reasons))})
    print(f'Prepared {len(rows)}/{len(failures)} failed components, {len(piece_rows)} loss pieces, {len(queries)} original-boundary rays',flush=True)
    with tempfile.TemporaryDirectory(prefix='root_loss_work_',dir=out)as td:
        temp=Path(td);rays=run_rays(tri,queries,temp);controls=[]
        for qi,q in enumerate(rays):
            v=q['root_interval']
            if v is None:continue
            if abs(v['entry_t_mm']-q['expected_original_entry_t_mm'])>2e-7:q['failure_reasons'].append('selected_root_interval_does_not_start_at_original_source_boundary')
            if any(float(np.dot(normals[f],q['direction']))>=-1e-10 for f in q['source_original_face_ids']):q['failure_reasons'].append('radial_direction_not_strictly_inward_to_source_face')
            q['passed']=not q['failure_reasons'];o=np.array(q['origin_mm']);d=np.array(q['direction']);a,b=v['entry_t_mm'],v['exit_t_mm'];nxt=v['next_air_end_t_mm'];gap=nxt-b if nxt is not None else 1.
            for role,t,e in [('root_first_material_midpoint',(a+b)/2,1),('root_before_entry_air',a-1e-4,0),('root_following_air',b+min(1e-4,gap/4),0)]:controls.append({'query_id':qi,'role':role,'point_mm':(o+d*t).tolist(),'expected_winding':e})
        np.array([c['point_mm']for c in controls],dtype='<f8').tofile(temp/'root_controls.bin')
        subprocess.run(['g++','-O3','-fopenmp','-std=c++17',str(HERE/'root_winding.cpp'),'-o',str(temp/'root_winding')],check=True)
        subprocess.run([str(temp/'root_winding'),str(temp/'root_triangles.bin'),str(temp/'root_controls.bin'),str(temp/'root_winding.csv')],check=True,env={**os.environ,'OMP_NUM_THREADS':'2'})
        values=np.loadtxt(temp/'root_winding.csv',delimiter=',')[:,1]
    for c,w in zip(controls,values):c.update(actual_winding=float(w),passed=bool(abs(w-c['expected_winding'])<1e-7))
    failed_controls=collections.defaultdict(list)
    for c in controls:
        if not c['passed']:failed_controls[c['query_id']].append(c)
    for r in rows:
        qi=[e['midpoint_radial_query_id']for e in r['original_boundary_edges']];pi=r['loss_piece_ids'];r['checks']={'unique_source_root_and_contained_fan_disk':not r['geometric_failure_reasons'],'all_original_boundary_midpoint_intervals_pass':all(rays[i]['passed']for i in qi),'all_material_air_winding_controls_pass':all(not failed_controls[i]for i in qi),'every_loss_piece_has_original_boundary_identity':all(piece_rows[i]['candidate_classification']=='source_bound_radial_root_boundary_piece'for i in pi)};r['bounded_radial_evidence_passed']=all(r['checks'].values())
    detail={'stl_sha256':stlsha,'strict_original_morphology_passed':False,'component_records':rows,'loss_piece_records':piece_rows,'all_original_ray_witnesses':rays,'whole_original_mesh_winding_controls':controls,'unclassified_components':unclassified}
    gzipjson(out/'root_loss_details.json.gz',detail)
    unknown_pieces=[p for p in piece_rows if p['candidate_classification'].startswith('unclassified')]
    result={'stl_sha256':stlsha,'bounded_radial_evidence_passed':len(rows)==len(failures)and all(r['bounded_radial_evidence_passed']for r in rows),'strict_morphology_passed':False,'automatic_morphology_exemption_applied':False,'source_sections_sha256':sha(source_sections),'source_root_report_sha256':sha(root_report),'root_validator_sha256':sha(Path(__file__)),'original_failed_component_count':len(failures),'mapped_component_count':len(rows),'retained_loss_piece_count':len(piece_rows),'boundary_radial_query_count':len(rays),'whole_original_mesh_winding_control_count':len(controls),'minimum_complete_radial_chord_lower_bound_mm':min(r['complete_radial_chord_lower_bound_mm']for r in rows),'maximum_failed_component_head_distance_mm':max(max(np.linalg.norm(np.array(p)-r['source_head_xy_mm'])for e in r['original_boundary_edges']for p in e['segment_xy_mm'])for r in rows),'failed_component_evidence':[{k:r[k]for k in['component_record_index','source_root_name','checks','geometric_failure_reasons']}for r in rows if not r['bounded_radial_evidence_passed']],'unclassified_components':unclassified,'unclassified_loss_pieces':unknown_pieces,'failed_or_unclassified_ray_ids':[i for i,r in enumerate(rays)if not r['passed']],'failed_winding_controls':[c for c in controls if not c['passed']],'detail_file':'root_loss_details.json.gz','detail_sha256':sha(out/'root_loss_details.json.gz'),'scope':'This is exact frozen-component and per-loss-piece radial linkage evidence for independent review. Strict radius0.4mm opening-loss failures remain failures. A radial solid chord into a certified support core does not establish local normal thickness at every loss point, and does not by itself authorize excluding any morphology failure. No blanket shell/corner mask, removed failures, altered thresholds, remeshing, or repaired polygons.','elapsed_seconds':time.time()-start}
    writejson(out/'root_loss_report.json',result);print(json.dumps({k:result[k]for k in['bounded_radial_evidence_passed','strict_morphology_passed','original_failed_component_count','mapped_component_count','retained_loss_piece_count','boundary_radial_query_count','minimum_complete_radial_chord_lower_bound_mm','elapsed_seconds']},indent=2),flush=True);return result
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--stl',type=Path,default=HERE/'output/model.stl');a.add_argument('--root-report',type=Path,default=HERE/'root_evidence/root_support_report.json');a.add_argument('--sections',type=Path,default=HERE/'output/qa-sections-full.json.gz');a.add_argument('--out',type=Path,default=HERE/'root_evidence');x=a.parse_args();r=audit_losses(x.stl,x.root_report,x.sections,x.out);raise SystemExit(0 if r['bounded_radial_evidence_passed']else 1)
