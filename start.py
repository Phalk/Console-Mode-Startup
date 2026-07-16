import subprocess
import sys
import os
import configparser
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QImageReader, QMovie



def get_exe_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.realpath(sys.executable))
    else:
        return os.path.dirname(os.path.abspath(__file__))

DEBUG_MODE = "--debug" in sys.argv
log_file = os.path.join(get_exe_dir(), 'startup_mode_log.txt')
def log_message(message):
    if not DEBUG_MODE:
        return
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{time.ctime()}: {message}\n")
    except:
        pass

def get_current_screen_resolution(window):
    app = QApplication.instance()
    screen = app.screenAt(window.pos())
    if screen:
        return f"{screen.geometry().width()}x{screen.geometry().height()}"
    return None

class SplashScreen(QWidget):
    def __init__(self, anim_path=None, custom_text="", show_percent=True, use_loop=False, bg_color="#000000", text_color="#FFFFFF"):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setStyleSheet(f"background-color: {bg_color};")
        self.use_loop = use_loop
        
        layout = QVBoxLayout()
        layout.addStretch()

        self.label = QLabel(custom_text, self)
        self.label.setStyleSheet(f"color: {text_color}; background-color: transparent;")
        self.label.setFont(QFont("Arial", 48))
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.frames = []
        self.movie = None
        self.anim_label = None
        
        if anim_path and os.path.exists(anim_path):
            self.anim_label = QLabel(self)
            self.anim_label.setAlignment(Qt.AlignCenter)
            
            if self.use_loop:
                self.movie = QMovie(anim_path)
                self.anim_label.setMovie(self.movie)
            else:
                reader = QImageReader(anim_path)
                for i in range(reader.imageCount()):
                    self.frames.append(QPixmap.fromImage(reader.read()))
                if self.frames:
                    self.anim_label.setPixmap(self.frames[0])
            
            layout.addWidget(self.anim_label)
        
        self.percent_label = QLabel("0%", self)
        self.percent_label.setStyleSheet(f"color: {text_color}; background-color: transparent;")
        self.percent_label.setFont(QFont("Century Gothic", 24))
        self.percent_label.setAlignment(Qt.AlignCenter)
        self.percent_label.setVisible(show_percent)
        layout.addWidget(self.percent_label)
        
        layout.addStretch()
        self.setLayout(layout)

    def show(self):
        super().show()
        if self.use_loop and self.movie:
            self.movie.start()
        screen = QApplication.instance().primaryScreen()
        self.setGeometry(screen.geometry())
        QApplication.instance().processEvents()

    def update_percent(self, percent):
        if self.percent_label.isVisible():
            self.percent_label.setText(f"{int(percent)}%")
        
        if not self.use_loop and self.frames and self.anim_label:
            frame_index = int((percent / 100) * (len(self.frames) - 1))
            frame_index = max(0, min(frame_index, len(self.frames) - 1))
            self.anim_label.setPixmap(self.frames[frame_index])
            
        QApplication.instance().processEvents()


# --- STARTUP EXECUTION LOGIC ---
app = QApplication(sys.argv)
script_dir = get_exe_dir()
config_path = os.path.join(script_dir, 'config.ini')

temp_win = QWidget()
temp_win.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
temp_win.show()
resolution = get_current_screen_resolution(temp_win)
temp_win.close()

config = configparser.ConfigParser()
config.read(config_path, encoding='utf-8')

section = resolution if resolution in config else 'default'
app_sections_to_launch = []
anim_path_ini = None
use_loop_ini = False
loading_text_ini = ""
show_percentage_ini = True
bgcolor_ini = "#000000"
textcolor_ini = "#FFFFFF"

if section in config:
    bgcolor_ini = config[section].get('bgcolor', fallback="#000000")
    textcolor_ini = config[section].get('textcolor', fallback="#FFFFFF")

    anim_entry = config[section].get('animation', fallback="")
    if anim_entry:
        clean_entry = anim_entry.replace('"', '').replace("'", "")
        if ',loop' in clean_entry:
            anim_path_ini = clean_entry.split(',loop')[0].strip()
            use_loop_ini = True
        else:
            anim_path_ini = clean_entry.strip()
            use_loop_ini = False
        
        if anim_path_ini and not os.path.isabs(anim_path_ini):
            anim_path_ini = os.path.join(script_dir, anim_path_ini)

    loading_text_ini = config[section].get('loading_text', fallback="")
    show_flag = config[section].getint('show_percentage', fallback=1)
    show_percentage_ini = (show_flag == 1)

    # Fetch sequence keys (1, 2, 3...)
    app_keys = sorted([k for k in config[section].keys() if k.isdigit()], key=int)
    for k in app_keys:
        val = config[section].get(k)
        if val: 
            app_sections_to_launch.append(val.strip())

# Sum up total wait time
total_wait_time = 0
for app_name in app_sections_to_launch:
    if app_name in config:
        try:
            wait_val = float(config[app_name].get('wait', fallback=0))
            total_wait_time += wait_val
        except ValueError:
            pass

splash = None
if total_wait_time > 0:
    splash = SplashScreen(anim_path_ini, loading_text_ini, show_percentage_ini, use_loop_ini, bgcolor_ini, textcolor_ini)
    splash.show()

elapsed_time = 0
for app_name in app_sections_to_launch:
    if app_name not in config:
        log_message(f"Section [{app_name}] declared in sequence, but not defined in config.ini.")
        continue

    # Clean up quotes from paths
    raw_path = config[app_name].get('path', fallback="").strip('"').strip("'")
    raw_runat = config[app_name].get('runat', fallback="").strip('"').strip("'")
    
    try:
        wait_seconds = float(config[app_name].get('wait', fallback=0))
    except ValueError:
        wait_seconds = 0

    if not raw_path:
        log_message(f"Section [{app_name}] does not contain a valid 'path'.")
        continue

    # Determine working directory (cwd)
    cwd_dir = None
    if raw_runat:
        cwd_dir = raw_runat
    else:
        path_dir = os.path.dirname(raw_path)
        if path_dir and os.path.exists(path_dir):
            cwd_dir = path_dir
        else:
            cwd_dir = script_dir

    # Launch process with Fallback Strategy
    success = False
    try:
        # First attempt: Direct execution
        subprocess.Popen(raw_path, shell=False, cwd=cwd_dir)
        success = True
        log_message(f"Successfully launched [{app_name}] directly: {raw_path}")
    except Exception as e1:
        log_message(f"Direct launch failed for [{app_name}]: {e1}. Retrying with System Shell...")
        try:
            # Second attempt: System Shell execution (Fallback essential for console hosts like Sunshine)
            subprocess.Popen(raw_path, shell=True, cwd=cwd_dir)
            success = True
            log_message(f"Successfully launched [{app_name}] via System Shell: {raw_path}")
        except Exception as e2:
            log_message(f"CRITICAL: All launch attempts failed for [{app_name}]. Error: {e2}")

    # Wait-time progress tracking
    if wait_seconds > 0:
        steps = int(wait_seconds * 20)
        for _ in range(steps):
            time.sleep(0.05)
            elapsed_time += 0.05
            if splash:
                percent = min((elapsed_time / total_wait_time) * 100, 100)
                splash.update_percent(percent)
            app.processEvents()

time.sleep(1) 
if splash: 
    splash.close()
app.quit()
sys.exit(0)