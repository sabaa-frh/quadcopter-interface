#config_manager.py

import json
import os
import logging
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "buffer_size": 100,
    "num_motors": 4,
    "enable_gps": True,
    "gps_fix_types": ["2D", "3D", "None"],
    "motor_color": "#ff0000",
    "voltage_drop_range": [0.0, 0.01],
    "altitude_variation": 0.1,
    "motor_current_range": [0.0, 10.0],
    "arduino_port":     "COM3",
    "arduino_baudrate": 115200,
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
    "ui_bg_color": "#ffffff",
    "light_mode": False,        # False → dark (default)  |  True → light
}

CONFIG_FILE = "config.json"

def load_config(config_file: str = CONFIG_FILE) -> Dict[str, Any]:
    """Load configuration from JSON file, filling missing keys with defaults."""
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            # Supplement missing keys with defaults:
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            with open(config_file, "w") as f:
                json.dump(config, f, indent=4)
            logging.info(f"Configuration loaded from {config_file}")
            return config
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()
    else:
        with open(config_file, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        logging.info(f"Default configuration written to {config_file}")
        return DEFAULT_CONFIG.copy()

# GUI part for configuration:

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QToolBox, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QLabel, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal

class ConfigTab(QWidget):
    """
    Configuration tab widget for adjusting and saving project settings.
    Emits configUpdated signal when configuration changes.
    """
    configUpdated = pyqtSignal(dict)

    def __init__(self, config_file: str = CONFIG_FILE, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config_file = config_file
        self.config = {}
        self.initUI()
        self.load_config()

    def initUI(self) -> None:
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
            label.setFixedSize(30, 30)
            label.setStyleSheet(f"background-color: {DEFAULT_CONFIG['motor_colors'][i]}; border: 1px solid black;")
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
            label.setFixedSize(30, 30)
            label.setStyleSheet(f"background-color: {DEFAULT_CONFIG['orientation_colors'][i]}; border: 1px solid black;")
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
        self.battery_color_label.setFixedSize(30, 30)
        self.battery_color_label.setStyleSheet(f"background-color: {DEFAULT_CONFIG['battery_color']}; border: 1px solid black;")
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

        self.arduino_port_edit = QLineEdit(self)
        data_layout.addRow("Arduino Port:", self.arduino_port_edit)
        self.arduino_baudrate_edit = QLineEdit(self)
        data_layout.addRow("Arduino Baudrate:", self.arduino_baudrate_edit)

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
        reload_graphs_layout.addRow("Reload Motor Graph Titles (comma separated):", self.reload_motor_titles_edit)
        self.reload_motor_color_labels = []
        reload_motor_color_layout = QHBoxLayout()
        for i in range(4):
            label = QLabel(self)
            label.setFixedSize(30, 30)
            label.setStyleSheet(f"background-color: {DEFAULT_CONFIG['reload_motor_colors'][i]}; border: 1px solid black;")
            label.mousePressEvent = lambda event, idx=i: self.choose_color(event, idx, self.reload_motor_color_labels, "reload_motor")
            self.reload_motor_color_labels.append(label)
            reload_motor_color_layout.addWidget(label)
        reload_graphs_layout.addRow("Reload Motor Graph Colors:", reload_motor_color_layout)
        self.reload_orientation_titles_edit = QLineEdit(self)
        reload_graphs_layout.addRow("Reload Orientation Graph Titles (comma separated):", self.reload_orientation_titles_edit)
        self.reload_orientation_color_labels = []
        reload_orientation_color_layout = QHBoxLayout()
        for i in range(4):
            label = QLabel(self)
            label.setFixedSize(30, 30)
            label.setStyleSheet(f"background-color: {DEFAULT_CONFIG['reload_orientation_colors'][i]}; border: 1px solid black;")
            label.mousePressEvent = lambda event, idx=i: self.choose_color(event, idx, self.reload_orientation_color_labels, "reload_orientation")
            self.reload_orientation_color_labels.append(label)
            reload_orientation_color_layout.addWidget(label)
        reload_graphs_layout.addRow("Reload Orientation Graph Colors:", reload_orientation_color_layout)
        self.reload_battery_title_edit = QLineEdit(self)
        reload_graphs_layout.addRow("Reload Battery Graph Title:", self.reload_battery_title_edit)
        self.reload_battery_color_label = QLabel(self)
        self.reload_battery_color_label.setFixedSize(30, 30)
        self.reload_battery_color_label.setStyleSheet(f"background-color: {DEFAULT_CONFIG['reload_battery_color']}; border: 1px solid black;")
        self.reload_battery_color_label.mousePressEvent = lambda event: self.choose_color(event, 0, [self.reload_battery_color_label], "reload_battery")
        reload_graphs_layout.addRow("Reload Battery Graph Color:", self.reload_battery_color_label)
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
        self.ui_bg_color_edit.setFixedSize(30, 30)
        self.ui_bg_color_edit.setStyleSheet(f"background-color: {DEFAULT_CONFIG['ui_bg_color']}; border: 1px solid black;")
        self.ui_bg_color_edit.mousePressEvent = lambda event: self.choose_color(event, 0, [self.ui_bg_color_edit], "ui_bg")
        global_layout.addRow("UI Background Color:", self.ui_bg_color_edit)
        self.theme_combo = QComboBox(self)
        self.theme_combo.addItems(["Dark", "Light"])
        global_layout.addRow("Theme:", self.theme_combo)
        self.toolbox.addItem(global_page, "Global Settings")
        

        main_layout.addWidget(self.toolbox)

        save_btn = QPushButton("Save Configuration", self)
        save_btn.clicked.connect(self.save_config)
        main_layout.addWidget(save_btn)
        self.setLayout(main_layout)

    def choose_color(self, event, idx: int, label_list: list, key: str) -> None:
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            if isinstance(label_list, list) and len(label_list) > idx:
                label_list[idx].setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            else:
                label_list[0].setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")

    def load_config(self) -> None:
        """Load configuration from file and populate UI fields."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
                for key, value in DEFAULT_CONFIG.items():
                    if key not in self.config:
                        self.config[key] = value
                with open(self.config_file, "w") as f:
                    json.dump(self.config, f, indent=4)
                self.motor_titles_edit.setText(",".join(self.config["motor_titles"]))
                motor_colors = self.config["motor_colors"]
                for i, label in enumerate(self.motor_color_labels):
                    label.setStyleSheet(f"background-color: {motor_colors[i]}; border: 1px solid black;")
                self.motor_update_freq_edit.setText(str(self.config["motor_update_freq"]))
                self.orientation_titles_edit.setText(",".join(self.config["orientation_titles"]))
                orientation_colors = self.config["orientation_colors"]
                for i, label in enumerate(self.orientation_color_labels):
                    label.setStyleSheet(f"background-color: {orientation_colors[i]}; border: 1px solid black;")
                self.orientation_update_freq_edit.setText(str(self.config["orientation_update_freq"]))
                self.battery_title_edit.setText(self.config["battery_title"])
                self.battery_color_label.setStyleSheet(f"background-color: {self.config['battery_color']}; border: 1px solid black;")
                self.battery_update_freq_edit.setText(str(self.config["battery_update_freq"]))
                self.buffer_size_edit.setText(str(self.config["buffer_size"]))
                self.arduino_port_edit.setText(self.config.get("arduino_port","COM3"))
                self.arduino_baudrate_edit.setText(str(self.config.get("arduino_baudrate",115200)))
                self.ip_webcam_url_edit.setText(self.config["ip_webcam_url"])
                default_reload_mode = self.config["default_reload_mode"]
                index = self.default_reload_mode_combo.findText(default_reload_mode)
                if index >= 0:
                    self.default_reload_mode_combo.setCurrentIndex(index)
                self.reload_motor_titles_edit.setText(",".join(self.config["reload_motor_titles"]))
                reload_motor_colors = self.config["reload_motor_colors"]
                for i, label in enumerate(self.reload_motor_color_labels):
                    label.setStyleSheet(f"background-color: {reload_motor_colors[i]}; border: 1px solid black;")
                self.reload_orientation_titles_edit.setText(",".join(self.config["reload_orientation_titles"]))
                reload_orientation_colors = self.config["reload_orientation_colors"]
                for i, label in enumerate(self.reload_orientation_color_labels):
                    label.setStyleSheet(f"background-color: {reload_orientation_colors[i]}; border: 1px solid black;")
                self.reload_battery_title_edit.setText(self.config["reload_battery_title"])
                self.reload_battery_color_label.setStyleSheet(f"background-color: {self.config['reload_battery_color']}; border: 1px solid black;")
                self.enable_gps_combo.setCurrentText(str(self.config["enable_gps"]))
                self.default_gps_fix_edit.setText(self.config["default_gps_fix"])
                self.ui_font_edit.setText(self.config["ui_font"])
                self.ui_bg_color_edit.setStyleSheet(f"background-color: {self.config['ui_bg_color']}; border: 1px solid black;")
                self.theme_combo.setCurrentText("Light"
                    if self.config.get("light_mode", False) else "Dark")
                logging.info("Configuration loaded in ConfigTab.")
            else:
                self.config = DEFAULT_CONFIG.copy()
                with open(self.config_file, "w") as f:
                    json.dump(self.config, f, indent=4)
                self.load_config()
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")

    def save_config(self) -> None:
        """Save the current configuration from UI fields to file and emit update signal."""
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
            self.config["arduino_port"]     = self.arduino_port_edit.text().strip()
            self.config["arduino_baudrate"] = int(self.arduino_baudrate_edit.text())
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
            self.config["light_mode"] = (self.theme_combo.currentText() == "Light")
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
            logging.info(f"Configuration saved to {self.config_file}")
            self.configUpdated.emit(self.config)
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")