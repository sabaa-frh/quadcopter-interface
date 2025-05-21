#data_handler.py

from __future__ import annotations

import logging
import time
import threading
from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np  # only used once for typed zeros (keep for future)
import pandas as pd
import serial
from PyQt6.QtCore import QTimer, QObject, pyqtSignal


class DataHandler(QObject):
    """Collects telemetry from the Arduino and stores it to buffers."""

    dataUpdated = pyqtSignal()

    # ------------------------------------------------------------------ construction

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__()
        self.config = config
        self.buffer_size: int = config.get("buffer_size", 100)
        self.num_motors: int = config.get("num_motors", 4)

        # --- serial -----------------------------------------------------
        self.arduino_port      = config.get("arduino_port", "")
        self.arduino_baudrate  = config.get("arduino_baudrate", 115200)
        self.serial_connected  = False
        self.serial_device     = None
        self.serial_thread     = None
        self.running           = False  # thread loop flag

        # --- ring‑buffers ----------------------------------------------
        self.time_buffer       = deque(maxlen=self.buffer_size)
        self.motor_currents    = [deque(maxlen=self.buffer_size) for _ in range(self.num_motors)]
        self.orientation       = [deque(maxlen=self.buffer_size) for _ in range(3)]  # roll, pitch, yaw
        self.altitude          = deque(maxlen=self.buffer_size)
        self.battery_voltage   = deque(maxlen=self.buffer_size)
        self.battery_percentage = deque(maxlen=self.buffer_size)
        self.motor_pwm         = [deque(maxlen=self.buffer_size) for _ in range(self.num_motors)]
        self.receiver_channels = [deque(maxlen=self.buffer_size) for _ in range(4)]  # yaw, pitch, throttle, roll

        # --- latest parsed line ----------------------------------------
        self.latest_arduino_data = {
            "motor_currents": [0.0] * self.num_motors,
            "roll":            0.0,
            "pitch":           0.0,
            "yaw":             0.0,
            "receiver":        [1500, 1500, 1000, 1500],
            "motor_pwm":       [1000] * self.num_motors,
            "last_update":     None,
        }

        # dict exposed to the UI (updated every cycle)
        self.pwm_iBus = {"yaw": 1500, "pit": 1500, "thr": 1000, "rol": 1500}

        # --- GPS placeholders (kept static when no fix) -----------------
        self.gps_fix = "None"
        self.gps_lat = 0.0
        self.gps_lon = 0.0
        self.gps_alt = 0.0
        self.speed_over_ground = 0.0
        self.course            = 0.0
        self.num_satellites    = 0

        # --- timer driving update_data() -------------------------------
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)

        if self.arduino_port:
            self.connect_to_arduino()

    # ------------------------------------------------------------------ serial helpers

    def connect_to_arduino(self) -> bool:
        try:
            self.serial_device = serial.Serial(
                port     = self.arduino_port,
                baudrate = self.arduino_baudrate,
                timeout  = 1,
            )
            time.sleep(2)  # allow Arduino to reset
            self.serial_connected = True
            logging.info("Connected to Arduino on %s", self.arduino_port)
            return True
        except Exception as exc:
            logging.error("Failed to connect to Arduino: %s", exc)
            self.serial_connected = False
            return False

    def disconnect_from_arduino(self) -> None:
        if self.serial_device and self.serial_device.is_open:
            self.serial_device.close()
        self.serial_connected = False
        logging.info("Disconnected from Arduino")

    def start_serial_thread(self) -> None:
        if not self.serial_connected:
            return
        self.running = True
        self.serial_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.serial_thread.start()

    def stop_serial_thread(self) -> None:
        self.running = False
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.join(timeout=1.0)

    # ------------------------------------------------------------------ read‑parse

    def _read_loop(self) -> None:
        """Background task: read chars, assemble full lines."""
        line = ""
        while self.running and self.serial_connected:
            try:
                if self.serial_device.in_waiting:
                    ch = self.serial_device.read(1).decode(errors="ignore")
                    if ch == "\n":
                        self._parse_line(line)
                        line = ""
                    else:
                        line += ch
            except Exception as exc:
                logging.error("Serial read error: %s", exc)
                time.sleep(1)

    def _parse_line(self, text: str) -> None:
        """VERY simplified parser that only accepts the exact Arduino format."""
        try:
            parts = text.split("|")
            if parts and "Rx:" in parts[0]:
                recv = []
                for tag in ["Y:", "P:", "T:", "R:"]:
                    for tok in parts[0].split():
                        if tok.startswith(tag):
                            recv.append(int(tok.replace(tag, "")))
                            break
                if len(recv) == 4:
                    self.latest_arduino_data["receiver"] = recv

            if len(parts) > 3 and "PWM:" in parts[3]:
                pwm = []
                for i in range(self.num_motors):
                    label = f"M{i+1}:"
                    for tok in parts[3].split():
                        if tok.startswith(label):
                            pwm.append(int(tok.replace(label, "")))
                            break
                if len(pwm) == self.num_motors:
                    self.latest_arduino_data["motor_pwm"] = pwm

            if len(parts) > 4 and "Ang:" in parts[4]:
                for axis, key in zip(["X:", "Y:", "Z:"], ["roll", "pitch", "yaw"]):
                    for tok in parts[4].split():
                        if tok.startswith(axis):
                            self.latest_arduino_data[key] = float(tok.replace(axis, ""))
                            break

            if len(parts) > 5 and "Current:" in parts[5]:
                curr = []
                for i in range(self.num_motors):
                    label = f"M{i+1}:"
                    for tok in parts[5].split():
                        if tok.startswith(label):
                            curr.append(float(tok.replace(label, "")))
                            break
                if len(curr) == self.num_motors:
                    self.latest_arduino_data["motor_currents"] = curr

            self.latest_arduino_data["last_update"] = datetime.now(timezone.utc)
        except Exception as exc:
            logging.error("Error parsing '%s': %s", text, exc)

    # ------------------------------------------------------------------ cyclic update (no simulation)

    def update_data(self) -> None:
        ts = datetime.now(timezone.utc)
        self.time_buffer.append(ts.timestamp())

        # decide if we have fresh serial data (<2 s old)
        has_recent = (
            self.latest_arduino_data["last_update"] is not None and
            (ts - self.latest_arduino_data["last_update"]).total_seconds() < 2.0
        )

        # 1. motor currents ------------------------------------------------
        if has_recent:
            vals = self.latest_arduino_data["motor_currents"]
        else:
            vals = [0.0] * self.num_motors
        for i, val in enumerate(vals):
            self.motor_currents[i].append(val)

        # 2. orientation ---------------------------------------------------
        if has_recent:
            orient = [self.latest_arduino_data[k] for k in ("roll", "pitch", "yaw")]
        else:
            orient = [0.0, 0.0, 0.0]
        for i, v in enumerate(orient):
            self.orientation[i].append(v)

        # 3. motor‑PWM -----------------------------------------------------
        if has_recent:
            pwm_vals = self.latest_arduino_data["motor_pwm"]
        else:
            pwm_vals = [1000] * self.num_motors
        for i, v in enumerate(pwm_vals):
            self.motor_pwm[i].append(v)

        # 4. receiver channels + expose dict ------------------------------
        if has_recent:
            recv_vals = self.latest_arduino_data["receiver"]
        else:
            recv_vals = [1500, 1500, 1000, 1500]
        for i, v in enumerate(recv_vals):
            self.receiver_channels[i].append(v)
        self.pwm_iBus = {"yaw": recv_vals[0], "pit": recv_vals[1], "thr": recv_vals[2], "rol": recv_vals[3]}

        # 5. altitude (keep last or zero) ----------------------------------
        alt = self.altitude[-1] if self.altitude else 0.0
        self.altitude.append(alt)

        # 6. battery stays flat until real packets report voltage ----------
        prev_v = self.battery_voltage[-1] if self.battery_voltage else 12.6
        pct    = (prev_v / 12.6) * 100.0
        self.battery_voltage.append(prev_v)
        self.battery_percentage.append(pct)

        # 7. GPS values remain as set externally (zeros by default) --------
        # (No change when not connected)

        self.dataUpdated.emit()

    # ------------------------------------------------------------------ public start/stop

    def start(self) -> None:
        if self.arduino_port and not self.serial_connected:
            self.connect_to_arduino()
        if self.serial_connected:
            self.start_serial_thread()
        self.timer.start(200)
        logging.info("DataHandler started")

    def stop(self) -> None:
        self.timer.stop()
        self.stop_serial_thread()
        self.disconnect_from_arduino()
        self._save_to_excel()
        logging.info("DataHandler stopped and file saved")

    # ------------------------------------------------------------------ persistence

    def _save_to_excel(self) -> None:
        readable = [datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S.%f")
                    for ts in self.time_buffer]
        df_dict: Dict[str, List[Any]] = {"Timestamp": readable}

        for i in range(self.num_motors):
            df_dict[f"Motor{i+1}"]       = list(self.motor_currents[i])
            df_dict[f"Motor{i+1}_PWM"]   = list(self.motor_pwm[i])

        df_dict["Roll"]  = list(self.orientation[0])
        df_dict["Pitch"] = list(self.orientation[1])
        df_dict["Yaw"]   = list(self.orientation[2])

        names = ["Yaw", "Pitch", "Throttle", "Roll"]
        for i, n in enumerate(names):
            df_dict[f"Rx_{n}"] = list(self.receiver_channels[i])

        df_dict["Altitude"]   = list(self.altitude)
        df_dict["Voltage"]    = list(self.battery_voltage)
        df_dict["Percentage"] = list(self.battery_percentage)

        df = pd.DataFrame(df_dict)
        try:
            df.to_excel("quadcopter_data.xlsx", index=False)
        except Exception as exc:
            logging.error("Excel save error: %s", exc)


    def updateConfig(self, new_config: Dict[str, Any]) -> None:
        """Update configuration and resize buffers if requested."""
        if "buffer_size" in new_config:
            new_len = new_config["buffer_size"]
            self.buffer_size = new_len
            self.time_buffer     = deque(self.time_buffer,     maxlen=new_len)
            self.motor_currents  = [deque(m, maxlen=new_len) for m in self.motor_currents]
            self.orientation     = [deque(o, maxlen=new_len) for o in self.orientation]
            self.altitude        = deque(self.altitude,        maxlen=new_len)
            self.battery_voltage = deque(self.battery_voltage, maxlen=new_len)
            self.battery_percentage = deque(self.battery_percentage, maxlen=new_len)
            self.motor_pwm       = [deque(m, maxlen=new_len) for m in self.motor_pwm]
            self.receiver_channels = [deque(r, maxlen=new_len) for r in self.receiver_channels]
            logging.info(f"DataHandler buffer size updated to {new_len}")

        # Reconnect logic for Arduino port/baud can go here if you expose those in your config tab
