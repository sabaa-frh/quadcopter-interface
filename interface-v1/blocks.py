#blocks.py

from PyQt6.QtWidgets import QVBoxLayout,QPushButton, QWidget,QLabel, QComboBox, QHBoxLayout,QFrame,QGridLayout
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import QTimer
import pyqtgraph as pg
from pyqtgraph import DateAxisItem

from PyQt6.QtCore import QTimer
pg.setConfigOption('background', 'w')  
pg.setConfigOption('foreground', 'k')  
# ---------------------------
# Motor Block: graph 
# ---------------------------

class MotorCurrentVisualization(QWidget):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.frequency = 200
        
        
        self.titles = [f"Motor {i+1}" for i in range(4)]
        self.colors = ['#ff0000', '#00ff00', '#0000ff', '#ff00ff']  # red, green, blue, magenta
        
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Header layout with title and frequency dropdown:
        header_layout = QHBoxLayout()
        block_title = QLabel("Motor Currents")
        block_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        freq_label = QLabel("Update Frequency:")
        self.freq_dropdown = QComboBox()
        self.freq_dropdown.addItems(["200", "500", "1000", "2000"])
        self.freq_dropdown.setCurrentText("200")
        self.freq_dropdown.currentTextChanged.connect(self.set_frequency)
        header_layout.addWidget(block_title)
        header_layout.addStretch(1)
        header_layout.addWidget(freq_label)
        header_layout.addWidget(self.freq_dropdown)
        main_layout.addLayout(header_layout)

        
        self.plots = []
        self.curves = []
        self.stats_labels = [] 

        
        for i in range(4):
            section_layout = QVBoxLayout()

            legend_layout = QHBoxLayout()
            
            color_label = QLabel()
            color_label.setFixedSize(5, 5)
            color_label.setStyleSheet(
                f"background-color: {self.colors[i]};"
            )
            # The legend text 
            motor_label = QLabel(self.titles[i])
            motor_label.setStyleSheet("font-weight: bold; font-size: 12px;")
            legend_layout.addWidget(color_label)
            legend_layout.addWidget(motor_label)
            legend_layout.addStretch(1)
            section_layout.addLayout(legend_layout)

         
            date_axis = DateAxisItem(orientation='bottom')
            plot_widget = pg.PlotWidget(axisItems={'bottom': date_axis})
            plot_widget.setBackground('w') 
            plot_widget.setLabel('left', "Current (A)")
            plot_widget.setLabel('bottom', "Time")
            
            curve = plot_widget.plot([], [], pen=pg.mkPen(color=self.colors[i], width=2))
            self.plots.append(plot_widget)
            self.curves.append(curve)
            section_layout.addWidget(plot_widget)
            

            # Create a horizontal layout for stats labels:
            stats_layout = QHBoxLayout()
            #style = "background-color: #ffffff; border: 1px solid black; border-radius: 5px; padding: 2px;"
            actual_lbl = QLabel("Actual: 0.00 A")
            #actual_lbl.setStyleSheet(style)
            min_lbl = QLabel("Min: 0.00 A")
            #min_lbl.setStyleSheet(style)
            max_lbl = QLabel("Max: 0.00 A")
            #max_lbl.setStyleSheet(style)
            stats_layout.addWidget(actual_lbl)
            stats_layout.addWidget(min_lbl)
            stats_layout.addWidget(max_lbl)
            self.stats_labels.append((actual_lbl, min_lbl, max_lbl))
            section_layout.addLayout(stats_layout)
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            main_layout.addWidget(separator)

            main_layout.addLayout(section_layout)
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        total_layout = QHBoxLayout()
        self.total_current_label = QLabel("Total: 0.00 A")
        total_style = "background-color: #ffffff; border: 1px solid black; border-radius: 5px; padding: 4px; font-weight: bold;"
        self.total_current_label.setStyleSheet(total_style)
        total_layout.addStretch()
        total_layout.addWidget(self.total_current_label)
        total_layout.addStretch()
        main_layout.addLayout(total_layout)

        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def set_frequency(self, freq_str):
        self.frequency = max(200, int(freq_str))
        self.timer.setInterval(self.frequency)

    def start(self):
        self.timer.start(self.frequency)

    def stop(self):
        self.timer.stop()

    def update_plot(self):
        base_interval_ms = 200
        sampling_factor = int(round(self.frequency / base_interval_ms))
        
        x_data_full = list(self.data_handler.time_buffer)
        x_data_full = [t.timestamp() for t in x_data_full] 
        x_data = x_data_full[::sampling_factor]
        if not x_data:
            return

     
        for i in range(4):
            motor_data_full = list(self.data_handler.motor_currents[i])
            motor_data = motor_data_full[::sampling_factor]
            if not motor_data:
                continue

          
            self.curves[i].setData(x_data[:len(motor_data)], motor_data)

          
            max_time = max(x_data)
            min_time = max_time - 20  # 20-second window
            self.plots[i].setXRange(min_time, max_time)

            # Update the stats labels:
            current = motor_data[-1]
            min_val = min(motor_data)
            max_val = max(motor_data)
            actual_lbl, min_lbl, max_lbl = self.stats_labels[i]
            actual_lbl.setText(f"Actual: {current:.2f} A")
            min_lbl.setText(f"Min: {min_val:.2f} A")
            max_lbl.setText(f"Max: {max_val:.2f} A")
        total_current = 0.0
        for i in range(4):
            motor_data_full = list(self.data_handler.motor_currents[i])
            if motor_data_full:
                total_current += motor_data_full[-1]
        self.total_current_label.setText(f"Total: {total_current:.2f} A")



# ---------------------------
# Orientation Block: graph 
# ---------------------------




class OrientationAltitudeVisualization(QWidget):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.frequency = 200

      
        self.titles = ["Roll", "Pitch", "Yaw", "Altitude"]
        self.colors = ["#ff0000", "#00ff00", "#0000ff", "#808080"]  # Red, Green, Blue, Gray
        self.ylabels = ["Degrees(°)", "Degrees(°)", "Degrees(°)", "Meters(m)"]
        
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Header layout with title and update frequency selection:
        header_layout = QHBoxLayout()
        block_title = QLabel("Orientation and Altitude")
        block_title.setStyleSheet("font-weight: bold; font-size: 14px;")

        freq_label = QLabel("Update Frequency:")
        self.freq_dropdown = QComboBox()
        self.freq_dropdown.addItems(["200", "500", "1000", "2000"])
        self.freq_dropdown.setCurrentText("200")
        self.freq_dropdown.currentTextChanged.connect(self.set_frequency)

        header_layout.addWidget(block_title)
        header_layout.addStretch(1)
        header_layout.addWidget(freq_label)
        header_layout.addWidget(self.freq_dropdown)
        main_layout.addLayout(header_layout)

       
        self.plots = []
        self.curves = []
        self.stats_labels = []  # (Actual, Min, Max)

        # Create a section for each data series (Roll, Pitch, Yaw, Altitude):
        for i in range(4):
            section_layout = QVBoxLayout()

            
            legend_layout = QHBoxLayout()
            color_label = QLabel()
            color_label.setFixedSize(5, 5)
            color_label.setStyleSheet(
                f"background-color: {self.colors[i]}; "
            )
            motor_label = QLabel(self.titles[i])
            motor_label.setStyleSheet("font-weight: bold; font-size: 12px;")
            legend_layout.addWidget(color_label)
            legend_layout.addWidget(motor_label)
            legend_layout.addStretch(1)
            section_layout.addLayout(legend_layout)

            
            date_axis = DateAxisItem(orientation='bottom')
            plot_widget = pg.PlotWidget(axisItems={'bottom': date_axis})
            plot_widget.setBackground('w')  # White background
            plot_widget.setLabel('left', self.ylabels[i])
            plot_widget.setLabel('bottom', "Time")

            curve = plot_widget.plot([], [], pen=pg.mkPen(color=self.colors[i], width=2))
            self.plots.append(plot_widget)
            self.curves.append(curve)
            section_layout.addWidget(plot_widget)

            stats_layout = QHBoxLayout()
            
            actual_lbl = QLabel("Actual: 0.00" + ("°" if i < 3 else " m"))
            min_lbl = QLabel("Min: 0.00" + ("°" if i < 3 else " m"))
            max_lbl = QLabel("Max: 0.00" + ("°" if i < 3 else " m"))
            stats_layout.addWidget(actual_lbl)
            stats_layout.addWidget(min_lbl)
            stats_layout.addWidget(max_lbl)
            self.stats_labels.append((actual_lbl, min_lbl, max_lbl))

            section_layout.addLayout(stats_layout)
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            main_layout.addWidget(separator)
            main_layout.addLayout(section_layout)

        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def set_frequency(self, freq_str):
        self.frequency = max(200, int(freq_str))
        self.timer.setInterval(self.frequency)

    def start(self):
        self.timer.start(self.frequency)

    def stop(self):
        self.timer.stop()

    def update_plot(self):
        base_interval_ms = 200
        sampling_factor = int(round(self.frequency / base_interval_ms))

        x_data_full = list(self.data_handler.time_buffer)
        x_data_full = [t.timestamp() for t in x_data_full]
        x_data = x_data_full[::sampling_factor]
        if not x_data:
            return

        roll_full = list(self.data_handler.orientation[0]) if len(self.data_handler.orientation) > 0 else []
        pitch_full = list(self.data_handler.orientation[1]) if len(self.data_handler.orientation) > 1 else []
        yaw_full = list(self.data_handler.orientation[2]) if len(self.data_handler.orientation) > 2 else []
        altitude_full = list(self.data_handler.altitude) if hasattr(self.data_handler, "altitude") else []

        roll = roll_full[::sampling_factor] if roll_full else []
        pitch = pitch_full[::sampling_factor] if pitch_full else []
        yaw = yaw_full[::sampling_factor] if yaw_full else []
        altitude = altitude_full[::sampling_factor] if altitude_full else []

        data_series = [roll, pitch, yaw, altitude]

        for i in range(4):
            y_data = data_series[i]
            if not y_data:
                continue

            self.curves[i].setData(x_data[:len(y_data)], y_data)

            max_time = max(x_data)
            min_time = max_time - 20
            self.plots[i].setXRange(min_time, max_time)

            current = y_data[-1]
            min_val = min(y_data)
            max_val = max(y_data)
            actual_lbl, min_lbl, max_lbl = self.stats_labels[i]
            if i < 3:
                # Roll, Pitch, Yaw in degrees
                actual_lbl.setText(f"Actual: {current:.2f}°")
                min_lbl.setText(f"Min: {min_val:.2f}°")
                max_lbl.setText(f"Max: {max_val:.2f}°")
            else:
                # Altitude in meters
                actual_lbl.setText(f"Actual: {current:.2f} m")
                min_lbl.setText(f"Min: {min_val:.2f} m")
                max_lbl.setText(f"Max: {max_val:.2f} m")
    
# ---------------------------
# Battery Block: graph 
# ---------------------------



class BatteryMonitoring(QWidget):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.frequency = 500
        self.show_percentage = True 
        
        self.initUI()

    def initUI(self):
       
        main_layout = QVBoxLayout()

      
        header_layout = QHBoxLayout()
        block_title = QLabel("Battery Monitoring")
        block_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        freq_label = QLabel("Update Frequency:")
        self.freq_dropdown = QComboBox()
        self.freq_dropdown.addItems(["200", "500", "1000", "2000"])
        self.freq_dropdown.setCurrentText("500")
        self.freq_dropdown.currentTextChanged.connect(self.set_frequency)
        header_layout.addWidget(block_title)
        header_layout.addStretch(1)
        header_layout.addWidget(freq_label)
        header_layout.addWidget(self.freq_dropdown)
        main_layout.addLayout(header_layout)

        self.toggle_button = QPushButton("Toggle: Percentage/Voltage")
        self.toggle_button.clicked.connect(self.toggle_view)
        main_layout.addWidget(self.toggle_button)

        date_axis = DateAxisItem(orientation='bottom')
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': date_axis})
        self.plot_widget.setBackground('#ffffff') 
        self.plot_widget.setLabel('left', "Battery (%)" if self.show_percentage else "Battery (V)")
        self.plot_widget.setLabel('bottom', "Time")
       
        main_layout.addWidget(self.plot_widget)

        self.curve = self.plot_widget.plot([], [], pen='m')

        stats_layout = QGridLayout()
        self.current_value_label = QLabel("           Actual: 0.00%")
        self.min_value_label = QLabel("Min: 0.00%")
        self.max_value_label = QLabel("Max: 0.00%")
        style = "background-color: #ffffff; border: 1px solid black; border-radius: 5px; padding: 2px;"
        self.current_value_label.setStyleSheet(style)
        self.min_value_label.setStyleSheet(style)
        self.max_value_label.setStyleSheet(style)
        # Row 0: Actual spanning 2 columns
        stats_layout.addWidget(self.current_value_label, 0, 0, 1, 2)
        # Row 1: Min in column 0 and Max in column 1
        stats_layout.addWidget(self.min_value_label, 1, 0)
        stats_layout.addWidget(self.max_value_label, 1, 1)
        
        stats_outer_layout = QHBoxLayout()
        stats_outer_layout.addStretch(1)
        stats_outer_layout.addLayout(stats_layout)
        stats_outer_layout.addStretch(1)
        main_layout.addLayout(stats_outer_layout)

        self.setLayout(main_layout)
    def set_frequency(self, freq_str):
        self.frequency = int(freq_str)
        self.timer.setInterval(self.frequency)

    def start(self):
        self.timer.start(self.frequency)

    def stop(self):
        self.timer.stop()

    def toggle_view(self):
        """Toggle between Battery Percentage and Voltage display."""
        self.show_percentage = not self.show_percentage
        self.plot_widget.setLabel('left', "Battery (%)" if self.show_percentage else "Battery (V)")
        self.update_plot()

    def update_plot(self):
        """Update the battery plot and statistics using PyQtGraph."""
        base_interval_ms = 200
        sampling_factor = int(round(self.frequency / base_interval_ms))

        x_data_full = list(self.data_handler.time_buffer)
        x_data_full = [t.timestamp() for t in x_data_full]
        x_data = x_data_full[::sampling_factor]

        if self.show_percentage:
            y_data_full = list(getattr(self.data_handler, "battery_percentage", []))
        else:
            y_data_full = list(getattr(self.data_handler, "battery_voltage", []))
        y_data = y_data_full[::sampling_factor] if y_data_full else []

        if not x_data or not y_data:
            return

        self.curve.setData(x_data, y_data)

        max_time = max(x_data)
        min_time = max_time - 20  # 20 seconds window
        self.plot_widget.setXRange(min_time, max_time)

        if self.show_percentage:
            self.plot_widget.setYRange(20, 100)
            self.plot_widget.getAxis('left').setTicks([[(20, "20"), (40, "40"), (60, "60"), (80, "80"), (100, "100")]])
        else:
            self.plot_widget.setYRange(10, 14.6)
            self.plot_widget.getAxis('left').setTicks([[(10,"10"),(11.1, "11.1"),(12.6, "12.6"), (14., "14")]])

        current = y_data[-1]
        min_val = min(y_data)
        max_val = max(y_data)
        unit = "%" if self.show_percentage else "V"
        self.current_value_label.setText(f"Actual: {current:.2f}{unit}")
        self.min_value_label.setText(f"Min: {min_val:.2f}{unit}")
        self.max_value_label.setText(f"Max: {max_val:.2f}{unit}")

 
    