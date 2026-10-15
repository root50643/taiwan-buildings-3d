"""Public package references, paired actual previews and strict disclosures."""
from pathlib import Path
import re,json
R=Path(__file__).resolve().parent;school=R.parents[2];camp=R.parents[1];reads=[R/'README.md',camp/'README.md',school/'README.md'];links=[]
for p in reads+[R/'QA.md',R/'sources.md']:
 text=p.read_text()
 for link in re.findall(r'\]\(([^)]+)\)',text):
  if not link.startswith(('http','https','#')):
   assert (p.parent/link).exists(),(p.name,link);links.append(link)
for p in reads:
 text=p.read_text();assert 'front.png' in text and 'rear.png'in text
 assert any('front.png'in line and 'rear.png'in line for line in text.splitlines()),p
for p in list(R.glob('*.json'))+list(R.glob('*.md'))+list(R.glob('*.py')):
 text=p.read_text();assert ('/'+'workspace'+'/')not in text and ('/'+'tmp'+'/')not in text,p.name
q=(R/'QA.md').read_text();assert '260' in q and '1128' in q and '172'in q and 'false'in q and '試印'in q and '0.003609' in q
checks={'all_local_links_resolve':True,'three_readmes_same_model_front_rear_same_row':True,'no_private_absolute_paths_in_public_text':True,'strict_failures_and_print_limits_disclosed':True}
(R/'documentation-check.json').write_text(json.dumps({'checks':checks,'passed':True,'verified_local_link_count':len(links)},indent=2));print(checks)
