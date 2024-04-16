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
  * player's line of sight
  * implemented using **Entity Component System (ECS)**
* EXTRA features
  * simple UI
    * status bar
    * help panel
    * action log
  * difficulty progression (with each level +1 monster)
  * highscore list
  * random tiles for walls and floor
  * some debug tools
    * show exit
    * show potions with it's type
    * show all monsters
    * activate all monsters
    * show monster paths
    * take screenshot

## Known bugs

* 2 or more monsters sometimes occupy the same location
* after loading a new level, sometimes player starts on monster position
* monsters hit 2 times per one player turn
* action log is not cleared as expected when new game starts

## Ideas for future

* ~~Highscore table~~ ✅ done
* ~~use walls tiles from 'tileset.png' instead of black rectangle~~
* add more monster types
* make fight more entertaining
* switch font to monospace pixel art
* add sounds (music and sfx)
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

## Credits

Assets created by:
[Pixel-boy](https://pixel-boy.itch.io/)
[AAA](https://www.instagram.com/challenger.aaa/?hl=fr)

Patreon: [https://www.patreon.com/pixelarchipel](https://www.patreon.com/pixelarchipel)