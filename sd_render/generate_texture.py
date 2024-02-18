import bpy
import logging
from sd_render.image_gen.comfy_ui import ComfyUi
from sd_render.image_gen.automatic1111 import Automatic1111
from sd_render.camera_utils import render_viewport, project_uvs, project_uv_from_active_camera
from sd_render.image_utils import bake_from_active, create_projector_object, set_projector_position_and_orientation, setup_projector_material, assign_material_to_projector, remove_projector

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

def generate(obj) -> str:
    props = bpy.context.scene.sd_link_properties
    image_size = 512
    rendered_image = render_viewport(image_size)

    if (props.backend == 'Automatic1111'):
        generator = Automatic1111(address=props.sd_address, port=props.sd_port)
        scheduler = None
    elif (props.backend == 'ComfyUI'):
        generator = ComfyUi(address=props.sd_address, port=props.sd_port)
        scheduler = props.scheduler
    else:
        return "Invalid backend selected."
    depth_map = '/tmp/viewer_node.png'
    #generated_path = "/tmp/sd_output.png"
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
                                             depth_map=depth_map,
                                             scheduler=scheduler)
    try:
        texture_image = bpy.data.images.load('/tmp/sd_output.png')
    except:
        return "Failed to generate texture."
    # bake_texture(obj, texture_image)
    
    target_object = obj
    
    bpy.context.active_object.select_set(False)
    
    projector = create_projector_object(target_object)
    bpy.context.view_layer.objects.active = projector
    set_projector_position_and_orientation(projector, target_object)
    projector_material = setup_projector_material(texture_image)
    assign_material_to_projector(projector, projector_material)
    
    project_uvs(projector)
    
    bake_from_active(projector, target_object, props.material_slot, props.texture_slot)
    
    if props.delete_projector:
        remove_projector(projector)

def execute():
    if len(bpy.context.selected_objects) > 0:
        obj = bpy.context.selected_objects[0]
        if obj.type == 'CAMERA':
            return "Cannot generate texture for camera. Please select an object."
        return generate(obj)
    else:
        return "No object selected. Please select an object."
