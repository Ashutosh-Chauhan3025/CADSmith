import cadquery as cq

# Define dimensions
plate_length = 80.0
plate_width = 60.0
plate_thickness = 4.0
hole_pattern_x = 70.0
hole_pattern_y = 50.0
hole_diameter = 3.0  # M3 hole diameter
hole_clearance_diameter = 3.5  # Clearance hole diameter for M3 fasteners

# Create the main plate
result = (
    cq.Workplane("XY")
    .box(plate_length, plate_width, plate_thickness, centered=(True, True, False))
)

# Calculate hole positions: 2x2 grid centered in 70x50mm pattern, 25mm spacing
# Center of pattern is at (35, 25) from the bottom-left of the pattern
# Offset from plate center: plate center is (40, 30), pattern center is (35, 25)
# So hole positions are: (35-25, 25-25), (35+25, 25-25), (35-25, 25+25), (35+25, 25+25)
# But relative to plate center: (40-35, 30-25) = (5, 5) offset
# So actual positions: (40-25, 30-25), (40+25, 30-25), (40-25, 30+25), (40+25, 30+25)
hole_positions = [
    (40 - 25, 30 - 25),
    (40 + 25, 30 - 25),
    (40 - 25, 30 + 25),
    (40 + 25, 30 + 25)
]

# Create holes using pushPoints for accurate placement
result = result.faces(">Z").workplane().pushPoints(hole_positions).hole(hole_clearance_diameter)