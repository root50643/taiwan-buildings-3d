"""原創參數曲面：2019–2022 主顧聖母堂外觀近似；輸出毫米。
公開平面描點 + 縱剖面比例，非實測／非原廠曲面。不得當施工圖。
"""
from pathlib import Path
import json, math
import numpy as np
import trimesh
from scipy.interpolate import PchipInterpolator
from manifold3d import Manifold, Mesh, CrossSection
OUT=Path(__file__).resolve().parent
S=3.5; BASE=2.4; FLOOR=BASE+3.0*S
# p62/page-4.jpg 1132x1600；順序為後端尖角→右側→前端→左側。
TRACE=[[402,790],[480,860],[548,930],[574,980],[574,1040],[561,1100],[540,1170],[516,1240],[490,1304],[315,1304],[290,1240],[267,1170],[244,1100],[229,1040],[224,980],[250,930],[325,860]]
# 607m² only used as a coarse scale anchor for the traced envelope. We choose
# 35m length, independently retain the traced aspect; area is reported, not forced.
K=35/514
py=np.array([790,860,930,980,1040,1100,1170,1240,1304]);
left=PchipInterpolator(py,[402,325,250,224,229,244,267,290,315]);right=PchipInterpolator(py,[402,480,548,574,574,561,540,516,490])
# p65 longitudinal silhouette, front x285 / rear990 / nave floor1394.
SECTION=[[285,1255],[385,1217],[486,1186],[553,1168],[618,1156],[681,1148],[718,1070],[752,1096],[832,1170],[894,1250],[950,1320],[989,1388]]
# Ridge offsets from floor; rear pair higher than front pair. Raised crossing
# represents the observed non-coplanar roof junction, not four symmetric lobes.
ridge=PchipInterpolator([0,.055,.13,.22,.31,.37,.415,.55,.72,1],[.45,3.5,7.8,12.2,15.3,14.2,11.6,10.9,9.5,6.45])
parts=[];cuts=[]
def box(x1,x2,y1,y2,z1,z2):return Manifold.cube((x2-x1,y2-y1,z2-z1)).translate((x1,y1,z1))
def worldbox(x1,x2,y1,y2,z1,z2):return box(x1*S,x2*S,y1*S,y2*S,FLOOR+z1*S,FLOOR+z2*S)
def prism(poly,z1,z2):return CrossSection([np.array(poly)]).extrude(z2-z1).translate((0,0,z1))
def xy(p):return ((p[0]-400)*K*S,(p[1]-1047)*K*S)
# 150 mm rectangular display plinth; terrace follows the chapel outline.
parts.append(box(-57,57,-75,75,0,BASE))
outline=np.array([xy(p) for p in TRACE]); terrace=outline*np.array([1.12,1.075])
parts.append(prism(terrace,BASE-.1,FLOOR-.6))
parts.append(prism(terrace*1.025,FLOOR-.9,FLOOR+.2))
# Landscape section: front/rear paths are near nave level; east flank drops.
# This is a schematic supporting terrain, explicitly not a measured topography.
gv=[];gf=[];gx=np.linspace(-57,57,19);gy=np.linspace(-75,75,41)
for y in gy:
 for x in gx:
  q=np.clip((x-12)/45,0,1);q=q*q*(3-2*q)
  depression=q*max(0,math.cos(math.pi*y/150))**1.4
  h=BASE+(FLOOR-.70-BASE)*(1-depression)
  gv.append([x,y,h])
for j in range(len(gy)-1):
 for i in range(len(gx)-1):
  a=j*len(gx)+i;b=a+1;c=a+len(gx);d=c+1;gf.extend([[a,b,d],[a,d,c]])
gb=list(range(len(gx)))+[j*len(gx)+len(gx)-1 for j in range(1,len(gy))]+list(range((len(gy)-1)*len(gx)+len(gx)-2,(len(gy)-1)*len(gx)-1,-1))+[j*len(gx) for j in range(len(gy)-2,0,-1)]
gl=[]
for i in gb:gl.append(len(gv));gv.append([gv[i][0],gv[i][1],.5])
gc=len(gv);gv.append([0,0,.5])
for k,a in enumerate(gb):
 b=gb[(k+1)%len(gb)];la=gl[k];lb=gl[(k+1)%len(gl)];gf.extend([[a,la,lb],[a,lb,b],[gc,lb,la]])
ground=Manifold(Mesh(np.asarray(gv,dtype=np.float32),np.asarray(gf,dtype=np.uint32)))
# Watertight structured surface and flat bottom. Grid avoids the exact zero-
# width rear vertex; end is a small 0.24m truncated point rooted into terrace.
ny=141;nx=81;ys=np.linspace(792,1304,ny);us=np.linspace(-1,1,nx);v=[]
for p in ys:
 t=(p-790)/514; xl=float(left(p));xr=float(right(p));mid=(xl+xr)/2;half=(xr-xl)/2
 for u in us:
  x=mid+u*half
  # side wall curves, not an ellipsoid: longitudinal asymmetry from section.
  z=.35+(float(ridge(t))-.35)*max(0,1-abs(u)**1.78)**.60
  # Four leaf separation; printable shallow recessed solid glazing bands.
  longband=math.exp(-((u*half*K)/.72)**8)
  crossband=math.exp(-((t-.365)/.042)**8)
  z-=.55*max(longband,crossband)*min(1,z/.8)*min(1,max(0,(14.3-z)/1.2))
  # Front terminates in the photographed flattened upper beam, not a round arch.
  if t>.90:z=min(z,6.0+(1-t)*30)
  # left/right slight independent curvature is inferred, not measured.
  z+=.10*math.sin(math.pi*t)*u*(1-u*u)
  v.append([*xy([x,p]),FLOOR+z*S])
f=[]
for j in range(ny-1):
 for i in range(nx-1):
  a=j*nx+i;b=a+1;c=a+nx;d=c+1;f.extend([[a,b,d],[a,d,c]])
# perimeter CCW as seen from above; top grid has positive normals.
boundary=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range((ny-1)*nx+nx-2,(ny-1)*nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
low=[]
for i in boundary:low.append(len(v));v.append([v[i][0],v[i][1],FLOOR-.15])
center=len(v);v.append([0,0,FLOOR-.15])
for k,a in enumerate(boundary):
 b=boundary[(k+1)%len(boundary)];la=low[k];lb=low[(k+1)%len(low)]
 f.extend([[a,la,lb],[a,lb,b],[center,lb,la]])
m=Manifold(Mesh(np.asarray(v,dtype=np.float32),np.asarray(f,dtype=np.uint32)));assert str(m.status()).endswith('NoError'),m.status();parts.append(m)
# Cross rooted in high rear crown. Minimum printed bar width 1.3mm.
ycross=(.31*514+790-1047)*K
parts.append(worldbox(-.20,.20,ycross-.22,ycross+.22,14.6,17.8))
parts.append(worldbox(-1.1,1.1,ycross-.22,ycross+.22,16.65,17.05))
# Front recessed glazed wall / robust two-level portal.
yfront=(1304-1047)*K
frontglass=[(-5.3,.35),(-5.1,1.8),(-4.4,3.3),(-3.2,4.9),(-2.3,5.7),(2.3,5.7),(3.2,4.9),(4.4,3.3),(5.1,1.8),(5.3,.35)]
cuts.append(CrossSection([np.asarray(frontglass[::-1])*S]).extrude(.60*S).rotate((90,0,0)).translate((0,(yfront+.05)*S,FLOOR)))
# Frame is added after the glazing cut: all bars retain a full-depth backing.
frontframes=[]
for xa,xb,za,zb in [(-3.05,-2.7,.20,5.15),(2.7,3.05,.20,5.15),(-5.25,5.25,2.6,2.95),(-2.9,2.9,4.9,5.25),(-1.22,-.9,.20,3.45),(.9,1.22,.20,3.45),(-1.22,1.22,3.15,3.5),(-.2,.2,3.1,5.1),(-1.55,-1.23,3.1,5.1),(1.23,1.55,3.1,5.1)]:
 frontframes.append(worldbox(xa,xb,yfront-.72,yfront+.015,za,zb))
# Transverse side doors below roof junction; backed relief (not thin frames).
for sign in [-1,1]:
 xa,xb=(-13.35,-10.7) if sign<0 else (10.7,13.35)
 parts.append(worldbox(xa,xb,-6.05,-3.05,-.12,3.15))
 cuts.append(worldbox(-13.6,-12.6,-5.4,-3.7,.15,2.65) if sign<0 else worldbox(12.6,13.6,-5.4,-3.7,.15,2.65))
# Lower side-window rhythm follows visible bays, deliberately simplified.
for p in [1028,1084,1138,1190]:
 yc=(p-1047)*K
 for sign in [-1,1]:
  xx=(float(left(p) if sign<0 else right(p))-400)*K
  cuts.append(worldbox(xx-.6,xx+.6,yc-.9,yc+.9,.45,1.45))
# The entry and rear grade meet the nave. No invented front basement windows.
# Only the eastern downhill flank receives exterior-reaching backed recesses.
for ya,yb in [(-10,-8),(-2.7,-1.1),(10,12)]:
 cuts.append(worldbox(10.8,16.5,ya,yb,-2.4,-.8))
# External east stair flights from terrace to display ground, rooted each step.
for yc in [0.0,6.0]:
 for i in range(9):
  ztop=FLOOR-(i+1)*(3*S/9)
  parts.append(box(42+i*.65,47+i*.65,(yc-2)*S,(yc+2)*S,BASE-.05,max(BASE+.15,ztop)))
# Main front shallow steps.
for i in range(3):parts.append(box(-10,10,64+i*1.6,66+i*1.6,BASE-.05,FLOOR-.3-i*.5))
solid=Manifold.batch_boolean(parts, __import__('manifold3d').OpType.Add)
solid=solid-Manifold.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
solid=solid+Manifold.batch_boolean(frontframes,__import__('manifold3d').OpType.Add)+ground
assert str(solid.status()).endswith('NoError'),solid.status()
mesh=solid.to_mesh();tm=trimesh.Trimesh(np.asarray(mesh.vert_properties)[:,:3],np.asarray(mesh.tri_verts),process=False)
assert tm.is_watertight and tm.is_winding_consistent and tm.volume>0
# Deterministic STL normals calculated directly by exporter; no repair.
(OUT/'model.stl').write_bytes(trimesh.exchange.stl.export_stl(tm))
from shapely.geometry import Polygon
report={'unit':'mm','scale_mm_per_m':S,'version':'2019–2022 exterior approximation','plan_source':'page-4.jpg / p62 / 1132x1600','outline_pixels':TRACE,'section_source':'page-7.jpg / p65 / 1132x1600','section_pixels':SECTION,'traced_envelope_area_m2':Polygon(TRACE).area*K*K,'traced_length_m':35,'published_building_area_m2':607,'area_definition_warning':'來源607㎡可能依外牆投影計算；描點屋殼外緣與其不必相同。面積只作量級交叉檢核，未強制調到607。','published_height_m':18.5,'shell_above_nave_floor_m':15.3,'nave_floor_above_display_grade_m':3,'cross_top_above_nave_floor_m':17.8,'height_warning':'來源18.5m的起算點／是否含十字架不明；三項高度分別列示，未聲稱精確吻合。','dimensions_mm':tm.extents.tolist(),'triangles':len(tm.faces)}
(OUT/'parameters.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
