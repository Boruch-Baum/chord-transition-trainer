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

a) Download the latest binary blob for your operating system :: This
   is the easiest method that takes the least technical know-how.

   [debian](./releases/latest/download/chord-transition-trainer)
   [macOs](./releases/latest/download/chord-transition-trainer.macos)
   [windows](./releases/latest/download/chord-transition-trainer.exe)

b) Run python source code file directly -

   [download latest tar.gz](./releases/latest/download/chord-transition-trainer.tar.gz)
   [download latest zip](./releases/latest/download/chord-transition-trainer.tar.gz)

   See section DEPENDENCIES below for what I think are all the
   packages you'll need to install in order for this to work.

c) Build binary blob

   c.0) download and extract your preferred archive

      [download latest tar.gz](./releases/latest/download/chord-transition-trainer.tar.gz)
      [download latest zip](./releases/latest/download/chord-transition-trainer.tar.gz)

   c.1) create and activate a python virtual environment

       `cd chord-transition-trainer`
       `python3 -m venv .venv`
       `source .venv/bin/activate`

   c.2) install pyinstaller, pyside6, and playsound3

       `pip3 install PySide6 pyinstaller playsound3`

   c.3) build the executable

       `pyinstaller --name "chord-transition-trainer" --windowed --onefile chord-transition-trainer`

   c.4) deactivate the python virtual environment

        `deactivate`

   c.5) find the executable in `dist/ChordTransitionTrainer`

   c.6) everything else you can delete

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
