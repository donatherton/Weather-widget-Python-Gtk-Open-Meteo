import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import os
import sys

def weather_icon(code, suffix='d'):
    """ Map a WMO weather code to an OpenWeatherMap icon file name """
    icons = {
        0: '01', 1: '02', 2: '03', 3: '04',
        45: '50', 48: '50',
        51: '09', 53: '09', 55: '09',
        56: '09', 57: '09',
        61: '10', 63: '10', 65: '10',
        66: '10', 67: '10',
        71: '13', 73: '13', 75: '13', 77: '13',
        80: '09', 81: '10', 82: '10',
        85: '13', 86: '13',
        95: '11', 96: '11', 99: '11',
    }
    return icons.get(code, '01') + suffix.lstrip('-')

def weather_description(code):
    """ Text description for a WMO weather code """
    descriptions = {
        0: 'Clear sky',
        1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
        45: 'Fog', 48: 'Depositing rime fog',
        51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
        56: 'Light freezing drizzle', 57: 'Dense freezing drizzle',
        61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
        66: 'Light freezing rain', 67: 'Heavy freezing rain',
        71: 'Slight snow fall', 73: 'Moderate snow fall', 75: 'Heavy snow fall',
        77: 'Snow grains',
        80: 'Slight rain showers', 81: 'Moderate rain showers', 82: 'Violent rain showers',
        85: 'Slight snow showers', 86: 'Heavy snow showers',
        95: 'Thunderstorm', 96: 'Thunderstorm with slight hail', 99: 'Thunderstorm with heavy hail',
    }
    return descriptions.get(code, 'Unknown')

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

def day_night(sunrise, sunset, time):
    """ Selects day/night marker based on datetime objects """
    return '-d' if sunrise <= time <= sunset else '-n'
