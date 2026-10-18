"""Quantify original unit value exactly; original failed 1e-12 gate retained."""
from fractions import Fraction as F
import hashlib,json
from pathlib import Path
import struct

root=Path(__file__).resolve().parent
raw=(root/'scene-unit-diagnosis.json').read_bytes();r=json.loads(raw)
actual=r['actual_scale_length'];bits=struct.unpack('<I',struct.pack('<f',actual))[0]
expected=struct.unpack('<f',struct.pack('<f',.001))[0]
next_up=struct.unpack('<f',struct.pack('<I',bits+1))[0]
ulp=F(next_up)-F(actual)
out={'scope':'Exact arithmetic on the recorded original Blender unit FloatProperty; no scene, STL or QA gate change.',
    'original_scene_sha256':r['scene_sha256'],'raw_diagnosis_sha256':hashlib.sha256(raw).hexdigest(),
    'system':r['system'],'length_unit':r['length_unit'],
    'actual_scale_length':actual,'actual_scale_length_exact':str(F(actual)),
    'binary32_bits_hex':hex(bits),'binary32_of_source_0p001':expected,
    'actual_equal_to_binary32_source_literal':actual==expected,
    'binary32_ULP_at_actual_value_exact':str(ulp),'binary32_ULP_at_actual_value':float(ulp),
    'stored_value_distance_from_expected_binary32_in_ULPs':0 if actual==expected else None,
    'actual_minus_python_literal_exact':str(F(actual)-F(.001)),
    'actual_minus_python_literal_in_ULPs_exact':str((F(actual)-F(.001))/ulp),
    'actual_minus_mathematical_1_over_1000_exact':str(F(actual)-F(1,1000)),
    'actual_minus_mathematical_1_over_1000_in_ULPs_exact':str((F(actual)-F(1,1000))/ulp),
    'strict_reproducibility_unit_comparison_threshold_unchanged':1e-12,
    'strict_reproducibility_unit_comparison_pass':abs(actual-.001)<1e-12,
    'strict_false_flag_and_exit_status_are_retained':True,
    'interpretation':'The original strict 1e-12 comparison remains false. The saved value is exactly the binary32 representation of source 0.001, with 0 ULP mismatch to that representation. This is traceable evidence for treating the unit-representation flag as nonblocking; it does not convert the failed gate into a pass.'}
(root/'scene-unit-quantization.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print(json.dumps(out,indent=2))
