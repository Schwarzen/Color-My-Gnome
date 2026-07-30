# /home/Warzen/Color-My-Desktop/colormydesktop/tests/conftest.py
import pytest
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

@pytest.fixture
def gui_playground(monkeypatch):
    """
    A reusable fixture that provides a window launcher for visual testing.
    Wipes out headless modes and provides a clean container canvas.
    """
    # Force UI display back on for live interactions
    monkeypatch.delenv("GDK_BACKEND", raising=False)
    monkeypatch.delenv("A11Y_FORCE_STATE_SET", raising=False)
    
    # Track the active window inside a wrapper container to pass to the test
    window_data = {
        "window": None,
        "box": None,
        "loop": None
    }
    
    def _create_playground(title="Widget Playground", width=400, height=200):
        # Create standard layout scaffold
        win = Gtk.Window(title=title)
        win.set_default_size(width, height)
        
        # Center layout box with standard layout padding
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(15)
        box.set_margin_bottom(15)
        box.set_margin_start(15)
        box.set_margin_end(15)
        
        win.set_child(box)
        
        # Lock loop control properties
        loop = GLib.MainLoop()
        win.connect("destroy", lambda w: loop.quit())
        
        window_data["window"] = win
        window_data["box"] = box
        window_data["loop"] = loop
        return window_data
        
    yield _create_playground
    
    # Post-Test Execution Loop Action
    # If the test function added a widget, this spins up and displays the playground
    if window_data["window"]:
        window_data["window"].present()
        print("\n[INFO] Playground open. Close the window to resume development...")
        window_data["loop"].run()

