# main.py
import sys
import logging

from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QPalette, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QMessageBox, QLabel
)

import pyqtgraph as pg

# ── local modules -----------------------------------------------------------
from ui.main_window   import MainWindow          # dashboard / camera / reload tabs
from config_manager   import load_config, ConfigTab
from data_handler     import DataHandler
from utils.logging_setup import setup_logging
# ----------------------------------------------------------------------------


class ExtendedMainWindow(QMainWindow):
    """Hosts the dashboard & configuration tabs + theme switching."""

    def __init__(self, data_handler: DataHandler) -> None:
        super().__init__()
        self.data_handler = data_handler
        self.setWindowTitle("Drone Telemetry Dashboard")

        # ---------- UI theme on first launch --------------------------------
        self.current_light_mode = self.data_handler.config.get("light_mode", False)
        self._apply_theme(self.current_light_mode)

        # ---------- Central tabs --------------------------------------------
        self.dashboard  = MainWindow(self.data_handler)
        self.config_tab = ConfigTab()
        self.config_tab.configUpdated.connect(self.update_dashboard_config)

        tabs = QTabWidget()
        tabs.addTab(self.dashboard,  "Dashboard")
        tabs.addTab(self.config_tab, "Configuration")
        self.setCentralWidget(tabs)

    # --------------------------------------------------------------------- theme

    def _apply_theme(self, light_on: bool) -> None:
        """Set Qt palette + PyQtGraph defaults and recolour existing widgets."""
        app = QApplication.instance()

        if light_on:
            palette = QApplication.style().standardPalette()            # new
            fg = "#000000"
        else:
            palette = QPalette()                                        # new
            base = QColor(15, 15, 15)
            palette.setColor(QPalette.ColorRole.Window,         base)
            palette.setColor(QPalette.ColorRole.WindowText,     Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base,           base)
            palette.setColor(QPalette.ColorRole.AlternateBase,  QColor(30, 30, 30))
            palette.setColor(QPalette.ColorRole.Text,           Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button,         base)
            palette.setColor(QPalette.ColorRole.ButtonText,     Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Highlight,      QColor(42, 130, 218))
            fg = "#ffffff"

        app.setPalette(palette)
        pg.setConfigOption("background", palette.color(QPalette.ColorRole.Base).name())
        pg.setConfigOption("foreground", fg)

        self._recolor_pg_widgets(light_on)
        self.current_light_mode = light_on

    # --------------------------------------------------------------------- recolor

    def _recolor_pg_widgets(self, light_on: bool) -> None:
        """Re-skin every existing PlotWidget and QLabel."""
        from PyQt6.QtWidgets import QLabel
        from pyqtgraph import PlotWidget, mkPen

        bg = "#ffffff" if light_on else \
             QApplication.palette().color(QPalette.ColorRole.Base).name()
        fg = "#000000" if light_on else "#ffffff"

        # ---- PyQtGraph plots --------------------------------------------
        for pw in self.findChildren(PlotWidget):
            pi = pw.getPlotItem()
            pw.setBackground(bg)

            # axes
            for ax_name in ("left", "bottom", "right", "top"):
                ax = pi.getAxis(ax_name)
                if ax is None:
                    continue
                try:
                    ax.setPen(mkPen(fg))
                    ax.setTextPen(mkPen(fg))
                except Exception:
                    pass  # older pg versions

            # title
            lbl = getattr(pi, "titleLabel", None)
            if lbl is not None:
                try:                    # pg ≥ 0.14
                    lbl.setColor(fg)
                except AttributeError:  # pg ≤ 0.13
                    try:
                        lbl.setAttr("color", fg)
                    except Exception:
                        txt = getattr(lbl, "text", lbl.toPlainText())
                        lbl.setText(txt, color=fg)

            # legend
            leg = getattr(pi, "legend", None)
            if leg is not None:
                for _, html_lbl in leg.items:
                    try:
                        html_lbl.setAttr("color", fg)          # pg ≥ 0.13
                    except Exception:
                        s = html_lbl.styleSheet()
                        html_lbl.setStyleSheet(
                            f"{s.split(';')[0]}; color: {fg};")

        # ---- Any QLabel stats / titles ----------------------------------
        for lbl in self.findChildren(QLabel):
            ss = lbl.styleSheet()
            if "background-color" in ss:
                continue

            tokens = [t for t in ss.split(";") if "color:" not in t]
            lbl.setStyleSheet(";".join(tokens) + f"; color: {fg};")

                # ---- Receiver QProgressBars  ------------------------------------
        from PyQt6.QtWidgets import QProgressBar
        for bar in self.findChildren(QProgressBar):
            bar.setStyleSheet("")

        

    # --------------------------------------------------------------------- config

    def update_dashboard_config(self, new_config: dict) -> None:
        """Propagate changes & always re-apply theme."""
        self.data_handler.updateConfig(new_config)
        self.dashboard.updateConfig(new_config)
        logging.info("Dashboard configuration updated.")

        self._apply_theme(new_config.get("light_mode", self.current_light_mode))

    # --------------------------------------------------------------------- window

    def closeEvent(self, event):
        if self.data_handler.timer.isActive() or self.data_handler.running:
            self.data_handler.stop()
        super().closeEvent(event)


# ── script entry-point --------------------------------------------------------

def main() -> None:
    setup_logging()
    logging.info("Starting Drone Telemetry Dashboard…")

    # QApplication must exist before QTimer
    app = QApplication(sys.argv)

    # Configuration and DataHandler
    config = load_config()
    data_handler = DataHandler(config)
    data_handler.start()

    # Main window
    window = ExtendedMainWindow(data_handler)
    window.showMaximized()

    # Ensure we stop the handler on app quit 
    app.aboutToQuit.connect(data_handler.stop)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
