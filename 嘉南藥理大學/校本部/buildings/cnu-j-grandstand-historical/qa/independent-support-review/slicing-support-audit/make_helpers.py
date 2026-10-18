from pathlib import Path
import ast,hashlib
p=Path('${EARLIER_INDEPENDENT_AUDIT_PY}')
s=p.read_text();t=ast.parse(s);names={'sha','parse_gcode','intersect_linear','capsule_intervals','coverage'}
out='from pathlib import Path\nfrom collections import Counter, defaultdict\nimport math,re,hashlib\nWORDS = re.compile(r"([A-Za-z])\\s*([-+]?(?:\\d+(?:\\.\\d*)?|\\.\\d+))")\n\n'
out+='\n\n'.join(ast.get_source_segment(s,n) for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names)
r=Path(__file__).resolve().parent
(r/'modal_capsule_helpers.py').write_text(out+'\n',encoding='utf8')
print(hashlib.sha256(p.read_bytes()).hexdigest())
