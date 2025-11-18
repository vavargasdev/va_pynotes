<div align="right">
<a href="./README-pt.md">Ler em português</a>
</div>

# VaPyNotes - A Simple Python Notes Application

VaPyNotes is a desktop application for taking and managing text-based notes, built with Python and the wxPython GUI toolkit.

The main focus is on usability, allowing for quick retrieval and simultaneous viewing of multiple notes organized by categories.

## Features

-   **Simple Note Editing**: A clean interface for writing and editing text notes.
-   **Category-Based Organization**: Assign categories to notes and filter them easily. Categories are color-coded for quick visual identification.
-   **Fast Search**: Quickly find notes by title or content.
-   **Local Storage**: Notes are stored in a local SQLite database file (`data/data_notes.db`). You can easily back up your notes by copying this file.
-   **Clean and Lightweight Interface**: A minimal UI that stays out of your way.
-   **Customizable**: Configure UI colors and the number of notes displayed on the screen via the `data/config.ini` file.

![PyNotes Application Screenshot](https://raw.githubusercontent.com/vavargasdev/va_pynotes/refs/heads/main/PyNotesSS.jpg)

## Status

**Under Development**. Currently tested on Windows only.

## Installation and Usage

### Prerequisites

-   Python 3.x
-   pip (Python package installer)

### Steps

1.  **Clone or download the repository:**
    ```bash
    git clone https://github.com/vavargasdev/va_pynotes.git
    cd va_pynotes
    ```

2.  **Create a Virtual Environment (Recommended):**
    It's good practice to create a virtual environment to manage project dependencies.
    ```bash
    # Create the environment
    python -m venv venv

    # Activate it
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Requirements:**
    Install the necessary Python packages. For now wxpython.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application:**
    You can start the application from the console or by using a batch file.

    -   **From the console:**
        ```bash
        python main.py
        ```

    -   **Using a `.bat` file (on Windows):**
        The repository includes a `run.bat` file. After installing the requirements inside the virtual environment, you can simply double-click this file to start the application.
        ```batch
        @echo off
        .\venv\Scripts\python.exe main.py
        ```

## Future Development (Roadmap)

-   [ ] Results pagination
-   [ ] Advanced sorting options (by date, title, etc.)
-   [ ] A dedicated settings window within the app
-   [ ] Better category and color management tools
-   [ ] Export database to CSV or plain text files
-   [ ] Markdown formatting support for notes
-   [ ] Syntax highlighting for code snippets