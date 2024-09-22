# blender-stable-diffusion-render
A Blender addon for using Stable Diffusion to render texture bakes for objects.

![examples](https://github.com/neph1/blender-stable-diffusion-render/assets/7988802/8f22d031-5f5d-47e9-a0c2-dd9dde0a0a4c)

![scene example](https://github.com/user-attachments/assets/3309579f-03b8-4a0d-ad20-983eaacaba89)


It will retain your existing UV coords and bake the result to them.

Supports both Automatic1111 and ComfyUI backends

Limitations: The intermediate object has its uv's projected from the view. So even though the result will be mapped 'around' the object, it won't render what isn't seen. Currently doesn't take subdivisions into consideration for the baking.

Multiple objects since [v1.5.0](https://github.com/neph1/blender-stable-diffusion-render/releases/tag/v1.5.0)

Example video: https://youtu.be/_VmOCM1rY7g
More complex example: https://youtu.be/TsxcImL1cCk

Why use this method?

1. Control. This is probably even quicker than sketching in a 2D program
2. Post processing. Use your textured objects as part of a scene, animate them, light them, put them in a stew.

Is this cheating?

Maybe. And if so, it's a good thing. Some inspiration:

Ian Hubert on World Building in Blender:
https://youtu.be/whPWKecazgM

Steps:

1. Download the 'sd_render' folder and install it as an addon.

2. Add a material to your object

3. Unwrap the UV map.

4. Set up a viewer node and render depth. Save result

5. Adjust the camera to maximize rendered area and for optimal projection (No longer needs to align with viewport)

6. Select object and hit "Render" in the "Stable Diffusion Render" panel in the "Render" tab

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/T6T3S8VXY)

![Screenshot from 2024-02-12 17-57-22](https://github.com/neph1/blender-stable-diffusion-render/assets/7988802/204b2d2a-2b5d-4575-84ac-e7625cd50b7d)

![Screenshot from 2024-02-12 17-57-42](https://github.com/neph1/blender-stable-diffusion-render/assets/7988802/5842777d-7029-4978-b043-6ba1e7005f8b)

![Screenshot from 2024-02-12 17-59-34](https://github.com/neph1/blender-stable-diffusion-render/assets/7988802/80ed6400-67af-4c0e-9b24-a16a846ce50a)


Switching backend:
This happens in the addon preferences

![Screenshot from 2024-02-18 14-51-16](https://github.com/neph1/blender-stable-diffusion-render/assets/7988802/a28c80e8-a782-4372-b892-1c0b140bba1a)

After switching, you need to restart for the configuration properties to update
