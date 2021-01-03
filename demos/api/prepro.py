import gmsh
import math
import sys

# This example shows how to implement a simple interactive pre-processor for a
# finite element solver; in particular, it shows how boundary conditions,
# material properties, etc., can be specified on parts of the model.

gmsh.initialize(sys.argv)
if len(sys.argv) > 1:
    gmsh.open(sys.argv[1])

# For Gmsh to know which types of boundary conditions, materials, etc., are
# available, one should define "template" ONELAB parameters with names
# containing the following substrings:
#
# - "ONELAB Context/Point Template/"
# - "ONELAB Context/Curve Template/"
# - "ONELAB Context/Surface Template/"
# - "ONELAB Context/Volume Template/"
#
# Double- (or right-) clicking on an entity in the GUI will then pop-up a
# context window where instances of these variables for the given entity can be
# edited. For example, if the "ONELAB Context/Curve Template/0Boundary
# condition" exists, double-clicking on curve 123 in the model will create
# "ONELAB Context/Curve 123/0Boundary condition" (or "ONELAB Context/Physical
# Curve 1000/0Boundary condition" depending on the choice in the context window,
# if curve 123 belongs to the physical curve 1000). The context window is also
# shown automatically when a new physical group is created in the GUI.
#
# Every time the ONELAB database is changed, the "ONELAB/Action" parameter is
# set to "check", which gives the Python code the opportunity to react in the
# event loop. This could e.g. be used to define new variables depending on the
# choices just made, or to show/hide existing variables. To make things simpler,
# several special attributes can be specified ("ServerActionSet",
# "ServerActionShow", "ServerActionShowMatch", "ServerActionHide", ...) when
# creating parameters, which allows to set the visibility or the value of
# dependent parameters without explicitly processing the "check" action.
#
# Other actions can be defined as well:
#
# * The "ONELAB/Button" parameter governs the behavior of the main "Run" button
#   in the GUI; in this example the "run" action could trigger running the
#   finite element solver with the defined parameters
#
# * Parameters with the "Macro" attribute set to "Action" will trigger an action
#   named after their value; in this example we use a macro to create a "select
#   entity" action where the user is asked to interactively select an entity in
#   the model.
#
# See https://gitlab.onelab.info/doc/tutorials/-/wikis/ONELAB-JSON-interface for
# more information about the ONELAB JSON database interface.

parameters = """
[
  {
    "type":"number",
    "name":"ONELAB Context/Curve Template/0Boundary condition",
    "values":[0],
    "choices":[0, 1],
    "valueLabels":{"Temperature [℃]":0, "Flux [Wm⁻²]":1}
  },
  {
    "type":"number",
    "name":"ONELAB Context/Curve Template/1Value",
    "values":[20],
    "min":0,
    "max":100,
    "step":0.1
  },
  {
    "type":"number",
    "name":"ONELAB Context/Surface Template/0Material",
    "values":[1],
    "choices":[0, 1, 2],
    "valueLabels":{"User-defined":0, "Steel":1, "Concrete":2},
    "attributes":
      {
        "ServerActionHideMatch":"ONELAB Context/Surface Template/1.*",
        "ServerActionShowMatch 0":"ONELAB Context/Surface Template/1.*",
        "ServerActionSet 1":"%10Cond, 205, %11Diff, 97",
        "ServerActionSet 2":"%10Cond, 37, %11Diff, 12"
      }
  },
  {
    "type":"number",
    "name":"ONELAB Context/Surface Template/10Cond",
    "label":"Conductivity [Wm⁻¹K⁻¹]",
    "values":[205],
    "min":0.1,
    "max":500,
    "step":0.1,
    "visible":false
  },
  {
    "type":"number",
    "name":"ONELAB Context/Surface Template/11Diff",
    "label":"Diffusivity [mm²s⁻¹]",
    "values":[97],
    "min":10,
    "max":1200,
    "step":0.1,
    "visible":false
  },
  {
    "type":"string",
    "name":"ONELAB/Button",
    "values":["Run", "run"],
    "visible":false
  },
  {
    "type":"number",
    "name":"My solver/1Some flag",
    "values":[0],
    "choices":[0, 1]
  },
  {
    "type":"number",
    "name":"My solver/2Some parameter",
    "values":[1.234],
    "min":0,
    "max":10,
    "step":0.1
  },
  {
    "type":"number",
    "name":"My solver/3Some choice",
    "values":[0],
    "choices":[0, 1],
    "valueLabels":{"Choice 1": 0, "Choice 2": 1}
  },
  {
    "type":"string",
    "name":"My solver/3Some input",
    "values":[""]
  },
  {
    "type":"string",
    "name":"My solver/5Some action",
    "values":["select entity"],
    "attributes":{"Macro":"Action"}
  }
]"""

gmsh.onelab.set(parameters)

def runSolver():
    print("parameters =", gmsh.onelab.get())
    print("running the solver with the given parameters...")
    diffus = gmsh.onelab.getNames("ONELAB Context/.*([0-9]+)/11Diffusivity")
    for d in diffus:
        print(d, "=", gmsh.onelab.getNumber(d))

def eventLoop():
    # terminate the event loop if the GUI was closed
    if gmsh.fltk.isAvailable() == 0: return 0
    # wait for an event
    gmsh.fltk.wait()
    # check if an action is requested
    action = gmsh.onelab.getString("ONELAB/Action")
    if len(action) < 1:
        # no action requested
        pass
    elif action[0] == "check":
        # database was changed: update/define new parameters depending on new
        # state
        gmsh.onelab.setString("ONELAB/Action", [""])
        # print("parameters = ", gmsh.onelab.get())
        gmsh.fltk.update()
    elif action[0] == "reset":
        # user clicked on "Reset database"
        gmsh.onelab.setString("ONELAB/Action", [""])
        gmsh.onelab.set(parameters)
        gmsh.fltk.update()
    elif action[0] == "run":
        # user clicked on "Run"
        gmsh.onelab.setString("ONELAB/Action", [""])
        runSolver()
    elif action[0] == "select entity":
        # user clicked on "My solver/Select an entity"
        gmsh.onelab.setString("ONELAB/Action", [""])
        gmsh.fltk.setStatusMessage(
            "Please select an entity (or press 'q' to quit)", True)
        r, ent = gmsh.fltk.selectEntities()
        if gmsh.fltk.isAvailable() == 0: return 0
        if r and len(ent):
            gmsh.fltk.showContextWindow(ent[0][0], ent[0][1])
        gmsh.fltk.setStatusMessage("", True)
    return 1

if "-nopopup" not in sys.argv:
    gmsh.fltk.initialize()
    while eventLoop():
        pass
else:
    runSolver()

gmsh.finalize()
