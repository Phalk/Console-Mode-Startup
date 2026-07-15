# Console Mode Startup

This Python script uses PyQt5 to automatically launch applications based on the screen resolution. It features a fully customizable "Loading" interface (GIFs, text, and colors) that synchronizes animation progress with the wait times defined for each application.
This is specially useful for people with multiseat solutions (ex: Ibik Aster).

## Features
- **Resolution-Based Launching**: Automatically detects screen resolution and runs specific apps from `config.ini`.
- **Visual Customization**: Define background color (`bgcolor`), text color (`textcolor`), and loading text per resolution.
- **Animation Modes**: Sync a GIF frame-by-frame with progress or run it in an infinite loop using the `,loop` flag.

## Prerequisites
- Python 3.10 or higher
- PyQt5 (`pip install PyQt5`)
- PyInstaller (`pip install pyinstaller`)

## Configuration (config.ini)
The `config.ini` file must be placed in the same directory as the executable.

```ini
[1920x1080]
; Appearance Settings
bgcolor = #000000
textcolor = #ffffff
loading_text = INITIALIZING SYSTEM...
show_percentage = 1
; Animation path (Quotes recommended if there are spaces)
animation = "loading.gif",loop

; Applications (Numeric keys = execution order)
; Always use quotes for paths with spaces!
1 = "C:\Program Files\My App\game.exe",wait=5
2 = "explorer.exe",wait=2

[default]
bgcolor = #1a1a1a
textcolor = #00ff00
loading_text = LOADING DEFAULT PROFILE...
animation = "sync_anim.gif"
show_percentage = 1
1 = notepad.exe,wait=3

```

## Converting to Executable

To generate the executable in a folder format (keeping `config.ini` and assets external for easy editing), use:

```bash
pyinstaller --noconsole --onedir start.py

```

**Note**: After building, manually copy your `config.ini` and animation files (GIFs) into the generated executable folder.

## Replacing the Windows Shell

1. Use the tool provided to change your windows shell (start config.exe)

## License

This project is licensed under the MIT License.
