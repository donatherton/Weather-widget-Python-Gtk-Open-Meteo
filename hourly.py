import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf
from datetime import datetime
import os
import utils

def hourly_forecast(self, pos):
    """ Opens sub-window with 48h forecast """
    # CSS
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    css = b"""
    label.day,image.day {
    padding: 0 3px 0 3px;
    min-height: 30px;
    border-bottom: 1px solid #bbbbbb;
    background: #eeeeee;
    color: #191919;
    }
    label.night, image.night {
    padding: 0 3px 0 3px;
    min-height: 30px;
    border-bottom: 1px solid #bbbbbb;
    background: #bbbbbb;
    color: #191919;
    }
    """
    provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    # Create window
    wnd = Gtk.Window()
    wnd.set_title('Hourly forecast')
    wnd.set_default_size(460, 600)
    wnd.move(pos[0], pos[1])

    grid_box = Gtk.ScrolledWindow()

    wnd.add(grid_box)
    box = Gtk.VBox()
    box.set_border_width(10)
    grid_box.add(box)

    grid = Gtk.Grid()
    grid.set_row_spacing(1)
    box.add(grid)

    top = ['Time', 'Temp', ' Cond', '  ', 'Rain', 'Wind', '', 'Cloud', 'Pres']
    f = 0
    for item in top:
      item_label = Gtk.Label()
      grid.attach(item_label, f, 0, 1, 1)
      item_label.set_markup('<b>' + item + '</b>')
      f = f + 1

    fc = self.Json['hourly']
    #print(self.Json)

    for i in range(0, 48):
      ts = fc[i]['dt'] #+ self.Json['timezone_offset']
      temp = fc[i]['temp']
      temp_colour = utils.temp_colour(temp)  # Colour coded text
      if self.prefs_values['temp_unit'] == 'F':
        temp = (temp * 1.8) + 32
      symbol = fc[i]['weather'][0]['icon']
      cond = fc[i]['weather'][0]['description']
      wnd_spd = fc[i]['wind_speed']
      wnd_colour = utils.wind_colour(wnd_spd)
      wnd_spd = round(utils.wnd_spd_unit(self.prefs_values['speed_unit'], wnd_spd))
      wnd_dir = fc[i]['wind_deg']
      try:
        gust = fc[i]['wind_gust']
        gust_colour = utils.wind_colour(gust)
        gust = round(utils.wnd_spd_unit(self.prefs_values['speed_unit'], gust))
      except KeyError:
        gust = 0
        gust_colour = ''
      pres = fc[i]['pressure']
      try:
        rain = fc[i]['rain']['1h']
        rain = round(float(rain), 1)
      except KeyError:
        rain = 0
#      try:
      pop = round(fc[i]['pop']*100)
      if pop > 0:
        pop = '<b>' + str(pop) + '%</b>'
      else:
        pop = str(pop) + '%'
#      except KeyError:
#        pop = '0%'
      cloud = fc[i]['clouds']

      sunrise = self.Json['current']['sunrise']
      sunset = self.Json['current']['sunset']

      t = datetime.fromtimestamp(ts).astimezone()
      d = t.date().strftime('%a')
      t = t.time().strftime('%H')

      wnd_dir = utils.get_wnd_dir(wnd_dir)

      dn = utils.day_night(sunrise, sunset, ts)

      day_label = Gtk.Label()
      grid.attach(day_label, 0, i + 1, 1, 1)

      if dn == '-n':
        context = day_label.get_style_context()
        context.add_class('night')
      else:
        context = day_label.get_style_context()
        context.add_class('day')
      day_label.set_markup('<b>' + d + ' ' + t + 'h</b>')

      temp = round(temp, 1)
      temp_label = Gtk.Label()
      grid.attach(temp_label, 1, i + 1, 1, 1)

      if dn == '-n':
        context = temp_label.get_style_context()
        context.add_class('night')
      else:
        context = temp_label.get_style_context()
        context.add_class('day')

      temp_label.set_markup('<b><span foreground=\"' + temp_colour + '\">' + str(temp) + '\N{DEGREE SIGN}' + 'C</span></b>')

      weather_icon = self.path + os.sep + 'PNG' + os.sep + symbol + '.png'
      weathericon = Gtk.Image.new_from_pixbuf()
      grid.attach(weathericon, 2, i + 1, 1, 1)

      if dn == '-n':
        context = weathericon.get_style_context()
        context.add_class('night')
      else:
        context = weathericon.get_style_context()
        context.add_class('day')
      pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(weather_icon, 20, 20)
      weathericon.set_from_pixbuf(pixbuf)
      weathericon.show()

      name_label = Gtk.Label()
      grid.attach(name_label, 3, i + 1, 1, 1)

      if dn == '-n':
        context = name_label.get_style_context()
        context.add_class('night')
      else:
        context = name_label.get_style_context()
        context.add_class('day')
      name_label.set_markup('<span variant=\"smallcaps\">' + cond + '</span>')
      name_label.set_line_wrap(True)

      precipitation = Gtk.Label()
      grid.attach(precipitation, 4, i + 1, 1, 1)

      if dn == '-n':
        context = precipitation.get_style_context()
        context.add_class('night')
      else:
        context = precipitation.get_style_context()
        context.add_class('day')
      if rain > 0:
        precipitation.set_markup('<b>' + str(rain) + 'mm, ' + pop + '</b>')
      else:
        precipitation.set_markup(str(rain) + 'mm, ' + pop)

      wnd_spd_label = Gtk.Label()
      grid.attach(wnd_spd_label, 5, i + 1, 1, 1)

      if dn == '-n':
        context = wnd_spd_label.get_style_context()
        context.add_class('night')
      else:
        context = wnd_spd_label.get_style_context()
        context.add_class('day')

      wnd_spd_label.set_markup(
        '<span foreground=\"' + wnd_colour + '\">' + str(wnd_spd) + '/</span><span foreground=\"' + gust_colour + '\">' + str(
          gust) + self.prefs_values['speed_unit'] + '</span>')

      wnd_dir_label = Gtk.Label()
      grid.attach(wnd_dir_label, 6, i + 1, 1, 1)

      if dn == '-n':
        context = wnd_dir_label.get_style_context()
        context.add_class('night')
      else:
        context = wnd_dir_label.get_style_context()
        context.add_class('day')
      wnd_dir_label.set_text(str(wnd_dir))

      cloud_label = Gtk.Label()
      grid.attach(cloud_label, 7, i + 1, 1, 1)

      if dn == '-n':
        context = cloud_label.get_style_context()
        context.add_class('night')
        cloud_label.set_text(str(cloud) + '%')
      else:
        context = cloud_label.get_style_context()
        context.add_class('day')
        cloud_bg = utils.cloud_colour(cloud)
        cloud_label.set_markup('<span background=\"' + cloud_bg + '\">' + str(cloud) + '%</span>')

      pres = round(float(pres))
      pressure = Gtk.Label()
      grid.attach(pressure, 8, i + 1, 1, 1)

      if dn == '-n':
        context = pressure.get_style_context()
        context.add_class('night')
      else:
        context = pressure.get_style_context()
        context.add_class('day')
      pressure.set_text(str(pres) + 'mb')

    grid.show_all()

    wnd.connect("destroy", Gtk.main_quit)
    wnd.show_all()
    Gtk.main()

@staticmethod
def temp_colour(temp):
    """ Selects font colour based on temperature """
    temp_colours = ['#00ffff', '#3399ff', '#3366cc', '#3319FF', '#ff3300', '#ff0000', '#993300']
    temp_ranges = [0, 5, 10, 15, 20, 25]
    for i in range(len(temp_ranges)):
        if temp < temp_ranges[i]:
            return temp_colours[i]
    return temp_colours[-1]

@staticmethod
def cloud_colour(cloud):
    """ Selects BG colour based on amount of cloud """
    cloud_colours = ['#eeeeee', '#dddddd', '#cccccc', '#bbbbbb', '#aaaaaa']
    cloud_ranges = [0, 20, 40, 60, 80]
    for i in range(len(cloud_ranges)):
        if cloud < cloud_ranges[i]:
            return cloud_colours[i]
    return cloud_colours[-1]

@staticmethod
def wind_colour(wnd_spd):
    wnd_colours = ['#2E423B', '#CE5C00', '#CE1600', '#CC0000', '#A40075']
    wnd_ranges = [8, 15, 20, 25]
    for i in range(len(wnd_ranges)):
        if wnd_spd < wnd_ranges[i]:
            return wnd_colours[i]
    return wnd_colours[-1]

@staticmethod
def day_night(sr, ss, h):
    """ Selects BG colour to show day/night """
    if (int(sr) <= int(h) and int(h) <= int(ss)) or (int(sr) <= int(h - 86400) and int(h - 86400) <= int(ss)) or (
        int(sr) <= int(h - 172800) and int(h - 172800) <= int(ss)):
      dn = '-d'
    else:
      dn = '-n'
    return dn
