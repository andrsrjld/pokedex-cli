# -*- coding: utf-8 -*-

import os
import sqlite3
import logging
import json

from .. import resource_path
from ..exceptions import *

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"

db = sqlite3.connect(os.path.join(resource_path, "veekun-pokedex.sqlite"))
cursor = db.cursor()

default_version = "x"
default_language = "en"

def get_versions():
    cursor.execute("""SELECT identifier
                        FROM versions
                   """)
    return [row[0] for row in cursor.fetchall()]


def get_types():
    cursor.execute("""SELECT type_id, name
                        FROM type_names
                       WHERE type_id < 10000 AND local_language_id=9
                   """)
    return {row[0]: row[1].lower() for row in cursor.fetchall()}


def get_pokemon_id(pokemon, language=default_language):
    try:
        pokemon_id = int(pokemon)
        if pokemon_id <= 0 or pokemon_id > 1025:
            raise NoSuchPokemon("#%d" % pokemon_id)
        return pokemon_id
    except ValueError:
        return get_pokemon_by_name(pokemon, language=language)


def get_pokemon_name(id, language=default_language):
    cursor.execute("""SELECT name
                        FROM pokemon_species_names s
                        JOIN languages l ON l.identifier="{language}"
                       WHERE s.local_language_id=l.id AND s.pokemon_species_id={id}
                   """.format(id=id, language=language))
    return cursor.fetchall()[0][0]


def get_pokemon_by_name(name, language=default_language):
    cursor.execute("""SELECT DISTINCT p.species_id
                        FROM pokemon p
                        JOIN languages l ON l.identifier="{language}"
                        JOIN pokemon_species_names s ON s.local_language_id=l.id 
                        AND LOWER(s.name)="{name}"
                        WHERE p.species_id=s.pokemon_species_id
                   """.format(name=name.lower().strip(), language=language))

    rows = cursor.fetchall()
    if len(rows) == 0:
        raise NoSuchPokemon(name)
    return rows[0][0]


def get_pokemon_type(pokemon_id):
    all_types = get_types()
    cursor.execute("""SELECT type_id, slot
                        FROM pokemon_types
                       WHERE pokemon_id={pokemon_id}
                   """.format(pokemon_id=pokemon_id))
    types = sorted([(row[0], int(row[1])) for row in cursor.fetchall()], key=lambda t: t[1])
    return map(lambda t: all_types[t[0]], types)


def get_pokemon_evolution_chain(pokemon_id, language=default_language):
    cursor.execute("""SELECT id, evolves_from_species_id
                        FROM pokemon_species
                       WHERE evolution_chain_id = (SELECT evolution_chain_id FROM pokemon_species WHERE id={pokemon_id})
                   """.format(pokemon_id=pokemon_id))
    chain = [(row[0], get_pokemon_name(row[0], language), row[1]) for row in cursor.fetchall()]
    # root = (pkmn for pkmn in chain if pkmn[2] is None).next()
    root = next((pkmn for pkmn in chain if pkmn[2] is None), None)
    tree = {root: {}}
    del chain[chain.index(root)]

    def add_evolutions(tree, root, chain):
        evolutions = [pkmn for pkmn in chain if pkmn[2] == root[0]]
        for evolution in evolutions:
            tree[root][evolution] = {}
            del chain[chain.index(evolution)]
            add_evolutions(tree[root], evolution, chain)

    add_evolutions(tree, root, chain)

    return tree


def get_type_effectiveness():
    cursor.execute("""
        SELECT t1.identifier as attacker_type, 
               t2.identifier as target_type, 
               te.damage_factor
        FROM type_efficacy te
        JOIN types t1 ON te.damage_type_id = t1.id
        JOIN types t2 ON te.target_type_id = t2.id
        WHERE te.damage_factor >= 200  -- Ambil yang super effective (2x damage atau lebih)
        ORDER BY te.damage_factor DESC  -- Urutkan berdasarkan damage terbesar
    """)
    
    effectiveness = {}
    for row in cursor.fetchall():
        attacker_type = row[0]
        target_type = row[1]
        damage_factor = row[2]
        
        if target_type not in effectiveness:
            effectiveness[target_type] = []
        effectiveness[target_type].append((attacker_type, damage_factor))
    
    return effectiveness


def get_pokemon_weaknesses(pokemon_id):
    """Calculate Pokemon's top 4 most effective weaknesses"""
    pokemon_types = list(get_pokemon_type(pokemon_id))
    effectiveness = get_type_effectiveness()
    
    weakness_scores = {}
    
    # Hitung total effectiveness untuk setiap tipe
    for ptype in pokemon_types:
        if ptype in effectiveness:
            for attacker, damage in effectiveness[ptype]:
                if attacker not in weakness_scores:
                    weakness_scores[attacker] = 0
                weakness_scores[attacker] += damage / 100.0  # Normalize damage factor
    
    # Urutkan weakness berdasarkan total effectiveness
    sorted_weaknesses = sorted(
        weakness_scores.items(),
        key=lambda x: (-x[1], x[0])  # Sort by score (descending) then by name
    )
    
    # Ambil 4 weakness teratas
    top_weaknesses = sorted_weaknesses[:4]
    
    # Kembalikan hanya nama tipenya
    return [w[0] for w in top_weaknesses]


def get_pokedex_entry(id, language=default_language, version=default_version):
    cursor.execute("""SELECT p.species_id, name, genus, flavor_text, height, weight
                        FROM pokemon p
                        JOIN languages l ON l.identifier="{language}"
                        JOIN versions v ON v.identifier="{version}"
                        JOIN pokemon_species_names s ON s.local_language_id=l.id AND s.pokemon_species_id=p.species_id
                        LEFT JOIN pokemon_species_flavor_text f ON f.language_id=l.id AND f.version_id=v.id AND f.species_id = p.species_id
                       WHERE p.species_id={id}
                   """.format(id=id, language=language, version=version))
    
    results = cursor.fetchall()
    
    if not results:
        newer_versions = ["sword", "shield", "scarlet", "violet"]
        for ver in newer_versions:
            cursor.execute("""SELECT p.species_id, name, genus, flavor_text, height, weight
                            FROM pokemon p
                            JOIN languages l ON l.identifier="{language}"
                            JOIN versions v ON v.identifier="{ver}"
                            JOIN pokemon_species_names s ON s.local_language_id=l.id AND s.pokemon_species_id=p.species_id
                            LEFT JOIN pokemon_species_flavor_text f ON f.language_id=l.id AND f.version_id=v.id AND f.species_id = p.species_id
                            WHERE p.species_id={id}
                       """.format(id=id, language=language, ver=ver))
            results = cursor.fetchall()
            if results:
                break
    
    return results


def get_pokemon_data(pokemon_id):
    """Get Pokemon data from local JSON database"""
    db_path = os.path.join(resource_path, "pokedex.json")
    
    with open(db_path, 'r') as f:
        all_pokemon = json.load(f)
    
    return all_pokemon.get(str(pokemon_id))
