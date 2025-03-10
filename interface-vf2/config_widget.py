#config_widget.py
import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QToolBox, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QLabel, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal

DEFAULT_CONFIG = {
    "buffer_size": 100,
    "num_motors": 4,
    "enable_gps": True,
    "gps_fix_types": ["2D", "3D", "None"],
    "motor_color": "#ff0000",
    "voltage_drop_range": [0.0, 0.01],
    "altitude_variation": 0.1,
    "motor_current_range": [0.0, 10.0],
    # Telemetry Graphs
    "motor_titles": ["Motor1", "Motor2", "Motor3", "Motor4"],
    "motor_colors": ["#0000ff", "#ffaa7f", "#aa5500", "#ff0000"],
    "motor_update_freq": 200,
    "orientation_titles": ["Roll", "Pitch", "Yaw", "Altitude"],
    "orientation_colors": ["#5500ff", "#55557f", "#ffff7f", "#808080"],
    "orientation_update_freq": 200,
    "battery_title": "Battery Status",
    "battery_color": "#ffaa7f",
    "battery_update_freq": 500,
    # Camera
    "ip_webcam_url": "",
    # Reload/Logging Options
    "default_reload_mode": "Full Reload",
    # Reload Graphs
    "reload_motor_titles": ["Motor 1", "Motor 2", "Motor 3", "Motor 4"],
    "reload_motor_colors": ["#ff0000", "#ff00ff", "#ffaaff", "#ff00ff"],
    "reload_orientation_titles": ["Roll", "Pitch", "Yaw", "Altitude"],
    "reload_orientation_colors": ["#ff0000", "#00ff00", "#0000ff", "#808080"],
    "reload_battery_title": "Battery Status",
    "reload_battery_color": "#ff00ff",
    "reload_battery_update_freq": 500,
    # Global Settings
    "default_gps_fix": "2D",
    "ui_font": "Arial",
    "ui_bg_color": "#ffffff"
}

def load_config(config_file="config.json"):
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
        # Supplement any missing keys with defaults:
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
        return config
    else:
        with open(config_file, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG

class ConfigTab(QWidget):
    configUpdated = pyqtSignal(dict)
    def __init__(self, config_file="config.json", parent=None):
        super().__init__(parent)
        self.config_file = config_file
        self.config = {}
        self.initUI()
        self.load_config()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        self.toolbox = QToolBox(self)

        # --- Telemetry Graphs Configuration Page ---
        telemetry_page = QWidget()
        telemetry_layout = QFormLayout(telemetry_page)
        # Motor Graphs
        self.motor_titles_edit = QLineEdit(self)
        telemetry_layout.addRow("Motor Graph Titles (comma separated):", self.motor_titles_edit)
        self.motor_color_labels = []
        motor_color_layout = QHBoxLayout()
        for i in range(4):
            label = QLabel(self)
            # The text is not displayed on the color box
            label.setStyleSheet(f"background-color: {DEFAULT_CONFIG['motor_colors'][i]}; padding: 5px;")
            label.mousePressEvent = lambda event, idx=i: self.choose_color(event, idx, self.motor_color_labels, "motor")
            self.motor_color_labels.append(label)
            motor_color_layout.addWidget(label)
        telemetry_layout.addRow("Motor Graph Colors:", motor_color_layout)
        self.motor_update_freq_edit = QLineEdit(self)
        telemetry_layout.addRow("Motor Graph Update Frequency (ms):", self.motor_update_freq_edit)

        # Orientation Graphs
        self.orientation_titles_edit = QLineEdit(self)
        telemetry_layout.addRow("Orientation Graph Titles (comma separated):", self.orientation_titles_edit)
        self.orientation_color_labels = []
        orientation_color_layout = QHBoxLayout()
        for i in range(4):
            label = QLabel(self)
            label.setStyleSheet(f"background-color: {DEFAULT_CONFIG['orientation_colors'][i]}; padding: 5px;")
            label.mousePressEvent = lambda event, idx=i: self.choose_color(event, idx, self.orientation_color_labels, "orientation")
            self.orientation_color_labels.append(label)
            orientation_color_layout.addWidget(label)
        telemetry_layout.addRow("Orientation Graph Colors:", orientation_color_layout)
        self.orientation_update_freq_edit = QLineEdit(self)
        telemetry_layout.addRow("Orientation Graph Update Frequency (ms):", self.orientation_update_freq_edit)

        # Battery Graph
        self.battery_title_edit = QLineEdit(self)
        telemetry_layout.addRow("Battery Graph Title:", self.battery_title_edit)
        self.battery_color_label = QLabel(self)
        self.battery_color_label.setStyleSheet(f"background-color: {DEFAULT_CONFIG['battery_color']}; border: 1px solid black; padding: 5px;")
        self.battery_color_label.mousePressEvent = lambda event: self.choose_color(event, 0, [self.battery_color_label], "battery")
        telemetry_layout.addRow("Battery Graph Color:", self.battery_color_label)
        self.battery_update_freq_edit = QLineEdit(self)
        telemetry_layout.addRow("Battery Graph Update Frequency (ms):", self.battery_update_freq_edit)
        self.toolbox.addItem(telemetry_page, "Telemetry Graphs")

        # --- Data Handling Configuration Page ---
        data_page = QWidget()
        data_layout = QFormLayout(data_page)
        self.buffer_size_edit = QLineEdit(self)
        data_layout.addRow("Buffer Size:", self.buffer_size_edit)
        self.toolbox.addItem(data_page, "Data Handling")

        # --- Camera Configuration Page ---
        camera_page = QWidget()
        camera_layout = QFormLayout(camera_page)
        self.ip_webcam_url_edit = QLineEdit(self)
        camera_layout.addRow("IP Webcam URL:", self.ip_webcam_url_edit)
        self.toolbox.addItem(camera_page, "Camera")

        # --- Reload/Logging Options Page ---
        reload_log_page = QWidget()
        reload_log_layout = QFormLayout(reload_log_page)
        self.default_reload_mode_combo = QComboBox(self)
        self.default_reload_mode_combo.addItems([
            "Full Reload", 
            "Partial Reload (Time Range)", 
            "Partial Reload (Last X Seconds)",
            "Partial Reload (Data Point Range)",
            "Partial Reload (Last X Data Points)"
        ])
        reload_log_layout.addRow("Default Reload Mode:", self.default_reload_mode_combo)
        self.toolbox.addItem(reload_log_page, "Reload/Logging")

        # --- Reload Graphs Configuration Page ---
        reload_graphs_page = QWidget()
        reload_graphs_layout = QFormLayout(reload_graphs_page)
        self.reload_motor_titles_edit = QLineEdit(self)
        reload_graphs_layout.addRow("Motor Graph Titles (comma separated):", self.reload_motor_titles_edit)
        self.reload_motor_color_labels = []
        reload_motor_color_layout = QHBoxLayout()
        for i in range(4):
            label = QLabel(self)
            label.setStyleSheet(f"background-color: {DEFAULT_CONFIG['reload_motor_colors'][i]}; border: 1px solid black; padding: 5px;")
            label.mousePressEvent = lambda event, idx=i: self.choose_color(event, idx, self.reload_motor_color_labels, "reload_motor")
            self.reload_motor_color_labels.append(label)
            reload_motor_color_layout.addWidget(label)
        reload_graphs_layout.addRow("Motor Graph Colors:", reload_motor_color_layout)
        self.reload_orientation_titles_edit = QLineEdit(self)
        reload_graphs_layout.addRow("Orientation Graph Titles (comma separated):", self.reload_orientation_titles_edit)
        self.reload_orientation_color_labels = []
        reload_orientation_color_layout = QHBoxLayout()
        for i in range(4):
            label = QLabel(self)
            label.setStyleSheet(f"background-color: {DEFAULT_CONFIG['reload_orientation_colors'][i]}; border: 1px solid black; padding: 5px;")
            label.mousePressEvent = lambda event, idx=i: self.choose_color(event, idx, self.reload_orientation_color_labels, "reload_orientation")
            self.reload_orientation_color_labels.append(label)
            reload_orientation_color_layout.addWidget(label)
        reload_graphs_layout.addRow("Orientation Graph Colors:", reload_orientation_color_layout)
        self.reload_battery_title_edit = QLineEdit(self)
        reload_graphs_layout.addRow("Battery Graph Title:", self.reload_battery_title_edit)
        self.reload_battery_color_label = QLabel(self)
        self.reload_battery_color_label.setStyleSheet(f"background-color: {DEFAULT_CONFIG['reload_battery_color']}; border: 1px solid black; padding: 5px;")
        self.reload_battery_color_label.mousePressEvent = lambda event: self.choose_color(event, 0, [self.reload_battery_color_label], "reload_battery")
        reload_graphs_layout.addRow("Battery Graph Color:", self.reload_battery_color_label)
    
        self.toolbox.addItem(reload_graphs_page, "Reload Graphs")

        # --- Global Settings Page ---
        global_page = QWidget()
        global_layout = QFormLayout(global_page)
        self.enable_gps_combo = QComboBox(self)
        self.enable_gps_combo.addItems(["True", "False"])
        global_layout.addRow("Enable GPS:", self.enable_gps_combo)
        self.default_gps_fix_edit = QLineEdit(self)
        global_layout.addRow("Default GPS Fix Type:", self.default_gps_fix_edit)
        self.ui_font_edit = QLineEdit(self)
        global_layout.addRow("UI Font:", self.ui_font_edit)
        self.ui_bg_color_edit = QLabel(self)
        self.ui_bg_color_edit.setStyleSheet(f"background-color: {DEFAULT_CONFIG['ui_bg_color']}; border: 1px solid black; padding: 5px;")
        self.ui_bg_color_edit.mousePressEvent = lambda event: self.choose_color(event, 0, [self.ui_bg_color_edit], "ui_bg")
        global_layout.addRow("UI Background Color:", self.ui_bg_color_edit)
        self.toolbox.addItem(global_page, "Global Settings")

        main_layout.addWidget(self.toolbox)

        # Save Button at the bottom
        save_btn = QPushButton("Save Configuration", self)
        save_btn.clicked.connect(self.save_config)
        main_layout.addWidget(self.toolbox)
        main_layout.addWidget(save_btn)
        self.setLayout(main_layout)

    def choose_color(self, event, idx, label_list, key):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            # Do not set text on the color indicator; only update background.
            if isinstance(label_list, list) and len(label_list) > idx:
                label_list[idx].setStyleSheet(f"background-color: {color.name()}; border: 1px solid black; padding: 5px;")
            else:
                label_list[0].setStyleSheet(f"background-color: {color.name()}; border: 1px solid black; padding: 5px;")

    def load_config(self):
        from copy import deepcopy
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
            # Supplement missing keys with defaults:
            for key, value in DEFAULT_CONFIG.items():
                if key not in self.config:
                    self.config[key] = deepcopy(value)
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
            # Populate Telemetry fields:
            self.motor_titles_edit.setText(",".join(self.config["motor_titles"]))
            motor_colors = self.config["motor_colors"]
            for i, label in enumerate(self.motor_color_labels):
                label.setStyleSheet(f"background-color: {motor_colors[i]}; border: 1px solid black; padding: 5px;")
            self.motor_update_freq_edit.setText(str(self.config["motor_update_freq"]))
            self.orientation_titles_edit.setText(",".join(self.config["orientation_titles"]))
            orientation_colors = self.config["orientation_colors"]
            for i, label in enumerate(self.orientation_color_labels):
                label.setStyleSheet(f"background-color: {orientation_colors[i]}; border: 1px solid black; padding: 5px;")
            self.orientation_update_freq_edit.setText(str(self.config["orientation_update_freq"]))
            self.battery_title_edit.setText(self.config["battery_title"])
            self.battery_color_label.setStyleSheet(f"background-color: {self.config['battery_color']}; border: 1px solid black; padding: 5px;")
            self.battery_update_freq_edit.setText(str(self.config["battery_update_freq"]))
            # Data Handling:
            self.buffer_size_edit.setText(str(self.config["buffer_size"]))
            # Camera:
            self.ip_webcam_url_edit.setText(self.config["ip_webcam_url"])
            # Reload/Logging Options:
            default_reload_mode = self.config["default_reload_mode"]
            index = self.default_reload_mode_combo.findText(default_reload_mode)
            if index >= 0:
                self.default_reload_mode_combo.setCurrentIndex(index)
            # Reload Graphs:
            self.reload_motor_titles_edit.setText(",".join(self.config["reload_motor_titles"]))
            reload_motor_colors = self.config["reload_motor_colors"]
            for i, label in enumerate(self.reload_motor_color_labels):
                label.setStyleSheet(f"background-color: {reload_motor_colors[i]}; border: 1px solid black; padding: 5px;")
            self.reload_orientation_titles_edit.setText(",".join(self.config["reload_orientation_titles"]))
            reload_orientation_colors = self.config["reload_orientation_colors"]
            for i, label in enumerate(self.reload_orientation_color_labels):
                label.setStyleSheet(f"background-color: {reload_orientation_colors[i]}; border: 1px solid black; padding: 5px;")
            self.reload_battery_title_edit.setText(self.config["reload_battery_title"])
            reload_battery_color = self.config["reload_battery_color"]
            self.reload_battery_color_label.setStyleSheet(f"background-color: {reload_battery_color}; border: 1px solid black; padding: 5px;")
            # Global Settings:
            self.enable_gps_combo.setCurrentText(str(self.config["enable_gps"]))
            self.default_gps_fix_edit.setText(self.config["default_gps_fix"])
            self.ui_font_edit.setText(self.config["ui_font"])
            self.ui_bg_color_edit.setStyleSheet(f"background-color: {self.config['ui_bg_color']}; border: 1px solid black; padding: 5px;")
        else:
            # If no config file exists, write the default configuration.
            self.config = DEFAULT_CONFIG.copy()
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
            self.load_config()

    def save_config(self):
        try:
            self.config["motor_titles"] = [s.strip() for s in self.motor_titles_edit.text().split(",")]
            self.config["motor_colors"] = [label.styleSheet().split("background-color: ")[1].split(";")[0] for label in self.motor_color_labels]
            self.config["motor_update_freq"] = int(self.motor_update_freq_edit.text())
            self.config["orientation_titles"] = [s.strip() for s in self.orientation_titles_edit.text().split(",")]
            self.config["orientation_colors"] = [label.styleSheet().split("background-color: ")[1].split(";")[0] for label in self.orientation_color_labels]
            self.config["orientation_update_freq"] = int(self.orientation_update_freq_edit.text())
            self.config["battery_title"] = self.battery_title_edit.text().strip()
            self.config["battery_color"] = self.battery_color_label.styleSheet().split("background-color: ")[1].split(";")[0]
            self.config["battery_update_freq"] = int(self.battery_update_freq_edit.text())
            self.config["buffer_size"] = int(self.buffer_size_edit.text())
            self.config["ip_webcam_url"] = self.ip_webcam_url_edit.text().strip()
            self.config["default_reload_mode"] = self.default_reload_mode_combo.currentText()
            self.config["reload_motor_titles"] = [s.strip() for s in self.reload_motor_titles_edit.text().split(",")]
            self.config["reload_motor_colors"] = [label.styleSheet().split("background-color: ")[1].split(";")[0] for label in self.reload_motor_color_labels]
            self.config["reload_orientation_titles"] = [s.strip() for s in self.reload_orientation_titles_edit.text().split(",")]
            self.config["reload_orientation_colors"] = [label.styleSheet().split("background-color: ")[1].split(";")[0] for label in self.reload_orientation_color_labels]
            self.config["reload_battery_title"] = self.reload_battery_title_edit.text().strip()
            self.config["reload_battery_color"] = self.reload_battery_color_label.styleSheet().split("background-color: ")[1].split(";")[0]
            self.config["enable_gps"] = self.enable_gps_combo.currentText() == "True"
            self.config["default_gps_fix"] = self.default_gps_fix_edit.text().strip()
            self.config["ui_font"] = self.ui_font_edit.text().strip()
            self.config["ui_bg_color"] = self.ui_bg_color_edit.styleSheet().split("background-color: ")[1].split(";")[0]

            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
            print("Configuration saved to", self.config_file)
            self.configUpdated.emit(self.config)
        except Exception as e:
            print("Error saving configuration:", e)
