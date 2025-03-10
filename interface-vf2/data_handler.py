#data_handler.py
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from collections import deque
from PyQt6.QtCore import QTimer
import random

class DataHandler:
    def __init__(self, config=None):
        if config is None:
            config = {}
        self.config = config

        self.buffer_size = config["buffer_size"]
        self.num_motors = config["num_motors"]
        self.enable_gps = config["enable_gps"]
        self.gps_fix_types = config["gps_fix_types"]
        self.motor_color = config["motor_color"]
        self.voltage_drop_range = config["voltage_drop_range"]
        self.altitude_variation = config["altitude_variation"]
        self.motor_current_range = config["motor_current_range"]
        
        # Create buffers.
        self.time_buffer = deque(maxlen=self.buffer_size)
        self.motor_currents = [deque(maxlen=self.buffer_size) for _ in range(self.num_motors)]
        self.orientation = [deque(maxlen=self.buffer_size) for _ in range(3)]  # Roll, Pitch, Yaw
        self.altitude = deque(maxlen=self.buffer_size)
        self.battery_voltage = deque(maxlen=self.buffer_size)
        self.battery_percentage = deque(maxlen=self.buffer_size)
       
        # GPS Integration.
        self.gps_connected = self.enable_gps
        if self.gps_connected:
            if len(self.gps_fix_types) > 1:
                self.gps_fix = random.choice(self.gps_fix_types[:-1])
            else:
                self.gps_fix = self.gps_fix_types[0]
        else:
            self.gps_fix = "None"
  
        self.gps_lat = 0.0
        self.gps_lon = 0.0
        self.gps_alt = 0.0
        
        
        self.speed_over_ground = 0.0  # in m/s
        self.course = 0.0             # in degrees
        self.num_satellites = 0       # integer count
        

        self.full_time_log = []
        self.full_motor_log = [[] for _ in range(self.num_motors)]
        self.full_orientation_log = [[] for _ in range(3)]
        self.full_altitude_log = []
        self.full_battery_voltage_log = []
        self.full_battery_percentage_log = []
        self.full_gps_log = []  
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.generate_data)
        
    def generate_data(self):
        # Get the current UTC time.
        timestamp = datetime.now(timezone.utc)
        self.time_buffer.append(timestamp)
        self.full_time_log.append(timestamp)
 
        # Simulate motor currents, orientation, altitude, battery voltage/percentage.
        new_motor_currents = np.random.uniform(self.motor_current_range[0], self.motor_current_range[1], self.num_motors)
        new_orientation = np.random.uniform(-180, 180, 3)
        new_altitude = (self.altitude[-1] + np.random.uniform(-self.altitude_variation, self.altitude_variation)) if self.altitude else 0.0

        prev_voltage = self.battery_voltage[-1] if self.battery_voltage else 12.6
        new_voltage = max(11.1, prev_voltage - np.random.uniform(self.voltage_drop_range[0], self.voltage_drop_range[1]))
        new_percentage = (new_voltage / 12.6) * 100
        
        for i in range(self.num_motors):
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

        # Simulate GPS data.
        if self.gps_connected:
            self.gps_lat = np.random.uniform(-90, 90)
            self.gps_lon = np.random.uniform(-180, 180)
            self.gps_alt = np.random.uniform(0, 1000)
            self.speed_over_ground = random.uniform(0, 20)  # m/s
            self.course = random.uniform(0, 360)            # degrees
            self.num_satellites = random.randint(4, 12)
            
        else:
            self.gps_lat = 0.0
            self.gps_lon = 0.0
            self.gps_alt = 0.0
            self.speed_over_ground = 0.0
            self.course = 0.0
            self.num_satellites = 0
            
            
        # Log all GPS data.
        self.full_gps_log.append({
            "connected": self.gps_connected,
            "lat": self.gps_lat,
            "lon": self.gps_lon,
            "alt": self.gps_alt,
            "fix": self.gps_fix,
            "speed": self.speed_over_ground,
            "course": self.course,
            "satellites": self.num_satellites
        })
        
    def start(self):
        self.timer.start(200)  # Data generation interval (200ms).
        
    def stop(self):
        self.timer.stop()
        self.save_to_excel()
        
    def save_to_excel(self):
        readable_timestamps = [ts.strftime("%Y-%m-%d %H:%M:%S.%f") for ts in self.full_time_log]
        data = {"Timestamp": readable_timestamps}
        for i in range(self.num_motors):
            data[f"Motor{i+1}"] = self.full_motor_log[i]
        data["Roll"] = self.full_orientation_log[0]
        data["Pitch"] = self.full_orientation_log[1]
        data["Yaw"] = self.full_orientation_log[2]
        data["Altitude"] = self.full_altitude_log
        data["Voltage"] = self.full_battery_voltage_log
        data["Percentage"] = self.full_battery_percentage_log
        # Include GPS data.
        data["GPS_Connected"] = [gps["connected"] for gps in self.full_gps_log]
        data["GPS_Lat"] = [gps["lat"] for gps in self.full_gps_log]
        data["GPS_Lon"] = [gps["lon"] for gps in self.full_gps_log]
        data["GPS_Alt"] = [gps["alt"] for gps in self.full_gps_log]
        data["GPS_Fix"] = [gps["fix"] for gps in self.full_gps_log]
        data["Speed"] = [gps["speed"] for gps in self.full_gps_log]
        data["Course"] = [gps["course"] for gps in self.full_gps_log]
        data["Satellites"] = [gps["satellites"] for gps in self.full_gps_log]
        
        
        df = pd.DataFrame(data)
        df.to_excel("quadcopter_data.xlsx", index=False, float_format="%.2f")

    def updateConfig(self, new_config):
        if "buffer_size" in new_config:
            new_buffer_size = new_config["buffer_size"]
            self.buffer_size = new_buffer_size
            self.time_buffer = deque(self.time_buffer, maxlen=new_buffer_size)
            self.motor_currents = [deque(m, maxlen=new_buffer_size) for m in self.motor_currents]
            self.orientation = [deque(o, maxlen=new_buffer_size) for o in self.orientation]
            self.altitude = deque(self.altitude, maxlen=new_buffer_size)
            self.battery_voltage = deque(self.battery_voltage, maxlen=new_buffer_size)
            self.battery_percentage = deque(self.battery_percentage, maxlen=new_buffer_size)
            print("DataHandler buffer size updated to", new_buffer_size)
