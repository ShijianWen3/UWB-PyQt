from pathlib import Path
from PyQt5.QtWidgets import QApplication, QFileDialog, QPushButton, QMessageBox, QWidget
from PyQt5.QtCore import Qt
from PyQt5 import uic
import sys
import os

from compile import compile_ui_file
compile_ui_file('connect_widget')

from ui_py.ui_connect_widget import Ui_ConnectionWidget

class ConnectionWidget(QWidget, Ui_ConnectionWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
     
if __name__ == '__main__':

        # 设置DPI策略
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)

    window = ConnectionWidget()
    window.show()
    
    sys.exit(app.exec_())