import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf
from datetime import datetime
import os
import utils

def hourly_forecast(win, pos):
    """ Opens sub-window with 7day forecast """
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

    fc = win.Json['hourly']
    daily = win.Json['daily']
    current = win.Json['current']

    # Start at the current hour
    now = current['time'][:13] + ':00'
    start = 0
    for j, ts in enumerate(fc['time']):
      if ts >= now:
        start = j
        break

    for n in range(167):
      i = start + n
      if i >= len(fc['time']):
        break
      row = n + 1

      ts = fc['time'][i]
      temp = fc['temperature_2m'][i]
      temp_colour = utils.temp_colour(temp)  # Colour coded text
      if win.prefs_values['temp_unit'] == 'F':
        temp = (temp * 1.8) + 32
      code = fc['weather_code'][i]
      cond = utils.weather_description(code)
      wnd_spd = fc['wind_speed_10m'][i]
      wnd_colour = utils.wind_colour(wnd_spd)
      wnd_spd = round(utils.wnd_spd_unit(win.prefs_values['speed_unit'], wnd_spd))
      wnd_dir = fc['wind_direction_10m'][i]
      gust = fc['wind_gusts_10m'][i]
      gust_colour = utils.wind_colour(gust)
      gust = round(utils.wnd_spd_unit(win.prefs_values['speed_unit'], gust))
      pres = fc['surface_pressure'][i]
      rain = round(float(fc['precipitation'][i]), 1)
      pop = round(fc['precipitation_probability'][i])
      if pop > 0:
        pop = '<b>' + str(pop) + '%</b>'
      else:
        pop = str(pop) + '%'
      cloud = fc['cloud_cover'][i]

      dt = datetime.fromisoformat(ts)
      sunrise = datetime.fromisoformat(daily['sunrise'][i // 24])
      sunset = datetime.fromisoformat(daily['sunset'][i // 24])

      d = dt.date().strftime('%a')
      t = dt.time().strftime('%H')

      wnd_dir = utils.get_wnd_dir(wnd_dir)

      dn = utils.day_night(sunrise, sunset, dt)
      symbol = utils.weather_icon(code, dn)

      day_label = Gtk.Label()
      grid.attach(day_label, 0, row, 1, 1)

      if dn == '-n':
        context = day_label.get_style_context()
        context.add_class('night')
      else:
        context = day_label.get_style_context()
        context.add_class('day')
      day_label.set_markup('<b>' + d + ' ' + t + 'h</b>')

      temp = round(temp, 1)
      temp_label = Gtk.Label()
      grid.attach(temp_label, 1, row, 1, 1)

      if dn == '-n':
        context = temp_label.get_style_context()
        context.add_class('night')
      else:
        context = temp_label.get_style_context()
        context.add_class('day')

      temp_label.set_markup('<b><span foreground=\"' + temp_colour + '\">' + str(temp) + '\N{DEGREE SIGN}' + 'C</span></b>')

      weather_icon = win.path + os.sep + 'PNG' + os.sep + symbol + '.png'
      weathericon = Gtk.Image.new_from_pixbuf()
      grid.attach(weathericon, 2, row, 1, 1)

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
      grid.attach(name_label, 3, row, 1, 1)

      if dn == '-n':
        context = name_label.get_style_context()
        context.add_class('night')
      else:
        context = name_label.get_style_context()
        context.add_class('day')
      name_label.set_markup('<span variant=\"smallcaps\">' + cond + '</span>')
      name_label.set_line_wrap(True)

      precipitation = Gtk.Label()
      grid.attach(precipitation, 4, row, 1, 1)

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
      grid.attach(wnd_spd_label, 5, row, 1, 1)

      if dn == '-n':
        context = wnd_spd_label.get_style_context()
        context.add_class('night')
      else:
        context = wnd_spd_label.get_style_context()
        context.add_class('day')

      wnd_spd_label.set_markup(
        '<span foreground=\"' + wnd_colour + '\">' + str(wnd_spd) + '/</span><span foreground=\"' + gust_colour + '\">' + str(
          gust) + win.prefs_values['speed_unit'] + '</span>')

      wnd_dir_label = Gtk.Label()
      grid.attach(wnd_dir_label, 6, row, 1, 1)

      if dn == '-n':
        context = wnd_dir_label.get_style_context()
        context.add_class('night')
      else:
        context = wnd_dir_label.get_style_context()
        context.add_class('day')
      wnd_dir_label.set_text(str(wnd_dir))

      cloud_label = Gtk.Label()
      grid.attach(cloud_label, 7, row, 1, 1)

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
      grid.attach(pressure, 8, row, 1, 1)

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
