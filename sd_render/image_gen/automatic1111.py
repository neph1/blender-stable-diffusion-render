import os
import requests
import json
import base64

from .base_gen import ImageGeneratorBase

class Automatic1111(ImageGeneratorBase):
    """ Generating images using the AUTOMATIC1111 API (stable-diffusion-webui)"""


    def __init__(self, address: str = '127.0.0.1', port: int = 7860) -> None:
        super().__init__("/sdapi/v1/txt2img", address, port)

    def generate_image(self, prompt: str, depth_map: str, negative_prompt: str = "text, watermark", seed: int = 0, sampler: str = "Euler a", steps: int = 30, cfg_scale: int = 7, width: int = 512, height: int = 512, cn_weight: float = 0.7, cn_guidance: float = 1, scheduler: str = None) -> str:
        """Generate an image from text."""
        image_data = self.send_request(prompt, depth_map, negative_prompt, seed, sampler, steps, cfg_scale, width, height, cn_weight, cn_guidance)
        if not image_data:
            return None
        self.convert_image(image_data, "/tmp", "sd_output")
        return image_data


    def send_request(self, prompt, depth_map, negative_prompt: str, seed: int, sampler: str, steps: int, cfg_scale: int, width: int, height: int, cn_weight: float, cn_guidance: float) -> bytes:

        data = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "alwayson_scripts": {},
            "seed": seed,
            "sampler_index": sampler,
            "batch_size": 1,
            "n_iter": 1,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "restore_faces": False,
            "override_settings": {},
            "override_settings_restore_afterwards": True,
            "alwayson_scripts": {
                "ControlNet":{
                    "args": [
                        {
                            "input_image": depth_map,
                            "module": "none",
                            "model": "control_depth-fp16 [400750f6]",
                            "weight": cn_weight,
                            "guidance": cn_guidance,
                       }
                    ]
                },
            },
        }
        response = requests.post(self.url, json=data)
        if response.status_code == 200:
            json_data = json.loads(response.content)
            return json_data['images'][0]
        else:
            print(f"Error: {response.status_code}")
            return None
