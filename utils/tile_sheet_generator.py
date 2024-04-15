import copy
import json

file_name = "tileset"
# why it is flipped?
width = 448 # 640
height = 640 # 448

tile_size = 16
cols = width // tile_size
rows = height // tile_size

frame = {
			"frame": {
				"x": "_X_",
				"y": "_Y_",
				"w": tile_size,
				"h": tile_size
			},
			"rotated": False,
			"trimmed": False,
			"spriteSourceSize": {
				"x": 0,
				"y": 0,
				"w": tile_size,
				"h": tile_size
			},
			"sourceSize": {
				"w": tile_size,
				"h": tile_size
			}
}

data = {
	"frames": {},
	"meta": {
		"app": "http://www.codeandweb.com/texturepacker",
		"version": "1.0",
		"image": f"{file_name}.png",
		"format": "RGBA8888",
		"size": {
			"w": width,
			"h": height
		},
		"scale": "1"
	}
}

index = 0
for r in range(rows):
    for c in range(cols):
        f = copy.deepcopy(frame)
        f["frame"]["x"] = c * tile_size
        f["frame"]["y"] = r * tile_size
        data["frames"][f"{index}.png"] = f
        index += 1

with open(f"{file_name}.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)