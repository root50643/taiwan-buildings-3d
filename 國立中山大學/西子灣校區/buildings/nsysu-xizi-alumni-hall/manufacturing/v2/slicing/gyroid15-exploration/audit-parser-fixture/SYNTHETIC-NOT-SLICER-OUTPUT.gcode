; GEOMETRY REVIEW EVIDENCE ONLY - NOT MACHINE READY. Reslice with the actual printer and material profile.
G90
M82
G92 E0
;LAYER_CHANGE
;Z:0.2
G1 Z0.2
;TYPE:External perimeter
G1 X10 Y0 E1
;TYPE:Support material
G1 X10 Y10 E2
M83
;TYPE:Support material interface
G1 X0 Y10 E1
;TYPE:Bridge infill
G1 X0 Y0 E1
;LAYER_CHANGE
;Z:0.4
G1 Z0.4
M82
G92 E0
;TYPE:Perimeter
G1 X10 Y0 E1
