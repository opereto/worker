from PIL import Image
from validations import validate_image_file
import base64

def image_file_to_base64(file):
    if not validate_image_file(file):
        raise Exception('Invalid Image')
    im = Image.open(file)
    return base64.b64encode(im.convert("RGBA").tostring("raw", "RGBA"))