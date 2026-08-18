# /home/Warzen/Color-My-Desktop/colormydesktop/config.py

# Single Point of Truth mapping your options rows to their respective toggle switches
SWITCH_REVEAL_MAP = {
    "topbarcolor": "topbar_toggle",
    "datemenucolor": "datemenu_toggle",
    # Simply add future custom features here to scale infinitely!
}

# Live memory storage container tracking toggle values (True = custom active, False = inherit/primary)
FEATURE_SWITCH_STATES = {
    "topbarcolor": False,
    "datemenucolor": False,
}
# Maps your unique 'css_id' fields straight to their exact matching SVG __TOKENS__
COLOR_REGISTRY_MAP = {
    # Home Page Rows
    "primary": "__PRIMARY__",
    "secondary": "__SECONDARY__",
    "accent": "__ACCENT__",
    "text": "__TEXT__",
    # Advanced GNOME Options Rows (Add new custom rows right here!)
    "topbarcolor": "__TOPBAR__",
    "datemenucolor": "__DATEMENU__",  # Example: Simply add lines here to expand your app!
    "panelcolor": "__PANEL__",  # Example
}


def get_default_color_map():
    """Returns baseline fallback colors if a dictionary lookup is completely empty."""
    return {
        "primary": "#246cc5",
        "secondary": "#1a4d8c",
        "accent": "#102f54",
        "text": "#ffffff",
        "topbarcolor": "INHERIT",
        "datemenucolor": "INHERIT",
    }
