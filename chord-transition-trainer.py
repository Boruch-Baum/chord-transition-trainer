#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Boruch Baum
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# The following is the text appears in the program's
# pop-up "About / Help" window.
ABOUT_HTML_TEXT="""<h1>Chord Transition Trainer</h1>

<b>SUMMARY:</b> PyQt application for practicing chord transitions,
with adjustable timing and probabilities.<p>

<b>DESCRIPTION:</b> One enters a list of chords (space-delimited
plain-text), selects how fast to practice transitioning (integer
seconds), for how long (integer minutes and seconds), and whether the
practice should be accompanied by audible metronome ticks (60 bpm).
When one presses the 'start' button, the program displays the current
chord for the student to play, an arrow, a preview of the chord to
transition to, and a progress bar giving a visual indication of how
much time remains before needing to perform the transition. Chords are
selected randomly from the plain-text list. A chord's probability of
being selected can be increased by adding duplicate entries for it on
the list. On-screen settings have been added for various cosmetic
customizations, such a font size, GUI colors, etc. All settings can be
saved and restored to/from a plain-text configuration file.<p>

<b>KEYBOARD-FRIENDLINESS:</b> One should be able to navigate the GUI using
keys such as TAB, SPACE, ENTER, ESC, etc.<p>

<b>COMMAND-LINE USAGE:</b> One can pass a list of chords to the
program as command-line arguments.<p>

<b>BLOAT:</b> The self-contained binary executable of this program is
on the order of 20x the size of the python source code, so if you care
about bloat and have many/most/all of the python libraries installed
anyway, you can save the space by running the source code file
directly instead of the binary blob. For a debian linux system, the
following dependencies are necessary: pyside6-tools libshiboken6-dev
python3-pyside6.qtwidgets python3-pyside6.qtcore python3-pyside6.qtgui
python3-playsound3 libpyside6-dev<p>

<b>LICENSE:</b> This is free open-source software, distributed under the
GPLv3 or greater license.<p>

<p>
File:    chord-transition-trainer<br>
Author:  Boruch Baum &lt;boruch_baum@gmx.com&gt;<br>
URL:     https://github.com/Boruch_Baum/chord-transition-trainer<br>
Created: 2026-07-16<br>
License: GPLv3+<br>
Version: 1.0
 """

__author__  = "Boruch Baum"
__url__     = "https://github.com/Boruch_Baum/chord-transition-trainer"
__email__   = "boruch_baum@gmx.com"
__license__ = "GPL-3.0-or-later"
__version__ = "1.0"

WHITE_ICON=":/icons/icon_16_white.svg"
BLACK_ICON=":/icons/icon_16_black.svg"
INVALID_CHORD="??"

from assets import resources_rc
import math
import os
from pathlib import Path
from playsound3 import playsound
from PySide6.QtCore import (
    Qt,
    QSettings,
    QTimer
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QKeyEvent,
    QPalette
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QStyle,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget
)
import random
import sys
import struct
import wave

class TextWindow(QDialog):
    """
    Scrollable text box, used for 'About / Help' pop-up
    """
    def __init__(self, parent=None, initial_text=""):
        super().__init__(parent)
        self.resize(400, 700)
        self.text_box = QTextEdit(self)
        self.text_box.setHtml(initial_text)
        self.text_box.setReadOnly(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.text_box)

class MainWindow(QWidget):
    """
    Displays chords, progress, and settings widgets
    """
    MIN_CHORDS=3
    MIN_CHORD_MESSAGE="Minimum three unique chords required: e.g. C D Em G7."
    MIN_CHORD_ERR_MESSAGE="Enter at least THREE unique chords (space-separated)."

    def __init__(self, chord_list: list[str],
                       app: QApplication,
                       app_name: str,
                       tick_path: str | os.PathLike[str]):
        super().__init__()
        self.app = app
        self.app_name = app_name
        self.chord_list = chord_list[:] if chord_list else []
        self.tick_path = tick_path
        self.setWindowTitle("Boruch's Amazing Chord Transition Trainer")
        self._set_defaults()
        self._set_initial_state_values()
        self._create_display_widgets()
        self._create_and_layout_controls()
        self._create_main_layout()
        self._load_ini_file_settings()
        self._get_initial_chord_text_list(chord_list)
        self._validate_chord_text_input_box()
        self._apply_styles()
        self._setup_interval_progress()
        self._update_time_elapsed_text()
        self._setup_timer()
        self._setup_icons()
        self._ensure_width_for_text()
        self.start_button.setFocus()
        # end __init__ for MainWindow

    # --- About / Help Information  ---

    def _about_dialog(self):
        about_window = TextWindow(self, initial_text=ABOUT_HTML_TEXT)
        about_window.exec()

    # ---------- Settings -----------

    def _make_settings(self) -> QSettings:
        # Use exe name for both org and app
        return QSettings(
            QSettings.IniFormat,
            QSettings.UserScope,
            self.app_name,
            self.app_name,
            self,
        )

    def _set_initial_state_values(self):
        self.running = False
        self.elapsed_session_seconds = 0
        self.elapsed_interval_seconds = 0
        self.current = self.next = INVALID_CHORD

    def _set_defaults(self):
        self.interval_seconds = 4
        self.interval_ms = self.interval_seconds * 1000
        self.mute_audio = True
        self.duration_minutes = 0
        self.duration_seconds = 30
        self.duration_total_seconds = self.duration_minutes * 60 + self.duration_seconds
        self.background_color = QColor("white")
        self.foreground_color = QColor("black")
        self.border_color = QColor("lightgray")
        self.font_size = 96
        self.interval_bar_color = QColor("deepskyblue")
        self.interval_bar_height = 32

    def _validate_chord_text_input_box(self) -> bool:
        is_valid = self._update_chord_list_from_box()
        self._set_chords_valid(is_valid)
        if is_valid:
            self._pick_initial_current_next_chords()
        else:
            self.current = self.next = INVALID_CHORD
        self._update_transition_text()
        return is_valid

    def _get_initial_chord_text_list(self, chord_list: list[str]):
        """
        Retrieves chord list from command line or ini file.
        Puts the text in window's text input / edit box.
        """
        if chord_list:
            initial_text = " ".join(chord_list)
        elif self.ini_file_chords_list:
            initial_text = self.ini_file_chords_list
        else:
            initial_text = ""
        self.chord_text_box.setText(initial_text)

    def _load_ini_file_settings(self) -> str | None:
        s = self._make_settings()
        x = s.value("window/x", None, type=int)
        y = s.value("window/y", None, type=int)
        w = s.value("window/w", None, type=int)
        h = s.value("window/h", None, type=int)
        if None not in (x, y, w, h):
            self.setGeometry(x, y, w, h)
        self.ini_file_chords_list = s.value("main/chords", "", type=str)
        if self.ini_file_chords_list:
            self.chord_text_box.setText(self.ini_file_chords_list)
        interval_seconds = s.value("main/interval_seconds", "", type=int)
        if interval_seconds:
            self.interval_seconds = interval_seconds
            self.interval_ms = self.interval_seconds * 1000
            self.interval_spin.setValue(interval_seconds)
        self.mute_audio = s.value("main/mute_audio", True, type=bool)
        self.mute.setChecked(self.mute_audio)
        duration_minutes = s.value("main/session_duration_minutes", "", type=int)
        if duration_minutes:
            self.duration_minutes = duration_minutes
            self.duration_min_spin.setValue(self.duration_minutes)
        duration_seconds = s.value("main/session_duration_seconds", "", type=int)
        if duration_seconds:
            self.duration_seconds = duration_seconds
            self.duration_sec_spin.setValue(self.duration_seconds)
        font_size = s.value("main/font_size", "", type=int)
        if font_size:
            self.font_size = font_size
            self.font_spin.setValue(self.font_size)
        interval_bar_height = s.value("main/interval_bar_height", "", type=int)
        if interval_bar_height:
            self.interval_bar_height = interval_bar_height
            self.bar_height_spin.setValue(self.interval_bar_height)
        update_color = False
        background_color = s.value("colors/background_color")
        if isinstance(background_color, QColor):
            update_color = True
            self.background_color = background_color
        foreground_color = s.value("colors/foreground_color")
        if isinstance(foreground_color, QColor):
            update_color = True
            self.foreground_color = foreground_color
        border_color = s.value("colors/border_color")
        if isinstance(border_color, QColor):
            update_color = True
            self.border_color = border_color
        interval_bar_color = s.value("colors/interval_bar_color_color")
        if isinstance(interval_bar_color, QColor):
            update_color = True
            self.interval_bar_color_color = interval_bar_color
        if update_color:
            self._apply_styles()

    def _save_settings(self):
        s = self._make_settings()
        s.setValue("main/chords", self.chord_text_box.text())
        s.setValue("main/mute_audio", self.mute.isChecked())
        s.setValue("main/interval_seconds", self.interval_seconds)
        s.setValue("main/session_duration_minutes", self.duration_minutes)
        s.setValue("main/session_duration_seconds", self.duration_seconds)
        s.setValue("main/font_size", self.font_size)
        s.setValue("main/interval_bar_height", self.interval_bar_height)
        s.setValue("colors/background_color", self.background_color)
        s.setValue("colors/foreground_color", self.foreground_color)
        s.setValue("colors/border_color", self.border_color)
        s.setValue("colors/interval_bar_color", self.interval_bar_color)
        s.setValue("window/x", self.x())
        s.setValue("window/y", self.y())
        s.setValue("window/w", self.width())
        s.setValue("window/h", self.height())
        s.sync()

    # ---------- Icons ----------

    def _is_dark_palette(self) -> bool:
        p = self.app.palette()
        bg = p.color(QPalette.ColorRole.Window)
        fg = p.color(QPalette.ColorRole.WindowText)
        bg_luma = 0.2126 * bg.red() + 0.7152 * bg.green() + 0.0722 * bg.blue()
        fg_luma = 0.2126 * fg.red() + 0.7152 * fg.green() + 0.0722 * fg.blue()
        return bg_luma < fg_luma

    def _setup_icons(self):
        if self._is_dark_palette():
            self.icon = QIcon(WHITE_ICON)
        else:
            self.icon = QIcon(BLACK_ICON)
        self.setWindowIcon(self.icon)
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.icon)
        menu = QMenu()
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.app.quit)
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.setToolTip("Chord Transition Trainer")
        self.tray.show()

    # ---------- Chord List  ----------

    def _is_text_valid(self, text: str) -> bool | list[str]:
        text = text.strip()
        if not text:
            return False
        parts = text.split()
        if len( list(dict.fromkeys(parts) ) ) >= self.MIN_CHORDS:
            return parts
        else:
            return False

    def _update_chord_list_from_box(self) -> bool:
        """
        Always populate self.chord_list, keeping duplicates
        for probability weighting
        """
        text = self.chord_text_box.text()
        is_valid = self._is_text_valid(text)
        self.chord_list = is_valid[:] if is_valid else [INVALID_CHORD]
        return is_valid

    # ---------- CURRENT / NEXT CHORDS ----------

    def _set_chords_valid(self, valid: bool):
        """
        Set style and message based upon validity of chords text box.
        This performs live update of the chord text box, and updates
        the transition text.
        """
        chords_label_font = self.chords_label.font()
        if valid:
            chords_label_font.setBold(True)
            self.chords_label.setFont(chords_label_font)
            self.chords_label.setStyleSheet("")      # revert to theme colors
            self.chord_text_box.setStyleSheet("")    # default QLineEdit look
            self.chords_help.setText("")
            self._pick_initial_current_next_chords()
        else:
            chords_label_font.setBold(True)
            self.chords_label.setFont(chords_label_font)
            self.chords_label.setStyleSheet("color: red;")
            self.chord_text_box.setStyleSheet(" QLineEdit { border: 2px solid red; } ")
            self.chords_help.setText(self.MIN_CHORD_ERR_MESSAGE)
            self.current = self.next = INVALID_CHORD
        self._update_transition_text()

    def _chords_text_changed(self, _text: str):
        """
        Live validation while typing: update styling immediately
        based on whether we have at least three unique chords.
        """
        text = self.chord_text_box.text()
        is_valid = self._is_text_valid(text)
        self._set_chords_valid(is_valid)
        if is_valid:
            self.chords_help.setText("")
        else:
            self.chords_help.setText(self.MIN_CHORD_ERR_MESSAGE)
            self.current = self.next = INVALID_CHORD
            self.stop_session()

    def _pick_initial_current_next_chords(self):
        parts = self._is_text_valid( self.chord_text_box.text() )
        if not parts:
            self.current = self.next = INVALID_CHORD
            return
        self.chord_list = parts
        self.current = random.choice(self.chord_list)
        candidates = [c for c in self.chord_list if c != self.current]
        self.next = random.choice(candidates)

    def _advance_chords(self):
        """
        Update for next chord transition.
        """
        self.current = self.next
        candidates = [c for c in self.chord_list if c != self.current]
        self.next = random.choice(candidates)

    def _update_transition_text(self):
        self.chord_transition_text.setText(f"{self.current}  →  {self.next}")
        self._ensure_width_for_text()

    # ---------- Styles ----------

    def _apply_styles(self):
        bg = self.background_color
        fg = self.foreground_color
        border = self.border_color
        self.chord_transition_text.setStyleSheet(f"""
            QLabel {{
                background-color: rgba({bg.red()}, {bg.green()}, {bg.blue()}, {bg.alpha()});
                color: {fg.name()};
                border: 2px solid {border.name()};
                padding: 16px;
                font-family: "Noto Sans";
                font-size: {self.font_size}px;
                font-weight: 600;
            }}
        """)
        self._apply_interval_progress_styles()
        self._apply_time_elapsed_text_style()

    def _setup_interval_progress(self):
        self.interval_progress.setRange(0, self.interval_seconds)
        self.interval_progress.setValue(0)
        self.interval_progress.setFormat("%v s")
        self._apply_interval_progress_styles()

    def _apply_interval_progress_styles(self):
        height = self.interval_bar_height
        color = self.interval_bar_color.name()
        self.interval_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #888;
                border-radius: 3px;
                text-align: center;
                min-height: {height}px;
                max-height: {height}px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)

    def _apply_time_elapsed_text_style(self):
        frame_color = self.border_color.lighter(140)
        bg = self.background_color
        text_color = self.foreground_color
        self.time_elapsed_text.setStyleSheet(f"""
            QLabel {{
                background-color: rgba({bg.red()}, {bg.green()}, {bg.blue()}, {bg.alpha()});
                color: {text_color.name()};
                border: 1px solid {frame_color.name()};
                border-radius: 4px;
                padding-top: 0px;
                padding-bottom: 0px;
                padding-left: 32px;
                padding-right: 32px;
                font-size: 11px;
            }}
        """)

    # ---------- Widgets and Layouts ---

    def _create_main_layout(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.addWidget(self.chord_transition_text)
        outer.addWidget(self.interval_progress)
        outer.addWidget(self.controls_box)

    def _create_display_widgets(self):
        self.chord_transition_text = QLabel("")
        self.chord_transition_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chord_transition_text.setWordWrap(False)
        self.interval_progress = QProgressBar()
        self.interval_progress.setTextVisible(True)
        self.time_elapsed_text = QLabel("")
        self.time_elapsed_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Helper message below the text box of space-delimited chords
        self.chords_help = QLabel("")
        help_font = self.chords_help.font()
        help_font.setPointSize(help_font.pointSize() - 1)
        self.chords_help.setFont(help_font)
        self.chords_help.setStyleSheet("color: #ff6666;")  # soft red

    def _create_and_layout_controls(self):
        # Chords text box: space-delimited chords
        self.chord_text_box = QLineEdit()
        self.chord_text_box.setPlaceholderText(self.MIN_CHORD_MESSAGE)
        if self.chord_list:
            self.chord_text_box.setText(" ".join(self.chord_list))
        self.chord_text_box.textChanged.connect(self._chords_text_changed)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 5)
        self.interval_spin.setValue(self.interval_seconds)
        self.interval_spin.setSingleStep(1)
        self.interval_spin.valueChanged.connect(self._interval_changed)

        self.mute = QCheckBox("Mute")
        # self.mute.setChecked(bool(self.mute_audio))
        self.mute.toggled.connect(self._mute_changed)

        self.duration_min_spin = QSpinBox()
        self.duration_min_spin.setRange(0, 59)
        self.duration_min_spin.setValue(self.duration_minutes)
        self.duration_min_spin.valueChanged.connect(self._duration_changed)

        self.duration_sec_spin = QSpinBox()
        self.duration_sec_spin.setRange(0, 59)
        self.duration_sec_spin.setValue(self.duration_seconds)
        self.duration_sec_spin.valueChanged.connect(self._duration_changed)

        self.font_spin = QSpinBox()
        self.font_spin.setRange(10, 200)
        self.font_spin.setValue(self.font_size)
        self.font_spin.valueChanged.connect(self._font_changed)

        self.bar_height_spin = QSpinBox()
        self.bar_height_spin.setRange(4, 64)
        self.bar_height_spin.setValue(self.interval_bar_height)
        self.bar_height_spin.valueChanged.connect(self._bar_height_changed)

        grid = QGridLayout()
        row = 0

        chords_label = QLabel("Chords to practice:")
        chords_label_font = chords_label.font()
        chords_label_font.setPointSize(chords_label_font.pointSize() + 1)
        chords_label_font.setBold(True)
        chords_label.setFont(chords_label_font)
        self.chords_label = chords_label
        grid.addWidget(self.chords_label, row, 0, 1, 2)
        grid.addWidget(self.chord_text_box, row, 2, 1, 5)
        row += 1

        # Helper message aligned under the text box
        grid.addWidget(self.chords_help, row, 2, 1, 5)
        row += 1

        grid.addWidget(QLabel("Settings:"), row, 0)
        grid.addWidget(QLabel("Interval:"), row, 1)
        grid.addWidget(self.interval_spin, row, 2)
        grid.addWidget(QLabel("seconds"), row, 3)
        row += 1

        grid.addWidget(QLabel("Duration:"), row, 1)
        grid.addWidget(self.duration_min_spin, row, 2)
        grid.addWidget(QLabel("minutes"), row, 3)
        grid.addWidget(self.duration_sec_spin, row, 4)
        grid.addWidget(QLabel("seconds"), row, 5)
        row += 1

        grid.addWidget(QLabel("Font size:"), row, 1)
        grid.addWidget(self.font_spin, row, 2)
        row += 1

        grid.addWidget(QLabel("Bar height:"), row, 1)
        grid.addWidget(self.bar_height_spin, row, 2)
        grid.addWidget(self.mute, row, 6)
        row += 1

        fg_button = QPushButton("Text")
        bg_button = QPushButton("Background")
        border_button = QPushButton("Border")
        bar_color_button = QPushButton("Bar")

        fg_button.clicked.connect(self._pick_fg_color) # Text color
        bg_button.clicked.connect(self._pick_bg_color)
        border_button.clicked.connect(self._pick_border_color)
        bar_color_button.clicked.connect(self._pick_interval_bar_color)

        secondary_style = """
            QPushButton {
                font-size: 11px;
                padding: 4px 8px;
            }
        """
        for button in (fg_button, bg_button, border_button, bar_color_button):
            button.setStyleSheet(secondary_style)

        colors_layout = QHBoxLayout()
        colors_layout.addWidget(QLabel("Colors:"))
        colors_layout.addSpacing(5)
        colors_layout.addWidget(fg_button)
        colors_layout.addWidget(bg_button)
        colors_layout.addWidget(border_button)
        colors_layout.addWidget(bar_color_button)
        colors_layout.addStretch(1)
        grid.addLayout(colors_layout, row, 1, 1, 4)
        row += 1

        save_button = QPushButton("Save settings")
        save_button.clicked.connect(self._save_settings)
        load_button = QPushButton("Load settings")
        load_button.clicked.connect(self._load_ini_file_settings)
        about_button = QPushButton("About / Help")
        about_button.clicked.connect(self._about_dialog)
        save_load_layout = QHBoxLayout()
        save_load_layout.addWidget(save_button)
        save_load_layout.addWidget(load_button)
        save_load_layout.addWidget(about_button)
        grid.addLayout(save_load_layout, row, 1, 1, 6)
        row += 1

        fixed_spacer = QSpacerItem(
            0, 20,
            QSizePolicy.Minimum,
            QSizePolicy.Fixed
        )
        grid.addItem(fixed_spacer, row, 0)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        quit_button = QPushButton("Exit")

        primary_font = QFont("Noto Sans", 13)
        primary_font.setBold(True)

        for button in (self.start_button, self.stop_button, quit_button):
            button.setFont(primary_font)
            button.setMinimumWidth(90)
            button.setMinimumHeight(32)

        self.start_button.clicked.connect(self.start_session)
        self.stop_button.clicked.connect(self.stop_session)
        quit_button.clicked.connect(self.app.quit)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.time_elapsed_text)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(quit_button)

        box = QGroupBox("")
        box_layout = QVBoxLayout(box)
        box_layout.addLayout(grid)
        box_layout.addLayout(buttons_layout)
        self.controls_box = QWidget()
        v = QVBoxLayout(self.controls_box)
        v.setContentsMargins(0, 5, 0, 0)
        v.addWidget(box)

    # ---------- Slots ----------

    def _interval_changed(self, value_s: int):
        self.interval_seconds = value_s
        self.elapsed_interval_seconds = 0

    def _mute_changed(self, checked: bool):
        self.mute_audio = checked

    def _duration_changed(self, _):
        self.duration_minutes = self.duration_min_spin.value()
        self.duration_seconds = self.duration_sec_spin.value()
        self.duration_total_seconds = self.duration_minutes * 60 + self.duration_seconds
        if not self.running:
            self.elapsed_session_seconds = 0
        self._update_time_elapsed_text()

    def _font_changed(self, value: int):
        self.font_size = value
        self._apply_styles()
        self._ensure_width_for_text()

    def _bar_height_changed(self, value: int):
        self.interval_bar_height = value
        self._apply_interval_progress_styles()

    # ---------- Color picker button click functions ----------

    def _pick_color(self, color_field: str, text_label: str) -> bool:
        """
        Generic color picker shared by all.
        """
        color = QColorDialog.getColor(getattr(self,color_field), self, text_label)
        if color.isValid():
            setattr(self, color_field, color)
            self._apply_styles()
            return True
        else:
            return False

    def _pick_bg_color(self):
        self._pick_color("background_color", "Pick background color")

    def _pick_fg_color(self):
        self._pick_color("foreground_color", "Pick text color")

    def _pick_border_color(self):
        self._pick_color("border_color", "Pick border color")

    def _pick_interval_bar_color(self):
        if self._pick_color("interval_bar_color", "Pick interval bar color"):
            self._apply_interval_progress_styles()

    # ---------- Session control ----------

    def start_session(self):
        """
        Begin a practice session. Initialize values, start timers,
        and update visuals.
        """
        if self.running or ( self.current == INVALID_CHORD ):
            return
        self.elapsed_session_seconds = 0
        self.elapsed_interval_seconds = 0
        self._setup_interval_progress()
        self._update_time_elapsed_text()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self._setup_timer()
        self.session_timer.start()
        self.running = True

    def stop_session(self):
        """
        Cleanly end a practice session.
        """
        if not self.running:
            return
        self.session_timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.running = False

    # ---------- Timer ----------

    def _setup_timer(self):
        self.session_timer = QTimer(self)
        self.session_timer.timeout.connect(self._on_timer_tick)
        self.session_timer.setInterval(1000)

    def _on_timer_tick(self):
        """
        Timer function. Update counters and displays.
        Optionally make a 'tick' sound.
        """
        self.elapsed_session_seconds += 1
        self.elapsed_interval_seconds += 1
        if self.elapsed_interval_seconds >= self.interval_seconds:
            self.elapsed_interval_seconds = 0
            self._advance_chords()
            self._update_transition_text()
        if not self.mute_audio:
            playsound(self.tick_path, block=False)
        self._update_time_elapsed_text()
        self.interval_progress.setValue(self.elapsed_interval_seconds)
        if self.elapsed_session_seconds >= self.duration_total_seconds:
            self.stop_session()
            return

    def _update_time_elapsed_text(self):
        """
        Textually show how long the training has been running.
        The text appears embedded in the progress bar, in the form
        elapsed mm:ss / total mm:ss.
        """
        self.time_elapsed_text.setText(
            f"{ int(self.elapsed_session_seconds // 60):02d}:" +
            f"{ int(self.elapsed_session_seconds  % 60):02d} / " +
            f"{self.duration_minutes:02d}:{self.duration_seconds:02d}"
        )
        self._apply_time_elapsed_text_style()

    # ---------- Dynamic width ----------

    def _ensure_width_for_text(self):
        """
        Dynamically resize window so chord text doesn't wrap or hide.
        """
        metrics = self.chord_transition_text.fontMetrics()
        text = self.chord_transition_text.text()
        if not text:
            return
        text_width = metrics.horizontalAdvance(text)
        needed = text_width + 100
        current_width = self.width()
        if needed > current_width:
            self.resize(needed, self.height())

    # ---------- Hotkeys: ESC, SPACE, ENTER/RETURN ----------

    def keyPressEvent(self, event: QKeyEvent):
        """
        Custom handlers for certain keyboard actions.
        """
        key = event.key()
        focus_widget = self.focusWidget()

        # ESC: stop if running, else quit app
        if key == Qt.Key_Escape:
            if self.running:
                self.stop_session()
            else:
                self.app.quit()
            return

        # SPACE behavior
        if key == Qt.Key_Space:
            # Only treat SPACE as normal when focus is inside the chords box
            if focus_widget is self.chord_text_box:
                super().keyPressEvent(event)
                return

            # Everywhere else: toggle start/stop
            if self.running:
                self.stop_session()
            else:
                self.start_session()
            return

        # ENTER/RETURN behavior
        if key in (Qt.Key_Return, Qt.Key_Enter):
            if focus_widget is self.chord_text_box:
                # Inside chords box: behave like TAB (move focus forward)
                self.focusNextChild()
                return
            else:
                # Outside chords box: behave like SPACE (toggle)
                if self.running:
                    self.stop_session()
                else:
                    self.start_session()
                return

        # Fallback: default handling for all other keys
        super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        """
        QT hook for customizing behavior such as keypresses.
        """
        # Intercept key presses globally
        if event.type() == event.Type.KeyPress:
            key = event.key()
            focus_widget = self.focusWidget()

            # ESC: stop if running, else quit app
            # The isActivewindow check is to prevent closing when the
            # child 'About / Help' window is open
            if key == Qt.Key_Escape and self.isActiveWindow():
                if self.running:
                    self.stop_session()
                    # After stopping, make Start the obvious next action
                    self.start_button.setFocus()
                else:
                    self.app.quit()
                event.accept()
                return True  # consume event

            # SPACE behavior
            if key == Qt.Key_Space:
                # Normal space only in chords box
                if focus_widget is self.chord_text_box:
                    return False  # let normal handling happen

                # Everywhere else: toggle start/stop and move focus
                if self.running:
                    self.stop_session()
                    self.start_button.setFocus()
                else:
                    self.start_session()
                    self.stop_button.setFocus()
                event.accept()
                return True  # don't let buttons see it as "click"

            # ENTER/RETURN behavior
            if key in (Qt.Key_Return, Qt.Key_Enter):
                if focus_widget is self.chord_text_box:
                    # Inside chords box: behave like TAB (move focus forward)
                    self.focusNextChild()
                    event.accept()
                    return True
                else:
                    # Outside chords box: behave like SPACE (toggle) and move focus
                    if self.running:
                        self.stop_session()
                        self.start_button.setFocus()
                    else:
                        self.start_session()
                        self.stop_button.setFocus()
                    event.accept()
                    return True
        # For everything else, fall back to default filtering
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        """
        QT exit hook: Ensure we stop timers and quit the app cleanly.
        Quit the Qt event loop so control returns to the terminal.
        """
        if self.running:
            self.stop_session()
        self.app.quit()
        event.accept()

    # ---------- End: Class Chordbox ----------

def create_tick_wav(tick_path: str | os.PathLike[str],
                    frequency: int = 1000,
                    duration_ms: int = 30):
    """
    Create a small file with a short audio clip resembling a metronome tick.
    """
    if os.path.exists(tick_path):
        return tick_path
    sample_rate = 44100
    num_samples = int(sample_rate * duration_ms / 1000.0)
    amplitude = 0.4 * 32767  # avoid clipping
    with wave.open(tick_path, "wb") as wf:
        wf.setnchannels(1)        # mono
        wf.setsampwidth(2)        # 16-bit
        wf.setframerate(sample_rate)
        for n in range(num_samples):
            t = n / sample_rate
            s = math.sin(2 * math.pi * frequency * t)  # sine wave
            sample_val = int(amplitude * s)
            wf.writeframes(struct.pack("<h", sample_val))

def configure_settings_path():
    """
    Use XDG_CONFIG_HOME as base for storing ini and wav files.
    """
    app_name   = os.path.splitext( os.path.basename(sys.argv[0]) )[0]
    xdg_config = Path( os.environ.get( "XDG_CONFIG_HOME",
                                       os.path.join(os.path.expanduser("~"),
                                       ".config") ) )
    app_config_dir = xdg_config / app_name
    app_config_dir.mkdir(parents=True, exist_ok=True)
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(
        QSettings.IniFormat,
        QSettings.UserScope,
        str(xdg_config)
    )
    return app_name, app_config_dir

def main(argv):
    """
    Currently, the only acceptable command-line arguments are chord strings.
    """
    app = QApplication(argv)
    app_name, app_config_dir = configure_settings_path()
    app.setOrganizationName(app_name)
    app.setApplicationName(app_name)
    tick_path = os.path.join(app_config_dir, "tick.wav")
    create_tick_wav(tick_path)
    w = MainWindow(argv[1:], app, app_name, tick_path)
    app.installEventFilter(w)  # let MainWindow see all app events
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
