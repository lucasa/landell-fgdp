# -*- coding: utf-8 -*-
# Copyright (C) 2010 Holoscopio Tecnologia
# Author: Luciana Fujii Pontello
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
from core import Output
import os
from sltv.utils import FileUtil

class FileOutput(Output):

    def __init__(self):
        Output.__init__(self)
        self.file_sink = gst.element_factory_make("filesink", "filesink")
        self.add(self.file_sink)
        self.sink_pad.set_target(self.file_sink.sink_pads().next())

    def config(self, dict):
        if os.path.exists(dict["location"]):
            print "file ouput", dict["location"], "already exists, using", FileUtil.append_time_to_path(dict["location"])
            self.file_sink.set_property("location", FileUtil.append_time_to_path(dict["location"]))
        else:
            self.file_sink.set_property("location", dict["location"])
