from PIL import Image
import io
import base64
import json

def paste_png_on_image(x, y, b64_string, base_image):

    image_data = base64.b64decode(b64_string)
    
    with io.BytesIO(image_data) as image_buffer:
        decoded_image = Image.open(image_buffer)
        decoded_image.load()

    base_image.paste(decoded_image, (x, y), decoded_image if decoded_image.mode == 'RGBA' else None)
    
    return base_image


chunks = json.load(open("level5_data.json"))
order = json.load(open("level5_order.json"))


width  = 3500 - 44
height = 4500 - 20

chunk_width = width // 128
chunk_height = height // 128

base_img = Image.new("RGBA", (width, height))

def chunk_index_to_xy(i):
    col = i % 128
    row = i // 128
    return col, row

for i, o in enumerate(order):
    x, y = chunk_index_to_xy(i)
    base_img = paste_png_on_image(x*chunk_width, y*chunk_height, chunks[o], base_img)
    print(i)

base_img.save("rebuilt.png")