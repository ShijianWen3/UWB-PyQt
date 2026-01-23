from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QMessageBox
from PyQt5.QtCore import Qt


from compile import compile_ui_file, compile_qrc_file
compile_ui_file('mainwindow')
compile_qrc_file('resources')

from ui_py.ui_mainwindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
     