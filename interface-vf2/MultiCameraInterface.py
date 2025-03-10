#MultiCameraInterface.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2

class VideoChannelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
   
        self.url_edit = QLineEdit(self)
        self.url_edit.setPlaceholderText("Enter IP Webcam URL here")
   
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_stream)
    
        self.video_label = QLabel("Video Feed", self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        
        layout.addWidget(self.url_edit)
        layout.addWidget(self.start_button)
        layout.addWidget(self.video_label)

    def start_stream(self):
 
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        
        url = self.url_edit.text().strip()
        if url:
            self.cap = cv2.VideoCapture(url)
           
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.timer.start(30)  

    def update_frame(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
              
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, _ = frame.shape
                bytes_per_line = 3 * width
                q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img).scaled(
                    self.video_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio
                )
                self.video_label.setPixmap(pixmap)
            else:
                self.video_label.setText("Failed to read frame")

    def closeEvent(self, event):
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        event.accept()

class MultiCameraWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("4 Video Channels")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        grid_layout = QGridLayout(central_widget)
        self.channels = []
        
        for i in range(4):
            channel = VideoChannelWidget(self)
            row = i // 2  # rows 0 and 1
            col = i % 2   # columns 0 and 1
            grid_layout.addWidget(channel, row, col)
            self.channels.append(channel)
