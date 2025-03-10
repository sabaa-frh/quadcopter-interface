# interface.py
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QPushButton
from PyQt6.QtCore import Qt
from DisplayWidget import DisplayWidget
from MultiCameraInterface import MultiCameraWindow
from reloadwindow import ReloadWindow

class MainWindow(QMainWindow):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Quadcopter Telemetry Dashboard")
        self.setGeometry(100, 100, 1400, 1000)
        tab_widget = QTabWidget()
        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.clicked.connect(self.toggle_start_stop)
        tab_widget.setCornerWidget(self.start_stop_button, Qt.Corner.TopRightCorner)

        # Create telemetry, camera, and reload tabs.
        self.telemetry_widget = DisplayWidget(self.data_handler)
        tab_widget.addTab(self.telemetry_widget, "Telemetry")
        camera_window = MultiCameraWindow()
        camera_widget = camera_window.centralWidget() or camera_window
        tab_widget.addTab(camera_widget, "Camera")
        self.reload_widget = ReloadWindow()
        tab_widget.addTab(self.reload_widget, "Reload Data")

        self.setCentralWidget(tab_widget)

    def updateConfig(self, new_config):
        self.telemetry_widget.motor.updateConfig(new_config)
        self.telemetry_widget.orientation.updateConfig(new_config)
        self.telemetry_widget.battery.updateConfig(new_config)
        

    def toggle_start_stop(self):
        if self.start_stop_button.text() == "Start":
            self.start_stop_button.setText("Stop")
            self.data_handler.start()
            try:
                self.telemetry_widget.motor.motor_block.start()
                self.telemetry_widget.orientation.orient_block.start()
                self.telemetry_widget.battery.battery_block.start()
            except Exception as e:
                print("Error starting telemetry blocks:", e)
        else:
            self.start_stop_button.setText("Start")
            self.data_handler.stop()
            try:
                self.telemetry_widget.motor.motor_block.stop()
                self.telemetry_widget.orientation.orient_block.stop()
                self.telemetry_widget.battery.battery_block.stop()
            except Exception as e:
                print("Error stopping telemetry blocks:", e)
            try:
                self.reload_widget.apply_reload()
            except Exception as e:
                print("Error updating reload window:", e)
