import os
import sys
import winreg
import configparser
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QTabWidget, QLineEdit, QListWidget, 
                             QColorDialog, QCheckBox, QSpinBox, QMessageBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt

def get_exe_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.realpath(sys.executable))
    else:
        return os.path.dirname(os.path.abspath(__file__))

class ConfiguradorApp(QWidget):
    def __init__(self):
        super().__init__()
        # Garante que busca o config.ini rigidamente na mesma pasta do script
        self.script_dir = get_exe_dir()
        self.config_path = os.path.join(self.script_dir, 'config.ini')
        
        self.config = configparser.ConfigParser()
        self.verificar_e_criar_config_ini()
        
        self.init_ui()

    def verificar_e_criar_config_ini(self):
        """Garante que o arquivo existe na pasta para não quebrar a interface."""
        if not os.path.exists(self.config_path):
            self.config['default'] = {
                'bgcolor': '#000000',
                'loading_text': 'Carregando...',
                'show_percentage': '1',
                'animation': ''
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
        else:
            self.config.read(self.config_path, encoding='utf-8')

    def init_ui(self):
        self.setWindowTitle("Configurador do Sistema de Inicialização")
        self.resize(650, 550)
        self.setStyleSheet("""
            QWidget { background-color: #1e1e24; color: #ffffff; font-family: 'Segoe UI', Arial; font-size: 13px; }
            QLineEdit, QListWidget, QSpinBox { background-color: #2b2b36; border: 1px solid #4f4f64; border-radius: 4px; padding: 5px; color: white; }
            QPushButton { background-color: #007acc; border: none; border-radius: 4px; padding: 8px 15px; color: white; font-weight: bold; }
            QPushButton:hover { background-color: #0098ff; }
            QPushButton#danger { background-color: #d9534f; }
            QPushButton#danger:hover { background-color: #c9302c; }
            QTabBar::tab { background: #2b2b36; padding: 10px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; color: #bbbbbb; }
            QTabBar::tab:selected { background: #007acc; color: white; }
            QGroupBox { border: 1px solid #4f4f64; border-radius: 6px; margin-top: 15px; padding-top: 15px; font-weight: bold; }
        """)

        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Criando e associando as abas CORRETAMENTE com seus respectivos layouts internos
        self.tabs.addTab(self.criar_aba_shell(), "Configuração de Shell")
        self.tabs.addTab(self.criar_aba_ini(), "Editar Inicialização (INI)")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    # ==========================================
    # ABA 1: GERENCIAMENTO DE SHELL (WINREG)
    # ==========================================
    def criar_aba_shell(self):
        aba = QWidget()
        layout = QVBoxLayout(aba) # <--- CORREÇÃO: O layout agora aponta diretamente para a aba pai
        
        info_label = QLabel(
            "Aqui você define se o Windows deve iniciar a sua Interface customizada (start.exe)\n"
            "diretamente ao ligar o PC ou manter o Explorer original."
        )
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        group = QGroupBox("Status do Shell Atual")
        group_layout = QFormLayout()
        
        self.lbl_status_shell = QLabel("Carregando...")
        self.lbl_status_shell.setStyleSheet("font-weight: bold; color: #ffcc00;")
        group_layout.addRow("Shell Ativo:", self.lbl_status_shell)
        group.setLayout(group_layout)
        layout.addWidget(group)

        btn_layout = QHBoxLayout()
        btn_alterar = QPushButton("Escolher Executável e Definir como Shell (-c)")
        btn_alterar.clicked.connect(self.acao_alterar_shell)
        
        btn_resetar = QPushButton("Restaurar Explorer Original (-r)")
        btn_resetar.setObjectName("danger")
        btn_resetar.clicked.connect(self.acao_restaurar_shell)

        btn_layout.addWidget(btn_alterar)
        btn_layout.addWidget(btn_resetar)
        layout.addLayout(btn_layout)
        
        layout.addStretch() # Empurra tudo para cima de forma organizada
        
        self.atualizar_status_shell()
        return aba

    def obter_caminho_shell_registro(self):
        caminho_chave = r"Software\Microsoft\Windows NT\CurrentVersion\Winlogon"
        try:
            chave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, caminho_chave, 0, winreg.KEY_READ)
            valor, _ = winreg.QueryValueEx(chave, "Shell")
            winreg.CloseKey(chave)
            return valor
        except FileNotFoundError:
            return "Padrão (explorer.exe)"
        except Exception as e:
            return f"Erro ao ler: {e}"

    def atualizar_status_shell(self):
        status = self.obter_caminho_shell_registro()
        self.lbl_status_shell.setText(status)
        if "explorer.exe" in status.lower() or "padrão" in status:
            self.lbl_status_shell.setStyleSheet("color: #5cb85c; font-weight: bold;")
        else:
            self.lbl_status_shell.setStyleSheet("color: #f0ad4e; font-weight: bold;")

    def acao_alterar_shell(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Selecione o executável do seu Inicializador", self.script_dir, "Executáveis (*.exe);;Todos os arquivos (*.*)")
        if caminho:
            caminho = os.path.normpath(caminho)
            caminho_chave = r"Software\Microsoft\Windows NT\CurrentVersion\Winlogon"
            try:
                chave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, caminho_chave, 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(chave, "Shell", 0, winreg.REG_SZ, caminho)
                winreg.CloseKey(chave)
                QMessageBox.information(self, "Sucesso", f"Shell modificado com sucesso!\nPróximo logon executará:\n{caminho}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao acessar registro (Execute como Admin):\n{e}")
            self.atualizar_status_shell()

    def acao_restaurar_shell(self):
        caminho_chave = r"Software\Microsoft\Windows NT\CurrentVersion\Winlogon"
        try:
            chave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, caminho_chave, 0, winreg.KEY_ALL_ACCESS)
            try:
                winreg.DeleteValue(chave, "Shell")
                QMessageBox.information(self, "Sucesso", "Shell restaurado para o explorer.exe padrão.")
            except FileNotFoundError:
                QMessageBox.information(self, "Info", "O Shell já estava definido como o padrão.")
            winreg.CloseKey(chave)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao acessar registro:\n{e}")
        self.atualizar_status_shell()

    # ==========================================
    # ABA 2: EDITOR DO CONFIG.INI
    # ==========================================
    def criar_aba_ini(self):
        aba = QWidget()
        layout = QVBoxLayout(aba) # <--- CORREÇÃO: O layout agora aponta diretamente para a aba pai

        # Seleção da Seção (Resoluções)
        sec_layout = QHBoxLayout()
        sec_layout.addWidget(QLabel("Resolução/Perfil:"))
        self.combo_secoes = QListWidget()
        self.combo_secoes.setFixedHeight(50)
        self.combo_secoes.itemClicked.connect(self.carregar_dados_secao)
        sec_layout.addWidget(self.combo_secoes)
        layout.addLayout(sec_layout)

        # Configurações Visuais
        vis_group = QGroupBox("Customização do Splash Screen")
        vis_layout = QFormLayout()
        
        self.txt_bgcolor = QLineEdit()
        self.btn_color_bg = QPushButton("Escolher")
        self.btn_color_bg.clicked.connect(lambda: self.abrir_paleta(self.txt_bgcolor))
        bg_h_layout = QHBoxLayout()
        bg_h_layout.addWidget(self.txt_bgcolor)
        bg_h_layout.addWidget(self.btn_color_bg)
        vis_layout.addRow("Cor de Fundo (Hex):", bg_h_layout)

        self.txt_anim = QLineEdit()
        self.btn_buscar_anim = QPushButton("Buscar GIF")
        self.btn_buscar_anim.clicked.connect(self.buscar_gif)
        anim_h_layout = QHBoxLayout()
        anim_h_layout.addWidget(self.txt_anim)
        anim_h_layout.addWidget(self.btn_buscar_anim)
        vis_layout.addRow("Caminho Animação:", anim_h_layout)
        
        self.chk_loop = QCheckBox("Repetir Animação em Loop")
        vis_layout.addRow("", self.chk_loop)

        self.txt_loading = QLineEdit()
        vis_layout.addRow("Texto de Carregamento:", self.txt_loading)
        
        self.chk_percent = QCheckBox("Mostrar Porcentagem")
        vis_layout.addRow("", self.chk_percent)

        vis_group.setLayout(vis_layout)
        layout.addWidget(vis_group)

        # Lista de Programas
        apps_group = QGroupBox("Aplicativos a Executar")
        apps_layout = QVBoxLayout()
        
        self.lista_apps = QListWidget()
        apps_layout.addWidget(self.lista_apps)

        # Adicionar/Remover Apps
        edit_app_layout = QHBoxLayout()
        self.txt_app_cmd = QLineEdit()
        self.txt_app_cmd.setPlaceholderText("Caminho do executável ou comando...")
        self.spin_wait = QSpinBox()
        self.spin_wait.setSuffix("s wait")
        self.spin_wait.setMaximum(300)

        btn_add_app = QPushButton("Adicionar")
        btn_add_app.clicked.connect(self.adicionar_app_lista)
        btn_del_app = QPushButton("Remover")
        btn_del_app.setObjectName("danger")
        btn_del_app.clicked.connect(self.remover_app_lista)

        edit_app_layout.addWidget(self.txt_app_cmd, 4)
        edit_app_layout.addWidget(self.spin_wait, 1)
        edit_app_layout.addWidget(btn_add_app, 1)
        edit_app_layout.addWidget(btn_del_app, 1)
        
        apps_layout.addLayout(edit_app_layout)
        apps_group.setLayout(apps_layout)
        layout.addWidget(apps_group)

        # Botão Geral de Salvar
        btn_salvar_ini = QPushButton("Salvar Configurações no config.ini")
        btn_salvar_ini.setStyleSheet("background-color: #5cb85c; font-size: 14px; padding: 10px;")
        btn_salvar_ini.clicked.connect(self.salvar_config_ini)
        layout.addWidget(btn_salvar_ini)

        self.atualizar_secoes_ini()
        return aba

    def atualizar_secoes_ini(self):
        self.combo_secoes.clear()
        for secao in self.config.sections():
            self.combo_secoes.addItem(secao)
        if self.config.sections():
            self.combo_secoes.setCurrentRow(0)
            self.carregar_dados_secao(self.combo_secoes.currentItem())

    def carregar_dados_secao(self, item):
        if not item: return
        secao = item.text()
        
        self.txt_bgcolor.setText(self.config[secao].get('bgcolor', fallback="#000000"))
        self.txt_loading.setText(self.config[secao].get('loading_text', fallback=""))
        self.chk_percent.setChecked(self.config[secao].getint('show_percentage', fallback=1) == 1)
        
        anim_entry = self.config[secao].get('animation', fallback="")
        if ',loop' in anim_entry:
            self.txt_anim.setText(anim_entry.split(',loop')[0].replace('"', '').strip())
            self.chk_loop.setChecked(True)
        else:
            self.txt_anim.setText(anim_entry.replace('"', '').strip())
            self.chk_loop.setChecked(False)

        self.lista_apps.clear()
        app_keys = sorted([k for k in self.config[secao].keys() if k.isdigit()], key=int)
        for k in app_keys:
            self.lista_apps.addItem(self.config[secao].get(k))

    def abrir_paleta(self, campo):
        cor = QColorDialog.getColor()
        if cor.isValid():
            campo.setText(cor.name())

    def buscar_gif(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Selecione o GIF de Animação", self.script_dir, "Imagens (*.gif *.png *.jpg)")
        if caminho:
            if caminho.startswith(self.script_dir):
                caminho = os.path.relpath(caminho, self.script_dir)
            self.txt_anim.setText(caminho)

    def adicionar_app_lista(self):
        cmd = self.txt_app_cmd.text().strip()
        if not cmd: return
        
        wait = self.spin_wait.value()
        entry = f'"{cmd}"' if not cmd.startswith('"') and " " in cmd else cmd
        if wait > 0:
            entry += f",wait={wait}"
            
        self.lista_apps.addItem(entry)
        self.txt_app_cmd.clear()
        self.spin_wait.setValue(0)

    def remover_app_lista(self):
        item = self.lista_apps.currentItem()
        if item:
            self.lista_apps.takeItem(self.lista_apps.row(item))

    def salvar_config_ini(self):
        item = self.combo_secoes.currentItem()
        if not item: return
        secao = item.text()

        self.config[secao]['bgcolor'] = self.txt_bgcolor.text()
        self.config[secao]['loading_text'] = self.txt_loading.text()
        self.config[secao]['show_percentage'] = "1" if self.chk_percent.isChecked() else "0"
        
        anim = self.txt_anim.text().strip()
        if anim:
            self.config[secao]['animation'] = f'"{anim}",loop' if self.chk_loop.isChecked() else f'"{anim}"'
        else:
            self.config[secao]['animation'] = ""

        chaves_para_remover = [k for k in self.config[secao].keys() if k.isdigit()]
        for k in chaves_para_remover:
            self.config.remove_option(secao, k)

        for i in range(self.lista_apps.count()):
            self.config[secao][str(i)] = self.lista_apps.item(i).text()

        try:
            with open(self.config_path, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            QMessageBox.information(self, "Salvo", "Configurações gravadas com sucesso no config.ini!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao escrever no arquivo:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfiguradorApp()
    window.show()
    sys.exit(app.exec_())