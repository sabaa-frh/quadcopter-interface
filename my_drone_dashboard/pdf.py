#pdf.py

import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QBrush, QPainterPath
from PyQt6.QtCore import Qt,  QRectF, QPointF

# Import the DataHandler
from data_handler import DataHandler

# The existing widget classes (DroneAttitudeIndicator, HeadingIndicator, etc.) remain unchanged
# DroneAttitudeIndicator class
class DroneAttitudeIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.roll = 0.0
        self.pitch = 0.0
        self.setMinimumSize(150, 150)
        
    def setPitchRoll(self, pitch, roll):
        self.pitch = pitch
        self.roll = roll
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 10
        
        # Save the current state
        painter.save()
        
        # Move to center and rotate
        painter.translate(center_x, center_y)
        painter.rotate(self.roll)
        
        # Draw artificial horizon
        sky_rect = QRectF(-radius, -radius, radius * 2, radius * 2)
        ground_rect = QRectF(-radius, 0, radius * 2, radius * 2)
        
        # Adjust for pitch
        pitch_offset = radius * self.pitch / 45.0  # Scale pitch to pixels
        painter.translate(0, pitch_offset)
        
        # Draw sky
        painter.setBrush(QBrush(QColor(0, 128, 255)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(-radius, -radius * 2, radius * 2, radius * 2))
        
        # Draw ground
        painter.setBrush(QBrush(QColor(139, 69, 19)))
        painter.drawRect(QRectF(-radius, 0, radius * 2, radius * 2))
        
        # Draw horizon line
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawLine(int(-radius), 0, int(radius), 0)
        
        # Draw pitch lines
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        for i in range(-45, 46, 5):
            if i == 0:
                continue  # Skip zero (horizon line already drawn)
                
            y = -i * radius / 45.0
            
            # Different line lengths based on multiples of 10
            line_length = radius * 0.5 if i % 10 == 0 else radius * 0.25
            
            painter.drawLine(int(-line_length / 2), int(y), int(line_length / 2), int(y))
            
            # Add degree numbers for multiples of 10
            if i % 10 == 0:
                painter.setFont(QFont("Arial", 8))
                degree_text = str(abs(i))
                text_width = painter.fontMetrics().horizontalAdvance(degree_text)
                painter.drawText(QPointF(-line_length / 2 - text_width - 5, y + 4), degree_text)
                painter.drawText(QPointF(line_length / 2 + 5, y + 4), degree_text)
        
        painter.restore()
        
        # Draw fixed aircraft symbol
        painter.setPen(QPen(Qt.GlobalColor.yellow, 3))
        painter.drawLine(int(center_x - 30), int(center_y), int(center_x - 10), int(center_y))
        painter.drawLine(int(center_x + 10), int(center_y), int(center_x + 30), int(center_y))
        painter.drawLine(int(center_x), int(center_y - 5), int(center_x), int(center_y + 5))
        
        # Draw outer circle
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2))
        
        # Draw roll indicator at the top
        painter.save()
        painter.translate(center_x, center_y)
        
        # Draw roll indicator ticks
        tick_angles = [-60, -45, -30, -20, -10, 0, 10, 20, 30, 45, 60]
        for angle in tick_angles:
            painter.save()
            painter.rotate(angle)
            tick_length = 10 if angle % 30 == 0 else 5
            painter.drawLine(0, int(-radius + 2), 0, int(-radius + 2 + tick_length))
            
            if angle % 30 == 0:
                painter.setFont(QFont("Arial", 8))
                text = str(abs(angle))
                text_width = painter.fontMetrics().horizontalAdvance(text)
                painter.drawText(QPointF(-text_width/2, -radius + 25), text)
            
            painter.restore()
        
        # Draw roll indicator arrow
        painter.rotate(-self.roll)
        painter.setPen(QPen(Qt.GlobalColor.yellow, 2))
        painter.drawLine(0, int(-radius + 5), 0, int(-radius + 15))
        painter.drawLine(0, int(-radius + 15), -5, int(-radius + 20))
        painter.drawLine(0, int(-radius + 15), 5, int(-radius + 20))
        
        painter.restore()


class HeadingIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.heading = 0.0
        self.setMinimumSize(80,80)
        
    def setHeading(self, heading):
        self.heading = heading
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width / 2
        
        # Draw background
        painter.setBrush(QBrush(QColor(10, 10, 30)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, width, height)
        
        # Draw heading scale
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        scale_width = width - 40
        scale_top = 20
        scale_height = 30
        
        painter.drawLine(20, scale_top + scale_height, width - 20, scale_top + scale_height)
        
        # Draw degree marks
        pixels_per_degree = scale_width / 60.0  # Show 60 degrees in view
        
        for i in range(-30, 31):
            degree = (self.heading + i) % 360
            x = int(center_x + i * pixels_per_degree)
            
            if 0 <= x <= width:
                # Different line heights based on multiples
                line_height = 15 if degree % 30 == 0 else (10 if degree % 10 == 0 else 5)
                
                painter.drawLine(x, scale_top + scale_height - line_height, x, scale_top + scale_height)
                
                # Add text for major headings
                if degree % 30 == 0:
                    # Use N, E, S, W for cardinal directions
                    if degree == 0:
                        label = "N"
                    elif degree == 90:
                        label = "E"
                    elif degree == 180:
                        label = "S"
                    elif degree == 270:
                        label = "W"
                    else:
                        label = str(degree)
                        
                    painter.setFont(QFont("Arial", 10))
                    text_width = painter.fontMetrics().horizontalAdvance(label)
                    painter.drawText(QPointF(x - text_width/2, scale_top + scale_height - 20), label)
        
        # Draw center triangle
        painter.setPen(QPen(Qt.GlobalColor.yellow, 2))
        painter.setBrush(QBrush(Qt.GlobalColor.yellow))
        triangle = QPainterPath()
        triangle.moveTo(center_x, scale_top)
        triangle.lineTo(center_x - 10, scale_top + 10)
        triangle.lineTo(center_x + 10, scale_top + 10)
        triangle.closeSubpath()
        painter.drawPath(triangle)
        
        # Draw heading number
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        heading_text = f"{int(self.heading):03d}°"
        text_width = painter.fontMetrics().horizontalAdvance(heading_text)
        painter.drawText(QPointF(center_x - text_width/2, height - 10), heading_text)


class AltitudeIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.altitude = 0.0
        self.setMinimumSize(80, 100)
        
    def setAltitude(self, altitude):
        self.altitude = altitude
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_y = height / 2
        
        # Draw background
        painter.setBrush(QBrush(QColor(10, 10, 30)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, width, height)
        
        # Draw altitude scale
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        scale_height = height - 40
        scale_left = width - 30
        scale_width = 20
        
        painter.drawLine(scale_left, 20, scale_left, height - 20)
        
        # Draw altitude marks
        pixels_per_meter = scale_height / 100.0  # Show 100m in view
        
        min_alt = self.altitude - 50
        max_alt = self.altitude + 50
        
        # Round to nearest 10m for clarity
        for alt in range(int(min_alt // 10) * 10, int(max_alt // 10) * 10 + 10, 10):
            y = int(center_y - (alt - self.altitude) * pixels_per_meter)
            
            if 20 <= y <= height - 20:
                # Different line lengths based on multiples
                line_length = 15 if alt % 50 == 0 else (10 if alt % 20 == 0 else 5)
                
                painter.drawLine(scale_left - line_length, y, scale_left, y)
                
                # Add text for major altitudes
                if alt % 50 == 0:
                    label = str(alt)
                    painter.setFont(QFont("Arial", 8))
                    text_width = painter.fontMetrics().horizontalAdvance(label)
                    painter.drawText(QPointF(scale_left - text_width - 5, y + 4), label)
        
        # Draw center pointer
        painter.setPen(QPen(Qt.GlobalColor.yellow, 2))
        painter.setBrush(QBrush(Qt.GlobalColor.yellow))
        triangle = QPainterPath()
        triangle.moveTo(width - 5, center_y)
        triangle.lineTo(width - 15, center_y - 10)
        triangle.lineTo(width - 15, center_y + 10)
        triangle.closeSubpath()
        painter.drawPath(triangle)
        
        # Draw altitude box
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.setBrush(QBrush(QColor(0, 0, 0, 180)))
        alt_box = QRectF(5, center_y - 15, width - 25, 30)
        painter.drawRect(alt_box)
        
        # Draw altitude number
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        alt_text = f"{int(self.altitude)}m"
        text_width = painter.fontMetrics().horizontalAdvance(alt_text)
        painter.drawText(QPointF(alt_box.center().x() - text_width/2, alt_box.center().y() + 5), alt_text)


class AirspeedIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.airspeed = 0.0
        self.setMinimumSize(80, 100)
        
    def setAirspeed(self, airspeed):
        self.airspeed = airspeed
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_y = height / 2
        
        # Draw background
        painter.setBrush(QBrush(QColor(10, 10, 30)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, width, height)
        
        # Draw speed scale
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        scale_height = height - 40
        scale_left = 30
        scale_width = 20
        
        painter.drawLine(scale_left, 20, scale_left, height - 20)
        
        # Draw speed marks
        pixels_per_unit = scale_height / 30.0  # Show 30 m/s in view
        
        min_speed = max(0, self.airspeed - 15)
        max_speed = self.airspeed + 15
        
        # Round to nearest 5m/s for clarity
        for speed in range(int(min_speed // 5) * 5, int(max_speed // 5) * 5 + 5, 5):
            y = int(center_y - (speed - self.airspeed) * pixels_per_unit)
            
            if 20 <= y <= height - 20:
                # Different line lengths based on multiples
                line_length = 15 if speed % 10 == 0 else 5
                
                painter.drawLine(scale_left, y, scale_left + line_length, y)
                
                # Add text for major speeds
                if speed % 10 == 0:
                    label = str(speed)
                    painter.setFont(QFont("Arial", 8))
                    painter.drawText(QPointF(scale_left + line_length + 5, y + 4), label)
        
        # Draw center pointer
        painter.setPen(QPen(Qt.GlobalColor.yellow, 2))
        painter.setBrush(QBrush(Qt.GlobalColor.yellow))
        triangle = QPainterPath()
        triangle.moveTo(5, center_y)
        triangle.lineTo(15, center_y - 10)
        triangle.lineTo(15, center_y + 10)
        triangle.closeSubpath()
        painter.drawPath(triangle)
        
        # Draw speed box
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.setBrush(QBrush(QColor(0, 0, 0, 180)))
        speed_box = QRectF(25, center_y - 15, width - 25, 30)
        painter.drawRect(speed_box)
        
        # Draw speed number
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        speed_text = f"{self.airspeed:.1f} m/s"
        text_width = painter.fontMetrics().horizontalAdvance(speed_text)
        painter.drawText(QPointF(speed_box.center().x() - text_width/2, speed_box.center().y() + 5), speed_text)


# Modified DronePFD class to use DataHandler
class DronePFD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Primary Flight Display")
        self.resize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create title label
        title_label = QLabel("DRONE PRIMARY FLIGHT DISPLAY")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; background-color: #102040; padding: 5px;")
        main_layout.addWidget(title_label)
        
        # Create horizontal layout for instruments
        instruments_layout = QHBoxLayout()
        main_layout.addLayout(instruments_layout)
        
        # Create airspeed indicator
        self.airspeed_indicator = AirspeedIndicator()
        instruments_layout.addWidget(self.airspeed_indicator)
        
        # Create central layout for attitude and heading
        central_layout = QVBoxLayout()
        instruments_layout.addLayout(central_layout)
        
        # Create attitude indicator
        self.attitude_indicator = DroneAttitudeIndicator()
        central_layout.addWidget(self.attitude_indicator)
        
        # Create heading indicator
        self.heading_indicator = HeadingIndicator()
        central_layout.addWidget(self.heading_indicator)
        
        # Create altitude indicator
        self.altitude_indicator = AltitudeIndicator()
        instruments_layout.addWidget(self.altitude_indicator)
        
        # Create info labels
        info_layout = QHBoxLayout()
        main_layout.addLayout(info_layout)
        
        # Create labels for extra info
        self.battery_label = QLabel("BATTERY: 100%")
        self.battery_label.setStyleSheet("color: lime; font-weight: bold;")
        self.gps_label = QLabel("GPS: 0 SATELLITES")
        self.gps_label.setStyleSheet("color: lime; font-weight: bold;")
        self.status_label = QLabel("STATUS: INITIALIZING")
        self.status_label.setStyleSheet("color: lime; font-weight: bold;")
        
        info_layout.addWidget(self.battery_label)
        info_layout.addWidget(self.gps_label)
        info_layout.addWidget(self.status_label)
        
        # Set the background color
        self.setStyleSheet("background-color: #0A0A1E;")
        
        # Initialize DataHandler with default configuration
        self.data_handler = DataHandler({
            "buffer_size": 100,
            "num_motors": 4,
            "enable_gps": True,
            "gps_fix_types": ["2D", "3D", "None"],
            "motor_color": "#ff0000",
            "voltage_drop_range": [0.0, 0.01],
            "altitude_variation": 0.1,
            "motor_current_range": [0.0, 10.0]
        })
        
        # Connect the dataUpdated signal to our update method
        self.data_handler.dataUpdated.connect(self.updateDisplay)
        
        # Start generating data
        self.data_handler.start()
        
    def updateDisplay(self):
        # Get the latest data from DataHandler
        try:
            # Attitude data (roll, pitch, yaw)
            roll = self.data_handler.orientation[0][-1] if self.data_handler.orientation[0] else 0.0
            pitch = self.data_handler.orientation[1][-1] if self.data_handler.orientation[1] else 0.0
            heading = self.data_handler.orientation[2][-1] if self.data_handler.orientation[2] else 0.0
            
            # Altitude data
            altitude = self.data_handler.altitude[-1] if self.data_handler.altitude else 0.0
            
            # Battery data
            voltage = self.data_handler.battery_voltage[-1] if self.data_handler.battery_voltage else 12.6
            battery_percent = self.data_handler.battery_percentage[-1] if self.data_handler.battery_percentage else 100.0
            
            # Use speed over ground for airspeed (approximation)
            airspeed = self.data_handler.speed_over_ground
            
            # GPS data
            gps_connected = self.data_handler.gps_connected
            gps_fix = self.data_handler.gps_fix
            num_satellites = self.data_handler.num_satellites
            
            # Update the instruments
            self.attitude_indicator.setPitchRoll(pitch, roll)
            self.heading_indicator.setHeading(heading)
            self.altitude_indicator.setAltitude(altitude)
            self.airspeed_indicator.setAirspeed(airspeed)
            
            # Determine status
            status_text = "FLYING"
            if battery_percent < 20:
                status_text = "LOW BATTERY"
            elif not gps_connected or gps_fix == "None" or num_satellites < 4:
                status_text = "POOR GPS"
            
            # Update the info labels
            battery_color = "lime" if battery_percent > 20 else "red"
            self.battery_label.setStyleSheet(f"color: {battery_color}; font-weight: bold;")
            self.battery_label.setText(f"BATTERY: {int(battery_percent)}%")
            
            gps_color = "lime" if gps_connected and num_satellites >= 4 else "yellow" if gps_connected else "red"
            self.gps_label.setStyleSheet(f"color: {gps_color}; font-weight: bold;")
            self.gps_label.setText(f"GPS: {num_satellites} SATELLITES")
            
            status_color = "lime" if status_text == "FLYING" else "red"
            self.status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
            self.status_label.setText(f"STATUS: {status_text}")
            
        except IndexError:
            # Handle case where data hasn't been generated yet
            pass

    def closeEvent(self, event):
        # Stop the data handler when window is closed
        self.data_handler.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DronePFD()
    window.show()
    sys.exit(app.exec())