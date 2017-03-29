# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2016
#
# ##### END LICENSE BLOCK #####

import time, struct, math
import os.path as path

import bpy, bmesh, mathutils


######################################################
# EXPORT HELPERS
######################################################

######################################################
# EXPORT MAIN FILES
######################################################

def save_prm_file(file, ob):
    scn = bpy.context.scene
    
    # get mesh name
    mesh = ob.data

    # create bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # list of faces and vertices
    faces = list(bm.faces)
    vertices = list(bm.verts)

    poly_count = len(faces)
    vertex_count = len(vertices)

    # write amount of polygons and vertices
    file.write(struct.pack("<hh", poly_count, vertex_count))

    # get layers
    uv_layer = bm.loops.layers.uv.active
    vc_layer = bm.loops.layers.color.get("color")
    va_layer = bm.loops.layers.color.get("alpha")
    flag_layer = bm.faces.layers.int.get("flags")

    # go through all polygons
    for poly in range(poly_count):
      bm.faces.ensure_lookup_table() # apparently needed now? blender sometimes prompts to call the function
      face = faces[poly]

      # figure out whether the face is quad
      is_quad = 1 if len(face.verts) > 3 else 0
      
      # get the flag layer (bit field)
      face_flags = face[flag_layer]

      # set the quad-flag if the poly is quadratic
      if is_quad:
        face_flags |= 0x001

      # write the flags
      file.write(struct.pack("<h", face_flags))

      # write the texture
      file.write(struct.pack("<h", 0))

      # write the vertex indices
      vert_order = [2, 1, 0, 3] if not is_quad else [3, 2, 1, 0]
      for i in vert_order:
        if i < len(face.verts):
          file.write(struct.pack("<h", vertices.index(face.verts[i])))
        else:
          file.write(struct.pack("<h", 0))

      # write the vertex colors
      for i in vert_order:
        if i < len(face.verts):
          color = face.loops[i][vc_layer]
          alpha = face.loops[i][va_layer]
          file.write(struct.pack("<BBBB", int(color.b * 255), int(color.g * 255), int(color.r * 255), int(alpha.v * 255)))
        else:
          file.write(struct.pack("<BBBB", 1, 1, 1, 1)) # write opaque white as default

      # write the uv
      for i in vert_order:
        if i < len(face.verts):
          uv = face.loops[i][uv_layer].uv
          file.write(struct.pack("<ff", uv[0], 1 - uv[1]))
        else:
          file.write(struct.pack("<ff", 0, 0))

    # export vertex positions and normals
    for v in range(vertex_count):
      vertex = vertices[v]
      coord = mathutils.Vector((vertex.co[0]*100, vertex.co[2]*-100, vertex.co[1]*100))
      normal = mathutils.Vector((vertex.normal[0], vertex.normal[1], vertex.normal[2]))
      file.write(struct.pack("<fff", coord[0], coord[1], coord[2]))
      file.write(struct.pack("<fff", normal[0], normal[1], normal[2]))

    # free the bmesh
    bm.free()



######################################################
# EXPORT
######################################################
def save_prm(filepath,
             context):


    time1 = time.clock()

    ob = bpy.context.selected_objects[0]
    print("exporting PRM: {} as {}...".format(str(ob), filepath))

    # write prm
    file = open(filepath, 'wb')
    save_prm_file(file, ob)
    file.close()

      
    # prm export complete
    print(" done in %.4f sec." % (time.clock() - time1))


def save(operator,
         context,
         filepath="",

         ):
  
    
    # save BND
    save_prm(filepath,
             context
             )

    return {'FINISHED'}