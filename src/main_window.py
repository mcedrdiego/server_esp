#!/home/apehooman/.virtualenvs/env/bin/python
from PySide6.QtWidgets import (
    QMainWindow, 
    QPushButton, 
    QWidget, 
    QHBoxLayout, 
    QVBoxLayout, 
    QGroupBox, 
    QLabel, 
    QFrame,
    QPlainTextEdit)
import numpy as np
import pyqtgraph as pg


class GraphScreen(pg.PlotWidget):
    def __init__(self, controller, parent=None, background="w", plotItem=None, **kargs):
        super().__init__(parent=parent, background=background, plotItem=plotItem, **kargs)

        styles = {"color": "k", "font-size": "12px"}
        self.controller = controller
        self.setLabel("left", "Current" ,"mA", **styles)
        self.setLabel("bottom", "Time" ,"s", **styles)
        self.showGrid(x=True,y=True)
        self.pen_ch1 = pg.mkPen(color="b", width=1)
        # self.setXRange(0,1, padding=0.02)
        self.setXRange(-10, 0)
        # self.setYRange(0, 5, padding=0.02)
        self.chunkSize = 1000
        self.data = np.empty((self.chunkSize+1, 2))
        self.ptr = 0
        self.curves = []
        self.startTime = pg.ptime.time()
        self.maxChunks = 10
    
    def plot_ch(self, x, y, ch=1):
        self.data_line_ch = self.plot(x, y, pen = self.pen_ch1)

    def update_ch(self, d):
        now = pg.ptime.time()
        for c in self.curves:
            c.setPos(-(now-self.startTime), 0)
        i = self.ptr % self.chunkSize
        if i == 0:
            curve = self.plot(pen=self.pen_ch1)
            self.curves.append(curve)
            last = self.data[-1]
            self.data = np.empty((self.chunkSize+1, 2))
            self.data[0] = last
            while len(self.curves) > self.maxChunks:
                c = self.curves.pop(0)
                self.removeItem(c)
        else:
            curve = self.curves[-1]
        self.data[i+1,0] = now - self.startTime
        self.data[i+1,1] = d # adds only one point but the ESP32 sends 30k at once 
        curve.setData(x=self.data[:i+2, 0], y=self.data[:i+2, 1]) # plots all available
        self.ptr += 1

    def update(self, s):
    	data = s.replace('[', '').replace(']','').strip(',').split()
    	for i in len(data):
    		self.update_ch(int(data[i])
    
    # def update_ch(self, x, y, ch = 1):
    #     self.data_line_ch.setData(x, y)

class StatsBox(QGroupBox):
    def __init__(self) -> None: # may need change
        super().__init__("Stats")
        self.esp_addr_label  = QLabel("Mac")
        
        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Sensor Address:"))
        layout.addWidget(self.esp_addr_label)

class RawDataBox(QGroupBox):
    def __init__(self, controller, parent=None) -> None:
        super().__init__("Raw Data", parent=parent)
        self.controller = controller

        self.txt_box = QPlainTextEdit()
        self.txt_box.setReadOnly(True) 
        self.btn = QPushButton("Start Server")
        self.btn.pressed.connect(self.controller.start_process)
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.txt_box)
        layout.addWidget(self.btn)
        
class ControlPanel(QFrame):
    def __init__(self, controller, parent = None ):
        super().__init__(parent=parent)
        self.controller = controller
        self.setFrameStyle(QFrame.StyledPanel)
        
        self.stats_panel = StatsBox()
        self.raw_data_panel = RawDataBox(self.controller)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.stats_panel)
        self.layout.addStretch()  
        self.layout.addWidget(self.raw_data_panel)
        ''' adds space between boxes'''
        self.setMaximumWidth(350)
        self.setLayout(self.layout)

class MainWindow(QMainWindow):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.controller = controller
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Current Sensor")

        self.screen = GraphScreen(self.controller)
        self.control_panel = ControlPanel(self.controller)
        self.content_layout = QHBoxLayout()
        self.content_layout.addWidget(self.screen)
        self.content_layout.addWidget(self.control_panel)
        # self.setMinimumSize(QSize())
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(self.content_layout)
