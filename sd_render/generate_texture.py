import bpy
import logging
from sd_render.image_gen.comfy_ui import ComfyUi
from sd_render.image_gen.automatic1111 import Automatic1111
from sd_render.camera_utils import render_viewport, project_uvs
from sd_render.image_utils import bake_from_active, create_projector_objects, set_projector_position_and_orientation, setup_projector_material, assign_material_to_projector, remove_projector, create_projector_object_from_list

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

def render(props):
    output_folder = bpy.context.scene.render.filepath
    rendered_image = render_viewport(props.ref_image_width, props.ref_image_height, output_folder)
    print("Output folder:", output_folder)
    if (props.backend == 'Automatic1111'):
        generator = Automatic1111(address=props.sd_address, port=props.sd_port, output_folder=output_folder)
        scheduler = None
    elif (props.backend == 'ComfyUI'):
        generator = ComfyUi(address=props.sd_address, port=props.sd_port, output_folder=output_folder, workflow=props.workflow)
        scheduler = props.scheduler
    else:
        return "Invalid backend selected."
    depth_map = f'{output_folder}/viewer_node.png'
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
                                             scheduler=scheduler,
                                             model=props.model)
    try:
        return bpy.data.images.load(f'{output_folder}/sd_output.png')
    except:
        return "Failed to generate texture."


def bake(selected_objects, texture_image, delete_projector: bool) -> str:
    
    bpy.context.active_object.select_set(False)
    
    projectors = create_projector_objects(selected_objects)
    # projector = create_projector_object_from_list(projectors)
    for object in selected_objects:

        if object.type == 'CAMERA':
            continue
        projector = projectors[object.name]
        bpy.context.view_layer.objects.active = projector
        set_projector_position_and_orientation(projector, object)
        projector_material = setup_projector_material(texture_image)
        assign_material_to_projector(projector, projector_material)
        bpy.ops.object.mode_set(mode = 'OBJECT')
        project_uvs(projector)
    
        bake_from_active(projector, object)

        if delete_projector:
            remove_projector(projector)
        
    for object in selected_objects:
        object.select_set(True)

def execute():
    props = bpy.context.scene.sd_link_properties
    if len(bpy.context.selected_objects) == 0 and props.bake_texture:
        return "No object selected. Please select an object."
    
    texture_image = render(props)
    if isinstance(texture_image, str):
        return texture_image # Error message
    
    selected_objects = None
    if props.bake_texture:
        selected_objects = bpy.context.selected_objects
        return bake(selected_objects, texture_image=texture_image, delete_projector=props.delete_projector)
    return ''

