# -*- coding: utf-8 -*-
# Copyright (C) 2010 Holoscopio Tecnologia
# Copyright (C) 2010 Gustavo Noronha Silva <gns@gnome.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import gobject
import pygst
pygst.require("0.10")
import gst

from core import EncodingUI
from sltv.settings import UI_DIR

class VP8EncodingUI(EncodingUI):

    def __init__(self):
        EncodingUI.__init__(self)
        self.interface.add_from_file(UI_DIR + "/encoding/vp8.ui")
        self.vp8_vorbis_box = self.interface.get_object("vp8_vorbis_box")
        self.vp8_quality_entry = self.interface.get_object("vp8_quality_entry")
        self.speed_entry = self.interface.get_object("speed_entry")
        self.vp8_keyframe_entry = self.interface.get_object("vp8_keyframe_entry")
        self.vp8_bitrate_entry = self.interface.get_object("vp8_bitrate_entry")
        self.vorbis_quality_entry = self.interface.get_object("vorbis_quality_entry")
        self.vorbis_bitrate_entry = self.interface.get_object("vorbis_bitrate_entry")

    def get_widget(self):
        return self.vp8_vorbis_box

    def get_name(self):
        return "WebM - vp8 vorbis"

    def get_description(self):
        return "VP8 + Vorbis (WebM) encoding"

    def update_config(self):
        self.vp8_quality_entry.set_text(self.config["vp8_quality"])
        self.speed_entry.set_text(self.config["speed"])
        self.vp8_bitrate_entry.set_text(self.config["vp8_bitrate"])
        self.vp8_keyframe_entry.set_text(self.config["max_keyframe_distance"])
        self.vorbis_quality_entry.set_text(self.config["vorbis_quality"])
        self.vorbis_bitrate_entry.set_text(self.config["vorbis_bitrate"])

    def get_config(self):
        self.config["vp8_quality"] = self.vp8_quality_entry.get_text()
        self.config["speed"] = self.speed_entry.get_text()
        self.config["max_keyframe_distance"] = self.vp8_keyframe_entry.get_text()
        self.config["vp8_bitrate"] = self.vp8_bitrate_entry.get_text()
        self.config["vorbis_quality"] = self.vorbis_quality_entry.get_text()
        self.config["vorbis_bitrate"] = self.vorbis_bitrate_entry.get_text()
        return self.config
