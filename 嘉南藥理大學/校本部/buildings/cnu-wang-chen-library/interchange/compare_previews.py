#!/usr/bin/env python3
"""Measure the two render_comparison.py pairs; not a color-calibration test."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--images',type=Path,required=True);p.add_argument('--report',type=Path,required=True)
a=p.parse_args();result={}
for view in ('front','rear'):
    original=Image.open(a.images/('original-'+view+'.png')).convert('RGB')
    imported=Image.open(a.images/('3mf-'+view+'.png')).convert('RGB')
    if original.size!=imported.size:raise ValueError('Image dimensions differ')
    difference=ImageChops.difference(original,imported);stats=ImageStat.Stat(difference)
    result[view]={'resolution':list(original.size),'mean_absolute_srgb8_channel_difference':stats.mean,
                  'maximum_absolute_srgb8_channel_difference':[hi for lo,hi in difference.getextrema()],
                  'identical_pixel_count':sum(p==(0,0,0) for p in difference.get_flattened_data()),
                  'total_pixels':original.width*original.height}
a.report.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
