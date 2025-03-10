#displaywidget.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QSizePolicy,QGridLayout,QFrame,QLineEdit
from PyQt6.QtCore import QTimer,Qt
from blocks import MotorCurrentVisualization
from blocks import OrientationAltitudeVisualization
from blocks import BatteryMonitoring
from PyQt6.QtGui import QFont
import datetime
# ---------------------------
# Motor Block: graph and stats inside one group box
# ---------------------------
class MotorBlock(QWidget):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler
        self.initUI()
    
    def initUI(self):
        self.group_box = QGroupBox("Motor Currents & Stats")
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(2, 2, 2, 2)
        group_layout.setSpacing(2)
        self.group_box.setLayout(group_layout)
       
        self.motor_block = MotorCurrentVisualization(self.data_handler)
        self.setStyleSheet("background-color: white;")
        group_layout.addWidget(self.motor_block, 0, Qt.AlignmentFlag.AlignTop)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)
    
    def update(self):
        self.motor_block.update_plot()


# ---------------------------
# Orientation Block: graph and stats inside one group box
# ---------------------------
class OrientationAltitudeBlock(QWidget):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler
        self.initUI()
    
    def initUI(self):
        self.group_box = QGroupBox("Orientation & Altitude & Stats")
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(2, 2, 2, 2)
        group_layout.setSpacing(2)
        self.group_box.setLayout(group_layout)
        
        self.orient_block = OrientationAltitudeVisualization(self.data_handler)
        self.setStyleSheet("background-color: white;")
        group_layout.addWidget(self.orient_block, 0, Qt.AlignmentFlag.AlignTop)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)
    
    def update(self):
        self.orient_block.update_plot()


# ---------------------------
# Battery Block: graph and stats inside one group box
# ---------------------------
class BatteryBlock(QWidget):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler
        self.initUI()
        
    def initUI(self):
        self.group_box = QGroupBox("Battery Status")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(2)
        group_layout.setContentsMargins(2, 2, 2, 2)
        self.group_box.setLayout(group_layout)

        
        self.battery_block = BatteryMonitoring(self.data_handler)
        self.setStyleSheet("background-color: white;")
        group_layout.addWidget(self.battery_block)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)
        
    def update(self):
        self.battery_block.update_plot()


#######################################################
# New DroneStatusBlock – shows status/error messages
#######################################################
class DroneStatusBlock(QWidget):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler  # Save the data handler reference.
        self.initUI()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(1000)

    def initUI(self):
        group_box = QGroupBox("Drone Status")
        group_box.setStyleSheet("QGroupBox { margin-top: 10px; }")
 
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(5)

        gps_layout = QGridLayout()
        gps_layout.setContentsMargins(0,20,0,0)
        gps_layout.setSpacing(2)

        self.gps_led = QLabel(self)
        self.gps_led.setFixedSize(12, 12)
        self.gps_led.setStyleSheet("background-color: red; border-radius: 6px;")
        
        gps_label = QLabel("  GPS")
        gps_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        gps_layout.addWidget(self.gps_led, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        gps_layout.addWidget(gps_label, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
   
        header_font = QFont()
        header_font.setBold(True)
        
        long_header = QLabel("Long")
        alt_header = QLabel("Alt")
        lat_header = QLabel("Lat")
        
        long_header.setFont(header_font)
        alt_header.setFont(header_font)
        lat_header.setFont(header_font)
        
        
        gps_layout.addWidget(long_header, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        gps_layout.addWidget(alt_header, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        gps_layout.addWidget(lat_header, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        

        self.long_value = QLabel("N/A")
        self.alt_value = QLabel("N/A")
        self.lat_value = QLabel("N/A")
        
        gps_layout.addWidget(self.long_value, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        gps_layout.addWidget(self.alt_value, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        gps_layout.addWidget(self.lat_value, 2, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        
        sat_header = QLabel("Satellites")
        time_header = QLabel("Time")
        
        sat_header.setFont(header_font)
        time_header.setFont(header_font)

        gps_layout.addWidget(sat_header, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        gps_layout.addWidget(time_header, 3, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.sat_value = QLabel("N/A")
        self.time_value = QLabel("N/A")
        gps_layout.addWidget(self.sat_value, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        gps_layout.addWidget(self.time_value, 4, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(gps_layout)
       
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Plain)
        main_layout.addWidget(separator)
        
        main_layout.addStretch(1)
        group_box.setLayout(main_layout)
        
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0,0,0,0)
        outer_layout.setSpacing(0)
        outer_layout.addWidget(group_box)
        self.setLayout(outer_layout)

    def refresh_status(self):
        # Get the current time for display.
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        # Call update_gps_status using data from the data handler.
        self.update_gps_status(
            connected=self.data_handler.gps_connected,
            lat=self.data_handler.gps_lat,
            lon=self.data_handler.gps_lon,
            alt=self.data_handler.gps_alt,
            fix_type=self.data_handler.gps_fix,
            sat_count=8,  # Or update with real satellite count if available.
            current_time=current_time
        )

    def update_gps_status(self, connected, lat, lon, alt, fix_type, sat_count, current_time):
        if connected:
            self.gps_led.setStyleSheet("background-color: green; border-radius: 6px;")
        else:
            self.gps_led.setStyleSheet("background-color: red; border-radius: 6px;")
        self.long_value.setText(f"{lon:.6f}")
        self.alt_value.setText(f"{alt:.2f} m")
        self.lat_value.setText(f"{lat:.6f}")
        self.sat_value.setText(str(sat_count))
        self.time_value.setText(current_time)

# ---------------------------
# Combined Display Widget
# ---------------------------
class DisplayWidget(QWidget):
    def __init__(self, data_handler):
        super().__init__()
       
        self.data_handler = data_handler
        self.initUI()
       
    def initUI(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(2)
        
        # First column: MotorBlock
        self.motor = MotorBlock(self.data_handler)
        self.motor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.motor, 1)  # Add stretch factor of 1
        
        # Second column: OrientationBlock
        self.orientation = OrientationAltitudeBlock(self.data_handler)
        self.orientation.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.orientation, 1)  # Add stretch factor of 1
        
        # Third column: Vertical layout with DroneStatusBlock on top and BatteryBlock underneath_v 
        third_column = QVBoxLayout()
        third_column.setContentsMargins(2,2,2,2)
        third_column.setSpacing(5)
        self.drone_status = DroneStatusBlock(self.data_handler)
        self.drone_status.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        third_column.addWidget(self.drone_status,1)
        
        self.battery = BatteryBlock(self.data_handler)
        self.battery.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        third_column.addWidget(self.battery, 1)  # Add stretch factor of 1
        
        third_widget = QWidget()
        third_widget.setLayout(third_column)
        third_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        #third_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(third_widget, 1)  # Add stretch factor of 1
        
        # Set stretch factors to ensure equal width for all columns
        main_layout.setStretch(0, 1)  # First column
        main_layout.setStretch(1, 1)  # Second column
        main_layout.setStretch(2, 1)  # Third column
        
        self.setLayout(main_layout)
        
    def update_all(self):
        self.motor.update()
        self.orientation.update()
        self.battery.update()
        self.drone_status.update_gps_status(
            connected=self.data_handler.gps_connected,
            lat=self.data_handler.gps_lat,
            lon=self.data_handler.gps_lon,
            alt=self.data_handler.gps_alt,
            fix_type=self.data_handler.gps_fix,
            sat_count=8,  # For simulation, satellites remain fixed
            current_time=datetime.datetime.now().strftime("%H:%M:%S")
        )