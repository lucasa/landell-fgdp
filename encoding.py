#!/usr/bin/python

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
import gtk

class Encoding:

	def __init__(self):
		self.interface = gtk.Builder()
		self.interface.add_from_file("encoding.ui")
		dialog = self.interface.get_object("dialog1")

		#Encoding selection
		dv_radiobutton = self.interface.get_object("dv_radiobutton")
		theora_radiobutton = self.interface.get_object("theora_radiobutton")
		encoding_action_group = gtk.ActionGroup("encoding_action_group")
		action_entries = [("theora_action", None, "Ogg Theora", None, "Ogg Theora encoding", 0),
				("dv_action", None, "DV", None, "Uncompressed DV", 1)]
		encoding_action_group.add_radio_actions(action_entries,
				0, self.encoding_changed, None)
		theora_action = encoding_action_group.get_action("theora_action")
		theora_action.connect_proxy(theora_radiobutton)
		dv_action = encoding_action_group.get_action("dv_action")
		dv_action.connect_proxy(dv_radiobutton)
		self.encoding_selection = "theora"

		data = ""

		close_button = self.interface.get_object("close_button")
		close_button.connect("pressed", self.close_dialog, data)
		dialog.connect("delete_event", self.close_dialog)

	def show_window(self):
		dialog = self.interface.get_object("dialog1")
		dialog.show_all()

	def get_video_encoding(self):
		if self.encoding_selection == "theora":
			print "theora_video_enc"
			theoraenc = gst.element_factory_make("theoraenc", "theoraenc")
			return theoraenc
		if self.encoding_selection == "dv":
			print "dv"
			dvenc = gst.element_factory_make("ffenc_dvvideo", "dvenc")
			return dvenc

	def get_audio_encoding(self):
		if self.encoding_selection == "theora":
			print "theora_audio_enc"
			self.audio = gst.Bin()
			audioconvert = gst.element_factory_make("audioconvert", "audioconvert")
			vorbisenc = gst.element_factory_make("vorbisenc", "vorbisenc")
			self.audio.add(audioconvert, vorbisenc)
			gst.element_link_many(audioconvert, vorbisenc)
			source_pad = gst.GhostPad("source_ghost_pad", self.audio.find_unlinked_pad(gst.PAD_SRC))
			sink_pad = gst.GhostPad("sink_ghost_pad", self.audio.find_unlinked_pad(gst.PAD_SINK))
			self.audio.add_pad(source_pad)
			self.audio.add_pad(sink_pad)
			return self.audio
		if self.encoding_selection == "dv":
			print "dv"
			audioconvert = gst.element_factory_make("audioconvert", "audioconvert")
			return audioconvert

	def get_mux(self):
		if self.encoding_selection == "theora":
			print "oggmux"
			oggmux = gst.element_factory_make("oggmux", "oggmux")
			return oggmux
		if self.encoding_selection == "dv":
			print "dv"
			ffmux = gst.element_factory_make("ffmux_dv", "ffmux")
			return ffmux

	def close_dialog(self, button, data):
		dialog = self.interface.get_object("dialog1")
		dialog.hide_all()

	def encoding_changed(self, radioaction, current):
		if current.get_name() == "theora_action":
			self.encoding_selection = "theora"
		if current.get_name() == "dv_action":
			self.encoding_selection = "dv"
