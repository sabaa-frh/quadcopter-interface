#data_handler.py
from datetime import datetime
import numpy as np
import pandas as pd
from collections import deque
from PyQt6.QtCore import QTimer
import random

class DataHandler:
    def __init__(self, buffer_size=100):
        self.buffer_size = buffer_size  # e.g., 30 seconds of data at 5Hz (200ms intervals)
        
        self.time_buffer = deque(maxlen=buffer_size)
        self.motor_currents = [deque(maxlen=buffer_size) for _ in range(4)]  # 4 motors
        self.orientation = [deque(maxlen=buffer_size) for _ in range(3)]     # Roll, Pitch, Yaw
        self.altitude = deque(maxlen=buffer_size)
        self.battery_voltage = deque(maxlen=buffer_size)
        self.battery_percentage = deque(maxlen=buffer_size)
       
        # --- GPS Integration (set once) ---
        self.gps_connected = True
        if self.gps_connected:
            self.gps_fix = random.choice(["2D", "3D"])
        else:
            self.gps_fix = "None"
  
        self.gps_lat = 0.0
        self.gps_lon = 0.0
        self.gps_alt = 0.0

        self.full_time_log = []
        self.full_motor_log = [[] for _ in range(4)]
        self.full_orientation_log = [[] for _ in range(3)]
        self.full_altitude_log = []
        self.full_battery_voltage_log = []
        self.full_battery_percentage_log = []
        self.full_gps_log = []  # List of dicts to store GPS data
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.generate_data)
        
    def generate_data(self):
   
        timestamp = datetime.now() 
        self.time_buffer.append(timestamp)
        self.full_time_log.append(timestamp)
 
        new_motor_currents = np.random.uniform(0, 10, 4)
        new_orientation = np.random.uniform(-180, 180, 3)
        new_altitude = self.altitude[-1] + np.random.uniform(-0.1, 0.1) if self.altitude else 0.0
        new_voltage = max(11.1, (self.battery_voltage[-1] if self.battery_voltage else 12.6) - np.random.uniform(0, 0.01))
        new_percentage = (new_voltage / 12.6) * 100
        
        # Log motor currents
        for i in range(4):
            self.motor_currents[i].append(new_motor_currents[i])
            self.full_motor_log[i].append(new_motor_currents[i])
        
        # Log orientation data
        for i in range(3):
            self.orientation[i].append(new_orientation[i])
            self.full_orientation_log[i].append(new_orientation[i])
        
        # Log altitude and battery data
        self.altitude.append(new_altitude)
        self.full_altitude_log.append(new_altitude)
        
        self.battery_voltage.append(new_voltage)
        self.full_battery_voltage_log.append(new_voltage)
        
        self.battery_percentage.append(new_percentage)
        self.full_battery_percentage_log.append(new_percentage)

        if self.gps_connected:
            self.gps_lat = np.random.uniform(-90, 90)
            self.gps_lon = np.random.uniform(-180, 180)
            self.gps_alt = np.random.uniform(0, 1000)  
        else:
            self.gps_lat = 0.0
            self.gps_lon = 0.0
            self.gps_alt = 0.0
            
    
        self.full_gps_log.append({
            "connected": self.gps_connected,
            "lat": self.gps_lat,
            "lon": self.gps_lon,
            "alt": self.gps_alt,
            "fix": self.gps_fix
        })
        
    def start(self):
        self.timer.start(200)  # Generate data every 200ms
        
    def stop(self):
        self.timer.stop()
        self.save_to_excel()
        
    def save_to_excel(self):
        readable_timestamps = [ts.strftime("%Y-%m-%d %H:%M:%S.%f") for ts in self.full_time_log]
        df = pd.DataFrame({
            "Timestamp": readable_timestamps,
            "Motor1": self.full_motor_log[0],
            "Motor2": self.full_motor_log[1],
            "Motor3": self.full_motor_log[2],
            "Motor4": self.full_motor_log[3],
            "Roll": self.full_orientation_log[0],
            "Pitch": self.full_orientation_log[1],
            "Yaw": self.full_orientation_log[2],
            "Altitude": self.full_altitude_log,
            "Voltage": self.full_battery_voltage_log,
            "Percentage": self.full_battery_percentage_log,
            "GPS_Connected": [gps["connected"] for gps in self.full_gps_log],
            "GPS_Lat": [gps["lat"] for gps in self.full_gps_log],
            "GPS_Lon": [gps["lon"] for gps in self.full_gps_log],
            "GPS_Alt": [gps["alt"] for gps in self.full_gps_log],
            "GPS_Fix": [gps["fix"] for gps in self.full_gps_log]
        })
        df.to_excel("quadcopter_data.xlsx", index=False, float_format="%.2f")
