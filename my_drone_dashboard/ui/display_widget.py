#display_widget.py


from PyQt6.QtWidgets import (
    QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QProgressBar, QSizePolicy,QSplitter
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import pyqtgraph as pg
from pyqtgraph.opengl import GLViewWidget, GLLinePlotItem
import numpy as np
from typing          import Any, Dict
from pdf import DroneAttitudeIndicator, HeadingIndicator
from ui.blocks import MotorCurrentVisualization, OrientationAltitudeVisualization, BatteryMonitoring

class MotorBlock(QWidget):
    """Group box for motor current visualization."""
    def __init__(self, data_handler: Any) -> None:
        super().__init__()
        self.data_handler = data_handler
        self.initUI()

    def initUI(self) -> None:
        self.group_box = QGroupBox("Motor Currents & Stats")
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(2,2,2,2)
        group_layout.setSpacing(2)
        self.group_box.setLayout(group_layout)
        self.motor_block = MotorCurrentVisualization(self.data_handler)
        group_layout.addWidget(self.motor_block, 0, Qt.AlignmentFlag.AlignTop)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)

    def updateConfig(self, new_config: dict) -> None:
        self.motor_block.updateConfig(new_config)


class OrientationAltitudeBlock(QWidget):
    """Group box for orientation/altitude stats + PFD + RC gauges."""
    def __init__(self, data_handler: Any) -> None:
        super().__init__()
        self.data_handler = data_handler
        self.initUI()

        # timer to refresh PFD & gauges
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_controls)
        self.timer.start(50)

    def initUI(self) -> None:
        self.group_box = QGroupBox("Orientation & Altitude & Stats")
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(2,2,2,2)
        group_layout.setSpacing(4)

        # 1) your existing 2×2 visualization
        self.orient_block = OrientationAltitudeVisualization(self.data_handler)
        group_layout.addWidget(self.orient_block)

        # 2) PFD + gauges row
        row = QHBoxLayout()

        # -- PFD --
        pfd_group = QGroupBox("Primary Flight Display")
        pfd_layout = QHBoxLayout(pfd_group)
        center = QVBoxLayout()
        self.attitude = DroneAttitudeIndicator()
        self.heading  = HeadingIndicator()
        center.addWidget(self.attitude)
        center.addWidget(self.heading)
        pfd_layout.addLayout(center)

        row.addWidget(pfd_group, stretch=3)

        # -- RC gauges for roll/pitch/yaw/throttle --
        gauge_box = QWidget()
        gauge_layout = QVBoxLayout(gauge_box)
        gauge_layout.setContentsMargins(4,4,4,4)
        gauge_layout.setSpacing(8)

        self.roll_bar = QProgressBar()
        self.roll_bar.setRange(1000,2000)
        self.roll_bar.setFormat("Roll: %v")
        gauge_layout.addWidget(self.roll_bar)

        self.pitch_bar = QProgressBar()
        self.pitch_bar.setRange(1000,2000)
        self.pitch_bar.setFormat("Pitch: %v")
        gauge_layout.addWidget(self.pitch_bar)

        self.yaw_bar = QProgressBar()
        self.yaw_bar.setRange(1000,2000)
        self.yaw_bar.setFormat("Yaw: %v")
        gauge_layout.addWidget(self.yaw_bar)

        self.throttle_bar = QProgressBar()
        self.throttle_bar.setOrientation(Qt.Orientation.Vertical)
        self.throttle_bar.setRange(1000,2000)
        self.throttle_bar.setFixedHeight(120)
        self.throttle_bar.setFormat("Thr: %v")
        gauge_layout.addWidget(self.throttle_bar)

        row.addWidget(gauge_box, stretch=1)

        group_layout.addLayout(row)
        self.group_box.setLayout(group_layout)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0,0,0,0)
        outer.addWidget(self.group_box)
        self.setLayout(outer)

    def refresh_controls(self) -> None:
        """Update PFD and RC gauge values from data_handler."""
        from datetime import datetime, timezone
        def safe(buf, d=0.0): return buf[-1] if buf else d

        # attitude
        roll  = safe(self.data_handler.orientation[0])
        pitch = safe(self.data_handler.orientation[1])
        yaw   = safe(self.data_handler.orientation[2])
        self.attitude.setPitchRoll(pitch, roll)
        self.heading.setHeading(yaw)

        # RC inputs (iBus PWM)
        pwm = self.data_handler.pwm_iBus  # assumes your data_handler stores it
        self.roll_bar.setValue(pwm.get('rol',1500))
        self.pitch_bar.setValue(pwm.get('pit',1500))
        self.yaw_bar.setValue(pwm.get('yaw',1500))
        self.throttle_bar.setValue(pwm.get('thr',1000))

    def updateConfig(self, new_config: Dict[str, Any]) -> None:
        self.orient_block.updateConfig(new_config)


class BatteryBlock(QWidget):
    """Group box for battery monitoring visualization."""
    def __init__(self, data_handler: Any) -> None:
        super().__init__()
        self.data_handler = data_handler
        self.initUI()

    def initUI(self) -> None:
        self.group_box = QGroupBox("Battery Status")
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(2,2,2,2)
        group_layout.setSpacing(2)
        self.group_box.setLayout(group_layout)
        self.battery_block = BatteryMonitoring(self.data_handler)
        group_layout.addWidget(self.battery_block)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)

    def updateConfig(self, new_config: dict) -> None:
        self.battery_block.updateConfig(new_config)

class DroneStatusBlock(QWidget):
    """Block to display drone status information plus 3D wireframe."""
    def __init__(self, data_handler: Any) -> None:
        super().__init__()
        self.data_handler = data_handler
        self.initUI()

        # Timer to refresh both grid and 3D model
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(50)  # 20 Hz

    def initUI(self) -> None:
        group_box = QGroupBox("Drone Status")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(4,4,4,4)

        # — 3D wireframe view —
        self.gl_view = GLViewWidget()
        self.gl_view.setBackgroundColor(pg.mkColor(30,30,30))
        self.gl_view.opts['distance'] = 20

        # build the drone arms
        arms = []
        # front arm + arrow
        arms.append(GLLinePlotItem(
            pos=np.array([[0,0,0],[0,1,0]], dtype=np.float32),
            color=(0,1,0,1), width=3))
        arms.append(GLLinePlotItem(
            pos=np.array([[0,1,0],[0,1.2,0]], dtype=np.float32),
            color=(1,1,1,1), width=3))
        # back
        arms.append(GLLinePlotItem(
            pos=np.array([[0,0,0],[0,-1,0]], dtype=np.float32),
            color=(1,0,0,1), width=3))
        # left/right
        arms.append(GLLinePlotItem(
            pos=np.array([[0,0,0],[-1,0,0]], dtype=np.float32),
            color=(0,0,1,1), width=3))
        arms.append(GLLinePlotItem(
            pos=np.array([[0,0,0],[1,0,0]], dtype=np.float32),
            color=(0,0,1,1), width=3))

        self.drone_lines = arms
        for item in self.drone_lines:
            self.gl_view.addItem(item)

       

        # — Status grid —
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)

        gps_label = QLabel("GPS")
        gps_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        grid.addWidget(gps_label, 0, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignLeft)

        grid.addWidget(QLabel("Latitude:"), 1, 0)
        self.lat_value = QLabel("N/A")
        grid.addWidget(self.lat_value, 1, 1)
        grid.addWidget(QLabel("Longitude:"), 1, 2)
        self.lon_value = QLabel("N/A")
        grid.addWidget(self.lon_value, 1, 3)

        grid.addWidget(QLabel("Altitude (m):"), 2, 0)
        self.alt_value = QLabel("N/A")
        grid.addWidget(self.alt_value, 2, 1)

        grid.addWidget(QLabel("UTC Time:"), 3, 0)
        self.utc_value = QLabel("N/A")
        grid.addWidget(self.utc_value, 3, 1, 1, 3)

        grid.addWidget(QLabel("Speed Over Ground (m/s):"), 4, 0)
        self.speed_value = QLabel("N/A")
        grid.addWidget(self.speed_value, 4, 1)
        grid.addWidget(QLabel("Course (°):"), 4, 2)
        self.course_value = QLabel("N/A")
        grid.addWidget(self.course_value, 4, 3)

        grid.addWidget(QLabel("Fix Quality:"), 5, 0)
        self.fix_value = QLabel("N/A")
        grid.addWidget(self.fix_value, 5, 1)
        grid.addWidget(QLabel("Satellites:"), 5, 2)
        self.sat_value = QLabel("N/A")
        grid.addWidget(self.sat_value, 5, 3)

        main_layout.addLayout(grid, stretch=1)
        main_layout.addWidget(self.gl_view, stretch=3)
        group_box.setLayout(main_layout)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0,0,0,0)
        outer.addWidget(group_box)
        self.setLayout(outer)

    def refresh_status(self) -> None:
        from datetime import datetime, timezone
        def safe(buf, d=0.0): return buf[-1] if buf else d

        # update grid values
        self.lat_value.setText(f"{self.data_handler.gps_lat:.6f}")
        self.lon_value.setText(f"{self.data_handler.gps_lon:.6f}")
        self.alt_value.setText(f"{self.data_handler.gps_alt:.2f}")
        self.utc_value.setText(
    datetime.fromtimestamp(
        self.data_handler.time_buffer[-1]  # Use actual timestamp from buffer
    ).strftime("%Y-%m-%d %H:%M:%S")
) if self.data_handler.time_buffer else "N/A"
        self.speed_value.setText(f"{self.data_handler.speed_over_ground:.2f}")
        self.course_value.setText(f"{self.data_handler.course:.2f}")
        self.fix_value.setText(str(self.data_handler.gps_fix))
        self.sat_value.setText(str(self.data_handler.num_satellites))

        # update 3D orientation
        roll  = safe(self.data_handler.orientation[0])
        pitch = safe(self.data_handler.orientation[1])
        yaw   = safe(self.data_handler.orientation[2])

        for item in self.drone_lines:
            item.resetTransform()
            item.rotate(yaw,   0,0,1)
            item.rotate(pitch, 0,1,0)
            item.rotate(roll,  1,0,0)
class DisplayWidget(QWidget):
    """Combined display widget for telemetry data with adjustable panel sizes both horizontally and vertically."""
    def __init__(self, data_handler: Any) -> None:
        super().__init__()
        self.data_handler = data_handler
        self.initUI()

        # redraw everything whenever new data arrives
        self.data_handler.dataUpdated.connect(self._refresh_all)

    def initUI(self) -> None:
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create the main horizontal splitter
        main_hsplit = QSplitter(Qt.Orientation.Horizontal)
        main_hsplit.setHandleWidth(5)
        main_hsplit.setChildrenCollapsible(False)  # Prevent widgets from being collapsed to zero size
        
        # Left column: Motor currents
        self.motor_block = MotorBlock(self.data_handler)
        self.motor_block.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_hsplit.addWidget(self.motor_block)
        
        # Middle column: Orientation & Altitude
        self.orientation_block = OrientationAltitudeBlock(self.data_handler)
        self.orientation_block.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_hsplit.addWidget(self.orientation_block)
        
        # Right column: Vertical split with Drone Status and Battery
        right_vsplit = QSplitter(Qt.Orientation.Vertical)
        right_vsplit.setHandleWidth(5)
        right_vsplit.setChildrenCollapsible(False)
        
        # Drone status
        self.drone_status = DroneStatusBlock(self.data_handler)
        self.drone_status.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_vsplit.addWidget(self.drone_status)
        
        # Battery
        self.battery = BatteryBlock(self.data_handler)
        self.battery.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_vsplit.addWidget(self.battery)
        
        main_hsplit.addWidget(right_vsplit)
        
        # Set initial sizes for both splitters
        main_hsplit.setSizes([300, 300, 250])
        right_vsplit.setSizes([350, 250])
        
        # Add the main horizontal splitter to the layout
        main_layout.addWidget(main_hsplit)
        self.setLayout(main_layout)

    def _refresh_all(self):
        print("Refresh called!")  # Debug line
        print(f"Motor data length: {len(self.data_handler.motor_currents[0])}")  # Debug line
        print(f"Time data length: {len(self.data_handler.time_buffer)}")  # Debug line
        
        try:
            self.motor_block.motor_block.update_plot()
            self.orientation_block.orient_block.update_plot()
            self.battery.battery_block.update_plot()
            self.drone_status.refresh_status()
            print("Refresh completed successfully!")  # Debug line
        except Exception as e:
            print(f"Refresh error: {e}")