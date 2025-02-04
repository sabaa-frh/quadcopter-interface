from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from DisplayWidget import DisplayWidget
from data_handler import DataHandler
from reloadwindow import ReloadWindow 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_handler = DataHandler()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Quadcopter Telemetry Dashboard")
        self.setGeometry(100, 100, 1400, 1000)
        self.showMaximized()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 5)
        main_layout.setSpacing(5)

        # Buttons layout (Start and Reload)
        button_layout = QHBoxLayout()
        self.start_stop_button = QPushButton("Start")
        self.reload_button = QPushButton("Reload Data")
        self.reload_button.clicked.connect(self.open_reload_interface)
        self.start_stop_button.clicked.connect(self.toggle_start_stop)
        button_layout.addWidget(self.start_stop_button)
        button_layout.addWidget(self.reload_button)
        main_layout.addLayout(button_layout)

    
        self.enhanced_display = DisplayWidget(self.data_handler)
        main_layout.addWidget(self.enhanced_display)

    

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
