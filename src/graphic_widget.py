#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GraphicsWidget - 完整的图形界面组件
基于CPP源码重写的PyQt5版本
"""
from compile import compile_ui_file
compile_ui_file('graphics_widget')
from ui_py.ui_graphics_widget import Ui_GraphicsWidget
import resources_rc

from PyQt5.QtWidgets import (QWidget, QGraphicsScene, QTableWidgetItem, 
                           QGraphicsSimpleTextItem, QGraphicsEllipseItem,
                           QGraphicsRectItem, QGraphicsPolygonItem,
                           QGraphicsLineItem, QGraphicsPixmapItem,
                           QMessageBox, QFileDialog, QDesktopWidget)
from PyQt5.QtCore import Qt, QPointF, QTimer, pyqtSignal, QRectF
from PyQt5.QtGui import QBrush, QPen, QColor, QPolygonF, QPixmap
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtCore import QUrl
import math
import xml.etree.ElementTree as ET

from graphic_view import GraphicsView  # 导入GraphicsView类

# 定义结构体
class Tag:
    def __init__(self):
        self.id = 0
        self.idx = 0
        self.ridx = 0
        self.p = [None] * 100  # 历史位置点
        self.avgp = None  # 平均位置点
        self.r95p = None  # R95圆
        self.geop = None  # 地理围栏圆
        self.circle = [None] * 8  # 定位圆
        self.r95Show = False
        self.LocatingcircleShow = [False] * 100
        self.tsPrev = 0.0
        self.colourH = 0.0
        self.colourS = 0.0
        self.colourV = 0.0
        self.showLabel = False
        self.tagLabel = None
        self.tagLabelStr = ""

class tag_Status:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.id = 0
        self.status = False
        self.warn_num = 0
        self.originalBrush = QBrush()
        self.originalPen = QPen()

class Anchor:
    def __init__(self):
        self.id = 0
        self.idx = 0
        self.ridx = 0
        self.show = True
        self.a = None  # 图形项
        self.ancLabel = None  # 标签
        self.p = QPointF()  # 位置

class BaseStation:
    def __init__(self):
        self.anchorId = 0
        self.groupId = 0
        self.set_groupId = 0
        self.status = False
        self.ip = ""
        self.mac = ""
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

class GraphicsWidget(QWidget):
    # 信号定义
    updateAnchorXYZ = pyqtSignal(int, int, float)  # id, x/y/z, value
    updateTagCorrection = pyqtSignal(int, int, int)  # aid, tid, value
    centerAt = pyqtSignal(float, float)
    centerRect = pyqtSignal(QRectF)
    updateAnchorList3D = pyqtSignal(int, bool, bool, float, float, float)
    setTagHistory = pyqtSignal(int)
    viewSizeChange = pyqtSignal(object)  # QSize
    LoadWidgetVisibleChange = pyqtSignal(bool)
    LoadWidgetIndexChange = pyqtSignal(int)
    updateGroupID = pyqtSignal(str, int)  # ip, GroupNo
    sendTagWarnCommand = pyqtSignal(int, bool)  # tagidA, status

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 从UI文件加载
        self.ui = Ui_GraphicsWidget()
        self.ui.setupUi(self)
        
        # 成员变量初始化
        self._tagSize = 0.3
        self._scene = None
        self._tags = {}  # QMap<quint64, Tag*>
        self._anchors = {}  # QMap<quint64, Anchor*>
        self._tagLabels = {}  # QMap<quint64, QString>
        
        self._historyLength = 20
        self._showHistory = True
        self._showHistoryP = True
        self._busy = True
        self._ignore = True
        self._geoFencingMode = False
        self._alarmOut = False
        self.status = [False] * 100
        self._selectedTagIdx = -1
        
        self.zone1 = None
        self.zone2 = None
        self._zone1Rad = 0.0
        self._zone2Rad = 0.0
        self._maxRad = 1000.0
        self._minRad = 0.0
        self._zone1Red = False
        self._zone2Red = False
        
        self.warn_flag = False
        self.warn_distance = 2.0
        
        self._line01 = None
        self._line02 = None
        self._line12 = None
        
        self.tableHeader = ["标签 ID", "X\n(m)", "Y\n(m)", "Z\n(m)", "状态", "定位圆", "静态R95\n(cm)",
                           "Anc 0\nrange(m)", "Anc 1\nrange(m)", "Anc 2\nrange(m)", "Anc 3\nrange(m)",
                           "Anc 4\nrange(m)", "Anc 5\nrange(m)", "Anc 6\nrange(m)", "Anc 7\nrange(m)",
                           "Rx Power\n(dBm)"]
        
        self.tableHeader_en = ["Tag", "X\n(m)", "Y\n(m)", "Z\n(m)", "Status", "Ranging", "R95\n(cm)",
                              "Anc 0\nrange(m)", "Anc 1\nrange(m)", "Anc 2\nrange(m)", "Anc 3\nrange(m)",
                              "Anc 4\nrange(m)", "Anc 5\nrange(m)", "Anc 6\nrange(m)", "Anc 7\nrange(m)",
                              "Rx Power\n(dBm)"]
        
        self.anchorHeader = ["组 ID", "基站 ID", "状态", "X (m)", "Y (m)", "Z (m)", "IP", "MAC",
                            "T0(cm)", "T1(cm)", "T2(cm)", "T3(cm)", "T4(cm)", "T5(cm)", "T6(cm)", "T7(cm)"]
        
        self.anchorHeader_en = ["Group", "Anchor", "Status", "X (m)", "Y (m)", "Z (m)", "IP", "MAC",
                               "T0(cm)", "T1(cm)", "T2(cm)", "T3(cm)", "T4(cm)", "T5(cm)", "T6(cm)", "T7(cm)"]
        
        self.m_polygon = QPolygonF()
        
        # QML相关
        self.m_QQuickWidget = None
        self.m_LoadWidget = None

        
        
        # 画布信息
        self.canvas_posX = "0"
        self.canvas_posY = "0"
        self.canvas_rotate = 0.0
        self.canvas_scale = "1"
        self.canvasInfomationVisible = True
        self.calibrationTextVisible = False
        self.calibrationIndex = 1
        self.canvasVisible = False
        self.canvasFontSize = 10
        
        # 定时器
        self.m_calibrationTimer = None
        self.m_calibrationTimer_100ms = None
        
        # 全局变量
        self.language = True  # True=中文, False=英文
        self.reseveSetok = False
        self.signalTimeOut = False
        self.baseStationList = []
        self.loadStationList = []
        self.statusList = []
        
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """初始化UI"""
        # 获取桌面尺寸
        desktop = QDesktopWidget()
        desktopHeight = desktop.geometry().height()
        desktopWidth = desktop.geometry().width()
        
        # 创建场景
        self._scene = QGraphicsScene(self)
        self.ui.graphicsView.setScene(self._scene)
        self.ui.graphicsView.scale(1, -1)  # 翻转Y轴
        self.ui.graphicsView.setBaseSize(int(desktopHeight * 0.75), int(desktopWidth * 0.75))
        
        # 设置标签表格
        self.ui.tagTable.setHorizontalHeaderLabels(self.tableHeader)
        self._setup_tag_table_columns()
        
        # 设置基站表格
        self.ui.anchorTable.setHorizontalHeaderLabels(self.anchorHeader)
        self._setup_anchor_table_columns()
        
        # 隐藏范围校正表
        self.hideTACorrectionTable(True)
        
        # 设置表格高度
        self.ui.anchorTable.setMaximumHeight(200)
        self.ui.tagTable.setMaximumHeight(200)
        
        # 设置默认值
        self._historyLength = 20
        self._showHistoryP = self._showHistory = True
        self._busy = True
        self._ignore = True
        self._selectedTagIdx = -1
        
        self._geoFencingMode = False
        self._alarmOut = False
        self.status = [False] * 100
        
        self._zone1Rad = 0.0
        self._zone2Rad = 0.0
        self._zone1Red = False
        self._zone2Red = False
        
        self.warn_flag = False
        self.warn_distance = 2.0
        
        # 初始化定时器
        self._init_timers()
        
        # 初始化QML组件
        self._init_qml_components()
        
        self.ui.stackedWidget.hide()
        
        self._busy = False
        self._ignore = False
        
    def _setup_tag_table_columns(self):
        """设置标签表格列宽"""
        self.ui.tagTable.setColumnWidth(0, 65)  # ID
        self.ui.tagTable.setColumnWidth(1, 50)  # X
        self.ui.tagTable.setColumnWidth(2, 50)  # Y
        self.ui.tagTable.setColumnWidth(3, 50)  # Z
        self.ui.tagTable.setColumnWidth(4, 65)  # 状态
        self.ui.tagTable.setColumnWidth(5, 60)  # 定位圆
        self.ui.tagTable.setColumnWidth(6, 60)  # R95
        
        # 设置范围列宽度
        for i in range(7, 15):
            self.ui.tagTable.setColumnWidth(i, 60)
        
        self.ui.tagTable.setColumnWidth(15, 60)  # Rx Power
        self.ui.tagTable.setColumnHidden(16, True)  # ID raw hex
        
        # 小屏幕适配
        desktop = QDesktopWidget()
        if desktop.geometry().width() <= 800:
            self.ui.tagTable.setMaximumWidth(600)
    
    def _setup_anchor_table_columns(self):
        """设置基站表格列宽"""
        self.ui.anchorTable.setColumnWidth(0, 55)  # Group ID
        self.ui.anchorTable.setColumnWidth(1, 55)  # ID
        self.ui.anchorTable.setColumnWidth(2, 55)  # Status
        self.ui.anchorTable.setColumnWidth(3, 55)  # X
        self.ui.anchorTable.setColumnWidth(4, 55)  # Y
        self.ui.anchorTable.setColumnWidth(5, 55)  # Z
        self.ui.anchorTable.setColumnWidth(6, 80)  # IP
        self.ui.anchorTable.setColumnWidth(7, 120)  # MAC
        
        # 设置T0-T7列宽度
        for i in range(8, 16):
            self.ui.anchorTable.setColumnWidth(i, 55)
    
    def _init_timers(self):
        """初始化定时器"""
        self.m_calibrationTimer_100ms = QTimer()
        self.m_calibrationTimer_100ms.setInterval(500)  # 500ms超时
        self.m_calibrationTimer_100ms.timeout.connect(self._calibration_timeout_100ms)
        
        self.m_calibrationTimer = QTimer()
        self.m_calibrationTimer.setInterval(8000)  # 8秒超时
        self.m_calibrationTimer.timeout.connect(self._calibration_timeout)
    
    def _init_qml_components(self):
        """初始化QML组件"""
        try:
            # 创建QQuickWidget并设置为顶层widget
            self.m_QQuickWidget = QQuickWidget(self)
            
            # 在加载QML前设置上下文属性
            self.m_QQuickWidget.rootContext().setContextProperty("canvas_posX", self.canvas_posX)
            self.m_QQuickWidget.rootContext().setContextProperty("canvas_posY", self.canvas_posY)
            self.m_QQuickWidget.rootContext().setContextProperty("canvas_rotate", self.canvas_rotate)
            self.m_QQuickWidget.rootContext().setContextProperty("canvas_scale", self.canvas_scale)
            self.m_QQuickWidget.rootContext().setContextProperty("language", self.language)
            self.m_QQuickWidget.rootContext().setContextProperty("canvasInfomationVisible", self.canvasInfomationVisible)
            self.m_QQuickWidget.rootContext().setContextProperty("calibrationIndex", self.calibrationIndex)
            self.m_QQuickWidget.rootContext().setContextProperty("calibrationTextVisible", self.calibrationTextVisible)
            
            # 设置透明背景
            self.m_QQuickWidget.setClearColor(QColor(Qt.transparent))
            
            # 加载QML文件
            qml_url = QUrl("qrc:/qml/CanvasInformation.qml")
            self.m_QQuickWidget.setSource(qml_url)
            
            # 检查加载错误
            if self.m_QQuickWidget.status() != QQuickWidget.Ready:
                print(f"QML加载失败: {self.m_QQuickWidget.errors()}")
            
            # 设置合理的大小和位置
            self.m_QQuickWidget.resize(280, 220)
            self.m_QQuickWidget.move(10, 10)
            
            # 设置堆叠顺序 - 使用raise()方法而不是属性
            self.m_QQuickWidget.raise_()
            self.m_QQuickWidget.show()
            
            # 连接QML信号
            m_item = self.m_QQuickWidget.rootObject()
            if m_item:
                try:
                    m_item.resetSignal.connect(self.resetButtonClicked)
                    print("QML信号连接成功")
                except Exception as e:
                    print(f"QML信号连接失败: {e}")
            else:
                print("无法获取QML根对象")
                
        except Exception as e:
            print(f"QML组件初始化失败: {e}")

    
    def _connect_signals(self):
        """连接信号"""
        # 表格信号
        self.ui.tagTable.cellChanged.connect(self.tagTableChanged)
        self.ui.anchorTable.cellChanged.connect(self.anchorTableChanged)
        self.ui.tagTable.cellClicked.connect(self.tagTableClicked)
        self.ui.anchorTable.cellClicked.connect(self.anchorTableClicked)
        self.ui.tagTable.itemSelectionChanged.connect(self.itemSelectionChanged)
        self.ui.anchorTable.itemSelectionChanged.connect(self.itemSelectionChangedAnc)
        
        # GraphicsView信号
        self.centerAt.connect(self.graphicsView().centerAt)
        self.centerRect.connect(self.graphicsView().centerRect)
        
        # 视图设置信号
        # self.graphicsView().sizeChanged.connect(self.sizeChanged)
        # self.graphicsView().rotateChanged.connect(self.rotateChanged)
        # self.graphicsView().visibleRectChanged.connect(self.visibleRectChanged)
        # self.graphicsView().scaleChanged.connect(self.scaleChanged)
        
        # 其他信号连接
        # 注意：这些需要在应用程序ready后连接
    
    def graphicsView(self):
        """获取GraphicsView实例"""
        return self.ui.graphicsView
    
    def loadConfigFile(self, filename):
        """加载配置文件"""
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            
            if root.tag == "config":
                for child in root:
                    if child.tag == "tag_cfg":
                        self._tagSize = float(child.get("size", "0.3"))
                        self._historyLength = int(child.get("history", "20"))
                    elif child.tag == "tag":
                        tag_id = int(child.get("ID"), 16)
                        label = child.get("label", "")
                        self._tagLabels[tag_id] = label
                        
            # 更新UI
            # ViewSettingsWidget.viewsettingswidget.setLinetext(str(self._tagSize))
            
        except Exception as e:
            print(f"Error loading config file: {e}")
            self.setTagHistory.emit(self._historyLength)
    
    def saveConfigFile(self, filename):
        """保存配置文件"""
        try:
            root = ET.Element("config")
            
            # 添加标签配置
            tag_cfg = ET.SubElement(root, "tag_cfg")
            tag_cfg.set("size", str(self._tagSize))
            tag_cfg.set("history", str(self._historyLength))
            
            # 添加标签信息
            for tag_id, label in self._tagLabels.items():
                tag = ET.SubElement(root, "tag")
                tag.set("ID", hex(tag_id))
                tag.set("label", label)
            
            tree = ET.ElementTree(root)
            tree.write(filename, encoding="utf-8", xml_declaration=True)
            
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def hideTACorrectionTable(self, hidden):
        """隐藏/显示范围校正表"""
        for i in range(8, 16):
            self.ui.anchorTable.setColumnHidden(i, hidden)
    
    def clearTags(self):
        """清除所有标签"""
        while self.ui.tagTable.rowCount() > 0:
            # 获取标签ID
            item = self.ui.tagTable.item(0, 16)  # ColumnIDr
            if item:
                tag_id = int(item.text(), 16)
                tag = self._tags.get(tag_id)
                
                if tag:
                    # 移除R95圆
                    if tag.r95p:
                        tag.r95p.setOpacity(0)
                        self._scene.removeItem(tag.r95p)
                        del tag.r95p
                        tag.r95p = None
                    
                    # 移除平均位置点
                    if tag.avgp:
                        tag.avgp.setOpacity(0)
                        self._scene.removeItem(tag.avgp)
                        del tag.avgp
                        tag.avgp = None
                    
                    # 移除地理围栏圆
                    if tag.geop:
                        tag.geop.setOpacity(0)
                        self._scene.removeItem(tag.geop)
                        del tag.geop
                        tag.geop = None
                    
                    # 移除定位圆
                    for i in range(8):
                        if tag.circle[i]:
                            tag.circle[i].setOpacity(0)
                            self._scene.removeItem(tag.circle[i])
                            del tag.circle[i]
                            tag.circle[i] = None
                    
                    # 移除标签
                    if tag.tagLabel:
                        tag.tagLabel.setOpacity(0)
                        self._scene.removeItem(tag.tagLabel)
                        del tag.tagLabel
                        tag.tagLabel = None
                    
                    # 移除历史点
                    for i in range(self._historyLength):
                        if tag.p[i]:
                            tag.p[i].setOpacity(0)
                            self._scene.removeItem(tag.p[i])
                            del tag.p[i]
                            tag.p[i] = None
                    
                    # 从映射中移除
                    if tag_id in self._tags:
                        del self._tags[tag_id]
            
            # 移除表格行
            self.ui.tagTable.removeRow(0)
        
        # 清空表格内容
        self.ui.tagTable.clearContents()
    
    def checktagwarn(self, state, warnsize):
        """检查标签警告"""
        print(f"checktagwarn state is: {state}, warnsize is: {warnsize}")
        self.warn_distance = warnsize
        self.warn_flag = state
    
    def handleTableUpdate(self, data):
        """处理表格更新"""
        row_count = self.ui.anchorTable.rowCount()
        data_size = len(data)
        load_size = len(self.loadStationList)
        
        exist = False
        
        for row in range(data_size):
            if row >= row_count:
                self.ui.anchorTable.insertRow(row)
            
            # 设置组ID
            group_id_item = self.ui.anchorTable.item(row, 0)
            if not group_id_item or not group_id_item.text():
                group_id_item = QTableWidgetItem()
                if data[row].set_groupId != 0:
                    group_id_item.setText(str(data[row].set_groupId))
                else:
                    group_id_item.setText(str(data[row].groupId))
                self.ui.anchorTable.setItem(row, 0, group_id_item)
            
            # 设置基站ID
            anchor_id_item = QTableWidgetItem(str(data[row].anchorId))
            self.ui.anchorTable.setItem(row, 1, anchor_id_item)
            
            # 设置状态
            status_item = QTableWidgetItem("True" if data[row].status else "False")
            if data[row].status:
                status_item.setForeground(QBrush(Qt.green))
            else:
                status_item.setForeground(QBrush(Qt.red))
            self.ui.anchorTable.setItem(row, 2, status_item)
            
            # 设置IP和MAC
            ip_item = QTableWidgetItem(data[row].ip)
            self.ui.anchorTable.setItem(row, 6, ip_item)
            
            mac_item = QTableWidgetItem(data[row].mac)
            self.ui.anchorTable.setItem(row, 7, mac_item)
            
            # 处理位置信息
            self._process_anchor_position(row, data[row], load_size)
    
    def _process_anchor_position(self, row, data, load_size):
        """处理基站位置信息"""
        x_item = self.ui.anchorTable.item(row, 3)
        y_item = self.ui.anchorTable.item(row, 4)
        z_item = self.ui.anchorTable.item(row, 5)
        
        if x_item and y_item and z_item:
            x = float(x_item.text()) if x_item.text() else 0.0
            y = float(y_item.text()) if y_item.text() else 0.0
            z = float(z_item.text()) if z_item.text() else 0.0
            
            self.anchPosG(row, data.anchorId, data.groupId, x, y, z, data.status, False)
            
            data.x = x
            data.y = y
            data.z = z
            
            self.setStationList(row, data.status)
        else:
            # 从加载列表中查找位置
            exist = False
            for load_index in range(load_size):
                if self.loadStationList[load_index].mac == data.mac:
                    exist = True
                    x = self.loadStationList[load_index].x
                    y = self.loadStationList[load_index].y
                    z = self.loadStationList[load_index].z
                    
                    x_item = QTableWidgetItem(f"{x:.2f}")
                    y_item = QTableWidgetItem(f"{y:.2f}")
                    z_item = QTableWidgetItem(f"{z:.2f}")
                    
                    self.ui.anchorTable.setItem(row, 3, x_item)
                    self.ui.anchorTable.setItem(row, 4, y_item)
                    self.ui.anchorTable.setItem(row, 5, z_item)
                    
                    self.anchPosG(row, data.anchorId, data.groupId, x, y, z, data.status, False)
                    self.setStationList(row, data.status)
                    break
            
            if not exist:
                self.anchPosG(row, data.anchorId, data.groupId, 0, 0, 2, data.status, False)
                self.setStationList(row, data.status)
    
    def itemSelectionChanged(self):
        """标签表格选择改变"""
        selected_items = self.ui.tagTable.selectedItems()
        # 处理选择改变
    
    def itemSelectionChangedAnc(self):
        """基站表格选择改变"""
        selected_items = self.ui.anchorTable.selectedItems()
        # 处理选择改变
    
    def tagTableChanged(self, row, column):
        """标签表格内容改变"""
        if not self._ignore:
            tag = None
            tag_id = int(self.ui.tagTable.item(row, 16).text(), 16)  # ColumnIDr
            tag = self._tags.get(tag_id)
            
            if not tag:
                return
            
            if column == 0:  # ColumnID - 标签改变
                new_label = self.ui.tagTable.item(row, column).text()
                tag.tagLabelStr = new_label
                if tag.tagLabel:
                    tag.tagLabel.setText(new_label)
                
                # 更新标签映射
                self._tagLabels[tag_id] = new_label
            
            elif column == 5:  # ColumnLocatingcircle - 定位圆显示
                item = self.ui.tagTable.item(row, column)
                tag.LocatingcircleShow[row] = (item.checkState() == Qt.Checked)
                self.status[row] = tag.LocatingcircleShow[row]
    
    def anchorTableChanged(self, row, column):
        """基站表格内容改变"""
        if not self._ignore:
            self._ignore = True
            
            anc = self._anchors.get(row)
            if not anc:
                self._ignore = False
                return
            
            if column == 0:  # AnchorColumnGroup - 组ID改变
                self._handle_group_change(row)
            elif column in [3, 4, 5]:  # X, Y, Z坐标改变
                self._handle_position_change(row, column)
            elif column in range(8, 16):  # T0-T7校正値
                self._handle_correction_change(row, column)
            
            self._ignore = False
            
            if self.canvasVisible:
                self.canvasShow(True)
    
    def _handle_group_change(self, row):
        """处理组ID改变"""
        ip_item = self.ui.anchorTable.item(row, 6)  # IP列
        group_item = self.ui.anchorTable.item(row, 0)  # Group列
        
        if ip_item and group_item:
            ip = ip_item.text()
            try:
                group_no = int(group_item.text())
                
                for station in self.baseStationList:
                    if station.ip == ip:
                        station.set_groupId = group_no
                        if group_no != station.groupId:
                            self.updateGroupID.emit(ip, group_no)
                        break
            except ValueError:
                pass
    
    def _handle_position_change(self, row, column):
        """处理位置改变"""
        try:
            value = float(self.ui.anchorTable.item(row, column).text())
            self.updateAnchorXYZ.emit(row, column, value)
            
            # 获取完整的位置信息
            x_item = self.ui.anchorTable.item(row, 3)
            y_item = self.ui.anchorTable.item(row, 4)
            z_item = self.ui.anchorTable.item(row, 5)
            
            x = float(x_item.text()) if x_item else 0.0
            y = float(y_item.text()) if y_item else 0.0
            z = float(z_item.text()) if z_item else 2.0
            
            # 确保项目存在
            if not x_item:
                x_item = QTableWidgetItem("0.00")
                self.ui.anchorTable.setItem(row, 3, x_item)
            if not y_item:
                y_item = QTableWidgetItem("0.00")
                self.ui.anchorTable.setItem(row, 4, y_item)
            if not z_item:
                z_item = QTableWidgetItem("2.00")
                self.ui.anchorTable.setItem(row, 5, z_item)
            
            # 更新基站位置
            self.anchPos(row, x, y, z, True, False)
            
        except ValueError:
            pass
    
    def _handle_correction_change(self, row, column):
        """处理校正値改变"""
        try:
            value = int(self.ui.anchorTable.item(row, column).text())
            self.updateTagCorrection.emit(row, column - 8, value)
        except ValueError:
            pass
    
    def anchorTableClicked(self, row, column):
        """基站表格点击"""
        anc = self._anchors.get(row)
        if not anc:
            return
        
        if column == 1:  # AnchorColumnID - 切换显示
            item = self.ui.anchorTable.item(row, column)
            anc.show = (item.checkState() == Qt.Checked)
            
            if anc.a:
                anc.a.setOpacity(1.0 if anc.show else 0.0)
            if anc.ancLabel:
                anc.ancLabel.setOpacity(1.0 if anc.show else 0.0)
            
            self.setStationList(row, anc.show)
        
        if self.canvasVisible:
            self.canvasShow(True)
    
    def tagTableClicked(self, row, column):
        """标签表格点击"""
        tag_id = int(self.ui.tagTable.item(row, 16).text(), 16)  # ColumnIDr
        tag = self._tags.get(tag_id)
        
        self._selectedTagIdx = row
        
        if not tag:
            return
        
        if column == 6:  # ColumnR95 - 切换R95显示
            item = self.ui.tagTable.item(row, column)
            tag.r95Show = (item.checkState() == Qt.Checked)
        
        elif column == 0:  # ColumnID - 切换标签显示
            item = self.ui.tagTable.item(row, column)
            tag.showLabel = (item.checkState() == Qt.Checked)
            
            if tag.tagLabel:
                tag.tagLabel.setOpacity(1.0 if tag.showLabel else 0.0)
    
    def tagIDToString(self, tag_id, t):
        """标签ID转字符串"""
        t[0] = "0x" + hex(tag_id)[2:]  # 移除0x前缀并重新添加
    
    def findTagRowIndex(self, t):
        """查找标签行索引"""
        for ridx in range(self.ui.tagTable.rowCount()):
            item = self.ui.tagTable.item(ridx, 16)  # ColumnIDr
            if item and item.text() == t:
                return ridx
        return -1
    
    def insertTag(self, ridx, t, showR95, showLabel, l):
        """插入标签"""
        self._ignore = True
        
        self.ui.tagTable.insertRow(ridx)
        
        for col in range(17):  # ColumnCount
            item = QTableWidgetItem()
            
            if col == 0:  # ColumnID
                if showLabel:
                    item.setCheckState(Qt.Checked)
                    item.setText(l)
                else:
                    item.setCheckState(Qt.Unchecked)
                    item.setText(l)
            elif col == 16:  # ColumnIDr
                item.setText(t)
            elif col == 6:  # ColumnR95
                if showR95:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
            elif col == 5:  # ColumnLocatingcircle
                item.setCheckState(Qt.Checked)
            
            self.ui.tagTable.setItem(ridx, col, item)
        
        self._ignore = False
    
    def addNewTag(self, tag_id):
        """添加新标签"""
        t = [""]
        self.tagIDToString(tag_id, t)
        
        ridx = self.findTagRowIndex(t[0])
        if ridx == -1:
            ridx = self.ui.tagTable.rowCount()
            label = self._tagLabels.get(tag_id, f"Tag {tag_id & 0xFFFF:04X}")
            self.insertTag(ridx, t[0], False, False, label)
    
    def addNewAnchor(self, anc_id, show):
        """添加新基站"""
        # 这里需要实现基站添加逻辑
        pass
    
    def addNewAnchorG(self, anc_id, anchindex, groupid, show):
        """添加新基站（带组信息）"""
        # 这里需要实现基站添加逻辑
        pass
    
    def insertAnchor(self, ridx, x, y, z, array, show):
        """插入基站"""
        # 这里需要实现基站插入逻辑
        pass
    
    def anchPos(self, anch_id, x, y, z, show, updatetable):
        """设置基站位置"""
        # 这里需要实现基站位置设置逻辑
        pass
    
    def anchPosG(self, anch_id, anchindex, groupid, x, y, z, show, update):
        """设置基站位置（带组信息）"""
        # 这里需要实现基站位置设置逻辑
        pass
    
    def tagPos(self, tag_id, x, y, z):
        """设置标签位置"""
        # 这里需要实现标签位置设置逻辑
        pass
    
    def tagStats(self, tag_id, x, y, z, r95):
        """设置标签统计信息"""
        # 这里需要实现标签统计设置逻辑
        pass
    
    def tagRange(self, tag_id, a_id, range_val, rx_power):
        """设置标签范围"""
        # 这里需要实现标签范围设置逻辑
        pass
    
    def setTagSize(self, size):
        """设置标签大小"""
        self._tagSize = size
    
    def setShowTagHistory(self, show):
        """设置显示标签历史"""
        self._showHistory = show
    
    def setShowTagAncTable(self, anchorTable, tagTable, ancTagCorr):
        """设置显示表格"""
        # 这里需要实现表格显示控制逻辑
        pass
    
    def showGeoFencingMode(self, mode):
        """显示地理围栏模式"""
        self._geoFencingMode = mode
    
    def zone1Value(self, value):
        """设置区域1值"""
        self._zone1Rad = value
    
    def zone2Value(self, value):
        """设置区域2值"""
        self._zone2Rad = value
    
    def tagHistoryNumber(self, value):
        """设置标签历史数量"""
        self._historyLength = value
    
    def zone(self, zone, radius, red):
        """设置区域"""
        if zone == 1:
            self._zone1Rad = radius
            self._zone1Red = red
        elif zone == 2:
            self._zone2Rad = radius
            self._zone2Red = red
    
    def setAlarm(self, in_alarm, out_alarm):
        """设置报警"""
        # 这里需要实现报警设置逻辑
        pass
    
    def ancRanges(self, a01, a02, a12):
        """设置基站范围"""
        # 这里需要实现基站范围设置逻辑
        pass
    
    def calibrationButtonClicked(self):
        """校准按钮点击"""
        # 这里需要实现校准逻辑
        pass
    
    def helpBtnReleased(self):
        """帮助按钮释放"""
        # 这里需要实现帮助逻辑
        pass
    
    def setCanvasVisible(self, visible):
        """设置画布可见"""
        self.canvasVisible = visible
        self.canvasShow(visible)
    
    def setCanvasInfoVisible(self, visible):
        """设置画布信息可见"""
        self.canvasInfomationVisible = visible
        if self.m_QQuickWidget:
            self.m_QQuickWidget.setVisible(visible)
    
    def canvasShow(self, visible):
        """显示画布"""
        # 这里需要实现画布显示逻辑
        pass
    
    def calculatePoint(self, pos_list):
        """计算点"""
        # 这里需要实现点计算逻辑
        pass
    
    def GetGravityPoint(self, pos_list):
        """获取重心点"""
        # 这里需要实现重心点计算逻辑
        pass
    
    def getMinPos(self, pos_list):
        """获取最小位置"""
        # 这里需要实现最小位置计算逻辑
        pass
    
    def getMaxPos(self, pos_list):
        """获取最大位置"""
        # 这里需要实现最大位置计算逻辑
        pass
    
    def sizeChanged(self, size):
        """尺寸改变"""
        self.viewSizeChange.emit(size)
    
    def rotateChanged(self, rotate):
        """旋转改变"""
        self.canvas_rotate = rotate
        if self.m_QQuickWidget:
            self.m_QQuickWidget.rootContext().setContextProperty("canvas_rotate", rotate)
    
    def visibleRectChanged(self):
        """可见矩形改变"""
        # 这里需要实现可见矩形改变逻辑
        pass
    
    def resetButtonClicked(self):
        """重置按钮点击"""
        if self.graphicsView():
            self.graphicsView().resetRotate()
    
    def scaleChanged(self, scale):
        """缩放改变"""
        self.canvas_scale = str(scale)
        if self.m_QQuickWidget:
            self.m_QQuickWidget.rootContext().setContextProperty("canvas_scale", str(scale))
    
    def updateCanvasPosition(self, posX, posY):
        """更新画布位置"""
        self.canvas_posX = str(posX)
        self.canvas_posY = str(posY)
        if self.m_QQuickWidget:
            self.m_QQuickWidget.rootContext().setContextProperty("canvas_posX", self.canvas_posX)
            self.m_QQuickWidget.rootContext().setContextProperty("canvas_posY", self.canvas_posY)
    
    def setCanvasVisible(self, visible):
        """设置画布可见"""
        self.canvasInfomationVisible = visible
        if self.m_QQuickWidget:
            self.m_QQuickWidget.rootContext().setContextProperty("canvasInfomationVisible", visible)
    
    def setCanvasFontSize(self, size):
        """设置画布字体大小"""
        self.canvasFontSize = size
        if self.m_QQuickWidget:
            # 这里需要实现字体大小改变逻辑
            pass
    
    def centerOnAnchors(self):
        """居中显示基站"""
        # 这里需要实现基站居中逻辑
        pass
    
    def anchTableEditing(self, editing):
        """基站表格编辑"""
        # 这里需要实现表格编辑逻辑
        pass
    
    def tagHistory(self, tag_id):
        """标签历史"""
        # 这里需要实现标签历史逻辑
        pass
    
    def setStationList(self, index, status):
        """设置基站列表"""
        # 这里需要实现基站列表设置逻辑
        pass
    
    def calculateDistance(self, x1, y1, x2, y2):
        """计算距离"""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def checkAndUpdateStatus(self):
        """检查并更新状态"""
        # 这里需要实现状态检查更新逻辑
        pass
    
    def _calibration_timeout_100ms(self):
        """校准超时100ms处理"""
        self.m_calibrationTimer_100ms.stop()
        if not self.reseveSetok:
            self.calibrationFailed()
            if self.language:
                QMessageBox.warning(None, "自标定启动失败", "自标定启动失败，设备不支持该功能或固件版本过低", "我知道了")
            else:
                QMessageBox.warning(None, "Warning", "The device does not support the function or the firmware version is too low.", "OK")
    
    def _calibration_timeout(self):
        """校准超时处理"""
        self.signalTimeOut = True
        # RTLSDisplayApplication.client().timeOutWarning()
    
    def calibrationTimerRestart(self):
        """重启校准定时器"""
        if self.m_calibrationTimer:
            self.m_calibrationTimer.stop()
            self.m_calibrationTimer.start()
    
    def calibrationTimerStop(self):
        """停止校准定时器"""
        if self.m_calibrationTimer:
            self.m_calibrationTimer.stop()
    
    def calibrationFailed(self):
        """校准失败"""
        # 这里需要实现校准失败逻辑
        pass
    
    def calibrationSuccess(self):
        """校准成功"""
        # 这里需要实现校准成功逻辑
        pass
    
    def event(self, event):
        """事件处理"""
        # 处理语言切换事件
        return super().event(event)
    
    def onReady(self):
        """准备就绪"""
        # 连接各种信号
        pass

# 全局变量
myGraphicsWidget = None

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    # 设置DPI策略
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    window = GraphicsWidget()
    window.show()
    
    sys.exit(app.exec_())

