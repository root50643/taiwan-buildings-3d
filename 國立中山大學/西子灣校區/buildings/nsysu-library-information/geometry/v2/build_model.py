"""Bounded NSYSU existing-main-block correction. Drawing-relative, not surveyed.
Python 3.12 + requirements.txt. No downloaded pixels, textures or source meshes.
Run python build_model.py [--params PATH] [--out DIR]. All outputs millimetres.
"""
import argparse, json, math
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
ROOT=Path(__file__).resolve().parent

def build(p):
    parts=[];cuts=[]; details=[]; records=[]
    def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
    def add(name,x,y,z,w,d,h):
        parts.append(box(x,y,z,w,d,h));records.append({'name':name,'operation':'union','center_xy_bottom_z_m':[x,y,z],'size_m':[w,d,h]})
    def cut(name,x,y,z,w,d,h):
        cuts.append(box(x,y,z,w,d,h));records.append({'name':name,'operation':'difference','center_xy_bottom_z_m':[x,y,z],'size_m':[w,d,h]})
    W=p['body_short_m'];D=p['body_long_m'];B=p['body_top_m'];C=p['crown_top_m'];deck=p['roof_deck_m'];floor=p['ground_floor_m'];end=D/2
    def detail(name,x,y,z,w,d,h):
        details.append(box(x,y,z,w,d,h));records.append({'name':name,'operation':'backed_relief','center_xy_bottom_z_m':[x,y,z],'size_m':[w,d,h]})
    # The entire above-ground envelope; porticoes are genuine open recesses, not black paint.
    add('ground_floor_raised_plinth',0,0,0,W+1.30,D+1.30,floor+.02)
    add('whole_tower_envelope',0,0,floor,W,D,B-floor+.01)
    for side,face in [(-1,'south'),(1,'north')]:
        cut(face+'_two_level_portico',0,side*(end-p['portico_depth_m']/2+.05),floor-.02,W+1,p['portico_depth_m']+.12,p['portico_clear_top_m']-floor+.02)
    # Only the four full-height cylinders per SHORT elevation are supported by the elevations.
    for side,face in [(-1,'south'),(1,'north')]:
        for i,x in enumerate(p['column_x_m']):
            details.append(Manifold.cylinder(B-floor+.04,p['column_radius_m'],p['column_radius_m'],circular_segments=32).translate((x,side*p['column_y_m'],floor-.01)))
            records.append({'name':f'{face}_round_column_{i+1}','operation':'union_cylinder','center_xy_bottom_z_m':[x,side*p['column_y_m'],floor-.01],'radius_m':p['column_radius_m'],'height_m':B-floor+.04})
    # Per-elevation windows: ten ranks; short face six windows per bay, long nine groups of four.
    for side,face in [(-1,'south'),(1,'north')]:
        for rank,z in enumerate(p['floor_window_bottoms_m']):
            y=side*(end-p['portico_depth_m'] if rank<2 else end)
            for bay,xc in enumerate(p['short_window_centers_m']):
                # South central two-level glazed entry and revised north door replace generic 1F windows.
                if bay==1 and ((face=='south' and rank<2) or (face=='north' and rank==0)):continue
                for k in range(p['short_windows_per_bay']):
                    x=xc+(k-(p['short_windows_per_bay']-1)/2)*p['window_pitch_m']
                    cut(f'{face}_F{rank+1}_bay{bay+1}_window{k+1}',x,y,z,p['window_width_m'],2*p['window_depth_m'],p['window_height_m'])
                    cut(f'{face}_F{rank+1}_bay{bay+1}_sill{k+1}',x,y,z-.65,p['window_width_m'],2*p['sill_recess_depth_m'],p['sill_recess_height_m'])
        # Drawn south double-height glazing versus later revised north 1F sliding-door hierarchy.
        y=side*(end-p['portico_depth_m'])
        ztop=p['portico_clear_top_m']-.18 if face=='south' else 2.78
        cut(face+'_central_entry_backing',0,y,floor+.02,9.25,.70,ztop-floor-.02)
        # Backed mullion relief is part of the monolithic solid, never free floating.
        for k in [-2,-1,0,1,2]:detail(face+'_entry_vertical_mullion_'+str(k),k*1.75,y-side*.18,floor+.01,.22,.45,ztop-floor)
        if face=='south':
            for z in [2.48,4.15]:detail('south_entry_transom_'+str(z),0,y-side*.18,z,9.35,.45,.20)
        else:detail('north_revised_door_transom',0,y-side*.18,2.36,9.35,.45,.20)
    for side,face in [(-1,'west'),(1,'east')]:
        for rank,z in enumerate(p['floor_window_bottoms_m']):
            for g,yc in enumerate(p['long_window_group_centers_m']):
                if rank<2 and g in [0,8]:continue # open two-level short-end porticoes, not invented side windows
                for k in range(p['long_windows_per_group']):
                    y=yc+(k-1.5)*p['long_window_pitch_m']
                    cap=p['connector_scope_cap_y_interval_m']
                    if rank==2 and y+p['long_window_width_m']/2>cap[0] and y-p['long_window_width_m']/2<cap[1]:continue # official3F connector interface, flush neutral scope cap
                    cut(f'{face}_F{rank+1}_group{g+1}_window{k+1}',side*W/2,y,z,2*p['window_depth_m'],p['long_window_width_m'],p['window_height_m'])
                    cut(f'{face}_F{rank+1}_group{g+1}_sill{k+1}',side*W/2,y,z-.65,2*p['sill_recess_depth_m'],p['long_window_width_m'],p['sill_recess_height_m'])
    records.append({'name':'opposite_3F_connector_scope_caps','operation':'omission_of_intersecting_window_relief','long_face_x_m':[-W/2,W/2],'y_interval_m':p['connector_scope_cap_y_interval_m'],'z_interval_m':p['connector_scope_cap_z_interval_m'],'note':'Flush artificial closed tower boundaries; no neighboring bridge or claim of exposed freestanding wall.'})
    # Crown plan is stepped: long-face panels project beyond body, short-face panels project beyond ends.
    add('crown_long_panel_volume',0,0,B-.01,p['crown_short_m'],p['crown_long_panel_m'],C-B+.01)
    add('crown_short_panel_volume',0,0,B-.01,p['crown_end_panel_short_m'],p['crown_long_m'],C-B+.01)
    # One shallow roof deck inside a supported parapet. Not a guessed inaccessible interior.
    cut('roof_deck_recess',0,0,deck,p['crown_short_m']-1.0,p['crown_long_panel_m']-1.0,C-deck+.10)
    cut('roof_end_deck_recess',0,0,deck,p['crown_end_panel_short_m']-1.0,p['crown_long_m']-1.0,C-deck+.10)
    def arch(u,v,w,face):
        z=p['crown_arch_bottom_m'];h=p['crown_arch_vertical_m'];rise=p['crown_arch_rise_m'];depth=p['crown_arch_depth_m'];r=w/2
        poly=[(u-r,z),(u+r,z),(u+r,z+h)]+[(u+r*math.cos(t),z+h+rise*math.sin(t)) for t in np.linspace(0,math.pi,49)[1:]]
        a=CrossSection([poly]).extrude(depth*2).rotate((90,0,0)).translate((0,v+depth,0))
        if face in ['east','west']:a=a.rotate((0,0,90))
        cuts.append(a);records.append({'name':face+'_crown_arch','operation':'arched_recess','center_m':u,'width_m':w,'bottom_m':z,'depth_m':depth})
    for side,face in [(-1,'south'),(1,'north')]:
        for u in p['crown_arch_short_centers_m']:
            arch(u,side*p['crown_long_m']/2,p['crown_arch_short_width_m'],face)
            cut(face+'_crown_lower_slit',u,side*p['crown_long_m']/2,p['crown_slit_bottom_m'],p['crown_arch_short_width_m'],2*p['crown_arch_depth_m'],p['crown_slit_height_m'])
    for side,face in [(-1,'west'),(1,'east')]:
        for u in p['crown_arch_long_centers_m']:
            # Rotation x=-v, y=u; map to the correct long-face exterior.
            arch(u,-side*p['crown_short_m']/2,p['crown_arch_long_width_m'],face)
            cut(face+'_crown_lower_slit',side*p['crown_short_m']/2,u,p['crown_slit_bottom_m'],2*p['crown_arch_depth_m'],p['crown_arch_long_width_m'],p['crown_slit_height_m'])
    # Unite structural envelope before subtracting all observed recesses.
    solid=Manifold.batch_boolean(parts,0)
    for i in range(0,len(cuts),100):solid=solid-Manifold.batch_boolean(cuts[i:i+100],0)
    # Exterior approach abstractions stop inside the tower boundary; hidden ramps/neighbor wings omitted.
    additions=[]
    for side,face in [(-1,'south'),(1,'north')]:
        for i in range(3):
            y=side*(end+.95-i*.42);z=.01;h=.12*(i+1)+.04
            additions.append(box(0,y,z,10.3,1.0,h));records.append({'name':face+'_three_step_abstraction_'+str(i+1),'operation':'union','center_xy_bottom_z_m':[0,y,z],'size_m':[10.3,1.0,h]})
    # Exactly ONE roof mass. The museum's displaced left drawing is explicitly excluded.
    mx,my=p['machine_center_xy_m'];additions.append(box(mx,my,deck-.05,p['machine_short_m'],p['machine_long_m'],p['machine_top_m']-deck+.05))
    records.append({'name':'single_offset_roof_machine_mass','operation':'union','center_xy_bottom_z_m':[mx,my,deck-.05],'size_m':[p['machine_short_m'],p['machine_long_m'],p['machine_top_m']-deck+.05]})
    solid=solid+Manifold.batch_boolean(additions+details,0)
    # Scale drawing-metre interpretation to independent display millimetres; base is presentation only.
    scale=p['model_mm_per_drawing_m'];base=p['base_mm'];solid=solid.scale((scale,scale,scale)).translate((0,0,base[2]-.03))
    solid=solid+box(0,0,0,*base)
    assert len(solid.decompose())==1,[(c.volume(),c.bounding_box()) for c in solid.decompose()]
    m=solid.simplify(0.000001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
    section=solid^Manifold.cube((base[0]+2,base[1]+2,6.0)).translate((-(base[0]+2)/2,-(base[1]+2)/2,0))
    sm=section.to_mesh64();section_mesh=trimesh.Trimesh(np.asarray(sm.vert_properties)[:,:3],np.asarray(sm.tri_verts),process=True)
    return mesh,records,section_mesh

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--params',type=Path,default=ROOT/'params.json');ap.add_argument('--out',type=Path,default=ROOT);a=ap.parse_args();p=json.loads(a.params.read_text());a.out.mkdir(parents=True,exist_ok=True)
    mesh,records,section_mesh=build(p);assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
    mesh.export(a.out/'model.stl');np.savez_compressed(a.out/'mesh-data.npz',vertices=mesh.vertices.astype('<f4'),faces=mesh.faces.astype('<i4'))
    np.savez_compressed(a.out/'plan-section-data.npz',vertices=section_mesh.vertices.astype('<f4'),faces=section_mesh.faces.astype('<i4'))
    (a.out/'construction-parts.json').write_text(json.dumps(records,indent=2)+'\n')
    summary={'schema':'bounded-exterior-build-v1','units':'mm','vertices':len(mesh.vertices),'triangles':len(mesh.faces),'bounds_mm':mesh.bounds.tolist(),'volume_mm3':float(mesh.volume),'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),'components':len(mesh.split()),'arch_recesses':{'south':3,'north':3,'east':4,'west':4},'roof_machine_masses':1,'new_package_count':0,'all_side_truecolor':False,'preview_material':'Existing neutral warm-stone preview only; not actual restoration'}
    (a.out/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary))
if __name__=='__main__':main()
