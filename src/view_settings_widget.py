from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog, QComboBox, QButtonGroup,QMessageBox, QDataWidgetMapper
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtNetwork import QUdpSocket
from ui_py.ui_view_settings_widget import Ui_ViewSettingsWidget
import sys
from compile import compile_ui_file

# 编译UI文件
compile_ui_file('view_settings_widget')


def generateColor(index, totalColors):
    """生成颜色的函数"""
    hue = float(index) / totalColors
    saturation = 0.7  # 饱和度
    value = 0.9  # 亮度
    h = int(hue * 360)
    s = int(saturation * 255)
    v = int(value * 255)
    return QColor.fromHsv(h, s, v)


class ViewSettingsWidget(QWidget, Ui_ViewSettingsWidget):
    """视图设置窗口组件"""
    
    # 信号定义
    saveViewSettings = pyqtSignal()
    checktagwarn = pyqtSignal(int)
    
    # 类静态成员（单例模式）
    viewsettingswidget = None
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置单例
        ViewSettingsWidget.viewsettingswidget = self
        
        # UI初始化
        self.ui = Ui_ViewSettingsWidget()
        self.ui.setupUi(self)
        
        # 成员变量初始化
        self._floorplanOpen = False
        self._logging = False
        self._enableAutoPos = False
        self._selected = 0
        self.fucStatus = False
        
        # 串口连接状态
        self._state = None  # SerialConnection.Disconnected
        
        # 定时器
        self.timer = QTimer()
        self.m_setTimer = QTimer()
        self.timer200ms = QTimer()
        
        # 端口列表
        self.oldPortStringList = []
        self.newPortStringList = []
        
        # 3D相关变量
        self.maxX = float('-inf')
        self.maxY = float('-inf')
        self.maxZ = float('-inf')
        self.minX = 0.0
        self.minY = 0.0
        self.minZ = 0.0
        self.rangeX = 0.0
        self.rangeY = 0.0
        self.rangeZ = 0.0
        self.ratio = 1.0
        self.inited3d = False
        
        # 3D图形对象（需要安装 PyQtDataVisualization）
        self.scatter = None
        self.series = None
        self.ancDataArray = None
        self.container = None
        self.seriesPoint = []  # MAX_NUM_TAGS
        self.m_labelPoint = []  # MAX_NUM_TAGS
        self.m_labelAnc = []  # MAX_NUM_ANCS
        
        # UDP Socket
        self.udpSocket = QUdpSocket(self)
        
        # 按钮组设置
        self._setupButtonGroups()
        
        # 连接信号槽
        self._connectSignals()
        
        # 初始化UI状态
        self._initializeUI()
        
        # 延迟初始化（在应用ready后）
        # RTLSDisplayApplication.connectReady(self, "onReady")
    
    def _setupButtonGroups(self):
        """设置按钮组"""
        # 导航模式按钮组
        # group = QButtonGroup(self)
        # group.addButton(self.ui.showNavigationMode, 1)  # 最小二乘
        # group.addButton(self.ui.showNavigationMode_4, 4)  # 官方三角定位
        # group.addButton(self.ui.showNavigationMode_3, 2)  # 一维
        
        # group1 = QButtonGroup(self)
        # group1.addButton(self.ui.showNavigationMode_2, 3)  # 3D视图
        # group1.addButton(self.ui.showNavigationMode_5, 5)  # 1D/2D视图
        pass
    
    def _connectSignals(self):
        """连接所有信号槽"""
        # 这里需要根据实际的应用架构连接信号
        # 示例：
        # RTLSDisplayApplication.serialConnection().dataupdate.connect(self.dataupdate)
        # self.ui.connect_pb.clicked.connect(self.connectButtonClicked)
        # self.ui.floorplanOpen_pb.clicked.connect(self.floorplanOpenClicked)
        # ... 更多信号连接
        pass
    
    def _initializeUI(self):
        """初始化UI状态"""
        # 设置初始状态
        # self.ui.showNavigationMode_4.setCheckState(Qt.Checked)
        # self.ui.showNavigationMode_5.setCheckState(Qt.Checked)
        # self.ui.showNavigationMode_2.setEnabled(False)
        
        # 日志按钮状态
        # if self._logging:
        #     self.ui.logging_pb.setText("停止")
        #     self.ui.label_logingstatus.setText("日志记录-开")
        # else:
        #     self.ui.logging_pb.setText("开始")
        #     self.ui.label_logingstatus.setText("日志记录-关")
        
        # 自动定位默认禁用
        # self.ui.useAutoPos.setDisabled(True)
        pass
    
    def onReady(self):
        """应用程序准备就绪后调用"""
        print("ViewSettingsWidget onReady()")
        
        # 创建数据映射器（用于自动同步UI和数据模型）
        # mapper = QPropertyDataWidgetMapper(RTLSDisplayApplication.viewSettings(), self)
        # mapper.addMapping(self.ui.gridWidth_sb, "gridWidth")
        # mapper.addMapping(self.ui.gridHeight_sb, "gridHeight")
        # ... 更多映射
        
        # 连接更多信号
        # RTLSDisplayApplication.serialConnection().connectionStateChanged.connect(
        #     self.connectionStateChanged)
        
        # 更新设备列表
        # self.updateDeviceList()
        # self.oldPortStringList = RTLSDisplayApplication.serialConnection().portsList()
        
        # 启动定时器更新串口设备列表
        # self.timer.timeout.connect(self.updateDeviceList)
        # self.timer.start(1000)  # 1秒更新一次
        pass
    
    # ========== 平面图相关方法 ==========
    
    def floorplanOpenClicked(self):
        """打开平面图按钮点击"""
        if not self._floorplanOpen:
            path = QFileDialog.getOpenFileName(
                self, "Open Bitmap", "", "Image (*.png *.jpg *.jpeg *.bmp)")[0]
            
            if not path:
                return
            
            if self.applyFloorPlanPic(path) == 0:
                # RTLSDisplayApplication.viewSettings().floorplanShow(True)
                # RTLSDisplayApplication.viewSettings().setFloorplanPath(path)
                pass
            
            self._floorplanOpen = True
            # self.ui.floorplanOpen_pb.setText("清除")
        else:
            # RTLSDisplayApplication.viewSettings().floorplanShow(False)
            # RTLSDisplayApplication.viewSettings().clearSettings()
            self._floorplanOpen = False
            # self.ui.floorplanOpen_pb.setText("打开")
            # 重置相关UI
    
    def applyFloorPlanPic(self, path):
        """应用平面图图片"""
        pm = QPixmap(path)
        
        if pm.isNull():
            return -1
        
        # self.ui.floorplanPath_lb.setText(QFileInfo(path).fileName())
        # RTLSDisplayApplication.viewSettings().setFloorplanPixmap(pm)
        self._floorplanOpen = True
        
        return 0
    
    def getFloorPlanPic(self):
        """获取平面图"""
        # path = RTLSDisplayApplication.viewSettings().getFloorplanPath()
        # self.applyFloorPlanPic(path)
        pass
    
    # ========== 网格和原点显示 ==========
    
    def gridShowClicked(self):
        """网格显示按钮点击"""
        # RTLSDisplayApplication.viewSettings().setShowGrid(
        #     self.ui.gridShow.isChecked())
        pass
    
    def originShowClicked(self):
        """原点显示按钮点击"""
        # RTLSDisplayApplication.viewSettings().setShowOrigin(
        #     self.ui.showOrigin.isChecked())
        pass
    
    def showOriginGrid(self, orig, grid):
        """显示原点和网格"""
        # self.ui.gridShow.setChecked(grid)
        # self.ui.showOrigin.setChecked(orig)
        pass
    
    # ========== 标签历史轨迹 ==========
    
    def tagHistoryShowClicked(self):
        """标签历史显示点击"""
        # RTLSDisplayApplication.graphicsWidget().setShowTagHistory(
        #     self.ui.showTagHistory.isChecked())
        pass
    
    def tagHistoryNumberValueChanged(self, value):
        """标签历史数量改变"""
        # RTLSDisplayApplication.graphicsWidget().tagHistoryNumber(value)
        pass
    
    def setTagHistory(self, h):
        """设置标签历史"""
        # self.ui.tagHistoryN.setValue(h)
        pass
    
    # ========== 串口连接相关 ==========
    
    def connectButtonClicked(self):
        """连接按钮点击"""
        # 根据当前状态执行不同操作
        # if self._state == SerialConnection.Disconnected or \
        #    self._state == SerialConnection.ConnectionFailed:
        #     RTLSDisplayApplication.serialConnection().openConnection(
        #         self.ui.comPort.currentIndex())
        # elif self._state == SerialConnection.Connecting:
        #     RTLSDisplayApplication.serialConnection().cancelConnection()
        # elif self._state == SerialConnection.Connected:
        #     RTLSDisplayApplication.serialConnection().closeConnection()
        pass
    
    def connectionStateChanged(self, state):
        """连接状态改变"""
        self._state = state
        
        # 根据状态更新UI
        # if state == SerialConnection.Disconnected or \
        #    state == SerialConnection.ConnectionFailed:
        #     self.ui.connect_pb.setText("连接")
        #     self.ui.BTN_getdata.setEnabled(False)
        #     # ... 更多UI更新
        # elif state == SerialConnection.Connecting:
        #     self.ui.connect_pb.setText("取消")
        # elif state == SerialConnection.Connected:
        #     self.ui.connect_pb.setText("断开")
        #     self.ui.BTN_getdata.setEnabled(True)
        
        # enabled = (state == Disconnected or state == ConnectionFailed)
        # self.ui.comPort.setEnabled(enabled)
        pass
    
    def updateDeviceList(self):
        """更新设备列表"""
        count = 0
        
        # RTLSDisplayApplication.serialConnection().findSerialDevices()
        # self.newPortStringList = RTLSDisplayApplication.serialConnection().portsList()
        
        # if len(self.newPortStringList) != len(self.oldPortStringList):
        #     self.oldPortStringList = self.newPortStringList
        #     self.ui.comPort.clear()
        #     self.ui.comPort.addItems(self.oldPortStringList)
        
        # count = self.ui.comPort.count()
        
        # # 检查端口是否还存在
        # if count == 0 or (port_name not in self.newPortStringList and port_name != ""):
        #     self.ui.connect_pb.setEnabled(False)
        #     self.ui.label.setEnabled(False)
        #     self.ui.comPort.setEnabled(False)
        #     RTLSDisplayApplication.serialConnection().closeConnection()
        
        return count
    
    def serialError(self):
        """串口错误"""
        # self.ui.connect_pb.setEnabled(False)
        # self.ui.label.setEnabled(False)
        # self.ui.comPort.setEnabled(False)
        pass
    
    # ========== 数据更新 ==========
    
    def dataupdate(self):
        """数据更新（从串口接收到数据后更新UI）"""
        # 更新设备信息到UI
        # self.ui.lE_model.setText(SerialConnection.model)
        # self.ui.lE_firmware.setText(SerialConnection.firmware)
        # self.ui.lE_role.setText(SerialConnection.role)
        # ... 更多字段更新
        
        # 根据角色启用/禁用某些按钮
        # if SerialConnection.role == "TAG":
        #     self.ui.BTN_addr.setEnabled(True)
        #     self.ui.BTN_jizhan.setEnabled(True)
        #     # ... 更多
        # elif SerialConnection.role == "ANCHOR":
        #     self.ui.BTN_addr.setEnabled(False)
        #     self.ui.BTN_jizhan.setEnabled(False)
        #     # ... 更多
        pass
    
    # ========== 日志记录 ==========
    
    def loggingClicked(self):
        """日志记录按钮点击"""
        if not self._logging:
            self._logging = True
            # RTLSDisplayApplication.client().openLogFile("")
            # self.ui.logging_pb.setText("停止")
            # self.ui.label_logingstatus.setText("日志记录-开")
            # self.ui.label_logfile.setText(
            #     RTLSDisplayApplication.client().getLogFilePath())
        else:
            # RTLSDisplayApplication.client().closeLogFile()
            # self.ui.logging_pb.setText("开始")
            # self.ui.label_logingstatus.setText("日志记录-关")
            # self.ui.label_logfile.setText("")
            # self.ui.saveFP.setChecked(False)
            self._logging = False
    
    # ========== 工具按钮 ==========
    
    def originClicked(self):
        """原点工具按钮点击"""
        # from OriginTool import OriginTool
        # tool = OriginTool(self)
        # tool.done.connect(tool.deleteLater)
        # RTLSDisplayApplication.graphicsView().setTool(tool)
        pass
    
    def scaleClicked(self):
        """缩放工具按钮点击"""
        # from ScaleTool import ScaleTool
        # sender = self.sender()
        # 
        # if sender == self.ui.scaleX_pb:
        #     tool = ScaleTool(ScaleTool.XAxis, self)
        # elif sender == self.ui.scaleY_pb:
        #     tool = ScaleTool(ScaleTool.YAxis, self)
        # else:
        #     return
        # 
        # tool.done.connect(tool.deleteLater)
        # RTLSDisplayApplication.graphicsView().setTool(tool)
        pass
    
    # ========== 自动定位 ==========
    
    def enableAutoPositioning(self, enable):
        """启用自动定位"""
        self._enableAutoPos = enable
        # self.ui.useAutoPos.setDisabled(not enable)
    
    def useAutoPosClicked(self):
        """使用自动定位点击"""
        # RTLSDisplayApplication.client().setUseAutoPos(
        #     self.ui.useAutoPos.isChecked())
        # RTLSDisplayApplication.graphicsWidget().anchTableEditing(
        #     not self.ui.useAutoPos.isChecked())
        pass
    
    # ========== 显示设置 ==========
    
    def tagAncTableShowClicked(self):
        """标签锚点表显示点击"""
        # RTLSDisplayApplication.graphicsWidget().setShowTagAncTable(
        #     self.ui.showAnchorTable.isChecked(),
        #     self.ui.showTagTable.isChecked(),
        #     self.ui.showAnchorTagCorrectionTable.isChecked())
        pass
    
    def checkCanvesAreaClicked(self, state):
        """画布区域复选框点击"""
        # if state == Qt.Checked:
        #     RTLSDisplayApplication.graphicsWidget().setCanvasVisible(True)
        # else:
        #     RTLSDisplayApplication.graphicsWidget().setCanvasVisible(False)
        pass
    
    def canvesFontSizeValueChanged(self, value):
        """画布字体大小改变"""
        # RTLSDisplayApplication.graphicsWidget().setCanvasFontSize(value)
        pass
    
    def checkCanvesInfoClicked(self, state):
        """画布信息复选框点击"""
        # if state == Qt.Checked:
        #     RTLSDisplayApplication.graphicsWidget().setCanvasInfoVisible(True)
        # else:
        #     RTLSDisplayApplication.graphicsWidget().setCanvasInfoVisible(False)
        pass
    
    def checkTagWarnClicked(self, state):
        """标签警告复选框点击"""
        # if state == Qt.Checked:
        #     print("CheckBox is clicked true")
        #     # size = self.ui.tagWarnSize.text().toInt()
        # else:
        #     print("CheckBox is clicked false")
        # 
        # RTLSDisplayApplication.graphicsWidget().checktagwarn(
        #     state, self.ui.tagWarnSize.text().toInt())
        pass
    
    def setCheckCanvesAreaState(self, state):
        """设置画布区域状态"""
        # if state:
        #     self.ui.checkCanvesArea.setCheckState(Qt.Checked)
        # else:
        #     self.ui.checkCanvesArea.setCheckState(Qt.Unchecked)
        pass
    
    # ========== 保存设置 ==========
    
    def saveFPClicked(self):
        """保存平面图点击"""
        # RTLSDisplayApplication.viewSettings().setSaveFP(
        #     self.ui.saveFP.isChecked())
        # 
        # if self.ui.saveFP.isChecked():
        #     self.saveViewSettings.emit()
        pass
    
    def showSave(self, save):
        """显示保存"""
        # self.ui.saveFP.setChecked(save)
        pass
    
    # ========== 导航模式 ==========
    
    def showNavigationModeClicked(self):
        """显示导航模式点击"""
        # if self.ui.showNavigationMode.isChecked():
        #     self.ui.showGeoFencingMode.setChecked(False)
        # else:
        #     self.ui.showGeoFencingMode.setChecked(True)
        # self.showGeoFencingModeClicked()
        pass
    
    def showGeoFencingModeClicked(self):
        """显示地理围栏模式点击"""
        pass
    
    # ========== 3D视图相关 ==========
    
    def initGraph3D(self):
        """初始化3D图形"""
        if self.inited3d:
            return
        
        self.inited3d = True
        # self.ratio = myGraphicsWidget._tagSize / 0.3
        
        # 初始化范围
        self.maxX = float('-inf')
        self.maxY = float('-inf')
        self.maxZ = float('-inf')
        self.minX = 0
        self.minY = 0
        self.minZ = 0
        
        # 创建3D散点图（需要 PyQtDataVisualization）
        # from PyQt5.QtDataVisualization import Q3DScatter, QScatter3DSeries
        # 
        # self.scatter = Q3DScatter()
        # self.container = QWidget.createWindowContainer(self.scatter)
        # # 设置容器大小
        # # ... 更多3D设置
        # 
        # self.scatter.activeTheme().setType(Q3DTheme.ThemeStoneMoss)
        # self.scatter.setShadowQuality(QAbstract3DGraph.ShadowQualitySoftLow)
        # # ... 更多配置
        
        self.updateAxisRange(False)
    
    def updateAxisRange(self, tag=False):
        """更新坐标轴范围"""
        if not tag:
            # 重置最大最小值
            self.maxX = float('-inf')
            self.maxY = float('-inf')
            self.maxZ = float('-inf')
            self.minX = 0
            self.minY = 0
            self.minZ = 0
        
        # 遍历锚点表更新范围
        # for i in range(myGraphicsWidget.ui.anchorTable.rowCount()):
        #     if self.checkAnchorStatus(i):
        #         x = float(myGraphicsWidget.ui.anchorTable.item(i, 3).text())
        #         y = float(myGraphicsWidget.ui.anchorTable.item(i, 5).text())
        #         z = float(myGraphicsWidget.ui.anchorTable.item(i, 4).text())
        #         
        #         self.maxX = max(self.maxX, x)
        #         self.maxY = max(self.maxY, y)
        #         self.maxZ = max(self.maxZ, z)
        #         self.minX = min(self.minX, x)
        #         self.minY = min(self.minY, y)
        #         self.minZ = min(self.minZ, z)
        
        if not tag:
            self.maxX += 0.5 * self.ratio
            self.maxY += 0.5 * self.ratio
            self.maxZ += 0.5 * self.ratio
            self.minX -= 0.5 * self.ratio
            self.minY -= 0.5 * self.ratio
            self.minZ -= 0.5 * self.ratio
        
        # 更新scatter的坐标轴范围
        # if self.scatter:
        #     self.scatter.axisX().setRange(self.minX, self.maxX)
        #     self.scatter.axisY().setRange(self.minY, self.maxY)
        #     self.scatter.axisZ().setRange(self.minZ, self.maxZ)
    
    def updateAxisRangeWithTag(self, x, y, z):
        """使用标签位置更新坐标轴范围"""
        self.maxX = max(self.maxX, x)
        self.maxY = max(self.maxY, z)
        self.maxZ = max(self.maxZ, y)
        self.minX = min(self.minX, x)
        self.minY = min(self.minY, z)
        self.minZ = min(self.minZ, y)
        
        self.updateAxisRange(True)
    
    def tag3DPos(self, tagId, x, y, z):
        """标签3D位置更新"""
        # 在3D视图中显示标签位置
        # if self.ui.showNavigationMode_2.checkState() == Qt.Checked:
        #     # 更新3D散点图中的标签位置
        #     # ... 实现3D位置更新逻辑
        #     self.updateAxisRangeWithTag(x, y, z)
        pass
    
    def anchorTableChanged(self, r, c):
        """锚点表改变"""
        # if myGraphicsWidget._busy:
        #     return
        # if not myGraphicsWidget.ui.graphicsView.isHidden():
        #     return
        # 
        # if self.checkAnchorStatus(r):
        #     self.updateAncAndLabel(r)
        pass
    
    def tagTableClicked(self, r, c):
        """标签表点击"""
        # 控制标签标签的显示/隐藏
        # if myGraphicsWidget.ui.tagTable.item(r, 0).checkState() == Qt.Checked:
        #     if self.m_labelPoint[r] not in self.scatter.customItems():
        #         # 创建标签
        #         pass
        # else:
        #     if self.m_labelPoint[r] in self.scatter.customItems():
        #         self.scatter.removeCustomItem(self.m_labelPoint[r])
        pass
    
    def updateAncAndLabel(self, r, update=False):
        """更新锚点和标签"""
        # x = float(myGraphicsWidget.ui.anchorTable.item(r, 3).text())
        # y = float(myGraphicsWidget.ui.anchorTable.item(r, 5).text())
        # z = float(myGraphicsWidget.ui.anchorTable.item(r, 4).text())
        # 
        # # 更新3D视图中的锚点位置和标签
        # # ... 实现更新逻辑
        pass
    
    def updateAnchorList3D(self, ridx, status, update, x, y, z):
        """更新3D锚点列表"""
        pass
    
    def checkAnchorStatus(self, r):
        """检查锚点状态"""
        # xItem = myGraphicsWidget.ui.anchorTable.item(r, 3)
        # yItem = myGraphicsWidget.ui.anchorTable.item(r, 5)
        # zItem = myGraphicsWidget.ui.anchorTable.item(r, 4)
        # 
        # if xItem and yItem and zItem:
        #     try:
        #         x = float(xItem.text())
        #         y = float(yItem.text())
        #         z = float(zItem.text())
        #         return True
        #     except:
        #         return False
        return False
    
    # ========== UDP发送 ==========
    
    def udpSendData(self):
        """UDP发送数据"""
        # 发送标签位置数据到UDP
        # if myGraphicsWidget.ui.tagTable.rowCount() == 0:
        #     return
        # 
        # for i in range(myGraphicsWidget.ui.tagTable.rowCount()):
        #     data = {
        #         "Command": "UpLink",
        #         "TagID": myGraphicsWidget.ui.tagTable.item(i, 0).text(),
        #         "X": myGraphicsWidget.ui.tagTable.item(i, 1).text(),
        #         "Y": myGraphicsWidget.ui.tagTable.item(i, 2).text(),
        #         "Z": myGraphicsWidget.ui.tagTable.item(i, 3).text()
        #     }
        #     
        #     import json
        #     json_str = json.dumps(data)
        #     IP = self.ui.LE_ip_address.text()
        #     port = int(self.ui.LE_com.text())
        #     self.udpSocket.writeDatagram(json_str.encode(), QHostAddress(IP), port)
        pass
    
    # ========== 其他辅助方法 ==========
    
    def myitemlist(self, length):
        """辅助方法"""
        num = 0
        for i in range(length):
            num = num + 1
        return num
    
    def enableFiltering(self):
        """启用过滤"""
        # self.ui.filtering.setEnabled(True)
        pass
    
    def updateLocationFilter(self, index):
        """更新位置过滤器"""
        # RTLSDisplayApplication.client().setLocationFilter(index)
        pass
    
    def showExplainBtnClicked(self):
        """显示说明按钮点击"""
        QMessageBox.information(
            self,
            "使用说明",
            "一键测绘功能可快速测量基站间各点距离以及面积。\n"
            "最少在选择框内勾选2个基站可启动测绘功能，3个及以上基站可测得面积"
        )
    
    def event(self, event):
        """事件处理（用于语言切换）"""
        # if event.type() == QEvent.LanguageChange:
        #     self.ui.retranslateUi(self)
        #     # 更新翻译相关UI
        return super().event(event)
    
    def __del__(self):
        """析构函数"""
        # 清理3D图形对象
        # for graph in self.m_graphLsit:
        #     del graph
        pass





if __name__ == '__main__':

        # 设置DPI策略
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)

    window = ViewSettingsWidget()
    window.show()
    
    sys.exit(app.exec_())
