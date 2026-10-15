from pathlib import Path
import os
HERE = Path(__file__).resolve().parent
W = Path(os.environ['NTOU_BOUNDARY_WORKDIR'])
O = HERE
S = Path(os.environ.get('NTOU_MODEL_DIR', str(Path(__file__).resolve().parents[2]))) / 'model.stl'
H = '752b4c147bd18874b1c49890596c260e58015520f71f60cebc6ee6144700ef49'
