#main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from interface import MainWindow
from data_handler import DataHandler
from config_widget import load_config,ConfigTab


config = load_config()
data_handler = DataHandler(config=config)

class ExtendedMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Telemetry Dashboard")
        self.setGeometry(100, 100, 1400, 1000)
        self.initUI()

    def initUI(self):
        tab_widget = QTabWidget(self)
        self.dashboard = MainWindow(data_handler=data_handler)
        tab_widget.addTab(self.dashboard, "Dashboard")
        self.config_tab = ConfigTab()
        self.config_tab.configUpdated.connect(self.update_dashboard_config)
        tab_widget.addTab(self.config_tab, "Configuration")
        self.setCentralWidget(tab_widget)

    def update_dashboard_config(self, new_config):
        data_handler.updateConfig(new_config)
        self.dashboard.updateConfig(new_config)
        self.dashboard.reload_widget.updateConfig(new_config)
        print("Dashboard configuration updated.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExtendedMainWindow()
    window.showMaximized()
    sys.exit(app.exec())
