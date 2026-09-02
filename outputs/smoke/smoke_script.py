import cadquery as cq
result = cq.Workplane("XY").box(20,20,20).faces(">Z").workplane().hole(5)
