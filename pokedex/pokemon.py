# -*- encoding: utf-8 -*-

import os
import logging
import requests

from .exceptions import *
from .database.queries import *
from .database.get import *

class Pokemon(object):
    def __init__(self, pokemon, language=default_language, version=default_version):
        try:
            # Coba cari Pokemon di PokeAPI
            if isinstance(pokemon, str):
                pokemon_name = pokemon.lower()
                response = requests.get(f"{POKEAPI_BASE_URL}/pokemon/{pokemon_name}")
            else:
                response = requests.get(f"{POKEAPI_BASE_URL}/pokemon/{pokemon}")

            if response.status_code == 200:
                pokemon_data = response.json()
                species_response = requests.get(pokemon_data['species']['url'])
                species_data = species_response.json() if species_response.status_code == 200 else {}

                self.number = pokemon_data['id']
                self.name = pokemon_data['name'].capitalize()
                self.types = [t['type']['name'] for t in pokemon_data['types']]
                self.height = pokemon_data['height'] * 10
                self.weight = pokemon_data['weight'] * 100
                self.genus = next((g['genus'] for g in species_data.get('genera', []) 
                                 if g['language']['name'] == language), "??? Pokémon")
                self.flavor = next((f['flavor_text'].replace('\n', ' ').replace('\f', ' ') 
                                  for f in species_data.get('flavor_text_entries', [])
                                  if f['language']['name'] == language), "")

                # Calculate weaknesses
                self.weaknesses = get_pokemon_weakness(self.types)

                # Download sprite if not exists
                icon_path = os.path.join(resource_path, f"icons/icon{self.number:03d}.png")
                if not os.path.exists(os.path.dirname(icon_path)):
                    os.makedirs(os.path.dirname(icon_path))
                
                if not os.path.exists(icon_path):
                    # Gunakan sprite dari PokemonDB dengan style yang berbeda
                    sprite_urls = [
                        # Black & White sprites yang memiliki gaya pixel art yang bagus
                        f"https://img.pokemondb.net/sprites/black-white/normal/{pokemon_data['name'].lower()}.png",
                        # Fallback ke style lain
                        f"https://img.pokemondb.net/sprites/black-white/anim/normal/{pokemon_data['name'].lower()}.gif",
                        f"https://img.pokemondb.net/sprites/x-y/normal/{pokemon_data['name'].lower()}.png",
                        # Fallback terakhir ke sprite default
                        f"https://img.pokemondb.net/sprites/home/normal/{pokemon_data['name'].lower()}.png"
                    ]
                    
                    for sprite_url in sprite_urls:
                        if not sprite_url:
                            continue
                        try:
                            sprite_response = requests.get(sprite_url)
                            if sprite_response.status_code == 200:
                                with open(icon_path, 'wb') as f:
                                    f.write(sprite_response.content)
                                break
                        except Exception as e:
                            logging.error(f"Error downloading sprite from {sprite_url}: {str(e)}")
                            continue

                # Get evolution chain
                if 'evolution_chain' in species_data:
                    evo_response = requests.get(species_data['evolution_chain']['url'])
                    if evo_response.status_code == 200:
                        self.chain = self._process_evolution_chain(evo_response.json()['chain'])
                    else:
                        self.chain = {(self.number, self.name): {}}
                else:
                    self.chain = {(self.number, self.name): {}}

            else:
                raise NoSuchPokemon(pokemon)

        except Exception as e:
            self.number = 0
            self.name = "MISSINGNO."
            self.genus = "???"
            self.flavor = f"Pokémon {pokemon} not found"
            self.types = ["flying", "normal"]
            self.weaknesses = []
            self.chain = {(0, "MISSINGNO."): {}}
            self.height = 10
            self.weight = 100

    def _process_evolution_chain(self, chain_data):
        """Process evolution chain data from PokeAPI"""
        result = {}
        species_name = chain_data['species']['name']
        species_url = chain_data['species']['url']
        species_id = int(species_url.split('/')[-2])
        
        current = (species_id, species_name.capitalize())
        result[current] = {}
        
        for evolution in chain_data.get('evolves_to', []):
            result[current].update(self._process_evolution_chain(evolution))
        
        return result

    def icon(self, shiny=False, mega=0):
        # Untuk sementara kita hanya mendukung icon normal (tidak shiny/mega)
        return f"icons/icon{self.number:03d}.png"

    @property
    def mega(self):
        return 0  # Sementara disable mega evolution
