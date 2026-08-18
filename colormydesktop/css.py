# /home/Warzen/Color-My-Desktop/colormydesktop/css.py
BASE_STYLE_SHEET = """
.color-preview-dot {
    border-radius: 6px;
    border: 1px solid rgba(0,0,0,0.3);
    transition: all 0.2s ease-in-out;
    min-width: 26px;
    min-height: 26px;
}

.preview-dropper-icon {
    transition: opacity 0.2s ease;
    opacity: 0.5;
}

/* --- HOVER PHYSICS MAPS LINKED TO YOUR BLUEPRINT ROW STYLE CLASS --- */
.color-row-css:hover .color-preview-dot,
.color-row-css:focus-within .color-preview-dot {
    transform: scale(1.18);
    box-shadow: 0 0 12px rgba(255, 255, 255, 0.25);
    border-color: rgba(255, 255, 255, 0.6);
}

.color-row-css:hover .preview-dropper-icon,
.color-row-css:focus-within .preview-dropper-icon {
    opacity: 1.0;
}

.color-preview-container:active .color-preview-dot {
    transform: scale(0.92);
    transition: transform 0.05s;
}

/* Base mockup layout dimensions constraints */
#mockup-preview-image {
    margin-top: -80px;
    margin-bottom: -60px;
    padding: 0px;
    width: 100%;
}

#mockup-wrapper {
    border-radius: 12px;
    background: linear-gradient(165deg, #181818 0%, #080808 100%);
    padding: 0px; 
    min-height: 10px;
}
"""
