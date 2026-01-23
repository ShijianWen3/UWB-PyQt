#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MainWindow - 集成主窗口类
重写Qt-cpp项目的MainWindow，集成所有独立组件
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QSplitter, QDockWidget, QAction, 
                           QMenuBar, QToolBar, QStatusBar, QMessageBox, 
                           QFileDialog, QTabWidget, QFrame, QLabel)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QPixmap, QFont

# 导入各个组件
from connect_widget import ConnectionWidget
from graphic_widget import GraphicsWidget
from view_settings_widget import ViewSettingsWidget




import resources_rc  # 导入编译后的资源文件

class MainWindow(QMainWindow):
    """主窗口类 - 集成所有组件"""
    
    # 应用程序信号
    appReady = pyqtSignal()
    windowClosed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # 初始化成员变量
        self._connection_widget = None
        self._graphics_widget = None
        self._view_settings_widget = None
        self._is_maximized = False
        self._geometry_saved = False
        
        # 设置窗口属性
        self.setWindowTitle("RTL Display Application - PyQt5")
        self.setWindowIcon(self._create_app_icon())
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 启动定时器
        self._init_timers()
        
    def _create_app_icon(self):
        """创建应用程序图标"""
        # 如果没有图标文件，创建一个简单的彩色图标
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.blue)
        return QIcon(pixmap)
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        self._create_central_widget()
        
        # 创建停靠窗口
        self._create_dock_widgets()
        
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建工具栏
        self._create_tool_bar()
        
        # 创建状态栏
        self._create_status_bar()
        
        # 设置窗口大小和位置
        self._setup_window_geometry()
        
    def _create_central_widget(self):
        """创建中央部件 - 主要显示区域"""
        # 创建主部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(2, 2, 2, 2)
        
        # 创建分割器
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # 创建左侧面板
        self._create_left_panel()
        
        # 创建右侧主显示区域
        self._create_right_panel()
        
    def _create_left_panel(self):
        """创建左侧面板"""
        # 创建左侧面板容器
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(2)
        left_layout.setContentsMargins(2, 2, 2, 2)
        
        # 创建标签页控件
        self.left_tabs = QTabWidget()
        left_layout.addWidget(self.left_tabs)
        
        # 添加连接控制组件
        # self._connection_widget = ConnectionWidget()
        # self.left_tabs.addTab(self._connection_widget, "连接控制")
        
        # 添加视图设置组件
        self._view_settings_widget = ViewSettingsWidget()
        self.left_tabs.addTab(self._view_settings_widget, "视图设置")
        
        # 设置左侧面板大小策略
        left_panel.setMaximumWidth(400)
        left_panel.setMinimumWidth(300)
        
        # 添加到主分割器
        self.main_splitter.addWidget(left_panel)
        
    def _create_right_panel(self):
        """创建右侧主显示区域"""
        # 创建右侧面板容器
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(2)
        right_layout.setContentsMargins(2, 2, 2, 2)
        
        # 创建图形显示组件
        self._graphics_widget = GraphicsWidget()
        right_layout.addWidget(self._graphics_widget)
        
        # 添加到主分割器
        self.main_splitter.addWidget(right_panel)
        
        # 设置分割器比例
        self.main_splitter.setStretchFactor(0, 1)  # 左侧
        self.main_splitter.setStretchFactor(1, 3)  # 右侧
        
    def _create_dock_widgets(self):
        """创建停靠窗口"""
        # 创建状态信息停靠窗口
        self._create_status_dock()
        
        # 创建日志停靠窗口
        self._create_log_dock()
        
    def _create_status_dock(self):
        """创建状态信息停靠窗口"""
        # 创建停靠窗口
        status_dock = QDockWidget("系统状态", self)
        status_dock.setObjectName("StatusDock")
        status_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        
        # 创建状态显示部件
        status_widget = QWidget()
        status_layout = QVBoxLayout(status_widget)
        
        # 添加状态标签
        self.status_label = QLabel("系统就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        # 添加连接状态
        self.connection_status_label = QLabel("连接状态: 未连接")
        status_layout.addWidget(self.connection_status_label)
        
        status_dock.setWidget(status_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, status_dock)
        
    def _create_log_dock(self):
        """创建日志停靠窗口"""
        # 创建停靠窗口
        log_dock = QDockWidget("运行日志", self)
        log_dock.setObjectName("LogDock")
        log_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        
        # 创建日志显示部件
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        
        # 创建日志文本区域
        from PyQt5.QtWidgets import QTextEdit
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setMaximumHeight(150)
        log_layout.addWidget(self.log_text_edit)
        
        log_dock.setWidget(log_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, log_dock)
        
        # 默认隐藏日志窗口
        log_dock.hide()
        
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        # 新建动作
        new_action = QAction('新建(&N)', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self._on_new_file)
        file_menu.addAction(new_action)
        
        # 打开动作
        open_action = QAction('打开(&O)...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)
        
        # 保存动作
        save_action = QAction('保存(&S)', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self._on_save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # 退出动作
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图(&V)')
        
        # 显示/隐藏停靠窗口
        show_status_action = QAction('显示状态窗口', self)
        show_status_action.setCheckable(True)
        show_status_action.setChecked(True)
        show_status_action.triggered.connect(self._toggle_status_dock)
        view_menu.addAction(show_status_action)
        
        show_log_action = QAction('显示日志窗口', self)
        show_log_action.setCheckable(True)
        show_log_action.setChecked(False)
        show_log_action.triggered.connect(self._toggle_log_dock)
        view_menu.addAction(show_log_action)
        
        view_menu.addSeparator()
        
        # 全屏动作
        fullscreen_action = QAction('全屏模式', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具(&T)')
        
        # 连接动作
        connect_action = QAction('连接设备', self)
        connect_action.triggered.connect(self._on_connect_device)
        tools_menu.addAction(connect_action)
        
        # 断开连接动作
        disconnect_action = QAction('断开连接', self)
        disconnect_action.triggered.connect(self._on_disconnect_device)
        tools_menu.addAction(disconnect_action)
        
        tools_menu.addSeparator()
        
        # 校准动作
        calibrate_action = QAction('校准', self)
        calibrate_action.triggered.connect(self._on_calibrate)
        tools_menu.addAction(calibrate_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu('设置(&S)')
        
        # 首选项动作
        preferences_action = QAction('首选项...', self)
        preferences_action.triggered.connect(self._on_preferences)
        settings_menu.addAction(preferences_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        # 关于动作
        about_action = QAction('关于(&A)...', self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
        
    def _create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar('主工具栏')
        toolbar.setObjectName('MainToolBar')
        self.addToolBar(toolbar)
        
        # 添加新建按钮
        new_btn = toolbar.addAction('新建')
        new_btn.triggered.connect(self._on_new_file)
        
        # 添加打开按钮
        open_btn = toolbar.addAction('打开')
        open_btn.triggered.connect(self._on_open_file)
        
        # 添加保存按钮
        save_btn = toolbar.addAction('保存')
        save_btn.triggered.connect(self._on_save_file)
        
        toolbar.addSeparator()
        
        # 添加连接按钮
        connect_btn = toolbar.addAction('连接')
        connect_btn.triggered.connect(self._on_connect_device)
        
        # 添加断开连接按钮
        disconnect_btn = toolbar.addAction('断开')
        disconnect_btn.triggered.connect(self._on_disconnect_device)
        
        toolbar.addSeparator()
        
        # 添加校准按钮
        calibrate_btn = toolbar.addAction('校准')
        calibrate_btn.triggered.connect(self._on_calibrate)
        
    def _create_status_bar(self):
        """创建状态栏"""
        statusbar = self.statusBar()
        
        # 添加状态标签
        self.status_label_main = QLabel('就绪')
        statusbar.addWidget(self.status_label_main)
        
        statusbar.addPermanentWidget(QLabel('|'))
        
        # 添加连接状态指示器
        self.connection_indicator = QLabel('●')
        self.connection_indicator.setStyleSheet('color: red; font-size: 16px;')
        statusbar.addPermanentWidget(QLabel('连接:'))
        statusbar.addPermanentWidget(self.connection_indicator)
        
        statusbar.addPermanentWidget(QLabel('|'))
        
        # 添加坐标显示
        self.coordinate_label = QLabel('X: 0.00, Y: 0.00')
        statusbar.addPermanentWidget(self.coordinate_label)
        
        statusbar.addPermanentWidget(QLabel('|'))
        
        # 添加时间显示
        self.time_label = QLabel('00:00:00')
        statusbar.addPermanentWidget(self.time_label)
        
    def _setup_window_geometry(self):
        """设置窗口几何属性"""
        # 设置初始大小
        self.resize(1200, 800)
        
        # 居中显示
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_rect = desktop.availableGeometry()
        self.move((screen_rect.width() - self.width()) // 2,
                 (screen_rect.height() - self.height()) // 2)
        
    def _connect_signals(self):
        """连接所有组件的信号"""
        # 连接图形组件的信号
        if self._graphics_widget:
            # 连接坐标更新信号
            self._graphics_widget.centerAt.connect(self._update_coordinate_display)
            
            # 连接视图大小改变信号
            self._graphics_widget.viewSizeChange.connect(self._on_view_size_changed)
            
        # 连接视图设置组件的信号
        if self._view_settings_widget:
            # 连接保存设置信号
            self._view_settings_widget.saveViewSettings.connect(self._on_save_settings)
            
        # 连接连接控制组件的信号
        if self._connection_widget:
            # 这里可以连接连接控制的相关信号
            pass
            
    def _init_timers(self):
        """初始化定时器"""
        # 创建更新时间显示的定时器
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self._update_time_display)
        self.time_timer.start(1000)  # 每秒更新一次
        
        # 创建状态检查定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._check_system_status)
        self.status_timer.start(5000)  # 每5秒检查一次
        
    def _update_time_display(self):
        """更新时间显示"""
        from datetime import datetime
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_label.setText(current_time)
        
    def _check_system_status(self):
        """检查系统状态"""
        # 这里可以添加系统状态检查逻辑
        pass
        
    def _update_coordinate_display(self, x, y):
        """更新坐标显示"""
        self.coordinate_label.setText(f'X: {x:.2f}, Y: {y:.2f}')
        
    def _on_view_size_changed(self, size):
        """视图大小改变处理"""
        # 可以在这里处理视图大小改变的逻辑
        pass
        
    def _on_save_settings(self):
        """保存设置处理"""
        self.log_message("设置已保存")
        
    def _toggle_status_dock(self):
        """切换状态窗口显示"""
        dock = self.findChild(QDockWidget, "StatusDock")
        if dock:
            dock.setVisible(not dock.isVisible())
            
    def _toggle_log_dock(self):
        """切换日志窗口显示"""
        dock = self.findChild(QDockWidget, "LogDock")
        if dock:
            dock.setVisible(not dock.isVisible())
            
    def _toggle_fullscreen(self):
        """切换全屏模式"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
    def _on_new_file(self):
        """新建文件处理"""
        reply = QMessageBox.question(self, '新建项目', 
                                   '创建新项目将清除当前数据，是否继续？',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 清除当前数据
            if self._graphics_widget:
                self._graphics_widget.clearTags()
            self.log_message("已创建新项目")
            
    def _on_open_file(self):
        """打开文件处理"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开配置文件", "", 
            "配置文件 (*.xml);;所有文件 (*.*)")
        
        if file_path and self._graphics_widget:
            self._graphics_widget.loadConfigFile(file_path)
            self.log_message(f"已加载配置文件: {file_path}")
            
    def _on_save_file(self):
        """保存文件处理"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存配置文件", "", 
            "配置文件 (*.xml);;所有文件 (*.*)")
        
        if file_path and self._graphics_widget:
            self._graphics_widget.saveConfigFile(file_path)
            self.log_message(f"已保存配置文件: {file_path}")
            
    def _on_connect_device(self):
        """连接设备处理"""
        # 这里可以实现设备连接逻辑
        self.connection_indicator.setStyleSheet('color: green; font-size: 16px;')
        self.connection_status_label.setText("连接状态: 已连接")
        self.log_message("设备已连接")
        
    def _on_disconnect_device(self):
        """断开连接处理"""
        # 这里可以实现设备断开逻辑
        self.connection_indicator.setStyleSheet('color: red; font-size: 16px;')
        self.connection_status_label.setText("连接状态: 未连接")
        self.log_message("设备已断开")
        
    def _on_calibrate(self):
        """校准处理"""
        if self._graphics_widget:
            self._graphics_widget.calibrationButtonClicked()
            self.log_message("开始校准")
            
    def _on_preferences(self):
        """首选项处理"""
        QMessageBox.information(self, "首选项", "首选项设置功能待实现")
        
    def _on_about(self):
        """关于对话框"""
        QMessageBox.about(self, "关于 RTL Display Application",
                         "RTL Display Application v1.0\n\n"
                         "基于PyQt5重写的RTL显示应用程序\n\n"
                         "作者: AI Assistant\n"
                         "版本: 1.0.0")
        
    def log_message(self, message):
        """添加日志消息"""
        if hasattr(self, 'log_text_edit'):
            timestamp = QTimer().currentTime().toString("HH:mm:ss")
            self.log_text_edit.append(f"[{timestamp}] {message}")
            
    def update_status(self, message):
        """更新状态信息"""
        if hasattr(self, 'status_label_main'):
            self.status_label_main.setText(message)
            
    def set_connection_status(self, connected):
        """设置连接状态"""
        if connected:
            self.connection_indicator.setStyleSheet('color: green; font-size: 16px;')
            self.connection_status_label.setText("连接状态: 已连接")
        else:
            self.connection_indicator.setStyleSheet('color: red; font-size: 16px;')
            self.connection_status_label.setText("连接状态: 未连接")
            
    def get_graphics_widget(self):
        """获取图形显示组件"""
        return self._graphics_widget
        
    def get_connection_widget(self):
        """获取连接控制组件"""
        return self._connection_widget
        
    def get_view_settings_widget(self):
        """获取视图设置组件"""
        return self._view_settings_widget
        
    def closeEvent(self, event):
        """关闭事件处理"""
        reply = QMessageBox.question(self, '确认退出',
                                   '确定要退出应用程序吗？',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 保存窗口几何状态
            self._save_geometry()
            
            # 发出窗口关闭信号
            self.windowClosed.emit()
            
            event.accept()
        else:
            event.ignore()
            
    def _save_geometry(self):
        """保存窗口几何状态"""
        # 这里可以保存窗口的几何状态到配置文件
        pass
        
    def showEvent(self, event):
        """显示事件处理"""
        super().showEvent(event)
        
        # 应用程序准备就绪后发出信号
        if not self._geometry_saved:
            self.appReady.emit()
            self._geometry_saved = True
            
    def resizeEvent(self, event):
        """大小改变事件处理"""
        super().resizeEvent(event)
        # 可以在这里处理窗口大小改变的逻辑
        
    def keyPressEvent(self, event):
        """键盘按键事件处理"""
        if event.key() == Qt.Key_F11:
            self._toggle_fullscreen()
        elif event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
        else:
            super().keyPressEvent(event)
            
    # 提供给外部调用的便捷方法
    def show_status_message(self, message, timeout=5000):
        """显示状态栏消息"""
        self.statusBar().showMessage(message, timeout)
        
    def enable_ui(self, enable=True):
        """启用/禁用UI"""
        self.setEnabled(enable)
        
    def set_wait_cursor(self):
        """设置等待光标"""
        from PyQt5.QtGui import QCursor
        self.setCursor(QCursor(Qt.WaitCursor))
        
    def restore_cursor(self):
        """恢复光标"""
        from PyQt5.QtGui import QCursor
        self.setCursor(QCursor(Qt.ArrowCursor))


# 全局主窗口实例
main_window = None

def create_main_window():
    """创建主窗口"""
    global main_window
    main_window = MainWindow()
    return main_window

def get_main_window():
    """获取主窗口实例"""
    global main_window
    return main_window


if __name__ == '__main__':
    # 设置DPI策略
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = create_main_window()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())