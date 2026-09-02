import cadquery as cq

diameter = 50
thickness = 2

result = (
    cq.Workplane("XY")
    .circle(diameter / 2)
    .extrude(thickness)
)