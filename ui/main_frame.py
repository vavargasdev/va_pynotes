import wx
import wx.adv
import json

from app_state import AppState
from constants import (
    ID_ABOUT,
    ID_CLEAR_ALL,
    ID_CLEAR_TAGS,
    ID_EXIT,
    ID_INSERT,
    ID_SEARCH,
    ID_SPLITTER,
    ID_UPDATE,
    LEFT_PANEL_WIDTH,
    WINDOW_DIMS,
)
from ui.left_panel import LeftPanel
from ui.right_panel import RightPanel


class MainFrame(wx.Frame):
    """The main application frame."""

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.app_state = AppState()
        self.app_state.load_config()
        self.load_categories()

        self.SetIcon(wx.Icon("assets/PyNotes-Ico.png"))
        self.init_ui()
        self.bind_events()

        # Initial data load
        self.on_update(None)

    def load_categories(self):
        """Loads categories from JSON or creates it from config."""
        try:
            with open("data/categories.json", "r") as f:
                self.app_state.categories = json.load(f)
            print("Categories loaded from categories.json")
        except (FileNotFoundError, json.JSONDecodeError):
            print("categories.json not found. Migrating from database...")
            self.app_state.categories = {}

            # Fetch existing distinct categories from the database
            self.app_state.cursor.execute(
                "SELECT DISTINCT categ FROM notas WHERE categ IS NOT NULL AND categ != ''"
            )
            existing_categories = self.app_state.cursor.fetchall()

            all_colors = list(self.app_state.config["CATCOLORS"].keys())
            color_count = len(all_colors)

            for i, row in enumerate(existing_categories):
                cat_key = row[0]
                if cat_key:
                    # Assign color cyclically
                    color_key = all_colors[i % color_count]
                    # Create a simple label from the key
                    label = cat_key.replace("_", " ").capitalize()
                    self.app_state.categories[cat_key] = {
                        "label": label,
                        "color": color_key,
                    }

            # Add a default "uncategorized" category if it doesn't exist
            if "none" not in self.app_state.categories:
                self.app_state.categories["none"] = {
                    "label": "None",
                    "color": "cor_001",
                }

            self.save_categories()

    def save_categories(self):
        """Saves the current categories map to categories.json."""
        with open("data/categories.json", "w") as f:
            json.dump(self.app_state.categories, f, indent=2)
        print("categories.json saved.")

    def init_ui(self):
        """Initializes the main user interface components."""
        self.splitter = wx.SplitterWindow(self, ID_SPLITTER, style=wx.SP_THIN_SASH)
        self.splitter.SetMinimumPaneSize(100)
        self.splitter.SetSashInvisible()

        # Panels
        self.left_panel = LeftPanel(
            self.splitter, self.app_state, on_update_callback=self.on_update
        )
        self.right_panel = RightPanel(
            self.splitter, self.app_state, self.save_categories
        )
        self.splitter.SplitVertically(self.left_panel, self.right_panel)
        self.splitter.SetSashPosition(LEFT_PANEL_WIDTH)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.splitter, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.SetBackgroundColour(self.app_state.config["UICOLORS"]["gr-2"])

        # Set window size, ensuring it fits on the screen
        screen_size_x, screen_size_y = wx.GetDisplaySize()
        win_w = min(WINDOW_DIMS["w"], screen_size_x * 0.95)
        win_h = min(WINDOW_DIMS["h"], screen_size_y * 0.95)
        self.SetSize(win_w, win_h)

        self.SetTitle("VaPyNotes")
        self.Center()

    def bind_events(self):
        """Binds all application-level events."""
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_SPLITTER_DCLICK, self.on_double_click, id=ID_SPLITTER)
        self.Bind(wx.EVT_BUTTON, self.on_add_item, id=ID_INSERT)
        self.Bind(wx.EVT_BUTTON, self.on_exit, id=ID_EXIT)
        self.Bind(wx.EVT_BUTTON, self.on_update, id=ID_UPDATE)
        self.Bind(wx.EVT_BUTTON, self.on_clear_and_update, id=ID_CLEAR_ALL)
        self.Bind(wx.EVT_BUTTON, self.on_clear_tags, id=ID_CLEAR_TAGS)
        self.Bind(wx.EVT_BUTTON, self.on_about_app, id=ID_ABOUT)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_update, id=ID_SEARCH)

    def on_update(self, evt):
        """Refreshes the list of notes based on current filters."""
        self.Freeze()
        print("Freezing UI and updating list...")

        # Save any pending changes from the focused card
        needs_reload = self.right_panel.save_card(self.right_panel.focused_card_id)

        if needs_reload:
            # A new category was added, we need to reload the UI completely
            self.reload_ui()

        # Clear the right panel
        self.right_panel.main_sizer.Clear(True)

        # Get search term
        search_term = self.left_panel.search_ctrl.GetValue()

        # Get selected tags
        selected_categories = []
        children = self.left_panel.tags_grid_sizer.GetChildren()
        for child in children:
            widget = child.GetWindow()
            if widget.GetValue():
                tag_id = widget.GetId()
                selected_categories.append(self.app_state.tag_id_map[tag_id])

        # Build the main SQL query
        sql = "SELECT * FROM notas "
        where_clauses = []
        params = []

        if search_term:
            where_clauses.append("(titulo LIKE ? OR texto LIKE ?)")
            params.extend([f"%{search_term}%", f"%{search_term}%"])

        if selected_categories:
            # Create a placeholder for each category: (?, ?, ?)
            placeholders = ", ".join("?" for _ in selected_categories)
            where_clauses.append(f"categ IN ({placeholders})")
            params.extend(selected_categories)

        if where_clauses:
            sql += "WHERE " + " AND ".join(where_clauses)

        sql += f" ORDER BY codigo_id DESC LIMIT {self.app_state.max_items}"

        self.app_state.cursor.execute(sql, params)

        # Rebuild the right panel
        self.right_panel.card = {}
        total_items = 0
        for row in self.app_state.cursor.fetchall():
            if row[0]:  # Ensure there's an ID
                total_items += 1
                self.right_panel.card[row[0]] = self.right_panel.create_card_item(
                    row[0], row[1], row[2], row[3], row[4]
                )
                self.right_panel.main_sizer.Add(
                    self.right_panel.card[row[0]],
                    flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                    border=4,
                )

        # Adjust layout and scrolling
        self.right_panel.main_sizer.Layout()
        self.right_panel.FitInside()
        self.right_panel.SetupScrolling()

        self.Thaw()
        self.right_panel.SetFocus()
        print("List updated.")

        # Update item counter
        self.left_panel.total_items_text.SetLabel(str(total_items))

    def on_add_item(self, evt):
        """Adds a new, empty note to the database and refreshes the list."""
        self.app_state.cursor.execute("SELECT MAX(codigo_id) FROM notas")
        last_id = self.app_state.cursor.fetchone()[0] or 0
        new_id = last_id + 1

        title = self.left_panel.search_ctrl.GetValue() or "New Title"

        self.app_state.cursor.execute(
            "INSERT INTO notas (codigo_id, categ, titulo, texto) VALUES (?, ?, ?, ?)",
            (new_id, self.app_state.current_tag, title, "New text here."),
        )
        print(f"Added new item with ID {new_id}")

        self.on_update(None)

        # Scroll to the new item
        if new_id in self.right_panel.card:
            self.right_panel.ScrollChildIntoView(self.right_panel.card[new_id])

    def on_clear_and_update(self, evt):
        """Clears search and tags, then updates the list."""
        self.left_panel.search_ctrl.SetValue("")
        self.left_panel.reset_category_buttons()
        self.on_update(None)

    def on_clear_tags(self, evt):
        """Clears all selected category tags and updates the list."""
        self.left_panel.reset_category_buttons()
        self.on_update(None)

    def on_about_app(self, evt):
        """Displays the About dialog."""
        description = """VaVar PyNotes - Aquart Dev
A system developed by Vagner Vargas to archive
notes for easy retrieval and use across
various categories.
"""
        licence = """VaVar PyNotes is MIT licensed."""
        info = wx.adv.AboutDialogInfo()
        info.SetIcon(wx.Icon("assets/PyNotes-Ico.png", wx.BITMAP_TYPE_PNG))
        info.SetName("VaVar PyNotes")
        info.SetVersion("0.1")
        info.SetDescription(description)
        info.SetCopyright("(C) 2025 Vagner Vargas")
        info.SetWebSite("http://dev.aquart.com.br")
        info.SetLicence(licence)
        info.AddDeveloper("Vagner Vargas")
        wx.adv.AboutBox(info)

    def on_exit(self, evt):
        """Closes the application."""
        self.Close(True)

    def on_close(self, evt):
        """Handles the window close event, ensuring the DB is closed."""
        self.app_state.close_db()
        self.Destroy()

    def on_double_click(self, evt):
        """Resets the splitter position on double-click."""
        self.splitter.SetSashPosition(LEFT_PANEL_WIDTH)

    def reload_ui(self):
        """Destroys and recreates the UI panels to reflect new categories."""
        self.Freeze()
        sash_pos = self.splitter.GetSashPosition()

        self.left_panel.Destroy()
        self.right_panel.Destroy()

        self.left_panel = LeftPanel(
            self.splitter, self.app_state, on_update_callback=self.on_update
        )
        self.right_panel = RightPanel(
            self.splitter, self.app_state, self.save_categories
        )
        self.splitter.SplitVertically(self.left_panel, self.right_panel)
        self.splitter.SetSashPosition(sash_pos)
        self.Thaw()
