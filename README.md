# blender-stable-diffusion-render
A Blender addon for using Stable Diffusion to render texture bakes for objects.

It will maintain your existing UV coords and bake the result to them.

Limitations: The intermediate object has its uv's projected from the view. So even though the result will be mapped 'around' the object, it won't render what isn't seen.

Steps:

1. Download the 'sd_render' folder and install it as an addon.

2. Add a material to your object

3. Unwrap the UV map.

4. Set up a viewer node and render depth. Save result

5. Set active camera as view

6. Select object and hit "Render" in the "Stable Diffusion Render" panel in the "Render" tab

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/T6T3S8VXY)

![Screenshot from 2024-02-12 17-57-22](https://github.com/neph1/blender-stable-diffusion-render/assets/7988802/204b2d2a-2b5d-4575-84ac-e7625cd50b7d)

![Screenshot from 2024-02-12 17-57-42](https://github.com/neph1/blender-stable-diffusion-render/assets/7988802/5842777d-7029-4978-b043-6ba1e7005f8b)

![Screenshot from 2024-02-12 17-59-34](https://github.com/neph1/blender-stable-diffusion-render/assets/7988802/80ed6400-67af-4c0e-9b24-a16a846ce50a)
