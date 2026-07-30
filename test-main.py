#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, Gtk, Gdk
from colormydesktop.lib_gui import MyMainWindow, PageHomeView
from colormydesktop.css import BASE_STYLE_SHEET


class TestColorApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="io.github.schwarzen.colormydesktop.test",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

    def do_activate(self):
        self.global_css_provider = Gtk.CssProvider.new()

        # We pre-load the static base blueprint hover parameters instantly
        # We initialize it with a safe default background color token
        initial_styles = BASE_STYLE_SHEET.replace("__BG_COLOR__", "#181a1e")
        self.global_css_provider.load_from_string(initial_styles)

        # Attach the provider to the entire layout screen pool interface layer
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.global_css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
        self.win = MyMainWindow(application=self)

        mock_themes = ["Default Slate", "Arch Dark", "GNOME Classic", "Nordic Winter"]

        # FIXED: Pass the custom list as a clean positional argument, keeping kwargs separate
        home_page_view = PageHomeView(
            themes_list_data=mock_themes, css_provider=self.global_css_provider
        )

        self.win.nav_view.push(home_page_view)
        self.win.present()


def main():
    app = TestColorApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
