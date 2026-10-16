"""Read-only exhaustive rational re-intersection of flagged original sample rays.

Independent of the CSV hit list and of the production BVH/candidate predicates.
Acceptance, production checkers, STL, sample points and normals remain unchanged.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
import gzip
import hashlib
import json
import math
import sys
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'verification'))
from qa_common import load_stl, require, write_json

EXPECTED = '8ad969e0135c2dfcd505cc85a1a79b78c9982cac3f8b9fe6f0525de9a34a367e'
WEIGHTS = [(F(1,3),)*3,
           tuple(map(F,('.98','.01','.01'))),tuple(map(F,('.01','.98','.01'))),tuple(map(F,('.01','.01','.98'))),
           tuple(map(F,('.495','.495','.01'))),tuple(map(F,('.01','.495','.495'))),tuple(map(F,('.495','.01','.495'))),
           tuple(map(F,('.49','.49','.02'))),tuple(map(F,('.49','.02','.49'))),tuple(map(F,('.02','.49','.49')))]


def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(a,b): return tuple(x*b for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def exact(value): return str(value.numerator)+'/'+str(value.denominator)
def decimal(value): return Decimal(value.numerator)/Decimal(value.denominator)


def main():
    raw,triangles,stored_normals,_ = load_stl(ROOT/'model.stl')
    stl_hash = hashlib.sha256(raw).hexdigest()
    require(stl_hash == EXPECTED,'Wrong trial STL')
    records = json.loads(gzip.decompress((ROOT/'qa/dense/dense-flagged-samples.json.gz').read_bytes()))
    # Every face is retained, including repeated coordinates. Caching an exact
    # coordinate representation is not a merge, weld, or face omission.
    vertices = {}
    exact_triangles = []
    planes = []
    for triangle in triangles:
        points = []
        for point in triangle:
            key = tuple(float(value)for value in point)
            if key not in vertices:
                vertices[key] = tuple(F.from_float(value)for value in key)
            points.append(vertices[key])
        a,b,c = points
        edge1,edge2 = sub(b,a),sub(c,a)
        n = cross(edge1,edge2)
        require(dot(n,n)>0,'Degenerate original triangle')
        exact_triangles.append((a,b,c))
        planes.append((edge1,edge2,n))
    print(f'Prepared all {len(exact_triangles)} original triangles for exact arithmetic.',flush=True)

    def winding(point):
        vector = triangles - np.asarray([float(value)for value in point])
        a,b,c = vector[:,0],vector[:,1],vector[:,2]
        la,lb,lc = (np.linalg.norm(value,axis=1)for value in (a,b,c))
        numerator = np.einsum('ij,ij->i',a,np.cross(b,c))
        denominator = la*lb*lc + np.einsum('ij,ij->i',a,b)*lc + np.einsum('ij,ij->i',b,c)*la + np.einsum('ij,ij->i',c,a)*lb
        return float((2*np.arctan2(numerator,denominator)).sum()/(4*np.pi))

    cases = []
    for record in records:
        index,sample = record['original_face_index'],record['sample_index']
        weight = WEIGHTS[sample]
        source = exact_triangles[index]
        point = tuple(sum(source[j][axis]*weight[j]for j in range(3))for axis in range(3))
        direction = mul(planes[index][2],F(-1))
        norm_squared = dot(direction,direction)
        # This parameterization is the same original normal line, using the
        # exact unnormalized triangle cross product. Only unit conversion uses
        # high-precision sqrt; all line/triangle predicates are rational.
        with localcontext() as context:
            context.prec = 90
            norm = decimal(norm_squared).sqrt()
            root_numerator=math.isqrt(norm_squared.numerator)
            root_denominator=math.isqrt(norm_squared.denominator)
            exact_norm=(F(root_numerator,root_denominator)
                        if root_numerator**2==norm_squared.numerator and root_denominator**2==norm_squared.denominator
                        else None)
            def distance(parameter):
                return decimal(parameter)*norm+Decimal('0.00001')
            def forward_of_original_origin(parameter):
                # Exact sign test even if the original face normal has an
                # irrational unit length: k*sqrt(norm_squared)+offset >= 0.
                return parameter>=0 or parameter*parameter*norm_squared<=F(1,100000)**2
            hits,backward_hits,coplanar,tangent_points = [],[],[],[]
            checked=nonparallel=parallel=coplanar_planes=0
            # Exhaustive loop: no BVH, float bounds, stored-normal filter, CSV
            # list, or source-specific face list is consulted here.
            for face,triangle in enumerate(exact_triangles):
                checked += 1
                a,b,c = triangle
                edge1,edge2,n = planes[face]
                h = cross(direction,edge2)
                determinant = dot(edge1,h)
                relative = sub(point,a)
                if determinant != 0:
                    nonparallel += 1
                    u = dot(relative,h)/determinant
                    q = cross(relative,edge1)
                    v = dot(direction,q)/determinant
                    parameter = dot(edge2,q)/determinant
                    if u>=0 and v>=0 and u+v<=1:
                        hit = {'parameter':parameter,'face':face,'direction':1 if dot(n,direction)>0 else -1,
                               'barycentric':(1-u-v,u,v)}
                        (hits if forward_of_original_origin(parameter) else backward_hits).append(hit)
                else:
                    parallel += 1
                    if dot(n,relative) != 0:
                        continue
                    coplanar_planes += 1
                    low=high=None
                    possible=True
                    for first,last in ((a,b),(b,c),(c,a)):
                        edge = sub(last,first)
                        intercept = dot(n,cross(edge,sub(point,first)))
                        slope = dot(n,cross(edge,direction))
                        if slope>0:
                            bound=-intercept/slope
                            low=bound if low is None else max(low,bound)
                        elif slope<0:
                            bound=-intercept/slope
                            high=bound if high is None else min(high,bound)
                        elif intercept<0:
                            possible=False
                    if not possible or low is None or high is None or low>high or not forward_of_original_origin(high):
                        continue
                    if low==high:
                        tangent_points.append({'parameter':low,'face':face})
                    else:
                        coplanar.append({'low':low,'high':high,'face':face})
            require(checked==len(triangles) and nonparallel+parallel==checked,'Incomplete original-face enumeration')
            hits.sort(key=lambda hit:(hit['parameter'],hit['face']))
            coplanar.sort(key=lambda interval:(interval['low'],interval['high'],interval['face']))
            # Compare only after the independent all-face computation exists.
            csv_hits=[]
            for token in record['original_cpp_row']['raw_intersections_t_face_direction'].strip(';').split(';'):
                t,face,orientation=token.split(':')
                csv_hits.append({'face':int(face),'t_string':t,'direction':int(orientation)})
            exact_by_face={hit['face']:hit for hit in hits}
            csv_by_face={hit['face']:hit for hit in csv_hits}
            unmatched_csv=sorted(set(csv_by_face)-set(exact_by_face))
            missing_csv=sorted(set(exact_by_face)-set(csv_by_face))
            comparisons=[]
            for face in sorted(set(csv_by_face)&set(exact_by_face)):
                t=distance(exact_by_face[face]['parameter'])
                delta=Decimal(csv_by_face[face]['t_string'])-t
                comparisons.append({'face_index':face,'csv_minus_exact_distance_mm':str(delta),
                                    'crossing_sign_matches':csv_by_face[face]['direction']==exact_by_face[face]['direction']})
            # Build all original-ray intervals from independently recomputed
            # crossings and exact coplanar endpoints. No event is silently
            # erased to force enter/exit alternation.
            parameters={hit['parameter']for hit in hits}
            parameters.update(value for interval in coplanar for value in (interval['low'],interval['high'])if forward_of_original_origin(value))
            parameters.update(item['parameter']for item in tangent_points if forward_of_original_origin(item['parameter']))
            # Begin at the original surface (k=0); the fixed exterior origin to
            # source interval is separately retained as 0..0.00001 mm.
            parameters.add(F(0))
            if exact_norm is not None:
                # Retain the unchanged exterior-origin-to-source interval too.
                parameters.add(-F(1,100000)/exact_norm)
            last=max(parameters,default=F(0))
            # Adding one unnormalized unit is only the diagnostic endpoint,
            # beyond all original intersections, never a replacement ray.
            parameters.add(last+1)
            boundaries=sorted(parameters)
            segments=[]
            for low,high in zip(boundaries,boundaries[1:]):
                middle=(low+high)/2
                midpoint=add(point,mul(direction,middle))
                boundary_faces=[item['face']for item in coplanar if item['low']<middle<item['high']]
                if boundary_faces:
                    state,number='ORIGINAL_SURFACE_BOUNDARY',None
                else:
                    number=winding(midpoint)
                    state='MATERIAL_INTERIOR'if abs(number-1)<1e-7 else 'AIR'if abs(number)<1e-7 else 'UNRESOLVED'
                segments.append({'from_t_mm':float(distance(low)),'to_t_mm':float(distance(high)),
                                 'length_mm':float(decimal(high-low)*norm),'state':state,
                                 'exact_unnormalized_parameters':[exact(low),exact(high)],
                                 'midpoint_mm':[float(value)for value in midpoint],
                                 'boundary_original_face_indices':boundary_faces,
                                 'original_mesh_solid_angle_winding_number':number})
            involved=sorted({index}|set(exact_by_face)|set(csv_by_face)|{item['face']for item in coplanar}|{item['face']for item in tangent_points})
            first_material=next((segment for segment in segments if segment['state']=='MATERIAL_INTERIOR'),None)
            case={**record,
                'all_original_faces_examined':checked,'original_face_count':len(triangles),
                'nonparallel_faces_tested':nonparallel,'parallel_faces_tested':parallel,
                'exact_coplanar_plane_faces_tested':coplanar_planes,
                'source_original_triangle_mm':triangles[index].tolist(),
                'exact_original_sample_point_rationals':[exact(value)for value in point],
                'exact_unnormalized_inward_direction_rationals':[exact(value)for value in direction],
                'exact_direction_squared_norm_rational':exact(norm_squared),
                'direction_norm_decimal_90_digits':str(norm),
                'exact_direction_norm_rational':exact(exact_norm)if exact_norm is not None else None,
                'cpp_reported_point_minus_exact_declared_sample_mm':[
                    float(F(record['original_cpp_row'][key])-point[axis])for axis,key in enumerate(('x','y','z'))],
                'exhaustive_exact_forward_transverse_hits':[
                    {'face_index':hit['face'],'exact_unnormalized_parameter':exact(hit['parameter']),
                     'distance_from_original_outside_origin_mm':str(distance(hit['parameter'])),
                     'crossing_direction_enter_minus_exit_plus':hit['direction'],
                     'exact_hit_barycentric_rationals':[exact(value)for value in hit['barycentric']]}
                    for hit in hits],
                'exact_backward_transverse_hit_count':len(backward_hits),
                'exhaustive_exact_coplanar_original_triangle_intervals':[
                    {'face_index':item['face'],'from_t_mm':str(distance(item['low'])),'to_t_mm':str(distance(item['high'])),
                     'exact_unnormalized_parameters':[exact(item['low']),exact(item['high'])],
                     'saved_outward_normal':stored_normals[item['face']].tolist()}for item in coplanar],
                'exhaustive_exact_coplanar_single_point_touches':[
                    {'face_index':item['face'],'distance_mm':str(distance(item['parameter'])),
                     'exact_unnormalized_parameter':exact(item['parameter'])}for item in tangent_points],
                'comparison_to_original_csv':{'original_csv_hit_count':len(csv_hits),'independent_exact_hit_count':len(hits),
                    'csv_face_ids_missing_from_exact_scan':unmatched_csv,'exact_face_ids_missing_from_csv':missing_csv,
                    'matching_face_distance_residuals':comparisons},
                'original_ray_material_boundary_air_segments':segments,
                'first_material_interior_segment':first_material,
                'first_material_interior_segment_ge_0p8mm':first_material is not None and first_material['length_mm']>=.8,
                'all_involved_original_faces':[{'face_index':face,'vertices_mm':triangles[face].tolist(),
                    'saved_outward_normal':stored_normals[face].tolist()}for face in involved],
                'interpretation':'Diagnosis only. Exhaustive independent intersections and explicit boundary intervals do not clear the original strict flag.'}
            cases.append(case)
            print(f"Face {index}/sample {sample}: all {checked} faces tested; independent hits {len(hits)}; coplanar intervals {len(coplanar)}; CSV unmatched {unmatched_csv}; CSV missing {missing_csv}.",flush=True)
    report={'stl_sha256':stl_hash,'diagnostic_only':True,'original_strict_passed':False,
            'production_acceptance_unchanged':True,'exhaustive_original_triangle_scan':True,
            'original_face_count':len(triangles),'flagged_original_rays':len(records),'cases':cases,
            'method':'For each declared original sample ray, every raw triangle is independently enumerated and tested using Fraction arithmetic on original float32 coordinates. All transverse plane intersections, exact barycentric membership, parallel-plane coplanarity and coplanar half-plane intervals are recomputed without BVH, floating-point candidate filters or CSV hit-list dependence. Forward-of-origin classification uses an exact squared rational comparison, even for irrational unit normals; coplanar single-point touches are retained as interval breakpoints. The exact original geometric normal is represented by its unnormalized cross product; physical distances use a 90-digit sqrt and the unchanged 0.00001 mm origin offset. CSV comparison happens only after exhaustive recomputation. Material/air interval midpoint winding uses every unchanged original triangle; surface boundaries stay explicit.',
            'coordinate_representation_note':'Exact arithmetic reconstructs the declared original barycentric sample. The unchanged C++ rows and tiny long-double/decimal representation residuals are retained. No alternate sampled ray, normal, production tolerance, threshold or acceptance flag is introduced.',
            'limits':'Authored diagnostic, not independent acceptance. Midpoint winding is a numerical cross-check rather than a global exact solid-occupancy proof. No local or global thickness waiver is applied.'}
    report['checker_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report['flags_sha256']=hashlib.sha256((ROOT/'qa/dense/dense-flagged-samples.json.gz').read_bytes()).hexdigest()
    checks={'all_four_original_flags_diagnosed':len(cases)==len(records)==4,
            'every_original_face_tested':all(c['all_original_faces_examined']==len(triangles) for c in cases),
            'no_missing_or_extra_transverse_hits':all(not c['comparison_to_original_csv']['csv_face_ids_missing_from_exact_scan'] and not c['comparison_to_original_csv']['exact_face_ids_missing_from_csv'] for c in cases),
            'all_transverse_signs_match':all(all(q['crossing_sign_matches'] for q in c['comparison_to_original_csv']['matching_face_distance_residuals']) for c in cases),
            'all_first_material_segments_ge_0p8':all(c['first_material_interior_segment_ge_0p8mm'] for c in cases),
            'all_flags_have_explicit_coplanar_intervals':all(c['exhaustive_exact_coplanar_original_triangle_intervals'] for c in cases),
            'original_stl_unchanged':hashlib.sha256((ROOT/'model.stl').read_bytes()).hexdigest()==stl_hash}
    report['diagnostic_checks']=checks;report['diagnostic_passed']=all(checks.values())
    write_json(ROOT/'qa/boundaries/ray-boundary-evidence.json',report)
    require(report['diagnostic_passed'],'Original-boundary diagnosis failed')


if __name__=='__main__':
    main()
