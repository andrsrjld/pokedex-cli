# -*- coding: utf-8 -*-

import os
import textwrap
from PIL import Image

from .. import resource_path
from .colors import rgb_to_xterm
from .conversion import rgb2short


block_top = "▀"
numbers = {
    "0": [u"┌─┐",
          u"│ │",
          u"└─┘"],
    "1": [u" ┐ ",
          u" │ ",
          u" ┴ "],
    "2": [u"┌─┐",
          u"┌─┘",
          u"└─┘"],
    "3": [u"┌─┐",
          u" ─┤",
          u"└─┘"],
    "4": [u"┬ ┬",
          u"└─┤",
          u"  ┴"],
    "5": [u"┌─┐",
          u"└─┐",
          u"└─┘"],
    "6": [u"┌─┐",
          u"├─┐",
          u"└─┘"],
    "7": [u"┌─┐",
          u"  │",
          u"  ┴"],
    "8": [u"┌─┐",
          u"├─┤",
          u"└─┘"],
    "9": [u"┌─┐",
          u"└─┤",
          u"└─┘"],
    "#": [u" ┼┼",
          u" ┼┼",
          u"   "],
}

type_colors = {
    "normal":   int(rgb2short("A8A77A")[0]),
    "fire":     int(rgb2short("EE8130")[0]),
    "water":    int(rgb2short("6390F0")[0]),
    "electric": int(rgb2short("F7D02C")[0]),
    "grass":    int(rgb2short("7AC74C")[0]),
    "ice":      int(rgb2short("96D9D6")[0]),
    "fighting": int(rgb2short("C22E28")[0]),
    "poison":   int(rgb2short("A33EA1")[0]),
    "ground":   int(rgb2short("E2BF65")[0]),
    "flying":   int(rgb2short("A98FF3")[0]),
    "psychic":  int(rgb2short("F95587")[0]),
    "bug":      int(rgb2short("A6B91A")[0]),
    "rock":     int(rgb2short("B6A136")[0]),
    "ghost":    int(rgb2short("735797")[0]),
    "dragon":   int(rgb2short("6F35FC")[0]),
    "dark":     int(rgb2short("705746")[0]),
    "steel":    int(rgb2short("B7B7CE")[0]),
    "fairy":    int(rgb2short("D685AD")[0]),
}


def clean_sprite(image):
    """Clean up sprite by removing stray black pixels and improving contrast"""
    pixels = image.load()
    width, height = image.size
    
    # Convert black pixels that are surrounded by non-black to background
    for y in range(1, height-1):
        for x in range(1, width-1):
            current = pixels[x, y]
            if current[0] < 30 and current[1] < 30 and current[2] < 30:  # If pixel is very dark
                neighbors = [
                    pixels[x-1, y], pixels[x+1, y],
                    pixels[x, y-1], pixels[x, y+1]
                ]
                # If surrounded by non-black pixels, convert to background
                if all(n[0] > 30 or n[1] > 30 or n[2] > 30 for n in neighbors):
                    pixels[x, y] = (40, 40, 40)  # Dark grey instead of pure black
    
    return image

def draw_image(buffer, path, x0=0, y0=0):
    image = Image.open(path).convert("RGB")
    
    # Ukuran standar untuk sprite Let's Go
    max_size = 32  # Tetap gunakan 32 untuk tampilan di terminal
    
    # Hitung rasio untuk scaling sambil mempertahankan aspek ratio
    ratio = min(max_size / image.width, max_size / image.height)
    new_size = (int(image.width * ratio), int(image.height * ratio))
    
    # Resize dengan nearest neighbor untuk mempertahankan ketajaman pixel art
    image = image.resize(new_size, Image.NEAREST)
    
    pixels = image.load()
    width, height = image.size

    # Center the image vertically
    y_offset = (max_size - height) // 2
    
    for y in range(0, height, 2):
        for x in range(width):
            if x + x0 < buffer.width and y + y0 + y_offset < buffer.height * 2:
                color_top = rgb_to_xterm(pixels[x, y])
                color_bottom = rgb_to_xterm(pixels[x, y + 1]) if y + 1 < height else 0
                buffer.put_cell((x0 + x, (y0 + y + y_offset) // 2), u"▀", color_top, color_bottom)


def draw_number(buffer, number, x0=0, y0=0, fg=15):
    chars = "#%03d" % number
    for i, char in enumerate(chars):
        template = numbers[char]
        for x in range(3):
            for y in range(3):
                buffer.put_cell((x0 + (i*3) + x, y0 + y), template[y][x], fg)


def draw_type(buffer, type1, type2, x0=0, y0=0):
    if type1:  # Hanya gambar type1 jika tidak None
        buffer.put_line((x0, y0), f" {type1.upper()} ", fg=0, bg=type_colors.get(type1.lower(), 0))
    if type2:  # Hanya gambar type2 jika tidak None
        buffer.put_line((x0 + len(type1) + 2, y0), f" {type2.upper()} ", fg=0, bg=type_colors.get(type2.lower(), 0))

def draw_flavor_text(buffer, text, width, x0=0, y0=0, fg=15, bg=-1):
    # Non-asian languages only!
    lines = textwrap.fill(text, width=width).split("\n")
    for i, line in enumerate(lines):
        buffer.put_line((x0, y0 + i), line, fg, bg)


def get_height(stage):
    if len(stage) == 0:
        return 2
    return sum([get_height(stage[pkmn]) for pkmn in stage])


def get_width(chain):
    maximum = max(len(pkmn[1]) for pkmn in chain.keys()) if chain.keys() else 0
    return maximum + max(get_width(stage) + 3 for stage in chain.values()) if chain.values() else 0


def draw_evolutions(buffer, chain, number, x0=0, y0=0, bg=-1):

    def draw(pkmn, evolutions, width, ox0, oy0):
        if width == 0:
            width = len(pkmn[1])
        ox1 = len(pkmn[1])
        fg = 245 if pkmn[0] != number else 15
        buffer.put_line((x0 + ox0, y0 + oy0), ("#%03d" % pkmn[0]).center(width), fg, bg)
        buffer.put_line((x0 + ox0, y0 + oy0 + 1), pkmn[1].center(width), fg, bg)
        if len(evolutions) > 0:
            buffer.put_line((x0 + ox0 + ox1, y0 + oy0 + 1), " > ", 33, bg)
            ox1 += 3

        last = 0
        if evolutions:
            longest = max(map(lambda p: len(p[1]), evolutions))
            for oy1, e in enumerate(evolutions):
                draw(e, evolutions[e], longest, ox0 + ox1, oy0 + oy1 * 2 + last)
                last = get_height(evolutions[e]) - 2

    # draw(chain.keys()[0], chain.values()[0], 0, 0, 0)
    keys = list(chain.keys())  # Ubah dict_keys menjadi list
    values = list(chain.values())  # Ubah dict_values menjadi list
    draw(keys[0], values[0], 0, 0, 0)
