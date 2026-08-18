# /home/Warzen/Color-My-Desktop/colormydesktop/broker.py
from colormydesktop.config import FEATURE_SWITCH_STATES, SWITCH_REVEAL_MAP
from colormydesktop.dialogs import DynamicPopupWindow


class ContextBroker:
    # Storage bins for our unique live object instances
    _contexts = {}
    manager = None
    gnome_options_singleton = None

    @classmethod
    def register_page(cls, page_id, instance):
        """
        Allows any unique UI page (PageHomeView, GnomeOptions, etc.)
        to identify itself and register its live memory block.
        """
        cls._contexts[page_id] = instance
        print(
            f"[CONTEXT BROKER] Registered UI Layer mapping: '{page_id}' -> {instance}"
        )

    @classmethod
    def get_page(cls, page_id):
        """
        Retrieves a registered page context safely.
        """
        return cls._contexts.get(page_id, None)

    @classmethod
    def navigate(cls, current_widget, target_page_class, page_id):
        """
        Universal Routing Engine. Manages singletons, tracks memory allocations,
        and dynamically determines whether to SPAWN a fresh popup window or
        SWAP layout frames inside an existing one.
        """
        sender_name = current_widget.__class__.__name__
        sender_mem = hex(id(current_widget))
        target_name = target_page_class.__name__

        print(
            f"\n[ROUTER] {sender_name} ({sender_mem}) requested transition to {target_name}..."
        )

        # 1. Look for an existing permanent instance in our lazy-loading state pool
        live_instance = cls.get_page(page_id)

        if live_instance:
            instance_mem = hex(id(live_instance))
            print(
                f"   -> Existing instance found at {instance_mem}. Preparing canvas routing tracks..."
            )
        else:
            print(
                f"   -> Instance not found for key '{page_id}'. Creating fresh layout memory block now..."
            )
            live_instance = target_page_class()
            instance_mem = hex(id(live_instance))
            print(
                f"   -> Successfully allocated {target_name} memory registry node at {instance_mem}."
            )
            cls.register_page(page_id, live_instance)

        # 2. DETECT PARENT CONTEXT: Determine whether to SPAWN or SWAP
        root_window = current_widget.get_root()
        root_class_name = root_window.__class__.__name__ if root_window else ""

        # Adjust "MyMainWindow" to match whatever class name your main app window uses!
        if root_class_name == "MyMainWindow":
            print(
                f"   -> Parent popup window container NOT detected (Root is {root_class_name}). Spawning fresh Window shell wrapper..."
            )

            # Use your standard framework manager to overlay a beautiful new window canvas block
            DynamicPopupWindow.spawn(
                parent_window=root_window,
                title="Advanced Options",
                content_widget=live_instance,
            )
        else:
            print(
                f"   -> Active parent popup container detected ({root_class_name}). Swapping view layout tracks smoothly..."
            )
            # If a popup window is already open, safely slide the old page out and slide the new one in
            DynamicPopupWindow.swap_content(
                current_widget=current_widget, new_content_widget=live_instance
            )

    @classmethod
    def translate_action(cls, sender_id, action_type, payload):
        """
        The central translation matrix. It captures who called the function (sender_id),
        updates their local UI context if needed, and forces updates on completely separate pages.
        """
        if not cls.manager:
            print("[BROKER ERROR] No manager instance registered to handle events yet!")
            return

        print(
            f"\n[BROKER ACTION] '{sender_id}' requested a state mutation loop: '{action_type}'"
        )

        #  Fetch our unique targets out of the registration pool
        home_page = cls.get_page("home_view")
        gnome_page = cls.get_page("gnome_options")

        # --- HANDLE MOCKUP VECTOR CLICKS ---
        if action_type == "CLICKED_MOCKUP_ELEMENT":
            element_id = payload["element_id"]
            print(f"[BROKER LOG] Mockup shape vector context clicked: '{element_id}'")

            if element_id == "topbar":
                from colormydesktop.lib_gui import GnomeOptions

                # Look up our active Home View card container block to use as the base context
                home_view = cls.get_page("home_view")

                # Automatically open the GnomeOptions window when clicking the topbar preview!
                if home_view:
                    cls.navigate(
                        current_widget=home_view,
                        target_page_class=GnomeOptions,
                        page_id="gnome_options",
                    )

            elif element_id == "accent_button":
                # Trigger a quick picker color swap, toggle rows, or launch another sub-page!
                pass

        if action_type == "TOGGLED_FEATURE_SWITCH":
            css_id = payload["css_id"]
            is_active = payload["is_active"]

            # Save permanently to our centralized memory state cache container
            FEATURE_SWITCH_STATES[css_id] = is_active
            print(f"[BROKER STATE] Feature toggle '{css_id}' cached as: {is_active}")

            # FIX: If the switch was turned ON, dynamically inject the primary hex string
            if is_active and home_page and gnome_page:
                # 1. Grab the current live text inside the home view primary box
                live_primary_hex = home_page.current_colors.get("primary", "#246cc5")

                # 2. Find the target entry row widget inside your GnomeOptions view
                target_row = gnome_page.color_entries.get(css_id, None)

                if target_row:
                    # 3. Overwrite the row's inner entry text buffer directly via code!
                    # This visually populates the entry on screen and triggers its 'changed' signal
                    if hasattr(target_row, "set_text"):
                        target_row.set_text(live_primary_hex)
                    elif hasattr(target_row, "get_editable"):
                        target_row.get_editable().set_text(live_primary_hex)

                    print(
                        f"[BROKER AUTOFILL] Populated custom entry '{css_id}' with primary color: {live_primary_hex}"
                    )

            # Re-trigger a mockup update to paint the color adjustments loop
            action_type = "CHANGED_TEXT_INPUT"
            payload = {"entry_row": None, "css_id": "primary"}

        # --- A. HANDLE TYPING ACTIONS ---
        if action_type == "CHANGED_TEXT_INPUT":
            # Save standard input changes to memory
            if payload["entry_row"] is not None:
                row = payload["entry_row"]
                css_id = payload["css_id"]
                sender_page = (
                    cls.get_page("home_view")
                    if sender_id == "PageHomeView"
                    else cls.get_page("gnome_options")
                )
                if sender_page and hasattr(sender_page, "current_colors"):
                    sender_page.current_colors[css_id] = row.get_text().strip()
                cls.manager.update_preview(row, css_id)

            if home_page and hasattr(home_page, "interactive_preview"):
                master_color_payload = {}

                # Load baseline values from Home Page
                if hasattr(home_page, "current_colors"):
                    master_color_payload.update(home_page.current_colors)

                # SCALABLE PRE-FILTER LOOP
                # Automatically iterates across any custom row mapped to a switch controller
                for advanced_key in SWITCH_REVEAL_MAP.keys():
                    switch_is_on = FEATURE_SWITCH_STATES.get(advanced_key, False)

                    if (
                        switch_is_on
                        and gnome_page
                        and hasattr(gnome_page, "current_colors")
                    ):
                        # Rule A: Switch active -> Extract custom text value from GnomeOptions memory map
                        custom_hex = gnome_page.current_colors.get(
                            advanced_key, ""
                        ).strip()
                        if custom_hex and custom_hex != "INHERIT":
                            master_color_payload[advanced_key] = custom_hex
                            continue

                    # Rule B: Switch inactive -> Dynamically force synchronization with current primary color
                    master_color_payload[advanced_key] = master_color_payload.get(
                        "primary", "#246cc5"
                    )

                # Push the cleanly processed configuration payload to your canvas renderer
                home_page.interactive_preview.update_colors(master_color_payload)
        # --- B. HANDLE ADVANCED COLOR PICKER DIALOG CLICKS ---
        elif action_type == "CLICKED_ADVANCED_PICKER":
            p = payload
            # Call your manager function directly, unpacking the exact expected arguments
            cls.manager.on_advanced_picker_clicked(
                p["gesture"], p["n_press"], p["x"], p["y"], p["entry_row"]
            )

        # --- C. HANDLE QUICK PALETTE PICKER DIALOG CLICKS ---
        elif action_type == "CLICKED_QUICK_PICKER":
            p = payload
            cls.manager.on_quick_picker_clicked(
                p["gesture"], p["n_press"], p["x"], p["y"], p["entry_row"]
            )
        elif action_type == "ANOTHER_FEATURE_EVENT":
            # Add infinite cross-page interaction loops here!
            pass
