import os
import sys

BMP_HEADER_SIZE = 54
BITES_IN_BYTE = 8


def get_masks(degree: int):
    text_mask = 0b11111111
    image_mask = 0

    text_mask <<= BITES_IN_BYTE - degree
    text_mask %= 256

    image_mask >>= degree
    image_mask <<= degree

    return text_mask, image_mask


def get_new_byte(character: int, text_mask: int, image_mask: int,
                 image, degree: int):
    image_byte = int.from_bytes(image.read(1), sys.byteorder) & image_mask
    text_byte = character & text_mask
    text_byte >>= BITES_IN_BYTE - degree
    image_byte |= text_byte
    return image_byte


def encrypt_bmp(input_bmp_path: str, encrypted_bmp_path: str, txt_file_path: str,
                *, encoding='utf-8', degree=2):
    text_length = os.stat(txt_file_path).st_size
    input_bmp_length = os.stat(input_bmp_path).st_size

    if text_length >= input_bmp_length * degree // BITES_IN_BYTE - 54:
        raise ValueError("Image is too small")

    with open(txt_file_path, 'r', encoding=encoding) as f_in:
        text = f_in.read()
    input_bmp = open(input_bmp_path, 'rb')
    encrypted_bmp = open(encrypted_bmp_path, 'wb')

    bmp_header = input_bmp.read(BMP_HEADER_SIZE)
    encrypted_bmp.write(bmp_header)

    text_mask, image_mask = get_masks(degree)

    for character in text:
        ord_character = ord(character)
        for i in range(BITES_IN_BYTE, degree):
            image_byte = get_new_byte(ord_character,
                                      text_mask, image_mask,
                                      input_bmp,
                                      degree)
            encrypted_bmp.write(image_byte.to_bytes(1, sys.byteorder))
            ord_character <<= degree

    encrypted_bmp.write(input_bmp.read())

    input_bmp.close()
    encrypted_bmp.close()
