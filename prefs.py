import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import urllib.request
import os
import sys

def prefs(self, pos):
    """ Saves and stores preferences """
    from urllib.parse import quote

    def geo_search(self):
      """ Shows up to 5 location search results """
      try:
        store.clear()
      except:
        pass

      geosearch = geosearch_input.get_text()

      search_url = 'https://nominatim.openstreetmap.org/?format=json&addressdetails=1&q=' + quote(
        geosearch) + '&limit=5'

      headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:152.0) Gecko/20100101 Firefox/152.0',
      }

      try:
          req = urllib.request.Request(search_url, headers=headers)
          location = urllib.request.urlopen(req)
      except Exception as e:
          print('Error', e)
      location = json.load(location)

      for i in range(len(location)):
        try:
          try:
            loc = location[i]['address']['city']
          except KeyError:
            loc = location[i]['address']['town']
        except KeyError:
          try:
            loc = location[i]['address']['village']
          except KeyError:
            loc = 'Unknown'

        store.append([location[i]['display_name'], loc, location[i]['lat'], location[i]['lon'], i])

      treeview.show_all()

    def save_and_reload(button, self):
      select = treeview.get_selection()
      model, treeiter = select.get_selected()
      if treeiter is not None:
        lat1 = model[treeiter][2]
        lon1 = model[treeiter][3]
        place_name1 = model[treeiter][1]
      else:
        place_name1 = self.prefs_values['loc']
        lat1 = self.prefs_values['lat']
        lon1 = self.prefs_values['lon']

      appid_value = appid.get_text()
      temp_button = [r for r in button1.get_group() if r.get_active()]
      speed_button = [r for r in wnd_spd_button1.get_group() if r.get_active()]
      timeout = time_out.get_text()
      if int(timeout) < 10: timeout = '10'
      font_size = font.get_value_as_int()

      with open(self.path + os.sep + 'prefs', 'w') as f:
        f.write('appid,' + appid_value + '\n')
        f.write('lat,' + lat1 + '\n')
        f.write('lon,' + lon1 + '\n')
        f.write('loc,' + place_name1 + '\n')
        f.write('temp_unit,' + temp_button[0].get_label() + '\n')
        f.write('speed_unit,' +speed_button[0].get_label() + '\n')
        f.write('timeout,' + timeout + '\n')
        f.write('font_size,' + str(font_size) + '\n')
        f.write('x,' + str(pos[0]) + '\n')
        f.write('y,' + str(pos[1]))
      os.execv(sys.argv[0], sys.argv)  # reload

    #  def lock_position(self):
    #    self.pos = win.get_position()
    #    save_and_reload(self)

    win = Gtk.Window()
    win.set_default_size(400, 550)
    win.set_border_width(10)
    win.set_title('Preferences')

    container = Gtk.ScrolledWindow()
    win.add(container)

    box = Gtk.VBox()
    container.add(box)

    #    searchLabel = Gtk.Label()
    #    box.pack_start(searchLabel, False, False, 0)
    #    searchLabel.set_markup('<b>Search location</b>')

    search_hbox = Gtk.HBox()
    box.pack_start(search_hbox, False, False, 0)
    geosearch_input = Gtk.SearchEntry()
    geosearch_input.set_text(self.prefs_values['loc'])
    geosearch_input.connect("activate", geo_search)
    search_hbox.pack_start(geosearch_input, True, True, 5)
    #    searchLabel.set_halign(Gtk.Align.START)

    search_button = Gtk.Button().new_with_label(" Search location ")
    search_button.connect('clicked', geo_search)
    search_hbox.pack_end(search_button, False, False, 0)

    grid_box = Gtk.ScrolledWindow()
    box.pack_start(grid_box, True, True, 5)

    treeview = Gtk.TreeView()
    store = Gtk.ListStore(str, str, str, str, int)
    treeview.set_model(store)

    renderer_text = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn('Add location from search results', renderer_text, text=0)
    treeview.append_column(column)
    grid_box.add(treeview)

    appid_label = Gtk.Label()
    box.pack_start(appid_label, False, False, 5)
    appid_label.set_markup('<b>OpenWeatherMap key:</b>')
    appid = Gtk.Entry()
    box.pack_start(appid, False, False, 0)
    appid.set_text(self.prefs_values['appid'])
    appid_label.set_halign(Gtk.Align.START)

    temp_box = Gtk.Box(spacing=6)
    box.pack_start(temp_box, False, False, 5)
    temp_label = Gtk.Label()
    temp_box.pack_start(temp_label, False, False, 5)
    temp_label.set_markup('<b>Temperature unit:</b>')
    button1 = Gtk.RadioButton.new_with_label_from_widget(None, "C")
    temp_box.pack_start(button1, False, False, 0)
    button2 = Gtk.RadioButton.new_from_widget(button1)
    button2.set_label("F")
    temp_box.pack_start(button2, False, False, 0)
    if self.prefs_values['temp_unit'] == 'F':
      button2.set_active(True)
    else:
      button1.set_active(True)

    wnd_spd_box = Gtk.Box(spacing=6)
    box.pack_start(wnd_spd_box, False, False, 5)
    wnd_spd_label = Gtk.Label()
    wnd_spd_box.pack_start(wnd_spd_label, False, False, 5)
    wnd_spd_label.set_markup('<b>Windspeed unit:</b>')
    wnd_spd_button1 = Gtk.RadioButton.new_with_label_from_widget(None, "kt")
    wnd_spd_box.pack_start(wnd_spd_button1, False, False, 0)
    wnd_spd_button2 = Gtk.RadioButton.new_from_widget(wnd_spd_button1)
    wnd_spd_button2.set_label("mph")
    wnd_spd_box.pack_start(wnd_spd_button2, False, False, 0)
    wnd_spd_button3 = Gtk.RadioButton.new_from_widget(wnd_spd_button1)
    wnd_spd_button3.set_label("m/s")
    wnd_spd_box.pack_start(wnd_spd_button3, False, False, 0)
    wnd_spd_button4 = Gtk.RadioButton.new_from_widget(wnd_spd_button1)
    wnd_spd_button4.set_label("kph")
    wnd_spd_box.pack_start(wnd_spd_button4, False, False, 0)
    wnd_spd_button5 = Gtk.RadioButton.new_from_widget(wnd_spd_button1)
    wnd_spd_button5.set_label("Bf")
    wnd_spd_box.pack_start(wnd_spd_button5, False, False, 0)
    if self.prefs_values['speed_unit'] == 'mph':
      wnd_spd_button2.set_active(True)
    elif self.prefs_values['speed_unit'] == 'm/s':
      wnd_spd_button3.set_active(True)
    elif self.prefs_values['speed_unit'] == 'kph':
      wnd_spd_button4.set_active(True)
    elif self.prefs_values['speed_unit'] == 'Bf':
      wnd_spd_button5.set_active(True)
    else:
      wnd_spd_button1.set_active(True)

    timeout_label = Gtk.Label()
    box.pack_start(timeout_label, False, False, 0)
    timeout_label.set_markup('<b>Refresh time (minutes):</b>')
    time_out = Gtk.Entry()
    box.pack_start(time_out, False, False, 5)
    time_out.set_text(str(self.get_timeout()))
    timeout_label.set_halign(Gtk.Align.START)

    font_label = Gtk.Label()
    box.pack_start(font_label, False, False, 5)
    font_label.set_markup('<b>Font size:</b>')
    font_adjustment = Gtk.Adjustment(lower=9, upper=48, step_increment=1, page_increment=10)
    font = Gtk.SpinButton()
    font.set_adjustment(font_adjustment)
    box.pack_start(font, False, False, 0)
    font.set_value(int(self.prefs_values['font_size']))
    font_label.set_halign(Gtk.Align.START)

    #  lockButton = Gtk.Button.new_with_label("Lock position")
    #  lockButton.connect("clicked", lock_position)
    #  box.pack_end(lockButton,False,False,5)
    #  lockButton.connect("clicked", lock_position)
    #  context = lockButton.get_style_context()
    #  context.add_class('prefs')

    button = Gtk.Button.new_with_label("Save and reload")
    button.connect("clicked", save_and_reload, self)
    box.pack_end(button, False, False, 5)
    #    context = button.get_style_context()
    #    context.add_class('prefs')

    win.connect('destroy', Gtk.main_quit)
    win.show_all()
    Gtk.main()

