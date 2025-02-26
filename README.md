![](https://img.shields.io/github/tag/Tenchi2xh/pokedex-cli.svg)

# Pokédex CLI

The Pocket Monster Index, now in your terminal!

- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Acknowledgments](#acknowledgments)

## Installation

### Using pip directly from GitHub

You can install the application directly from GitHub using pip:

```
pip install "git+https://github.com/Tenchi2xh/pokedex-cli.git@v0.1.4#egg=pokedex-cli"
```

### Using requirements.txt

Alternatively, you can clone the repository and install the required dependencies:

1. Clone the repository:
   ```bash
   git clone https://github.com/Tenchi2xh/pokedex-cli.git
   cd pokedex-cli
   ```

2. Install the required system dependencies (for Ubuntu/Debian):
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-dev python3-pip libjpeg-dev zlib1g-dev python3-venv
   ```

3. Install the Python dependencies:
   ```bash
   cd /path/to/pokedex-cli
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

For the best output quality, please adjust the vertical line spacing in your terminal emulator until the block characters connect.

## Usage

```
$ pokedex --help
Usage: main.py [OPTIONS] POKEMON

  Command-line interface for a quick Pokédex reference.

  Positional argument POKEMON can be either an id or a name, which has to be
  specified in the configured language.

Options:
  -s, --shiny                     Show shiny version of the Pokémon.
  -m, --mega                      Show Mega Evolution(s) if available.
  -l, --language LANGUAGE         Pokédex language to use.
  -pv, --pokedex-version VERSION  Pokédex version to use.
  -f, --format FORMAT             Output format (can be card, json, simple,
                                  line, page).
  --help                          Show this message and exit.
```

## Screenshots

<img width="527" alt="screen shot 2016-07-18 at 21 58 44" src="https://cloud.githubusercontent.com/assets/4116708/16928557/a648e8ce-4d33-11e6-9234-f76b8a1ef720.png">
<img width="485" alt="screen shot 2016-07-18 at 22 01 08" src="https://cloud.githubusercontent.com/assets/4116708/16928550/9effd960-4d33-11e6-8f28-04ac185595db.png">
<img width="500" alt="screen shot 2016-07-18 at 22 03 53" src="https://cloud.githubusercontent.com/assets/4116708/16928547/9b4c0f64-4d33-11e6-8143-b285790ea4bc.png">

## Acknowledgments

- Database fetched at runtime from [Veekun](http://veekun.com/dex/downloads)
- Icons adapted from [Pikachumazzinga on DeviantArt](http://pikachumazzinga.deviantart.com/art/Pokemon-Essentials-Icon-Pack-ORAS-UPDATE-424114559)

Pokémon © 2002-2016 Pokémon. © 1995-2016 Nintendo/Creatures Inc./GAME FREAK inc. TM, ® and Pokémon character names are trademarks of Nintendo.

No copyright or trademark infringement is intended in using Pokémon content in this project.
