
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
    sampler: StringProperty(
        name="Sampler",
        description="Sampler for the model",
        default="Euler a"
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

        layout.prop(generate_image_properties, "prompt")
        layout.prop(generate_image_properties, "negative_prompt")
        layout.prop(generate_image_properties, "seed")
        layout.prop(generate_image_properties, "sampler")
        layout.prop(generate_image_properties, "steps")
        layout.prop(generate_image_properties, "cfg_scale")
        layout.prop(generate_image_properties, "width")
        layout.prop(generate_image_properties, "height")
        layout.prop(generate_image_properties, "cn_weight")
        layout.prop(generate_image_properties, "cn_guidance")
        layout.prop(generate_image_properties, "sd_address")
        layout.prop(generate_image_properties, "sd_port")
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
