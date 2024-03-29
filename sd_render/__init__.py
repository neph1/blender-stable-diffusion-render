
bl_info = {
    "name": "Stable Diffusion Render and Bake",
    "author": "Rickard Edén",
    "version": (1, 3, 0),
    "blender": (4, 0, 0),
    "location": "Render > Stable Diffusion Render (Create Tab)",
    "description": "Stable Diffusion Render and Bake",
    "warning": "",
    "doc_url": "https://github.com/neph1/blender-stable-diffusion-render",
    "category": "Render",
}

if "bpy" in locals():
    import importlib
    importlib.reload(base64)
    importlib.reload(numpy)
    importlib.reload(PIL)
    importlib.reload(base_gen)
    importlib.reload(automatic111)
    importlib.reload(image_utils)
    importlib.reload(camera_utils)
else:
    import base64
    import numpy
    import PIL

import bpy

from sd_render import generate_texture
import os

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       PropertyGroup,
                       )
class BackendSelector(bpy.types.AddonPreferences):
    bl_idname = __name__

    backend_enum: bpy.props.EnumProperty(
        name="backend",
        description="Select backend to use for rendering and baking",
        items=(
            ('Automatic1111', "Automatic1111", ""),
            ('ComfyUI', "ComfyUI", ""),
        ),
        default='Automatic1111'
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "backend_enum", text="Backend")

class StableDiffusionProperties(PropertyGroup):
    prompt: StringProperty(
        name="Prompt",
        description="Positive prompt",
        default=""
    )
    depth_map: StringProperty(
        name="Depth map",
        description="Base64 encoded image",
        default="viewer_node.png"
    )
    negative_prompt: StringProperty(
        name="Negative Prompt",
        description="Negative prompt",
        default="text, watermark"
    )
    seed: IntProperty(
        name="Seed",
        description="Seed for random number generator",
        default=-1
    )

    steps: IntProperty(
        name="Steps",
        description="Number of steps for generation",
        default=30
    )
    cfg_scale: IntProperty(
        name="CFG Scale",
        description="Scale of the CFG model",
        default=7
    )
    width: IntProperty(
        name="Width",
        description="Width of the generated image",
        default=512
    )
    height: IntProperty(
        name="Height",
        description="Height of the generated image",
        default=512
    )
    cn_weight: FloatProperty(
        name="CN Weight",
        description="Control net weight",
        default=0.7
    )
    cn_guidance: FloatProperty(
        name="CN Guidance",
        description="Control net guidance / strength",
        default=1
    )
    sd_address: StringProperty(
        name="Address",
        description="Address to SD backend",
        default="127.0.0.1"
    )
    sd_port: StringProperty(
        name="Port",
        description="Port to SD backend",
        default="7860"
    )
    delete_projector: BoolProperty(
        name="Delete Projector",
        description="Delete the median object after baking",
        default=True
    )
    model: StringProperty(
        name="Model",
        description="Model to use. Include file ending. Leave empty to use workflow default.",
        default=""
    )
    ref_image_width: IntProperty(
        name="Reference Image Width",
        description="Width of the reference image (depth map)",
        default=512
    )
    ref_image_height: IntProperty(
        name="Reference Image Height",
        description="Height of the reference image (depth map)",
        default=512
    )
    bake_texture: BoolProperty(
        name="Bake texture to object",
        description="Bake the generated image to the selected object",
        default=True
    )

class Automatic1111Properties(StableDiffusionProperties):
    auto1111_samplers = [
        ('Euler a', "Euler a", ""),
        ('Euler', "Euler", ""),
        ('LMS', "LMS", ""),
        ('Heun', "Heun", ""),
        ('DPM2', "DPM2", ""),
        ('DPM2 a', "DPM2 a", ""),
        ('DPM++ 2S a', "DPM++ 2S a", ""),
        ('DPM++ 2M', "DPM++ 2M", ""),
        ('DPM fast', "DPM fast", ""),
        ('DPM adaptive', "DPM adaptive", ""),
        ('LMS Karras', "LMS Karras", ""),
        ('DPM2 Karras', "DPM2 Karras", ""),
        ('DPM2 a Karras', "DPM2 a Karras", ""),
        ('DPM++ 2S a Karras', "DPM++ 2S a Karras", ""),
        ('DPM++ 2M Karras', "DPM++ 2M Karras", ""),
        ('DPM++ SDE Karras', "DPM++ SDE Karras", ""),
        ('DPM++ 2M SDE Karras', "DPM++ 2M SDE Karras", ""),
        ('DDIM', "DDIM", ""),
        ('PLMS', "PLMS", ""),
        ('UniPC', "UniPC", ""),

    ]

    sampler: EnumProperty(name="Sampler", 
                           items=auto1111_samplers, 
                           description="Sampler for the model",
                           default='Euler a')
    backend: StringProperty(name="backend", default="Automatic1111")

class ComfyUiProperties(StableDiffusionProperties):

    comfy_samplers = [
        ('euler', "euler", ""),
        ('euler_ancestral', "euler_ancestral", ""),
        ('heun', "heun", ""),
        ('dpm_2', "dpm_2", ""),
        ('dpm_2_ancestral', "dpm_2_ancestral", ""),
        ('lms', "lms", ""),
        ('dpm_fast', "dpm_fast", ""),
        ('dpm_adaptive', "dpm_adaptive", ""),
        ('dpmpp_2s_ancestral', "dpmpp_2s_ancestral", ""),
        ('dpmpp_sde', "dpmpp_sde", ""),
        ('dpmpp_sde_gpu', "dpmpp_sde_gpu", ""),
        ('dpmpp_2m', "dpmpp_2m", ""),
        ('dpmpp_2m_sde', "dpmpp_2m_sde", ""),
        ('dpmpp_2m_sde_gpu', "dpmpp_2m_sde_gpu", ""),
        ('dpmpp_3m_sde', "dpmpp_3m_sde", ""),
        ('dpmpp_3m_sde_gpu', "dpmpp_3m_sde_gpu", ""),
        ('ddim', "ddim", ""),
        ('uni_pc', "uni_pc", ""),
        ('uni_pc_bh2', "uni_pc_bh2", ""),

    ]
        
    workflows = [(file, file, "") for file in os.listdir(os.path.join(os.path.dirname(__file__), "workflows"))]

    workflow: EnumProperty(name="Workflow", 
                           items=workflows, 
                           description="Workflow to use",
                           default='comfy_depth_workflow.json')


    sampler: EnumProperty(name="Sampler", 
                           items=comfy_samplers, 
                           description="Sampler for the model",
                           default='euler')

    comfy_schedulers = [
        ('normal', "normal", "All"),
        ('karras', "karras", "SDE"),
        ('exponential', "exponential", "2M/3M"),
        ('sgm_uniform', "sgm_uniform", ""),
        ('simple', "simple", "All"),
        ('ddim_uniform', "ddim_uniform", "UniPC, DDIM"),
    ]


    scheduler: EnumProperty(name="Scheduler",
                            items=comfy_schedulers,
                            description="Scheduler for the model",
                            default='normal')
    backend: StringProperty(name="backend", default="ComfyUI")

class Automatic1111Settings(Panel):
    bl_label = "Stable Diffusion Render"
    bl_idname = "OBJECT_PT_generate_image"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        generate_image_properties = scene.sd_link_properties
        draw_generation_settings(layout, generate_image_properties)
        col = self.layout.column(align=True)
        col.operator(RenderButton_operator.bl_idname, text="Render")

class ComfyUiSettings(Panel):
    bl_label = "Stable Diffusion Render"
    bl_idname = "OBJECT_PT_generate_image"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        generate_image_properties = scene.sd_link_properties
        layout.prop(generate_image_properties, "workflow", text="Workflow")
        layout.prop(generate_image_properties, "scheduler", text="Scheduler")
        draw_generation_settings(layout, generate_image_properties)
        col = self.layout.column(align=True)
        col.operator(RenderButton_operator.bl_idname, text="Render")
    
    


def draw_generation_settings(layout, generate_image_properties):
    layout.prop(generate_image_properties, "sampler", text="Sampler")
    layout.prop(generate_image_properties, "prompt", expand=True)
    layout.prop(generate_image_properties, "negative_prompt", expand=True)
    layout.prop(generate_image_properties, "model")
    layout.prop(generate_image_properties, "seed")
    layout.prop(generate_image_properties, "steps")
    layout.prop(generate_image_properties, "cfg_scale")
    layout.prop(generate_image_properties, "width")
    layout.prop(generate_image_properties, "height")
    layout.prop(generate_image_properties, "cn_weight")
    layout.prop(generate_image_properties, "cn_guidance")
    layout.prop(generate_image_properties, "ref_image_width")
    layout.prop(generate_image_properties, "ref_image_height")
    layout.separator()
    layout.label(text="Backend settings")
    layout.prop(generate_image_properties, "sd_address")
    layout.prop(generate_image_properties, "sd_port")
    layout.separator()
    layout.label(text="Baking settings")
    layout.prop(generate_image_properties, "delete_projector")
    layout.prop(generate_image_properties, "bake_texture")


class RenderButton_operator(bpy.types.Operator):
    bl_idname = "sd_link.render_button"
    bl_label = "Render"

    def execute(self, context):
        result = generate_texture.execute()
        if result:
            self.report({'ERROR'}, result)
        return {'FINISHED'}
    
def update_options(context):
    preferences = context.preferences.addons[__name__].preferences

    if preferences.backend_enum == 'Automatic1111':
        bpy.utils.register_class(Automatic1111Properties)
        bpy.types.Scene.sd_link_properties = PointerProperty(type=Automatic1111Properties)
        bpy.utils.register_class(Automatic1111Settings)
    elif preferences.backend_enum == 'ComfyUI':
        bpy.utils.register_class(ComfyUiProperties)
        bpy.types.Scene.sd_link_properties = PointerProperty(type=ComfyUiProperties)
        bpy.utils.register_class(ComfyUiSettings)

def register():
    bpy.utils.register_class(RenderButton_operator)
    
    bpy.utils.register_class(BackendSelector)
    update_options(bpy.context)

def unregister():
    bpy.utils.unregister_class(RenderButton_operator)
    bpy.utils.unregister_class(BackendSelector)
    bpy.utils.unregister_class(Automatic1111Settings)
    bpy.utils.unregister_class(ComfyUiSettings)

if __name__ == "__main__":
    register()
