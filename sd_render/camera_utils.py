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
    view_params = save_viewport_position()
    bpy.context.active_object.select_set(False)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode = 'EDIT')
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    with bpy.context.temp_override(area=area, region=region, edit_object=bpy.context.edit_object):
                        #bpy.ops.view3d.view_camera()
                        bpy.ops.uv.project_from_view()
    bpy.ops.object.mode_set(mode = 'OBJECT')
    #apply_viewport_position(view_params)

def project_uv_from_active_camera(obj):
    active_camera = bpy.context.scene.camera
    
    if active_camera is None:
        print("No active camera found.")
        return
    
    bpy.context.view_layer.objects.active = obj
    bpy.context.scene.tool_settings.uv_texture_add_operator_projector = active_camera
    
    with bpy.context.temp_override(edit_object=bpy.context.edit_object):
        bpy.ops.uv.project_from_view(correct_aspect=True, camera_bounds=True)

""" 
Source:
https://b3d.interplanety.org/en/saving-and-restoring-the-3d-viewport-position/

"""
VIEWPORT_ATTRIBUTES = [
    'view_matrix', 'view_distance', 'view_perspective', 
    'use_box_clip', 'use_clip_planes', 'is_perspective',
    'show_sync_view', 'clip_planes'
]

def save_viewport_position():
    r3d = get_r3d()
    copy_if_possible = lambda x: x.copy() if hasattr(x, 'copy') else x
    data = {attr: copy_if_possible(getattr(r3d, attr)) for attr in VIEWPORT_ATTRIBUTES}
    return data

def apply_viewport_position(data):
    r3d = get_r3d()
    for attr in VIEWPORT_ATTRIBUTES:
        setattr(r3d, attr, data[attr])

def get_r3d():
    area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
    r3d = area.spaces[0].region_3d
    return r3d