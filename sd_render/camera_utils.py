import bpy

def render_viewport(image_size):
    bpy.context.scene.render.resolution_x = image_size
    bpy.context.scene.render.resolution_y = image_size
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    
    outputPath = "/tmp/viewer_node.png"  # Set the desired output path
    bpy.data.images["Viewer Node"].save_render(outputPath)
    return bpy.data.images["Viewer Node"]


def project_uvs(obj):
    bpy.context.active_object.select_set(False)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode = 'EDIT')
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    with bpy.context.temp_override(area=area, region=region, edit_object=bpy.context.edit_object):
                        bpy.ops.uv.project_from_view(correct_aspect=True, camera_bounds=True)
    bpy.ops.object.mode_set(mode = 'OBJECT')

