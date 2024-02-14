
bl_info = {
    "name": "Stable Diffusion Render and Bake",
    "author": "Rickard Edén",
    "version": (1, 0, 0),
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
    importlib.reload(base_gen)
    importlib.reload(automatic111)
    importlib.reload(image_utils)
    importlib.reload(camera_utils)
else:
    import base64
    import numpy

import bpy

from sd_render import generate_texture

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

    samplers = [
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
                           items=samplers, 
                           description="Sampler for the model",
                           default='Euler a')

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
    material_slot: StringProperty(
        name="Material slot",
        description="Material slot in target object",
        default="7860"
    )
    texture_slot: StringProperty(
        name="Texture slot",
        description="Texture slot in material slot",
        default="7860"
    )
    delete_projector: BoolProperty(
        name="Delete Projector",
        description="Delete the median object after baking",
        default=True
    )

class StableDiffusionRenderPanel(Panel):
    bl_label = "Stable Diffusion Render"
    bl_idname = "OBJECT_PT_generate_image"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        generate_image_properties = scene.sd_link_properties



        layout.label(text="Generation settings")
        layout.prop(generate_image_properties, "prompt")
        layout.prop(generate_image_properties, "negative_prompt")
        layout.prop(generate_image_properties, "seed")
        layout.prop(generate_image_properties, "sampler", text="Sampler")
        layout.prop(generate_image_properties, "steps")
        layout.prop(generate_image_properties, "cfg_scale")
        layout.prop(generate_image_properties, "width")
        layout.prop(generate_image_properties, "height")
        layout.prop(generate_image_properties, "cn_weight")
        layout.prop(generate_image_properties, "cn_guidance")
        layout.separator()
        layout.label(text="Backend settings")
        layout.prop(generate_image_properties, "sd_address")
        layout.prop(generate_image_properties, "sd_port")
        layout.separator()
        layout.label(text="Baking settings")
        layout.prop(generate_image_properties, "delete_projector")
        #layout.prop(generate_image_properties, "material_slot")
        #layout.prop(generate_image_properties, "texture_slot")

        col = self.layout.column(align=True)
        col.operator(RenderButton_operator.bl_idname, text="Render")

class RenderButton_operator(bpy.types.Operator):
    bl_idname = "sd_link.render_button"
    bl_label = "Render"

    def execute(self, context):
        result = generate_texture.execute()
        if result:
            self.report({'ERROR'}, result)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(StableDiffusionProperties)
    bpy.utils.register_class(RenderButton_operator)
    bpy.types.Scene.sd_link_properties = PointerProperty(type=StableDiffusionProperties)
    bpy.utils.register_class(StableDiffusionRenderPanel)

def unregister():
    bpy.utils.unregister_class(StableDiffusionProperties)
    bpy.utils.unregister_class(RenderButton_operator)
    bpy.utils.unregister_class(StableDiffusionRenderPanel)

if __name__ == "__main__":
    register()
