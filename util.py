'''
    Utility functions
'''
import io
from flask import make_response


def make_image_response(img_path):
    ''' Make response for an image '''
    with io.FileIO(str(img_path)) as img:
        img_bytes = img.readall()
    response = make_response(img_bytes)
    response.headers.set('Content-Type', 'image/jpeg')
    return response
