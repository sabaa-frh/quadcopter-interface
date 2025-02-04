import sys
import pandas as pd
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,QLabel, QGridLayout, QSizePolicy, QComboBox, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

##############################################
# Reload Block for Motor Currents & Stats
##############################################
class ReloadMotorBlock(QWidget):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.initUI()
        self.plot_data()
        
    def initUI(self):
        
        self.group_box = QGroupBox("Motor Currents & Stats")
        group_layout = QVBoxLayout()
       
        group_layout.setContentsMargins(2, 2, 2, 2)
        group_layout.setSpacing(2)
        self.group_box.setLayout(group_layout)
    
        
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.axes = self.fig.subplots(4, 1, sharex=True)
        self.fig.subplots_adjust(top=0.965,bottom=0.123,left=0.116,right=0.972,hspace=0.258,wspace=0.2)
        self.motor_lines = []
        colors = ['r', 'g', 'b', 'm']
        for i, ax in enumerate(self.axes):
            line, = ax.plot([], [], color=colors[i], label=f"Motor {i+1}")
            ax.set_ylabel("Current (A)", fontsize=6)
            ax.legend()
            self.motor_lines.append(line)
        self.axes[-1].set_xlabel("Time (s)")
        
       
        group_layout.addWidget(self.canvas)
        group_layout.addWidget(self.toolbar)
        
       
        summary_layout = QGridLayout()
        summary_layout.setSpacing(2)
        summary_layout.setContentsMargins(5, 5, 5, 5)
        headers = ["Motor",  "Min", "Max", "Avg"]
        for col, header in enumerate(headers):
            lbl = QLabel(header)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-weight: bold;")
            summary_layout.addWidget(lbl, 0, col)
        self.motor_stat_labels = []
        for i in range(4):
            motor_lbl = QLabel(f"Motor {i+1}")
            motor_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            summary_layout.addWidget(motor_lbl, i+1, 0)
            
            min_lbl = QLabel("0.00")
            max_lbl = QLabel("0.00")
            avg_lbl = QLabel("0.00")
            for lbl in ( min_lbl, max_lbl, avg_lbl):
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            summary_layout.addWidget(min_lbl, i+1, 1)
            summary_layout.addWidget(max_lbl, i+1, 2)
            summary_layout.addWidget(avg_lbl, i+1, 3)
            self.motor_stat_labels.append(( min_lbl, max_lbl, avg_lbl))
       
        
        summary_widget = QWidget()
        summary_widget.setLayout(summary_layout)
        summary_widget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        group_layout.addWidget(summary_widget, 0, Qt.AlignmentFlag.AlignTop)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)
        
    def plot_data(self):
      
        time_data = self.df["Timestamp"].tolist()
        motors = []
        for i in range(1, 5):
            motors.append(self.df[f"Motor{i}"].tolist())
  
        for i, ax in enumerate(self.axes):
            self.motor_lines[i].set_data(time_data, motors[i])
            ax.relim()
            ax.autoscale_view(scalex=False, scaley=True)
        self.canvas.draw()
       
        for i, motor_data in enumerate(motors):
            if motor_data:
              
                min_val = min(motor_data)
                max_val = max(motor_data)
                avg_val = sum(motor_data) / len(motor_data)
                min_lbl, max_lbl, avg_lbl = self.motor_stat_labels[i]
                
                min_lbl.setText(f"{min_val:.2f}")
                max_lbl.setText(f"{max_val:.2f}")
                avg_lbl.setText(f"{avg_val:.2f}")

##############################################
# Reload Block for Orientation & Altitude & Stats
##############################################
class ReloadOrientationBlock(QWidget):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.initUI()
        self.plot_data()
    
    def initUI(self):
        self.group_box = QGroupBox("Orientation & Altitude & Stats")
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(2, 2, 2, 2)
        group_layout.setSpacing(2)
        self.group_box.setLayout(group_layout)
        
       
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.axes = self.fig.subplots(4, 1, sharex=True)
        self.fig.subplots_adjust(top=0.969,bottom=0.123,left=0.154,right=0.972,hspace=0.229,wspace=0.2)
        
        self.orient_lines = []
        titles = ["Roll", "Pitch", "Yaw", "Altitude"]
        colors = ['r', 'g', 'b', 'm']
        for i, ax in enumerate(self.axes):
            line, = ax.plot([], [],color=colors[i], label=titles[i])
            ax.set_ylabel("Degrees(°)" if i < 3 else "Meters(m)", fontsize=6)
            ax.legend(fontsize=8)
            self.orient_lines.append(line)
        self.axes[-1].set_xlabel("Time (s)")
        group_layout.addWidget(self.canvas)
        group_layout.addWidget(self.toolbar)
        
       
        summary_layout = QGridLayout()
        summary_layout.setContentsMargins(2, 2, 2, 2)
        summary_layout.setSpacing(2)
        headers = ["Metric", "Min", "Max", "Avg"]
        for col, header in enumerate(headers):
            lbl = QLabel(header)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-weight: bold;")
            summary_layout.addWidget(lbl, 0, col)
        self.orient_stat_labels = []
        metrics = ["Roll", "Pitch", "Yaw", "Altitude"]
        for i, metric in enumerate(metrics):
            metric_lbl = QLabel(metric)
            metric_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            summary_layout.addWidget(metric_lbl, i+1, 0)
            
            min_lbl = QLabel("0.00")
            max_lbl = QLabel("0.00")
            avg_lbl = QLabel("0.00")
            for lbl in ( min_lbl, max_lbl, avg_lbl):
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            summary_layout.addWidget(min_lbl, i+1, 1)
            summary_layout.addWidget(max_lbl, i+1, 2)
            summary_layout.addWidget(avg_lbl, i+1, 3)
            self.orient_stat_labels.append((min_lbl, max_lbl, avg_lbl))
      
        
        summary_widget = QWidget()
        summary_widget.setLayout(summary_layout)
        summary_widget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        group_layout.addWidget(summary_widget, 0, Qt.AlignmentFlag.AlignTop)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)
    
    def plot_data(self):
        time_data = self.df["Timestamp"].tolist()
        roll = self.df["Roll"].tolist()
        pitch = self.df["Pitch"].tolist()
        yaw = self.df["Yaw"].tolist()
        altitude = self.df["Altitude"].tolist()
        data_list = [roll, pitch, yaw, altitude]
        for i, ax in enumerate(self.axes):
            self.orient_lines[i].set_data(time_data, data_list[i])
            ax.relim()
            ax.autoscale_view(scalex=False, scaley=True)
        self.canvas.draw()
    
        for i, data in enumerate(data_list):
            if data:
               
                min_val = min(data)
                max_val = max(data)
                avg_val = sum(data) / len(data)
                min_lbl, max_lbl, avg_lbl = self.orient_stat_labels[i]
                
                min_lbl.setText(f"{min_val:.2f}")
                max_lbl.setText(f"{max_val:.2f}")
                avg_lbl.setText(f"{avg_val:.2f}")

##############################################
# Reload Block for Battery & Stats
##############################################
class ReloadBatteryBlock(QWidget):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.initUI()
        self.plot_data()
        
    def initUI(self):
        self.group_box = QGroupBox("Battery & Stats")
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(2, 2, 2, 2)
        group_layout.setSpacing(2)
        self.group_box.setLayout(group_layout)
        
       
        self.fig = Figure(figsize=(5,2))
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax = self.fig.add_subplot(111)
        self.battery_line, = self.ax.plot([], [], 'm-', label="Battery Percentage")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Percentage (%)")
        self.ax.legend(fontsize=8)
        self.fig.subplots_adjust(top=0.955,bottom=0.176,left=0.179,right=0.962,hspace=0.2,wspace=0.2)
        group_layout.addWidget(self.canvas)
        group_layout.addWidget(self.toolbar)
        
      
        summary_layout = QGridLayout()
        summary_layout.setContentsMargins(2, 2, 2, 2)
        summary_layout.setSpacing(2)
        headers = ["Metric",  "Min", "Max", "Avg"]
        for col, header in enumerate(headers):
            lbl = QLabel(header)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-weight: bold;")
            summary_layout.addWidget(lbl, 0, col)
        self.battery_stat_labels = []
        metrics = ["Voltage", "Percentage"]
        for i, metric in enumerate(metrics):
            metric_lbl = QLabel(metric)
            metric_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            summary_layout.addWidget(metric_lbl, i+1, 0)
            
            min_lbl = QLabel("0.00")
            max_lbl = QLabel("0.00")
            avg_lbl = QLabel("0.00")
            for lbl in ( min_lbl, max_lbl, avg_lbl):
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            summary_layout.addWidget(min_lbl, i+1, 1)
            summary_layout.addWidget(max_lbl, i+1, 2)
            summary_layout.addWidget(avg_lbl, i+1, 3)
            self.battery_stat_labels.append(( min_lbl, max_lbl, avg_lbl))
 
        
        summary_widget = QWidget()
        summary_widget.setLayout(summary_layout)
        summary_widget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        group_layout.addWidget(summary_widget, 0, Qt.AlignmentFlag.AlignTop)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)
    
    def plot_data(self):
        time_data = self.df["Timestamp"].tolist()
        percentage = self.df["Percentage"].tolist()
        self.battery_line.set_data(time_data, percentage)
        self.ax.relim()
        self.ax.autoscale_view(scalex=False, scaley=True)
        self.canvas.draw()
  
        voltage = self.df["Voltage"].tolist()
        if voltage:
            
            min_val = min(voltage)
            max_val = max(voltage)
            avg_val = sum(voltage) / len(voltage)
            min_lbl, max_lbl, avg_lbl = self.battery_stat_labels[0]
            
            min_lbl.setText(f"{min_val:.2f}")
            max_lbl.setText(f"{max_val:.2f}")
            avg_lbl.setText(f"{avg_val:.2f}")
        if percentage:
            
            min_val = min(percentage)
            max_val = max(percentage)
            avg_val = sum(percentage) / len(percentage)
            min_lbl, max_lbl, avg_lbl = self.battery_stat_labels[1]
            
            min_lbl.setText(f"{min_val:.2f}")
            max_lbl.setText(f"{max_val:.2f}")
            avg_lbl.setText(f"{avg_val:.2f}")

##############################################
# Combined Reload Display Widget
##############################################
class CombinedReloadDisplayWidget(QWidget):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.initUI()
        
    def initUI(self):
        layout = QHBoxLayout()
        self.reload_motor = ReloadMotorBlock(self.df)
        self.reload_orientation = ReloadOrientationBlock(self.df)
        self.reload_battery = ReloadBatteryBlock(self.df)
        layout.addWidget(self.reload_motor)
        layout.addWidget(self.reload_orientation)
        layout.addWidget(self.reload_battery)
        self.setLayout(layout)

##############################################
# ReloadWindow Main Class
##############################################
class ReloadWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reload Data")
        self.setGeometry(150, 150, 1400, 1000)
        self.initUI()
    
    def initUI(self):
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
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            self.df_full = None
        
        if self.df_full is not None:
            self.combined_reload_display = CombinedReloadDisplayWidget(self.df_full)
            main_layout.addWidget(self.combined_reload_display)
        else:
            error_label = QLabel("Failed to load data.")
            main_layout.addWidget(error_label)
    
    def set_partial_fields_enabled(self, time_abs, time_rel, index_abs, index_rel):
        self.start_time_edit.setEnabled(time_abs)
        self.end_time_edit.setEnabled(time_abs)
        self.last_time_edit.setEnabled(time_rel)
        self.start_index_edit.setEnabled(index_abs)
        self.end_index_edit.setEnabled(index_abs)
        self.last_points_edit.setEnabled(index_rel)
    
    def reload_mode_changed(self, mode):
    
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
    
    def apply_reload(self):
        if self.df_full is None:
            return
        
        mode = self.mode_dropdown.currentText()
        if mode == "Full Reload":
            df_filtered = self.df_full.copy()
        elif mode == "Partial Reload (Time Range)":
            try:
                start_time = float(self.start_time_edit.text())
                end_time = float(self.end_time_edit.text())
            except ValueError:
                print("Invalid time values. Please enter numeric values.")
                return
            df_filtered = self.df_full[(self.df_full["Timestamp"] >= start_time) & (self.df_full["Timestamp"] <= end_time)]
        elif mode == "Partial Reload (Last X Seconds)":
            try:
                last_seconds = float(self.last_time_edit.text())
            except ValueError:
                print("Invalid time value. Please enter a numeric value.")
                return
           
            max_time = self.df_full["Timestamp"].max()
            df_filtered = self.df_full[self.df_full["Timestamp"] >= (max_time - last_seconds)]
        elif mode == "Partial Reload (Data Point Range)":
            try:
                start_idx = int(self.start_index_edit.text())
                end_idx = int(self.end_index_edit.text())
            except ValueError:
                print("Invalid index values. Please enter integer values.")
                return
            df_filtered = self.df_full.iloc[start_idx:end_idx]
        elif mode == "Partial Reload (Last X Data Points)":
            try:
                last_points = int(self.last_points_edit.text())
            except ValueError:
                print("Invalid data points value. Please enter an integer value.")
                return
            df_filtered = self.df_full.iloc[-last_points:]
        else:
            df_filtered = self.df_full.copy()
        
    
        central_layout = self.centralWidget().layout()
        if hasattr(self, "combined_reload_display"):
            central_layout.removeWidget(self.combined_reload_display)
            self.combined_reload_display.deleteLater()
        
        self.combined_reload_display = CombinedReloadDisplayWidget(df_filtered)
        central_layout.addWidget(self.combined_reload_display)

