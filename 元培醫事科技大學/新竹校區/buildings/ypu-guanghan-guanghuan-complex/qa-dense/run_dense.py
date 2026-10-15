from pathlib import Path
import numpy as np,subprocess,hashlib,json
R=Path(__file__).resolve().parent
raw=(R.parent/'model.stl').read_bytes()
assert hashlib.sha256(raw).hexdigest()==json.loads((R/'input.json').read_text())['sha256']
a=np.frombuffer(raw,offset=84,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])['v'].astype('<f8')
a.tofile(R/'triangles.bin')
subprocess.run(['g++','-O3','-std=c++17',str(R/'dense-ray.cpp'),'-o',str(R/'dense-ray')],check=True)
subprocess.run([str(R/'dense-ray'),str(R/'triangles.bin'),str(R/'all-original.csv')],check=True)
