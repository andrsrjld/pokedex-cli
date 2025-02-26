# -*- encoding: utf-8 -*-

import os
import requests
import zlib
import json
from progressbar import ProgressBar

from .. import resource_path

# Daftar kelemahan berdasarkan tipe Pokémon
POKEMON_WEAKNESS = {
    "normal": ["fighting"],
    "fire": ["water", "ground", "rock"],
    "water": ["electric", "grass"],
    "electric": ["ground"],
    "grass": ["fire", "ice", "poison", "flying", "bug"],
    "ice": ["fire", "fighting", "rock", "steel"],
    "fighting": ["flying", "psychic", "fairy"],
    "poison": ["ground", "psychic"],
    "ground": ["water", "ice", "grass"],
    "flying": ["electric", "ice", "rock"],
    "psychic": ["bug", "ghost", "dark"],
    "bug": ["fire", "flying", "rock"],
    "rock": ["water", "grass", "fighting", "ground", "steel"],
    "ghost": ["ghost", "dark"],
    "dragon": ["ice", "dragon", "fairy"],
    "dark": ["fighting", "bug", "fairy"],
    "steel": ["fire", "fighting", "ground"],
    "fairy": ["poison", "steel"]
}

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"

def download_database():
    """Download or update Pokemon data from PokeAPI"""
    db_path = os.path.join(resource_path, "pokedex.json")
    icons_dir = os.path.join(resource_path, "icons")
    
    # Buat direktori icons jika belum ada
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
    
    if not os.path.exists(db_path):
        print("Downloading Pokemon database...")
        all_pokemon = {}
        
        with ProgressBar(max_value=1025) as bar:
            # Get Pokemon data
            for pokemon_id in range(1, 1026):  # Up to Gen 9
                try:
                    response = requests.get(f"{POKEAPI_BASE_URL}/pokemon/{pokemon_id}")
                    if response.status_code == 200:
                        pokemon_data = response.json()
                        
                        # Get species data for additional info
                        species_response = requests.get(f"{POKEAPI_BASE_URL}/pokemon-species/{pokemon_id}")
                        species_data = species_response.json() if species_response.status_code == 200 else {}
                        
                        # Try different sprite sources in order of preference
                        sprite_urls = [
                            f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_id}.png",
                            f"https://play.pokemonshowdown.com/sprites/gen5/{pokemon_data['name'].lower()}.png",
                            pokemon_data['sprites']['front_default']
                        ]
                        
                        sprite_downloaded = False
                        for sprite_url in sprite_urls:
                            if not sprite_url:
                                continue
                            
                            sprite_response = requests.get(sprite_url)
                            if sprite_response.status_code == 200:
                                icon_path = os.path.join(icons_dir, f"icon{pokemon_id:03d}.png")
                                with open(icon_path, 'wb') as f:
                                    f.write(sprite_response.content)
                                sprite_downloaded = True
                                break
                        
                        if not sprite_downloaded:
                            print(f"\nWarning: Could not download sprite for #{pokemon_id} {pokemon_data['name']}")
                        
                        all_pokemon[pokemon_id] = {
                            "id": pokemon_id,
                            "name": pokemon_data["name"],
                            "types": [t["type"]["name"] for t in pokemon_data["types"]],
                            "height": pokemon_data["height"],
                            "weight": pokemon_data["weight"],
                            "genus": next((g["genus"] for g in species_data.get("genera", []) if g["language"]["name"] == "en"), ""),
                            "flavor_text": next((f["flavor_text"] for f in species_data.get("flavor_text_entries", []) if f["language"]["name"] == "en"), ""),
                            "evolution_chain": species_data.get("evolution_chain", {}).get("url", "")
                        }
                        print(f"\rDownloaded data and sprite for #{pokemon_id} {pokemon_data['name']}")
                        bar.update(pokemon_id)
                except Exception as e:
                    print(f"\nError downloading Pokemon #{pokemon_id}: {str(e)}")
                    continue
        
        # Save to file
        with open(db_path, 'w') as f:
            json.dump(all_pokemon, f)
        print("\nDatabase and sprites downloaded successfully!")

def get_pokemon_weakness(pokemon_types):
    """
    Calculate Pokemon weaknesses based on its type(s)
    """
    if not pokemon_types:
        return []
        
    # Convert types to lowercase for consistency
    types = [t.lower() for t in pokemon_types]
    
    # Get all weaknesses for each type
    all_weaknesses = []
    for ptype in types:
        if ptype in POKEMON_WEAKNESS:
            all_weaknesses.extend(POKEMON_WEAKNESS[ptype])
    
    # Remove duplicates and sort
    unique_weaknesses = sorted(list(set(all_weaknesses)))
    
    return unique_weaknesses

def search_pokemon(name):
    """
    Fungsi pencarian Pokémon yang langsung menampilkan kelemahannya.
    :param name: str - Nama Pokémon
    """
    pokemon_data = get_pokemon_data(name)
    if not pokemon_data:
        print(f"Pokémon {name} tidak ditemukan.")
        return

    print(f"Pokémon: {name}")
    print(f"Type: {', '.join(pokemon_data['types'])}")
    print(f"Weakness: {', '.join(pokemon_data['weaknesses'])}")

# Contoh Penggunaan
if __name__ == "__main__":
    search_pokemon("Mudkip")
