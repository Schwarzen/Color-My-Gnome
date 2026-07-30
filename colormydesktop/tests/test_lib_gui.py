import importlib
import os
import pytest
from gi.repository import Gtk

def test_universal_playground(gui_playground):
    """
    Dynamically imports and mounts whatever widget class you are currently editing.
    Safely bypasses GTK4 parent constraints to prevent blank renders.
    """
    target_module = os.getenv("PLAYGROUND_MODULE", "colormydesktop.lib_gui")
    target_class = os.getenv("PLAYGROUND_CLASS")
    
    if not target_class:
        pytest.skip("No TARGET_CLASS defined. Skipping playground loop.")

    # 1. Dynamically import the target element class
    mod = importlib.import_module(target_module)
    WidgetClass = getattr(mod, target_class)
    
    # 2. Spin up our boilerplate window container
    ctx = gui_playground(title=f"Live Component Audit: {target_class}")
    live_widget = WidgetClass()
    
    # 3. Handle specific class layout configurations
    if isinstance(live_widget, Gtk.Window):
        ctx["window"].destroy()
        ctx["loop"].connect("destroy", lambda w: ctx["loop"].quit())
        live_widget.present()
        return

    # 4. FIX: Handle GTK4 Parent Constraint Rules
    # If the widget already has a parent container inside your production code,
    # we un-parent it from that temporary block so our window can display it.
    current_parent = live_widget.get_parent()
    if current_parent is not None:
        # If it belongs to an internal container box, pull that outer box instead
        if hasattr(current_parent, "unparent"):
            live_widget.unparent()
        elif hasattr(current_parent, "remove"):
            current_parent.remove(live_widget)
            
    # 5. Drop the freshly isolated widget cleanly into our display box
    ctx["box"].append(live_widget)

