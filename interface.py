#interface.py

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from DisplayWidget import DisplayWidget
from PyQt6.QtCore import QTimer
from data_handler import DataHandler
from reloadwindow import ReloadWindow 
from MultiCameraInterface import MultiCameraWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_handler = DataHandler()
        self.camera_window = None
        self.initUI()
        self.setup_update_timer()

    def initUI(self):
        self.setWindowTitle("Quadcopter Telemetry Dashboard")
        self.setGeometry(100, 100, 1400, 1000)
        self.showMaximized()
        
        central_widget = QWidget()
        
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 5)
        main_layout.setSpacing(5)

        
        button_layout = QHBoxLayout()
        self.start_stop_button = QPushButton("Start")
        self.reload_button = QPushButton("Reload Data")
        self.camera_button = QPushButton("Camera") 
        self.reload_button.clicked.connect(self.open_reload_interface)
        self.start_stop_button.clicked.connect(self.toggle_start_stop)
        self.camera_button.clicked.connect(self.open_camera_window)
        button_layout.addWidget(self.start_stop_button)
        button_layout.addWidget(self.reload_button)
        button_layout.addWidget(self.camera_button)
        main_layout.addLayout(button_layout)


    
        self.enhanced_display = DisplayWidget(self.data_handler)
        main_layout.addWidget(self.enhanced_display)
    def setup_update_timer(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.enhanced_display.update_all)
        self.update_timer.start(200)
    def open_camera_window(self):
        if self.camera_window is None:
            self.camera_window = MultiCameraWindow()
            self.camera_window.showMaximized()
        self.camera_window.show()
    def toggle_start_stop(self):
        if self.start_stop_button.text() == "Start":
            self.start_stop_button.setText("Stop")
            self.data_handler.start()
            self.enhanced_display.motor.motor_block.start()
            self.enhanced_display.orientation.orient_block.start()
            self.enhanced_display.battery.battery_block.start()
        else:
            self.start_stop_button.setText("Start")
            self.data_handler.stop()
            self.enhanced_display.motor.motor_block.stop()
            self.enhanced_display.orientation.orient_block.stop()
            self.enhanced_display.battery.battery_block.stop()

    def open_reload_interface(self):
        self.reload_window = ReloadWindow()
        self.reload_window.showMaximized()
