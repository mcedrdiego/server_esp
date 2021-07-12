
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
		pen_ch1 = pg.mkPen(color="b", width=1)
		# self.setXRange(0,1, padding=0.02)
		self.setXRange(-1000, 0)
		self.maxSize = 5000
		self.y = []
		self.x =  list(range(-self.maxSize, 0))
		self.counter = 0
		self.data_plot = self.plot(pen = pen_ch1)

	def update_ch(self, d):
		if self.counter < self.maxSize:
			self.y.append(d)
			self.data_plot.setData(list(range(-len(self.y), 0)), self.y)
		else:
			self.y.pop(0)
			self.y.append(d)
			self.data_plot.setData(self.x, self.y)
			
	def update(self, s):
		data = s.replace('[', '').replace(']','').strip(',').replace(',','').split()
		for i in range(len(data)):
			self.update_ch(int(data[i]))

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
