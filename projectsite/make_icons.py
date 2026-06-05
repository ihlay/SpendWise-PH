from PIL import Image, ImageDraw
import os

os.makedirs('static/img', exist_ok=True)

for size in [192, 512]:
    img = Image.new('RGB', (size, size), color='#1B5E20')
    draw = ImageDraw.Draw(img)
    draw.ellipse([size//4, size//4, 3*size//4, 3*size//4], fill='#FFFFFF')
    img.save(f'static/img/icon-{size}.png')

print('Icons created!')