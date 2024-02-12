import bpy
import io
import sys
import numpy as np
from sd_render.image_gen.automatic1111 import Automatic1111
from sd_render.camera_utils import *
from sd_render.image_utils import *

def generate(obj):
    image_size = 512
    rendered_image = render_viewport(image_size)
    bytes = bytearray()
    #for value in rendered_image.pixels:
    #    bytes.append(int(max([0, min([255, value * 255])])))
    #image_bytes = np.array(bytes, dtype=np.uint8)
    
    generator = Automatic1111()
    depth_map = '/tmp/viewer_node.png'
    props = bpy.context.scene.sd_link_properties
    #generated_path = "/tmp/sd_output.png"  # Set the path to your texture image
    generated_path = generator.generate_image(prompt=props.prompt,
                                              negative_prompt=props.negative_prompt,
                                              seed=props.seed,
                                              sampler=props.sampler,
                                              steps=props.steps,
                                              cfg_scale=props.cfg_scale,
                                              width=props.width,
                                              height=props.height,
                                              cn_weight=props.cn_weight,
                                              cn_guidance=props.cn_guidance,
                                              depth_map=depth_map)
    if generated_path:
        texture_image = bpy.data.images.load('/tmp/sd_output.png')
    else:
        print("Error: Generation failed.")
    
    project_from_view = False
    
    if project_from_view:
        project_uvs(obj)
    
    # bake_texture(obj, texture_image)
    
    target_object = obj
    
    bpy.context.active_object.select_set(False)
    
    projector = create_projector_object(target_object)
    bpy.context.view_layer.objects.active = projector
    set_projector_position_and_orientation(projector, target_object)
    projector_material = setup_projector_material(texture_image)
    assign_material_to_projector(projector, projector_material)
    
    project_uvs(projector)
    
    bake_from_active(projector, target_object)
    
    remove_projector(projector)

def execute():
    if len(bpy.context.selected_objects) > 0:
        obj = bpy.context.selected_objects[0]
        generate(obj)
    else:
        print("Error: No object selected. Please select an object.")
