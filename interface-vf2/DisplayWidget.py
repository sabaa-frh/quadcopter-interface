#displaywidget.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QSizePolicy,QGridLayout,QFrame
from PyQt6.QtCore import QTimer,Qt
from blocks import MotorCurrentVisualization
from blocks import OrientationAltitudeVisualization
from blocks import BatteryMonitoring
from PyQt6.QtGui import QFont
from datetime import datetime, timezone

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

    def updateConfig(self, new_config):
        self.motor_block.updateConfig(new_config)
    

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
    def updateConfig(self, new_config):
        self.orient_block.updateConfig(new_config)


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
    def updateConfig(self, new_config):
        self.battery_block.updateConfig(new_config)
    


#######################################################
# New DroneStatusBlock – shows status/error messages
#######################################################
class DroneStatusBlock(QWidget):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler 
        self.initUI()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(1000)
        
    def initUI(self):
        # Create a group box for Drone Status.
        group_box = QGroupBox("Drone Status")
        group_box.setStyleSheet("QGroupBox")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(2)

        grid = QGridLayout()
        grid.setSpacing(5)

        gps_label = QLabel("  GPS")
        gps_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        grid.addWidget(gps_label, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        
        header_font = QFont()
        header_font.setBold(True)
        
        # --- Position Information ---
        grid.addWidget(QLabel("Latitude:"), 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.lat_value = QLabel("N/A")
        grid.addWidget(self.lat_value, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        
        grid.addWidget(QLabel("Longitude:"), 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.lon_value = QLabel("N/A")
        grid.addWidget(self.lon_value, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)
        
        grid.addWidget(QLabel("Altitude (m):"), 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.alt_value = QLabel("N/A")
        grid.addWidget(self.alt_value, 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # --- Time Data ---
        grid.addWidget(QLabel("UTC Time & Date:"), 3, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.utc_value = QLabel("N/A")
        grid.addWidget(self.utc_value, 3, 1, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # --- Movement and Direction ---
        grid.addWidget(QLabel("Speed Over Ground (m/s):"), 4, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.speed_value = QLabel("N/A")
        grid.addWidget(self.speed_value, 4, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        
        grid.addWidget(QLabel("Course (°):"), 4, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.course_value = QLabel("N/A")
        grid.addWidget(self.course_value, 4, 3, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # --- Satellite and Fix Quality Data ---
        grid.addWidget(QLabel("Fix Quality:"), 5, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.fix_value = QLabel("N/A")
        grid.addWidget(self.fix_value, 5, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        
        grid.addWidget(QLabel("Satellites:"), 5, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.sat_value = QLabel("N/A")
        grid.addWidget(self.sat_value, 5, 3, alignment=Qt.AlignmentFlag.AlignLeft)
        
        main_layout.addLayout(grid)
        main_layout.addStretch(1)

        group_box.setLayout(main_layout)
        outer_layout = QVBoxLayout()
        outer_layout.addWidget(group_box)
        self.setLayout(outer_layout)
        
    def refresh_status(self):
        # Get current UTC time.
        utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        lat = self.data_handler.gps_lat
        lon = self.data_handler.gps_lon
        alt = self.data_handler.gps_alt
        speed = getattr(self.data_handler, "speed_over_ground", 0.0)
        course = getattr(self.data_handler, "course", 0.0)
        fix = getattr(self.data_handler, "gps_fix", "N/A")
        satellites = getattr(self.data_handler, "num_satellites", 0)
        
        self.lat_value.setText(f"{lat:.6f}")
        self.lon_value.setText(f"{lon:.6f}")
        self.alt_value.setText(f"{alt:.2f}")
        self.utc_value.setText(utc_now)
        self.speed_value.setText(f"{speed:.2f}")
        self.course_value.setText(f"{course:.2f}")
        self.fix_value.setText(str(fix))
        self.sat_value.setText(str(satellites))
        

    

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
        
        # Third column 
        third_column = QVBoxLayout()
        third_column.setContentsMargins(2,2,2,2)
        third_column.setSpacing(5)
        self.drone_status = DroneStatusBlock(self.data_handler)
        self.drone_status.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        third_column.addWidget(self.drone_status,1)
        
        self.battery = BatteryBlock(self.data_handler)
        self.battery.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        third_column.addWidget(self.battery, 1)  
        
        third_widget = QWidget()
        third_widget.setLayout(third_column)
        third_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
   
        main_layout.addWidget(third_widget, 1)
        
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
            sat_count=8, 
            current_time=datetime.datetime.now().strftime("%H:%M:%S")
        )
    
    