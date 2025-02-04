from PyQt6.QtWidgets import QVBoxLayout,QPushButton, QWidget,QLabel, QComboBox, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


# ---------------------------
# Motor Block: graph 
# ---------------------------

class MotorCurrentVisualization(QWidget):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.toolbar = NavigationToolbar(self.canvas, self)  
        
        self.frequency = 200
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        block_title = QLabel("Motor Currents")
        block_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(block_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        freq_layout = QHBoxLayout()
        freq_label = QLabel("Update Frequency:")
        self.freq_dropdown = QComboBox()
        self.freq_dropdown.addItems(["200", "500", "1000", "2000"])
        self.freq_dropdown.setCurrentText("200")
        self.freq_dropdown.currentTextChanged.connect(self.set_frequency)
        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(self.freq_dropdown)
        
        layout.addLayout(freq_layout)
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)
        layout.addStretch(1)
        self.setLayout(layout)
        
        
        # Initialize subplots
        self.axes = self.figure.subplots(4, 1)
        self.figure.subplots_adjust(top=0.924,bottom=0.098,left=0.087,right=0.986,hspace=0.62,wspace=0.2)
        self.lines = []
        colors = ['r', 'g', 'b', 'm']
        for i, ax in enumerate(self.axes):
            line, = ax.plot([], [], color=colors[i], label=f"Motor {i+1}", picker=True)
            self.lines.append(line)
            ax.set_ylabel("Current (A)", fontsize=6)
            self.axes[i].legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=1) 
            
            if i < 3:
                ax.tick_params(labelbottom=False)
                ax.set_xlabel("")
        self.axes[-1].set_xlabel("Time (s)")
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.draw()
    def on_pick(self, event):
        if event.artist in self.lines:
            line = event.artist
            xdata, ydata = line.get_data()
            ind = event.ind[0]
  
            if not xdata or not str(xdata[ind]).strip():
                x_value = self.data_handler.time_buffer[ind]
            else:
                x_value = xdata[ind]
            print(f"Clicked Motor {self.lines.index(line) + 1}: Time={x_value:.2f}s, Current={ydata[ind]:.2f}A")

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
        x_data = x_data_full[::sampling_factor]
        for i in range(4):
            motor_data_full = list(self.data_handler.motor_currents[i])
            motor_data = motor_data_full[::sampling_factor]
            self.lines[i].set_data(x_data, motor_data)
            self.axes[i].relim()
            self.axes[i].autoscale_view(scalex=False, scaley=True)
            self.axes[i].legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=1)
            if x_data:
                max_time = max(x_data)
                self.axes[i].set_xlim(max(0, max_time - 20), max_time)
        
        self.canvas.draw()


# ---------------------------
# Orientation Block: graph 
# ---------------------------


class OrientationAltitudeVisualization(QWidget):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.frequency = 200 
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        block_title = QLabel("Orientation and Altitude")
        block_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(block_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        freq_layout = QHBoxLayout()
        freq_label = QLabel("Update Frequency:")
        self.freq_dropdown = QComboBox()
        self.freq_dropdown.addItems(["200", "500", "1000", "2000"])
        self.freq_dropdown.setCurrentText("200")
        self.freq_dropdown.currentTextChanged.connect(self.set_frequency)
        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(self.freq_dropdown)
        
        layout.addLayout(freq_layout)
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)
        layout.addStretch(1)
        self.setLayout(layout)
        
        # Initialize subplots
        self.axes = self.figure.subplots(4, 1)
        self.figure.subplots_adjust(top=0.927,bottom=0.097,left=0.128,right=0.986,hspace=0.618,wspace=0.2) 
        self.lines = [] 
        self.titles = ["Roll", "Pitch", "Yaw", "Altitude"]
        colors = ['r', 'g', 'b', 'm']
        for i, ax in enumerate(self.axes):
            line, = ax.plot([], [], color=colors[i], label=self.titles[i], picker=True)
            self.lines.append(line)
            ax.set_ylabel("Degrees(°)" if i < 3 else "Meters(m)", fontsize=6)
            ax.legend()
            
            if i < 3:
                ax.tick_params(labelbottom=False)
                ax.set_xlabel("")
        self.axes[-1].set_xlabel("Time (s)")
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.draw()

    def on_pick(self, event):
        if event.artist in self.lines:
            line = event.artist
            xdata, ydata = line.get_data()
            ind = event.ind[0]
            x_value = xdata[ind]
            if x_value is None or (isinstance(x_value, str) and not x_value.strip()):
                x_value = event.mouseevent.xdata
            print(f"Clicked {self.titles[self.lines.index(line)]}: Time={x_value:.2f}s, Value={ydata[ind]:.2f}")

    def set_frequency(self, freq_str):
        self.frequency = max(200, int(freq_str))
        self.timer.setInterval(self.frequency)

    def start(self):
        self.timer.start(self.frequency)

    def stop(self):
        self.timer.stop()

    def update_plot(self):
        data = [self.data_handler.orientation[0], self.data_handler.orientation[1], self.data_handler.orientation[2], self.data_handler.altitude]
        for i in range(4):
            self.lines[i].set_data(self.data_handler.time_buffer, data[i])
            self.axes[i].relim()
            self.axes[i].autoscale_view(scalex=False, scaley=True)
            self.axes[i].legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=1)
            if len(self.data_handler.time_buffer) > 0:
                max_time = max(self.data_handler.time_buffer)
                self.axes[i].set_xlim(max(0, max_time - 20), max_time)
        self.canvas.draw()
    
# ---------------------------
# Battery Block: graph 
# ---------------------------

class BatteryMonitoring(QWidget):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler
        self.figure = Figure(figsize=(5,2))
        self.canvas = FigureCanvas(self.figure)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.frequency = 500
        self.toolbar = NavigationToolbar(self.canvas, self) 
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(top=0.827,bottom=0.295,left=0.233,right=0.96,hspace=1.0,wspace=0.2)
        self.line, = self.ax.plot([], [], 'm-', label="Battery", )
        self.show_percentage = True
        
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        block_title = QLabel("Battery Monitoring")
        block_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(block_title, alignment=Qt.AlignmentFlag.AlignCenter)

        freq_layout = QHBoxLayout()
        freq_label = QLabel("Update Frequency:")
        self.freq_dropdown = QComboBox()
        self.freq_dropdown.addItems(["200", "500", "1000", "2000"])
        self.freq_dropdown.setCurrentText("200")
        self.freq_dropdown.currentTextChanged.connect(self.set_frequency)
        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(self.freq_dropdown)


        self.toggle_button = QPushButton("Toggle: Percentage/Voltage")
        self.toggle_button.clicked.connect(self.toggle_view)
        
        layout.addLayout(freq_layout)
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.toggle_button)
        layout.addStretch(1)
        self.setLayout(layout)
        
        
        self.ax.set_title("Battery Level", fontsize=10)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("battery (%)")
        self.ax.legend()
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.draw()

    def set_frequency(self, freq_str):
        self.frequency = int(freq_str)
        self.timer.setInterval(self.frequency)

    def start(self):
        self.timer.start(self.frequency)

    def stop(self):
        self.timer.stop()

    def on_pick(self, event):
        """Handle click events on data points."""
        if event.artist == self.line:
            xdata, ydata = self.line.get_data()
            ind = event.ind[0]
            unit = "%" if self.show_percentage else "V"
            print(f"Battery: Time={xdata[ind]:.2f}s, Value={ydata[ind]:.2f}{unit}")

    def toggle_view(self):
        """Switch between percentage and voltage views."""
        self.show_percentage = not self.show_percentage
        self.ax.set_ylabel("battery (%)" if self.show_percentage else "battery (V)")
        self.update_plot()
    def update_plot(self):
        base_interval_ms = 200
       
        sampling_factor = int(round(self.frequency / base_interval_ms))
        
        
        x_data_full = list(self.data_handler.time_buffer)
        x_data = x_data_full[::sampling_factor]
        
        if self.show_percentage:
            y_data_full = list(self.data_handler.battery_percentage)
        else:
            y_data_full = list(self.data_handler.battery_voltage)
        y_data = y_data_full[::sampling_factor]
        
        self.line.set_data(x_data, y_data)
        self.ax.relim()
        self.ax.autoscale_view(scalex=False, scaley=True)
        if x_data:
            max_time = max(x_data)
            self.ax.set_xlim(max(0, max_time - 20), max_time)
        
        self.canvas.draw()
 
    