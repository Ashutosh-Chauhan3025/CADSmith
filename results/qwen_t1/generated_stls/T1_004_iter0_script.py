import cadquery as cq

base_diameter = 30.0
height = 45.0

result = cq.Solid.makeCone(radius1=base_diameter / 2, radius2=0, height=height, pnt=(0,0,0), dir=(0,0,1))