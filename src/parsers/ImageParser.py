# Notebook: https://colab.research.google.com/drive/1ueNhEeQvaZLNusZeyniCHW2zFHY1v4y_

import easyocr
import io

from parsers.DefaultParser import DefaultParser

from PIL import Image, ImageOps, ImageEnhance


class ImageParser(DefaultParser):
    """
    Adds supports for extracting text from image
    """

    # global reader to be re-used
    ocr_reader = easyocr.Reader(['en'])

    def extract_text(self, path):
        im = Image.open(path)
        # convert image to grayscale
        im = ImageOps.grayscale(im)
        # increase image contrast 2x
        im = ImageEnhance.Contrast(im).enhance(2)
        # save imag to byte buffer
        img_byte_arr = io.BytesIO()
        im.save(img_byte_arr, format='PNG')
        # extract text from image
        img_byte_arr = img_byte_arr.getvalue()
        ocr_output = self.ocr_reader.readtext(
            path,
            detail=0,
            paragraph=True,
        )
        # convert array of text to string
        return '\n'.join(ocr_output)
