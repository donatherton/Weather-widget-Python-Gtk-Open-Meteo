import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf
from urllib import request
import json
from datetime import datetime
import os
import utils

def five_days(win, pos):
    """ Opens sub-window with 5 day forecast """
    url_forecast = 'http://api.openweathermap.org/data/2.5/forecast?lat=' + win.prefs_values['lat'] + '&lon=' + win.prefs_values['lon'] + '&appid=' + win.prefs_values['appid']

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
    wnd.set_title('5 day 3 hour forecast')
    wnd.set_default_size(450, 700)
    wnd.move(pos[0], pos[1])

    container = Gtk.ScrolledWindow()
    # container.set_policy (Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)

    wnd.add(container)
    flowbox = Gtk.VBox()
    flowbox.set_border_width(10)
    container.add(flowbox)

    grid = Gtk.Grid()
    grid.set_row_spacing(1)
    flowbox.add(grid)

    try:
        forecast_url = request.urlopen(url_forecast)
        forecast = json.load(forecast_url)
    except Exception as e:
        print(e)

    sunrise = forecast['city']['sunrise']
    sunset = forecast['city']['sunset']
    sunrisetime = datetime.fromtimestamp(sunrise).astimezone()
    sunrise = sunrisetime.time().strftime('%H:%M')
    sunsettime = datetime.fromtimestamp(sunset).astimezone()
    sunset = sunsettime.time().strftime('%H:%M')

    top = ['Time', 'Temp', '  ', '  ', 'Rain', 'Wind', '', 'Cloud', 'Pres']
    f = 0
    for item in top:
      item_label = Gtk.Label()
      grid.attach(item_label, f, 0, 1, 1)
      item_label.set_markup('<b>' + item + '</b>')
      item_label.set_halign(Gtk.Align.START)
      f = f + 1

    for i in range(40):
      t = forecast['list'][i]['dt']
      t = datetime.fromtimestamp(t).astimezone()
      d = t.strftime('%a')
      t = t.time().strftime('%H')

      dn = utils.day_night_5day(sunrise, sunset, t)

      day_label = Gtk.Label()
      grid.attach(day_label, 0, i + 1, 1, 1)
      if dn == '-n':
        context = day_label.get_style_context()
        context.add_class('night')
      else:
        context = day_label.get_style_context()
        context.add_class('day')

      day_label.set_markup('<b>' + d + ' ' + t + 'h</b>')

      temp = forecast['list'][i]['main']['temp'] - 273.15
      temp_colour = utils.temp_colour(temp)  # Colour coded text
      if win.prefs_values['temp_unit'] == 'F':
        temp = (temp * 1.8) + 32
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

      symbol = forecast['list'][i]['weather'][0]['icon']
      weather_icon = win.path + os.sep + 'PNG' + os.sep + symbol + '.png'
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

      name = forecast['list'][i]['weather'][0]['description']
      name_label = Gtk.Label()
      grid.attach(name_label, 3, i + 1, 1, 1)
      if dn == '-n':
        context = name_label.get_style_context()
        context.add_class('night')
      else:
        context = name_label.get_style_context()
        context.add_class('day')

      name_label.set_markup('<span variant=\"smallcaps\">' + name + '</span>')
      name_label.set_line_wrap(True)

      try:
        prec = forecast['list'][i]['rain']['3h']
      except KeyError:
        prec = 0

      prec = round(float(prec), 1)
      precipitation = Gtk.Label()
      grid.attach(precipitation, 4, i + 1, 1, 1)
      if dn == '-n':
        context = precipitation.get_style_context()
        context.add_class('night')
      else:
        context = precipitation.get_style_context()
        context.add_class('day')
      if prec > 0:
        precipitation.set_markup('<b>' + str(prec) + 'mm</b>')
      else:
        precipitation.set_text(str(prec) + 'mm')

      wnd_spd = forecast['list'][i]['wind']['speed']
      wnd_colour = utils.wind_colour(wnd_spd)
      wnd_spd = round(utils.wnd_spd_unit(win.prefs_values['speed_unit'], wnd_spd))
      wnd_spd_label = Gtk.Label()
      try:
        wnd_gust = forecast['list'][i]['wind']['gust']
        gust_colour = utils.wind_colour(wnd_gust)
        wnd_gust = '/' + str(round(utils.wnd_spd_unit(win.prefs_values['speed_unit'], wnd_gust)))
      except KeyError:
        gust_colour = '#2E423B'
        wnd_gust = ''
      grid.attach(wnd_spd_label, 5, i + 1, 1, 1)
      if dn == '-n':
        context = wnd_spd_label.get_style_context()
        context.add_class('night')
      else:
        context = wnd_spd_label.get_style_context()
        context.add_class('day')

      wnd_spd_label.set_markup('<span foreground=\"' + wnd_colour + '\">' + str(
        wnd_spd) + '</span><span foreground=\"' + gust_colour + '\">' + wnd_gust + win.prefs_values['speed_unit'] + '</span>')

      wnd_dir = utils.get_wnd_dir(forecast['list'][i]['wind']['deg'])
      wnd_dir_label = Gtk.Label()
      grid.attach(wnd_dir_label, 6, i + 1, 1, 1)
      if dn == '-n':
        context = wnd_dir_label.get_style_context()
        context.add_class('night')
      else:
        context = wnd_dir_label.get_style_context()
        context.add_class('day')

      wnd_dir_label.set_text(str(wnd_dir))

      cloud = forecast['list'][i]['clouds']['all']
      cloud_label = Gtk.Label()
      grid.attach(cloud_label, 7, i + 1, 1, 1)
      cloud_bg = utils.cloud_colour(cloud)
      if dn == '-n':
        context = cloud_label.get_style_context()
        context.add_class('night')
        cloud_label.set_markup(str(cloud) + '%')
      else:
        context = cloud_label.get_style_context()
        context.add_class('day')
        cloud_label.set_markup('<span background=\"' + cloud_bg + '\">' + str(cloud) + '%</span>')

      pres = forecast['list'][i]['main']['pressure']
      pressure = Gtk.Label()
      grid.attach(pressure, 8, i + 1, 1, 1)
      if dn == '-n':
        context = pressure.get_style_context()
        context.add_class('night')
      else:
        context = pressure.get_style_context()
        context.add_class('day')

      pressure.set_text(str(pres) + 'mb')

    wnd.connect("destroy", Gtk.main_quit)
    wnd.show_all()
    Gtk.main()
