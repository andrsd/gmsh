# ------------------------------------------------------------------------------
#
#  Gmsh Python tutorial 20
#
#  STEP import and manipulation, geometry partitioning
#
# ------------------------------------------------------------------------------

# The OpenCASCADE geometry kernel allows to import STEP files and to modify
# them. In this tutorial we will load a STEP geometry and partition it into
# slices.

import gmsh
import math
import os

gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)

gmsh.model.add("t20")

# Load a STEP file (using `importShapes' instead of `merge' allows to directly
# retrieve the tags of the highest dimensional imported entities):
path = os.path.dirname(os.path.abspath(__file__))
v = gmsh.model.occ.importShapes(os.path.join(path, '..', 't20_data.step'))

# If we had specified
#
# gmsh.option.setString('OCCTargetUnit', 'M')
#
# before merging the STEP file, OpenCASCADE would have converted the units to
# meters (instead of the default, which is millimeters).

# Get the bounding box of the volume:
gmsh.model.occ.synchronize()
xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(v[0][0], v[0][1])

# Note that the synchronization step can be avoided in Gmsh >= 4.6 by using
# `gmsh.model.occ.getBoundingBox()' instead of `gmsh.model.getBoundingBox()'.

# We want to slice the model into N slices, and either keep the volume slices
# or just the surfaces obtained by the cutting:

N = 5 # Number of slices
surf = False # Keep only surfaces?

dz = (zmax - zmin) / N;

# Define the cutting planes
for i in range(1, N):
    gmsh.model.occ.addRectangle(xmin, ymin, zmin + i * dz,
                                xmax-xmin, ymax-ymin,
                                1000 + i)

# Fragment (i.e. intersect) the volume with all the cutting planes:
gmsh.model.occ.fragment(v, [(2, i) for i in range(1000+1, 1000+N)])

# Now remove all the surfaces (and their bounding entities) that are not on the
# boundary of a volume, i.e. the parts of the cutting planes that "stick out" of
# the volume:

gmsh.model.occ.synchronize()
gmsh.model.occ.remove(gmsh.model.getEntities(2), True)

# The previous synchronization step can be avoided in Gmsh >= 4.6 by using
# `gmsh.model.occ.getEntities()' instead of `gmsh.model.getEntities()'.

gmsh.model.occ.synchronize()

if surf:
    # If we want to only keep the surfaces, retrieve the surfaces in bounding
    # boxes around the cutting planes...
    eps = 1e-4
    s = []
    for i in range(1, N):
        s.extend(gmsh.model.getEntitiesInBoundingBox(
            xmin-eps,ymin-eps,zmin + i * dz - eps,
            xmax+eps,ymax+eps,zmin + i * dz + eps, 2))
    # ...and remove all the other entities (here directly in the model, as we
    # won't modify any OpenCASCADE entities later on):
    dels = gmsh.model.getEntities(2)
    for e in s:
        dels.remove(e)
    gmsh.model.removeEntities(gmsh.model.getEntities(3))
    gmsh.model.removeEntities(dels)
    gmsh.model.removeEntities(gmsh.model.getEntities(1))
    gmsh.model.removeEntities(gmsh.model.getEntities(0))

# Finally, let's specify a global mesh size and mesh the partitioned model:
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 3)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 3)
gmsh.model.mesh.generate(3)
gmsh.write("t20.msh")

# Show the result:
# gmsh.fltk.run()

gmsh.finalize()
