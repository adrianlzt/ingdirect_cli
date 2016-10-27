from base64 import b64decode

import png
import sys
import logging
logger = logging.getLogger(__name__)

def obtiene_rgb(pix, fila, columna):
    # El array tiene los valores: R, G, B, A, R, G, B, A...
    return pix[columna][fila*4:fila*4+3]

def parse_pin(pix):
    resultado = []
    if obtiene_rgb(pix, 27, 31) == [125,125,125]: #0
        resultado.append(0)
    if obtiene_rgb(pix, 32, 28) == [255,255,255]: #1
        resultado.append(1)
    if obtiene_rgb(pix, 33, 33) == [78,78,78]: #2
        resultado.append(2)
    if obtiene_rgb(pix, 29, 29) == [208,208,208]: #3
        resultado.append(3)
    if obtiene_rgb(pix, 31, 34) == [78,78,78]: #4
        resultado.append(4)
    if obtiene_rgb(pix, 26, 32) == [78,78,78]: #5
        resultado.append(5)
    if obtiene_rgb(pix, 28, 28) == [184,184,184]: #6
        resultado.append(6)
    if obtiene_rgb(pix, 26, 23) == [184,184,184]: #7
        resultado.append(7)
    if obtiene_rgb(pix, 29, 29) == [78,78,78]: #8
        resultado.append(8)
    if obtiene_rgb(pix, 33, 29) == [125,125,125]: #9
        resultado.append(9)

    if len(resultado) != 1:
        raise Exception("No se ha encontrado ningun resultado o mas de uno! %s" % resultado)

    return resultado.pop()

def process_pin_images(pinpad):
    logger.info(sys._getframe().f_code.co_name)

    imagenes = convert_pinpad_to_array_data(pinpad)

    pinpad_numers = []
    n = 0
    for i in imagenes:
        pinpad_numers.append(parse_pin(i))
        n+=1

    return pinpad_numers

def convert_pinpad_to_array_data(images_array):
    """
    Convierte un array de imagenes en base64 en un array de ints entre 0 y 255
    :param images_array: pinpad pasado por ING
    :return: array de arrays de arrays de valores [img[filas[valores]], ...]
    """
    imagenes = []
    for imgb64 in images_array:
        p = png.Reader(bytes=b64decode(imgb64))
        imagen = []
        for line in p.asRGBA()[2]:
            imagen.append(list(line))
        imagenes.append(imagen)

    return imagenes

