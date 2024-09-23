
import bpy

def create_projector_objects(obj_list):
    """Create projector objects for each object in the list"""
    projectors = dict()
    for obj in obj_list:
        obj_data = obj.data.copy()
        projector = bpy.data.objects.new(name=f"TextureProjector_{obj.name}", object_data=obj_data)
        projector.data.uv_layers.new(name="bake")
        bpy.context.collection.objects.link(projector)
        projectors[obj.name] = projector
    
    return projectors

def create_projector_object_from_list(obj_list):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.active_object.select_set(False)
    bpy.context.view_layer.objects.active = obj_list[0]
    for obj in obj_list:
        if obj.type == 'MESH':
            obj.select_set(True)
        bpy.ops.object.join()
    return obj_list[0]

def setup_projector_material(rendered_image):
    """Set up projector material with the rendered image"""
    projector_material = bpy.data.materials.new(name="TextureProjectorMaterial")
    projector_material.use_nodes = True
    projector_material.node_tree.nodes.clear()
    image_texture_node = projector_material.node_tree.nodes.new('ShaderNodeTexImage')
    image_texture_node.image = rendered_image
    output_node = projector_material.node_tree.nodes.new('ShaderNodeOutputMaterial')
    projector_material.node_tree.links.new(image_texture_node.outputs[0], output_node.inputs[0])
    return projector_material

def assign_material_to_projector(projector, projector_material):
    """Assign projector material to projector object"""
    if not projector.data.materials:
        projector.data.materials.append(projector_material)
    else:
        projector.data.materials[0] = projector_material

def set_projector_position_and_orientation(projector, target_object):
    """Set projector position and orientation"""
    projector.location = target_object.location
    projector.rotation_euler = target_object.rotation_euler

def bake_from_active(projector, target_object):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.active_object.select_set(False)
    projector.select_set(True)
    target_object.select_set(True)
    bpy.context.view_layer.objects.active = target_object
    bpy.context.scene.render.bake.use_selected_to_active = True
    print("Baking to object", target_object.name)
    bpy.ops.object.bake(type='COMBINED', use_clear=True, cage_extrusion=0.1)
    projector.select_set(False)
    target_object.select_set(False)
    
def remove_projector(projector):
    bpy.data.materials.remove(projector.data.materials[0])
    bpy.data.objects.remove(projector)

def move_unselected_faces(selected_object, delta_x):
    bpy.ops.object.mode_set(mode='EDIT')
    mesh = selected_object.data
    
    selected_faces = [f.index for f in mesh.polygons if f.select]
    
    # Iterate through the UV coordinates of unselected faces
    for face_index, face in enumerate(mesh.polygons):
        if face.index not in selected_faces:
            for loop_index in face.loop_indices:
                uv_coord = mesh.uv_layers.active.data[loop_index].uv
                uv_coord.x += delta_x
    mesh.update()
    bpy.ops.object.mode_set(mode = 'OBJECT')
