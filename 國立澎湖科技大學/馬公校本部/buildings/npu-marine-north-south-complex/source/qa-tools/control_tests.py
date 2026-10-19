"""Known geometric positives/negatives for the all-triangle contact implementation."""
import argparse,hashlib,json,platform
from pathlib import Path
import numpy as np,trimesh
from manufacturing_qa import triangle_contacts

def mesh(vertices,faces):return trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args()
 box=trimesh.creation.box([2,2,2]);far=box.copy();far.apply_translation([5,0,0]);cross=box.copy();cross.apply_translation([.7,.6,.5])
 cases=[
  ('single_closed_box',box,True,None),
  ('two_separated_boxes',trimesh.util.concatenate([box,far]),True,None),
  ('two_crossing_closed_boxes',trimesh.util.concatenate([box,cross]),False,'proper_intersections'),
  ('proper_non_coplanar_triangle_cross',mesh([[-1,-1,0],[1,-1,0],[0,1,0],[0,-.5,-1],[0,-.5,1],[0,.7,0]],[[0,1,2],[3,4,5]]),False,'proper_intersections'),
  ('coplanar_area_overlap',mesh([[0,0,0],[2,0,0],[0,2,0],[.2,.2,0],[1.2,.2,0],[.2,1.2,0]],[[0,1,2],[3,4,5]]),False,'coplanar_overlap'),
  ('non_topological_point_touch',mesh([[0,0,0],[1,0,0],[0,1,0],[1,0,0],[2,0,0],[2,-1,0]],[[0,1,2],[3,4,5]]),False,'nonadjacent_point_contacts'),
  ('non_topological_edge_touch',mesh([[0,0,0],[1,0,0],[0,1,0],[1,0,0],[1,1,0],[0,1,0]],[[0,1,2],[3,4,5]]),False,'nonadjacent_line_contacts'),
  ('legal_shared_edge',mesh([[0,0,0],[1,0,0],[0,1,0],[1,1,0]],[[0,1,2],[1,3,2]]),True,None),
  ('legal_shared_vertex',mesh([[0,0,0],[1,0,0],[0,1,0],[-1,0,0],[0,-1,0]],[[0,1,2],[0,3,4]]),True,None)
 ]
 records=[]
 for name,m,expected,flag in cases:
  result=triangle_contacts(m);counts=result['counts'];got=counts['pass_no_non_topological_contact'];passed=got==expected and (not flag or counts[flag]>0)
  records.append({'case':name,'expected_no_non_topological_contact':expected,'expected_positive_counter':flag,'control_pass':bool(passed),'counts':counts,'records':result['records'],'input_vertices_mm':m.vertices.tolist(),'input_faces':m.faces.tolist()})
  print(name,'PASS' if passed else 'FAIL',flush=True)
 report={'schema_version':1,'all_controls_pass':all(x['control_pass'] for x in records),'case_count':len(records),'trimesh_version':trimesh.__version__,'python_version':platform.python_version(),'implementation_sha256':hashlib.sha256((Path(__file__).parent/'manufacturing_qa.py').read_bytes()).hexdigest(),'control_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':records,'scope':'Controls validate crossing, planar overlap, non-topological point/edge contacts, expected shared topology and ordinary boxes. They do not prove the algorithm correct for every degenerate numerical configuration. Complete candidate topology, positive-volume components, triangle-pair tests and assembly booleans remain separate checks.'}
 Path(args.output).write_text(json.dumps(report,indent=2),encoding='utf-8')
 if not report['all_controls_pass']:raise SystemExit(1)
if __name__=='__main__':main()
