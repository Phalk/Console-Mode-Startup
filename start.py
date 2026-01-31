import subprocess
import sys
import os
import configparser
import time
import shlex
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QImageReader, QMovie

def get_exe_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.realpath(sys.executable))
    else:
        return os.path.dirname(os.path.abspath(__file__))

log_file = os.path.join(get_exe_dir(), 'startup_mode_log.txt')
def log_message(message):
    try:
        with open(log_file, 'a') as f:
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

# --- LÓGICA DE INICIALIZAÇÃO ---
app = QApplication(sys.argv)
script_dir = get_exe_dir()
config_path = os.path.join(script_dir, 'config.ini')

temp_win = QWidget()
temp_win.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
temp_win.show()
resolution = get_current_screen_resolution(temp_win)
temp_win.close()

config = configparser.ConfigParser()
config.read(config_path)

section = resolution if resolution in config else 'default'
apps_to_launch = []
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
        # Padronização: Remove aspas se o usuário as colocou no INI para o path do GIF
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
    show_percentage_ini = True if show_flag == 1 else False

    app_keys = sorted([k for k in config[section].keys() if k.isdigit()], key=int)
    for k in app_keys:
        val = config[section].get(k)
        if val: apps_to_launch.append(val)

total_wait_time = sum(float(e.split(',wait=')[1]) for e in apps_to_launch if ',wait=' in e)

splash = None
if total_wait_time > 0:
    splash = SplashScreen(anim_path_ini, loading_text_ini, show_percentage_ini, use_loop_ini, bgcolor_ini, textcolor_ini)
    splash.show()

elapsed_time = 0
for app_entry in apps_to_launch:
    # shlex.split lida corretamente com aspas no comando do executável
    if ',wait=' in app_entry:
        cmd_part, wait_val = app_entry.rsplit(',wait=', 1)
        try: wait_seconds = float(wait_val)
        except: wait_seconds = 0
    else:
        cmd_part = app_entry
        wait_seconds = 0

    try:
        parts = shlex.split(cmd_part)
        subprocess.Popen(parts, shell=False)
    except Exception as e:
        log_message(f"Erro ao abrir {cmd_part}: {e}")

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
if splash: splash.close()
app.quit()
sys.exit(0)
