# From video 16 Create Property Group & Enumerator (Panel)

# 2021-04-18 It works with several runs, each run has a different prefix
# Problem is that when I assign the materials to the newest run,
# it applies it to the older ones, which prevents mixed color scheme runs...

# Change emission_mat to an array of materials, and add a new set of materials
# for each consecutive level.
# With only one level, pretty much no difference!
# Save this one as 2021_04_18_chryzoid_chryzode_panel_before_mat_array_change.py
# Now called 2021_04_18_chryzoid_chryzode_panel.py
# It did not work.
# A better idea: give the lines a second prefix that denotes the color scheme
# and give them their colors accordingly, using only oNE palette!
# 2021-04-21 Now it works with selecting a ref line...
 
# 2021-04-23 tried to install as an addon with the bl_info below, and I got this message:

#  File "C:\Users\jpbjp\AppData\Roaming\Blender Foundation\Blender\2.92\scripts\addons\2021_04_18_chryzoid_chryzode_panel.py", line 272, in chryzoid_operator
#    mats = bpy.data.materials
# AttributeError: '_RestrictData' object has no attribute 'materials'
# 2021-05-01 3pm. It works with both chryzoid and chryzode, though you have to run a chryzoid first
# saved as 2021_05_01_chryzoid_chryzode_01.py
# NO, IT DOES WORK NOW, ALSO WHEN STARTING WITH CHRYZODE!

"""
2021-04-30 Saved as 2021_04_30_chryzoid_good_before_chryzode_implementation.py

Remove all extra comments from the next version 2021_05_01_chryzoid_chryzode.py
"""

import bpy
import time
from datetime import datetime
from math import sin, cos, tau, sqrt, atan2, radians
import random
import pprint
import os
from bpy.props import *
from operator import itemgetter

# Addon info
bl_info = {
    "name": "Chryzoid UI",
    "author": "JPB",
    "description": "The Blender Chryzoid!",
    "version": "1,0,0",
    "location":"Properties > Materials > The Blender Chryzoid",
    "category": "material",
    "support": "COMMUNITY",
    "blender": (2,92,0)
    }
    
timenow = time.time()

radius = 100 # The radius of the circle the points will sit on
radius2ThicknessRatio = 100
currentRefLineName = ""

colors_and_strengths = [#((.008, .008, .008, 1), 50, "gray"),
                      ((1, 0, 0, 1), 50, "red"),
                      ((0, 1, 0, 1), 50, "green"),
                      ((0, 0, 1, 1), 50, "blue"),
                      ((1, 0, 1, 1), 50, "purple"),
                      ((0, 0.423268, 0.863157, 1), 50, "cyan"),
                      ((0.838799, 0, 0.262251, 1), 50, "magenta"),
                      ((1, 0.887923, 0, 1), 50, "yellow"),
                      ((1, 1, 1, 1), 50, "white")  ]

# Static variables to know the color scheme used
# make it to an array for multiple runs color scheme attribution
# When using the value, use them directly, since COLORSHEMES[X] = X!
# The array is only used for its size
ONE = 0
RANDOM = 1
SERIAL = 2
LEVEL = 3
LEVEL_SERIAL = 4
POINT = 5
COLORSCHEMES = [ONE, RANDOM, SERIAL, LEVEL, LEVEL_SERIAL, POINT]

colorUseFlag = LEVEL_SERIAL # use of colors flag 'one' for one color
lineSetPrefix = "00_"
colorSchemePrefix = "00_"

# Each element of levelsLogF-orMaterials has the numPoints for that level
# for instance [3, 5, 7]
levelsLogForMaterials = [] # doChr-yzoid will fill this array to indicate the levels
#levelsLogForMaterials.append(-1) # DEBUG REMOVE AFTER 

os.system("cls")
print("-----> 30 time", timenow)
#### START OF REFLINE PROPERTIES
class RefLineProperties(bpy.types.PropertyGroup):
    refLineEnum : bpy.props.EnumProperty(
            name =          "",
            description =   "Pick the Reference Line",
            items =         [   ('ReferenceLine1', "ReferenceLine1", ""),
                                ('ReferenceLine2', "ReferenceLine2", ""),
                                ('ReferenceLine3', "ReferenceLine3", "")
                            ]
        )
#### END OF REFLINE PROPERTIES

#### START OF CLEARLINES PROPERTIES
class ClearLinesProperties(bpy.types.PropertyGroup):
    clearLinesBool : bpy.props.BoolProperty(
            name =  "",
            description="Delete the Existing Lines",
            default = True
            )
#### END OF CLEARLINES PROPERTIES

#### START OF COLORMODE PROPERTIES
class ColorModeProperties(bpy.types.PropertyGroup):
    colorModeEnum : bpy.props.EnumProperty(
            name =          "",
            description =   "Pick the Color Mode",
            items =         [   ('ONE', "ONE", ""),
                                ('RANDOM', "RANDOM", ""),
                                ('SERIAL', "SERIAL", ""),
                                ('LEVEL', "LEVEL", ""),
                                ('LEVEL_SERIAL', "LEVEL_SERIAL", ""),
                                ('POINT', "POINT", "")
                            ]
        )
#### END OF COLORMODE PROPERTIES

#### START OF CHRYZOID PROPERTIES
class ChryzoidProperties(bpy.types.PropertyGroup):
    title :         bpy.props.StringProperty(name="Chryzoid Title")
    numberFrom :    bpy.props.IntProperty(name="", default = 3, min = 3)    
    numberTo :      bpy.props.IntProperty(name="", default = 4, min = 4)    
    skip :          bpy.props.IntProperty(name="", default = 1, min = 1)
    z :             bpy.props.FloatProperty(name="", default = -.05)
    pos_z :         bpy.props.BoolProperty(
                                    name =  "",
                                    description="Use Positive Z",
                                    default = False
                    )
#### END OF CHRYZOID PROPERTIES
    
#### START OF CHRYZODE PROPERTIES
class ChryzodeProperties(bpy.types.PropertyGroup):
    title :         bpy.props.StringProperty(name="Chryzode Title")
    numPoints :     bpy.props.IntProperty(name="", default = 17, min = 3)    
    multiplier :    bpy.props.IntProperty(name="", default = 5, soft_min = 2, min = 1)
#### END OF CHRYZODE PROPERTIES
    
    
class ChryzoidPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label =          "Chryzoid " + str(abs(round((timenow - round(timenow))*500)))
    bl_idname =         "SCENE_PT_chryzoid"
    bl_space_type =     'VIEW_3D'
    bl_region_type =    'UI'
    bl_category =       "Chryzoid"

    def draw(self, context):
        #print("CCCCC 124 Start of draw for chryzoid")
        layout = self.layout
        scene = context.scene
        # below: x = y; x is a name YOU choose; y 
        refline_props = scene.refline_properties
        colorMode_props = scene.colorMode_properties
        clearLines_props = scene.clearLines_properties
        chryzoid_props = scene.chryzoid_properties
        chryzode_props = scene.chryzode_properties

        # Put the referene line picker
        #split = layout.split(factor=1)
        split = layout.split(factor= .32)
        col = split.column(align = True)
        col.label(text="ef Line:", icon="EVENT_R")
        col = split.column(align = True)
        col.prop(context.scene, "prop")
        
        # Put the color mode picker
        split = layout.split()
        col = split.column(align = True)
        col.label(text="olor Mode:", icon="EVENT_C")
        col = split.column(align = True)
        col.prop(colorMode_props, "colorModeEnum")
        
        row = layout.row()
        row = layout.row()
        
        split = layout.split()
       
        col = split.column(align = True)
        row = col.row()
        row.prop(clearLines_props, "clearLinesBool")
        row.label(text="el Old Lines Before Run", icon="EVENT_D")
        row = layout.row()
        split = layout.split()
        col = split.column(align = True)
        col.label(text="el ALL Lines", icon="EVENT_D")
        col = split.column(align = True)
        col.operator("chryzo2.operator", text="DELETE")
        #row = split.column(align=True)

        row = layout.row()
        split = layout.split(factor=.0001)
        col = split.column(align=True)
        #split.label(text="", icon="EVENT_Z")
        split.label(text="Positiv Z")
        #col = split.column(align=True)
        split.prop(chryzoid_props, "pos_z")
        split.prop(chryzoid_props, "z")

        row = layout.row()
        #row = split.column(align=True)
        split = layout.split()
        col = split.column(align = True)
        col.label(text = "ew Ref Line", icon="EVENT_N")
        col = split.column(align = True)
        col.operator("chryzo3.operator", text="New Ref Line")
        row = layout.row()
        row.label(text="Chryzoid")
        row.scale_y = 1
        
        # Create 3 columns, by using a split layout.
        split = layout.split()
        # First column
        col = split.column(align=True)
        col.label(text="rom:", icon="EVENT_F")
        col.prop(chryzoid_props, "numberFrom")

        # Second column, aligned
        col = split.column(align=True)
        col.label(text="o:", icon="EVENT_T")
        col.prop(chryzoid_props, "numberTo")

        # 3rd column, aligned
        col = split.column(align=True)
        col.label(text="kip:", icon="EVENT_S")
        col.prop(chryzoid_props, "skip")
        
        row = layout.row()
        split = layout.split()
        col = split.column(align=True)
        col.operator("chryzoid.operator", text="Run Chryzoid")
#        col = split.column(align=True)
#        col.operator("chryzo4.operator", text="CLS!!!")
        
        # Do layout for chryzode
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(text="Chryzode")
        
        # Create two columns, by using a split layout.
        split = layout.split()

        # First column
        col = split.column(align=True)
        sub = col.row()
        col.label(text="um of Points", icon="EVENT_N")
        col.prop(chryzode_props, "numPoints")

        # Second column, aligned
        col = split.column(align=True)
        col.label(text="ultiplier", icon="EVENT_M")
        col.prop(chryzode_props, "multiplier")
        row = layout.row()
        row = layout.row()
        row.operator("chryzo.operator", text="Run Chryzode")
       
def items_prop(self, context):
    return [(ob.name, ob.name, "") for ob in context.scene.objects if (ob.name.find("ReferenceLine") != -1)]


def update_prop(self, context):
    # This is where the Ref Line: dropdown menu is updated
    # I don't seem to need to do anything here anymore
    #print("-----> 231 I am updating prop")
    return

#### START OF VIEW3D FIND FUNCTION
def view3d_find(context, return_area = False ):
    # returns first 3d view, normally we get from context
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            v3d = area.spaces[0]
            rv3d = v3d.region_3d
            for region in area.regions:
                if region.type == 'WINDOW':
                    if return_area: return region, rv3d, v3d, area
                    return region, rv3d, v3d
    return None, None
#### END OF VIEW3D FIND FUNCTION

##### REMOVE OLD LINES FUNCTION
def removeOldLines(context, chryzoidOrChryzode):
    objs = bpy.data.objects
    if chryzoidOrChryzode == "Chryzoid":
        #print("FFFFF 282 in remove-OldLines and Removing chryzoid lines...")
        for obj in objs:
            if obj.name.find("_1p_") != -1 or obj.name.find("_2i_") != -1 or obj.name.find("ReferenceLine.") == 0:
                bpy.data.objects.remove(obj, do_unlink=True)
    elif chryzoidOrChryzode == "Chryzode":
        #print("FFFFF 287 in remove-OldLines and Removing chryzode lines...")
        for obj in objs:
            if obj.name.find("_L__") != -1 or obj.name.find("ReferenceLine.") == 0:
                bpy.data.objects.remove(obj, do_unlink=True)
    override = bpy.context.copy()
    override["area.type"] = ['OUTLINER']
    override["display_mode"] = ['ORPHAN_DATA']
    # removes the unused data from memory
    # From https://blenderartists.org/t/blender-2-92-goes-in-not-responding-neverland/1299982/2
    # this would normally occur when you close and re-open file
    # the number 4 is an arbitrary number of times to repeaet the command
    # which allows for purging unused materials, textures, etc
    # that are currently linked to mesh data
    bpy.ops.outliner.orphans_purge(override, 4)
##### END OF REMOVE OLD LINES FUNCTION

##### START OF PURGE OLD MATERIALS FUNCTION, FROM https://blenderartists.org/t/deleting-all-materials-in-script/594160/2
# the new function from nezumi.blend at https://blenderartists.org/t/blender-2-92-python-use-of-intproperties-crashes-addon/1298622/6
# still crashes, let's try a new approach
def purgeOldMaterials(context):
    #print("PPPPP 307 Purge old materials")
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)
#    def purgeOldMat-erials(self, context):
#        for mat in list(self.mats):
#            mat.remove(bpy.data.materials[0])
# my old that crashed blender because self.mats has possibly changed address
#    def purgeOldMat-erials(self, context):
#        for mat in self.mats:
#            self.mats.remove(bpy.data.materials[0])
##### END OF PURGE OLD MATERIALS FUNCTION

##### START OF CREATE SHADERS FUNCTION
### OBS em_matGiven is now an array of em_matGiven, use the current lineSetNumber on it
# I pass emission_mat[x], not the original emission_mat
# Nope, back to the old passing of the whole emission_mat
def createShaders(context, em_matGiven):
    # EMISSION SHADER: CREATE AN EMISSION SHADER SO THAT WE CAN SEE THE LINE
    # EMISSION SHADER: NEW SHADER
    COLOR = 0
    STRENGTH = 1
    COLOR_NAME = 2
    
    nodes = []
    material_output = []
    node_emission = []
    links = []

    # create as many materials as we have colors
    for col_or in range(len(colors_and_strengths)):
        em_matGiven.append(bpy.data.materials.new(name = "_Emission_" + colors_and_strengths[col_or][COLOR_NAME]))
        em_matGiven[col_or].use_nodes = True
        nodes.append(em_matGiven[col_or].node_tree.nodes)
        material_output.append(nodes[col_or].get('Material Output'))
        node_emission.append(nodes[col_or].new(type='ShaderNodeEmission'))
        node_emission[col_or].inputs[0].default_value = colors_and_strengths[col_or][COLOR] # RGB + Alpha
        node_emission[col_or].inputs[1].default_value = colors_and_strengths[col_or][STRENGTH] # strength
        links.append(em_matGiven[col_or].node_tree.links)
        new_link = links[col_or].new(node_emission[col_or].outputs[0], material_output[col_or].inputs[0])
            
    # remove BSDF From Materials (used to be a function
    for i in range(len(bpy.data.materials)):
        mat = bpy.data.materials[i]
        if mat.name.find("Principled BSDF") != -1:
            node_to_delete =  mat.node_tree.nodes['Principled BSDF']
            mat.node_tree.nodes.remove( node_to_delete )
    #print("-----> 377 at the end of create shaders and the next element in em_matGiven has now size", len(em_matGiven))
##### END OF CREATE SHADERS FUNCTION

##### START OF POPULATE POINTS AND LINE LENGTHS FUNCTION
def populatePointsAndLineLengths(context, numPointsGiven):
    global radius
    global sidesLen
    global theta0
    global points
    theta0 = tau / 2 * (1 / 2 + 1 / numPointsGiven)
    
    # purge points array
    points = []
    # purge sidesLen array EXCEPT 0 ELEMENT, WHICH IS 0!
    sidesLen = []
    sidesLen.append(0)
        
    # START OF BUILD POINTS ARRAY
    for i in range(numPointsGiven):
       # points.append((self.radius * cos(i * tau/numPointsGiven), self.radius * sin(i * tau/numPointsGiven), 0))
        points.append((radius * cos(i * tau/numPointsGiven), radius * sin(i * tau/numPointsGiven), 0))
    # END OF BUILD POINTS ARRAY

    # START OF BUILD SIDESLEN ARRAY FOR __EVEN__ numPointsGiven
    if numPointsGiven % 2 == 0:
        numPointsGivenOver2 = int (numPointsGiven/2)
        # Fill from 0 to numPointsGiven/2 excluded
        for i in range(1, numPointsGivenOver2):
            sidesLen.append(sqrt((points[i][0] - points[0][0]) * (points[i][0] - points[0][0]) + (points[i][1] - points[0][1]) * (points[i][1] - points[0][1])) / 100)
        # Fill numPointsGiven/2, the lone longest segment
        sidesLen.append(sqrt((points[numPointsGivenOver2][0] - points[0][0]) * (points[numPointsGivenOver2][0] - points[0][0]) + (points[numPointsGivenOver2][1] - points[0][1]) * (points[numPointsGivenOver2][1] - points[0][1])) / 100)
        # Fill numPointsGiven/2 + 1 to numPointsGiven - 1
        for i in range(numPointsGivenOver2 + 1, numPointsGiven - 0):
            sidesLen.append(sidesLen[numPointsGiven - i])
    # END OF BUILD SIDES LENGTHS ARRAY FOR EVEN numPointsGiven

    # START OF BUILD SIDESLEN ARRAY FOR __ODD__ numPointsGiven
    if numPointsGiven % 2 != 0:
        numPointsGivenOver2 = int (numPointsGiven / 2)

        # Fill from 0 to numPointsGiven/2 INCLUDED
        for i in range(1, numPointsGivenOver2 + 1):
            sidesLen.append(sqrt((points[i][0] - points[0][0]) * (points[i][0] - points[0][0]) + (points[i][1] - points[0][1]) * (points[i][1] - points[0][1])) / 100)
            #print(">>>>> 629 for i:", i, "added", sidesLen[len(sidesLen) - 1])

        # Fill numPointsGiven/2 + 1 to numPointsGiven - 1
        for i in range(numPointsGivenOver2 + 1, numPointsGiven):
            sidesLen.append(sidesLen[numPointsGiven - i])
    # END OF BUILD SIDESLEN ARRAY FOR __ODD__ numPointsGiven
#    for i in range(len(points)):
#        print(">>>>> 399 points", points[i])
#    for i in range(len(sidesLen)):
#        print(">>>>> 401 Side Length", sidesLen[i])
##### END OF POPULATE POINTS AND LINE LENGTHS FUNCTION

##### START OF select Object By Name FUNCTION
def selectObjectByName(context, objectToSelect):
    ## deselect all (just in case?) then select and activate Refe renceLine WITHOUT USING bpy.ops
    # from https://blenderartists.org/t/element-selected-in-outliner-and-i-dont-want-it-to-be/1296825/3
    for selected in bpy.context.selected_objects:
        selected.select_set(False)
    newObject = bpy.data.objects[objectToSelect] 
    newObject.select_set(True)
    bpy.context.view_layer.objects.active = newObject
# other code to select only one object, using bpy.ops...
# from https://blenderartists.org/t/element-selected-in-outliner-and-i-dont-want-it-to-be/1296825/3
# don't run it, the one above works too
#bpy.ops.object.select_all(action='DESELECT')
#obj = bpy.data.objects["Refer0enceLine"] 
#obj.select_set(True)
#bpy.context.view_layer.objects.active = obj
##### END OF select Object By Name FUNCTION

class chryzoid_operator(bpy.types.Operator):
    bl_label = "Operator"
    bl_idname = "chryzoid.operator"
    
    print("CCCCC 433 Start of chryzoid_operator")
##### Here I copy all the code from the F3 chryzoid...
    lineNr = 0
    
    # move the declaration below to def __init__(self):
    #mats = bpy.data.materials
    numPoints = 7 # The number of points to be distributed equidistantly on the circumference of the circle of radius defined below
    points = []
     # This is used to differentiate runs when clearLines_props.clearLinesBool is false and more than one set of lines is created
    runNumber = 1
    # The consecutive values, from index 1, of the array below have the length of a side from a point to a point index away from it
    sidesLen = []
    sidesLen.append(0) # Array of sides lengths [0] has 0, see note 3 lines above
    theta0 = tau / 2 * (1 / 2 + 1 / numPoints)

    # Static variables below to know which index we have in the line name
    # The line names syntax is the following
    # AA_BB_L_CC_1p_DD_EE for periphery lines,thus the "_1p_", where p is for periphery 
    # and 1 so that the periphery lines come first in the Outliner
    # or 
    # AA_BB_L_CC_2i_DD_EE for inside lines, thus the "_2i_", where i is for inside
    # and 2 so that the inside lines come second in the Outliner
    #
    # AA is the run number
    # BB is the color scheme  number so that the schemes can be preserved 
    # when giving materials in more than one run
    # _L_ is there just to say that we have lines
    # CC is the number of points
    # _1p_ or _2i_ indicate whether it is periphery or inside lines, see 8 and 11 lines above
    # DD is the point from
    # EE is the line to
    
    LINESETPREFIX = 0
    COLORSCHEMEPREFIX = 1
    NUMLINE = 3
    POINTFROM = 5
    POINTTO = 6
    
    lineSetNumber = 0
    ##### START OF SHOW LINE DATA FUNCTION (ONLY FOR DEBUG)
    def showLineData(self, context, lineToShow):
        #return
        refLine = bpy.data.objects[lineToShow]
        print("-----> 384 \nLINE", lineToShow, "DATA:\nLocation:", refLine.location, "\nRotation:", refLine.rotation_euler, "\nScale:", refLine.scale)
    ##### END OF SHOW LINE DATA FUNCTION (ONLY FOR DEBUG)
        
    #### START OF DO COLORS BY LEVEL FUNCTION
    def doColorsByLevel(self, context, linesGiven, em_matGiven, levelOrLevelSerial):
        # Here I get only lines with AA_03 as starting name, since we are on the LEVEL scheme
        #os.system("cls")
        global levelsLogForMaterials
        # if levelsLogForM-aterials is [3, 5, 7] we get the 3 from [0] and the 7 from [len() - 1
        # This way, we know how many levels to treat, from to to,
        # and how many lines there are per level, per n * (n - 1)/2
        print("ccccc 483 in doColorsByLevel and levelsLo-gForMaterials", levelsLogForMaterials)
        firstLineNumPoints = levelsLogForMaterials[0]
        lastLineNumPoints = levelsLogForMaterials[len(levelsLogForMaterials) - 1]
        numLevels = lastLineNumPoints - firstLineNumPoints
        calcNumLines = 0
        if len(levelsLogForMaterials) == 1:
            # Assign a random color for each level
            matForThatLevel = random.randint(0, len(em_matGiven) - 1)
            for j in range(len(linesGiven)):
                linesGiven[calcNumLines + j].data.materials.append(em_matGiven[matForThatLevel])

        if len(levelsLogForMaterials) > 1:
            matForThatLevel = 0
            for i in range(len(levelsLogForMaterials)):
                # Assign a random color for each level
                if levelOrLevelSerial == LEVEL:
                    matForThatLevel = random.randint(0, len(em_matGiven) - 1)
                # or do it serial and Assign the next color for each level
                if levelOrLevelSerial == LEVEL_SERIAL:
                    matForThatLevel = (matForThatLevel + 1)# % len(em_matGiven)
                numLinesForThatLevel = int(levelsLogForMaterials[i] * (levelsLogForMaterials[i] - 1) / 2)
                for j in range(numLinesForThatLevel):
                    linesGiven[calcNumLines + 0].data.materials.append(em_matGiven[matForThatLevel % len(em_matGiven)])
                    calcNumLines += 1
                #calcNumLines += int(levelsLogForMaterials[i] * (levelsLogForMaterials[i] - 1) / 2)
    #### END OF DO COLORS BY LEVEL FUNCTION

    #### START OF DO COLORS BY POINT FUNCTION
    def doColorsByPoint(self, context, linesGiven, em_matGiven):
        # Assign a random color for each point from 0
        global levelsLogForMaterials
        lastPointToCheck = levelsLogForMaterials[len(levelsLogForMaterials) - 1]
        #print("-----> 423 PPPPPP in points and I have", len(linesGiven), "lines and log", levelsLogForMaterials, "--------> last poinit to check", lastPointToCheck)
        linesDone = []
        for i in range(len(linesGiven)):
            linesDone.append(-1)
        # The last element of linesDone, by line below, contains the actual number of lines done...
        linesDone.append(0)
        colorForThatPoint = random.randint(0, len(colors_and_strengths) - 1)
        colorForPreviousPoint = colorForThatPoint
        
        # START OF DO LINES EMANATING FROM THE 0 POINT
        pointToCheck = 0
        #print("-----> 434 line name split", linesGiven[i].name.split("_"))
        for i in range(len(linesGiven)):
            # a is the number of points b is the point to c is the point from
            a = int(linesGiven[i].name.split("_")[self.NUMLINE])
            b = int(linesGiven[i].name.split("_")[self.POINTTO])
            c = linesGiven[i].name.split("_")[self.POINTFROM]
            if (a == b) or (c == "00"):
                linesDone[i] = pointToCheck
                linesDone[len(linesDone) - 1] += 1
                linesGiven[i].data.materials.append(em_matGiven[colorForThatPoint])
        # END OF DO LINES EMANATING FROM THE 0 POINT
        
        # START OF DO LINES EMANATING FROM THE 1 POINT
        for i in range(1, lastPointToCheck):
            if linesDone[len(linesDone) - 1] == len(linesGiven):
                break
            colorForThatPoint = random.randint(0, len(colors_and_strengths) - 1)
            while colorForThatPoint == colorForPreviousPoint:
                colorForThatPoint = random.randint(0, len(colors_and_strengths) - 1)
            colorForPreviousPoint = colorForThatPoint
            for j in range(len(linesGiven)):
                # a is point from
                a = int(linesGiven[j].name.split("_")[self.POINTFROM])
                #b = int(linesGiven[j].name.split("_")[self.POINTTO])
                if linesDone[j] == -1:
                    if a == i:
                        linesDone[j] = i
                        linesGiven[j].data.materials.append(em_matGiven[colorForThatPoint])
                        linesDone[len(linesDone) - 1] += 1
    #### END OF DO COLORS BY POINT FUNCTION

    #### START OF APPLY SCHEME FUNCTION FOR CHRYZOID
    def applyScheme(self, context, linesToUse, schemeNumber, em_matGiven):
        #print("-----> 502 in app-ly one scheme and lines", linesToUse)
        
        # app-ly material to frame (temporary)
        bpy.data.objects['ReferenceLinePLANE'].data.materials.clear()
        bpy.data.objects['ReferenceLinePLANE'].data.materials.append(em_matGiven[2])
        colorToUse = random.randint(0, len(em_matGiven) - 1)
        for i in range(len(linesToUse)):
            linesToUse[i].data.materials.clear()
        # NOW APPLY
        #print("sssss 569 in app-lyScheme and sheme number", schemeNumber, "is it ONE (I mean 0...)", ONE)
        if schemeNumber == ONE:
            #print("sssss 571 in app-lyScheme and YES IT IS", schemeNumber)
            for i in range(len(linesToUse)):
                linesToUse[i].data.materials.append(em_matGiven[colorToUse])

        if schemeNumber == RANDOM:
            for i in range(len(linesToUse)):
                linesToUse[i].data.materials.append(em_matGiven[random.randint(0, self.numPoints - 1)])

        if schemeNumber == SERIAL:
            colorToUse = 0;
            for i in range(len(linesToUse)):
                linesToUse[i].data.materials.append(em_matGiven[colorToUse])
                colorToUse = (colorToUse + 1) % len(em_matGiven)

        if schemeNumber == LEVEL:
            self.doColorsByLevel(context, linesToUse, em_matGiven, LEVEL)

        if schemeNumber == LEVEL_SERIAL:
            self.doColorsByLevel(context, linesToUse, em_matGiven, LEVEL_SERIAL)

        if schemeNumber == POINT:
            self.doColorsByPoint(context, linesToUse, em_matGiven)
    #### END OF APPLY SCHEME FUNCTION FOR CHRYZOID

    #### START OF APPLY MATERIALS TO LINES CHRYZOID FUNCTION
    def applyMaterialsToLinesChryzoid(self, context, em_matGiven):
        #global colorUseFlag
        global lineSetPrefix
        #print("ccccc 598 in applyMaterial-sToLinesChryzoid and colorschemeprefix", colorSchemePrefix[0:2])
        colSchemeForLine = int(colorSchemePrefix[0:2])

        # FIRST, BUILD A LIST OF LINES

        # parse through all possible color schemes
        # Get the number of color schemes from the dropdown!
        # Nope, what you get is the length of the string!!!
        # Then make the scheme numbers to an array...
        scene = context.scene
        colorMode_props = scene.colorMode_properties
        # Here is the only place where COLORSCHEMES is used for its length
        # # All other places, use X instead of COLORSCHEME[X] SINCE COLORSCHEME[X] == X!
        numSchemes =  len(COLORSCHEMES)        
        #print("-----> 522 num schemes", numSchemes)
        
        # For each scheme, build the list of lines that have it
        for scheme in range(numSchemes):
            #print("-----> 488 SSSS Doing scheme", scheme)
            
            # make scheme # to a string with '_' at the end
            prefix = ""
            if scheme < 10:
                prefix = "0"
            schemeNumberString = "_" + prefix + str(scheme) + "_L"
            
            # get all the lines that have that scheme
            lines = []
            for j in range(len(bpy.data.objects)):
                if (bpy.data.objects[j].name.find(schemeNumberString) != -1):
                    lines.append(bpy.data.objects[j])
            # if any, apply the right scheme
            if len(lines) > 0:
                #print("-----> 541 I found", len(lines), "with", schemeNumberString, "as prefix calling applyS-cheme")
                self.applyScheme(context, lines, scheme, em_matGiven)
    #### END OF APPLY MATERIALS TO LINES CHRYZOID FUNCTION

    ##### START OF build Ref Line From CUBE FUNCTION
    def buildRefLineFromCube(self, context):
        global runNumber
        
        # try to do the scaling in edit mode
        #bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=True, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.transform.resize(value=(radius, radius / radius2ThicknessRatio, radius / radius2ThicknessRatio))
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.context.scene.cursor.location[0] = -radius / 2
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        bpy.context.scene.cursor.location[0] = 0
        bpy.context.object.location[0] = 0
        #bpy.ops.mesh.select_all(action='DESELECT')
        
        # Override code to run the loopcuts...
        region, rv3d, v3d, area = view3d_find(context, True)

        override = {
            'scene'  : bpy.context.scene,
            'region' : region,
            'area'   : area,
            'space'  : v3d
        }
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.loopcut_slide(
            override,
            MESH_OT_loopcut = {
                "object_index" : 0,
                "number_cuts":550, 
                "smoothness":0, 
                "falloff":'SMOOTH', 
                "edge_index":4, 
                "mesh_select_mode_init":(True, False, False)
            }, 
            TRANSFORM_OT_edge_slide = {
                "value"             : 0, 
                "mirror"                : False, 
                "snap"                  : False, 
                "snap_target"           : 'CLOSEST', 
                "snap_point"            : (0, 0, 0), 
                "snap_align"            : False, 
                "snap_normal"           : (0, 0, 0), 
                "correct_uv"            : False, 
                "release_confirm"       : False, 
            }
        )
        bpy.context.object.name="ReferenceLine"
        bpy.context.object.location = (-300, 100, 0)
        for selected in bpy.context.selected_objects:
            print("-----> 700 JUST CREATED REFLINE, thus it is OBVIOUSLY selected", selected.name)
            print("-----> 701 called only when no ref line found in draw full lines...")
    ##### END OF build Ref Line From CUBE FUNCTION

    ##### START OF BUILDPREFIXESFORNAMESFORCHRYZOID FUNCTION
    def buildPrefixesForNameForChryzoid(self, context, numPointsGiven, iGiven, jGiven):
        if numPointsGiven > 9:
            zeroPrefix = ''
        else:
            zeroPrefix = '0'
        if iGiven > 9:
            zeroPrefixI = ''
        else:
            zeroPrefixI = '0'
        if jGiven > 9:
            zeroPrefixJ = ''
        else:
            zeroPrefixJ = '0'
        zero_prefixes =  (zeroPrefix, zeroPrefixI, zeroPrefixJ)
        #print("-----> 709 and prefixes are", zero_prefixes)
        return zero_prefixes
    ##### END OF BUILDPREFIXESFORNAMESFORCHRYZOID FUNCTION

    ##### START OF look for dot ref lines  and show them DEBUG FUNCTION
    def look_for_dot_ref_lines_and_show_them(self, context, message):
        #print("LLLLL 716 looking for '.' ref lines:\"", message, "\"")
        reflines = []
        reflinesString = "FFFFFF Found these ref lines:"
        for ob in bpy.data.objects:
            if ob.name.find(".") != -1:
                reflines.append(ob)
#        if len(reflines) == 0:
#            print("LLLLL 722: NO '.' reflines...")
#        else:
#            for ob in reflines:        
#                reflinesString = reflinesString + ob.name + " "
#                print("LLLLL 725 I have the following '.' ref lines", ob.name)
#        print(reflinesString)
    ##### END OF look for dot ref lines  and show them DEBUG FUNCTION

                                  
    ##### START OF DRAWFULLLINE FUNCTION
    def drawFullLinesChryzoid(self, context, numPointsGiven):
        # Draw all lines
        
        # buildRe_fLine if it does not exist
        # Now you can pick the reference line from a dropdown menu...
        #os.system("cls")
        global currentRefLineName
        global lineSetPrefix
        foundRefLine = False
        
        # Look for a reference line that corresponds to the dropdown menu asdf
        #print("\nLLLLL 744 Looking for\"", context.scene.prop, "\" in object list")
        for i in range(len(bpy.data.objects)):
            if bpy.data.objects[i].name.find(context.scene.prop) == 0:
                foundRefLine = True
                bpy.ops.object.select_all(action='DESELECT')
                #print("LLLLL 749 I got it: \"", context.scene.prop, "\"")
                # Fetch the selected reference line from dropdown menu
                selectObjectByName(context, context.scene.prop)  
                break
        if foundRefLine == False:
            self.buildRefLineFromCube(context)
        
        # AT THIS POINT ReferenceLine IS SELECTED EXIT EDIT MODE
        #print("-----> 757 ref line selected is \"", bpy.context.object.name, "\"")
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Keep a pointer to the reference line (it is the ONLY selected object)
        currentRefLineName = bpy.context.selected_objects[0].name
        #print(">>>>> 762 current ref line name \"", currentRefLineName, "\"")
        
        # FIRST DRAW LINES ON PERIPHERY 0_1, 1_2, AND SO ON
        # OBS! THE REFERENCE LINE MUST BE SELECTED IF IT EXISTS ALREADY IT IS! 
        #print("ccccc 765 DO I HAVE A COLORUSEFLAG!!!!!!", colorUseFlag)  
        colorSchemePrefix = "0" + str(colorUseFlag) + "_"
        
        for i in range(len(points)):
            #self.look_for_dot_ref_lines_and_show_them(context, ">>>>> 772 BEFORE drawing EACH periphery line")
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[currentRefLineName].select_set(True)
            
            
            # FROM https://b3d.interplanety.org/en/how-to-set-object-mesh-to-active-in-blender-2-8-python-api/
            objs = context.window.scene.objects
            for obj in objs:
                if obj.name == currentRefLineName:
                    #print("????? 782 Do I have the right object?????", obj.name)
                    context.view_layer.objects.active = obj
                    break
            
            bpy.context.scene.cursor.location=(0, 0, 0)
            #print("SSSSS 787 Selected objects", list(context.selected_objects), "and context.object.name", context.object.name)
            #print("BBBBB 788 i:", i, "object name BEFORE DUP", context.object.name)
            # Get a copy of the selected reference line for next chryzoid periphery line
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0)})
            #print("AAAAA 791 i:", i, "object name AFTER DUP", context.object.name)
            #self.look_for_dot_ref_lines_and_show_them(context, ">>>>> 779 AFTER duplicating ref line")
            
            # Build prefixes for name
            prefixes = self.buildPrefixesForNameForChryzoid(context, numPointsGiven, i, (i + 1))
            zeroPrefix = prefixes[0]
            zeroPrefixI = prefixes[1]
            zeroPrefixIPlus1 = prefixes[2]
                             
            # Assign name
            context.object.name = lineSetPrefix + colorSchemePrefix + "L_" + zeroPrefix + str(numPointsGiven) + "_" + "1p_" + zeroPrefixI + str(i) + "_" +  zeroPrefixIPlus1 + str(i + 1 % numPointsGiven)
            #print("RRRRR 802 i:", i, "object name AFTER RENAMING", context.object.name)
            # AT THIS POINT WE HAVE THE RIGHT NAME for a periph line: AA_BB_L_CC_1p_DD_EE
            
            # Place line where it has to be on the Z = 0 plane
            context.object.location[0] = points[i][0]
            context.object.location[1] = points[i][1]
            
            # Place line on Z axis so that the levels is in ascending order (Lower levels on top)
            if context.scene.chryzoid_properties.pos_z == True:
                context.object.location[2] = (numPointsGiven - 3) * context.scene.chryzoid_properties.z
                
            # Place line on Z axis so that the levels is in descending order (Higher levels on top)
            if context.scene.chryzoid_properties.pos_z == False:
                context.object.location[2] = (numPointsGiven - 3) * -context.scene.chryzoid_properties.z
            
            
            # Resize
            context.object.scale[0] = sidesLen[1]

            # Rotate the line by the right amount in Z axis for periphery lines for chryzoid
            ang = (theta0 + (i) * tau / numPointsGiven) % tau
            bpy.data.objects[context.object.name].rotation_euler[2] = ang
            #print("aaaaaaaaaaaaaaa 828 chryzoid periphery angle for points", numPointsGiven, ":", round(ang * 360 / tau), "theta0", round(theta0 * 360 / tau))
        #print("\nLLLLL 825 PERIPHERY LINES FINE, LET'S LOOK AT THE INNER ONES...\n")
        # END OF DRAWING THE LINES ON PERIPHERY...
            
        # LET'S DRAW THE INNER LINES, THEN...
                
        # AT THIS POINT RefeLine_Periph_num_num-1_num IS SELECTED
        for i in range(len(points)): # OBS DISABLED IF 0 IN THE RANGE, FOR DEBUGGING...
            for j in range(i + 2, len(points) - 0):
                # Nothing to do here, get out!
                if (j - i) == numPointsGiven - 1:
                    continue

                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[currentRefLineName].select_set(True)
                objs = context.window.scene.objects
                for obj in objs:
                    if obj.name == currentRefLineName:
                        #print("IIIIII 860 Do I have the right object?????", obj.name)
                        context.view_layer.objects.active = obj
                        break
            
                bpy.context.scene.cursor.location=(0, 0, 0)
                #print("IIIIII 873 Selected objects", list(context.selected_objects), "and context.object.name", context.object.name)
                #print("IIIIII 874 i:", i, "object name BEFORE DUP", context.object.name)
                # Get a copy of the selected reference line for next chryzoid inner line
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(-0, -0, 0)}) #
                #print("IIIIII 877 i:", i, "object name AFTER DUP", context.object.name)
                
                # Build prefixes for name
                prefixes = self.buildPrefixesForNameForChryzoid(context, numPointsGiven, i, j)
                zeroPrefix = prefixes[0]
                zeroPrefixI = prefixes[1]
                zeroPrefixJ = prefixes[2]
                
                # Assign name
                bpy.context.selected_objects[0].name = lineSetPrefix + colorSchemePrefix + "L_" + zeroPrefix + str(numPointsGiven) + "_" + "2i_" + zeroPrefixI + str(i) + "_" + zeroPrefixJ + str(j)
                #print("RRRRR 887 i:", i, "object name AFTER RENAMING", context.object.name)
                # AT THIS POINT WE HAVE THE RIGHT NAME for an inner line: AA_BB_L_CC_2i_DD_EE
            
                # Place line where it has to be on the Z = 0 plane
                bpy.context.object.location[0] = points[i][0]
                bpy.context.object.location[1] = points[i][1]
                
                # Place line so that the levels is in ascending order (Lower levels on top)
                if bpy.context.scene.chryzoid_properties.pos_z == True:
                    bpy.context.object.location[2] = (numPointsGiven - 3) * bpy.context.scene.chryzoid_properties.z
                
                # Place line so that the levels is in descending order (Higher levels on top)
                if bpy.context.scene.chryzoid_properties.pos_z == False:
                    bpy.context.object.location[2] = (numPointsGiven - 3) * -bpy.context.scene.chryzoid_properties.z
                
                #bpy.context.object.scale[0] = sidesLen[j - i]
            

                # scaling issue here
                # used to do it in object mode (one line of code only), 
                # the old resize in object mode
                # Resize
                context.object.scale[0] = sidesLen[j - i]

                # Rotate the line by the right amount in Z axis for inner lines for chryzoid
                ang = (theta0 + i * (tau / numPointsGiven) + (j - i - 1) * (tau / (2 * numPointsGiven))) % tau
                #print("aaaaaaaaaaaaaaa 890 chryzoid inner angle for points", numPointsGiven, ":", round(ang * 360 / tau), "theta0", round(theta0 * 360 / tau))
                bpy.data.objects[bpy.context.object.name].rotation_euler[2] = ang
            bpy.context.scene.cursor.location=(0, 0, 0)
    ##### END OF DRAWFULLLINE FUNCTION

    ##### START OF DO CHRYZOID FUNCTION
    def doChryzoid(self, context, numPointsGiven, colorSchemeGiven):
        colorUseFlag = colorSchemeGiven
        populatePointsAndLineLengths(context, numPointsGiven)
        self.drawFullLinesChryzoid(context, numPointsGiven) # DRAW LINES AFTER THEY HAVE BEEN SCALED. OBS IT CALLS build RefLine!
    ##### END OF DO CHRYZOID FUNCTION

    ##### START OF EXECUTE FUNCTION FOR CHRYZOID
    def execute(self, context):
        print("\nCCCCC 911 At start of execute for chryzoid")
        #os.system("cls")
        
        global COLORSCHEMES
        global colorUseFlag
        global levelsLogForMaterials
        global lineSetPrefix
        global lineSetNumber

        layout = self.layout
        scene = context.scene
        refline_props = scene.refline_properties
        colorMode_props = scene.colorMode_properties
        clearLines_props = scene.clearLines_properties
        chryzoid_props = scene.chryzoid_properties
        chryzode_props = scene.chryzode_properties
        
        
        ###### LET'S     ###### HAVE    ###### FUN    ###### NOW...
        startTime = time.time()
        startDate = datetime.now()

        # Remove old lines if necessary
        # Moved the function out so that chryzode also can use it
        #print("CCCCC 925 about to call remove-OldLines")
        if clearLines_props.clearLinesBool == True:
            removeOldLines(context, "Chryzoid")
            
        # Purge materials
        # Moved the function out so that chryzode also can use it
        purgeOldMaterials(context)
        emission_mat = []
        createShaders(context, emission_mat)
        #print("!!!!!! 929 in execute and levelsLogForMaterials", levelsLogForMaterials, "SHOUD BE -1...")
        levelsLogForMaterials = [] # Reset the levels log for materials
        print("\n-----> 931 At start of EXECUTE FOR chryzoid_operator...\n...about to do chryzoids from", bpy.context.scene.chryzoid_properties.numberFrom, "to", bpy.context.scene.chryzoid_properties.numberTo, "skipping", bpy.context.scene.chryzoid_properties.skip, "...\n...and colorUseFlag", colorUseFlag, "before setting it, and colorMode_props.colorModeEnum", colorMode_props.colorModeEnum)
        if colorMode_props.colorModeEnum == 'ONE':
            colorUseFlag = COLORSCHEMES[ONE]
        if colorMode_props.colorModeEnum == 'RANDOM':
            colorUseFlag = COLORSCHEMES[RANDOM]
        if colorMode_props.colorModeEnum == 'SERIAL':
            colorUseFlag = COLORSCHEMES[SERIAL]
        if colorMode_props.colorModeEnum == 'LEVEL':
            colorUseFlag = COLORSCHEMES[LEVEL]
        if colorMode_props.colorModeEnum == 'POINT':
            colorUseFlag = COLORSCHEMES[POINT]
        # Get the prefix of the lines, that is the "XX_" that is before "L_"
        # The XX_ is there for all lines of one run to differentiate them from another run
        # to avoid ending with ".001" and so on on the next run
        lineSetPrefix = "00_"
        lineSetNumber = 0
        foundLinePrefix = False
        lineNameFound = ""
        lineSetNumberPadding = ""
        #allLinesFound = []
        
        # set lineSetNumber to the next value if applicable for chryzoid
        for j in range(len(bpy.data.objects)):
            if bpy.data.objects[j].name.find("L_") != -1:
                self.lineSetNumber = int(bpy.data.objects[j].name[:2]) + 1
                lineNameFound = bpy.data.objects[j].name
                foundLinePrefix = True
        if self.lineSetNumber < 10:
            lineSetNumberPadding = "0"
        lineSetPrefix = lineSetNumberPadding + str(self.lineSetNumber) + "_"
        print("-----> 960 At start of EXECUTE FOR chryzoid_operator lineSetNumber", self.lineSetNumber, "and linesetprefix", lineSetPrefix)
            
        # Start of dochryzoid loop
        for i in range(context.scene.chryzoid_properties.numberFrom, context.scene.chryzoid_properties.numberTo + 1, context.scene.chryzoid_properties.skip):
            levelsLogForMaterials.append(i)
            tempstarttime = time.time()
            #print("----> 866 Doing chryzoid", i, "of from", bpy.context.scene.chryzoid_properties.numberFrom, "to", bpy.context.scene.chryzoid_properties.numberTo, "skip", bpy.context.scene.chryzoid_properties.skip)
            self.doChryzoid(context, i, colorUseFlag)
            tempendtime = time.time()
            print("-----> 968 Doing chryzoid", i, "of from", context.scene.chryzoid_properties.numberFrom, "to", bpy.context.scene.chryzoid_properties.numberTo, "skip", bpy.context.scene.chryzoid_properties.skip, "took", round((tempendtime - tempstarttime) * 1000), "ms")
            
            # MAKE SURE THAT REF LINES IS SELECTED AT START OF EACH RUN
            for selected in bpy.context.selected_objects:
                selected.select_set(False)

            #newObject = bpy.data.objects["ReferenceLine"] 
            newObject = bpy.data.objects[context.scene.prop] 
            newObject.select_set(True)
            bpy.context.view_layer.objects.active = newObject

        self.applyMaterialsToLinesChryzoid(context, emission_mat)

        endTime = time.time()
        print("CCCCC 989 At end of execute for chryzoid") # and", startDate)
        #print("-----> 1019 At end of execute and It took:", round((endTime - startTime) * 1000), "ms")
         
        selectObjectByName(context, context.scene.prop)
                
        return {'FINISHED'}
    ##### END OF EXECUTE FUNCTION FOR CHRYZOID

    #execute(bpy.context)
    
#### start of chryzode_operator
class chryzode_operator(bpy.types.Operator):
    bl_label = "Operator"
    bl_idname = "chryzo.operator"
    
    print("ccccc 1004 Start of chryzode_operator")
    
    ##### START OF BUILDPREFIXESFORNAMESFORCHRYZODE FUNCTION
    def buildPrefixesForNameForChryzode(self, context, numPointsGiven, linesArrayIGiven):
        if numPointsGiven > 99:
            zeroPrefix = ''
        elif numPointsGiven <= 99 and numPointsGiven > 9:
            zeroPrefix = '0'
        else:
            zeroPrefix = '00'
            
        if linesArrayIGiven[0] > 999:
            zeroFromPrefix = ''
        elif linesArrayIGiven[0] < 99 and linesArrayIGiven[0] > 9:
            zeroFromPrefix = '0'
        else:
            zeroFromPrefix = '00'
            
        if linesArrayIGiven[1] > 999:
            zeroToPrefix = ''
        elif linesArrayIGiven[1] < 99 and linesArrayIGiven[1] > 9:
            zeroToPrefix = '0'
        else:
            zeroToPrefix = '00'
            
        zero_prefixes =  (zeroPrefix, zeroFromPrefix, zeroToPrefix)
        #print("-----> 1030 and prefixes are", zero_prefixes)
        return zero_prefixes
    ##### END OF BUILDPREFIXESFORNAMESFORCHRYZODE FUNCTION

    #### START OF DRAW FULL LINES CHRYZODE FUNCTION
    def drawFullLinesChryzode(self, context, numPointsGiven, linesArrayGiven):
        
        global currentRefLineName
        global lineSetPrefix
        foundRefLine = False
        
        # Look for a reference line that corresponds to the dropdown menu asdf
        #print("\nLLLLL 1042 Looking for\"", context.scene.prop, "\" in object list")
        for i in range(len(bpy.data.objects)):
            if bpy.data.objects[i].name.find(context.scene.prop) == 0:
                foundRefLine = True
                bpy.ops.object.select_all(action='DESELECT')
                #print("LLLLL 1047 I got it: \"", context.scene.prop, "\"")
                # Fetch the selected reference line from dropdown menu
                selectObjectByName(context, context.scene.prop)  
                break
        if foundRefLine == False:
            self.buildRefLineFromCube(context)

        # AT THIS POINT ReferenceLine IS SELECTED EXIT EDIT MODE
        #print("-----> 1055 ref line selected is \"", bpy.context.object.name, "\"")
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Keep a pointer to the reference line (it is the ONLY selected object)
        currentRefLineName = bpy.context.selected_objects[0].name
        #print(">>>>> 762 current ref line name \"", currentRefLineName, "\"")

        
        # OBS! THE REFERENCE LINE MUST BE SELECTED IF IT EXISTS ALREADY IT IS!   
        colorSchemePrefix = "0" + str(colorUseFlag) + "_"
        #print("ccccc 1015 in drawFullLinesChryzode and currentRefLineName", currentRefLineName, "\n")
        for i in range(len(linesArrayGiven)):
            #self.look_for_dot_ref_lines_and_show_them(context, ">>>>> 772 BEFORE drawing EACH periphery line")
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[currentRefLineName].select_set(True)
            
            
            # FROM https://b3d.interplanety.org/en/how-to-set-object-mesh-to-active-in-blender-2-8-python-api/
            objs = context.window.scene.objects
            #print("?????? 1036 I have objects", objs[:])
            for obj in objs:
                if obj.name == currentRefLineName:
                    #print("????? 1039 in drawFullLinesChryzode and I have object", obj.name, "Do I have the right object?????", currentRefLineName)
                    context.view_layer.objects.active = obj
                    break
            
            bpy.context.scene.cursor.location=(0, 0, 0)
            # Get a copy of the selected reference line for next chryzode line
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0)})
            # Build prefixes for name
            prefixes = self.buildPrefixesForNameForChryzode(context, numPointsGiven, linesArrayGiven[i])
            zeroPrefix = prefixes[0]
            zeroPrefixFrom = prefixes[1]
            zeroPrefixTo = prefixes[2]
            # Assign name
            context.object.name = lineSetPrefix + colorSchemePrefix + "L__" + zeroPrefix + str(numPointsGiven) + "_" + zeroPrefixFrom + str(linesArrayGiven[i][0]) + "_" +  zeroPrefixTo + str(linesArrayGiven[i][0])
            #print("RRRRR 790 i:", i, "object name AFTER RENAMING", context.object.name)
            # AT THIS POINT WE HAVE THE RIGHT NAME for a periph line: AA_BB_L_CC_1p_DD_EE
            
            # Place line where it has to be on the Z = 0 plane
            context.object.location[0] = points[linesArrayGiven[i][0]][0]
            context.object.location[1] = points[linesArrayGiven[i][0]][1]
            
            # Place line on Z axis so that the levels is in ascending order (Lower levels on top)
            if context.scene.chryzoid_properties.pos_z == True:
                context.object.location[2] = (numPointsGiven - 3) * context.scene.chryzoid_properties.z
                
            # Place line on Z axis so that the levels is in descending order (Higher levels on top)
            if context.scene.chryzoid_properties.pos_z == False:
                context.object.location[2] = (numPointsGiven - 3) * -context.scene.chryzoid_properties.z
            
            
            # Resize
            context.object.scale[0] = sidesLen[linesArrayGiven[i][1] - linesArrayGiven[i][0]]

            # Rotate the line by the right amount in Z axis for lines for chryzode
            #ang = (theta0 + i * (tau / numPointsGiven) + (j - i - 1) * (tau / (2 * numPointsGiven))) % tau
            ang = (theta0 + linesArrayGiven[i][0] * (tau / numPointsGiven) + (linesArrayGiven[i][1] - linesArrayGiven[i][0] - 1) * (tau / (2 * numPointsGiven))) % tau
            #ang = (theta0 + (linesArrayGiven[i][1] - linesArrayGiven[i][0]) * tau / numPointsGiven) % tau
            bpy.data.objects[context.object.name].rotation_euler[2] = ang
            #print("ccccc 1065 i:", i, "drawing line for", linesArrayGiven[i], " point factor [1] - [0]", (linesArrayGiven[i][1] - linesArrayGiven[i][0]), "chryzode angle for points", numPointsGiven, "(theta0", round(theta0 * 360 / tau), "\b):", round(ang * 360 / tau))
    #### END OF DRAW FULL LINES CHRYZODE FUNCTION

    ##### START OF REMOVE DUPLICATES FROM ARRAY
    def remove_duplicates(self, context, nums):
        for i in range (len(nums) - 1, 0, -1):
            if nums[i] == nums[i - 1]:
                del nums[i - 1]
        return nums
        ##### START OF REMOVE DUPLICATES FROM ARRAY

    ##### START OF BUILD LINES TO PLACE ARRAY FUNCTION
    def buildLinesToPlaceArray(self, context, numPointsGiven, multiplierGiven):
        linesArray = []
        for i in range(1, numPointsGiven + 1):
            linesArray.append([i % numPointsGiven, i * multiplierGiven % numPointsGiven])
        for i in range(len(linesArray)):
            if linesArray[i][1] < linesArray[i][0]:
                linesArray[i] = linesArray[i][::-1]
        #print("aaaaa 1086 Original Array", linesArray, "remove elements where both values are equal")
        new_array = []
        # reverse elements where second value is less than first value
        for i in range(len(linesArray)):
            if linesArray[i][0] != linesArray[i][1]:
                new_array.append(linesArray[i])
        #print("aaaaa 1080    Final Array", new_array, "reverse elements where second value is less than first value")
        # sort by first element
        new_array = sorted(new_array, key=lambda item: item[0])
        #print("aaaaa 1080    fInAl Array", new_array, "sort by first element")
        # remove duplicates
        new_array = self.remove_duplicates(context, new_array)
        #print("aaaaa 1098    FINAL Array", new_array, "remove duplicates")
        return new_array
    ##### END OF BUILD LINES TO PLACE ARRAY FUNCTION
            
    ##### START OF DO CHRYZODE FUNCTION
    def doChryzode(self, context, numPointsGiven, multiplierGiven, colorSchemeGiven):
        colorUseFlag = colorSchemeGiven
        #print("ccccc 1084 in doChry-zode and num", numPointsGiven, " and mult", multiplierGiven, " color use flag DOES NOT UPDATE FIX  IT ASDF", colorUseFlag, "")
        #print("ccccc 1085 in doChry-zode and calling populate")
        populatePointsAndLineLengths(context, numPointsGiven)
        linesArray = self.buildLinesToPlaceArray(context, numPointsGiven, multiplierGiven)
        #print("ccccc 1088 in doChry-zode and calling self.drawFullLines and linesArray\n", linesArray)
        self.drawFullLinesChryzode(context, numPointsGiven, linesArray) # DRAW LINES AFTER THEY HAVE BEEN SCALED. OBS IT CALLS build RefLine!
    ##### END OF DO CHRYZODE FUNCTION

    ##### END OF APPLY MATERIALS TO LINES FOR CHRYZODE FUNCTION
    def applyMaterialsToLinesChryzode(self, context, em_matGiven):
        #print("AAAAA 1163 in apply mats to lines for chryzode")
        
        global lineSetPrefix
        # get color scheme, though for chryzode, we use only ONE and RANDOM
        colSchemeForLine = int(colorSchemePrefix[0:2])
        
        scene = context.scene
        colorMode_props = scene.colorMode_properties
        
        # Get a list of the lines to apply materials to
        zodeLinesONE = []
        zodeLinesRANDOM = []
        for obj in bpy.data.objects:
            if obj.name.find("00_L__") != -1:
                zodeLinesONE.append(obj)
            elif obj.name.find("L__") != -1:
                zodeLinesRANDOM.append(obj)
        #print("GGGGG 1152 I have the following", len(zodeLinesONE), "zode lines ONE") #, zodeLinesONE)
        #print("GGGGG 1153 I have the following", len(zodeLinesRANDOM), " zode lines RANDOM") #, zodeLinesRANDOM)
        for line in zodeLinesONE:
            line.data.materials.clear()
            line.data.materials.append(em_matGiven[0])
        for line in zodeLinesRANDOM:
            line.data.materials.clear()
            line.data.materials.append(em_matGiven[random.randint(0, len(em_matGiven) - 1)])
    ##### END OF APPLY MATERIALS TO LINES FOR CHRYZODE FUNCTION

    def execute(self, context):

        global currentRefLineName
        global colorUseFlag
        global COLORSCHEMES
        global levelsLogForMaterials
        global lineSetPrefix
        global lineSetNumber
        
        layout = self.layout
        scene = context.scene
        refline_props = scene.refline_properties
        chryzoid_props = scene.chryzoid_properties
        chryzode_props = scene.chryzode_properties
        colorMode_props = scene.colorMode_properties
        clearLines_props = scene.clearLines_properties

        #os.system("cls")
        timenow = time.time()
        print("\nccccc 1209 At start of execute CHRYZODE at", timenow, "and # of Points:", context.scene.chryzode_properties.numPoints, "and multiplier:", context.scene.chryzode_properties.multiplier)
        #print("rrrrrrrrrrrr 1138 currentRefLineName", currentRefLineName)
        
        # Remove old lines if necessary
        if clearLines_props.clearLinesBool == True:
            removeOldLines(context, "Chryzode")
            
        # Purge materials
        # Moved the function out so that chryzode also can use it
        #print("ccccc 1112 purging old materials for chryzode")
        purgeOldMaterials(context)
        emission_mat = []
        createShaders(context, emission_mat)
        # NOT NEEDED in chryzode: levelsLogForMaterials = [] # Reset the levels log for materials
        if colorMode_props.colorModeEnum == 'ONE':
            colorUseFlag = COLORSCHEMES[ONE]
        if colorMode_props.colorModeEnum == 'RANDOM':
            colorUseFlag = COLORSCHEMES[RANDOM]
        if colorMode_props.colorModeEnum == 'SERIAL':
            colorUseFlag = COLORSCHEMES[SERIAL]
        if colorMode_props.colorModeEnum == 'LEVEL':
            colorUseFlag = COLORSCHEMES[LEVEL]
        if colorMode_props.colorModeEnum == 'POINT':
            colorUseFlag = COLORSCHEMES[POINT]

        # Get the prefix of the lines, that is the "XX_" that is before "L_"
        # The XX_ is there for all lines of one run to differentiate them from another run
        # to avoid ending with ".001" and so on on the next run
        lineSetPrefix = "00_"
        lineSetNumber = 0
        foundLinePrefix = False
        lineNameFound = ""
        lineSetNumberPadding = ""

        # set lineSetNumber to the next value if applicable for chryzode
        for j in range(len(bpy.data.objects)):
            if bpy.data.objects[j].name.find("L__") != -1:
                lineSetNumber = int(bpy.data.objects[j].name[:2]) + 1
                lineNameFound = bpy.data.objects[j].name
                foundLinePrefix = True
        if lineSetNumber < 10:
            lineSetNumberPadding = "0"
        lineSetPrefix = lineSetNumberPadding + str(lineSetNumber) + "_"

        self.doChryzode(context, context.scene.chryzode_properties.numPoints, context.scene.chryzode_properties.multiplier, colorUseFlag)

        self.applyMaterialsToLinesChryzode(context, emission_mat)
        
        selectObjectByName(context, context.scene.prop)
        #print("ccccc 1258 I selected", context.scene.prop, "with select by name function")
        #print("ccccc 1259 7I pick this line NOPE FIX IT ASDF", refline_props.refLineEnum)
        print("ccccc 1260 At end of execute CHRYZODE")
        return {'FINISHED'}
    #### END OF EXECUTE FOR CHRYZODE
#### end of chryzode_operator


# I wanted to call it deleteLine and it did not accept it!
class chryzo2_operator(bpy.types.Operator):
    bl_label = "Operator"
    bl_idname = "chryzo2.operator"
    
    def execute(self, context):
        #os.system("cls")
        timenow = time.time()
        print("-----> CCCCC 1075 removing old chryzoid lines from chryzo2_operator")
        scene = context.scene
        refline_props = scene.refline_properties
        chryzoid_props = scene.chryzoid_properties
        chryzode_props = scene.chryzode_properties
        lines = []
        for i in range(len(bpy.data.objects)):
            if (bpy.data.objects[i].name.find("_1p_") != -1 or bpy.data.objects[i].name.find("_2i_") != -1 or bpy.data.objects[i].name.find("_L__") != -1) :
                lines.append(bpy.data.objects[i])
        #print("I got lines", lines)
        for obj in lines:
            bpy.data.objects.remove(obj, do_unlink=True)

        return {'FINISHED'}
#### end of chryzoid2_operator

       
#### build_refline_operator
class chryzo3_operator(bpy.types.Operator):
    bl_label = "Operator"
    bl_idname = "chryzo3.operator"
    
    def execute(self, context):
        lines_to_unlink = []

        chryzoid_operator.buildRefLineFromCube(self, context)
        for obj in bpy.context.scene.collection.objects:
            if obj.name.find("ReferenceLine") != -1:
                obj.name = obj.name.replace("ReferenceLine", "ReferenceLineNew")
        bpy.ops.object.editmode_toggle()
        coll_from = bpy.context.scene.collection
        coll_to = bpy.data.collections['Collection']
        for obj in bpy.context.scene.collection.objects:
            if obj.name.find("ReferenceLine") != -1:
                lines_to_unlink.append(obj)
        for obj in lines_to_unlink:
            coll_to.objects.link(obj)
        for obj in lines_to_unlink:
            coll_from.objects.unlink(obj)

        return {'FINISHED'}
#### end of build_refline_operator

#### start clearConsole_operator
class chryzo4_operator(bpy.types.Operator):
    bl_label = "Operator"
    bl_idname = "chryzo4.operator"
    
    def execute(self, context):
        os.system("cls")
        return {'FINISHED'}
#### end of clearConsole_operator
    
#classes = [RefLineProperties, ColorModeProperties, ClearLinesProperties, ChryzoidProperties, ChryzodeProperties, ChryzoidPanel, ChryzodePanel, chryzoid_operator, chryzode_operator, chryzode2_operator]#, deleteLines_operator]

classes = [RefLineProperties, ColorModeProperties, ClearLinesProperties, ChryzoidProperties, ChryzodeProperties, ChryzoidPanel, chryzoid_operator, chryzode_operator, chryzo2_operator, chryzo3_operator, chryzo4_operator]#, deleteLines_operator]

def register():
    for clas in classes:
        bpy.utils.register_class(clas)

    bpy.types.Scene.refline_properties = bpy.props.PointerProperty(type = RefLineProperties)
    bpy.types.Scene.colorMode_properties = bpy.props.PointerProperty(type = ColorModeProperties)
    bpy.types.Scene.clearLines_properties = bpy.props.PointerProperty(type = ClearLinesProperties)
    bpy.types.Scene.chryzoid_properties = bpy.props.PointerProperty(type = ChryzoidProperties)
    bpy.types.Scene.chryzode_properties = bpy.props.PointerProperty(type = ChryzodeProperties)
    bpy.types.Scene.prop = bpy.props.EnumProperty(name="", items=items_prop, update=update_prop)


def unregister():
    for clas in classes:
        bpy.utils.unregister_class(clas)
    del bpy.types.Scene.refline_properties
    del bpy.types.Scene.colorMode_properties
    del bpy.types.Scene.chryzoid_properties
    del bpy.types.Scene.chryzode_properties
    del bpy.types.Scene.prop

def __init__(self):
    mats = bpy.data.materials

if __name__ == "__main__":
    register()
    #print("I am doing it on __name__ etc")
    #chryzoid_operator.execute(bpy.context)
