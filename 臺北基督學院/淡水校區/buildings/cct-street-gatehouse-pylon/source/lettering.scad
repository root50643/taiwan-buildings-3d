// Text geometry generated from installed Noto Sans CJK TC Bold; font file not bundled.
// Six visible school-name characters. Badge internals / tiny English wall inscription omitted.
$fn = 18;
chars = ["臺", "北", "基", "督", "學", "院"];
for (i = [0:5])
  translate([72.25, 0.10, 51.2 - i*5.4])
    rotate([90,0,0])
      linear_extrude(height=0.45)
        text(chars[i], size=2.9, font="Noto Sans CJK TC:style=Bold", halign="center", valign="center", spacing=1);
