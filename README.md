# Console Mode Startup

This Python script uses PyQt5 to automatically launch applications based on the screen resolution. It features a fully customizable "Loading" interface (GIFs, text, and colors) that synchronizes animation progress with the wait times defined for each application.

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
; Use ",loop" for infinite animation, or just the filename to sync with progress
animation = loading.gif,loop

; Applications (Numeric keys = execution order)
1 = C:\Path\To\Game.exe,wait=5
2 = explorer.exe,wait=2

[default]
bgcolor = #1a1a1a
textcolor = #00ff00
loading_text = LOADING DEFAULT PROFILE...
animation = sync_anim.gif
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

To replace the default Windows shell (explorer.exe) with this script for a specific user, follow these steps to safely modify the registry:

1. Log in to a Windows user account with **administrative privileges** (different from the target user).
2. Open `regedit.exe`.
3. Go to the **File** menu and select **Load Hive**.
4. Navigate to the target user's profile directory (e.g., `C:\Users\TargetUser\`).
5. Select the `ntuser.dat` file (you may need to enable "Hidden Files") and load it, giving it a temporary name (e.g., `TempHive`).
6. Navigate to the following path:
`HKEY_USERS\TempHive\Software\Microsoft\Windows NT\CurrentVersion\Winlogon`
7. Create a new **String Value** named `Shell`.
8. Set its value to the full path of your generated `.exe` (e.g., `C:\CustomShell\startup_mode.exe`).
9. Go back to the `TempHive` folder in the left sidebar, click the **File** menu, and select **Unload Hive** to save changes.
10. Log out and log back in as the target user to apply the new shell.

## Troubleshooting

* **Failed to load Python DLL**: Ensure you are using the `sys.exit()` method (included in the script) and that your antivirus isn't interfering with the `%TEMP%` folder.
* **GIF Not Playing**: Verify if the filename in `config.ini` matches the file in the folder exactly.
* **Logs**: Detailed execution info and detected resolutions are saved to `startup_mode_log.txt`.

## License

This project is licensed under the MIT License.
