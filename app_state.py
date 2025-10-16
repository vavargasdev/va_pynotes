import sqlite3
from configparser import ConfigParser
import os


class AppState:
    """A class to hold the application's state."""

    def __init__(self):
        self.config = {}
        self.max_items = "8"
        self.current_tag = "text"
        self.tag_id_map = {}

        # Database
        self.conn = sqlite3.connect("data/data_notes.db")
        self.cursor = self.conn.cursor()

    def load_config(self, path="data/config.ini"):
        """Loads configuration from an INI file."""
        config_parser = ConfigParser()
        config_parser.read(path)

        for section_name in config_parser.sections():
            self.config[section_name] = {}
            for key, value in config_parser.items(section_name):
                if "|" in value:
                    self.config[section_name][key] = [item.strip() for item in value.split("|")]
                else:
                    self.config[section_name][key] = value

        self.max_items = self.config["GENERAL"]["limiteres"]

    def close_db(self):
        """Commits changes and closes the database connection."""
        if self.conn:
            self.conn.commit()
            self.conn.close()

    @staticmethod
    def initialize_database():
        """
        Checks for the database directory and file.
        If the file doesn't exist, it creates the DB,
        the 'notas' table, and populates it with initial sample notes.
        """
        db_folder = 'data'
        db_file = os.path.join(db_folder, 'data_notes.db')

        # Create the data directory if it doesn't exist
        if not os.path.exists(db_folder):
            os.makedirs(db_folder)

        # If the database file already exists, do nothing.
        if os.path.exists(db_file):
            return

        try:
            # Connect to the database (this will create the file)
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # 1. Create the 'notas' table
            cursor.execute("""
            CREATE TABLE notas (
                codigo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                categ     TEXT,
                titulo    TEXT,
                texto     TEXT,
                imagens   TEXT,
                data      DATE DEFAULT (DATE('now'))
            );
            """)

            # 2. Define and insert the initial notes
            initial_notes = [
                (
                    'Text',
                    'Edit Notes',
                    'Edit your notes, reminders, or code snippets here. The title and category can also be changed. '
                    'Select an existing category or type a new one in the field. Notes are saved automatically.\n\n'
                    'To find a note, use the search field above and the category buttons to filter. '
                    'The 10 most recent notes for the filter will be displayed.'
                ),
                (
                    'none',
                    'Add New Notes',
                    'To create a new note, click the "Add Note" button on the left. A new blank note will appear on the right. '
                    'Just add a title, category, and your content.'
                )
            ]

            cursor.executemany(
                "INSERT INTO notas (categ, titulo, texto) VALUES (?, ?, ?)",
                initial_notes
            )

            # Commit changes and close the connection
            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            print(f"Database error: {e}")
