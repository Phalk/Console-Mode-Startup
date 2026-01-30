import subprocess
import sys
import os
import configparser
import time
import shlex
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Função para obter o diretório do executável
def get_exe_dir():
    if getattr(sys, 'frozen', False):  # Rodando como .exe (PyInstaller)
        return os.path.dirname(os.path.realpath(sys.executable))
    else:  # Rodando como .py
        return os.path.dirname(os.path.abspath(__file__))

# Configurar log de depuração
log_file = os.path.join(get_exe_dir(), 'startup_mode_log.txt')
def log_message(message):
    try:
        with open(log_file, 'a') as f:
            f.write(f"{time.ctime()}: {message}\n")
    except:
        pass

# Função para obter a resolução da tela atual
def get_current_screen_resolution(window):
    app = QApplication.instance()
    screen = app.screenAt(window.pos())
    if screen:
        resolution = f"{screen.geometry().width()}x{screen.geometry().height()}"
        log_message(f"Janela detectada na resolução: {resolution}")
        return resolution
    return None

# Classe para a splash screen
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")
        
        self.label = QLabel("NOW LOADING...", self)
        self.label.setStyleSheet("color: #FFFFFF; background-color: transparent;")
        self.label.setFont(QFont("Arial", 48))
        self.label.setAlignment(Qt.AlignCenter)
        
        self.percent_label = QLabel("0%", self)
        self.percent_label.setStyleSheet("color: #FFFFFF; background-color: transparent;")
        self.percent_label.setFont(QFont("Century Gothic", 24))
        self.percent_label.setAlignment(Qt.AlignCenter)
        
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.percent_label)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

    def show(self):
        super().show()
        # Ajusta para o tamanho total da tela primária
        screen = QApplication.instance().primaryScreen()
        self.setGeometry(screen.geometry())
        QApplication.instance().processEvents()
        log_message("Splash screen exibida com sucesso.")

    def update_percent(self, percent):
        self.percent_label.setText(f"{int(percent)}%")
        QApplication.instance().processEvents()

# --- INÍCIO DO SCRIPT ---

app = QApplication(sys.argv)
script_dir = get_exe_dir()
config_path = os.path.join(script_dir, 'config.ini')

log_message(f"Iniciando processo. Diretório: {script_dir}")

# Detectar resolução usando uma janela invisível rápida
temp_win = QWidget()
temp_win.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
temp_win.setAttribute(Qt.WA_NoSystemBackground)
temp_win.show()
resolution = get_current_screen_resolution(temp_win)
temp_win.close()

if not resolution:
    log_message("Erro: Não foi possível detectar a resolução.")
    sys.exit(1)

# Carregar Configurações
config = configparser.ConfigParser()
if not config.read(config_path):
    log_message(f"Erro: Arquivo {config_path} não encontrado.")
    sys.exit(1)

section = resolution if resolution in config else 'other'
apps_to_launch = []

if section in config:
    app_keys = sorted([k for k in config[section].keys() if k.isdigit()], key=int)
    for k in app_keys:
        val = config[section].get(k)
        if val:
            apps_to_launch.append(val)

if not apps_to_launch:
    log_message("Nenhum aplicativo para lançar.")
    sys.exit(0)

# Calcular tempo total para decidir se mostra a Splash
total_wait_time = 0
for entry in apps_to_launch:
    if ',wait=' in entry:
        try:
            total_wait_time += float(entry.split(',wait=')[1])
        except ValueError:
            pass

# Instanciar Splash somente se houver tempo de espera
splash = None
if total_wait_time > 0:
    splash = SplashScreen()
    splash.show()

# Execução dos Aplicativos
elapsed_time = 0
for app_entry in apps_to_launch:
    # Parsing de tempo e comando
    if ',wait=' in app_entry:
        cmd_part, wait_val = app_entry.split(',wait=')
        try:
            wait_seconds = float(wait_val)
        except:
            wait_seconds = 0
    else:
        cmd_part = app_entry
        wait_seconds = 0

    # Parsing de argumentos
    try:
        parts = shlex.split(cmd_part)
        exe = parts[0]
        args = parts[1:]
    except:
        exe = cmd_part
        args = []

    # Lançar App
    log_message(f"Lançando: {exe}")
    try:
        subprocess.Popen([exe] + args, shell=False)
    except Exception as e:
        log_message(f"Falha ao abrir {exe}: {e}")

    # Espera com atualização de progresso
    if wait_seconds > 0:
        steps = int(wait_seconds * 10) # 10 atualizações por segundo para fluidez
        for _ in range(steps):
            time.sleep(0.1)
            elapsed_time += 0.1
            if splash:
                percent = min((elapsed_time / total_wait_time) * 100, 100)
                splash.update_percent(percent)
            app.processEvents()

# Finalização Limpa
if splash:
    splash.close()

log_message("Processo concluído. Encerrando de forma limpa.")

# Correção: Usar sys.exit para permitir que o PyInstaller limpe a pasta _MEI
app.quit()
sys.exit(0)
