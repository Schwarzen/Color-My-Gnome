#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🎨 Compiling Blueprint UI files..."

# 1. Main Window
blueprint-compiler compile main_window.blp --output ../main_window.ui
echo "✓ Compiled main_window.ui"

# 2. Home Page
blueprint-compiler compile page_home.blp --output ../page_home.ui
echo "✓ Compiled page_home.ui"

# 3. Color Row Item
blueprint-compiler compile color_row_item.blp --output ../color_row_item.ui
echo "✓ Compiled color_row_item.ui"

blueprint-compiler compile advanced_page.blp --output ../advanced_page.ui
echo "✓ Compiled advanced_options.ui"

blueprint-compiler compile gnome_options.blp --output ../gnome_options.ui
echo "✓ Compiled gnome_options.ui"

blueprint-compiler compile gnome_setup_dialog.blp --output ../gnome_setup_dialog.ui
echo "✓ Compiled gnome_setup_dialog.ui"

echo "✨ All UI files compiled successfully!"
