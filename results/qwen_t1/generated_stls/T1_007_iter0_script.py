import cadquery as cq

result = cq.Workplane("XY").polygon(6, 20).extrude(35)