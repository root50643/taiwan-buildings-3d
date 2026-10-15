"""Fixed source-bounded roots. Never search for the longest direction."""

import sys
sys.dont_write_bytecode=True
import numpy as np
def classify(p,n):
 x,y,z=p;axis=int(np.argmax(np.abs(n)))
 # Bounds are construction-source families, in exported +X east,+Y north,+Z up.
 # Anchor planes are fixed strictly behind the deepest recess, never chosen by
 # testing a set of rays and taking the longest.
 if 9.38<=x<=10.2 and -60.01<=y<=-39.99 and 4.19<=z<=19.61 and axis==1:
  return 'west_hall_door_pane_overlap_relief',np.array([1.,0,0]),11.2,0
 if 69.8<=x<=70.62 and -40.01<=y<=-19.99 and 4.19<=z<=19.61 and axis==1:
  return 'east_hall_door_pane_overlap_relief',np.array([-1.,0,0]),68.8,0
 if -10.2<=y<=-9.38 and 19.99<=x<=40.01 and 4.19<=z<=19.61 and axis==0:
  return 'north_hall_door_pane_overlap_relief',np.array([0.,-1,0]),-11.2,1
 if 20.919<=x<=21.851 and -109.501<=y<=-99.999 and 4.69<=z<=15.36 and axis==2:
  return 'west_service_stacked_louver_relief',np.array([1.,0,0]),23.2,0
 if 23.499<=x<=29.001 and -126.251<=y<=-125.399 and 5.09<=z<=10.61 and axis==2:
  return 'south_equipment_bay_louver_relief',np.array([0.,1,0]),-124.,1
 if 34.199<=x<=37.801 and 24.49<=z<=31.101 and axis==2:
  if -60.351<=y<=-59.999: return 'north_roof_unit_louver_and_cap_relief',np.array([0.,-1,0]),-61.25,1
  if -70.001<=y<=-69.649: return 'south_roof_unit_louver_and_cap_relief',np.array([0.,1,0]),-68.75,1
 if 79.499<=x<=80.001 and -132.001<=y<=-131.199 and 8.84<=z<=15.11 and axis==0:
  return 'southeast_window_end_land',np.array([0.,1,0]),-124.,1
 return None

