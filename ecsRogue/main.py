# /// script
# dependencies = [
#  "pyved_engine",
# ]
from launch_game import bootgame
import json

if __name__ == '__main__':  # Keep this if u wish to allow direct script direct execution/No pyv-cli
    with open('cartridge/metadat.json', 'r') as fp:
        bootgame(json.load(fp))
