#from server import Server
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QObject, Signal, QProcess

from main_window import MainWindow
#from server import Server

class Controller:
    def __init__(self) -> None:
        # Use QApplication(sys.argv) to allow command line 
        # else use QApplication([])
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow(controller=self)
        #self.server = Server(controller=self)
        self.p = None

    def run_app(self):
        self.main_window.show()
        return self.app.exec_()

    def data_ready_callback(self, arg):
        pass
    
    def message(self, s):
        self.main_window.control_panel.raw_data_panel.txt_box.appendPlainText(s)
        self.main_window.screen.update(s)

    def start_process(self):
        if self.p is None:  # No process running.
            self.message("Executing process")
            self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.
            self.p.start("python3", ['../socket_server.py'])
            self.main_window.control_panel.raw_data_panel.btn.setText('Stop server')
        else:
            self.p.terminate()
            self.main_window.control_panel.raw_data_panel.btn.setText('Start server')

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)
        # Extract progress if it is in the data.
        # progress = simple_percent_parser(stderr)
        # if progress:
        #     self.progress.setValue(progress)
        # self.message(stderr)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def process_finished(self):
        self.message("Process finished.")
        self.main_window.control_panel.raw_data_panel.btn.setText('Start server')
        self.p = None

class AcquisitionWorker(QObject): 
    #finished  = Signal()
    data_ready = Signal()

    def __init__(self) -> None:
        super().__init__()

    def run(self):
        pass
