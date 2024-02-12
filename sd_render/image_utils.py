import bpy
import numpy as np

def get_camera_matrix():
  """
  Retrieves the projection matrix of the active camera.

  Returns:
      numpy.array: The camera's projection matrix.
  """
  camera_data = bpy.context.scene.camera
  camera_matrix = np.array(camera_data.matrix_world).reshape(4, 4)
  return camera_matrix

def get_object_matrix(obj):
  """
  Retrieves the transformation matrix of the given object.

  Args:
      obj: The object for which to get the transformation matrix.

  Returns:
      numpy.array: The object's transformation matrix.
  """
  object_matrix = np.array(obj.matrix_world).reshape(4, 4)
  return object_matrix

def transform_texture(texture_data, camera_matrix, object_matrix):
  """
  Transforms the texture data from camera space to UV space.

  Args:
      texture_data: The texture data as a NumPy array.
      camera_matrix: The camera's projection matrix.
      object_matrix: The object's transformation matrix.

  Returns:
      numpy.array: The transformed texture data.
  """
  inv_camera_matrix = np.linalg.inv(camera_matrix)
  combined_matrix = inv_camera_matrix @ object_matrix
  transformed_data = texture_data.dot(combined_matrix.T)
  return transformed_data

def load_rendered_image():
    """Load the rendered image"""
    rendered_image_path = bpy.context.scene.render.filepath
    rendered_image = bpy.data.images.load(rendered_image_path)
    return rendered_image

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

def project_texture_onto_uv_map(target_object):
    """Project the texture onto the UV map"""
    bpy.context.view_layer.objects.active = target_object
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.project_from_view()
    bpy.ops.object.mode_set(mode='OBJECT')

def capture_projected_texture(projector, rendered_image):
    """Capture the projected texture"""
    bpy.context.active_object.select_set(False)
    projected_texture = bpy.data.images.new(name="ProjectedTexture", width=rendered_image.size[0], height=rendered_image.size[1])
    projector.select_set(True)
    bpy.context.view_layer.objects.active = projector
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'})
    projected_texture.filepath_raw = "/tmp/projected_texture.png"
    projected_texture.file_format = 'PNG'
    projected_texture.save()
    return projected_texture

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
