import gi
import os
import sys
from colormydesktop.dialogs import DialogMixin
from colormydesktop.functions import ThemeManager
from gi.repository import Gtk, Adw, Gio, Gdk

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

PYTHON_DIR = os.path.dirname(os.path.abspath(__file__))


@Gtk.Template(filename="colormydesktop/color_row_item.ui")
class ColorEntryRow(Adw.EntryRow):
    __gtype_name__ = "ColorEntryRow"

    advanced_btn = Gtk.Template.Child()
    advanced_bg_box = Gtk.Template.Child()
    advanced_icon = Gtk.Template.Child()
    quick_btn = Gtk.Template.Child()
    quick_bg_box = Gtk.Template.Child()
    quick_icon = Gtk.Template.Child()
    status_label = Gtk.Template.Child()
    fix_btn = Gtk.Template.Child()
    magic_btn = Gtk.Template.Child()

    def __init__(self, main_page_context, label, default_hex, css_id, show_magic=True):
        super().__init__()
        self.home_page = main_page_context
        self.css_id = css_id
        self.set_title(label)
        self.set_text(default_hex)

        self.advanced_bg_box.set_name(f"{css_id}-preview")
        self.quick_bg_box.set_name(f"{css_id}-preview")
        self.advanced_icon.set_name(f"{css_id}-icon")
        self.quick_icon.set_name(f"{css_id}-icon")
        self.magic_btn.set_visible(show_magic)

        self.connect_after(
            "changed", lambda entry: self.home_page.manager.update_mockup_css()
        )
        self.connect(
            "changed",
            lambda entry: self.home_page.manager.update_preview(entry, css_id),
        )

        # Connect methods that are now safely declared in PageHomeView below
        self.magic_btn.connect("clicked", self.home_page.on_generate_variants_clicked)
        self.fix_btn.connect("clicked", self.home_page.on_fix_contrast_clicked)

        adv_gesture = Gtk.GestureClick.new()
        adv_gesture.connect(
            "pressed",
            lambda g, n, x, y: self.home_page.manager.on_advanced_picker_clicked(
                g, n, x, y, self
            ),
        )
        self.advanced_btn.add_controller(adv_gesture)

        quick_gesture = Gtk.GestureClick.new()
        quick_gesture.connect(
            "pressed",
            lambda g, n, x, y: self.home_page.manager.on_quick_picker_clicked(
                g, n, x, y, self
            ),
        )
        self.quick_btn.add_controller(quick_gesture)


@Gtk.Template(filename="colormydesktop/page_home.ui")
class PageHomeView(Adw.NavigationPage):
    __gtype_name__ = "PageHomeView"

    color_rows_group = Gtk.Template.Child()
    mockup_wrapper = Gtk.Template.Child()
    mockup_image = Gtk.Template.Child()
    show_mockup_switch = Gtk.Template.Child()
    gnome_switch = Gtk.Template.Child()

    def __init__(self, themes_list_data=None, css_provider=None, **kwargs):
        # FIX A: Extract custom parameters before initializing the underlying GObject
        super().__init__(**kwargs)
        self.css_provider = css_provider
        # Attach the provider to the entire screen layout engine display pool.
        # This guarantees that ANY widget nested inside this page can read your dynamic CSS rules!
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        # 1. LOAD THE SVG PAINTABLE ASSET (Identical to your original code)
        svg_path = os.path.join(PYTHON_DIR, "preview-symbolic.svg")
        if os.path.exists(svg_path):
            svg_file = Gio.File.new_for_path(svg_path)
            # Create the dynamic scale target descriptor
            self.mockup_paintable = Gtk.IconPaintable.new_for_file(svg_file, 1200, -1)
            # Inject the loaded data object straight into your blueprint Image node
            self.mockup_image.set_from_paintable(self.mockup_paintable)

        # 2. CONNECT THE RESPONSIVE TOGGLE EVENT
        # When clicked on small viewports, it hides/reveals column B below column A
        self.show_mockup_switch.connect("notify::active", self.on_mockup_toggle_changed)

        self.themes = themes_list_data or []
        self.color_entries = {}
        self.status_labels = {}
        self.status_buttons = {}
        self.current_colors = {}

        color_configurations = [
            {
                "label": "Primary Color",
                "hex": "#246cc5",
                "id": "primary",
                "magic": False,
            },
            {
                "label": "Secondary",
                "hex": "#5e6c7d",
                "id": "secondary",
                "magic": False,
            },
            {
                "label": "Accent",
                "hex": "#f4f5f7",
                "id": "accent",
                "magic": False,
            },
            {
                "label": "Text",
                "hex": "#e1251b",
                "id": "text",
                "magic": True,
            },
        ]

        for config in color_configurations:
            color_row = ColorEntryRow(
                main_page_context=self,
                label=config["label"],
                default_hex=config["hex"],
                css_id=config["id"],
                show_magic=config["magic"],
            )

            self.color_entries[config["id"]] = color_row
            self.status_labels[config["id"]] = color_row.status_label
            self.status_buttons[config["id"]] = color_row.fix_btn
            self.current_colors[config["id"]] = config["hex"]

            self.color_rows_group.add(color_row)
        self.manager = ThemeManager(ui_context=self)
        for css_id, color_row in self.color_entries.items():
            self.manager.update_preview(color_row, css_id)

        self.manager.update_mockup_css()

    def on_mockup_toggle_changed(self, switch_row, pspec):
        """
        Manually syncs the visible state of your layout panel whenever the
        user updates the mobile/narrow viewport switch row.
        """
        is_checked = switch_row.get_active()
        self.mockup_wrapper.set_visible(is_checked)
        print(
            f"[ADAPTIVE LOGIC] Mockup visibility overridden manually to: {is_checked}"
        )

    # FIX B: Added real fallback methods to ensure the ColorEntryRow setup doesn't crash on init

    def on_generate_variants_clicked(self, button):
        pass

    def on_fix_contrast_clicked(self, button):
        pass

    def on_advanced_picker_clicked(self, gesture, n_press, x, y, target_entry):
        pass

    def on_quick_picker_clicked(self, gesture, n_press, x, y, target_entry):
        pass


@Gtk.Template(filename="colormydesktop/main_window.ui")
class MyMainWindow(Adw.ApplicationWindow):
    __gtype_name__ = "MyMainWindow"

    nav_view = Gtk.Template.Child()
    close_btn = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.close_btn.connect("clicked", lambda _: self.close())
