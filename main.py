#!/usr/bin/env python
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Author: Don Atherton
# Web: donatherton.co.uk
# WeatherWidget (c) Don Atherton don@donatherton.co.uk

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio, WebKit2
from urllib import request
from datetime import datetime
import json
import os
from sys import exit
import hourly
import five_days
import prefs
import utils

class Win(Gtk.Window):
  def __init__(self):
    Gtk.Window.__init__(self, type=Gtk.WindowType.TOPLEVEL)
    self.prefs_values = []
    self.path = os.path.dirname(__file__)

    prefs_file = self.path + os.sep + 'prefs'
    default_prefs = {
      'appid': 'API key from https://home.openweathermap.org',
      'lat': '51.5',
      'lon': '0.0',
      'loc': 'London',
      'temp_unit': 'C',
      'speed_unit': 'mph',
      'timeout': '15',
      'font_size': '12',
      'x': '250',
      'y': '10'
    }
    try:
      with open(prefs_file, 'r') as file_object:
        self.prefs_values = {}
        for line in file_object:
          pref_value = line.split(',')
          self.prefs_values[pref_value[0]] = pref_value[1].strip()
    except (IndexError, FileNotFoundError):
      print('No prefs file')
      print('API key required')
      self.prefs_values = default_prefs
      # Bring up prefs dialog
      prefs.prefs(self, [250, 10])

    # CSS
    css = bytes('window {font-size: ' + str(self.prefs_values['font_size']) + 'px;}', 'UTF-8')
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    try:
      custom = Gtk.CssProvider()  # From custom.css file
      custom.load_from_file(Gio.File.new_for_path(self.path + os.sep + 'custom.css'))
      Gtk.StyleContext.add_provider_for_screen(screen, custom, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    except FileNotFoundError:
      pass
    Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    # Set up main window
    self.set_default_size(410, 310)
    self.move(int(self.prefs_values['x']), int(self.prefs_values['y']))
    self.set_border_width(10)
    self.set_title('Weather Widget')
    self.set_skip_taskbar_hint(True)
    self.set_keep_below(True)
    self.set_decorated(False)

    visual = screen.get_rgba_visual()  # opacity from custom.css
    self.set_visual(visual)

    self.main_container = Gtk.VBox(spacing=8)
    self.add(self.main_container)

    # Box for the hourly & 5 day buttons
    hbox = Gtk.HBox()
    self.main_container.pack_end(hbox, False, False, 0)

    # Button for hourly forecast
    button = Gtk.LinkButton.new_with_label("Hourly forecast")
    button.connect("clicked", self.call_hourly)
    hbox.pack_start(button, True, True, 0)
    button.set_tooltip_text('Hourly forecast for next 48h')

    # Button for 5 day forecast
    fivedaybutton = Gtk.LinkButton.new_with_label("5 day forecast")
    fivedaybutton.connect("clicked", self.call_five_day)
    hbox.pack_start(fivedaybutton, True, True, 0)
    fivedaybutton.set_tooltip_text('3 hourly forecast for next 5 days')

# Button for maps
    radar_owm = Gtk.LinkButton.new_with_label("Radar")
    radar_owm.connect("clicked", self.call_radar_owm)
    hbox.pack_end(radar_owm, True, True, 0)
    radar_owm.set_tooltip_text('Radar')
    # Right-click menu
    menu = Gtk.Menu()
    context = menu.get_style_context()
    context.add_class('menu')
    reload = Gtk.MenuItem()
    reload.set_label('reload')
    menu.append(reload)
    reload.show()

    preferences = Gtk.MenuItem()
    preferences.set_label('Preferences')
    menu.append(preferences)
    preferences.show()

    close_widget = Gtk.MenuItem()
    close_widget.set_label('Quit')
    menu.append(close_widget)
    close_widget.show()
    # Button for rainfall radar
    radar = Gtk.LinkButton.new_with_label("Ventusky")
    radar.connect("clicked", self.call_radar)
    hbox.pack_end(radar, True, True, 0)
    radar.set_tooltip_text('Maps')
    # Right-click menu
    menu = Gtk.Menu()
    context = menu.get_style_context()
    context.add_class('menu')
    reload = Gtk.MenuItem()
    reload.set_label('reload')
    menu.append(reload)
    reload.show()

    preferences = Gtk.MenuItem()
    preferences.set_label('Preferences')
    menu.append(preferences)
    preferences.show()

    close_widget = Gtk.MenuItem()
    close_widget.set_label('Quit')
    menu.append(close_widget)
    close_widget.show()

    self.connect('button_press_event', utils.button_press, menu)
    reload.connect('button_press_event', utils.refresh)
    preferences.connect('button_press_event', self.set_preferences)
    close_widget.connect('button_press_event', utils.stop)
    self.grid = Gtk.Grid()
    self.Json = {}

  def get_timeout(self):
    """ Time to refresh. timeout is accessed from outside, so use get method """
    try:
      timeout = max(int(self.prefs_values['timeout']), 10)
    except IndexError:
      timeout = 15
    return timeout

  def call_hourly(self, button):
    pos = self.get_position()
    hourly.hourly_forecast(self, pos)

  def call_five_day(self, button):
    pos = self.get_position()
    five_days.five_days(self, pos)

  def call_radar(self, button):
    self.rainfall_radar()

  def call_radar_owm(self, button):
    self.rainfall_radar_owm()

  def set_preferences(self, widget, event):
    # Open prefs dialogue
    if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
      pos = self.get_position()
      prefs.prefs(self, pos)


  def rainfall_radar_owm(self):
    """ Brings up rainfall radar window """
    # Create window
    rain_win = Gtk.Window()
    rain_win.set_default_size(900, 700)

    # Create view for webpage
    viewport = Gtk.ScrolledWindow()
    webview = WebKit2.WebView()
    webview.load_uri('file://' + self.path + os.sep + 'radar/radar.html?lat=' + self.prefs_values['lat'] + '&lon=' + self.prefs_values['lon'])
    viewport.add(webview)
    # Add everything and initialize
    container = Gtk.VBox()
    container.pack_start(viewport,True,True,0)
    rain_win.add(container)

    rain_win.connect("destroy", Gtk.main_quit)
    rain_win.show_all()
    Gtk.main()

  def rainfall_radar(self):
    """ Brings up rainfall radar window """
    # Create window
    rain_owm_win = Gtk.Window()
    rain_owm_win.set_default_size(1500, 840)

    # Create view for webpage
    viewport = Gtk.ScrolledWindow()
    webview = WebKit2.WebView()
    webview.load_uri('file://' + self.path + os.sep + 'radar/ventusky.html')
    viewport.add(webview)
    # Add everything and initialize
    container = Gtk.VBox()
    container.pack_start(viewport,True,True,0)
    rain_owm_win.add(container)

    rain_owm_win.connect("destroy", Gtk.main_quit)
    rain_owm_win.show_all()
    Gtk.main()



  def the_loop(self):
    """ The main display, refreshes every <timeout> minutes"""
    try:
      # The data source
      url = 'https://api.openweathermap.org/data/3.0/onecall?lat=' + self.prefs_values['lat'] + '&lon=' + self.prefs_values['lon'] + '&exclude=minutely,alerts&units=metric&appid=' + self.prefs_values['appid']
      data = request.urlopen(url)
    except Exception as e:
      print('Error: ', e)
      return True
    self.grid.destroy()

    self.grid = Gtk.Grid()
    self.grid.set_column_homogeneous(True)
    self.grid.set_row_spacing(10)
    self.grid.set_column_spacing(5)
    self.main_container.add(self.grid)

    # Get current conditions
    self.Json = json.load(data)
    cc = self.Json['current']

    temp = cc['temp']
    feels_like = cc['feels_like']
    if self.prefs_values['temp_unit'] == 'F':
      temp = (temp * 1.8) + 32
      feels_like = (feels_like * 1.8) + 32
    temp = str(round(temp, 1))
    feels_like = str(round(feels_like, 1))
    cond = cc['weather'][0]['description']
    icon = cc['weather'][0]['icon']
    wnd_spd = cc['wind_speed']
    wnd_spd = str(round(utils.wnd_spd_unit(self.prefs_values['speed_unit'], wnd_spd)))
    try:
      gust = cc['wind_gust']
      gust = '/' + str(round(utils.wnd_spd_unit(self.prefs_values['speed_unit'], gust)))
    except KeyError:
      gust = ''
    wnd_dir = cc['wind_deg']
    pres = cc['pressure']
    humidity = cc['humidity']

    sunrise = cc['sunrise']
    sunset = cc['sunset']
    update = cc['dt']
    update = datetime.fromtimestamp(update).astimezone()

    wnd_dir = utils.get_wnd_dir(wnd_dir)

    # Create the boxes
    vbox1 = Gtk.VBox(spacing=0)
    self.grid.attach(vbox1, 0, 0, 2, 1)
    vbox1.set_tooltip_text('Current conditions')
    vbox2 = Gtk.VBox(spacing=0)
    self.grid.attach(vbox2, 3, 0, 2, 1)
    vbox2.set_tooltip_text('Current conditions')
    vbox3 = Gtk.VBox(spacing=0)
    self.grid.attach(vbox3, 5, 0, 2, 1)

    city = Gtk.Label()
    vbox1.pack_start(city, True, True, 0)
    temperature = Gtk.Label()
    vbox1.pack_start(temperature, True, True, 0)
    temperature.set_margin_top(10)
    current_cond = Gtk.Label()
    vbox1.pack_start(current_cond, True, True, 0)
    current_cond.set_margin_top(10)
    weather_icon = Gtk.Image.new_from_pixbuf()
    vbox1.pack_start(weather_icon, True, True, 0)
    wnd_box = Gtk.HBox()
    vbox2.pack_start(wnd_box, True, True, 0)
    wnd_speed = Gtk.Label()
    wnd_box.pack_start(wnd_speed, True, True, 0)
    wnd_dir_icon = Gtk.Image.new_from_pixbuf()
    vbox3.pack_start(wnd_dir_icon, True, True, 0)
    wnd_dir_icon.set_valign(Gtk.Align.START)
    pressure = Gtk.Label()
    vbox2.pack_start(pressure, True, True, 0)
    hum = Gtk.Label()
    vbox2.pack_start(hum, True, True, 0)
    sun_set = Gtk.Label()
    vbox2.pack_start(sun_set, True, True, 0)
    last_update = Gtk.Label()
    vbox2.pack_start(last_update, True, True, 0)

    # Print data
    city.set_markup('<span size=\"large\"><b>' + self.prefs_values['loc'] + '</b></span>')
    city.set_halign(Gtk.Align.START)
    city.set_line_wrap(True)

    temperature.set_markup(
      '<span size=\"xx-large\"><b>' + temp + '\N{DEGREE SIGN}' + self.prefs_values['temp_unit'] + '</b></span> ' + 'f/l ' + feels_like + '\N{DEGREE SIGN}' + self.prefs_values['temp_unit'])
    temperature.set_halign(Gtk.Align.START)

    current_cond.set_markup('<span variant=\"smallcaps\">' + cond + '</span>')
    current_cond.set_line_wrap(True)

    current_cond.set_halign(Gtk.Align.START)

    weathericon = self.path + os.sep + 'PNG' + os.sep + icon + '.png'
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(weathericon, 50, 50)
    weather_icon.set_from_pixbuf(pixbuf)
    weather_icon.set_halign(Gtk.Align.START)

    wnd_speed.set_text('Wind: ' + wnd_spd + gust + self.prefs_values['speed_unit'] + ' ' + wnd_dir)
    wnd_speed.set_halign(Gtk.Align.START)

    wnd_icon = self.path + os.sep + 'bearingicons' + os.sep + wnd_dir + '.png'
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(wnd_icon, 60, 60)
    wnd_dir_icon.set_from_pixbuf(pixbuf)
    wnd_dir_icon.set_tooltip_text('Wind direction')

    pressure.set_text('Pressure: ' + str(pres) + 'mb')
    pressure.set_halign(Gtk.Align.START)

    hum.set_text('Humidity: ' + str(humidity) + '%')
    hum.set_halign(Gtk.Align.START)

    sunrisetime = datetime.fromtimestamp(sunrise).astimezone()
    sunset = datetime.fromtimestamp(sunset).astimezone()
    sun_set.set_text(
      'Sunrise: ' + sunrisetime.time().strftime('%H:%M') + '\n' + 'Sunset:  ' + sunset.time().strftime('%H:%M'))
    sun_set.set_halign(Gtk.Align.START)

    last_update.set_text('Updated: ' + update.time().strftime('%H:%M:%S'))
    last_update.set_halign(Gtk.Align.START)

    # 7 day forecast
    fc = self.Json['daily']

    for i in range(7):
      vbox = Gtk.VBox()
      self.grid.attach(vbox, i, 1, 1, 1)

      t = fc[i]['dt']
      t = datetime.fromtimestamp(t).astimezone()
      t = t.date().strftime('%a')

      forecast_time = Gtk.Label()
      vbox.pack_start(forecast_time, True, True, 0)
      forecast_time.set_text(t)
      forecast_time.set_halign(Gtk.Align.START)
#      temp = fc[i]['temp']['day']
      min_temp = fc[i]['temp']['min']
      if self.prefs_values['temp_unit'] == 'F':
        min_temp = (min_temp * 1.8) + 32
      min_temp = str(round(min_temp))
      max_temp = fc[i]['temp']['max']
      if self.prefs_values['temp_unit'] == 'F':
        max_temp = (max_temp * 1.8) + 32
      max_temp = str(round(max_temp))
      min_max = Gtk.Label()
      vbox.pack_start(min_max, True, True, 0)
      min_max.set_text(max_temp + '/' + min_temp + '\N{DEGREE SIGN}' + 'C')
      min_max.set_tooltip_text('Max and min temp')
      min_max.set_halign(Gtk.Align.START)

      symbol = fc[i]['weather'][0]['icon']
      weathericon = self.path + os.sep + 'PNG' + os.sep + symbol + '.png'
      icon = Gtk.Image.new_from_pixbuf()
      vbox.pack_start(icon, True, True, 0)
      pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(weathericon, 30, 30)
      icon.set_from_pixbuf(pixbuf)
      icon.set_tooltip_markup('<span variant=\"smallcaps\">' + fc[i]['weather'][0]['description'] + '</span>')
      icon.set_halign(Gtk.Align.START)

      wnd_spd = fc[i]['wind_speed']
      wnd_spd = str(round(utils.wnd_spd_unit(self.prefs_values['speed_unit'], wnd_spd)))
      try:
        gust = fc[i]['wind_gust']
        gust = str(round(utils.wnd_spd_unit(self.prefs_values['speed_unit'], gust)))
        gust = '/' + gust
      except KeyError:
        gust = ''
      wind = Gtk.Label()
      vbox.pack_start(wind, True, True, 0)
      wind.set_text(str(wnd_spd) + gust + self.prefs_values['speed_unit'])
      wind.set_tooltip_text('wind speed')
      wind.set_halign(Gtk.Align.START)

      wnd_dir = fc[i]['wind_deg']
      wnd_dir = utils.get_wnd_dir(wnd_dir)
      wnddir = Gtk.Label()
      vbox.pack_start(wnddir, True, True, 0)
      wnddir.set_text(str(wnd_dir))
      wnddir.set_tooltip_text('Wind direction')
      wnddir.set_halign(Gtk.Align.START)

      humidity = fc[i]['humidity']
      hum = Gtk.Label()
      vbox.pack_start(hum, True, True, 0)
      hum.set_text('H ' + str(humidity) + '%')
      hum.set_tooltip_text('Humidity')
      hum.set_halign(Gtk.Align.START)

      prec = fc[i]['pop']
      precipitation = Gtk.Label()
      vbox.pack_start(precipitation, True, True, 0)
      precipitation.set_text(str(round(prec * 100)) + '%')
      precipitation.set_tooltip_text('Chance of rain')
      precipitation.set_halign(Gtk.Align.START)

      try:
        rain = fc[i]['rain']
        rain = round(rain, 1)
      except KeyError:
        rain = '0'
      rainfall = Gtk.Label()
      vbox.pack_start(rainfall, True, True, 0)
      rainfall.set_text(str(rain) + 'mm')
      rainfall.set_tooltip_text('Total amount of rain')
      rainfall.set_halign(Gtk.Align.START)

      pres = fc[i]['pressure']
      pressure = Gtk.Label()
      vbox.pack_start(pressure, True, True, 0)
      pressure.set_text(str(pres) + 'mb')
      pressure.set_tooltip_text('Pressure')
      pressure.set_halign(Gtk.Align.START)

    self.grid.show_all()
    return True

if __name__ == '__main__':
  win = Win()
  win.connect("destroy", Gtk.main_quit)
  win.show_all()
  win.the_loop()
  timeout_add = GLib.timeout_add_seconds(win.get_timeout() * 60, win.the_loop)
  Gtk.main()
