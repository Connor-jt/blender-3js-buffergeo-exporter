
import bpy
import os
from bpy.types import Operator
from bpy.props import *

## //////////////////////////////////////////////////////////// ##
## CODE SOURCED FROM https://blender.stackexchange.com/a/42825 ##
## ////////////////////////////////////////////////////////// ##
# note: the code was doodoo, bing actually fixed it for me
class OpenBrowser(Operator):
    bl_idname = "open.browser"
    bl_label = "submit"
    # apparently we needed a colon here
    filepath: StringProperty(name="File Path", description="Filepath used for exporting the BufferGeometry", default= "")

    def execute(self, context):
        # ok now we can try and actually export it
        # CHECK TO SEE IF FILE EXISTS
        # IF NOT, THEN CREATE IT
        # ideally, we should create a file for each object
        adding_index = False
        if (len(bpy.data.objects) > 1):
            adding_index = True

        for obj in bpy.data.objects:
            # figure out the filename
            curr_filename = self.filepath
            if (adding_index): curr_filename += "_" + obj.name + ".js"
            export_mesh(obj.data, curr_filename, self)

        return {'FINISHED'}
    def invoke(self, context, event): 
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}  

def export_mesh(mesh, filename, self):
    # create a sub array
    out_verts = [0 for i in range(len(mesh.vertices) * 3)]
    tri_groups = {}

    # matching index is probably very important, so lets make sure we do that
    for vertex in mesh.vertices:
        index = vertex.index * 3
        out_verts[index  ] = vertex.co[0]
        out_verts[index+1] = vertex.co[1]
        out_verts[index+2] = vertex.co[2]
    # index for tris is not important, whats important is sorting them by material
    for face in mesh.polygons:
        # first test to see if the triangle count is correct
        if (len(face.vertices) != 3):
            self.report({'FAILURE'}, filename + " failed to export, non-triangle polygon found")
            return
        # figure out what tri goup to add this to
        tri_group = face.material_index
        # if the tri group isn't setup, set it up
        if (tri_group in tri_groups):
            tri_groups[tri_group].append(face.vertices[0])
            tri_groups[tri_group].append(face.vertices[1])
            tri_groups[tri_group].append(face.vertices[2])
        else:
            tri_groups[tri_group] = []
            tri_groups[tri_group].append(face.vertices[0])
            tri_groups[tri_group].append(face.vertices[1])
            tri_groups[tri_group].append(face.vertices[2])

    # now write out the stuff
    # if (os.path.exists(filename)): # apparently we dont need to check if its valid
    try:
        file = open(filename, 'w')

        file.write(str("const mesh_geo = new THREE.BufferGeometry();\n"))
        file.write(str("const mesh_verts = new Float32Array("))
        file.write(str(out_verts))
        file.write(str(");\n"))
        file.write(str("const mesh_indices = ["))
        # this was for debugging indexes
        # for key in tri_groups:
        #     file.write(str("\n// group: "+str(key)+"\n"))
        #     for tri in tri_groups[key]:
        #         file.write(str(tri) + str(", "))
        for key in tri_groups:
            for tri in tri_groups[key]:
                file.write(str(tri) + str(", "))

        file.write(str("];\n"))
        file.write(str("mesh_geo.setIndex(mesh_indices);\n"))
        file.write(str("mesh_geo.setAttribute('position', new THREE.BufferAttribute(mesh_verts, 3));\n"))
        
        vert_index = 0
        for key in tri_groups:
            vert_count = len(tri_groups[key])
            file.write(str("mesh_geo.addGroup("+str(vert_index)+", "+str(vert_count)+", "+str(key)+");\n"))
            vert_index += vert_count
    except:
        self.report({'FAILURE'}, filename + " failed to export, file error")
        return
    
    self.report({'INFO'}, filename + " was successfully exported")
    return



    


## /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// ##
## CODE SOURCED FROM https://github.com/Waffle1434/Mjolnir-Forge-Editor/blob/master/Blender%20(Download%20a%20Release,%20Not%20Me!)/forge.py#L244 ##
## ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// ##
# i believe we use this to store variables across sessions, so we can unregister UI and register it with the new code
# hence why we attmept to unregister before we do anything else
persist_vars = bpy.app.driver_namespace

class c_Export3BG(Operator):
    """Export meshes into Three.js BufferGeometry javascript"""
    bl_idname = 'buffergeo.export'
    bl_label = "Export as 3js BufferGeo"

    def invoke(self, context, event):
        return self.execute(context)
    def execute(self, context):
        self.report({'INFO'}, 'selecting location')
        bpy.ops.open.browser('INVOKE_DEFAULT')
        return { 'FINISHED'}
def export3BG(self, context): self.layout.operator(c_Export3BG.bl_idname, text="Three.js BufferGeometry (.js)")





def registerDrawEvent(event, item):
    id = event.bl_rna.name
    handles = persist_vars.get(id, [])
    event.append(item)
    handles.append(item)
    persist_vars[id] = handles
def removeDrawEvents(event):
    for item in persist_vars.get(event.bl_rna.name,[]):
        try: event.remove(item)
        except: pass

def register():
    bpy.utils.register_class(c_Export3BG)
    bpy.utils.register_class(OpenBrowser) 
    registerDrawEvent(bpy.types.TOPBAR_MT_file_export, export3BG)

def unregister():
    try: 
        bpy.utils.unregister_class(c_Export3BG)
        bpy.utils.unregister_class(OpenBrowser)
    except: pass
    removeDrawEvents(bpy.types.TOPBAR_MT_file_export)


try: unregister()
except: pass
register()
