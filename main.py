# -*- coding: utf-8 -*-
"""
VaVar PyNotes - Aquart Dev
A desktop application to store and manage notes 
and code snippets using a SQLite database.
author: Vagner Vargas
website: dev.aquart.com.br
last edited: Out 2025
"""
import wx
from app_state import AppState
from ui.main_frame import MainFrame


def main():
    """Main function to run the application."""
    AppState.initialize_database()
    app = wx.App()
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
