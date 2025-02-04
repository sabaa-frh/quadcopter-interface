import numpy as np
import pandas as pd
import time
from collections import deque
from PyQt6.QtCore import QTimer

class DataHandler:
    def __init__(self, buffer_size=100):
        self.buffer_size = buffer_size  # e.g., 30 seconds of data at 5Hz (200ms intervals)

        self.time_buffer = deque(maxlen=buffer_size)
        self.motor_currents = [deque(maxlen=buffer_size) for _ in range(4)]  # 4 motors
        self.orientation = [deque(maxlen=buffer_size) for _ in range(3)]     # Roll, Pitch, Yaw
        self.altitude = deque(maxlen=buffer_size)
        self.battery_voltage = deque(maxlen=buffer_size)
        self.battery_percentage = deque(maxlen=buffer_size)
       
        # Full logs to record ALL data
        self.full_time_log = []
        self.full_motor_log = [[] for _ in range(4)]
        self.full_orientation_log = [[] for _ in range(3)]
        self.full_altitude_log = []
        self.full_battery_voltage_log = []
        self.full_battery_percentage_log = []
       
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.generate_data)
        
    def generate_data(self):
        # Initialize start time on first call
        if self.start_time is None:
            self.start_time = time.time()
        
       
        elapsed = time.time() - self.start_time
     
        self.time_buffer.append(elapsed)
        self.full_time_log.append(elapsed)
      
        new_motor_currents = np.random.uniform(0, 10, 4)
        new_orientation = np.random.uniform(-180, 180, 3)
        new_altitude = self.altitude[-1] + np.random.uniform(-0.1, 0.1) if self.altitude else 0.0
        new_voltage = max(11.1, (self.battery_voltage[-1] if self.battery_voltage else 12.6) - np.random.uniform(0, 0.01))
        new_percentage = (new_voltage / 12.6) * 100
        
   
        for i in range(4):
            self.motor_currents[i].append(new_motor_currents[i])
            self.full_motor_log[i].append(new_motor_currents[i])
        
   
        for i in range(3):
            self.orientation[i].append(new_orientation[i])
            self.full_orientation_log[i].append(new_orientation[i])
        
        self.altitude.append(new_altitude)
        self.full_altitude_log.append(new_altitude)
        
    
        self.battery_voltage.append(new_voltage)
        self.full_battery_voltage_log.append(new_voltage)
        
        self.battery_percentage.append(new_percentage)
        self.full_battery_percentage_log.append(new_percentage)
        
    def start(self):
        self.timer.start(200)  # Generate data every 200ms
        
    def stop(self):
        self.timer.stop()
        self.save_to_excel()
        
    def save_to_excel(self):
        # Use the full logs to save all data from the start
        df = pd.DataFrame({
            "Timestamp": self.full_time_log,
            "Motor1": self.full_motor_log[0],
            "Motor2": self.full_motor_log[1],
            "Motor3": self.full_motor_log[2],
            "Motor4": self.full_motor_log[3],
            "Roll": self.full_orientation_log[0],
            "Pitch": self.full_orientation_log[1],
            "Yaw": self.full_orientation_log[2],
            "Altitude": self.full_altitude_log,
            "Voltage": self.full_battery_voltage_log,
            "Percentage": self.full_battery_percentage_log
        })
        df.to_excel("quadcopter_data.xlsx", index=False,float_format="%.2f")
