# Pyved_Roguelike_template

Sample project based on [Pyved engine](https://github.com/gaudiatech/pyved-engine) using ECS Roguelike template

![screenshot](/screenshots/screenshot.png)

Core project is taken from engine repo [t-workshop/ECSRogue](https://github.com/gaudiatech/pyved-engine/tree/master/t-workshop/ECSRogue).

Try it online:
[PLAY!](https://hubertrex.github.io/Pyved_Roguelike_template/)

## Features

* from original project
  * random map generation
  * A* path finding for monsters
  * implemented using **Entity Component System (ECS)**
* EXTRA features
  * simple UI
    * status bar
    * help panel
    * action log
  * difficulty progression (with each level +1 monster)
  * some debug tools
    * show exit
    * show potions with it's type
    * show all monsters
    * activate all monsters
    * show monster paths

## Known bugs

* monsters sometimes occupy the same location
* monsters hit 2 times per one turn

## Ideas for future

* Highscore table (WIP)
* use walls tiles from 'tileset.png' instead of black rectangle
* switch font to pixel art witch fixed length
* add sounds
* make UI more appealing (icons, colors, menus)

## Installation

```bash
# create venv
python3 -m venv .venv
# activate it
# on Linux/MacOS
source .venv/bin/activate
# on Windows
.venv\Scripts\activate

# install packages
pip install -r requirements.txt

```

## Run

Desktop mode:

```bash
# using pyved command line tools
pyv-cli play ecsRogue
```

```bash
# or just like that
cd ecsRogue
python main.py
```

***

Browser mode:

```bash
# from top level project folder
pygbag --ume_block 0 ecsRogue
```

open [http://localhost:8000/]() in browser

use [http://localhost:8000#debug]() to show terminal in browser - useful for troubleshooting

## Deploying

### To [kata.games](https://kata.games/)

TODO: needs fixing, not working with the lates pyved-engine version

```bash
pyv-cli share ecsRogue
```

### To [itch.io](https://itch.io/)

full instruction [here](https://pygame-web.github.io/wiki/pygbag/itch.io/)

in short:

```bash
pygbag --ume_block 0 --archive ecsRogue
```

upload 'build/web.zip' to [itch.io](https://itch.io/) or any other hosted site.

***

### To GitHub pages

full instruction [here](https://pygame-web.github.io/wiki/pygbag/github.io/)
