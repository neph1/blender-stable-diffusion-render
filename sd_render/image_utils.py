import bpy
import numpy as np


def create_projector_object(obj):
    """Create a projector object"""
    obj_data = obj.data.copy()
    projector = bpy.data.objects.new(name="TextureProjector", object_data=obj_data)
    projector.data.uv_layers.remove(projector.data.uv_layers[0])
    projector.data.uv_layers.new(name="bake")
    bpy.context.collection.objects.link(projector)
    return projector

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
    bpy.context.active_object.select_set(False)
    bpy.context.view_layer.objects.active = target_object
    projector.select_set(True)
    #bpy.context.view_layer.objects.active = target_object
    target_object.data.uv_layers.active = target_object.data.uv_layers[0]
    bpy.context.scene.render.bake.use_selected_to_active = True
    bpy.ops.object.bake(type='COMBINED', use_clear=True, cage_extrusion=0.1)
    
def remove_projector(projector):
    bpy.data.materials.remove(projector.data.materials[0])
    bpy.data.objects.remove(projector)
