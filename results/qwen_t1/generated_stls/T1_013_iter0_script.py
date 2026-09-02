import cadquery as cq

result = cq.Workplane("XY").box(60, 20, 8, centered=(True, True, True))