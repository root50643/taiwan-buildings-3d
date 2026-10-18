"""Record original Blender unit FloatProperty value; never alters the scene."""
from fractions import Fraction as F
import hashlib,json
from pathlib import Path
import struct
import bpy

root=Path(__file__).resolve().parents[1]
blend=root/'models/v4/scene.blend'
bpy.ops.wm.open_mainfile(filepath=str(blend),load_ui=False)
u=bpy.context.scene.unit_settings;actual=float(u.scale_length)
expected_f32=struct.unpack('<f',struct.pack('<f',.001))[0]
r={'scope':'Read-only diagnostic of original saved scene units; no scene or model mutation.',
    'scene_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
    'system':u.system,'length_unit':u.length_unit,
    'actual_scale_length':actual,'actual_scale_length_hex':actual.hex(),'actual_scale_length_exact':str(F(actual)),
    'intended_source_literal':.001,'intended_source_literal_exact':str(F(.001)),
    'actual_minus_python_source_literal':actual-.001,
    'actual_minus_source_literal_exact':str(F(actual)-F(.001)),
    'binary32_of_intended_literal':expected_f32,
    'actual_exactly_equals_binary32_of_intended_literal':actual==expected_f32,
    'first_repro_check_abs_difference_lt_1e_12':abs(actual-.001)<1e-12,
    'interpretation':'Blender stores scale_length as a binary32 FloatProperty. Comparing its value to the exact expected binary32 of the source literal is appropriate; a 1e-12 tolerance against the Python binary64 literal produces a false verification failure. Original failed report is preserved; geometry checker thresholds are unchanged.'}
(root/'qa/scene-unit-diagnosis.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps(r,indent=2))
