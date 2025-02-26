# -*- encoding: utf-8 -*-
from __future__ import print_function

import json as json_lib
import os

from .graphics.cell_buffer import Buffer
from .graphics.draw import *

icon_width = 32
format_names = ["card", "json", "simple", "line", "page"]

# Add type colors mapping at the top of the file
type_colors = {
    'normal': 250,   # Light gray
    'fire': 196,     # Red
    'water': 33,     # Blue
    'electric': 220, # Yellow
    'grass': 40,     # Green
    'ice': 51,       # Light blue
    'fighting': 167, # Orange red
    'poison': 127,   # Purple
    'ground': 178,   # Sandy
    'flying': 117,   # Light purple
    'psychic': 205,  # Pink
    'bug': 70,       # Lime green
    'rock': 137,     # Brown
    'ghost': 92,     # Dark purple
    'dragon': 27,    # Dark blue
    'dark': 237,     # Dark gray
    'steel': 245,    # Light steel blue
    'fairy': 213,    # Light pink
}

def draw_weakness_with_color(buffer, weakness, x_pos, y_pos, bg=0):
    """Draw a single weakness with colored background"""
    weakness_str = f" {weakness.upper()} "
    buffer.put_line((x_pos, y_pos), weakness_str, fg=0, bg=type_colors.get(weakness.lower(), 0))
    return len(weakness_str) + 2  # Add extra space between badges

def card(pokemon, shiny=False, mega=False):
    evolutions_height = get_height(next(iter(pokemon.chain.values())))
    evolutions_width = get_width(pokemon.chain)
    content_width = max([evolutions_width, len(pokemon.genus) + 3 + 8 + 12, 32])

    icons = pokemon.mega + 1 if mega else 1
    total_icon_width = icons * icon_width + 4
    
    content_width = max(content_width, icon_width + 4)
    width = content_width + total_icon_width + 4
    
    # Adjust the height of the buffer
    extra_height = 6  # Reduce height
    buffer = Buffer(width + 1, 18 + evolutions_height - 2 + extra_height)  # Adjusted height

    # Draw Pokemon icon(s) with proper centering
    icon_start_x = content_width + 3
    for mega_idx in range(icons):
        icon_x = icon_start_x + (icon_width + 2) * mega_idx
        draw_image(
            buffer, 
            os.path.join(resource_path, pokemon.icon(shiny=shiny, mega=mega_idx)),
            x0=icon_x,
            y0=1
        )

    # Draw header information
    buffer.put_line((3, 1), pokemon.name)
    buffer.put_line((3, 2), u"%s Pokémon" % pokemon.genus.capitalize(), fg=245)
    buffer.put_line((3, 3), "%0.2f m / %0.1f kg" % (pokemon.height / 10.0, pokemon.weight / 10.0), fg=240)

    # Draw Pokemon number
    draw_number(buffer, pokemon.number, x0=content_width-12, y0=1)

    # Draw Pokemon types with proper spacing
    y_pos = 5
    x_pos = 3
    for type_name in pokemon.types:
        type_str = f" {type_name.upper()} "
        buffer.put_line((x_pos, y_pos), type_str, fg=0, bg=type_colors.get(type_name.lower(), 0))
        x_pos += len(type_str) + 1

    # Draw flavor text
    y_pos = 7
    draw_flavor_text(buffer, pokemon.flavor, content_width - 3, x0=3, y0=y_pos)
    
    # Draw separator line
    y_pos = 11
    buffer.put_line((3, y_pos), "-" * (content_width - 3), fg=240)

    # Draw "Weaknesses:" label
    y_pos = 12
    buffer.put_line((3, y_pos), "Weaknesses:", fg=245)
    
    # Draw colored weaknesses, limit to top 4
    top_weaknesses = pokemon.weaknesses[:4] if pokemon.weaknesses else []  # Ensure it's always defined
    x_pos = 14

    for weakness in top_weaknesses:
        x_pos += draw_weakness_with_color(buffer, weakness, x_pos, y_pos)

    if not top_weaknesses:
        buffer.put_line((14, y_pos), "None", fg=245)

    # Calculate next y position
    y_pos = 14 if len(top_weaknesses) <= 2 else 15

    # Draw footer separator
    buffer.put_line((3, y_pos), "-" * (content_width - 3), fg=240)

    # Draw evolution chain
    y_pos += 2
    draw_evolutions(buffer, pokemon.chain, pokemon.number, x0=3, y0=y_pos)

    buffer.display()

def json(pokemon):
    print(json_lib.dumps({
        "number": pokemon.number,
        "name": pokemon.name,
        "genus": pokemon.genus,
        "flavor": pokemon.flavor,
        "types": pokemon.types,
        "weaknesses": pokemon.weaknesses,
        "chain": [{"number": stage[0], "name": stage[1]} for stage in pokemon.chain],
        "height": pokemon.height,
        "weight": pokemon.weight
    }, indent=4))

def simple(pokemon):
    print(u"%s (#%03d), %s Pokémon" % (pokemon.name, pokemon.number, pokemon.genus))
    types = "/".join(map(lambda s: s.capitalize(), pokemon.types))
    print("%s, %0.2f m, %0.1f kg" % (types, pokemon.height / 10.0, pokemon.weight / 10.0))
    print(pokemon.flavor)
    
    # Format weaknesses for simple display
    if hasattr(pokemon, 'weaknesses') and pokemon.weaknesses:
        weakness_list = [w.capitalize() for w in pokemon.weaknesses]
        print("Weaknesses: " + ", ".join(weakness_list))
    else:
        print("Weaknesses: None")
    print("-" * 40)

def line(pokemon):
    evolution = " > ".join(["#%03d" % stage[0] for stage in pokemon.chain])
    types = "/".join(map(lambda s: s.capitalize(), pokemon.types))
    
    # Format weaknesses for line display
    if hasattr(pokemon, 'weaknesses') and pokemon.weaknesses:
        weakness_list = [w.capitalize() for w in pokemon.weaknesses]
        weaknesses = ", ".join(weakness_list)
    else:
        weaknesses = "None"
        
    print(u"%s (#%03d): %s | %s | Weaknesses: %s" % (pokemon.name, pokemon.number, types, evolution, weaknesses))
