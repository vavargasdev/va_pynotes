import html
import os
from functools import partial

import wx
import wx.lib.buttons as wxbt
import wx.lib.scrolledpanel as scrolled
from PIL import Image, ImageGrab
from wx.lib.expando import EVT_ETC_LAYOUT_NEEDED, ExpandoTextCtrl

from constants import (
    IMAGE_DIR,
    THUMB_DIR,
    THUMB_SIZE,
)
from utils import sanitize_text


class RightPanel(scrolled.ScrolledPanel):
    """
    The right, scrollable panel that displays the note cards.
    """

    def __init__(self, parent, app_state, save_categories_callback):
        """Constructor"""
        scrolled.ScrolledPanel.__init__(self, parent, -1, style=wx.VSCROLL)
        self.app_state = app_state
        self.focused_card_id = 0
        self.attached_images = {}
        self.save_categories_callback = save_categories_callback

        self.SetBackgroundColour(self.app_state.config["UICOLORS"]["gr-0"])

        # Main sizer for the right panel
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        self.card = {}

        self.SetupScrolling()
        self.SetAutoLayout(1)
        self.Show()

    def text_change(self, evt):
        """Called when an ExpandoTextCtrl needs a layout update."""
        # Let the parent layout its children first.
        evt.GetEventObject().GetParent().Layout()
        # Postpone the scrollbar adjustment until after this event is done.
        wx.CallAfter(self.FitInside)

    def ScrollChildIntoView(self, child):
        """Override to prevent automatic scrolling on focus."""
        pass

    def on_mouse_wheel(self, evt):
        """Pass mouse wheel events to the parent for scrolling."""
        self.GetEventHandler().ProcessEvent(evt)
        evt.Skip()

    def on_copy(self, evt):
        """Copy the card's main text to the clipboard."""
        btn_id = evt.GetId()
        card_id = btn_id - 1000
        card_children = self.card[card_id].GetChildren()
        text_to_copy = card_children[1].GetValue()

        data_obj = wx.TextDataObject()
        data_obj.SetText(text_to_copy)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data_obj)
            wx.TheClipboard.Close()
            print(f"Card {card_id} text copied.")
        else:
            wx.MessageBox("Error copying to clipboard.")
        evt.Skip()

    def on_delete(self, evt):
        """Delete a card from the UI and the database."""
        self.focused_card_id = 0

        btn_id = evt.GetId()
        card_id = btn_id - 2000

        if self.card[card_id]:
            self.card[card_id].DestroyLater()

        # Delete from DB
        self.app_state.cursor.execute(
            "DELETE FROM notas WHERE codigo_id = ?", (card_id,)
        )
        self.app_state.conn.commit()
        print(f"Removed card {card_id}")

        self.main_sizer.Layout()
        wx.CallAfter(self.FitInside)
        evt.Skip()

    def on_paste_image(self, item_title, evt):
        """Paste an image from the clipboard and attach it to the card."""
        btn_id = evt.GetId()
        item_id = btn_id - 7000

        image_count = len(self.attached_images.get(item_id, [])) + 1

        # Filenames
        attachment_filename = (
            str(item_id)
            + "_"
            + str(image_count)
            + "_"
            + sanitize_text(item_title)
            + ".jpg"
        )
        thumb_path = os.path.join(THUMB_DIR, attachment_filename)
        image_path = os.path.join(IMAGE_DIR, attachment_filename)

        # Grab image from clipboard
        clipboard_image = ImageGrab.grabclipboard()

        if isinstance(clipboard_image, Image.Image):
            # Convert image to RGB if it has an alpha channel (e.g., RGBA)
            # as JPEG format does not support transparency.
            if clipboard_image.mode in ("RGBA", "P"):
                clipboard_image = clipboard_image.convert("RGB")

            # Save full image
            clipboard_image.save(image_path, "JPEG")
            print("Image saved successfully!")

            # Save thumbnail
            thumb_image = clipboard_image.copy()
            thumb_image.thumbnail(THUMB_SIZE)
            thumb_image.save(thumb_path, "JPEG")

            # Update internal list
            self.attached_images.setdefault(item_id, []).append(attachment_filename)
            print(self.attached_images[item_id])

            # Update DB
            image_list_str = ",".join(self.attached_images[item_id])
            sql = "UPDATE notas SET imagens = ? WHERE codigo_id = ?"
            self.app_state.cursor.execute(sql, (image_list_str, item_id))

            # Add thumbnail to UI
            attachments_panel = self.FindWindowById(item_id + 8000)
            if attachments_panel:
                attachments_sizer = attachments_panel.GetSizer()
                if attachments_sizer:
                    image_bitmap = wx.Bitmap(thumb_path, wx.BITMAP_TYPE_JPEG)
                    image_control = wx.StaticBitmap(
                        attachments_panel, wx.ID_ANY, image_bitmap
                    )

                    # Bind click to open full image
                    image_control.Bind(
                        wx.EVT_LEFT_DOWN,
                        lambda event, path=image_path: self.on_image_click(event, path),
                    )
                    # Bind right-click to delete
                    image_control.Bind(
                        wx.EVT_CONTEXT_MENU,
                        lambda event, img_ctrl=image_control, panel=attachments_panel, filename=attachment_filename: self.on_image_right_click(
                            event, img_ctrl, panel, filename
                        ),
                    )

                    attachments_sizer.Add(
                        image_control, flag=wx.EXPAND | wx.ALL, border=6
                    )

                    attachments_panel.Layout()

        else:
            print("No image found on clipboard.")

        self.main_sizer.Layout()
        wx.CallAfter(self.FitInside)
        evt.Skip()

    def on_image_click(self, event, image_path):
        """Handler to open the original image in the default system viewer."""
        if os.path.exists(image_path):
            os.startfile(image_path)
        else:
            wx.MessageBox("Image file not found!", "Error", wx.ICON_ERROR)

    def on_image_right_click(self, event, img_ctrl, attachments_panel, filename):
        """Show a context menu to delete an image."""
        menu = wx.Menu()
        delete_item = menu.Append(wx.ID_ANY, "Delete image")

        self.Bind(
            wx.EVT_MENU,
            lambda evt: self.on_delete_image(img_ctrl, attachments_panel, filename),
            delete_item,
        )

        self.PopupMenu(menu)
        menu.Destroy()

    def on_delete_image(self, img_ctrl, attachments_panel, filename):
        """Deletes an attached image from the UI, filesystem, and DB."""
        attachments_sizer = attachments_panel.GetSizer()
        item_id = attachments_panel.GetId() - 8000

        # Remove from UI
        attachments_sizer.Detach(img_ctrl)
        img_ctrl.Hide()
        img_ctrl.Destroy()
        attachments_panel.Layout()

        # Remove from internal list
        if (
            item_id in self.attached_images
            and filename in self.attached_images[item_id]
        ):
            self.attached_images[item_id].remove(filename)

        # Update DB
        image_list_str = ",".join(self.attached_images.get(item_id, []))
        sql = "UPDATE notas SET imagens = ? WHERE codigo_id = ?"
        self.app_state.cursor.execute(sql, (image_list_str, item_id))

        # TODO: Delete files from filesystem

        self.main_sizer.Layout()
        wx.CallAfter(self.FitInside)

    def on_blur_lang(self, evt):
        """Handler for when the category combo box loses focus."""
        item_id = evt.GetId() - 3000
        self.handle_focus_change(item_id)
        evt.Skip()

    def on_blur_tit(self, evt):
        """Handler for when the title text control loses focus."""
        item_id = evt.GetId() - 4000
        self.handle_focus_change(item_id)
        evt.Skip()

    def on_blur_texto(self, evt):
        """Handler for when the main text control loses focus."""
        item_id = evt.GetId() - 5000
        self.handle_focus_change(item_id)
        evt.Skip()

    def handle_focus_change(self, previous_item_id):
        """
        Determines which card is losing/gaining focus and saves the
        card that lost focus.
        """
        focused_widget = self.FindFocus()
        current_focus_id = focused_widget.GetId() if focused_widget else 0

        if current_focus_id > 5000:
            self.focused_card_id = current_focus_id - 5000
        elif current_focus_id > 4000:
            self.focused_card_id = current_focus_id - 4000
        elif current_focus_id > 3000:
            self.focused_card_id = current_focus_id - 3000
        else:
            self.focused_card_id = 0

        if previous_item_id and self.focused_card_id != previous_item_id:
            self.save_card(previous_item_id)

    def save_card(self, item_id):
        """Saves the contents of a specific card to the database."""
        # Returns True if a new category was added, indicating a UI reload is needed.
        if item_id < 1:
            return False

        new_category_added = False
        category_key, title, text = "", "", ""

        try:
            card_panel = self.card.get(item_id)
            if not card_panel:
                return False

            category_combo = wx.FindWindowById(item_id + 3000, card_panel)
            if category_combo:
                # GetValue() can be a user-typed value or a selection
                category_label = category_combo.GetValue()

                # Find the key corresponding to the label
                category_key = ""
                found = False
                for key, data in self.app_state.categories.items():
                    if data["label"] == category_label:
                        category_key = key
                        found = True
                        break

                # If not found, it's a new category
                if not found and category_label:
                    category_key = sanitize_text(category_label.lower())

                    # Assign a color
                    used_colors = list(self.app_state.categories.values())
                    all_colors = list(self.app_state.config["CATCOLORS"].keys())

                    # Find the next available color, or cycle through them
                    next_color_index = len(used_colors) % len(all_colors)
                    new_color_key = all_colors[next_color_index]

                    # Update state and save
                    self.app_state.categories[category_key] = {
                        "label": category_label,
                        "color": new_color_key,
                    }
                    self.save_categories_callback()
                    new_category_added = True
                    print(
                        f"New category '{category_label}' added with color '{new_color_key}'"
                    )

            title_ctrl = wx.FindWindowById(item_id + 4000, card_panel)
            if title_ctrl:
                title = title_ctrl.GetValue()

            text_ctrl = wx.FindWindowById(item_id + 5000, card_panel)
            if text_ctrl:
                text = text_ctrl.GetValue()
        except Exception as e:
            print(f"Error reading card data for saving: {e}")
            pass

        # SQL
        if category_key and title and text:
            sql = (
                "UPDATE notas SET categ = ?, titulo = ?, texto = ? WHERE codigo_id = ?"
            )
            self.app_state.cursor.execute(sql, (category_key, title, text, item_id))
        elif title and text:
            sql = "UPDATE notas SET titulo = ?, texto = ? WHERE codigo_id = ?"
            self.app_state.cursor.execute(sql, (title, text, item_id))
        else:
            print(f"Card {item_id} not saved (empty).")
            return new_category_added

        self.app_state.conn.commit()
        print(f"Saved card {item_id}")
        return new_category_added

    def create_card_item(
        self, item_id, item_category, item_title, item_text, item_images
    ):
        """Factory method to create a single note card widget."""
        # Fallback for category
        try:
            color_key = self.app_state.categories[item_category]["color"]
        except KeyError:
            item_category = "none"
            color_key = self.app_state.categories.get("none", {}).get(
                "color", "cor_001"
            )

        # Colors - [0] = base, [1] = light, [2] = dark
        card_colors = self.app_state.config["CATCOLORS"][color_key]

        card_panel = wx.Panel(self, id=item_id)
        card_panel.SetBackgroundColour(self.app_state.config["UICOLORS"]["wh-1"])

        header_panel = wx.Panel(card_panel)
        header_panel.SetMinSize((-1, 40))  # Aumenta a altura para acomodar padding
        header_color = card_colors[1]
        header_panel.SetBackgroundColour(header_color)

        # Color indicator square
        color_indicator = wx.Panel(header_panel, size=(20, 20))
        color_indicator.SetBackgroundColour(card_colors[0])
        color_indicator.SetToolTip(self.app_state.categories[item_category]["label"])

        # BT Copy
        img = wx.Image(
            "assets/" + self.app_state.config["UIICONS"]["copy-note"],
            wx.BITMAP_TYPE_PNG,
        )
        img = img.Scale(32, 32, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.Bitmap(img)
        copy_btn = wxbt.GenBitmapButton(
            header_panel,
            item_id + 1000,
            bitmap,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.BORDER_NONE,
        )
        copy_btn.SetToolTip("Copy note text to clipboard")
        card_panel.Bind(wx.EVT_BUTTON, self.on_copy, id=item_id + 1000)

        # BT Delete
        img_del = wx.Image(
            "assets/" + self.app_state.config["UIICONS"]["delete-note"],
            wx.BITMAP_TYPE_PNG,
        )
        img_del = img_del.Scale(32, 32, wx.IMAGE_QUALITY_HIGH)
        bitmap_del = wx.Bitmap(img_del)
        delete_btn = wxbt.GenBitmapButton(
            header_panel,
            item_id + 2000,
            bitmap_del,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.BORDER_NONE,
        )
        delete_btn.SetBackgroundColour(header_color)
        delete_btn.SetToolTip("Delete this note")
        card_panel.Bind(wx.EVT_BUTTON, self.on_delete, id=item_id + 2000)

        # BT Paste
        img_paste = wx.Image(
            "assets/" + self.app_state.config["UIICONS"]["add-image"],
            wx.BITMAP_TYPE_PNG,
        )
        img_paste = img_paste.Scale(32, 32, wx.IMAGE_QUALITY_HIGH)
        bitmap_paste = wx.Bitmap(img_paste)
        paste_btn = wxbt.GenBitmapButton(
            header_panel,
            item_id + 7000,
            bitmap_paste,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.BORDER_NONE,
        )
        paste_btn.SetBackgroundColour(header_color)
        paste_btn.SetToolTip("Paste image from clipboard and attach")
        card_panel.Bind(
            wx.EVT_BUTTON, partial(self.on_paste_image, item_title), id=item_id + 7000
        )

        category_combo = wx.ComboBox(
            header_panel,
            id=item_id + 3000,
            value="",
            choices=[],
            style=wx.CB_SORT | wx.CB_DROPDOWN,
        )
        category_combo.SetBackgroundColour(self.app_state.config["UICOLORS"]["wh-2"])

        # Populate with labels from the categories dictionary
        category_labels = [data["label"] for data in self.app_state.categories.values()]
        category_combo.SetItems(sorted(category_labels))

        # Set the current value
        category_combo.SetValue(self.app_state.categories[item_category]["label"])
        category_combo.SetToolTip("Select or type a category")

        title_ctrl = wx.TextCtrl(
            header_panel, id=item_id + 4000, value=item_title, style=wx.BORDER_NONE
        )
        title_ctrl.SetFont(wx.Font(14, 73, 90, 90, False, wx.EmptyString))
        title_ctrl.SetForegroundColour(self.app_state.config["UICOLORS"]["gr-0"])
        title_ctrl.SetBackgroundColour(header_color)

        card_sizer = wx.BoxSizer(wx.VERTICAL)
        card_panel.SetSizer(card_sizer)

        # Header Sizer with
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        header_panel.SetSizer(header_sizer)

        # Left side: color indicator and title
        header_sizer.Add(
            color_indicator, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=4
        )
        header_sizer.Add(
            title_ctrl, proportion=1, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=8
        )

        # Right side: combo box and buttons
        header_sizer.Add(
            category_combo, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8
        )
        header_sizer.Add(copy_btn, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=4)
        header_sizer.Add(delete_btn, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=4)
        header_sizer.Add(paste_btn, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)

        card_sizer.Add(header_panel, flag=wx.EXPAND | wx.ALL, border=0)

        # --- Content Wrapper for Text and Attachments (to apply padding) ---
        content_wrapper = wx.Panel(card_panel)
        # content_wrapper.SetBackgroundColour(self.app_state.config["UICOLORS"]["wh-1"])
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        content_wrapper.SetSizer(content_sizer)

        # Main text block (added to the content_sizer)
        item_text = html.unescape(item_text)
        text_block = ExpandoTextCtrl(content_wrapper, id=item_id + 5000, style=wx.BORDER_NONE)
        text_block.SetFont(
            wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False, "Consolas")
        )
        text_block.SetForegroundColour(self.app_state.config["UICOLORS"]["gr-0"])
        # text_block.SetBackgroundColour(self.app_state.config["UICOLORS"]["wh-1"])

        # Set the value AFTER unbinding the event to prevent recursion on initial layout
        text_block.Unbind(EVT_ETC_LAYOUT_NEEDED)
        text_block.SetValue(item_text)
        text_block.Bind(EVT_ETC_LAYOUT_NEEDED, self.text_change)

        # Use proportion=0 and wx.EXPAND to avoid recursion error
        content_sizer.Add(text_block, 1, wx.EXPAND)

        # Attached images
        self.attached_images[item_id] = []
        attachments_sizer = wx.BoxSizer(wx.HORIZONTAL)
        attachments_panel = wx.Panel(content_wrapper, id=item_id + 8000)
        # attachments_panel.SetBackgroundColour(self.app_state.config["UICOLORS"]["wh-1"])
        attachments_panel.SetSizer(attachments_sizer)

        if item_images:
            attachments = [x.strip() for x in item_images.split(",")]
            self.attached_images[item_id] = attachments
            for i, attachment_filename in enumerate(attachments):
                thumb_path = os.path.join(THUMB_DIR, attachment_filename)
                image_path = os.path.join(IMAGE_DIR, attachment_filename)
                image_bitmap = wx.Bitmap(thumb_path, wx.BITMAP_TYPE_JPEG)
                image_control = wx.StaticBitmap(
                    attachments_panel, wx.ID_ANY, image_bitmap
                )

                image_control.Bind(
                    wx.EVT_LEFT_DOWN,
                    lambda event, path=image_path: self.on_image_click(event, path),
                )
                image_control.Bind(
                    wx.EVT_CONTEXT_MENU,
                    lambda event, ctrl=image_control, panel=attachments_panel, filename=attachment_filename: self.on_image_right_click(
                        event, ctrl, panel, filename
                    ),
                )
                attachments_sizer.Add(image_control, flag=wx.LEFT, border=8)

        # Add attachments panel to the content sizer
        content_sizer.Add(attachments_panel, 0, wx.EXPAND | wx.TOP, 6)

        card_sizer.Add(content_wrapper, 1, wx.EXPAND | wx.ALL, 8)

        # Bind events
        card_panel.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        text_block.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        category_combo.Bind(wx.EVT_KILL_FOCUS, self.on_blur_lang)
        title_ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_blur_tit)
        text_block.Bind(wx.EVT_KILL_FOCUS, self.on_blur_texto)

        return card_panel
