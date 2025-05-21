#reload_window.py

import logging
from datetime import datetime
import pandas as pd
from PyQt6.QtWidgets import (
    QGridLayout, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QLineEdit, QPushButton, QFrame
)
import pyqtgraph as pg
from pyqtgraph import DateAxisItem
from config_manager import load_config
from PyQt6.QtCore import Qt
from typing import Any, Dict

class LocalDateAxisItem(DateAxisItem):
    """Custom DateAxisItem to format timestamps."""
    def tickStrings(self, values, scale, spacing):
        return [datetime.fromtimestamp(value).strftime("%H:%M:%S") for value in values]

class ReloadMotorBlock(QWidget):
    """Block to display motor current plots and stats for reloaded data."""
    def __init__(self, df: pd.DataFrame, config: Dict[str, Any]) -> None:
        super().__init__()
        self.df = df
        self.config = config
        self.titles = self.config.get("reload_motor_titles", [])
        self.colors = self.config.get("reload_motor_colors", [])
        self.initUI()
        self.plot_data()

    def initUI(self) -> None:
        self.group_box = QGroupBox("Motor Currents & Stats")
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(2,2,2,2)
        group_layout.setSpacing(4)
        self.group_box.setLayout(group_layout)

        self.motor_container = QWidget()
        motor_layout = QVBoxLayout()
        self.motor_container.setLayout(motor_layout)
        #self.setStyleSheet("background-color: white;")

        self.motor_plots = []
        self.stats_labels = []
        self.titles_labels = []

        for i in range(4):
            motor_widget = QWidget()
            motor_widget_layout = QVBoxLayout()
            motor_widget.setLayout(motor_widget_layout)
            header_layout = QHBoxLayout()
            motor_label = QLabel(self.titles[i] if i < len(self.titles) else f"Motor {i+1}")
            motor_label.setStyleSheet("font-weight: bold;")
            self.titles_labels.append(motor_label)
            header_layout.addWidget(motor_label)
            header_layout.addStretch(1)
            motor_widget_layout.addLayout(header_layout)

            date_axis = LocalDateAxisItem(orientation='bottom')
            plot_widget = pg.PlotWidget(axisItems={'bottom': date_axis})
            #plot_widget.setBackground('w')
            plot_widget.setLabel('left', "Current (A)")
            plot_widget.setLabel('bottom', "Time")
            motor_widget_layout.addWidget(plot_widget)
            self.motor_plots.append(plot_widget)

            stats_layout = QHBoxLayout()
            avg_lbl = QLabel("Avg: 0.00 A")
            min_lbl = QLabel("Min: 0.00 A")
            max_lbl = QLabel("Max: 0.00 A")
            style = " border: 1px solid black; border-radius: 5px; padding: 2px;"
            avg_lbl.setStyleSheet(style)
            min_lbl.setStyleSheet(style)
            max_lbl.setStyleSheet(style)
            stats_layout.addWidget(avg_lbl)
            stats_layout.addWidget(min_lbl)
            stats_layout.addWidget(max_lbl)
            self.stats_labels.append((avg_lbl, min_lbl, max_lbl))
            motor_widget_layout.addLayout(stats_layout)

            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            motor_widget_layout.addWidget(separator)
            motor_layout.addWidget(motor_widget)

        group_layout.addWidget(self.motor_container)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)

    def plot_data(self) -> None:
        """Plot motor data and update stats labels."""
        time_data = self.df["Timestamp"].tolist()
        time_data_ts = [t.to_pydatetime().timestamp() for t in time_data]
        motors = [self.df.get(f"Motor{i+1}", []).tolist() for i in range(4)]
        for i in range(4):
            plot_widget = self.motor_plots[i]
            plot_widget.clear()
            if time_data_ts and motors[i]:
                plot_widget.plot(
                    time_data_ts, motors[i],
                    pen=pg.mkPen(color=self.colors[i] if i < len(self.colors) else "#000000", width=2),
                    name=self.titles[i] if i < len(self.titles) else f"Motor {i+1}"
                )
                plot_widget.enableAutoRange(axis=pg.ViewBox.XAxis, enable=True)
            if motors[i]:
                avg_val = sum(motors[i]) / len(motors[i])
                min_val = min(motors[i])
                max_val = max(motors[i])
                avg_lbl, min_lbl, max_lbl = self.stats_labels[i]
                avg_lbl.setText(f"Avg: {avg_val:.2f} A")
                min_lbl.setText(f"Min: {min_val:.2f} A")
                max_lbl.setText(f"Max: {max_val:.2f} A")

    def updateConfig(self, new_config: Dict[str, Any]) -> None:
        if "reload_motor_titles" in new_config:
            self.titles = new_config["reload_motor_titles"]
            for i, label in enumerate(self.titles_labels):
                if i < len(self.titles):
                    label.setText(self.titles[i])
        if "reload_motor_colors" in new_config:
            self.colors = new_config["reload_motor_colors"]
        self.plot_data()

class ReloadOrientationBlock(QWidget):
    """Block to display orientation and altitude plots for reloaded data."""
    def __init__(self, df: pd.DataFrame, config: Dict[str, Any]) -> None:
        super().__init__()
        self.df = df
        self.config = config
        self.titles = self.config.get("reload_orientation_titles", [])
        self.colors = self.config.get("reload_orientation_colors", [])
        self.initUI()
        self.plot_data()

    def initUI(self) -> None:
        self.group_box = QGroupBox("Orientation & Altitude & Stats")
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(2,2,2,2)
        group_layout.setSpacing(4)
        self.group_box.setLayout(group_layout)
        #self.setStyleSheet("background-color: white;")

        self.orient_container = QWidget()
        orient_layout = QVBoxLayout()
        self.orient_container.setLayout(orient_layout)

        self.orient_plots = []
        self.stats_labels = []
        self.titles_labels = []
        self.color_labels = []

        for i in range(4):
            widget = QWidget()
            widget_layout = QVBoxLayout()
            widget.setLayout(widget_layout)
            header_layout = QHBoxLayout()
            color_label = QLabel()
            color_label.setFixedSize(15, 15)
            color_label.setStyleSheet(f"background-color: {self.colors[i] if i < len(self.colors) else '#000000'};")
            self.color_labels.append(color_label)
            title_label = QLabel(self.titles[i] if i < len(self.titles) else f"Param {i+1}")
            title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
            self.titles_labels.append(title_label)
            header_layout.addWidget(title_label)
            header_layout.addStretch(1)
            widget_layout.addLayout(header_layout)

            date_axis = LocalDateAxisItem(orientation='bottom')
            plot_widget = pg.PlotWidget(axisItems={'bottom': date_axis})
            #plot_widget.setBackground('w')
            ylabel = "Degrees(°)" if i < 3 else "Meters(m)"
            plot_widget.setLabel('left', ylabel)
            plot_widget.setLabel('bottom', "Time")
            widget_layout.addWidget(plot_widget)
            self.orient_plots.append(plot_widget)

            stats_layout = QHBoxLayout()
            unit = "°" if i < 3 else " m"
            avg_lbl = QLabel(f"Avg: 0.00{unit}")
            min_lbl = QLabel(f"Min: 0.00{unit}")
            max_lbl = QLabel(f"Max: 0.00{unit}")
            style = " border: 1px solid black; border-radius: 5px; padding: 2px;"
            avg_lbl.setStyleSheet(style)
            min_lbl.setStyleSheet(style)
            max_lbl.setStyleSheet(style)
            stats_layout.addWidget(avg_lbl)
            stats_layout.addWidget(min_lbl)
            stats_layout.addWidget(max_lbl)
            self.stats_labels.append((avg_lbl, min_lbl, max_lbl))
            widget_layout.addLayout(stats_layout)

            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            widget_layout.addWidget(separator)
            orient_layout.addWidget(widget)

        group_layout.addWidget(self.orient_container)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)

    def plot_data(self) -> None:
        time_data = self.df["Timestamp"].tolist()
        time_data_ts = [t.to_pydatetime().timestamp() for t in time_data]
        roll = self.df.get("Roll", []).tolist()
        pitch = self.df.get("Pitch", []).tolist()
        yaw = self.df.get("Yaw", []).tolist()
        altitude = self.df.get("Altitude", []).tolist()
        data_list = [roll, pitch, yaw, altitude]
        for i in range(4):
            plot_widget = self.orient_plots[i]
            plot_widget.clear()
            if time_data_ts and data_list[i]:
                plot_widget.plot(
                    time_data_ts, data_list[i],
                    pen=pg.mkPen(color=self.colors[i] if i < len(self.colors) else "#000000", width=2),
                    name=self.titles[i] if i < len(self.titles) else f"Param {i+1}"
                )
                plot_widget.enableAutoRange(axis=pg.ViewBox.XAxis, enable=True)

    def updateConfig(self, new_config: Dict[str, Any]) -> None:
        if "reload_orientation_titles" in new_config:
            self.titles = new_config["reload_orientation_titles"]
            for i, label in enumerate(self.titles_labels):
                if i < len(self.titles):
                    label.setText(self.titles[i])
        if "reload_orientation_colors" in new_config:
            self.colors = new_config["reload_orientation_colors"]
            for i, color_label in enumerate(self.color_labels):
                if i < len(self.colors):
                    color_label.setStyleSheet(f"background-color: {self.colors[i]}; border: 1px solid black;")
        self.plot_data()

class ReloadBatteryBlock(QWidget):
    """Block to display battery data and stats for reloaded data."""
    def __init__(self, df: pd.DataFrame, config: Dict[str, Any]) -> None:
        super().__init__()
        self.df = df
        self.config = config
        self.battery_title = self.config.get("reload_battery_title", "Battery Status")
        self.battery_color = self.config.get("reload_battery_color", "#000000")
        self.show_percentage = True
        self.initUI()
        self.plot_data()

    def initUI(self) -> None:
        self.group_box = QGroupBox("Battery & Stats")
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(2,2,2,2)
        group_layout.setSpacing(4)
        self.group_box.setLayout(group_layout)

        self.toggle_button = QPushButton("Toggle: Percentage/Voltage")
        self.toggle_button.clicked.connect(self.toggle_view)
        group_layout.addWidget(self.toggle_button)

        date_axis = LocalDateAxisItem(orientation='bottom')
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': date_axis})
        #self.plot_widget.setBackground('w')
        self.plot_widget.setLabel('left', "Battery (%)" if self.show_percentage else "Battery (V)")
        self.plot_widget.setLabel('bottom', "Time")
        self.plot_widget.addLegend(offset=(120,1))
        self.plot_widget.setFixedHeight(200)
        group_layout.addWidget(self.plot_widget)

        self.battery_curve = self.plot_widget.plot(
            [], [],
            pen=pg.mkPen(color=self.battery_color, width=2),
            name="Battery Percentage"
        )

        stats_layout = QGridLayout()
        self.avg_value_label = QLabel("Avg: 0.00%")
        self.min_value_label = QLabel("Min: 0.00%")
        self.max_value_label = QLabel("Max: 0.00%")
        style = " border: 1px solid black; border-radius: 5px; padding: 2px;"
        self.avg_value_label.setStyleSheet(style)
        self.min_value_label.setStyleSheet(style)
        self.max_value_label.setStyleSheet(style)
        stats_layout.addWidget(self.avg_value_label, 0, 0, 1, 2)
        stats_layout.addWidget(self.min_value_label, 1, 0)
        stats_layout.addWidget(self.max_value_label, 1, 1)

        stats_outer_layout = QHBoxLayout()
        stats_outer_layout.addStretch(1)
        stats_outer_layout.addLayout(stats_layout)
        stats_outer_layout.addStretch(1)
        group_layout.addLayout(stats_outer_layout)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.group_box)
        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def plot_data(self) -> None:
        time_data = self.df["Timestamp"].tolist()
        time_data_ts = [t.to_pydatetime().timestamp() for t in time_data]
        if self.show_percentage:
            y_data = self.df.get("Percentage", []).tolist()
        else:
            y_data = self.df.get("Voltage", []).tolist()
        if time_data_ts and y_data:
            self.battery_curve.setData(time_data_ts, y_data)
            self.plot_widget.enableAutoRange(axis=pg.ViewBox.XAxis, enable=True)
            if self.show_percentage:
                self.plot_widget.setYRange(20, 100)
            else:
                self.plot_widget.setYRange(10, 14.6)
            avg_val = sum(y_data) / len(y_data)
            min_val = min(y_data)
            max_val = max(y_data)
            unit = "%" if self.show_percentage else "V"
            self.avg_value_label.setText(f"Avg: {avg_val:.2f}{unit}")
            self.min_value_label.setText(f"Min: {min_val:.2f}{unit}")
            self.max_value_label.setText(f"Max: {max_val:.2f}{unit}")

    def toggle_view(self) -> None:
        self.show_percentage = not self.show_percentage
        self.plot_widget.setLabel('left', "Battery (%)" if self.show_percentage else "Battery (V)")
        self.plot_data()

    def updateConfig(self, new_config: Dict[str, Any]) -> None:
        if "reload_battery_title" in new_config:
            self.battery_title = new_config["reload_battery_title"]
            self.plot_widget.setLabel('left', self.battery_title)
        if "reload_battery_color" in new_config:
            self.battery_color = new_config["reload_battery_color"]
            self.battery_curve.setPen(pg.mkPen(color=self.battery_color, width=2))
        self.plot_data()

class CombinedReloadDisplayWidget(QWidget):
    """Combined widget for reloaded data display."""
    def __init__(self, df: pd.DataFrame, config: Dict[str, Any]) -> None:
        super().__init__()
        self.df = df
        self.config = config
        self.initUI()

    def initUI(self) -> None:
        layout = QHBoxLayout()
        self.reload_motor = ReloadMotorBlock(self.df, config=self.config)
        self.reload_orientation = ReloadOrientationBlock(self.df, config=self.config)
        self.reload_battery = ReloadBatteryBlock(self.df, config=self.config)
        layout.addWidget(self.reload_motor)
        layout.addWidget(self.reload_orientation)
        layout.addWidget(self.reload_battery)
        self.setLayout(layout)

    def updateConfig(self, new_config: Dict[str, Any]) -> None:
        self.reload_motor.updateConfig(new_config)
        self.reload_orientation.updateConfig(new_config)
        self.reload_battery.updateConfig(new_config)
        self.config.update(new_config)

class ReloadWindow(QMainWindow):
    """Main window for reloading and filtering logged data."""
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Reload Data")
        self.setGeometry(150, 150, 1400, 1000)
        self.initUI()

    def initUI(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 5)
        main_layout.setSpacing(5)

        options_layout = QHBoxLayout()

        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems([
            "Full Reload", 
            "Partial Reload (Time Range)", 
            "Partial Reload (Last X Seconds)",
            "Partial Reload (Data Point Range)",
            "Partial Reload (Last X Data Points)"
        ])
        self.mode_dropdown.currentTextChanged.connect(self.reload_mode_changed)
        options_layout.addWidget(QLabel("Reload Mode:"))
        options_layout.addWidget(self.mode_dropdown)

        self.start_time_edit = QLineEdit()
        self.start_time_edit.setPlaceholderText("Start Time (s)")
        self.end_time_edit = QLineEdit()
        self.end_time_edit.setPlaceholderText("End Time (s)")
        self.last_time_edit = QLineEdit()
        self.last_time_edit.setPlaceholderText("Last X Seconds")
        self.start_index_edit = QLineEdit()
        self.start_index_edit.setPlaceholderText("Start Index")
        self.end_index_edit = QLineEdit()
        self.end_index_edit.setPlaceholderText("End Index")
        self.last_points_edit = QLineEdit()
        self.last_points_edit.setPlaceholderText("Last X Data Points")

        options_layout.addWidget(QLabel("Start Time:"))
        options_layout.addWidget(self.start_time_edit)
        options_layout.addWidget(QLabel("End Time:"))
        options_layout.addWidget(self.end_time_edit)
        options_layout.addWidget(QLabel("Last Seconds:"))
        options_layout.addWidget(self.last_time_edit)
        options_layout.addWidget(QLabel("Start Index:"))
        options_layout.addWidget(self.start_index_edit)
        options_layout.addWidget(QLabel("End Index:"))
        options_layout.addWidget(self.end_index_edit)
        options_layout.addWidget(QLabel("Last Data Points:"))
        options_layout.addWidget(self.last_points_edit)

        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.apply_reload)
        options_layout.addWidget(self.reload_button)
        main_layout.addLayout(options_layout)

        self.set_partial_fields_enabled(False, False, False, False)

        try:
            self.df_full = pd.read_excel("quadcopter_data.xlsx")
            self.df_full["Timestamp"] = pd.to_datetime(self.df_full["Timestamp"], format="%Y-%m-%d %H:%M:%S.%f")
        except Exception as e:
            logging.error(f"Error loading Excel file: {e}")
            self.df_full = None

        if self.df_full is not None:
            current_config = load_config()
            self.combined_reload_display = CombinedReloadDisplayWidget(self.df_full, config=current_config)
            main_layout.addWidget(self.combined_reload_display)
        else:
            error_label = QLabel("Failed to load data.")
            main_layout.addWidget(error_label)

    def set_partial_fields_enabled(self, time_abs: bool, time_rel: bool, index_abs: bool, index_rel: bool) -> None:
        self.start_time_edit.setEnabled(time_abs)
        self.end_time_edit.setEnabled(time_abs)
        self.last_time_edit.setEnabled(time_rel)
        self.start_index_edit.setEnabled(index_abs)
        self.end_index_edit.setEnabled(index_abs)
        self.last_points_edit.setEnabled(index_rel)

    def reload_mode_changed(self, mode: str) -> None:
        self.set_partial_fields_enabled(False, False, False, False)
        if mode == "Full Reload":
            pass
        elif mode == "Partial Reload (Time Range)":
            self.set_partial_fields_enabled(True, False, False, False)
        elif mode == "Partial Reload (Last X Seconds)":
            self.set_partial_fields_enabled(False, True, False, False)
        elif mode == "Partial Reload (Data Point Range)":
            self.set_partial_fields_enabled(False, False, True, False)
        elif mode == "Partial Reload (Last X Data Points)":
            self.set_partial_fields_enabled(False, False, False, True)

    def apply_reload(self) -> None:
        try:
            self.df_full = pd.read_excel("quadcopter_data.xlsx")
            self.df_full["Timestamp"] = pd.to_datetime(self.df_full["Timestamp"], format="%Y-%m-%d %H:%M:%S.%f")
        except Exception as e:
            logging.error(f"Error loading Excel file: {e}")
            self.df_full = None
            return

        if self.df_full is None or self.df_full.empty:
            return

        mode = self.mode_dropdown.currentText()
        if mode == "Full Reload":
            df_filtered = self.df_full.copy()
        elif mode == "Partial Reload (Time Range)":
            try:
                start_time_input = datetime.strptime(self.start_time_edit.text(), "%H:%M:%S.%f")
            except ValueError:
                try:
                    start_time_input = datetime.strptime(self.start_time_edit.text(), "%H:%M:%S")
                except ValueError:
                    logging.error("Invalid start time format. Use HH:MM:SS or HH:MM:SS.mmm")
                    return
            try:
                end_time_input = datetime.strptime(self.end_time_edit.text(), "%H:%M:%S.%f")
            except ValueError:
                try:
                    end_time_input = datetime.strptime(self.end_time_edit.text(), "%H:%M:%S")
                except ValueError:
                    logging.error("Invalid end time format. Use HH:MM:SS or HH:MM:SS.mmm")
                    return
            base_date = self.df_full["Timestamp"].min().date()
            start_time = datetime.combine(base_date, start_time_input.time())
            end_time = datetime.combine(base_date, end_time_input.time())
            df_filtered = self.df_full[(self.df_full["Timestamp"] >= start_time) & (self.df_full["Timestamp"] <= end_time)]
        elif mode == "Partial Reload (Last X Seconds)":
            try:
                last_seconds = float(self.last_time_edit.text())
            except ValueError:
                logging.error("Invalid time value. Please enter a numeric value.")
                return
            max_time = self.df_full["Timestamp"].max()
            start_time = max_time - pd.Timedelta(seconds=last_seconds)
            df_filtered = self.df_full[self.df_full["Timestamp"] >= start_time]
        elif mode == "Partial Reload (Data Point Range)":
            try:
                start_idx = int(self.start_index_edit.text())
                end_idx = int(self.end_index_edit.text())
            except ValueError:
                logging.error("Invalid index values. Please enter integer values.")
                return
            df_filtered = self.df_full.iloc[start_idx:end_idx]
        elif mode == "Partial Reload (Last X Data Points)":
            try:
                last_points = int(self.last_points_edit.text())
            except ValueError:
                logging.error("Invalid data points value. Please enter an integer value.")
                return
            df_filtered = self.df_full.iloc[-last_points:]
        else:
            df_filtered = self.df_full.copy()

        container = self.centralWidget()
        if container is None:
            container = self
        central_layout = container.layout()
        if central_layout is None:
            central_layout = QVBoxLayout(container)
            container.setLayout(central_layout)
        if hasattr(self, "combined_reload_display"):
            central_layout.removeWidget(self.combined_reload_display)
            self.combined_reload_display.deleteLater()

        current_config = load_config()
        self.combined_reload_display = CombinedReloadDisplayWidget(df_filtered, config=current_config)
        central_layout.addWidget(self.combined_reload_display)

    def updateConfig(self, new_config: Dict[str, Any]) -> None:
        if hasattr(self, "combined_reload_display"):
            self.combined_reload_display.updateConfig(new_config)
        else:
            logging.error("No reload display to update.")
