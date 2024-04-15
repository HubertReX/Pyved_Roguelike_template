# wall combinations
import json
from rich import print
import copy

# Big walls from the middle of tileset - NOT SO EASY    
# dungeon_dirs = {
#     # only 1 wall next to us
#     "1000" : 913,
#     "0100" : 1022,
#     "0010" : 916,
#     "0001" : 996,
#     # 2 walls
#     "1100" : 860,
#     "0110" : 1028,
#     "0011" : 1000,
#     "1001" : 888,
    
#     "1010" : 885,
#     "0101" : 995,
#     # 3 walls
#     "1110": 994,
#     "0111": 857,
#     "1011": 1024,
#     "1101": 972,
#     # all 4
#     # "1111": 1025
# }

walls_dirs = {
    # only 1 wall next to us
    "1000" : 78,
    "0100" : 77,
    "0010" : 78,
    "0001" : 105,
    # 2 walls
    "1100" : 103,
    "0110" : 75,
    "0011" : 76,
    "1001" : 104,
    
    "1010" : 78,
    "0101" : 106,
    # 3 walls
    "1110": 79,
    "0111": 80,
    "1011": 108,
    "1101": 107,
    # all 4
    "1111": 109
}
paravan_offset = 131 - 75 
big_fence = copy.deepcopy(walls_dirs)
for key, value in big_fence.items():
    big_fence[key] = value - paravan_offset
    
big_wall = copy.deepcopy(walls_dirs)
for key, value in big_wall.items():
    big_wall[key] = value + paravan_offset
    

terrain_set = {}
terrain_set["big_fence"] = big_fence
terrain_set["small_fence"] = walls_dirs
terrain_set["big_wall"] = big_wall

print(terrain_set)
