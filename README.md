csgo-icon-extractor
===================

Python command-line utility for extracting the icon set used in the _Counter-Strike: Global Offensive_ video game.

## How to Use

**Pre-requisites:** You must have [Python](https://www.python.org/) (v3.3+) and [SWFTools](http://www.swftools.org/) (v0.9+) installed.

### Getting Started

- Clone this Git repository:  
`git clone https://github.com/jessewebb/csgo-icon-extractor.git`
- Change directories into the cloned repository's root:  
`cd csgo-icon-extractor/`
- Make a copy of CS:GO's icon library file (`iconlib.swf`):  
`copy "C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo\resource\flash\iconlib.swf" iconlib.swf`
- Run the csgo-icon-extractor command-line script (`main.py`):  
`py -3 main.py`

You will then have a `csgo-icons/` directory with all of the icons from the game within it!

### Advanced Usage

TODO

## References

- ["CS:GO Weapon Icons" thread in reddit's /r/GlobalOffensive/](https://www.reddit.com/r/GlobalOffensive/comments/2g7fjf/csgo_weapon_icons/)
- ["How to extract images from swf file?" answer on Stack Overflow](http://stackoverflow.com/a/15843723/346561)

## License

This software is free under [the MIT License](https://github.com/jessewebb/csgo-icon-extractor/blob/master/LICENSE).

Copyright © 2016 Jesse Webb
