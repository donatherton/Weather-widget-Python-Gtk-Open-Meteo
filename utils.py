import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import urllib.request
import os
import sys

def wnd_spd_unit(unit, wndspd):
    switcher = {
        'm/s': wndspd,
        'kph': wndspd * 3.6,
        'mph': wndspd * 2.23694,
        'kt': wndspd * 1.944,
        'Bf': min((float(wndspd) / 0.836) ** (2 / 3), 12)
    }
    return switcher.get(unit, wndspd)

def get_wnd_dir(wnd_dir):
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    ranges = [11, 33, 56, 78, 101, 123, 146, 168, 190, 213, 235, 258, 280, 303, 325, 347]
    for i, r in enumerate(ranges):
        if wnd_dir <= r:
            return dirs[i]
    return dirs[-1]

def refresh(widget, event):
    # reload
    if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
        os.execv(sys.argv[0], sys.argv)

def button_press(widget, event, menu):
    """ Handle right click, bring up menu """
    if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
        menu.popup(None, None, None, event.button, 1, event.time)

def stop(widget, event):
    if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
        Gtk.main_quit()

def temp_colour(temp):
    """ Selects font colour based on temperature """
    temp_colours = ['#00ffff', '#3399ff', '#3366cc', '#3319FF', '#ff3300', '#ff0000', '#993300']
    temp_ranges = [0, 5, 10, 15, 20, 25]
    for i in range(len(temp_ranges)):
        if temp < temp_ranges[i]:
            return temp_colours[i]
    return temp_colours[-1]

def cloud_colour(cloud):
    """ Selects BG colour based on amount of cloud """
    cloud_colours = ['#eeeeee', '#dddddd', '#cccccc', '#bbbbbb', '#aaaaaa']
    cloud_ranges = [0, 20, 40, 60, 80]
    for i in range(len(cloud_ranges)):
        if cloud < cloud_ranges[i]:
            return cloud_colours[i]
    return cloud_colours[-1]

def wind_colour(wnd_spd):
    wnd_colours = ['#2E423B', '#CE5C00', '#CE1600', '#CC0000', '#A40075']
    wnd_ranges = [8, 15, 20, 25]
    for i in range(len(wnd_ranges)):
        if wnd_spd < wnd_ranges[i]:
            return wnd_colours[i]
    return wnd_colours[-1]

def day_night(sr, ss, h):
    """ Selects BG colour to show day/night """
    if (int(sr) <= int(h) and int(h) <= int(ss)) or (int(sr) <= int(h - 86400) and int(h - 86400) <= int(ss)) or (
            int(sr) <= int(h - 172800) and int(h - 172800) <= int(ss)):
        dn = '-d'
    else:
        dn = '-n'
    return dn

def day_night_5day(sr, ss, h):
    return '-d' if sr <= h <= ss else '-n'
