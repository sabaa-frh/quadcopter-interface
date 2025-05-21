#blocks.py
from PyQt6.QtWidgets import QVBoxLayout,QSplitter,QSizePolicy, QHBoxLayout, QWidget, QLabel, QComboBox, QFrame, QGridLayout, QPushButton
from PyQt6.QtCore import QTimer, Qt
import pyqtgraph as pg
from pyqtgraph import DateAxisItem
from typing import Any, Dict


class MotorCurrentVisualization(QWidget):
    """Visualization widget for motor currents in a 2×2 grid plus a 4-bar chart."""
    def __init__(self, data_handler: Any) -> None:
        super().__init__()
        self.data_handler = data_handler
        self.data_handler.dataUpdated.connect(self.update_plot)
        # initial settings
        self.frequency = self.data_handler.config.get("motor_update_freq", 200)
        self.titles    = self.data_handler.config.get("motor_titles", [])
        self.colors    = self.data_handler.config.get("motor_colors", [])

        # placeholders for curves, stats‐labels, and panel widgets
        self.plots = []
        self.curves = []
        self.stats  = []
        self.motor_widgets = []

        self.initUI()

    def initUI(self) -> None:
        """Build the 2 × 2 grid (one vertical splitter between rows)
        + a 4-bar chart below it."""
        # ── container ────────────────────────────────────────────────
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)

        # ── header: block title + frequency selector ────────────────
        header = QHBoxLayout()
        header.addWidget(QLabel("<b>Motor Currents</b>"))
        header.addStretch(1)
        header.addWidget(QLabel("Update Frequency:"))
        self.freq_dropdown = QComboBox()
        self.freq_dropdown.addItems(["200", "500", "1000", "2000"])
        self.freq_dropdown.setCurrentText(str(self.frequency))
        self.freq_dropdown.currentTextChanged.connect(self.set_frequency)
        header.addWidget(self.freq_dropdown)
        main_layout.addLayout(header)

        # ── build the four motor panels ─────────────────────────────
        self.motor_widgets = []
        self.plots, self.curves, self.stats = [], [], []

        for i in range(4):
            panel  = QWidget()
            vbox   = QVBoxLayout(panel)
            vbox.setContentsMargins(2, 2, 2, 2)

            # legend (colour swatch + title)
            leg = QHBoxLayout()
            col = self.colors[i] if i < len(self.colors) else "#000000"
            sw  = QLabel(); sw.setFixedSize(10, 10)
            sw.setStyleSheet(f"background-color:{col};")
            leg.addWidget(sw)
            title = self.titles[i] if i < len(self.titles) else f"Motor {i+1}"
            leg.addWidget(QLabel(f"<b>{title}</b>"))
            leg.addStretch(1)
            vbox.addLayout(leg)

            # time-series plot
            axis  = DateAxisItem(orientation='bottom')
            plot  = pg.PlotWidget(axisItems={'bottom': axis})
            plot.setLabel('left', "Current (A)")
            curve = plot.plot([], [], pen=pg.mkPen(color=col, width=2))
            self.plots.append(plot)
            self.curves.append(curve)
            vbox.addWidget(plot)

            # stats row
            stat = QHBoxLayout()
            a  = QLabel("Actual: 0.00 A")
            mi = QLabel("Min: 0.00 A")
            ma = QLabel("Max: 0.00 A")
            stat.addWidget(a); stat.addWidget(mi); stat.addWidget(ma)
            self.stats.append((a, mi, ma))
            vbox.addLayout(stat)

            # separator
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setFrameShadow(QFrame.Shadow.Sunken)
            vbox.addWidget(sep)

            panel.setSizePolicy(QSizePolicy.Policy.Expanding,
                                QSizePolicy.Policy.Expanding)
            self.motor_widgets.append(panel)

        # ── grid with ONE vertical splitter between rows ─────────────
        # row 1 ­– Motor 1 & 2
        row1 = QSplitter(Qt.Orientation.Horizontal)
        row1.setHandleWidth(5)
        row1.setChildrenCollapsible(False)
        row1.addWidget(self.motor_widgets[0])
        row1.addWidget(self.motor_widgets[1])

        # row 2 ­– Motor 3 & 4
        row2 = QSplitter(Qt.Orientation.Horizontal)
        row2.setHandleWidth(5)
        row2.setChildrenCollapsible(False)
        row2.addWidget(self.motor_widgets[2])
        row2.addWidget(self.motor_widgets[3])

        # vertical splitter that controls the two rows together
        grid_split = QSplitter(Qt.Orientation.Vertical)
        grid_split.setHandleWidth(5)
        grid_split.setChildrenCollapsible(False)
        grid_split.addWidget(row1)
        grid_split.addWidget(row2)
        self.row_splitter = grid_split    

        # ── bar chart of latest currents ─────────────────────────────
        self.bar_plot = pg.PlotWidget()
        self.bar_plot.setLabel('left', "Current (A)")
        self.bar_plot.getAxis('bottom').setTicks(
            [[(i, f"M{i+1}") for i in range(4)]])
        self.bar_plot.setFixedHeight(150)

        # placeholder to absorb extra vertical stretch
        placeholder = QWidget()
        placeholder.setSizePolicy(QSizePolicy.Policy.Expanding,
                                QSizePolicy.Policy.Expanding)

        bar_and_bottom = QSplitter(Qt.Orientation.Vertical)
        bar_and_bottom.setHandleWidth(5)
        bar_and_bottom.setChildrenCollapsible(False)
        bar_and_bottom.addWidget(self.bar_plot)
        bar_and_bottom.addWidget(placeholder)
        bar_and_bottom.setStretchFactor(0, 0)
        bar_and_bottom.setStretchFactor(1, 1)
        bar_and_bottom.setSizes([150, 100])

        # ── final vertical stack: grid + bar section ────────────────
        main_split = QSplitter(Qt.Orientation.Vertical)
        main_split.setHandleWidth(5)
        main_split.setChildrenCollapsible(False)
        main_split.addWidget(grid_split)
        main_split.addWidget(bar_and_bottom)
        main_split.setStretchFactor(0, 1)
        main_split.setStretchFactor(1, 0)
        main_split.setSizes([400, 200])

        main_layout.addWidget(main_split)

        # ── total-current label centered under everything ───────────
        total_box = QHBoxLayout()
        total_box.addStretch(1)
        self.total_current_label = QLabel("Total: 0.00 A")
        self.total_current_label.setStyleSheet(
            "border:1px solid black; border-radius:5px; padding:4px; font-weight:bold;")
        total_box.addWidget(self.total_current_label)
        total_box.addStretch(1)
        main_layout.addLayout(total_box)

        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                        QSizePolicy.Policy.Expanding)

    def set_frequency(self, freq_str: str) -> None:
        """Update how often plots refresh """
        self.frequency = int(freq_str)

    def update_plot(self) -> None:
        """Fetch the latest data from DataHandler and redraw both time-series and bars."""
        step = max(1, round(self.frequency / 200))
        # DataHandler.time_buffer now holds float seconds
        times = list(self.data_handler.time_buffer)[::step] 

        # update each motor’s curve + stats
        for i, curve in enumerate(self.curves):
            data = list(self.data_handler.motor_currents[i])[::step]
            if not data:
                continue
            curve.setData(times[:len(data)], data)
            plot = self.plots[i]
            mx = max(times)
            plot.setXRange(mx - 20, mx)

            a, mi, ma = self.stats[i]
            a.setText(f"Actual: {data[-1]:.2f} A")
            mi.setText(f"Min:    {min(data):.2f} A")
            ma.setText(f"Max:    {max(data):.2f} A")

        # update bar chart
        current_vals = [
            (self.data_handler.motor_currents[i][-1]
             if self.data_handler.motor_currents[i] else 0.0)
            for i in range(4)
        ]
        self.bar_plot.clear()
        ticks = [(i, f"M{i+1}") for i in range(4)]
        self.bar_plot.getAxis('bottom').setTicks([ticks])
        for i, val in enumerate(current_vals):
            bg = pg.BarGraphItem(
                x=[i], height=[val], width=0.6, brush=self.colors[i]
            )
            self.bar_plot.addItem(bg)
        self.bar_plot.enableAutoRange(axis=pg.ViewBox.XAxis, enable=True)
        self.bar_plot.enableAutoRange(axis=pg.ViewBox.YAxis, enable=True)

        # update total
        total = sum(current_vals)
        self.total_current_label.setText(f"Total: {total:.2f} A")

    def updateConfig(self, new_config: Dict[str, Any]) -> None:
        """Allow dynamic reconfiguration of titles, colors, and update frequency."""
        if "motor_titles" in new_config:
            self.titles = new_config["motor_titles"]
            for i, w in enumerate(self.motor_widgets):
                header = w.layout().itemAt(0).layout()
                header.itemAt(1).widget().setText(self.titles[i])

        if "motor_colors" in new_config:
            self.colors = new_config["motor_colors"]
            for i, curve in enumerate(self.curves):
                curve.setPen(pg.mkPen(color=self.colors[i], width=2))
            for i, w in enumerate(self.motor_widgets):
                sw = w.layout().itemAt(0).layout().itemAt(0).widget()
                sw.setStyleSheet(f"background-color: {self.colors[i]};")

        if "motor_update_freq" in new_config:
            self.frequency = new_config["motor_update_freq"]


class OrientationAltitudeVisualization(QWidget):
    """2×2 grid of orientation & altitude plots, with equal‐sized top and bottom rows."""
    def __init__(self, data_handler: Any) -> None:
        super().__init__()
        self.data_handler = data_handler
        self.data_handler.dataUpdated.connect(self.update_plot)
        # refresh frequency (driven externally via dataUpdated)
        self.frequency = self.data_handler.config.get("orientation_update_freq", 200)
        self.titles    = self.data_handler.config.get("orientation_titles", [])
        self.colors    = self.data_handler.config.get("orientation_colors", [])
        self.ylabels   = self.data_handler.config.get(
            "orientation_ylabels",
            ["Degrees(°)"]*3 + ["Meters(m)"]
        )

        # placeholders
        self.plots = []
        self.curves = []
        self.swatches  = [] 
        self.title_labels = []
        self.stats_labels = []

        self.initUI()

    def initUI(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4,4,4,4)

        # header with freq selector (optional)
        header = QHBoxLayout()
        header.addWidget(QLabel("<b>Orientation & Altitude</b>"))
        header.addStretch(1)
        header.addWidget(QLabel("Update Frequency:"))
        self.freq_dropdown = QComboBox()
        self.freq_dropdown.addItems(["200","500","1000","2000"])
        self.freq_dropdown.setCurrentText(str(self.frequency))
        self.freq_dropdown.currentTextChanged.connect(self.set_frequency)
        header.addWidget(self.freq_dropdown)
        main_layout.addLayout(header)

        # build four panels
        panels = [ self._make_panel(i) for i in range(4) ]

        # two horizontal splitters, one per row
        row1 = QSplitter(Qt.Orientation.Horizontal)
        row1.setHandleWidth(5)
        row1.setChildrenCollapsible(False)
        row1.addWidget(panels[0])
        row1.addWidget(panels[1])

        row2 = QSplitter(Qt.Orientation.Horizontal)
        row2.setHandleWidth(5)
        row2.setChildrenCollapsible(False)
        row2.addWidget(panels[2])
        row2.addWidget(panels[3])

        # placeholder absorbs any extra vertical space
        placeholder = QWidget()
        placeholder.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # stack row1, row2, and placeholder vertically
        main_split = QSplitter(Qt.Orientation.Vertical)
        main_split.setHandleWidth(5)
        main_split.setChildrenCollapsible(False)
        main_split.addWidget(row1)
        main_split.addWidget(row2)
        main_split.addWidget(placeholder)
        self.row_splitter = main_split

        # give row1 & row2 equal stretch, placeholder none
        main_split.setStretchFactor(0, 1)
        main_split.setStretchFactor(1, 1)
        main_split.setStretchFactor(2, 0)
        main_split.setSizes([200, 200, 1])

        main_layout.addWidget(main_split)
        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _make_panel(self, i: int) -> QWidget:
        panel = QWidget()
        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(4,4,4,4)

        # legend
        col = self.colors[i] if i < len(self.colors) else "#000000"
        leg = QHBoxLayout()
        swatch = QLabel(); swatch.setFixedSize(12,12)
        swatch.setStyleSheet(f"background-color: {col};")
        leg.addWidget(swatch)
        self.swatches.append(swatch)
        title = QLabel(self.titles[i] if i < len(self.titles) else f"Param {i+1}")
        title.setStyleSheet("font-weight:bold;")
        leg.addWidget(title)
        self.title_labels.append(title)
        leg.addStretch(1)
        vbox.addLayout(leg)

        # plot
        axis = DateAxisItem(orientation='bottom')
        plot = pg.PlotWidget(axisItems={'bottom': axis})
        
        plot.setLabel('left', self.ylabels[i])
        plot.setLabel('bottom', 'Time')
        pen = pg.mkPen(color=col, width=2)
        curve = plot.plot([], [], pen=pen)
        self.plots.append(plot)
        self.curves.append(curve)
        vbox.addWidget(plot)

        # stats: actual, min, max
        unit = '°' if i < 3 else ' m'
        stats = QHBoxLayout()
        a  = QLabel(f"Actual: 0.00{unit}")
        mi = QLabel(f"Min:    0.00{unit}")
        ma = QLabel(f"Max:    0.00{unit}")
        stats.addWidget(a); stats.addWidget(mi); stats.addWidget(ma)
        self.stats_labels.append((a, mi, ma))
        vbox.addLayout(stats)

        # separator
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        vbox.addWidget(sep)

        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return panel

    def set_frequency(self, freq_str: str) -> None:
        """Update refresh frequency (for informational / dropdown only)."""
        self.frequency = max(200, int(freq_str))

    def update_plot(self) -> None:
        """Redraw all four plots using the latest DataHandler buffers."""
        step = max(1, round(self.frequency / 200))
        # DataHandler.time_buffer holds floats
        times = list(self.data_handler.time_buffer)[::step] 

        # orientation series + altitude
        series = [
            list(self.data_handler.orientation[idx])[::step]
            if len(self.data_handler.orientation[idx]) else []
            for idx in range(3)
        ] + [
            list(self.data_handler.altitude)[::step]
            if self.data_handler.altitude else []
        ]

        for i, curve in enumerate(self.curves):
            y = series[i]
            if not y:
                continue
            curve.setData(times[:len(y)], y)
            plot = self.plots[i]
            mx = max(times)
            plot.setXRange(mx - 20, mx)

            a, mi, ma = self.stats_labels[i]
            unit = '°' if i < 3 else ' m'
            a.setText(f"Actual: {y[-1]:.2f}{unit}")
            mi.setText(f"Min:    {min(y):.2f}{unit}")
            ma.setText(f"Max:    {max(y):.2f}{unit}")

    def updateConfig(self, new_config: Dict[str, Any]) -> None:
        """Allow runtime changes to titles, colors, and refresh rate."""
        if "orientation_titles" in new_config:
            self.titles = new_config["orientation_titles"]
            for i, lbl in enumerate(self.title_labels):
                if i < len(self.titles):
                   lbl.setText(self.titles[i]) 
        if "orientation_colors" in new_config:
            self.colors = new_config["orientation_colors"]
            for i, curve in enumerate(self.curves):
                col = self.colors[i] if i < len(self.colors) else "#000000"
                curve.setPen(pg.mkPen(color=col, width=2))
                if i < len(self.swatches):
                    self.swatches[i].setStyleSheet(f"background-color: {col};")
        if "orientation_update_freq" in new_config:
            self.frequency = new_config["orientation_update_freq"]
        # immediately redraw with new settings
        self.update_plot()

class BatteryMonitoring(QWidget):
    """Visualization widget for battery monitoring."""
    def __init__(self, data_handler: Any) -> None:
        super().__init__()
        self.data_handler = data_handler
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.frequency = self.data_handler.config.get("battery_update_freq", 500)
        self.show_percentage = True
        self.initUI()

    def initUI(self) -> None:
        main_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        block_title = QLabel("Battery Monitoring")
        block_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        freq_label = QLabel("Update Frequency:")
        self.freq_dropdown = QComboBox()
        self.freq_dropdown.addItems(["200", "500", "1000", "2000"])
        self.freq_dropdown.setCurrentText(str(self.frequency))
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
        
        self.plot_widget.setLabel('left', "Battery (%)" if self.show_percentage else "Battery (V)")
        self.plot_widget.setLabel('bottom', "Time")
        main_layout.addWidget(self.plot_widget)
        self.curve = self.plot_widget.plot([], [], pen='m')
        stats_layout = QGridLayout()
        self.current_value_label = QLabel("Actual: 0.00%")
        self.min_value_label = QLabel("Min: 0.00%")
        self.max_value_label = QLabel("Max: 0.00%")
        style = " border: 1px solid grey; border-radius: 5px; padding: 2px;"
        self.current_value_label.setStyleSheet(style)
        self.min_value_label.setStyleSheet(style)
        self.max_value_label.setStyleSheet(style)
        stats_layout.addWidget(self.current_value_label, 0, 0, 1, 2)
        stats_layout.addWidget(self.min_value_label, 1, 0)
        stats_layout.addWidget(self.max_value_label, 1, 1)
        stats_outer_layout = QHBoxLayout()
        stats_outer_layout.addStretch(1)
        stats_outer_layout.addLayout(stats_layout)
        stats_outer_layout.addStretch(1)
        main_layout.addLayout(stats_outer_layout)
        self.setLayout(main_layout)

    def set_frequency(self, freq_str: str) -> None:
        self.frequency = int(freq_str)
        self.timer.setInterval(self.frequency)

    def start(self) -> None:
        self.timer.start(self.frequency)

    def stop(self) -> None:
        self.timer.stop()

    def toggle_view(self) -> None:
        self.show_percentage = not self.show_percentage
        self.plot_widget.setLabel('left', "Battery (%)" if self.show_percentage else "Battery (V)")
        self.update_plot()

    def update_plot(self) -> None:
        base_interval_ms = 200
        sampling_factor = int(round(self.frequency / base_interval_ms))
        x_data_full = list(self.data_handler.time_buffer)
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
        min_time = max_time - 20
        self.plot_widget.setXRange(min_time, max_time)
        if self.show_percentage:
            self.plot_widget.setYRange(20, 100)
        else:
            self.plot_widget.setYRange(10, 14.6)
        current = y_data[-1]
        min_val = min(y_data)
        max_val = max(y_data)
        unit = "%" if self.show_percentage else "V"
        self.current_value_label.setText(f"Actual: {current:.2f}{unit}")
        self.min_value_label.setText(f"Min: {min_val:.2f}{unit}")
        self.max_value_label.setText(f"Max: {max_val:.2f}{unit}")

    def updateConfig(self, new_config: Dict[str, Any]) -> None:
        if "battery_update_freq" in new_config:
            self.frequency = new_config["battery_update_freq"]
            self.timer.setInterval(self.frequency)
        if "battery_color" in new_config:
            new_color = new_config["battery_color"]
            self.curve.setPen(pg.mkPen(color=new_color, width=2))
        if "battery_title" in new_config:
            self.plot_widget.setLabel('left', new_config["battery_title"])
        self.update_plot()



