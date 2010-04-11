#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010 Holoscópio Tecnologia
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
import gtk
from sltv.output import *
from sltv.audio import *
from sltv.sltv import *
from sltv.settings import UI_DIR

import about
import sources
import message
import outputs
import sltv.effects



class SltvUI:

    def __init__(self):
        self.interface = gtk.Builder()
        self.interface.add_from_file(UI_DIR + "/sltv.ui")
        self.main_window = self.interface.get_object("window1")
        self.main_window.show_all()
        self.about = about.About(self)

        preview_area = self.interface.get_object("preview_area")
        self.sltv = Sltv(preview_area, self)

        self.play_button = self.interface.get_object("play_button")
        self.stop_button = self.interface.get_object("stop_button")
        self.overlay_button = self.interface.get_object("overlay_button")

        self.outputs = self.sltv.outputs
        self.outputs_ui = outputs.Outputs(self, self.outputs)

        #combobox to choose source

        self.source_combobox = self.interface.get_object("sources_combobox")
        self.sources = self.sltv.sources
        self.sources_ui = sources.Sources(self, self.sources)
        self.source_combobox.set_model(sources.VideoModel(self.sources).model)
        cell = gtk.CellRendererText()
        self.source_combobox.pack_start(cell, True)
        self.source_combobox.add_attribute(cell, "text", 0)
        self.source_combobox.set_active(0)
        self.source_combobox.connect("changed",self.on_switch_source)

        self.on_switch_source(self.source_combobox)

        # audio combobox
        self.audio_sources_combobox = self.interface.get_object("audio_sources_combobox")
        self.audio_sources_combobox.set_model(sources.AudioModel(self.sources).model)
        cell = gtk.CellRendererText()
        self.audio_sources_combobox.pack_start(cell, True)
        self.audio_sources_combobox.add_attribute(cell, "text", 0)
        self.audio_sources_combobox.connect("changed", self.on_select_audio_source)
        self.audio_sources_combobox.set_active(0)

        #menu

        output_menuitem = self.interface.get_object("output_menuitem")
        sources_menuitem = self.interface.get_object("sources_menuitem")
        self.about_menu = self.interface.get_object("about_menu")

        self.video_effect_combobox = self.interface.get_object(
                "video_effect_combobox"
        )
        self.audio_effect_combobox = self.interface.get_object(
                "audio_effect_combobox"
        )
        self.effect_registry = sltv.effects.EffectRegistry()
        self._create_effects_combobox(self.video_effect_combobox, "video")
        self._create_effects_combobox(self.audio_effect_combobox, "audio")
        self.effect_checkbutton = self.interface.get_object(
            "effect_checkbutton"
        )
        self.video_effect_button = self.interface.get_object(
                "video_effect_button"
        )
        self.audio_effect_button = self.interface.get_object(
                "audio_effect_button"
        )
        self.preview_checkbutton = self.interface.get_object(
                "preview_checkbutton"
        )


        self.video_effect_label = self.interface.get_object("video_effect_label")
        self.audio_effect_label = self.interface.get_object("audio_effect_label")

        self.effect_checkbutton.connect("toggled", self.effect_toggled)
        self.preview_checkbutton.connect("toggled", self.preview_toggled)
        self.play_button.connect("clicked", self.on_play_press)
        self.stop_button.connect("clicked", self.on_stop_press)
        self.overlay_button.connect("clicked", self.on_overlay_change)
        self.main_window.connect("delete_event", self.on_window_closed)
        output_menuitem.connect("activate", self.show_output)
        sources_menuitem.connect("activate", self.show_sources)
        self.about_menu.connect("activate", self.show_about)
        self.video_effect_button.connect("clicked", self.effect_changed)
        self.audio_effect_button.connect("clicked", self.effect_changed)

        self.set_effects(False)
        self.preview_state = False
        self.sltv.set_preview(False)
        self.overlay_textview = self.interface.get_object("overlay_textview")
        self.effect_enabled = False

    def _create_effects_combobox(self, combobox, effect_type):
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        combobox.set_model(liststore)
        cell = gtk.CellRendererText()
        combobox.pack_start(cell, True)
        combobox.add_attribute(cell, 'text', 0)
        liststore.append(("none",))
        for etype in self.effect_registry.get_types(effect_type):
            liststore.append((etype,))
        combobox.set_active(0)

    def selected_video_source(self):
        model = self.source_combobox.get_model()
        iter = self.source_combobox.get_active_iter()
        if iter == None:
            return None
        return model.get_value(iter, 0)

    def selected_audio_source(self):
        model = self.audio_sources_combobox.get_model()
        iter = self.audio_sources_combobox.get_active_iter()
        if iter == None:
            return None
        return model.get_value(iter, 0)

    def on_play_press(self, event):
        if self.selected_video_source() == None:
            message.MessageInfo(
                "Please, choose or add a video source.",
                self
            )
            return False

        self.play_button.set_sensitive(False)
        self.play()
        self.stop_button.set_sensitive(True)

    def play(self):
        if not self.sltv.playing():
            overlay_buffer = self.overlay_textview.get_buffer()
            overlay_text = overlay_buffer.get_text(
                overlay_buffer.get_start_iter(),
                overlay_buffer.get_end_iter(),
                True
            )
            video_effect_name = self.video_effect_combobox.get_active_text()
            audio_effect_name = self.audio_effect_combobox.get_active_text()
            self.overlay_button.set_sensitive(True)
            if self.effect_enabled == True:
                if self.selected_audio_source() == None:
                    self.audio_effect_button.set_sensitive(False)
                else:
                    self.audio_effect_button.set_sensitive(True)
                self.video_effect_button.set_sensitive(True)
            self.sltv.set_overlay_text(overlay_text)
            self.sltv.set_video_effect_name(video_effect_name)
            self.sltv.set_audio_effect_name(audio_effect_name)
            self.sltv.play()
        self.audio_sources_combobox.set_sensitive(False)

    def on_switch_source(self, combobox):
        source_name = self.selected_video_source()
        self.sltv.set_video_source(source_name)

    def on_select_audio_source(self, combobox):
        source_name = self.selected_audio_source()
        self.sltv.set_audio_source(source_name)

    def show_encoding(self, menuitem):
        self.sltv.show_encoding()

    def show_output(self, menuitem):
        self.outputs_ui.show_window()

    def show_sources(self, menuitem):
        self.sources_ui.show_window()

    def show_about(self, menuitem):
        self.about.show_window()

    def set_effects(self, state):
        self.video_effect_combobox.set_sensitive(state)
        self.audio_effect_combobox.set_sensitive(state)
        self.video_effect_label.set_sensitive(state)
        self.audio_effect_label.set_sensitive(state)
        if self.sltv.playing() and state == True:
            self.video_effect_button.set_sensitive(True)
            if self.selected_audio_source() == None:
                self.audio_effect_button.set_sensitive(False)
            else:
                self.audio_effect_button.set_sensitive(True)
        elif self.sltv.playing() and state == False:
            self.video_effect_button.set_sensitive(False)
            self.audio_effect_button.set_sensitive(False)

        self.effect_enabled = state
        self.sltv.set_effects(state)
        #Send signal

    def effect_toggled(self, checkbox):
        self.set_effects(not self.effect_enabled)

    def effect_changed(self, button):
        if self.effect_enabled:
            print "sending change_effect"
            if button is self.video_effect_button:
                self.sltv.change_effect(
                        self.video_effect_combobox.get_active_text(), MEDIA_VIDEO
                )
            else:
                self.sltv.change_effect(
                        self.audio_effect_combobox.get_active_text(), MEDIA_AUDIO
                )

    def preview_toggled(self, checkbox):
        self.preview_state = not self.preview_state
        self.sltv.set_preview(self.preview_state)

    def on_stop_press(self, event):
        self.stop_button.set_sensitive(False)
        self.stop()
        self.play_button.set_sensitive(True)

    def stop(self):
        if self.sltv.playing():
            self.overlay_button.set_sensitive(False)
            self.audio_effect_button.set_sensitive(False)
            self.video_effect_button.set_sensitive(False)
            self.audio_sources_combobox.set_sensitive(True)
            self.sltv.stop()

    def on_window_closed(self, event, data):
        gtk.main_quit()

    def on_overlay_change(self, event):
        overlay_buffer = self.overlay_textview.get_buffer()
        overlay_text = overlay_buffer.get_text(
            overlay_buffer.get_start_iter(),
            overlay_buffer.get_end_iter(),
            True
        )
        self.sltv.change_overlay(overlay_text)
