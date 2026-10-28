import bpy,json,pathlib
r=pathlib.Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
font=bpy.data.fonts.load('/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc')
parts=[]
for i,ch in enumerate('國立高雄大學'):
 c=bpy.data.curves.new('sign','FONT');c.body=ch;c.font=font;c.size=1.3;c.extrude=.045;c.resolution_u=3
 o=bpy.data.objects.new(ch,c);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object
 # triangulate then local x => world x, y => z, depth => negative y
 bpy.ops.object.modifier_add(type='TRIANGULATE');bpy.ops.object.modifier_apply(modifier=o.modifiers[-1].name)
 v=[[float(q.co.x)+1.25+i*1.28,-float(q.co.z)-.025,float(q.co.y)+8.2]for q in o.data.vertices];f=[list(q.vertices)for q in o.data.polygons]
 parts.append({'name':ch,'vertices':v,'faces':f});o.select_set(False)
(r/'signage-geometry.json').write_text(json.dumps(parts));print('SIGNS',len(parts))
