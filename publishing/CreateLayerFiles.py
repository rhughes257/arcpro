import os
import arcpy
from arcpy import env

"""
Before running this tool, run the create_directories tool to build the folder structure for the geodatabase.

Use this tool to create initial layer files for each feature class in the input geodatabase

1.  Only if the feature class is populated with features
2.  An existing layer is NOT overwritten

"""
masterGDB = arcpy.GetParameterAsText(0)
# masterGDB = r"C:\ESRI_WORK_FOLDER\rtaa\MasterGDB\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"
outfolder = arcpy.GetParameterAsText(1)
# outfolder = r"C:\ESRI_WORK_FOLDER\rtaa\layers"

env.workspace = masterGDB
datasets = arcpy.ListDatasets()
for d in datasets:
    env.workspace = os.path.join(masterGDB, d)
    fclist = arcpy.ListFeatureClasses()
    dfolder = os.path.join(outfolder, d)
    for fc in fclist:
        i = 0
        with arcpy.da.SearchCursor(fc, "*") as cursor:
            for row in cursor:
                i += 1
        if i:
            layer_name = fc[0]
            for x in fc[1:]:
                # camelCased feature class names are split using the underscore
                if x.isupper():
                    layer_name += "_{}".format(x)
                else:
                    layer_name += x
            # if there are exceptions to this where feature class names are incorrectly camelCased they must be
            # specified here
            if layer_name == "Easements_And_Rightsof_Way":
                layer_name = "Easements_and_Rights_of_Way"

            outlayer = arcpy.MakeFeatureLayer_management(fc, layer_name)
            outpath = os.path.join(dfolder, "{}.lyrx".format(layer_name))

            if not os.path.exists(outpath):
                arcpy.SaveToLayerFile_management(outlayer, outpath)
                if arcpy.Exists(outpath):
                    arcpy.AddMessage("Layer {}.lyrx was created".format(layer_name))
                else:
                    arcpy.AddError("Layer {}.lyrx failed to be created".format(layer_name))
            else:
                arcpy.AddMessage("Layer {}.lyrx already exists".format(layer_name))

            arcpy.Delete_management(outlayer)
        else:
            arcpy.AddMessage("Feature Class {} is empty.  No layer created".format(fc))
