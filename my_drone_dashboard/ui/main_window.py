#main_window.py

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QLabel, QPushButton, QWidget, QHBoxLayout,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer

from ui.display_widget import DisplayWidget
from ui.reload_window  import ReloadWindow
from ui.multi_camera   import MultiCameraWindow

if TYPE_CHECKING:  # avoid circular import at runtime
    from data_handler import DataHandler


class MainWindow(QMainWindow):
    """Hosts all dashboard tabs and shows connection state in real‑time."""

    def __init__(self, data_handler: DataHandler) -> None:
        super().__init__()
        self.data_handler = data_handler
        self.initUI()
        self._setup_connection_timer()

    # ------------------------------------------------------------------ UI

    def initUI(self) -> None:
        self.setWindowTitle("Quadcopter Telemetry Dashboard")
        self.setGeometry(100, 100, 1400, 1000)

        # ── main tab widget ------------------------------------------------
        tab_widget = QTabWidget()

        # ── connection / control widgets in top‑right corner --------------
        self.conn_label = QLabel("Disconnected")
        self.conn_label.setStyleSheet("color:red;font-weight:bold;")

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setFixedHeight(22)
        self.connect_btn.clicked.connect(self._on_connect_clicked)

        self.stop_btn = QPushButton("Stop & Save")
        self.stop_btn.setFixedHeight(22)
        self.stop_btn.clicked.connect(self._on_stop_clicked)

        corner = QWidget()
        h = QHBoxLayout(corner)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)
        h.addWidget(self.conn_label)
        h.addWidget(self.connect_btn)
        h.addWidget(self.stop_btn)
        tab_widget.setCornerWidget(corner, Qt.Corner.TopRightCorner)

        # ── Telemetry tab --------------------------------------------------
        self.telemetry_widget = DisplayWidget(self.data_handler)
        tab_widget.addTab(self.telemetry_widget, "Telemetry")

        # ── Camera tab -----------------------------------------------------
        camera_window = MultiCameraWindow()
        camera_widget = camera_window.centralWidget() or camera_window
        tab_widget.addTab(camera_widget, "Camera")

        # ── Reload Data tab ------------------------------------------------
        self.reload_widget = ReloadWindow()
        tab_widget.addTab(self.reload_widget, "Reload Data")

        self.setCentralWidget(tab_widget)

    # ------------------------------------------------------------------ connection polling

    def _setup_connection_timer(self) -> None:
        self.conn_timer = QTimer(self)
        self.conn_timer.timeout.connect(self._update_connection_status)
        self.conn_timer.start(500)  # twice per second

    def _update_connection_status(self) -> None:
        ser = self.data_handler.serial_device
        if ser and ser.is_open:
            self.conn_label.setText("Connected")
            self.conn_label.setStyleSheet("color:green;font-weight:bold;")
        else:
            self.conn_label.setText("Disconnected")
            self.conn_label.setStyleSheet("color:red;font-weight:bold;")

    # ------------------------------------------------------------------ slots / actions

    def _on_connect_clicked(self) -> None:
        """Attempt to (re)connect the Arduino and start serial thread."""
        if self.data_handler.serial_connected:
            QMessageBox.information(self, "Already connected",
                                    "Arduino is already connected.")
            return

        ok = self.data_handler.connect_to_arduino()
        if ok:
            self.data_handler.start_serial_thread()
            # ensure sampling timer is running (may have been stopped)
            if not self.data_handler.timer.isActive():
                self.data_handler.timer.start(200)
            QMessageBox.information(self, "Connected",
                                    f"Connected to {self.data_handler.arduino_port}")
            self.connect_btn.setEnabled(False)  # prevent double click
            self.stop_btn.setEnabled(True)
        else:
            QMessageBox.warning(self, "Connection failed",
                                "Cannot connect to Arduino. Check the port and cable.")

    def _on_stop_clicked(self) -> None:
        """Stop timers, close serial and save the Excel log."""
        if self.data_handler.timer.isActive() or self.data_handler.running:
            self.data_handler.stop()
            self.stop_btn.setEnabled(False)
            self.connect_btn.setEnabled(True)
            QMessageBox.information(self, "Data saved",
                                    "Telemetry log saved to quadcopter_data.xlsx")
            self.reload_widget.apply_reload()

    # ------------------------------------------------------------------ propagate config

    def updateConfig(self, new_config: dict) -> None:
        self.telemetry_widget.motor_block.updateConfig(new_config)
        self.telemetry_widget.orientation_block.updateConfig(new_config)
        self.telemetry_widget.battery.updateConfig(new_config)

    # ------------------------------------------------------------------ window life‑cycle

    def closeEvent(self, event):
        # guarantee we flush data to disk even on window X
        if self.data_handler.timer.isActive() or self.data_handler.running:
            self.data_handler.stop()
        super().closeEvent(event)

   