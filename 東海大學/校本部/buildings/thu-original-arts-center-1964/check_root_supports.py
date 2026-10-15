#!/usr/bin/env python3
"""Finite per-support material-core certificates on exact original STL triangles.

No mesh repair, building exception masks, or nominal shell-thickness acceptance.
Each source-declared head gets a connected graph of radius-0.4 mm capsules from
its column stem into four shell directions. Boundary distance sampled at <=.04
mm supplies a rigorous 1-Lipschitz lower bound along the complete segments.
All point distance candidates are original faces; omitted faces are bounded
outside a 1.5 mm cube. Whole-original-mesh winding establishes material side.
Original intersection sections and every selected root first-solid/next-air
interval, original face IDs, raw hits and coplanar overlaps are retained.
"""
from pathlib import Path
import argparse, collections, gzip, hashlib, json, math, os, struct, subprocess, tempfile, time
import numpy as np
import trimesh
from shapely.geometry import LineString, box

HERE=Path(__file__).resolve().parent
DT=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')])

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def writejson(p,obj): p.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def gzipjson(p,obj):
    with p.open('wb') as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0) as g:
        g.write(json.dumps(obj,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
def raw_read(p):
    b=p.read_bytes();n=struct.unpack('<I',b[80:84])[0]
    if len(b)!=84+n*50:raise ValueError('Not exact binary STL size')
    r=np.frombuffer(b,offset=84,count=n,dtype=DT);t=r['vertices'].astype(np.float64)
    n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);a=np.linalg.norm(n,axis=1)
    if not np.all(np.isfinite(t)) or np.any(a<=0):raise ValueError('Invalid original triangle')
    return r,t,n/a[:,None]

class OriginalIndex:
    def __init__(self,tri):
        self.t=tri;self.mesh=trimesh.Trimesh(vertices=tri.reshape(-1,3),faces=np.arange(len(tri)*3).reshape(-1,3),process=False)
        self.tree=self.mesh.triangles_tree
    def clearance(self,p):
        radius=1.5;idx=np.array(sorted(self.tree.intersection(tuple(p-radius)+tuple(p+radius))),int)
        if not len(idx):return {'distance_lower_bound_mm':radius,'closest_original_face_id':None,'closest_point_mm':None,'candidate_count':0,'excluded_bbox_distance_lower_bound_mm':radius}
        c=trimesh.triangles.closest_point(self.t[idx],np.broadcast_to(p,(len(idx),3)))
        ds=np.linalg.norm(c-p,axis=1);k=int(np.argmin(ds));d=float(ds[k]);fi=int(idx[k])
        return {'distance_lower_bound_mm':min(d,radius),'candidate_minimum_distance_mm':d,'closest_original_face_id':fi,'closest_point_mm':c[k].tolist(),'closest_original_triangle_mm':self.t[fi].tolist(),'candidate_count':len(idx),'excluded_bbox_distance_lower_bound_mm':radius}
    def vertical_top(self,xy,reference):
        p=np.r_[xy,100.];d=np.array([0.,0.,-1.]);idx=np.array(sorted(self.tree.intersection((xy[0]-1e-7,xy[1]-1e-7,-1.,xy[0]+1e-7,xy[1]+1e-7,101.))),int)
        t=self.t[idx];e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];cross=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,cross);ok=np.abs(det)>1e-15
        t=t[ok];idx=idx[ok];e1=e1[ok];e2=e2[ok];cross=cross[ok];det=det[ok]
        off=p-t[:,0];u=np.einsum('ij,ij->i',off,cross)/det;q=np.cross(off,e1);v=q@d/det;dist=np.einsum('ij,ij->i',e2,q)/det
        ok=(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(dist>0)
        hits=sorted([(float(100-a),int(b))for a,b in zip(dist[ok],idx[ok])],reverse=True)
        close=[h for h in hits if abs(h[0]-reference)<1.0]
        if not close:raise ValueError('No source-near actual roof top')
        z,fi=max(close)
        return z,fi,hits


def run_rays(tri,queries,directory):
    tri.astype('<f8').tofile(directory/'root_triangles.bin');np.array([q['origin_mm']+q['direction'] for q in queries],dtype='<f8').tofile(directory/'root_queries.bin')
    subprocess.run(['g++','-O3','-std=c++17',str(HERE/'root_rays.cpp'),'-o',str(directory/'root_rays')],check=True)
    subprocess.run([str(directory/'root_rays'),str(directory/'root_triangles.bin'),str(directory/'root_queries.bin'),str(directory/'root_ray_events.txt')],check=True)
    output=[]
    for q,line in zip(queries,(directory/'root_ray_events.txt').read_text().splitlines()):
        a,b,c=line.split('|');meta=list(map(int,a.split(',')));hits=[];cop=[]
        for item in b.rstrip(';').split(';'):
            if item:
                x=item.split(',');hits.append({'t_mm':float(x[0]),'original_face_id':int(x[1]),'barycentric_uv':[float(x[2]),float(x[3])],'normal_dot_direction':float(x[4])})
        for item in c.rstrip(';').split(';'):
            if item:
                x=item.split(',');cop.append({'start_mm':float(x[0]),'end_mm':float(x[1]),'original_face_id':int(x[2]),'plane_distance_mm':float(x[3]),'normal_dot_direction':float(x[4])})
        groups=[]
        for h in hits:
            if not groups or h['t_mm']-groups[-1]['t_mm']>1e-10:groups.append({'t_mm':h['t_mm'],'original_hits':[]})
            groups[-1]['original_hits'].append(h)
        for g in groups:
            nd=np.array([x['normal_dot_direction']for x in g['original_hits']]);g['crossing']='entry'if np.all(nd< -1e-12)else('exit'if np.all(nd>1e-12)else'unclassified')
        intervals=[];target=None
        for i in range(len(groups)-1):
            if groups[i]['crossing']=='entry' and groups[i+1]['crossing']=='exit':
                start,end=groups[i]['t_mm'],groups[i+1]['t_mm'];nxt=groups[i+2]['t_mm']if i+2<len(groups)else None
                v={'entry_t_mm':start,'exit_t_mm':end,'solid_length_mm':end-start,'next_air_end_t_mm':nxt,'next_air_length_mm':None if nxt is None else nxt-end,'entry_original_face_ids':[h['original_face_id']for h in groups[i]['original_hits']],'exit_original_face_ids':[h['original_face_id']for h in groups[i+1]['original_hits']]}
                intervals.append(v)
                if start+1e-8<q['target_t_mm']<end-1e-8:target=v
        reasons=[]
        if meta[1:]!=[0,0]:reasons.append('origin_not_confirmed_outside_by_two_parities')
        if target is None:reasons.append('no_classifiable_material_interval_contains_nominated_root_point')
        if target is not None and target['solid_length_mm']<.8-1e-6:reasons.append('root_material_interval_shorter_than_0p8')
        if any(g['crossing']=='unclassified'for g in groups):reasons.append('unclassified_crossing_retained')
        if target is not None:
            a,b=target['entry_t_mm'],target['next_air_end_t_mm']
            if any(v['end_mm']>a+1e-10 and(b is None or v['start_mm']<b-1e-10)for v in cop):reasons.append('positive_length_boundary_overlap_in_root_or_next_air_interval')
        output.append({**q,'origin_parity_controls':meta[1:],'all_original_hits':hits,'all_coplanar_boundary_intervals':cop,'all_grouped_events':groups,'all_classifiable_material_intervals':intervals,'root_interval':target,'failure_reasons':reasons,'passed':not reasons})
    if len(output)!=len(queries):raise ValueError('Missing ray output rows')
    return output


def explicit_sections(tri,center,valley):
    """Unrepaired original-triangle intersections clipped to declared 2.4 mm box.
    Every contributing original face and any coplanar original face is retained.
    These are witnesses, not polygonized/hull-replaced geometry.
    """
    out=[];planes=[]
    for dz in [-1.6,-1.2,-.8,-.6,-.4,-.2,.05,.3,.6]:planes.append(('horizontal',np.array([center[0],center[1],valley+dz]),np.array([0,0,1.]),np.array([1.,0,0]),np.array([0,1.,0])))
    for angle in [0,45,90,135]:
        a=math.radians(angle);u=np.array([math.cos(a),math.sin(a),0]);v=np.array([0,0,1.]);n=np.cross(u,v);planes.append((f'vertical_{angle}deg',np.array([center[0],center[1],valley-.5]),n,u,v))
    # Conservative original bbox test, independent of normal or feature category.
    lo=np.array([center[0]-3.5,center[1]-3.5,valley-3.]);hi=np.array([center[0]+3.5,center[1]+3.5,valley+3.]);ix=np.where(np.all(tri.max(1)>=lo,axis=1)&np.all(tri.min(1)<=hi,axis=1))[0]
    clip=box(-2.4,-2.4,2.4,2.4)
    for label,o,n,u,v in planes:
        records=[];cop=[];deg=[]
        for fi in ix:
            t=tri[fi];d=(t-o)@n
            if np.all(np.abs(d)<=1e-10):cop.append(int(fi));continue
            if d.min()>1e-10 or d.max()< -1e-10:continue
            pts=[]
            for k in range(3):
                j=(k+1)%3
                if abs(d[k])<=1e-10:pts.append(t[k])
                if d[k]*d[j]<0:pts.append(t[k]+(t[j]-t[k])*d[k]/(d[k]-d[j]))
            unique=[]
            for p in pts:
                if not any(np.linalg.norm(p-q)<1e-8 for q in unique):unique.append(p)
            if len(unique)<2:deg.append({'original_face_id':int(fi),'classification':'point_contact','points_mm':[p.tolist()for p in unique]});continue
            if len(unique)!=2:
                pairs=[(np.linalg.norm(a-b),a,b)for a in unique for b in unique];_,a,b=max(pairs,key=lambda x:x[0]);axis=b-a
                collinear=all(np.linalg.norm(np.cross(p-a,axis))/np.linalg.norm(axis)<1e-8 for p in unique)
                deg.append({'original_face_id':int(fi),'classification':'collinear_duplicate_intersection_stations'if collinear else'unclassified_multiple_intersections','points_mm':[p.tolist()for p in unique]})
                if not collinear:continue
                unique=[a,b]
            p=np.array(unique)-o;uv=np.column_stack([p@u,p@v]);line=LineString(uv).intersection(clip)
            if line.is_empty or line.length<=1e-9:continue
            if line.geom_type!='LineString':deg.append({'original_face_id':int(fi),'classification':'unclassified_clip_'+line.geom_type});continue
            coords=np.array(line.coords);world=o+coords[:,0,None]*u+coords[:,1,None]*v
            records.append({'original_face_id':int(fi),'original_triangle_mm':t.tolist(),'segment_uv_mm':coords.tolist(),'segment_xyz_mm':world.tolist()})
        out.append({'name':label,'plane_origin_mm':o.tolist(),'plane_normal':n.tolist(),'basis_u':u.tolist(),'basis_v':v.tolist(),'declared_clip_uv_mm':[-2.4,-2.4,2.4,2.4],'segments':records,'coplanar_original_face_ids':cop,'degenerate_or_unclassified':deg})
    return out


def audit(stl,manifest,parameters,out,limit=None):
    start=time.time();out.mkdir(exist_ok=True,parents=True);initial_sha=sha(stl)
    meta=json.loads(manifest.read_text());params=json.loads(parameters.read_text());rec,tri,normals=raw_read(stl);idx=OriginalIndex(tri)
    if meta['stl_sha256']!=initial_sha:raise ValueError('Manifest SHA does not match source STL')
    F=params['fabrication'];S=params['source_era'];K=F['mm_per_plan_pixel'];roots=meta['roofs'][:limit];all_paths=[];all_queries=[];sections=[];controls=[];root_records=[]
    for ri,roof in enumerate(roots):
        px,py=roof['head_px'];c=np.array([(px-S['base_bounds_px'][0])*K,(S['base_bounds_px'][3]-py)*K]);valley=roof['valley_mm'];actual_z,topfi,tophits=idx.vertical_top(c,valley)
        # A seed is not acceptance evidence: every complete resulting capsule is checked.
        trunk_bottom=np.r_[c,actual_z-1.8];junction=np.r_[c,actual_z-.75]
        endpoints=[]
        for direction in [[1,0],[0,1],[-1,0],[0,-1]]:
            xy=c+np.array(direction)*1.8;zt,fi,hits=idx.vertical_top(xy,valley+.5)
            candidates=[]
            for down in np.linspace(.42,.75,23):
                p=np.r_[xy,zt-down];q=idx.clearance(p);candidates.append((q['distance_lower_bound_mm'],p,down,q))
            dist,p,down,evidence=max(candidates,key=lambda q:q[0]);endpoints.append({'direction_xy':direction,'point_mm':p.tolist(),'actual_top_z_mm':zt,'actual_top_original_face_id':fi,'actual_top_hits_z_face':hits,'seed_depth_below_actual_top_mm':float(down),'candidate_clearance_mm':dist})
        paths=[('column_stem',trunk_bottom,junction)]+[(f'shell_branch_{i+1}',junction,np.array(e['point_mm']))for i,e in enumerate(endpoints)]
        path_ids=[]
        for pname,a,b in paths:
            length=float(np.linalg.norm(b-a));n=max(1,math.ceil(length/.04));points=np.linspace(a,b,n+1);w=[]
            for j,p in enumerate(points):w.append({'sample_index':j,'point_mm':p.tolist(),**idx.clearance(p)})
            step=length/n;lower=min(q['distance_lower_bound_mm']for q in w)-step/2-1e-6
            path_id=len(all_paths);path_ids.append(path_id);all_paths.append({'path_id':path_id,'root_index':ri,'root_name':roof['name'],'name':pname,'start_mm':a.tolist(),'end_mm':b.tolist(),'segment_length_mm':length,'sample_spacing_mm':step,'numeric_guard_mm':1e-6,'radius_required_mm':.4,'continuous_clearance_lower_bound_mm':lower,'continuous_material_diameter_lower_bound_mm':2*lower,'clearance_passed':lower>=.4,'point_distance_witnesses':w})
            for frac in [0,.25,.5,.75,1]:controls.append({'root_index':ri,'path_id':path_id,'role':'core_path_material','fraction':frac,'point_mm':(a+(b-a)*frac).tolist(),'expected_winding':1})
        # Horizontal root cross-sections at 6 heights and three transverse offsets,
        # plus actual shell-thickness normals at four measured branch endpoints.
        query_ids=[]
        for dz in [-1.6,-1.2,-.9,-.6,-.4,-.2]:
            for angle in [0,45,90,135]:
                ang=math.radians(angle);d=np.array([math.cos(ang),math.sin(ang),0.]);cross=np.array([-d[1],d[0],0.])
                for off in [-.2,0,.2]:
                    target=np.r_[c,actual_z+dz]+off*cross;origin=target-200*d
                    query_ids.append(len(all_queries));all_queries.append({'root_index':ri,'root_name':roof['name'],'role':'head_section','z_relative_to_actual_valley_mm':dz,'section_angle_degrees':angle,'transverse_offset_mm':off,'origin_mm':origin.tolist(),'direction':d.tolist(),'target_point_mm':target.tolist(),'target_t_mm':200.})
        for e in endpoints:
            target=np.array(e['point_mm']);n=normals[e['actual_top_original_face_id']];origin=target+200*n
            query_ids.append(len(all_queries));all_queries.append({'root_index':ri,'root_name':roof['name'],'role':'shell_branch_normal_section','actual_top_original_face_id':e['actual_top_original_face_id'],'origin_mm':origin.tolist(),'direction':(-n).tolist(),'target_point_mm':target.tolist(),'target_t_mm':200.})
        ss=explicit_sections(tri,c,actual_z)
        for si,sec in enumerate(ss):
            if not sec['segments']:
                o=np.array(sec['plane_origin_mm']);u=np.array(sec['basis_u']);v=np.array(sec['basis_v'])
                sec['empty_boundary_control_ids']=[]
                for uv in [[0,0],[-2.39,-2.39],[-2.39,2.39],[2.39,-2.39],[2.39,2.39]]:
                    sec['empty_boundary_control_ids'].append(len(controls));controls.append({'root_index':ri,'section_index':si,'role':'boundary_free_section_classification','point_mm':(o+uv[0]*u+uv[1]*v).tolist(),'expected_winding':None})
        sections.append({'root_index':ri,'root_name':roof['name'],'sections':ss})
        root_records.append({'root_index':ri,'name':roof['name'],'source_head_px':roof['head_px'],'source_valley_mm':valley,'actual_head_xy_mm':c.tolist(),'actual_valley_top_z_mm':actual_z,'actual_head_top_above_declared_shell_valley_mm':actual_z-valley,'head_top_interpretation':'Exposed column cap may stand above the internal shell valley; no nominal shell-thickness assumption is used for acceptance','actual_valley_original_face_id':topfi,'actual_vertical_head_hits_z_face':tophits,'root_neighborhood_xy_half_width_mm':2.4,'stem_start_mm':trunk_bottom.tolist(),'junction_mm':junction.tolist(),'shell_endpoints':endpoints,'path_ids':path_ids,'query_ids':query_ids})
        print(f'Prepared root {ri+1}/{len(roots)}: {roof["name"]}; minimum core diameter lower bound {min(all_paths[i]["continuous_material_diameter_lower_bound_mm"]for i in path_ids):.6f} mm',flush=True)
    with tempfile.TemporaryDirectory(prefix='root_work_',dir=out)as td:
        temp=Path(td);rays=run_rays(tri,all_queries,temp)
        # Winding tests on every core path and all root-interval first-material
        # midpoints and immediately-following air. Two parity probes are retained
        # for every ray origin. No unclassified sample is dropped.
        for qi,q in enumerate(rays):
            v=q['root_interval']
            if v is None:continue
            o=np.array(q['origin_mm']);d=np.array(q['direction']);a,b=v['entry_t_mm'],v['exit_t_mm'];next_t=v['next_air_end_t_mm'];gap=(next_t-b)if next_t is not None else 1.
            for role,t,expect in [('root_first_material_midpoint',(a+b)/2,1),('root_before_entry_air',a-min(1e-4,a/2),0),('root_following_air',b+min(1e-4,gap/4),0)]:
                controls.append({'root_index':q['root_index'],'query_id':qi,'role':role,'point_mm':(o+d*t).tolist(),'expected_winding':expect})
        np.array([c['point_mm']for c in controls],dtype='<f8').tofile(temp/'root_controls.bin')
        subprocess.run(['g++','-O3','-fopenmp','-std=c++17',str(HERE/'root_winding.cpp'),'-o',str(temp/'root_winding')],check=True)
        env={**os.environ,'OMP_NUM_THREADS':'2'}
        subprocess.run([str(temp/'root_winding'),str(temp/'root_triangles.bin'),str(temp/'root_controls.bin'),str(temp/'root_winding.csv')],check=True,env=env)
        winding=np.loadtxt(temp/'root_winding.csv',delimiter=',')[:,1]
    if len(winding)!=len(controls):raise ValueError('Missing winding controls')
    for c,w in zip(controls,winding):
        expect=c['expected_winding'];c.update(actual_winding=float(w),passed=bool(min(abs(w),abs(w-1))<1e-7 if expect is None else abs(w-expect)<1e-7))
    for group in sections:
        for sec in group['sections']:
            ids=sec.get('empty_boundary_control_ids',[])
            if ids:
                vals=[controls[i]['actual_winding']for i in ids];sec['boundary_free_region_classification']='material'if all(abs(v-1)<1e-7 for v in vals)else('air'if all(abs(v)<1e-7 for v in vals)else'unclassified')
    for ri,r in enumerate(root_records):
        cc=[c for c in controls if c['root_index']==ri];ss=sections[ri]['sections'];unclassified=[v for s in ss for v in s['degenerate_or_unclassified']if v['classification'].startswith('unclassified')]
        r['checks']={'actual_exposed_head_top_within_declared_root_vertical_neighborhood':abs(r['actual_valley_top_z_mm']-r['source_valley_mm'])<.4,'five_connected_core_paths':len(r['path_ids'])==5,'all_complete_core_capsules_have_diameter_ge_0p8_mm':all(all_paths[i]['clearance_passed']for i in r['path_ids']),'all_root_first_material_intervals_ge_0p8_and_classified':all(rays[i]['passed']for i in r['query_ids']),'all_whole_original_mesh_winding_controls':all(c['passed']for c in cc),'all_13_declared_sections_retained_and_classified':len(ss)==13 and all(s['segments']or s.get('boundary_free_region_classification')in['material','air']for s in ss),'no_unclassified_section_intersections':not unclassified}
        r['passed']=all(r['checks'].values());r['minimum_certified_core_diameter_mm']=min(all_paths[i]['continuous_material_diameter_lower_bound_mm']for i in r['path_ids']);r['failed_query_ids']=[i for i in r['query_ids']if not rays[i]['passed']];r['failed_controls']=[c for c in cc if not c['passed']]
    end_sha=sha(stl);checks={'source_sha_unchanged':initial_sha==end_sha,'all_26_declared_roots_tested':len(root_records)==26,'every_declared_root_passed':all(r['passed']for r in root_records)}
    details={'stl_sha256':initial_sha,'roots':root_records,'paths':all_paths,'original_interval_queries':rays,'explicit_original_sections':sections,'whole_mesh_winding_controls':controls}
    gzipjson(out/'root_support_details.json.gz',details)
    report={'passed':all(checks.values()),'checks':checks,'stl_sha256':initial_sha,'source_manifest_sha256':sha(manifest),'source_parameters_sha256':sha(parameters),'validator_sha256':{p.name:sha(p)for p in[Path(__file__),HERE/'root_rays.cpp',HERE/'root_winding.cpp']},'original_triangle_count':len(tri),'root_count':len(root_records),'core_path_count':len(all_paths),'root_interval_query_count':len(rays),'explicit_section_count':sum(len(s['sections'])for s in sections),'whole_original_mesh_winding_control_count':len(controls),'minimum_certified_material_core_diameter_mm':min(p['continuous_material_diameter_lower_bound_mm']for p in all_paths),'failed_roots':[r for r in root_records if not r['passed']],'failed_or_unclassified_queries':[{'query_id':i,'root_name':q['root_name'],'reasons':q['failure_reasons']}for i,q in enumerate(rays)if not q['passed']],'failed_winding_controls':[c for c in controls if not c['passed']],'per_instance_summary':[{k:r[k]for k in['root_index','name','passed','checks','minimum_certified_core_diameter_mm']}for r in root_records],'detail_file':'root_support_details.json.gz','detail_sha256':sha(out/'root_support_details.json.gz'),'method':'A source-declared head binds five connected finite original-STL material-core paths. Every path has a certified radius >=0.4 mm from all original triangles, using exact point-to-original-triangle distances at <=0.04 mm spacing, a 1-Lipschitz complete-segment bound, a 1.5 mm omitted-face bounding-box lower bound, and a 1e-6 mm guard. Material side is checked by compensated long-double solid-angle winding over all original triangles. Each instance retains 13 raw original-triangle sections and 76 direct BVH all-hit cross-section rays with first root-solid and next-air intervals, face identity, tangent/coplanar records and material/air controls.','limits':'Finite root-neighborhood linkage certificate only. Does not classify or exempt any morphology opening-loss polygon or original-normal short chord; those require separate source-bounded evidence and independent review. The measured tube is a certified connected >=0.8 mm core, not a claim that every local shell point or every shell face normal has >=0.8 mm thickness. No mesh was repaired, filtered, remeshed or healed.','elapsed_seconds':time.time()-start}
    writejson(out/'root_support_report.json',report);print(json.dumps({k:report[k]for k in ['passed','stl_sha256','root_count','minimum_certified_material_core_diameter_mm','root_interval_query_count','whole_original_mesh_winding_control_count','elapsed_seconds']},indent=2),flush=True)
    return report

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--stl',type=Path,default=HERE/'output/model.stl');a.add_argument('--manifest',type=Path,default=HERE/'output/build-manifest.json');a.add_argument('--parameters',type=Path,default=HERE/'parameters.json');a.add_argument('--out',type=Path,default=HERE/'root_evidence');a.add_argument('--limit',type=int);args=a.parse_args();r=audit(args.stl,args.manifest,args.parameters,args.out,args.limit);raise SystemExit(0 if r['passed']else 1)
