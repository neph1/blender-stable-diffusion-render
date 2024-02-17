from abc import ABC
import os
import io
import base64
from PIL import Image

class ImageGeneratorBase(ABC):

    def __init__(self, endpoint: str, address: str = 'localhost', port: int = 7860) -> None:
        self.address = address
        self.port = port
        self.url = f"http://{self.address}:{self.port}{endpoint}"

    def convert_image(self, image_data: bytes, output_folder: str, image_name):
        try:
            decoded_data = base64.b64decode(image_data)
            # Further processing with the decoded data
        except base64.binascii.Error as e:
            print("Error decoding base64 data:", e)
        image = Image.open(io.BytesIO(decoded_data))
        path = os.path.join(output_folder, image_name + '.png')
        image.save(path)
