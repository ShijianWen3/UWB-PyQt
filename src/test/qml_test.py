import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtGui import QColor
import resources_rc  # 导入编译后的资源文件

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QML Display Test")
        self.setGeometry(100, 100, 800, 600)  # 设置窗口大小
        
        # 创建 QQuickWidget 组件并将其添加到窗口
        self.m_QQuickWidget = QQuickWidget(self)
        self.m_QQuickWidget.setSource(QUrl("qrc:/qml/CanvasInformation.qml"))
        self.m_QQuickWidget.resize(800, 600)  # 设置大小，防止显示不出来
        self.m_QQuickWidget.move(0, 0)
        
        # 设置 QQuickWidget 背景透明
        self.m_QQuickWidget.setClearColor(QColor(Qt.transparent))
        
        # 添加 QQuickWidget 到主窗口
        self.setCentralWidget(self.m_QQuickWidget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()  # 显示窗口
    sys.exit(app.exec_())  # 启动应用程序事件循环
