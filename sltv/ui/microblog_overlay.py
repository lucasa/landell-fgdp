# -*- coding: utf-8 -*-
# Copyright (C) 2010 Holoscópio Tecnologia
# Author: Luciana Fujii Pontello <luciana@holoscopio.com>
# Author: Thadeu Lima de Souza Cascardo <cascardo@holoscopio.com>
# Author: Marcelo Jorge Vieira <metal@holoscopio.com>
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
from sltv.settings import UI_DIR
import sltv.config as config
from threading import Thread
import twitter
import urllib2
import shutil
import urlparse
import time

class MicroblogOverlayUI:

    def __init__(self, ui, sltv):
        self.ui = ui
        self.sltv = sltv
        self.interface = gtk.Builder()
        self.interface.add_from_file(UI_DIR + "/microblog_overlay.ui")
        self.widget = self.interface.get_object("vbox")

        self.button = self.interface.get_object("apply_button")
        self.clear_button = self.interface.get_object("clear_button")

        self.hashtag_selector_entry = self.interface.get_object(
            "hashtag_entry"
        )        
        editable = getattr(twitter.Api(), "GetSearch", None) is not None
        self.hashtag_selector_entry.set_editable(editable)
        self.hashtag_selector_entry.set_can_focus(editable)
        
        self.interval_selector_entry = self.interface.get_object(
            "interval_entry"
        )
        
        self.username_selector_entry = self.interface.get_object(
            "username_entry"
        )
        
        self.show_selector_entry = self.interface.get_object(
            "show_entry"
        )
        
        self.api_selector_combo = self.interface.get_object(
            "api_combobox"
        )
        try:
            twitter.Api(base_url="http://identi.ca/api")
        except:
            self.api_selector_combo.set_sensitive(False)

        # valign
        self.top_button = self.interface.get_object("top_toolbutton")
        self.bottom_button = self.interface.get_object("bottom_toolbutton")

        self.vertical_group = gtk.ActionGroup("vertical_group")
        vertical_actions = [
            ("top_radioaction", "gtk-goto-top", "Top", None,
                "Top", 0),
            ("bottom_radioaction", "gtk-goto-bottom", "Bottom", None,
                "Bottom", 1)
        ]
        self.vertical_group.add_radio_actions(
                vertical_actions, 0, None, None
        )

        self.top_radioaction = self.vertical_group.get_action("top_radioaction")
        self.top_radioaction.connect_proxy(self.top_button)
        
        self.bottom_radioaction = self.vertical_group.get_action(
                "bottom_radioaction"
        )
        self.bottom_radioaction.connect_proxy(self.bottom_button)

        self._set_config()
        self._load_config()

        self.button.connect("clicked", self.on_apply_clicked)
        self.clear_button.connect("clicked", self.on_clear_clicked)
        self.sltv.connect("preplay", self._preplay)
        self.sltv.connect("playing", self._playing)
        self.sltv.connect("stopped", self._stopped)
        self.top_radioaction.connect("changed", self.on_vertical_changed)
        
        self.update_status = None
        self.hashtag = ""
        self.username = ""
        self.show_time = ""
    	self.interval = ""
        self.valign = None

        self.apis_urls = ["https://api.twitter.com/1", "http://identi.ca/api"]
        self._create_api_combobox(self.api_selector_combo, self.apis_urls)

    def _set_config(self):
        self.config = config.config
        self.section = "Settings"
        self.item = "Twitter Overlay"

    def _load_config(self):
        config_item = self.config.get_item(self.section, self.item)
        if config_item:
            if "hashtag" in config_item:
                self._set_hashtag(config_item['hashtag'])
            if "valign" in config_item:
                self._set_valign(config_item['microblog_valign'])
            if "interval" in config_item:
                self._set_interval(config_item['interval'])
            if "username" in config_item:
                self._set_interval(config_item['username'])
            if "show" in config_item:
                self._set_show(config_item['show'])

    def _create_api_combobox(self, combobox, urls):
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        combobox.set_model(liststore)
        cell = gtk.CellRendererText()
        combobox.pack_start(cell, True)
        combobox.add_attribute(cell, 'text', 0)
        for url in urls:
            liststore.append((url,))
        combobox.set_active(0)

    def _set_valign(self, valign):
        self.valign = valign
        action = self.vertical_group.get_action(self.valign+"_radioaction")
        action.set_active(True)
    
    def _set_hashtag(self, hashtag):
        self.hashtag = hashtag
        self.hashtag_selector_entry.set_text("")
        if hashtag:
            self.hashtag_selector_entry.set_text(hashtag)
    
    def _set_username(self, user):
        self.username = user
        self.username_selector_entry.set_text("")
        if user:
            self.username_selector_entry.set_text(user)

    def _set_interval(self, interval):
        self.interval = interval
        self.interval_selector_entry.set_text("")
        if self.interval:
            self.interval_selector_entry.set_text(interval)
            
    def _set_show(self, show):
        self.show_time = show
        self.show_selector_entry.set_text("")
        if self.show_time:
            self.show_selector_entry.set_text(show)
        
    def on_vertical_changed(self, widget, current):
        name = current.get_name()
        if name == "top_radioaction":
            action = "top"
        elif name == "bottom_radioaction":
            action = "bottom"

        self.valign = action
        self.save()

    def _make_config(self):
        config = {}
        config['username'] = self.username
        config['hashtag'] = self.hashtag
        config['microblog_valign'] = self.valign
        config['interval'] = self.interval
        config['show'] = self.show_time
        return config

    def save(self):
        self.config.set_item(self.section, self.item, self._make_config())

    def _get_hashtag(self):
         return self.hashtag_selector_entry.get_text()
         
    def _get_username(self):
         return self.username_selector_entry.get_text()

    def _get_interval(self):
         return self.interval_selector_entry.get_text()
         
    def _get_show(self):
         return self.show_selector_entry.get_text()

    def update_config(self, text, img, user):
        font = 18
        font = font - len(text)/12
        if font < 10:
            font = 10
        #print len(text), font
        
        max_line = 50
        words = text.split(' ')
        lines = []
        line = ''
        for w in words:
            if len(line) + len(w) < max_line:
                line = line + ' ' + w
            else:
                lines.append(line)
                line = w
        lines.append(line)
        
        #print lines
        text = ''
        i = 0
        for l in lines:
            if len(l) > 0:
                if i == 0:
                    text = l
                else:
                    text = text + '<tspan x="60" dy="1.2em">' + l + '</tspan>'
                i = i+1
        
        if len(text) > 0 and text != ' ':
            if user:
                user = '@'+user
            svg = '<svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><rect x="52" y="10" width="600" height="50" fill="white" style="fill-opacity:0.7"/><text x="60" y="25" fill="black" font-size="'+str(font)+'">'+text+'</text><image x="5" y="10" width="50" height="50" xlink:href="'+img+'" /><text x="5" y="75" fill="red" font-size="12">'+user+'</text></svg>'
        else:
            svg = '<svg width="100%" height="100%"></svg>'
        self.sltv.rsvg.set_property("data", svg)

    def apply_settings(self):
        if self.update_status:
            self.update_status.stop()
            
        if self.sltv.playing:
            self.update_status = UpdateStatus(self.update_config, self.api_selector_combo.get_active_text())
            self.update_status.set_username(self._get_username())
            self.update_status.set_hashtag(self._get_hashtag())
            self.update_status.set_interval(self._get_interval())
            self.update_status.set_show(self._get_show())
            self.update_status.start()

    def _preplay(self, sltv):
        self.apply_settings()

    def _playing(self, sltv):
        self.button.set_sensitive(True)
        if not self.update_status:
            self.update_status = UpdateStatus(self.update_config, self.api_selector_combo.get_active_text())
            self.update_status.set_username(self._get_username())
            self.update_status.set_hashtag(self._get_hashtag())
            self.update_status.set_interval(self._get_interval())
            self.update_status.set_show(self._get_show())
            self.update_status.start()

    def _stopped(self, sltv):
        self.button.set_sensitive(False)
        if self.update_status:
            self.update_status.stop()

    def on_apply_clicked(self, event):
        self.apply_settings()

    def on_clear_clicked(self, event):
        self._set_hashtag("")
        self._set_username("")
        self._set_interval("")
        self._set_show("")
        if self.update_status:
            self.update_status.stop()
            self.update_status = None

    def get_widget(self):
        return self.widget
        
class UpdateStatus(Thread):

    def __init__(self, callback, api_url, user=None, tag=None):
        Thread.__init__(self)
        self.setDaemon(True)
        self.user = user
        self.hashtag = tag
        self.interval = 5.0
        self.show = 5.0
        self.service_url = api_url
        self.file_out = "/tmp/_landell_microblog_avatar.png"
        self.callback = callback
    	try:
	        self.api = twitter.Api(base_url=self.service_url)
        except:
            print "Microblog monitor has no support to the Identi.ca API. Please update the python-twitter library to a version >= 0.8"
            self.api = twitter.Api()
	    
        self.active = False
    
    def stop(self):
        self.callback("", "", "")
        self.active = False
        #print "monitoring thread stopped"
    
    def set_username(self, user):
        if user and len(user) > 0:
            self.user = user
    
    def set_hashtag(self, tag):
        if tag and len(tag) > 0:
            self.hashtag = tag

    def set_interval(self, interval):
        if interval and len(interval) > 0:
            self.interval = float(interval)

    def set_show(self, show):
        if show and len(show) > 0:
            self.show = float(show)

    def run(self):
        statuses = []
        self.active = True
        while self.active:
            if self.user:
                statuses = self.api.GetUserTimeline(self.user)
            elif self.hashtag:
                statuses = self.api.GetSearch(self.hashtag, per_page=30)
            
            i = 0
            print 'Microblog monitor loaded', len(statuses), 'profiles from user [', self.user, '] hashtag [', self.hashtag, '] network [', self.service_url, ']'
            for s in statuses:
                if self.active:
                    #try:
                    #    print i, s.AsJsonString()
                    #except:
                    #    pass
                    url = s.user.profile_image_url
                    text = s.text
                    self.callback("", "", "")
                    if self.download(url, self.file_out):
                        if s.user.name:
                            name = s.user.name
                        else:
                            name = s.user.screen_name
                        time.sleep(self.interval)
                        self.callback(text, self.file_out, name)
                        time.sleep(self.show)
                i = i+1
            time.sleep(self.interval)
            
    def download(self, url, fileName=None):
        def getFileName(url,openUrl):
            if 'Content-Disposition' in openUrl.info():
                # If the response has Content-Disposition, try to get filename from it
                cd = dict(map(
                    lambda x: x.strip().split('=') if '=' in x else (x.strip(),''),
                    openUrl.info().split(';')))
                if 'filename' in cd:
                    filename = cd['filename'].strip("\"'")
                    if filename: return filename
            # if no filename was found above, parse it out of the final URL.
            return os.path.basename(urlparse.urlsplit(openUrl.url)[2])

        try:
            r = urllib2.urlopen(urllib2.Request(url))
            fileName = fileName or getFileName(url,r)
            with open(fileName, 'wb') as f:
                shutil.copyfileobj(r,f)
            return True
        except RuntimeError:
            return False
        finally:
            try:
                r.close()
            except:
                pass
