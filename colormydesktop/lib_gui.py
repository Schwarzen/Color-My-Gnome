import gi
import os
import sys
from colormydesktop.mockup import InteractiveMockup
from colormydesktop.advancedpref import AdvancedMixin
from colormydesktop.dialogs import DialogMixin
from colormydesktop.functions import ThemeManager
from gi.repository import Gtk, Adw, Gio, Gdk

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

if os.environ.get("FLATPAK_ID"):
    # Inside Flatpak, the script is at /app/bin/
    BASH_SCRIPT = "/app/bin/color-my-desktop-backend"
    SCSS_DIR = os.path.expanduser(
        "~/.var/app/io.github.schwarzen.colormydesktop/data/scss"
    )
    SCSS_USR = os.path.expanduser(
        "~/.var/app/io.github.schwarzen.colormydesktop/data/scss"
    )
    PALETTES = "/app/share/color-my-desktop/palettes"
    PYTHON_DIR = "/app/bin/colormydesktop"
else:
    # Native install location
    BASH_SCRIPT = os.path.expanduser("~/.local/bin/color-my-desktop-backend")
    SCSS_DIR = os.path.expanduser("~/.local/share/color-my-desktop/scss")
    SCSS_USR = os.path.expanduser("~/.local/share/color-my-desktop/scss")
    PALETTES = os.path.expanduser("~/.local/share/color-my-desktop/palettes")
    PYTHON_DIR = os.path.expanduser("~/.local/bin/colormydesktop")


# SECTION: DYNAMIC COLOR ENTRY ROW OBJECT {{{
@Gtk.Template(filename=f"{PYTHON_DIR}/color_row_item.ui")
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

    def __init__(
        self,
        main_page_context,
        label,
        default_hex,
        css_id,
        show_magic=True,
        manager_instance=None,
    ):
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

        self.manager = manager_instance

        from colormydesktop.broker import ContextBroker

        # 1. Route text changes to the Broker
        self.connect_after(
            "changed",
            lambda entry: ContextBroker.translate_action(
                sender_id=self.home_page.__class__.__name__,
                action_type="CHANGED_TEXT_INPUT",
                payload={"entry_row": self, "css_id": css_id},
            ),
        )

        # 2. Route Advanced Picker Clicks to the Broker
        adv_gesture = Gtk.GestureClick.new()
        adv_gesture.connect(
            "pressed",
            lambda g, n, x, y: ContextBroker.translate_action(
                sender_id=self.home_page.__class__.__name__,
                action_type="CLICKED_ADVANCED_PICKER",
                payload={"gesture": g, "n_press": n, "x": x, "y": y, "entry_row": self},
            ),
        )
        self.advanced_btn.add_controller(adv_gesture)

        # 3. Route Quick Picker Clicks to the Broker
        quick_gesture = Gtk.GestureClick.new()
        quick_gesture.connect(
            "pressed",
            lambda g, n, x, y: ContextBroker.translate_action(
                sender_id=self.home_page.__class__.__name__,
                action_type="CLICKED_QUICK_PICKER",
                payload={"gesture": g, "n_press": n, "x": x, "y": y, "entry_row": self},
            ),
        )
        self.quick_btn.add_controller(quick_gesture)
        # Connect methods that are now safely declared in PageHomeView below
        # self.magic_btn.connect("clicked", self.home_page.on_generate_variants_clicked)
        # self.fix_btn.connect("clicked", self.home_page.on_fix_contrast_clicked)


# }}}
# SECTION: GnomeSetupDialog
@Gtk.Template(filename=f"{PYTHON_DIR}/gnome_setup_dialog.ui")
class GnomeSetupDialog(Gtk.Box):
    __gtype_name__ = "GnomeSetupDialog"

    # Bind elements we need to interact with dynamically
    status_expander = Gtk.Template.Child()
    host_path_label = Gtk.Template.Child()

    def __init__(self, parent_window=None, theme_manager=None, **kwargs):
        super().__init__(**kwargs)

        from colormydesktop.broker import ContextBroker

        self.manager = getattr(ContextBroker, "manager", None)

        # 1. Fallback for parent_window
        self.host_path = "~/.config/systemd/user"

        ContextBroker.register_page("gnome_setup_dialog", self)

        # 3. Safely execute status checks if manager exists
        self.run_status_check()

    def run_status_check(self):

        if self.manager and hasattr(self.manager, "get_safe_key"):
            safe_key = self.manager.get_safe_key(self.host_path)
        else:
            safe_key = None  # Or your default fallback value
            print("no safe key used")
        # Look for path in Memory -> then File Cache
        portal_path = getattr(self.manager, f"active_portal_{safe_key}", None)

        if not portal_path:
            portal_path = self.manager.load_cached_portal_path(self.host_path)
            if portal_path:
                setattr(self.manager, f"active_portal_{safe_key}", portal_path)

        # Accurate Status Checks
        has_access = portal_path is not None and os.path.exists(portal_path)
        path_exists = False
        service_exists = False

        if has_access:
            path_exists = os.path.isfile(
                os.path.join(portal_path, "gnome-refresher.path")
            )
            service_exists = os.path.isfile(
                os.path.join(portal_path, "gnome-refresher.service")
            )

        # Add dynamic rows to the expander
        display_path = portal_path if portal_path else "Folder Not Linked"
        self.status_expander.add_row(
            self.create_status_row(f"Portal Access: {display_path}", has_access)
        )
        self.status_expander.add_row(
            self.create_status_row("Systemd .path file found", path_exists)
        )
        self.status_expander.add_row(
            self.create_status_row("Systemd .service file found", service_exists)
        )

    def create_status_row(self, title, is_ready):
        """Helper to generate styled Adw.ActionRows for status"""
        row = Adw.ActionRow(title=title)
        icon_name = "emblem-ok-symbolic" if is_ready else "window-close-symbolic"
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.add_css_class("success" if is_ready else "error")
        row.add_prefix(icon)
        return row

    # --- UI Signal Handlers from Blueprint ---

    @Gtk.Template.Callback()
    def on_copy_path_clicked(self, *args):
        expanded_path = os.path.expanduser(self.host_path)
        Gdk.Display.get_default().get_clipboard().set_content(
            Gdk.ContentProvider.new_for_value(expanded_path)
        )
        self._show_toast("Path copied!")

    @Gtk.Template.Callback()
    def on_copy_cmd_clicked(self, *args):
        full_cmd = "systemctl --user daemon-reload && systemctl --user enable --now gnome-refresher.path"
        Gdk.Display.get_default().get_clipboard().set_content(
            Gdk.ContentProvider.new_for_value(full_cmd)
        )
        self._show_toast("Command copied!")

    @Gtk.Template.Callback()
    def on_installer_clicked(self, *args):
        # Trigger the installer function from your logic manager
        self.manager.install_gnome_host_refresher()

    def _show_toast(self, message):
        """Helper to show toast notifications via the main window's toast overlay"""
        # Assumes ThemeManager or parent_window has the toast_overlay bound
        if hasattr(self.manager, "toast_overlay"):
            self.manager.toast_overlay.add_toast(Adw.Toast.new(message))


# SECTION: GNOME OPTIONS {{{
@Gtk.Template(filename=f"{PYTHON_DIR}/gnome_options.ui")
class GnomeOptions(Gtk.Box):
    __gtype_name__ = "GnomeOptions"
    topbar_color_row = Gtk.Template.Child()
    datemenu_color_row = Gtk.Template.Child()
    topbar_toggle = Gtk.Template.Child()
    datemenu_toggle = Gtk.Template.Child()
    refresh_switch = Gtk.Template.Child()
    from colormydesktop.functions import ThemeManager

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.environment_status()
        self.color_entries = {}
        self.status_labels = {}
        self.status_buttons = {}
        self.current_colors = {}
        self.home_page = self
        from colormydesktop.broker import ContextBroker

        # Synchronize toggle states dynamically from your UI switches on startup
        # Assumes 'topbar_toggle' and 'datemenu_toggle' are bound Gtk.Template.Child elements
        advanced_gnome_configurations = [
            {
                "label": "TopBar Color",
                "hex": "#246cc5",
                "id": "topbarcolor",
            },
            {
                "label": "Datemenu Color",
                "hex": "#246cc5",
                "id": "datemenucolor",
            },
        ]

        for config in advanced_gnome_configurations:
            entry_row = ColorEntryRow(
                main_page_context=self,
                label=config["label"],
                default_hex=config["hex"],
                css_id=config["id"],
            )
            self.color_entries[config["id"]] = entry_row
            self.status_labels[config["id"]] = entry_row.status_label
            self.current_colors[config["id"]] = config["hex"]

            if config["id"] == "topbarcolor":
                self.topbar_color_row.add(entry_row)
            elif config["id"] == "datemenucolor":
                self.datemenu_color_row.add(entry_row)

            if ContextBroker.manager:
                ContextBroker.manager.update_preview(entry_row, config["id"])

        # Connect your toggle switch signals exactly like before
        self.switches = {
            "topbarcolor": self.topbar_toggle,
            "datemenucolor": self.datemenu_toggle,
            "refresh_switch": self.refresh_switch,
        }

        for css_id, switch_widget in self.switches.items():
            switch_widget.connect(
                "notify::active",
                lambda sw, pspec, cid=css_id: ContextBroker.translate_action(
                    sender_id="GnomeOptions",
                    action_type="TOGGLED_FEATURE_SWITCH",
                    payload={
                        "css_id": cid,
                        "is_active": sw.get_active(),
                        "widget": sw,
                        "page": self,  # <-- Pass the GnomeOptions instance as 'self'
                    },
                ),
            )

    def environment_status(self):
        from colormydesktop.broker import ContextBroker

        is_flatpak = os.path.exists("/.flatpak-info")

        if not is_flatpak:
            ready = True
        else:
            theme_manager = getattr(ContextBroker, "manager", None)
            if theme_manager and hasattr(theme_manager, "is_gnome_refresh_ready"):
                # Call using the actual ThemeManager instance as 'self'
                ready = theme_manager.is_gnome_refresh_ready()
            else:
                ready = False

            # Check dictionary storage or direct template child attribute
        if hasattr(self, "switches") and "refresh_switch" in self.switches:
            self.switches["refresh_switch"].set_active(ready)
        elif hasattr(self, "refresh_switch") and self.refresh_switch:
            self.refresh_switch.set_active(ready)

    @property
    def manager(self):
        """
        Dynamically climbs the widget tree to find the live root window
        and extracts the active ThemeManager instance.
        """
        root_window = self.get_root()
        if root_window and hasattr(root_window, "logic"):
            return root_window.logic

        # Fallback trace: check if your main application layer holds it under self.manager
        if root_window and hasattr(root_window, "manager"):
            return root_window.manager

        print("[MOCKUP ERROR] Could not locate an active ThemeManager instance.")
        return None


#             }}}
# SECTION: ADVANCED PAGE {{{
@Gtk.Template(filename=f"{PYTHON_DIR}/advanced_page.ui")
class AdvancedPage(Gtk.Box):
    __gtype_name__ = "AdvancedPage"

    gnome_options = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from colormydesktop.broker import ContextBroker

        ContextBroker.register_page("advanced_options", self)

    @Gtk.Template.Callback()
    def on_gnome_card_pressed(self, gesture, n_press, x, y):
        from colormydesktop.lib_gui import GnomeOptions
        from colormydesktop.broker import ContextBroker

        # Explicit, readable, and highly maintainable:
        # Pass 'self' (the AdvancedPage), the class blueprint, and your string identifier key.
        ContextBroker.navigate(
            current_widget=self, target_page_class=GnomeOptions, page_id="gnome_options"
        )


# }}}
# SECTION: HOME PAGE {{{
@Gtk.Template(filename=f"{PYTHON_DIR}/page_home.ui")
class PageHomeView(Adw.NavigationPage):
    __gtype_name__ = "PageHomeView"

    color_rows_group = Gtk.Template.Child()
    mockup_wrapper = Gtk.Template.Child()
    mockup_image = Gtk.Template.Child()
    show_mockup_switch = Gtk.Template.Child()
    combo_row = Gtk.Template.Child()
    name_row = Gtk.Template.Child()
    advanced_options_action_btn = Gtk.Template.Child()
    build_btn = Gtk.Template.Child()
    # MAIN SWITCHES
    gnome_switch = Gtk.Template.Child()
    plasma_switch = Gtk.Template.Child()
    gtk4_switch = Gtk.Template.Child()
    zen_switch = Gtk.Template.Child()
    youtube_switch = Gtk.Template.Child()
    vesktop_switch = Gtk.Template.Child()

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

        # 2. INSTANTIATE YOUR INTERACTIVE MOCKUP WIDGET
        # Pass the raw SVG text string into your custom canvas class
        self.interactive_preview = InteractiveMockup()

        # Optional layout settings to ensure it fills space gracefully
        self.interactive_preview.set_hexpand(True)
        self.interactive_preview.set_vexpand(True)

        # 3. SWAP THE WIDGETS IN THE PARENT CONTAINER
        # Find the parent layout widget that used to hold 'self.mockup_image'
        parent_container = self.mockup_image.get_parent()

        if parent_container:
            # Remove the old static image node
            parent_container.remove(self.mockup_image)

            # Insert your new interactive mockup canvas right where the old image lived
            parent_container.append(self.interactive_preview)

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
                "hex": "#e1251b",
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
        from colormydesktop.broker import ContextBroker

        ContextBroker.register_page("home_view", self)
        ContextBroker.manager = self.manager
        # FIX: Instantiate GnomeOptions EXACTLY ONCE right here on app launch!
        from colormydesktop.lib_gui import GnomeOptions

        ContextBroker.gnome_options_singleton = GnomeOptions()

        # Register it as an active view context immediately so the broker can read its defaults
        ContextBroker.register_page(
            "gnome_options", ContextBroker.gnome_options_singleton
        )

        for css_id, color_row in self.color_entries.items():
            color_row.manager = self.manager
            self.manager.update_preview(color_row, css_id)
            # Seed our central ContextBroker's current_colors map on startup
            # This fills up the dictionary using your default constructor text strings!
            self.current_colors[css_id] = color_row.get_text().strip()
        # Fire a simulated text input change event straight through the broker matrix
        # This gathers all rows, processes the "INHERIT" flags, and repaints SVG instantly on boot
        ContextBroker.translate_action(
            sender_id="PageHomeView",
            action_type="CHANGED_TEXT_INPUT",
            payload={
                "entry_row": list(self.color_entries.values())[0],
                "css_id": "primary",
            },
        )
        ContextBroker.translate_action(
            sender_id="PageHomeView",
            action_type="BUILD_BUTTON_CLICKED",
            payload={},
        )
        gnome_opts = (
            ContextBroker.gnome_options_singleton
        )  # or ContextBroker.get_page("gnome_options")

        # 2. Extract the active boolean state
        is_active = False
        if gnome_opts:
            # If stored in your self.switches dictionary:
            if (
                hasattr(gnome_opts, "switches")
                and "refresh_switch" in gnome_opts.switches
            ):
                is_active = gnome_opts.switches["refresh_switch"].get_active()

            # Or if bound directly as a Template.Child:
            elif hasattr(gnome_opts, "refresh_switch"):
                is_active = gnome_opts.refresh_switch.get_active()
        self.manager.initial_status(self, is_active)

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


# }}}
# SECTION: MAIN WINDOW {{{
@Gtk.Template(filename=f"{PYTHON_DIR}/main_window.ui")
class MyMainWindow(Adw.ApplicationWindow):
    __gtype_name__ = "MyMainWindow"

    nav_view = Gtk.Template.Child()
    close_btn = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.close_btn.connect("clicked", lambda _: self.close())


# }}}
