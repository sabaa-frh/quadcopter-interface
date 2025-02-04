from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QGridLayout, QSizePolicy
from PyQt6.QtCore import Qt
from blocks import MotorCurrentVisualization
from blocks import OrientationAltitudeVisualization
from blocks import BatteryMonitoring

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
        group_layout.setSpacing(2)
        group_layout.setContentsMargins(2, 2, 2, 2)
        self.group_box.setLayout(group_layout)
        
      
        self.motor_block = MotorCurrentVisualization(self.data_handler)
        self.motor_block.setFixedHeight(self.motor_block.sizeHint().height())
        group_layout.addWidget(self.motor_block, 0, Qt.AlignmentFlag.AlignTop)
        
      
        self.motor_block.timer.timeout.connect(self.update_summary)
        
       
        summary_layout = QGridLayout()
        summary_layout.setSpacing(2)
        summary_layout.setContentsMargins(5, 5, 5, 5)
        headers = ["Motor", "Value", "Min", "Max", "Avg"]
        for col, header in enumerate(headers):
            lbl = QLabel(header)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-weight: bold;")
            summary_layout.addWidget(lbl, 0, col)
        
        self.motor_stat_labels = []  # List of tuples: (value, min, max, avg)
        for i in range(4):
            motor_lbl = QLabel(f"Motor {i+1}")
            motor_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            summary_layout.addWidget(motor_lbl, i+1, 0)
            value_lbl = QLabel("0.00")
            min_lbl = QLabel("0.00")
            max_lbl = QLabel("0.00")
            avg_lbl = QLabel("0.00")
            for lbl in (value_lbl, min_lbl, max_lbl, avg_lbl):
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            summary_layout.addWidget(value_lbl, i+1, 1)
            summary_layout.addWidget(min_lbl, i+1, 2)
            summary_layout.addWidget(max_lbl, i+1, 3)
            summary_layout.addWidget(avg_lbl, i+1, 4)
            self.motor_stat_labels.append((value_lbl, min_lbl, max_lbl, avg_lbl))
        
        # Wrap the summary grid in a container widget
        summary_widget = QWidget()
        summary_widget.setLayout(summary_layout)
        summary_widget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        group_layout.addWidget(summary_widget, 0, Qt.AlignmentFlag.AlignTop)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)
    
    def update_summary(self):
       
        for i, motor_deque in enumerate(self.data_handler.motor_currents):
            if motor_deque:
                values = list(motor_deque)
                current = values[-1]
                min_val = min(values)
                max_val = max(values)
                avg_val = sum(values) / len(values)
                value_lbl, min_lbl, max_lbl, avg_lbl = self.motor_stat_labels[i]
                value_lbl.setText(f"{current:.2f}")
                min_lbl.setText(f"{min_val:.2f}")
                max_lbl.setText(f"{max_val:.2f}")
                avg_lbl.setText(f"{avg_val:.2f}")
    
    def update(self):
        self.motor_block.update_plot()
        self.update_summary()

# ---------------------------
# Orientation Block: graph and stats inside one group box
# ---------------------------
class OrientationBlock(QWidget):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler
        self.initUI()
    
    def initUI(self):
        self.group_box = QGroupBox("Orientation & Altitude & Stats")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(2)
        group_layout.setContentsMargins(5, 5, 5, 5)
        self.group_box.setLayout(group_layout)
        
        self.orient_block = OrientationAltitudeVisualization(self.data_handler)
        self.orient_block.setFixedHeight(self.orient_block.sizeHint().height())
        group_layout.addWidget(self.orient_block, 0, Qt.AlignmentFlag.AlignTop)
        
       
        self.orient_block.timer.timeout.connect(self.update_summary)
        
        summary_layout = QGridLayout()
        summary_layout.setSpacing(2)
        summary_layout.setContentsMargins(5, 5, 5, 5)
        headers = ["Metric", "Value", "Min", "Max", "Avg"]
        for col, header in enumerate(headers):
            lbl = QLabel(header)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-weight: bold;")
            summary_layout.addWidget(lbl, 0, col)
        
        metrics = ["Roll", "Pitch", "Yaw", "Altitude"]
        self.orient_stat_labels = []
        for i, metric in enumerate(metrics):
            metric_lbl = QLabel(metric)
            metric_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            summary_layout.addWidget(metric_lbl, i+1, 0)
            value_lbl = QLabel("0.00")
            min_lbl = QLabel("0.00")
            max_lbl = QLabel("0.00")
            avg_lbl = QLabel("0.00")
            for lbl in (value_lbl, min_lbl, max_lbl, avg_lbl):
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            summary_layout.addWidget(value_lbl, i+1, 1)
            summary_layout.addWidget(min_lbl, i+1, 2)
            summary_layout.addWidget(max_lbl, i+1, 3)
            summary_layout.addWidget(avg_lbl, i+1, 4)
            self.orient_stat_labels.append((value_lbl, min_lbl, max_lbl, avg_lbl))
        
        summary_widget = QWidget()
        summary_widget.setLayout(summary_layout)
        summary_widget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        group_layout.addWidget(summary_widget, 0, Qt.AlignmentFlag.AlignTop)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)
    
    def update_summary(self):
       
        for i in range(3):
            if self.data_handler.orientation[i]:
                values = list(self.data_handler.orientation[i])
                current = values[-1]
                min_val = min(values)
                max_val = max(values)
                avg_val = sum(values) / len(values)
                value_lbl, min_lbl, max_lbl, avg_lbl = self.orient_stat_labels[i]
                value_lbl.setText(f"{current:.2f}")
                min_lbl.setText(f"{min_val:.2f}")
                max_lbl.setText(f"{max_val:.2f}")
                avg_lbl.setText(f"{avg_val:.2f}")
   
        if self.data_handler.altitude:
            values = list(self.data_handler.altitude)
            current = values[-1]
            min_val = min(values)
            max_val = max(values)
            avg_val = sum(values) / len(values)
            value_lbl, min_lbl, max_lbl, avg_lbl = self.orient_stat_labels[3]
            value_lbl.setText(f"{current:.2f}")
            min_lbl.setText(f"{min_val:.2f}")
            max_lbl.setText(f"{max_val:.2f}")
            avg_lbl.setText(f"{avg_val:.2f}")
    
    def update(self):
        self.orient_block.update_plot()
        self.update_summary()


# ---------------------------
# Battery Block: graph and stats inside one group box
# ---------------------------
class BatteryBlock(QWidget):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler
        self.initUI()
        
    def initUI(self):
        self.group_box = QGroupBox("Battery & Stats")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(2)
        group_layout.setContentsMargins(5, 5, 5, 5)
        self.group_box.setLayout(group_layout)
        
        self.battery_block = BatteryMonitoring(self.data_handler)
        self.battery_block.setFixedHeight(self.battery_block.sizeHint().height())
        group_layout.addWidget(self.battery_block, 0, Qt.AlignmentFlag.AlignTop)
        
      
        self.battery_block.timer.timeout.connect(self.update_summary)
        
        summary_layout = QGridLayout()
        summary_layout.setSpacing(2)
        summary_layout.setContentsMargins(5, 5, 5, 5)
        headers = ["Metric", "Value", "Min", "Max", "Avg"]
        for col, header in enumerate(headers):
            lbl = QLabel(header)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-weight: bold;")
            summary_layout.addWidget(lbl, 0, col)
            
        metrics = ["Voltage", "Percentage"]
        self.battery_stat_labels = []
        for i, metric in enumerate(metrics):
            metric_lbl = QLabel(metric)
            metric_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            summary_layout.addWidget(metric_lbl, i+1, 0)
            value_lbl = QLabel("0.00")
            min_lbl = QLabel("0.00")
            max_lbl = QLabel("0.00")
            avg_lbl = QLabel("0.00")
            for lbl in (value_lbl, min_lbl, max_lbl, avg_lbl):
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            summary_layout.addWidget(value_lbl, i+1, 1)
            summary_layout.addWidget(min_lbl, i+1, 2)
            summary_layout.addWidget(max_lbl, i+1, 3)
            summary_layout.addWidget(avg_lbl, i+1, 4)
            self.battery_stat_labels.append((value_lbl, min_lbl, max_lbl, avg_lbl))
        
        summary_widget = QWidget()
        summary_widget.setLayout(summary_layout)
        summary_widget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        group_layout.addWidget(summary_widget, 0, Qt.AlignmentFlag.AlignTop)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)
        
    def update_summary(self):
        if self.data_handler.battery_voltage:
            values = list(self.data_handler.battery_voltage)
            current = values[-1]
            min_val = min(values)
            max_val = max(values)
            avg_val = sum(values) / len(values)
            value_lbl, min_lbl, max_lbl, avg_lbl = self.battery_stat_labels[0]
            value_lbl.setText(f"{current:.2f}")
            min_lbl.setText(f"{min_val:.2f}")
            max_lbl.setText(f"{max_val:.2f}")
            avg_lbl.setText(f"{avg_val:.2f}")
        if self.data_handler.battery_percentage:
            values = list(self.data_handler.battery_percentage)
            current = values[-1]
            min_val = min(values)
            max_val = max(values)
            avg_val = sum(values) / len(values)
            value_lbl, min_lbl, max_lbl, avg_lbl = self.battery_stat_labels[1]
            value_lbl.setText(f"{current:.2f}")
            min_lbl.setText(f"{min_val:.2f}")
            max_lbl.setText(f"{max_val:.2f}")
            avg_lbl.setText(f"{avg_val:.2f}")
            
    def update(self):
        self.battery_block.update_plot()
        self.update_summary()


# ---------------------------
# Combined Display Widget
# ---------------------------
class DisplayWidget(QWidget):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler
        self.initUI()
       
        
    def initUI(self):
        layout = QHBoxLayout()
        self.motor = MotorBlock(self.data_handler)
        self.orientation = OrientationBlock(self.data_handler)
        self.battery = BatteryBlock(self.data_handler)
        layout.addWidget(self.motor)
        layout.addWidget(self.orientation)
        layout.addWidget(self.battery)
        self.setLayout(layout)
        
    def update_all(self):
        self.motor.update()
        self.orientation.update()
        self.battery.update()
