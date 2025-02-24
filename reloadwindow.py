#reloadwindow.py

import pandas as pd
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,QLabel, QGridLayout, QSizePolicy, QComboBox, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import gridspec
from datetime import datetime
from matplotlib.dates import DateFormatter
from matplotlib.patches import Rectangle
from matplotlib import dates as mdates


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
        
        # Create a grid layout for interleaving graph and stats
        spec = gridspec.GridSpec(8, 1, height_ratios=[3, 1, 3, 1, 3, 1, 3, 1])
        self.fig.subplots_adjust(top=0.947,bottom=0.0,left=0.107,right=0.984,hspace=0.945,wspace=0.2)
        
        self.motor_lines = []
        self.stats_labels = []
        colors = ['r', 'g', 'b', 'm']
        
        for i in range(4):
            # Motor Current Graph
            ax = self.fig.add_subplot(spec[i * 2])
            ax.set_ylabel("Current (A)", fontsize=6)
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
            line, = ax.plot([], [], color=colors[i], label=f"Motor {i+1}")
            ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=1)
            
            if i < 3:
                ax.set_xticklabels([])
                
            self.motor_lines.append(line)
            
            # Stats Box Underneath Each Graph
            stats_ax = self.fig.add_subplot(spec[i * 2 + 1])
            stats_ax.axis("off")
            rect = Rectangle((0, 0), 1, 1, transform=stats_ax.transAxes, edgecolor='white', 
                             facecolor='white', lw=2, alpha=0.3)
            stats_ax.add_patch(rect)
            
            avg_lbl = stats_ax.text(0.1, 0.6, "Avg: 0.00 A", fontsize=9, 
                                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
            min_lbl = stats_ax.text(0.4, 0.6, "Min: 0.00 A", fontsize=9, 
                                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
            max_lbl = stats_ax.text(0.7, 0.6, "Max: 0.00 A", fontsize=9, 
                                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
            
            self.stats_labels.append((avg_lbl, min_lbl, max_lbl))
        
        group_layout.addWidget(self.canvas)
        group_layout.addWidget(self.toolbar)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)
    
    def plot_data(self):
        time_data = self.df["Timestamp"].tolist()
        motors = [self.df[f"Motor{i+1}"].tolist() for i in range(4)]  # Extract data for all 4 motors

        for i in range(4):  # Loop through all motors
            ax = self.fig.axes[i * 2]  # Ensure correct subplot selection (0, 2, 4, 6)
            ax.clear()  # Clear previous data to avoid overwriting issues
            ax.set_ylabel("Current (A)", fontsize=6)
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
            
            # Ensure we have valid time and motor data before plotting
            if time_data and motors[i]:  
                ax.plot(time_data, motors[i], label=f"Motor {i+1}", color=['r', 'g', 'b', 'm'][i])  
                ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=1)
                ax.relim()
                ax.autoscale_view(scalex=False, scaley=True)
                
                ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=8))
        # Update the stats for each motor
        for i in range(4):
            if motors[i]:  
                avg_val = sum(motors[i]) / len(motors[i])
                min_val = min(motors[i])
                max_val = max(motors[i])

                avg_lbl, min_lbl, max_lbl = self.stats_labels[i]
                avg_lbl.set_text(f"Avg: {avg_val:.2f} A")
                min_lbl.set_text(f"Min: {min_val:.2f} A")
                max_lbl.set_text(f"Max: {max_val:.2f} A")

        self.canvas.draw()
##############################################
# Reload Block for Orientation & Altitude & Stats
##############################################
class ReloadOrientationBlock(QWidget):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.titles = ["Roll", "Pitch", "Yaw", "Altitude"]
        self.colors = ['r', 'g', 'b', 'm']
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
        
        # Create a grid layout for interleaving graph and stats
        spec = gridspec.GridSpec(8, 1, height_ratios=[3, 1, 3, 1, 3, 1, 3, 1])
        self.fig.subplots_adjust(top=0.947,
bottom=0.0,
left=0.132,
right=0.984,
hspace=0.945,
wspace=0.2)
        
        self.orient_lines = []
        self.stats_labels = []
        titles = ["Roll", "Pitch", "Yaw", "Altitude"]
        colors = ['r', 'g', 'b', 'm']
        
        for i in range(4):
            # Orientation Graphs
            ax = self.fig.add_subplot(spec[i * 2])
            ax.set_ylabel("Degrees(°)" if i < 3 else "Meters(m)", fontsize=6)
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
            line, = ax.plot([], [], color=colors[i], label=titles[i])
            ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=1)
            
            if i < 3:
                ax.set_xticklabels([])
                
            self.orient_lines.append(line)
            
            # Stats Box Underneath Each Graph
            stats_ax = self.fig.add_subplot(spec[i * 2 + 1])
            stats_ax.axis("off")
            rect = Rectangle((0, 0), 1, 1, transform=stats_ax.transAxes, edgecolor='white', 
                             facecolor='white', lw=2, alpha=0.3)
            stats_ax.add_patch(rect)
            
            avg_lbl = stats_ax.text(0.1, 0.6, "Avg: 0.00°", fontsize=9, 
                                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
            min_lbl = stats_ax.text(0.4, 0.6, "Min: 0.00°", fontsize=9, 
                                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
            max_lbl = stats_ax.text(0.7, 0.6, "Max: 0.00°", fontsize=9, 
                                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
            
            self.stats_labels.append((avg_lbl, min_lbl, max_lbl))
        
        group_layout.addWidget(self.canvas)
        group_layout.addWidget(self.toolbar)
        
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
    
        for i, ax in enumerate(self.fig.axes[::2]):
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
            ax.clear()
            ax.set_ylabel("Degrees(°)" if i < 3 else "Meters(m)", fontsize=6)
    
            if time_data and data_list[i]:
                ax.plot(time_data, data_list[i], label=self.titles[i], color=self.colors[i])
                ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=1)
                ax.relim()
                ax.autoscale_view(scalex=False, scaley=True)
                ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=8))
        
        for i, data in enumerate(data_list):
            if data:
                avg_val = sum(data) / len(data)
                min_val = min(data)
                max_val = max(data)
                avg_lbl, min_lbl, max_lbl = self.stats_labels[i]
                avg_lbl.set_text(f"Avg: {avg_val:.2f}°" if i < 3 else f"Avg: {avg_val:.2f}m")
                min_lbl.set_text(f"Min: {min_val:.2f}°" if i < 3 else f"Min: {min_val:.2f}m")
                max_lbl.set_text(f"Max: {max_val:.2f}°" if i < 3 else f"Max: {max_val:.2f}m")
        
        self.canvas.draw()

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
    
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Create a grid layout for interleaving graph and stats
        spec = gridspec.GridSpec(3, 1, height_ratios=[3, 1, 1])
        self.fig.subplots_adjust(top=0.955, bottom=0.1, left=0.179, right=0.962, hspace=0.5, wspace=0.2)
        
        # Battery Graph
        self.ax = self.fig.add_subplot(spec[0])
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Battery (%)")
        self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        self.battery_line, = self.ax.plot([], [], 'm-', label="Battery Percentage")
        self.ax.legend()
        
        # Average Value Box
        stats_ax1 = self.fig.add_subplot(spec[1])
        stats_ax1.axis("off")
        self.avg_value_label = stats_ax1.text(0.5, 0.5, "Avg: 0.00%", fontsize=10, ha='center',
                                              bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.7'))
        
        # Min & Max Values Box
        stats_ax2 = self.fig.add_subplot(spec[2])
        stats_ax2.axis("off")
        self.min_value_label = stats_ax2.text(0.3, 0.5, "Min: 0.00%", fontsize=9, ha='center',
                                              bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
        self.max_value_label = stats_ax2.text(0.7, 0.5, "Max: 0.00%", fontsize=9, ha='center',
                                              bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
        
        group_layout.addWidget(self.canvas)
        group_layout.addWidget(self.toolbar)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)
    
    def plot_data(self):
        time_data = self.df["Timestamp"].tolist()
        percentage = self.df["Percentage"].tolist()
        
        if time_data and percentage:
            self.battery_line.set_data(time_data, percentage)
            self.ax.relim()
            self.ax.autoscale_view(scalex=False, scaley=True)
            
            max_time = max(time_data)
            min_time = max_time - pd.Timedelta(seconds=20)
            self.ax.set_xlim(min_time, max_time)
        
        # Compute stats
        if percentage:
            avg_val = sum(percentage) / len(percentage)
            min_val = min(percentage)
            max_val = max(percentage)
            self.avg_value_label.set_text(f"Avg: {avg_val:.2f}%")
            self.min_value_label.set_text(f"Min: {min_val:.2f}%")
            self.max_value_label.set_text(f"Max: {max_val:.2f}%")
        
        self.canvas.draw()

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
            self.df_full["Timestamp"] = pd.to_datetime(self.df_full["Timestamp"], format="%Y-%m-%d %H:%M:%S.%f")
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
        if self.df_full is None or self.df_full.empty:
            return

        mode = self.mode_dropdown.currentText()
        if mode == "Full Reload":
            df_filtered = self.df_full.copy()
        elif mode == "Partial Reload (Time Range)":
            try:
                # Try to parse start and end times with milliseconds
                start_time_input = datetime.strptime(self.start_time_edit.text(), "%H:%M:%S.%f")
            except ValueError:
                try:
                    # Fallback: parse without milliseconds
                    start_time_input = datetime.strptime(self.start_time_edit.text(), "%H:%M:%S")
                except ValueError:
                    print("Invalid start time format. Use HH:MM:SS or HH:MM:SS.mmm")
                    return

            try:
                end_time_input = datetime.strptime(self.end_time_edit.text(), "%H:%M:%S.%f")
            except ValueError:
                try:
                    end_time_input = datetime.strptime(self.end_time_edit.text(), "%H:%M:%S")
                except ValueError:
                    print("Invalid end time format. Use HH:MM:SS or HH:MM:SS.mmm")
                    return
            base_date = self.df_full["Timestamp"].min().date()
            start_time = datetime.combine(base_date, start_time_input.time())
            end_time = datetime.combine(base_date, end_time_input.time())

            df_filtered = self.df_full[
                (self.df_full["Timestamp"] >= start_time) &
                (self.df_full["Timestamp"] <= end_time)
            ]
        elif mode == "Partial Reload (Last X Seconds)":
            try:
                last_seconds = float(self.last_time_edit.text())
            except ValueError:
                print("Invalid time value. Please enter a numeric value.")
                return
            max_time = self.df_full["Timestamp"].max()
            start_time = max_time - pd.Timedelta(seconds=last_seconds)
            df_filtered = self.df_full[self.df_full["Timestamp"] >= start_time]
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

        # Update the display widget
        central_layout = self.centralWidget().layout()
        if hasattr(self, "combined_reload_display"):
            central_layout.removeWidget(self.combined_reload_display)
            self.combined_reload_display.deleteLater()

        self.combined_reload_display = CombinedReloadDisplayWidget(df_filtered)
        central_layout.addWidget(self.combined_reload_display)

