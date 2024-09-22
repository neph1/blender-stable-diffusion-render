import base64
import json

import os
import random
import time

import requests
from .base_gen import ImageGeneratorBase

class ComfyUi(ImageGeneratorBase):
    """ Generating images using the COMFY_UI API (comfy-ui)"""

    sampler_id = "8"   
    
    def __init__(self, output_folder: str, address: str = '127.0.0.1', port: int = 8188, workflow: str = 'comfy_depth_workflow.json') -> None:
        super().__init__("/prompt", output_folder, address, port)
        self.workflow = workflow

    def generate_image(self, prompt: str, depth_map: str, negative_prompt: str = "text, watermark", seed: int = -1, sampler: str = "euler", steps: int = 30, cfg_scale: float = 7, width: int = 512, height: int = 512, cn_weight: float = 0.7, cn_guidance: float = 1, scheduler: str = '', model: str = '', cn_start: float = 0.0, cn_end: float = 1.0) -> str:
        """Generate an image from text."""
        image_data = self.send_request(prompt, depth_map, negative_prompt, seed, sampler, steps, cfg_scale, width, height, cn_weight, cn_guidance, scheduler, model, cn_start, cn_end)
        if not image_data:
            return None
        self.convert_image(image_data[0], "sd_output")
        return image_data


    def send_request(self, prompt, depth_map, negative_prompt: str, seed: int, sampler: str, steps: int, cfg_scale: int, width: int, height: int, cn_weight: float, cn_guidance: float, scheduler: str = '', model: str = '', cn_start: float = 1.0, cn_end: float = 1.0) -> bytes:

        path = self._load_workflow(self.workflow)
        with open(path) as f:
            workflow = json.load(f)

        image_name = self._upload_image(depth_map)

        if not image_name:
            print("Error uploading image.")
            return None
        
        if model:
            workflow = self.set_model(workflow, model)

        workflow = self._set_control_net(workflow, image_name, cn_weight, cn_guidance, cn_start, cn_end)
        workflow = self._set_text_prompts(workflow, prompt, negative_prompt)

        workflow = self._set_sampler(workflow, sampler, cfg_scale, seed, steps, scheduler)
        workflow = self._set_image_size(workflow, width, height)

        p = {"prompt": workflow}
        data = json.dumps(p)
        response = requests.post(self.url + self.generate_endpoint, json=p)
        if not response.status_code == 200:
            try:
                error_data = response.json()
                print("Error:")
                print(str(error_data))
                
            except json.JSONDecodeError:
                print(f"Error: Unable to parse JSON error data.")
            return None
        
        json_data = json.loads(response.content)
        prompt_id = json_data['prompt_id']
        while not self.poll_queue(prompt_id):
            # pause the thread for 1 second
            time.sleep(1)
            self.lock = False
        return self.get_history(prompt_id)
        
    def get_history(self, prompt_id: str):
        response = requests.get(f"{self.url}/history", data=prompt_id)
        if response.status_code == 200:
            history = json.loads(response.content)
            history = history[prompt_id]
            output_images = {}
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                if 'images' in node_output:
                    images_output = []
                    for image in node_output['images']:
                        image_data = self.get_image(image['filename'], image['subfolder'], image['type'])
                        images_output.append(image_data)
                    output_images[node_id] = images_output
            return output_images[node_id]

    def get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        headers = {"Content-Type": "image/png"}
        response = requests.get(f"{self.url}/view", params=data, headers=headers, stream=True)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
        
    def poll_queue(self, prompt_id: str):    
        """ Return True if the prompt is not in the queue, False otherwise."""
        response = requests.get(f"{self.url}/queue")
        if response.status_code == 200:
            json_data = json.loads(response.content)
            for prompt in json_data['queue_pending']:
                if prompt[1] == prompt_id:
                    return False
            for prompt in json_data['queue_running']:
                if prompt[1] == prompt_id:
                    return False
        return True
        
    def set_model(self, data: dict, model: str):
        data["4"]["inputs"]["ckpt_name"] = model
        return data
    
    def _load_workflow(self, workflow: str) -> dict:
        file_path = os.path.join(os.path.dirname(__file__) + '/../workflows/', workflow)
        return file_path
        
    def _set_text_prompts(self, data: dict, prompt: str, negative_prompt: str) -> dict:
        data["6"]["inputs"]["text"] = prompt
        data["7"]["inputs"]["text"] = negative_prompt
        return data
        
    def _set_sampler(self, data: dict, sampler: str, cfg: float, seed: int, steps: int, scheduler: str = '') -> dict:
        data["3"]["inputs"]["sampler_name"] = sampler.lower()
        data["3"]["inputs"]["cfg"] = cfg
        data["3"]["inputs"]["seed"] = random.randint(0, 18446744073709552000) if seed == -1 else seed
        print("seed", data["3"]["inputs"]["seed"])
        data["3"]["inputs"]["steps"] = steps
        if scheduler:
            data["3"]["inputs"]["scheduler"] = scheduler
        return data
    
    def _set_image_size(self, data: dict, width: int = 512, height: int = 512) -> dict:
        data["5"]["inputs"]["width"] = width
        data["5"]["inputs"]["height"] = height
        return data
    
    def _set_control_net(self, data:dict, depth_map: str, weight: float, guidance: float, start: float, end: float) -> dict:
        data["11"]["inputs"]["image"] = depth_map
        data["13"]["inputs"]["strength"] = weight
        data["13"]["inputs"]["start_percent"] = start
        data["13"]["inputs"]["end_percent"] = end
        return data
    
    def _upload_image(self, depth_map: str) -> str:
        with open(depth_map, 'rb') as file:
            files = {'image': file}
            data = {'type': 'input'}
            response = requests.post(f"{self.url}/upload/image", files=files, data=data)

            if response.status_code == 200:
                return json.loads(response.text)["name"]
            else:
                print(f"Error uploading image: {response.status_code}")
            return None