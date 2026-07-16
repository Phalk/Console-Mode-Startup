import os
import sys
import winreg
import configparser
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QTabWidget, QLineEdit, QListWidget, 
                             QColorDialog, QCheckBox, QSpinBox, QMessageBox, QGroupBox, QFormLayout, QComboBox)
from PyQt5.QtCore import Qt

def get_exe_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.realpath(sys.executable))
    else:
        return os.path.dirname(os.path.abspath(__file__))

class ConfiguratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.script_dir = get_exe_dir()
        self.config_path = os.path.join(self.script_dir, 'config.ini')
        
        self.config = configparser.ConfigParser()
        self.verify_and_create_config_ini()
        
        self.init_ui()

    def verify_and_create_config_ini(self):
        """Ensures the config.ini file exists to prevent UI crashes."""
        if not os.path.exists(self.config_path):
            self.config['default'] = {
                'bgcolor': '#000000',
                'loading_text': 'Loading...',
                'show_percentage': '1',
                'animation': '',
                '1': 'example_app'
            }
            self.config['example_app'] = {
                'path': 'notepad.exe',
                'wait': '2'
            }
            self.save_to_disk()
        else:
            self.config.read(self.config_path, encoding='utf-8')

    def save_to_disk(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save config.ini:\n{e}")

    def init_ui(self):
        self.setWindowTitle("Startup System Configurator")
        self.resize(700, 600)
        self.setStyleSheet("""
            QWidget { background-color: #1e1e24; color: #ffffff; font-family: 'Segoe UI', Arial; font-size: 13px; }
            QLineEdit, QListWidget, QSpinBox, QComboBox { background-color: #2b2b36; border: 1px solid #4f4f64; border-radius: 4px; padding: 5px; color: white; }
            QPushButton { background-color: #007acc; border: none; border-radius: 4px; padding: 8px 15px; color: white; font-weight: bold; }
            QPushButton:hover { background-color: #0098ff; }
            QPushButton#danger { background-color: #d9534f; }
            QPushButton#danger:hover { background-color: #c9302c; }
            QPushButton#neutral { background-color: #4f4f64; }
            QPushButton#neutral:hover { background-color: #6a6a85; }
            QTabBar::tab { background: #2b2b36; padding: 10px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; color: #bbbbbb; }
            QTabBar::tab:selected { background: #007acc; color: white; }
            QGroupBox { border: 1px solid #4f4f64; border-radius: 6px; margin-top: 15px; padding-top: 15px; font-weight: bold; }
        """)

        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Adding the three functional tabs
        self.tabs.addTab(self.create_shell_tab(), "Shell Configuration")
        self.tabs.addTab(self.create_ini_tab(), "Edit Sequence & Resolution")
        self.tabs.addTab(self.create_apps_tab(), "Register/Edit Applications")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    # ==========================================
    # TAB 1: SHELL MANAGEMENT (WINREG)
    # ==========================================
    def create_shell_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info_label = QLabel(
            "Configure whether Windows should launch your custom startup interface (start.exe)\n"
            "directly upon booting the PC or keep the default Windows Explorer."
        )
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        group = QGroupBox("Current Shell Status")
        group_layout = QFormLayout()
        
        self.lbl_shell_status = QLabel("Loading...")
        self.lbl_shell_status.setStyleSheet("font-weight: bold; color: #ffcc00;")
        group_layout.addRow("Active Shell:", self.lbl_shell_status)
        group.setLayout(group_layout)
        layout.addWidget(group)

        btn_layout = QHBoxLayout()
        btn_change = QPushButton("Select Executable and Set as Shell (-c)")
        btn_change.clicked.connect(self.action_change_shell)
        
        btn_reset = QPushButton("Restore Original Explorer (-r)")
        btn_reset.setObjectName("danger")
        btn_reset.clicked.connect(self.action_restore_shell)

        btn_layout.addWidget(btn_change)
        btn_layout.addWidget(btn_reset)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        self.update_shell_status()
        return tab

    def get_registry_shell_path(self):
        key_path = r"Software\Microsoft\Windows NT\CurrentVersion\Winlogon"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "Shell")
            winreg.CloseKey(key)
            return value
        except FileNotFoundError:
            return "Default (explorer.exe)"
        except Exception as e:
            return f"Error reading registry: {e}"

    def update_shell_status(self):
        status = self.get_registry_shell_path()
        self.lbl_shell_status.setText(status)
        if "explorer.exe" in status.lower() or "default" in status.lower():
            self.lbl_shell_status.setStyleSheet("color: #5cb85c; font-weight: bold;")
        else:
            self.lbl_shell_status.setStyleSheet("color: #f0ad4e; font-weight: bold;")

    def action_change_shell(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select your custom Startup Executable", self.script_dir, "Executables (*.exe);;All Files (*.*)")
        if path:
            path = os.path.normpath(path)
            key_path = r"Software\Microsoft\Windows NT\CurrentVersion\Winlogon"
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(key, "Shell", 0, winreg.REG_SZ, path)
                winreg.CloseKey(key)
                QMessageBox.information(self, "Success", f"Shell successfully updated!\nNext logon will execute:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to access registry (Try running as Admin):\n{e}")
            self.update_shell_status()

    def action_restore_shell(self):
        key_path = r"Software\Microsoft\Windows NT\CurrentVersion\Winlogon"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            try:
                winreg.DeleteValue(key, "Shell")
                QMessageBox.information(self, "Success", "Shell restored to default explorer.exe.")
            except FileNotFoundError:
                QMessageBox.information(self, "Info", "The Shell is already set to default.")
            winreg.CloseKey(key)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to access registry:\n{e}")
        self.update_shell_status()

    # ==========================================
    # TAB 2: SEQUENCE & RESOLUTION EDITOR
    # ==========================================
    def create_ini_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Resolution / Profile Selection
        sec_layout = QHBoxLayout()
        sec_layout.addWidget(QLabel("Resolution / Profile:"))
        self.list_sections = QListWidget()
        self.list_sections.setFixedHeight(60)
        self.list_sections.itemClicked.connect(self.load_section_data)
        sec_layout.addWidget(self.list_sections)
        
        # Profile Management Buttons
        btn_sec_layout = QVBoxLayout()
        btn_add_sec = QPushButton("Add Profile")
        btn_add_sec.clicked.connect(self.add_profile_section)
        btn_del_sec = QPushButton("Remove Profile")
        btn_del_sec.setObjectName("danger")
        btn_del_sec.clicked.connect(self.remove_profile_section)
        btn_sec_layout.addWidget(btn_add_sec)
        btn_sec_layout.addWidget(btn_del_sec)
        sec_layout.addLayout(btn_sec_layout)
        
        layout.addLayout(sec_layout)

        # Visual Customization Options
        vis_group = QGroupBox("Splash Screen Customization")
        vis_layout = QFormLayout()
        
        self.txt_bgcolor = QLineEdit()
        self.btn_color_bg = QPushButton("Pick Color")
        self.btn_color_bg.clicked.connect(lambda: self.open_color_picker(self.txt_bgcolor))
        bg_h_layout = QHBoxLayout()
        bg_h_layout.addWidget(self.txt_bgcolor)
        bg_h_layout.addWidget(self.btn_color_bg)
        vis_layout.addRow("Background Color (Hex):", bg_h_layout)

        self.txt_anim = QLineEdit()
        self.btn_search_anim = QPushButton("Browse GIF")
        self.btn_search_anim.clicked.connect(self.search_gif)
        anim_h_layout = QHBoxLayout()
        anim_h_layout.addWidget(self.txt_anim)
        anim_h_layout.addWidget(self.btn_search_anim)
        vis_layout.addRow("Animation Path:", anim_h_layout)
        
        self.chk_loop = QCheckBox("Repeat Animation in Loop")
        vis_layout.addRow("", self.chk_loop)

        self.txt_loading = QLineEdit()
        vis_layout.addRow("Loading Text:", self.txt_loading)
        
        self.chk_percent = QCheckBox("Show Percentage Progress")
        vis_layout.addRow("", self.chk_percent)

        vis_group.setLayout(vis_layout)
        layout.addWidget(vis_group)

        # Execution Sequencing
        seq_group = QGroupBox("Application Execution Order")
        seq_layout = QHBoxLayout()
        
        self.list_apps_seq = QListWidget()
        seq_layout.addWidget(self.list_apps_seq, 4)

        # Reordering Buttons (Up / Down)
        order_btn_layout = QVBoxLayout()
        self.btn_move_up = QPushButton("▲")
        self.btn_move_up.setObjectName("neutral")
        self.btn_move_up.clicked.connect(lambda: self.move_sequence_item(-1))
        
        self.btn_move_down = QPushButton("▼")
        self.btn_move_down.setObjectName("neutral")
        self.btn_move_down.clicked.connect(lambda: self.move_sequence_item(1))
        
        order_btn_layout.addWidget(self.btn_move_up)
        order_btn_layout.addWidget(self.btn_move_down)
        order_btn_layout.addStretch()
        seq_layout.addLayout(order_btn_layout, 1)

        seq_group.setLayout(seq_layout)
        layout.addWidget(seq_group)

        # Adding Registered Apps to Sequence
        add_seq_layout = QHBoxLayout()
        add_seq_layout.addWidget(QLabel("Add App to Order:"))
        self.combo_available_apps = QComboBox()
        add_seq_layout.addWidget(self.combo_available_apps, 3)
        
        btn_add_to_seq = QPushButton("Add to Sequence")
        btn_add_to_seq.clicked.connect(self.add_app_to_sequence)
        btn_del_from_seq = QPushButton("Remove from Sequence")
        btn_del_from_seq.setObjectName("danger")
        btn_del_from_seq.clicked.connect(self.remove_app_from_sequence)
        
        add_seq_layout.addWidget(btn_add_to_seq, 1)
        add_seq_layout.addWidget(btn_del_from_seq, 1)
        layout.addLayout(add_seq_layout)

        # Global Section Save
        btn_save_ini = QPushButton("Save Settings to config.ini")
        btn_save_ini.setStyleSheet("background-color: #5cb85c; font-size: 14px; padding: 10px;")
        btn_save_ini.clicked.connect(self.save_section_ini)
        layout.addWidget(btn_save_ini)

        self.update_sections_ui()
        return tab

    # ==========================================
    # TAB 3: INDEPENDENT APP REGISTRY
    # ==========================================
    def create_apps_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("Manage your registered applications and their global execution variables:"))

        # Registered App List
        self.list_registered_apps = QListWidget()
        self.list_registered_apps.setFixedHeight(150)
        self.list_registered_apps.itemClicked.connect(self.load_app_data_for_editing)
        layout.addWidget(self.list_registered_apps)

        # Detailed Form
        app_form_group = QGroupBox("Application Parameters")
        app_form_layout = QFormLayout()

        self.txt_app_id = QLineEdit()
        self.txt_app_id.setPlaceholderText("Ex: my_game_launcher (no spaces)")
        app_form_layout.addRow("Unique Identifier ([name]):", self.txt_app_id)

        self.txt_app_path = QLineEdit()
        self.txt_app_path.setPlaceholderText("Absolute path to executable or global command...")
        self.btn_browse_app_exe = QPushButton("Browse Executable")
        self.btn_browse_app_exe.clicked.connect(self.browse_app_executable)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.txt_app_path)
        path_layout.addWidget(self.btn_browse_app_exe)
        app_form_layout.addRow("Executable Path (path):", path_layout)

        self.txt_app_runat = QLineEdit()
        self.txt_app_runat.setPlaceholderText("Working directory / startup folder (Optional)")
        app_form_layout.addRow("Working Directory (runat):", self.txt_app_runat)

        self.spin_app_wait = QSpinBox()
        self.spin_app_wait.setSuffix(" seconds")
        self.spin_app_wait.setMaximum(300)
        app_form_layout.addRow("Wait Time (wait):", self.spin_app_wait)

        app_form_group.setLayout(app_form_layout)
        layout.addWidget(app_form_group)

        # Database / Save Operations
        btn_action_layout = QHBoxLayout()
        btn_save_app = QPushButton("Save / Register Application")
        btn_save_app.clicked.connect(self.save_or_update_app)
        
        btn_delete_app = QPushButton("Delete Application Registry")
        btn_delete_app.setObjectName("danger")
        btn_delete_app.clicked.connect(self.delete_app_registry)

        btn_action_layout.addWidget(btn_save_app)
        btn_action_layout.addWidget(btn_delete_app)
        layout.addLayout(btn_action_layout)

        layout.addStretch()
        self.update_registered_apps_list()
        return tab

    # ==========================================
    # INTERNAL LOGIC & CONTROLLER LOGIC
    # ==========================================

    def get_resolution_sections(self):
        """Retrieves only sections that are screen resolutions or 'default'."""
        resolutions = []
        for s in self.config.sections():
            if s == 'default' or 'x' in s or s.replace('x', '').isdigit():
                # Avoid picking up app-specific declared sections
                if 'path' not in self.config[s]:
                    resolutions.append(s)
        return resolutions

    def get_app_sections(self):
        """Retrieves only sections dedicated to actual registered applications."""
        apps = []
        for s in self.config.sections():
            if 'path' in self.config[s]:
                apps.append(s)
        return apps

    def update_sections_ui(self):
        self.list_sections.clear()
        for section in self.get_resolution_sections():
            self.list_sections.addItem(section)
        
        if self.list_sections.count() > 0:
            self.list_sections.setCurrentRow(0)
            self.load_section_data(self.list_sections.currentItem())
            
        self.update_sequencer_app_combobox()

    def update_sequencer_app_combobox(self):
        self.combo_available_apps.clear()
        self.combo_available_apps.addItems(self.get_app_sections())

    def update_registered_apps_list(self):
        self.list_registered_apps.clear()
        for app_name in self.get_app_sections():
            self.list_registered_apps.addItem(app_name)

    def load_section_data(self, item):
        if not item: return
        section = item.text()
        
        self.txt_bgcolor.setText(self.config[section].get('bgcolor', fallback="#000000"))
        self.txt_loading.setText(self.config[section].get('loading_text', fallback=""))
        self.chk_percent.setChecked(self.config[section].getint('show_percentage', fallback=1) == 1)
        
        anim_entry = self.config[section].get('animation', fallback="")
        if ',loop' in anim_entry:
            self.txt_anim.setText(anim_entry.split(',loop')[0].replace('"', '').strip())
            self.chk_loop.setChecked(True)
        else:
            self.txt_anim.setText(anim_entry.replace('"', '').strip())
            self.chk_loop.setChecked(False)

        self.list_apps_seq.clear()
        app_keys = sorted([k for k in self.config[section].keys() if k.isdigit()], key=int)
        for k in app_keys:
            self.list_apps_seq.addItem(self.config[section].get(k))

    def open_color_picker(self, field):
        color = QColorDialog.getColor()
        if color.isValid():
            field.setText(color.name())

    def search_gif(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Animation GIF", self.script_dir, "Images (*.gif *.png *.jpg)")
        if path:
            if path.startswith(self.script_dir):
                path = os.path.relpath(path, self.script_dir)
            self.txt_anim.setText(path)

    def move_sequence_item(self, direction):
        current_row = self.list_apps_seq.currentRow()
        if current_row == -1: return

        new_row = current_row + direction
        if 0 <= new_row < self.list_apps_seq.count():
            current_item = self.list_apps_seq.takeItem(current_row)
            self.list_apps_seq.insertItem(new_row, current_item)
            self.list_apps_seq.setCurrentRow(new_row)

    def add_app_to_sequence(self):
        selected_app = self.combo_available_apps.currentText()
        if selected_app:
            self.list_apps_seq.addItem(selected_app)

    def remove_app_from_sequence(self):
        item = self.list_apps_seq.currentItem()
        if item:
            self.list_apps_seq.takeItem(self.list_apps_seq.row(item))

    def add_profile_section(self):
        from PyQt5.QtWidgets import QInputDialog
        res, ok = QInputDialog.getText(self, "New Profile", "Enter the Resolution or Profile Name (Ex: 1920x1080):")
        if ok and res.strip():
            new_section = res.strip()
            if new_section not in self.config:
                self.config[new_section] = {
                    'bgcolor': '#000000',
                    'loading_text': 'Starting...',
                    'show_percentage': '1'
                }
                self.save_to_disk()
                self.update_sections_ui()

    def remove_profile_section(self):
        item = self.list_sections.currentItem()
        if not item: return
        section = item.text()
        
        if section == 'default':
            QMessageBox.warning(self, "Warning", "The 'default' profile cannot be deleted.")
            return

        confirm = QMessageBox.question(self, "Confirmation", f"Are you sure you want to delete the profile '{section}'?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.config.remove_section(section)
            self.save_to_disk()
            self.update_sections_ui()

    def save_section_ini(self):
        item = self.list_sections.currentItem()
        if not item: return
        section = item.text()

        self.config[section]['bgcolor'] = self.txt_bgcolor.text()
        self.config[section]['loading_text'] = self.txt_loading.text()
        self.config[section]['show_percentage'] = "1" if self.chk_percent.isChecked() else "0"
        
        anim = self.txt_anim.text().strip()
        if anim:
            self.config[section]['animation'] = f'"{anim}",loop' if self.chk_loop.isChecked() else f'"{anim}"'
        else:
            self.config[section]['animation'] = ""

        # Remove old sequencing options
        keys_to_remove = [k for k in self.config[section].keys() if k.isdigit()]
        for k in keys_to_remove:
            self.config.remove_option(section, k)

        # Regrate with newly ordered sequencing UI lines
        for i in range(self.list_apps_seq.count()):
            self.config[section][str(i + 1)] = self.list_apps_seq.item(i).text()

        self.save_to_disk()
        QMessageBox.information(self, "Success", f"Profile [{section}] saved successfully!")

    # --- APP REGISTRY INTERACTIONS ---

    def browse_app_executable(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Executable", self.script_dir, "Executables (*.exe);;All Files (*.*)")
        if path:
            self.txt_app_path.setText(path)
            # Auto fill working directory if empty
            if not self.txt_app_runat.text().strip():
                self.txt_app_runat.setText(os.path.dirname(path))

    def load_app_data_for_editing(self, item):
        if not item: return
        app_name = item.text()
        
        self.txt_app_id.setText(app_name)
        self.txt_app_path.setText(self.config[app_name].get('path', fallback="").strip('"').strip("'"))
        self.txt_app_runat.setText(self.config[app_name].get('runat', fallback="").strip('"').strip("'"))
        
        try:
            wait_val = int(self.config[app_name].get('wait', fallback=0))
        except ValueError:
            wait_val = 0
        self.spin_app_wait.setValue(wait_val)

    def save_or_update_app(self):
        app_id = self.txt_app_id.text().strip().replace(' ', '_')
        path = self.txt_app_path.text().strip()

        if not app_id or not path:
            QMessageBox.warning(self, "Error", "Application Identifier and Path cannot be empty!")
            return

        if app_id not in self.config:
            self.config.add_section(app_id)

        self.config[app_id]['path'] = f'"{path}"' if " " in path and not path.startswith('"') else path
        
        runat = self.txt_app_runat.text().strip()
        if runat:
            self.config[app_id]['runat'] = f'"{runat}"' if " " in runat and not runat.startswith('"') else runat
        else:
            if 'runat' in self.config[app_id]:
                self.config.remove_option(app_id, 'runat')

        wait = self.spin_app_wait.value()
        if wait > 0:
            self.config[app_id]['wait'] = str(wait)
        else:
            if 'wait' in self.config[app_id]:
                self.config.remove_option(app_id, 'wait')

        self.save_to_disk()
        QMessageBox.information(self, "Success", f"Application [{app_id}] registered successfully!")
        
        # Clear fields and update combos
        self.txt_app_id.clear()
        self.txt_app_path.clear()
        self.txt_app_runat.clear()
        self.spin_app_wait.setValue(0)
        
        self.update_registered_apps_list()
        self.update_sequencer_app_combobox()

    def delete_app_registry(self):
        item = self.list_registered_apps.currentItem()
        if not item: return
        app_name = item.text()

        confirm = QMessageBox.question(self, "Confirmation", f"This will remove '{app_name}' from your registry and all associated boot sequences. Proceed?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.config.remove_section(app_name)
            
            # Clean sequences referencing the deleted application
            for section in self.get_resolution_sections():
                keys_to_remove = []
                for k, v in self.config[section].items():
                    if v == app_name:
                        keys_to_remove.append(k)
                for k in keys_to_remove:
                    self.config.remove_option(section, k)
            
            self.save_to_disk()
            self.update_registered_apps_list()
            self.update_sections_ui()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfiguratorApp()
    window.show()
    sys.exit(app.exec_())