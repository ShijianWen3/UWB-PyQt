#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app_main - RTL Display Application 主入口
整合所有组件的完整应用程序
"""

import sys
import os
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

# 添加项目路径到系统路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from compile import compile_qrc_file
compile_qrc_file('resources')

# 导入主窗口
from mainwindow_test import MainWindow, create_main_window

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rtl_display.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class RTLDisplayApplication:
    """RTL Display 应用程序类"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self._is_ready = False
        
    def initialize(self):
        """初始化应用程序"""
        try:
            # 设置应用程序属性
            self._setup_application()
            
            # 创建主窗口
            self._create_main_window()
            
            # 连接信号
            self._connect_signals()
            
            # 设置定时器
            self._setup_timers()
            
            logger.info("应用程序初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"应用程序初始化失败: {e}")
            return False
            
    def _setup_application(self):
        """设置应用程序属性"""
        # 设置高DPI支持
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
            
        # 创建应用程序实例
        self.app = QApplication(sys.argv)
        
        # 设置应用程序信息
        self.app.setApplicationName("RTL Display Application")
        self.app.setApplicationDisplayName("RTL Display")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("RTL Display Team")
        self.app.setOrganizationDomain("rtl-display.com")
        
    def _create_main_window(self):
        """创建主窗口"""
        self.main_window = create_main_window()
        
        # 设置窗口图标
        icon = self._create_application_icon()
        self.main_window.setWindowIcon(icon)
        
    def _create_application_icon(self):
        """创建应用程序图标"""
        from PyQt5.QtGui import QPixmap, QPainter, QColor
        from PyQt5.QtCore import QRect
        
        # 创建简单的图标
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制蓝色圆形背景
        painter.setBrush(QColor(41, 128, 185))
        painter.setPen(QColor(52, 152, 219))
        painter.drawEllipse(QRect(4, 4, 56, 56))
        
        # 绘制白色"RTL"文字
        painter.setPen(Qt.white)
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "RTL")
        
        painter.end()
        return QIcon(pixmap)
        
    def _connect_signals(self):
        """连接信号"""
        if self.main_window:
            # 连接应用程序就绪信号
            self.main_window.appReady.connect(self._on_app_ready)
            
            # 连接窗口关闭信号
            self.main_window.windowClosed.connect(self._on_window_closed)
            
            # 连接组件间的信号
            self._connect_component_signals()
            
    def _connect_component_signals(self):
        """连接组件间的信号"""
        if not self.main_window:
            return
            
        graphics_widget = self.main_window.get_graphics_widget()
        view_settings_widget = self.main_window.get_view_settings_widget()
        connection_widget = self.main_window.get_connection_widget()
        
        # 连接视图设置到图形组件的信号
        if view_settings_widget and graphics_widget:
            # 标签历史显示
            # view_settings_widget.tagHistoryShowClicked.connect(
            #     graphics_widget.setShowTagHistory)
            
            # 标签历史数量
            # view_settings_widget.tagHistoryNumberValueChanged.connect(
            #     graphics_widget.tagHistoryNumber)
            
            pass
            
        # 连接连接控制到图形组件的信号
        if connection_widget and graphics_widget:
            # 这里可以添加连接相关的信号连接
            pass
            
    def _setup_timers(self):
        """设置定时器"""
        # 创建系统状态检查定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._check_system_status)
        self.status_timer.start(5000)  # 5秒检查一次
        
        # 创建性能监控定时器
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self._check_performance)
        self.performance_timer.start(10000)  # 10秒检查一次
        
    def _check_system_status(self):
        """检查系统状态"""
        if self.main_window and self._is_ready:
            # 这里可以添加系统状态检查逻辑
            pass
            
    def _check_performance(self):
        """检查性能"""
        # 这里可以添加性能监控逻辑
        pass
        
    def _on_app_ready(self):
        """应用程序就绪处理"""
        self._is_ready = True
        logger.info("应用程序已就绪")
        
        # 可以在这里执行应用程序启动后的初始化操作
        self._post_init_setup()
        
    def _on_window_closed(self):
        """窗口关闭处理"""
        logger.info("主窗口已关闭")
        self._is_ready = False
        
    def _post_init_setup(self):
        """应用程序启动后的设置"""
        if not self.main_window:
            return
            
        # 设置初始状态
        self.main_window.update_status("应用程序就绪")
        self.main_window.show_status_message("RTL Display Application 已启动", 3000)
        
        # 加载默认配置
        self._load_default_config()
        
    def _load_default_config(self):
        """加载默认配置"""
        try:
            # 这里可以加载默认配置文件
            config_file = "default_config.xml"
            if os.path.exists(config_file):
                if self.main_window.get_graphics_widget():
                    self.main_window.get_graphics_widget().loadConfigFile(config_file)
                    logger.info(f"已加载默认配置: {config_file}")
            else:
                logger.info("未找到默认配置文件，使用默认设置")
                
        except Exception as e:
            logger.warning(f"加载默认配置失败: {e}")
            
    def run(self):
        """运行应用程序"""
        if not self.initialize():
            return 1
            
        try:
            # 显示主窗口
            self.main_window.show()
            
            # 运行事件循环
            return self.app.exec_()
            
        except Exception as e:
            logger.error(f"应用程序运行错误: {e}")
            return 1
            
    def shutdown(self):
        """关闭应用程序"""
        logger.info("正在关闭应用程序...")
        
        # 停止定时器
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        if hasattr(self, 'performance_timer'):
            self.performance_timer.stop()
            
        # 保存设置
        self._save_settings()
        
        logger.info("应用程序已关闭")
        
    def _save_settings(self):
        """保存设置"""
        try:
            # 这里可以保存应用程序设置
            if self.main_window and self.main_window.get_graphics_widget():
                # 保存图形组件的配置
                pass
                
        except Exception as e:
            logger.warning(f"保存设置失败: {e}")


def main():
    """主函数"""
    try:
        # 创建应用程序实例
        app_instance = RTLDisplayApplication()
        
        # 运行应用程序
        exit_code = app_instance.run()
        
        # 清理
        app_instance.shutdown()
        
        return exit_code
        
    except Exception as e:
        logger.error(f"应用程序启动失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())