# -*- coding: utf-8 -*-
# Copyright (C) 2010 Holoscopio Tecnologia
# Author: Luciana Fujii Pontello <luciana@holoscopio.com>
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
from threading import Thread
from multiprocessing import Process
import fgdp
try:
    import fgdp
except:
    pass
    
class FGDPOutput(Output):

    def __init__(self):
        Output.__init__(self)        
        self.fgdp_sink = gst.element_factory_make(
                "fgdpsink", "fgdpsink"
        )
        self.queue_fgdp = gst.element_factory_make(
                "queue", None
        )
        self.fgdp_sink.set_property('port', 15000)
        self.add(self.fgdp_sink)
        self.add(self.queue_fgdp)
        self.queue_fgdp.link(self.fgdp_sink)
        self.sink_pad.set_target(self.queue_fgdp.sink_pads().next())

    def config(self, dict):
         self.fgdp_sink.set_property('host', dict["ip"])
         self.fgdp_sink.set_property('port', int(dict["port"]))
         self.fgdp_sink.set_property('username', dict["username"])
         self.fgdp_sink.set_property('password', dict["password"])
         self.fgdp_sink.set_property('version', '0.1')
         self.fgdp_sink.set_property('max-reconnection-delay', 2)
