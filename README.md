# Console Mode Startup

This Python script uses PyQt5 to automatically launch applications based on the resolution of the screen where it is executed. It reads a configuration file (`config.ini`) to determine which applications to launch for a specific screen resolution (e.g., `1920x1080`). If the detected resolution is not listed in `config.ini`, it falls back to a default `[other]` section. The script runs without user interaction, launching applications immediately upon execution.

## Features
- Detects the screen resolution (e.g., `1920x1080`) using PyQt5's `QApplication.screenAt()`.
- Reads application paths from `config.ini` based on the detected screen resolution or the `[other]` section as a fallback.
- Logs execution details to `startup_mode_log.txt` for debugging.
- Executes applications asynchronously using `subprocess.Popen` and terminates immediately after launching.
- No user interface or input required; applications start automatically.

## Prerequisites
- Python 3.6 or higher
- PyQt5 (`pip install PyQt5`)
- PyInstaller (for converting to .exe, `pip install pyinstaller`)
- Windows operating system (for application path compatibility)

## Installation
1. Clone or download the script to your local machine.
2. Install the required Python packages:
   ```bash
   pip install PyQt5 pyinstaller
   ```
3. Create a `config.ini` file in the same directory as the script with the following structure:
   ```ini
   [1920x1080]
   0=explorer.exe

   [2560x1440]
   0=C:\Playnite\Playnite.FullscreenApp.exe

   [other]
   0=notepad.exe
   ```
   - Replace the paths with the actual applications you want to launch for each screen resolution.
   - The `[other]` section is used for any resolution not explicitly listed.
   - Ensure keys (e.g., `0`, `1`) are numeric and sequential for proper sorting.

## Converting to Executable
To convert the script to a single executable file (`.exe`) without a console window, use PyInstaller with the following command:
```bash
pyinstaller --noconsole --onedir startup_mode.py
```
- `--noconsole`: Prevents the console window from appearing when running the .exe.
- `--onefile`: Packages the script and its dependencies into a single executable file.
- The output executable will be located in the `dist` folder.

**Note**: Ensure `config.ini` is placed in the same directory as the generated `.exe` for it to work correctly.

## Replacing the Windows Shell
To replace the default Windows shell (explorer.exe) with this script, follow these steps to modify the registry:

1. Log in to a Windows user account with administrative privileges (different from the target user).
2. Open `regedit.exe`.
3. Go to the **File** menu and select **Load Hive**.
4. Navigate to the target user's profile directory (e.g., `C:\Users\myUser\`).
5. Select the `ntuser.dat` file and load it, giving it a temporary name (e.g., `TempHive`).
6. Navigate to the following registry path:
   ```
   HKEY_USERS\TempHive\Software\Microsoft\Windows NT\CurrentVersion\Winlogon
   ```
7. Create a new **String Value** named `Shell`.
8. Set its value to the full path of the generated `.exe` (e.g., `C:\path\to\startup_mode.exe`).
9. Go to the **File** menu and select **Unload Hive** to save changes.
10. Log out and log back in as the target user to apply the new shell.

The script will now run automatically when the user logs in, replacing the default Windows shell.

## Usage
1. Ensure `config.ini` is properly configured with application paths for each screen resolution and an `[other]` section for unrecognized resolutions.
2. Run the script (or the generated `.exe`).
3. The script:
   - Detects the resolution of the screen where it is executed (e.g., `1920x1080`).
   - Loads the applications listed in the corresponding `[resolution]` section of `config.ini` or the `[other]` section if the resolution is not found.
   - Launches the applications asynchronously and terminates immediately.
4. Execution details are logged to `startup_mode_log.txt` in the same directory for debugging purposes.

## Functionality
The script provides a streamlined way to launch applications based on the screen resolution:
- **Resolution-Based Execution**: Automatically detects the screen resolution and launches the applications listed in the matching `config.ini` section (e.g., `[1920x1080]`).
- **Fallback Mechanism**: If the resolution is not listed, it uses the `[other]` section to launch default applications.
- **Use Case**: Ideal for multi-monitor setups where different screens have distinct resolutions, allowing customized application launches (e.g., a gaming frontend on one screen, standard desktop on another).

## Troubleshooting
- **Error: `config.ini` not found or invalid**: Ensure `config.ini` exists in the same directory as the script or `.exe` and is properly formatted.
- **Applications not launching**: Verify that the paths in `config.ini` are correct and that the applications are accessible.
- **Resolution not detected**: Check `startup_mode_log.txt` to confirm the detected resolution and ensure it matches a section in `config.ini` or that `[other]` is defined.
- **Registry modification issues**: Ensure you have administrative privileges and are loading the correct `ntuser.dat` file for the target user.
- Check `startup_mode_log.txt` for detailed error messages and execution logs.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
