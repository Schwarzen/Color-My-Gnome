import gi

import cairo

gi.require_version("Gtk", "4.0")
gi.require_version("Rsvg", "2.0")
from gi.repository import Gtk, Gdk, Rsvg


class InteractiveMockup(Gtk.DrawingArea):
    """
    A custom interactive widget that renders an SVG mockup, tracks accurate mouse coordinates,
    updates layout hover highlight overlays, and handles independent shape click callbacks.
    """

    def __init__(self, raw_svg_template):
        super().__init__()

        print(
            f"DEBUG: SVG data string received successfully! Total characters: {len(raw_svg_template)}"
        )
        # Store the clean, un-mutated master SVG text layout template
        self.raw_svg_template = raw_svg_template
        # Load your raw SVG template directly into memory
        baseline_svg = self.raw_svg_template
        baseline_svg = baseline_svg.replace("__PRIMARY__", "#1a4d8c")
        baseline_svg = baseline_svg.replace("__SECONDARY__", "#1a4d8c")
        baseline_svg = baseline_svg.replace("__ACCENT__", "#102f54")
        baseline_svg = baseline_svg.replace("__TEXT__", "#ffffff")
        # State tracking flags

        try:
            self.handle = Rsvg.Handle.new_from_data(baseline_svg.encode("utf-8"))
            print("[MOCKUP SYSTEM] Base SVG compiled successfully!")
        except Exception as error:
            print(f"[MOCKUP SYSTEM] CRITICAL PARSE ERROR: {error}")

        self.hovered_element = None

        self.interactive_element_ids = ["topbar", "datemenu", "powermenu"]
        # 2. Configure widget options to capture interaction events
        self.set_draw_func(self.on_draw)

        # 3. Attach standard GTK4 pointer controllers for inputs
        motion_ctrl = Gtk.EventControllerMotion()
        motion_ctrl.connect("motion", self.on_mouse_moved)
        motion_ctrl.connect("leave", self.on_mouse_left)
        self.add_controller(motion_ctrl)

        click_ctrl = Gtk.GestureClick()
        click_ctrl.connect("pressed", self.on_mockup_clicked)
        self.add_controller(click_ctrl)

    def update_colors(self, color_data_map):
        """
        Force-cleans incoming parameters to guarantee strict hex validation.
        this is where the SVG variables are replaced by the live color values
        """

        from colormydesktop.config import COLOR_REGISTRY_MAP, get_default_color_map

        # 1. Start with a baseline fallback structure
        final_colors = get_default_color_map()
        # 2. Overwrite defaults with any live values currently present in our data map
        final_colors.update(color_data_map)

        def sanitize(hex_val):
            hex_val = str(hex_val).strip().replace(";", "")
            if hex_val and not hex_val.startswith("#"):
                hex_val = f"#{hex_val}"
            return hex_val

        # 3. Perform automated string iteration over the SVG template document bytes
        processed_svg = self.raw_svg_template

        for css_id, svg_token in COLOR_REGISTRY_MAP.items():
            # Grab the hex value, sanitize it, and execute a dynamic text replace!
            hex_value = sanitize(final_colors.get(css_id, "#ffffff"))
            processed_svg = processed_svg.replace(svg_token, hex_value)

        try:
            self.handle = None
            self.handle = Rsvg.Handle.new_from_data(processed_svg.encode("utf-8"))
            self.queue_allocate()
            self.queue_draw()
        except Exception as error:
            print(f"[MOCKUP SYSTEM] Automated loop compilation error: {error}")

    def _get_svg_base_dimensions(self):
        """
        Queries layout viewBox dimensions safely using positional indexing
        to completely bypass tuple unpacking parameter length mismatch crashes.
        """
        if not self.handle:
            return 400.0, 300.0

        try:
            # 1. Capture the output variables together inside a flat tuple array container
            intrinsic_data = self.handle.get_intrinsic_dimensions()

            # The viewBox structure is consistently delivered as the very last element (-1)
            viewbox = intrinsic_data[-1]

            # The 'has_viewbox' flag sits as the second-to-last item (-2)
            has_viewbox = intrinsic_data[-2]

            if has_viewbox and viewbox is not None:
                # If a valid viewBox layout geometry scale is found, return its bounds
                print(
                    f"[RECOVERY DEBUG] Extracted viewBox values -> W: {viewbox.width}, H: {viewbox.height}"
                )
                return float(viewbox.width), float(viewbox.height)
        except Exception as error:
            print(f"[RECOVERY ERROR] Intrinsic lookup failed: {error}")

        # 2. STANDARD FALLBACK
        # If the tuple structure is unexpected, query the baseline pixel bounds property
        dimensions = self.handle.get_dimensions()
        if dimensions.width > 0 and dimensions.height > 0:
            return float(dimensions.width), float(dimensions.height)

        # Global backup resolution
        return 400.0, 300.0

    def on_draw(self, drawing_area, cr, width, height):
        if not self.handle:
            return

        svg_w, svg_h = self._get_svg_base_dimensions()

        scale_x = width / svg_w
        scale_y = height / svg_h

        # Render the base document SVG asset
        cr.save()
        cr.scale(scale_x, scale_y)

        viewport = Rsvg.Rectangle()
        viewport.x, viewport.y, viewport.width, viewport.height = 0.0, 0.0, svg_w, svg_h
        self.handle.render_document(cr, viewport)
        cr.restore()

        # ID-TARGETED HIGHLIGHT OVERLAY
        if self.hovered_element and self.handle:
            try:
                # FIX 1: Unpack 'logical_rect' instead of relying solely on local bounds
                success, _, logical_rect = self.handle.get_geometry_for_element(
                    f"#{self.hovered_element}"
                )

                if success and logical_rect is not None:
                    # TRANSFORM METRICS: Maps the global layout rect straight to screen pixels
                    screen_x = logical_rect.x * scale_x
                    screen_y = logical_rect.y * scale_y
                    screen_w = logical_rect.width * scale_x
                    screen_h = logical_rect.height * scale_y

                    # Draw selection frame over the calculated global layout pixel bounds
                    cr.set_source_rgba(1.0, 1.0, 1.0, 0.18)
                    cr.rectangle(screen_x, screen_y, screen_w, screen_h)
                    cr.fill_preserve()

                    cr.set_source_rgba(1.0, 1.0, 1.0, 0.5)
                    cr.set_line_width(1.5)
                    cr.stroke()
            except Exception as e:
                print(f"[DRAW ERROR] Highlight fail: {e}")

    def _get_element_at_pos(self, x, y):
        """
        Calculates matrix transformations dynamically to map mouse coordinate bounds
        directly onto native XML element IDs using global logical dimensions.
        """
        if not self.handle:
            return None

        svg_w, svg_h = self._get_svg_base_dimensions()
        w = self.get_width()
        h = self.get_height()
        if w <= 0 or h <= 0:
            return None

        # Translate actual screen cursor pixels back down into unscaled file grid coordinates
        svg_x = (x / w) * svg_w
        svg_y = (y / h) * svg_h

        # Loop through your element IDs to detect direct vector bounding hits
        for element_id in self.interactive_element_ids:
            try:
                # FIX 2: Check logical boundaries to catch grouped translations
                success, _, logical_rect = self.handle.get_geometry_for_element(
                    f"#{element_id}"
                )

                if success and logical_rect is not None:
                    # Check if the unscaled mouse cursor sits inside the global layout coordinates
                    if logical_rect.x <= svg_x <= (
                        logical_rect.x + logical_rect.width
                    ) and logical_rect.y <= svg_y <= (
                        logical_rect.y + logical_rect.height
                    ):
                        return element_id
            except Exception:
                continue
        return None

    def on_mouse_moved(self, controller, x, y):
        detected_hit = self._get_element_at_pos(x, y)

        if detected_hit != self.hovered_element:
            self.hovered_element = detected_hit
            # Change mouse cursor style dynamically based on hit state
            if self.hovered_element:
                self.set_cursor(Gdk.Cursor.new_from_name("pointer", None))
            else:
                self.set_cursor(None)
            self.queue_draw()  # Tells GTK to trigger a graphical refresh immediately

    def on_mouse_left(self, controller):
        self.hovered_element = None
        self.set_cursor(None)
        self.queue_draw()

    def on_mockup_clicked(self, gesture, n_press, x, y):
        clicked_element = self._get_element_at_pos(x, y)
        if clicked_element:
            # 3. ROUTE THE MOCKUP CLICK EVENT INTO THE BROKER GRAPH GLOBALLY!
            from colormydesktop.broker import ContextBroker

            ContextBroker.translate_action(
                sender_id="InteractiveMockup",
                action_type="CLICKED_MOCKUP_ELEMENT",
                payload={"element_id": clicked_element},
            )

    def execute_mockup_action(self, element_id):
        """
        Maps element clicks directly out to your external application logic blocks.
        """
        print(f"[MOCKUP INTERACTION] Target item clicked: {element_id}")

        if element_id == "topbar":
            # Fire an external function, toggle row displays, or pop open a submenu!
            pass
