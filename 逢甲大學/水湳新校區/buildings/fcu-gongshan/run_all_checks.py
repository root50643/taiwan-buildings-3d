"""Fail-closed checks. The detailed-loss check intentionally remains nonzero until specific review."""
from pathlib import Path
import subprocess,sys
R=Path(__file__).parent
for script in ['check_raw_mesh.py','validate_model.py','check_render_rebuild.py','check_thin_features.py','check_layer_components.py','check_all_layers.py','check_feature_rays.py','check_ribbon_rays.py','check_tip_dense_rays.py','check_tip_layer_support.py','check_original_sections.py','check_white_roi_rays.py','check_component_detail.py']:
 print('RUN',script,flush=True)
 subprocess.run([sys.executable,str(R/script)],cwd=R,check=True)
