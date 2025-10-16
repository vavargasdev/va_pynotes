import wx
import wx.lib.buttons as wxbt

from constants import (
    ID_ABOUT,
    ID_CLEAR_ALL,
    ID_CLEAR_TAGS,
    ID_EXIT,
    ID_INSERT,
    ID_SEARCH,
    ID_TAG_START,
    ID_UPDATE,
    PADDING,
    DEFAULT_FONT,
)


class LeftPanel(wx.Panel):
    """
    The left panel of the application, containing controls like
    search, category filters, and action buttons.
    """

    def __init__(self, parent, app_state, on_update_callback=None):
        super().__init__(parent)
        self.app_state = app_state
        self.on_update_callback = on_update_callback

        self.init_ui()

    def init_ui(self):
        # Main sizer for the left panel
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        # Add Note button with icon
        img = wx.Image(
            "assets/" + self.app_state.config["UIICONS"]["add-note"], wx.BITMAP_TYPE_PNG
        )
        img = img.Scale(32, 32, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.Bitmap(img)

        self.add_button = wxbt.GenBitmapTextButton(
            self,
            ID_INSERT,
            bitmap,
            "  Add Note",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.BORDER_NONE,
        )

        self.add_button.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.add_button.SetMinSize(wx.Size(-1, 60))
        self.add_button.SetBackgroundColour(self.app_state.config["UICOLORS"]["co-0"])
        self.add_button.SetFont(
            wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD, False, DEFAULT_FONT)
        )

        self.add_button.Bind(wx.EVT_ENTER_WINDOW, self.on_add_button_hover)
        self.add_button.Bind(wx.EVT_LEAVE_WINDOW, self.on_add_button_leave)

        self.add_button.SetForegroundColour(self.app_state.config["UICOLORS"]["wh-1"])
        self.main_sizer.Add(
            self.add_button, flag=wx.EXPAND | wx.ALL | wx.ALIGN_TOP, border=0
        )

        # Search field
        self.search_wrapper = wx.Panel(self)
        self.search_wrapper.SetBackgroundColour(
            self.app_state.config["UICOLORS"]["wh-2"]
        )
        self.search_wrapper.SetMinSize(wx.Size(-1, 45))  # altura mínima opcional

        self.search_ctrl = wx.TextCtrl(
            self.search_wrapper, ID_SEARCH, style=wx.TE_PROCESS_ENTER | wx.BORDER_NONE
        )
        self.search_ctrl.SetFont(
            wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, DEFAULT_FONT)
        )
        self.search_ctrl.SetHint("Search [Enter]")
        self.search_ctrl.SetBackgroundColour(self.app_state.config["UICOLORS"]["wh-2"])
        self.search_ctrl.SetForegroundColour(self.app_state.config["UICOLORS"]["gr-0"])

        search_sizer = wx.BoxSizer(wx.VERTICAL)
        search_sizer.Add(self.search_ctrl, 1, wx.EXPAND | wx.ALL, 8)  # padding interno
        self.search_wrapper.SetSizer(search_sizer)
        self.main_sizer.Add(
            self.search_wrapper,
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=PADDING - 1,
        )

        # Grid for category buttons
        self.tags_grid_sizer = wx.GridSizer(1, 3, 4, 2)  # rows, cols, vgap, hgap

        self.tag_buttons = {}
        grid_row = 1
        grid_col = 1
        tag_id = ID_TAG_START

        self.color_tag_normal_bg = self.app_state.config["UICOLORS"]["gr-3"]
        self.color_tag_normal_fg = self.app_state.config["UICOLORS"]["co-1"]
        self.color_tag_active_bg = self.app_state.config["UICOLORS"]["co-0"]
        self.color_tag_active_fg = self.app_state.config["UICOLORS"]["gr-3"]

        self.app_state.tag_id_map = {}

        custom_font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, DEFAULT_FONT)

        # Iterate over the new categories structure
        for key, cat_data in self.app_state.categories.items():
            if grid_col > 3:
                grid_col = 1
                grid_row += 1
                self.tags_grid_sizer.SetRows(grid_row)

            self.app_state.tag_id_map[tag_id] = key
            btn = wx.ToggleButton(self, tag_id, cat_data["label"][:10], style=wx.BORDER_NONE)
            btn.SetBackgroundColour(self.color_tag_normal_bg)
            btn.SetForegroundColour(self.color_tag_normal_fg)
            btn.SetMinSize(wx.Size(-1, 40))
            btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            btn.SetFont(custom_font)

            # Bind para alternar as cores ao selecionar/deselecionar
            def make_toggle_handler(b):
                def handler(evt):
                    if b.GetValue():
                        b.SetBackgroundColour(self.color_tag_active_bg)
                        b.SetForegroundColour(self.color_tag_active_fg)
                    else:
                        b.SetBackgroundColour(self.color_tag_normal_bg)
                        b.SetForegroundColour(self.color_tag_normal_fg)
                    b.Refresh()

                    # Force immediate UI update for the button before the list refresh
                    wx.Yield()

                    self.on_change_tag(evt)  # Mantém a lógica de tag atual
                    if self.on_update_callback:
                        self.on_update_callback(None)  # Dispara a atualização da lista

                return handler

            btn.Bind(wx.EVT_TOGGLEBUTTON, make_toggle_handler(btn))

            self.tag_buttons[key] = btn
            self.tags_grid_sizer.Add(
                btn,
                flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
                border=2,
            )
            tag_id += 1
            grid_col += 1

        # Adiciona a grid direto ao main_sizer
        self.main_sizer.Add(
            self.tags_grid_sizer, flag=wx.EXPAND | wx.ALL, border=PADDING - 4
        )

        # Total items count
        self.total_items_text = wx.StaticText(
            self, label="0", style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE
        )
        self.total_items_text.SetFont(
            wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD, False, DEFAULT_FONT)
        )
        self.total_items_text.SetForegroundColour(
            self.app_state.config["UICOLORS"]["gr-0"]
        )
        self.main_sizer.Add(
            self.total_items_text, flag=wx.EXPAND | wx.ALL, border=PADDING
        )

        # Action Buttons
        action_buttons_panel = wx.Panel(self)

        action_sizer = wx.BoxSizer(wx.VERTICAL)

        self.update_button = self.create_action_button(
            ID_UPDATE, "Update List", parent=action_buttons_panel
        )
        action_sizer.Add(self.update_button, 0, wx.TOP | wx.EXPAND, PADDING)

        self.clear_button = self.create_action_button(
            ID_CLEAR_ALL, "Reset", parent=action_buttons_panel
        )
        action_sizer.Add(self.clear_button, 0, wx.TOP | wx.EXPAND, PADDING)

        self.clear_tags_button = self.create_action_button(
            ID_CLEAR_TAGS, "Clear Tags", parent=action_buttons_panel
        )
        action_sizer.Add(self.clear_tags_button, 0, wx.TOP | wx.EXPAND, PADDING)

        self.about_button = self.create_action_button(
            ID_ABOUT, "About this App", parent=action_buttons_panel
        )
        action_sizer.Add(self.about_button, 0, wx.TOP | wx.EXPAND, PADDING)

        self.exit_button = self.create_action_button(
            ID_EXIT, "Exit Application", parent=action_buttons_panel
        )
        action_sizer.Add(self.exit_button, 0, wx.TOP | wx.EXPAND, PADDING)

        action_buttons_panel.SetSizer(action_sizer)

        self.main_sizer.Add(
            action_buttons_panel, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=PADDING
        )

    def reset_category_buttons(self):
        """Resets all category toggle buttons to their deselected state."""
        for button in self.tag_buttons.values():
            if button.GetValue():
                button.SetValue(False)
                button.SetBackgroundColour(self.color_tag_normal_bg)
                button.SetForegroundColour(self.color_tag_normal_fg)
                button.Refresh()

    def on_add_button_hover(self, event):
        self.add_button.SetBackgroundColour(self.app_state.config["UICOLORS"]["dt-1"])
        self.add_button.Refresh()
        event.Skip()

    def on_add_button_leave(self, event):
        self.add_button.SetBackgroundColour(self.app_state.config["UICOLORS"]["co-0"])
        self.add_button.Refresh()
        event.Skip()

    def on_button_hover(self, event):
        btn = event.GetEventObject()
        btn.SetForegroundColour(self.app_state.config["UICOLORS"]["gr-3"])
        btn.SetBackgroundColour(self.app_state.config["UICOLORS"]["co-0"])
        btn.Refresh()
        event.Skip()

    def on_button_leave(self, event):
        btn = event.GetEventObject()
        btn.SetForegroundColour(self.app_state.config["UICOLORS"]["co-0"])
        btn.SetBackgroundColour(self.app_state.config["UICOLORS"]["gr-3"])
        btn.Refresh()
        event.Skip()

    def on_change_tag(self, evt):
        """Sets the current tag based on the button pressed."""
        tag_id = evt.GetEventObject().GetId()
        self.app_state.current_tag = self.app_state.tag_id_map[tag_id]

    def create_action_button(self, btn_id, btn_label, parent=None):
        if parent is None:
            parent = self
        button = wx.Button(
            parent,
            btn_id,
            btn_label,
            wx.DefaultPosition,
            wx.DefaultSize,
            0 | wx.BORDER_NONE,
        )
        button.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, DEFAULT_FONT))
        button.SetForegroundColour(self.app_state.config["UICOLORS"]["co-0"])
        button.SetBackgroundColour(self.app_state.config["UICOLORS"]["gr-3"])
        button.SetMinSize(wx.Size(-1, 40))
        button.SetToolTip(btn_label)
        button.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        button.Bind(wx.EVT_ENTER_WINDOW, self.on_button_hover)
        button.Bind(wx.EVT_LEAVE_WINDOW, self.on_button_leave)
        return button
