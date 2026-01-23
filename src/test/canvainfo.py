#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CanvasInfoWidget - 画布信息显示面板
替代QML组件,显示位置、旋转、缩放等信息
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor


class CanvasInfoWidget(QWidget):
    """画布信息显示面板"""
    
    # 信号定义
    resetSignal = pyqtSignal()  # 重置按钮信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setupUI()
        
        # 默认值
        self._posX = 0.0
        self._posY = 0.0
        self._rotate = 0.0
        self._scale = 1.0
        self._language = True  # True=中文, False=英文
        
    def _setupUI(self):
        """设置UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        
        # 标题
        title_label = QLabel("画布信息")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # 分隔线
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #cccccc;")
        main_layout.addWidget(separator)
        
        # 位置信息
        pos_layout = QHBoxLayout()
        pos_icon = QLabel("✕\n⃞")  # X/Y 图标
        pos_icon.setAlignment(Qt.AlignCenter)
        pos_icon.setFixedWidth(30)
        self.pos_label = QLabel("-0.10, -0.52")
        self.pos_label.setFont(QFont("Monospace", 9))
        pos_layout.addWidget(pos_icon)
        pos_layout.addWidget(self.pos_label)
        pos_layout.addStretch()
        main_layout.addLayout(pos_layout)
        
        # 旋转和缩放信息
        rotate_scale_layout = QHBoxLayout()
        
        # 旋转角度
        rotate_icon = QLabel("∠")
        rotate_icon.setAlignment(Qt.AlignCenter)
        rotate_icon.setFixedWidth(20)
        self.rotate_label = QLabel("0.00°")
        self.rotate_label.setFont(QFont("Monospace", 9))
        
        # 缩放倍数
        scale_icon = QLabel("⟲")
        scale_icon.setAlignment(Qt.AlignCenter)
        scale_icon.setFixedWidth(20)
        self.scale_label = QLabel("3.06x")
        self.scale_label.setFont(QFont("Monospace", 9))
        
        rotate_scale_layout.addWidget(rotate_icon)
        rotate_scale_layout.addWidget(self.rotate_label)
        rotate_scale_layout.addSpacing(10)
        rotate_scale_layout.addWidget(scale_icon)
        rotate_scale_layout.addWidget(self.scale_label)
        rotate_scale_layout.addStretch()
        main_layout.addLayout(rotate_scale_layout)
        
        # 重置按钮
        self.reset_button = QPushButton("重置")
        self.reset_button.setFixedHeight(30)
        self.reset_button.clicked.connect(self.resetSignal.emit)
        main_layout.addWidget(self.reset_button)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 230);
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
            QLabel {
                background-color: transparent;
                border: none;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        # 设置固定大小
        self.setFixedSize(200, 140)
        
    def updatePosition(self, x, y):
        """更新位置信息"""
        self._posX = x
        self._posY = y
        self.pos_label.setText(f"{x:.2f}, {y:.2f}")
    
    def updateRotate(self, angle):
        """更新旋转角度"""
        self._rotate = angle
        self.rotate_label.setText(f"{angle:.2f}°")
    
    def updateScale(self, scale):
        """更新缩放倍数"""
        self._scale = scale
        self.scale_label.setText(f"{scale:.2f}x")
    
    def setLanguage(self, is_chinese):
        """设置语言"""
        self._language = is_chinese
        if is_chinese:
            self.findChild(QLabel, "").setText("画布信息")  # 标题
            self.reset_button.setText("重置")
        else:
            self.findChild(QLabel, "").setText("Canvas Info")
            self.reset_button.setText("Reset")
    
    def setCanvasInfoVisible(self, visible):
        """设置可见性"""
        self.setVisible(visible)


# 测试代码
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QGraphicsView
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    view = QGraphicsView()
    view.setFixedSize(800, 600)
    
    # 创建信息面板
    info_widget = CanvasInfoWidget(view)
    info_widget.move(10, view.height() - info_widget.height() - 10)
    info_widget.updatePosition(-0.10, -0.52)
    info_widget.updateRotate(0.00)
    info_widget.updateScale(3.06)
    
    # 连接重置信号
    info_widget.resetSignal.connect(lambda: print("Reset clicked!"))
    
    view.show()
    
    sys.exit(app.exec_())