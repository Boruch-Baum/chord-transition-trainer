[![License:GPLv3+](https://img.shields.io/badge/License-GPLv3+-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)

# Chord Transition Trainer

Randomly presents chord transitions from the chords you select, at the
speed you select, for the duration you select.
<div align=center>
<video
  src="https://github.com/user-attachments/assets/70f07f2a-fa5f-4cf8-b64e-6fb7e0334629"
  alt="screencast for chord transition trainer">
</video>
</div>

## Installation:

I'm planning on releasing binary blobs, but for now, you can create
your own, or just run it directly from source.

### Running directly from source

Install the dependencies, and run the source file, If you want to
install the dependencies using apt-get, see below.

```sh
pip3 install PySide6 playsound3
./chord-transition-trainer.py
```

### Build a binary executable blob

The following should place an executable in `dist/chord-transition-trainer`

```sh
python3 -m venv .venv
source .venv/bin/activate
pip3 install PySide6 pyinstaller playsound3
pyinstaller --name "chord-transition-trainer" --windowed --onefile chord-transition-trainer.py
deactivate
```

## Operation

+ One can increase the probability of a particular chord being
  presented by entering it multiple times on the list.

+ The program can save and restore your settings. The data is stored
  in plaintext at:
  $XDG_CONFIG_HOME/chord-transition-trainer/chord-transition-trainer.ini

+ When launching the program from a command-line one can pass it a
  list of chords as arguments.

## Dependencies

   The following are the *debian linux* names for the required
   packages. Other operating systems may distribute them under
   slightly different names.

   + python3-pyside6
   + python3-playsound3

   The above may automatically also install the following:

   + pyside6-tools
   + libshiboken6-dev
   + python3-pyside6.qtwidgets
   + python3-pyside6.qtcore
   + python3-pyside6.qtgui
   + python3-playsound3
   + libpyside6-dev

## Feedback:

 * It's best to contact me by opening an 'issue' on the program's github
   repository (see above) or, distant second-best, by direct e-mail.

 * Code contributions are welcome and github starring is appreciated.

## Compatibility

 This package was orginally developed and tested under Debian linux
 13.6 (trixie), using python 3.16 and pyside6 6.8.

## Colophon

* Copyright © 2026, Boruch Baum <boruch_baum@gmx.com>
* Author/Maintainer: Boruch Baum <boruch_baum@gmx.com>
* Homepage: https://github.com/Boruch-Baum/chord-transition-trainer
* SPDX-License-Identifier: GPL-3.0-or-later
