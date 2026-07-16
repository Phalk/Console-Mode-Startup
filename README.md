# Console Mode Startup

Turns any Windows PC into a game-console-like experience: boots straight into your apps/games — no desktop, no explorer, just "power on and play".

This Python script uses PyQt5 to automatically launch applications based on the screen resolution. It features a fully customizable "Loading" interface (GIFs, text, and colors) that synchronizes animation progress with the wait times defined for each application.

This is especially useful for people with multiseat solutions (ex: Ibik Aster) or custom arcade/HTPC setups.

## Features

- **Resolution-Based Launching**: Automatically detects the active screen resolution and runs specific apps from `config.ini`.
- **Visual Customization**: Define background color (`bgcolor`), text color (`textcolor`), and loading text per resolution.
- **Animation Modes**: Sync a GIF frame-by-frame with progress or run it in an infinite loop using the `,loop` flag.
- **Robust Execution (Fallback)**: Attempts to launch applications directly to avoid console window flickers, with an automatic fallback to system shell execution if needed.
- **Debug & Logging Mode**: Only generates execution and error logs when explicitly started with the `--debug` parameter, keeping your production environment clean.

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
; Animation path (Quotes are stripped automatically; use ',loop' for infinite loop)
animation = "loading.gif",loop

; Applications (Numeric keys = execution order)
; Always use quotes for paths with spaces!
1 = App1
2 = App2

[App1]
path = "C:\Program Files\My App\game.exe"
wait = 5
; Optional: Define execution directory (defaults to application path or script folder)
runat = "C:\Program Files\My App"

[App2]
path = "explorer.exe"
wait = 2

[default]
bgcolor = #1a1a1a
textcolor = #00ff00
loading_text = LOADING DEFAULT PROFILE...
animation = "sync_anim.gif"
show_percentage = 1
1 = Notepad

[Notepad]
path = notepad.exe
wait = 3
```

# Debug and Logging
By default, the script runs silently and does not write any logs. If you need to troubleshoot paths or execution issues, you can enable logging by passing the --debug parameter at startup:

* Running via Python: 
python start.py --debug

* Running the compiled Executable: 
start.exe --debug

When active, it will generate a startup_mode_log.txt file in the application directory containing detailed step-by-step launch events.

# Converting to Executable
To generate the executable in a folder format (keeping config.ini and assets external for easy editing), run:

* pyinstaller --noconsole --onedir start.py

Note: After building, manually copy your config.ini and animation files (GIFs) into the generated dist/start executable folder.

# Replacing the Windows Shell
Use the tool provided to change your Windows shell (start.config).

# License
This project is licensed under the MIT License.
