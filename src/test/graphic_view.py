#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced GraphicsView - 增强版图形视图
基于CPP源码重写的PyQt5版本，包含完整的工具系统
"""

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt5.QtCore import Qt, QPointF, QRectF, QPoint, pyqtSignal, QObject
from PyQt5.QtGui import QPainter, QPen, QBrush, QCursor, QTransform, QPixmap, QWheelEvent
import math

class AbstractTool(QObject):
    """抽象工具类"""
    done = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._view = None
    
    def setView(self, view):
        """设置视图"""
        self._view = view
    
    def view(self):
        """获取视图"""
        return self._view
    
    def cursor(self):
        """获取光标"""
        return Qt.ArrowCursor
    
    def mousePressEvent(self, scenePos):
        """鼠标按下事件"""
        return False
    
    def mouseMoveEvent(self, scenePos):
        """鼠标移动事件"""
        pass
    
    def mouseReleaseEvent(self, scenePos):
        """鼠标释放事件"""
        pass
    
    def clicked(self, scenePos):
        """点击事件"""
        pass
    
    def draw(self, painter, rect, cursorPos):
        """绘制"""
        pass
    
    def cancel(self):
        """取消"""
        self.done.emit()

class RubberBandTool(AbstractTool):
    """橡皮筋工具"""
    def __init__(self, view=None):
        super().__init__(view)
        self._startPos = QPointF()
        self._currentPos = QPointF()
        self._active = False
    
    def cursor(self):
        """获取光标"""
        return Qt.CrossCursor
    
    def mousePressEvent(self, scenePos):
        """鼠标按下事件"""
        self._startPos = scenePos
        self._currentPos = scenePos
        self._active = True
        return True
    
    def mouseMoveEvent(self, scenePos):
        """鼠标移动事件"""
        if self._active:
            self._currentPos = scenePos
            if self.view() and self.view().scene():
                self.view().scene().update()
    
    def mouseReleaseEvent(self, scenePos):
        """鼠标释放事件"""
        if self._active:
            self._currentPos = scenePos
            self._active = False
            
            # 创建选择矩形
            rect = QRectF(self._startPos, self._currentPos).normalized()
            
            # 选择矩形内的项目
            if self.view() and self.view().scene():
                items = self.view().scene().items(rect)
                for item in items:
                    if item.flags() & QGraphicsItem.ItemIsSelectable:
                        item.setSelected(True)
            
            self.done.emit()
    
    def draw(self, painter, rect, cursorPos):
        """绘制橡皮筋"""
        if self._active:
            painter.setPen(QPen(Qt.blue, 1, Qt.DashLine))
            painter.drawRect(QRectF(self._startPos, self._currentPos).normalized())

class PanTool(AbstractTool):
    """平移工具"""
    def __init__(self, view=None):
        super().__init__(view)
        self._lastPos = QPointF()
        self._active = False
    
    def cursor(self):
        """获取光标"""
        return Qt.OpenHandCursor
    
    def mousePressEvent(self, scenePos):
        """鼠标按下事件"""
        self._lastPos = scenePos
        self._active = True
        return True
    
    def mouseMoveEvent(self, scenePos):
        """鼠标移动事件"""
        if self._active and self.view():
            delta = scenePos - self._lastPos
            self.view().translateView(-delta.x(), -delta.y())
            self._lastPos = scenePos
    
    def mouseReleaseEvent(self, scenePos):
        """鼠标释放事件"""
        self._active = False
        self.done.emit()

class ZoomTool(AbstractTool):
    """缩放工具"""
    def __init__(self, view=None):
        super().__init__(view)
        self._centerPos = QPointF()
        self._active = False
    
    def cursor(self):
        """获取光标"""
        return Qt.SizeAllCursor
    
    def mousePressEvent(self, scenePos):
        """鼠标按下事件"""
        self._centerPos = scenePos
        self._active = True
        return True
    
    def mouseMoveEvent(self, scenePos):
        """鼠标移动事件"""
        if self._active and self.view():
            # 计算缩放因子
            delta = scenePos - self._centerPos
            distance = math.sqrt(delta.x() ** 2 + delta.y() ** 2)
            
            # 根据距离计算缩放
            if distance > 10:
                scale = 1.0 + (distance - 10) * 0.01
                if delta.y() < 0:
                    scale = 1.0 / scale
                
                self.view().scaleView(scale, scale, self._centerPos)
                self._centerPos = scenePos
    
    def mouseReleaseEvent(self, scenePos):
        """鼠标释放事件"""
        self._active = False
        self.done.emit()

class GraphicsView(QGraphicsView):
    # 信号定义
    visibleRectChanged = pyqtSignal(QRectF)
    sizeChanged = pyqtSignal(object)  # QSize
    rotateChanged = pyqtSignal(float)
    scaleChanged = pyqtSignal(float)
    
    # 鼠标上下文枚举
    DefaultMouseContext = 0
    PanningMouseContext = 1
    SceneMouseContext = 2
    ToolMouseContext = 3
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 成员变量初始化
        self.rotateAngle = 0.0
        self._tool = None
        self._mouseContext = self.DefaultMouseContext
        self._lastMouse = QPoint()
        self._visibleRect = QRectF(-1, -1, 6, 6)
        self._ignoreContextMenu = False
        
        # 公共成员变量
        self.g_button = Qt.NoButton
        self.centerPoint = QPointF()
        self.startPoint = QPointF()
        self.currentPoint = QPointF()
        self.Button = None
        
        # 静态变量（模拟C++的static）
        self.lastAngle = 0.0
        self.mouseAngle = 0.0
        self.firstMove = True
        
        # 视图设置
        self._viewSettings = ViewSettings()  # 创建默认视图设置
        
        # 设置
        self.setMouseTracking(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.NoDrag)
        
        self.setVisibleRect(QRectF(-1, -1, 6, 6))
        self.setSceneRect(-1500, -1500, 3000, 3000)
        
        # 安装事件过滤器
        self.viewport().installEventFilter(self)
    
    def onReady(self):
        """应用程序准备就绪时调用"""
        # 连接视图设置信号
        self._viewSettings.floorplanChanged.connect(self.floorplanChanged)
        self._viewSettings.gridChanged.connect(self.gridChanged)
        self._viewSettings.originChanged.connect(self.originChanged)
    
    def translateView(self, dx, dy):
        """平移视图"""
        self.setVisibleRect(self._visibleRect.translated(dx, dy))
    
    def scaleView(self, sx, sy, center=None):
        """缩放视图"""
        if center is None:
            center = self._visibleRect.center()
        
        visibleRect = QRectF(self._visibleRect)
        diff = center - visibleRect.topLeft()
        
        visibleRect.translate(diff.x(), diff.y())
        
        # 限制宽高在1到1500之间
        new_width = max(1.0, min(visibleRect.width() * sx, 1500.0))
        new_height = max(1.0, min(visibleRect.height() * sy, 1500.0))
        
        visibleRect.setWidth(new_width)
        visibleRect.setHeight(new_height)
        
        visibleRect.translate(
            -diff.x() * visibleRect.width() / self._visibleRect.width(),
            -diff.y() * visibleRect.height() / self._visibleRect.height()
        )
        
        scale = max(1.0, min(visibleRect.height() * sy, 1500.0))
        self.scaleChanged.emit(round(scale,2))
        self.setVisibleRect(visibleRect)
    
    def setVisibleRect(self, visibleRect):
        """设置可见矩形"""
        self._visibleRect = QRectF(visibleRect)
        self.fitInView(self._visibleRect, Qt.KeepAspectRatio)
        self.visibleRectChanged.emit(visibleRect)
    
    def visibleRect(self):
        """获取可见矩形"""
        return QRectF(self._visibleRect)
    
    def centerRect(self, visibleRect):
        """居中显示矩形"""
        s = 1.206 * 1.2  # zoom out
        
        # 容错：当rect为一条直线时，center会出现nan，导致矩形设置错误
        rec = QRectF(visibleRect)
        if rec.width() == 0:
            rec.setWidth(1)
        if rec.height() == 0:
            rec.setHeight(1)
        
        self.setVisibleRect(rec)
        self.scaleView(s, s, self._visibleRect.center())
    
    def centerAt(self, x, y):
        """将视图中心移动到指定坐标"""
        visibleRect = QRectF(self._visibleRect)
        p = QPointF(x, y)
        visibleRect.moveCenter(p)
        self.setVisibleRect(visibleRect)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        event.ignore()
        
        self._mouseContext = self.DefaultMouseContext
        
        # 如果有工具，优先让工具处理
        if self._tool:
            if self._tool.mousePressEvent(self.mapToScene(event.pos())):
                event.accept()
                self._mouseContext = self.ToolMouseContext
        else:
            super().mousePressEvent(event)
            if event.isAccepted():
                self._mouseContext = self.SceneMouseContext
        
        self.g_button = event.button()
        self.centerPoint = self.mapToParent(self.viewport().rect().center())
        self.startPoint = self.mapToParent(event.pos())
        
        if not event.isAccepted():
            if event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier:
                # 创建橡皮筋工具
                t = RubberBandTool(self)
                t.done.connect(lambda: self.setTool(None))
                self.setTool(t)
                if self._tool.mousePressEvent(self.mapToScene(event.pos())):
                    event.accept()
                    self._mouseContext = self.ToolMouseContext
            elif event.button() == Qt.LeftButton:
                self._lastMouse = event.pos()
                event.accept()
            elif event.button() == Qt.RightButton and self._tool:
                self._tool.cancel()
                event.accept()
                self._ignoreContextMenu = True
        
        # 如果右键事件被捕获，不显示上下文菜单
        if event.button() == Qt.RightButton:
            self._ignoreContextMenu = event.isAccepted() and (self._mouseContext != self.SceneMouseContext)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self._tool and self.scene():
            self.scene().update()  # 工具可能需要重绘
        
        if self._mouseContext == self.ToolMouseContext:
            if self._tool:
                self._tool.mouseMoveEvent(self.mapToScene(event.pos()))
            event.accept()
        
        elif self._mouseContext == self.SceneMouseContext:
            super().mouseMoveEvent(event)
        
        elif self._mouseContext == self.PanningMouseContext:
            if self.g_button == Qt.LeftButton:
                mouse = event.pos()
                mouseDiff = mouse - self._lastMouse
                self._lastMouse = mouse
                mappedMouseDiff = self.mapToScene(0, 0) - self.mapToScene(mouseDiff)
                self.translateView(mappedMouseDiff.x(), mappedMouseDiff.y())
        
        elif self._mouseContext == self.DefaultMouseContext:
            if event.buttons() & Qt.LeftButton:
                self.viewport().setCursor(Qt.ClosedHandCursor)
                self._mouseContext = self.PanningMouseContext
            elif event.buttons() & Qt.RightButton:
                self.currentPoint = self.mapToParent(event.pos())
                
                from PyQt5.QtCore import QLineF
                lineBegin = QLineF(self.centerPoint, self.startPoint)
                lineEnd = QLineF(self.centerPoint, self.currentPoint)
                self.mouseAngle = lineBegin.angleTo(lineEnd)
                
                angel = self.mouseAngle - self.lastAngle
                
                if (self.mouseAngle > self.lastAngle and abs(angel) < 350 and 
                    not self.firstMove):
                    self.rotateAngle += angel
                    self.rotate(angel)
                elif (self.mouseAngle < self.lastAngle and abs(angel) < 350 and 
                      not self.firstMove):
                    self.rotateAngle += angel
                    self.rotate(angel)
                
                self.lastAngle = self.mouseAngle
                if self.firstMove:
                    self.firstMove = False
                
                self.update()
                self.rotateChanged.emit(round(self.rotateAngle, 2))
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.firstMove = True
        
        if self._mouseContext == self.ToolMouseContext:
            if self._tool:
                self._tool.mouseReleaseEvent(self.mapToScene(event.pos()))
            event.accept()
        
        elif self._mouseContext == self.SceneMouseContext:
            super().mouseReleaseEvent(event)
        
        elif self._mouseContext == self.PanningMouseContext:
            self._lastMouse = QPoint()
            self.viewport().unsetCursor()
        
        elif self._mouseContext == self.DefaultMouseContext:
            if event.button() == Qt.LeftButton:
                if self._tool:
                    self._tool.clicked(self.mapToScene(event.pos()))
                else:
                    # 清除选择
                    if self.scene():
                        self.scene().clearSelection()
        
        self._mouseContext = self.DefaultMouseContext
    
    def contextMenuEvent(self, event):
        """上下文菜单事件"""
        # 这个右键事件之前被捕获了，不执行菜单
        if self._ignoreContextMenu and event.reason() == event.Mouse:
            self._ignoreContextMenu = False
            return
        
        super().contextMenuEvent(event)
        
        # 如果没有项目接受事件，显示场景菜单
        if not event.isAccepted():
            # 这里可以显示自定义的场景菜单
            pass
    
    def wheelEvent(self, event):
        """鼠标滚轮事件"""
        delta = event.angleDelta().y()
        s = 2 - math.pow(2, delta / 360.0)
        self.scaleView(s, s, self.mapToScene(event.pos()))
    
    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        self.fitInView(self._visibleRect, Qt.KeepAspectRatio)
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        self.fitInView(self._visibleRect, Qt.KeepAspectRatio)
        size = event.size()
        self.sizeChanged.emit(size)
    
    def keyPressEvent(self, event):
        """键盘按下事件"""
        if event.key() == Qt.Key_Escape and self._tool:
            event.accept()
            self._tool.cancel()
        else:
            super().keyPressEvent(event)
    
    def drawOrigin(self, painter):
        """绘制原点"""
        p = QPointF(0, 0)
        painter.setPen(QPen(QBrush(Qt.red), 0))
        painter.drawEllipse(p, 0.05, 0.05)
    
    def drawGrid(self, painter, rect):
        """绘制网格"""
        # 添加一些空间，以防十字中心不在绘图矩形中
        adjusted = rect.adjusted(-0.025, -0.025, 0.025, 0.025)
        
        width = self._viewSettings.gridWidth()
        height = self._viewSettings.gridHeight()
        
        left = width * math.ceil(adjusted.left() / width)
        top = height * math.ceil(adjusted.top() / height)
        
        painter.setPen(QPen(QBrush(Qt.lightGray), 0))
        
        if width > 0 and height > 0:
            x = left
            while x < adjusted.right():
                y = top
                while y < adjusted.bottom():
                    painter.drawLine(QPointF(x, y - 0.025), QPointF(x, y + 0.025))
                    painter.drawLine(QPointF(x - 0.025, y), QPointF(x + 0.025, y))
                    y += height
                x += width
    
    def drawFloorplan(self, painter, rect):
        """绘制平面图"""
        pm = self._viewSettings.floorplanPixmap()
        
        if not pm.isNull():
            painter.save()
            transform = self._viewSettings.floorplanTransform()
            transform.scale(1, -1)  # 应用垂直翻转
            painter.setTransform(transform, True)
            painter.translate(0, -pm.height())
            painter.setPen(QPen(QBrush(Qt.black), 1))
            painter.drawPixmap(0, 0, pm)
            painter.drawRect(0, 0, pm.width(), pm.height())
            painter.restore()
    
    def drawForeground(self, painter, rect):
        """绘制前景"""
        super().drawForeground(painter, rect)
        
        if self._tool:
            self._tool.draw(painter, rect, self.mapToScene(self.mapFromGlobal(QCursor.pos())))
    
    def drawBackground(self, painter, rect):
        """绘制背景"""
        super().drawBackground(painter, rect)
        
        if self._viewSettings.getFloorplanShow():
            self.drawFloorplan(painter, rect)
        
        if self._viewSettings.gridShow():
            self.drawGrid(painter, rect)
        
        if self._viewSettings.originShow():
            self.drawOrigin(painter)
    
    def setTool(self, tool):
        """设置工具"""
        if self._tool:
            try:
                self._tool.done.disconnect(self.toolDone)
                self._tool.destroyed.disconnect(self.toolDestroyed)
            except:
                pass
            self._tool.cancel()
            self.unsetCursor()
        
        self._tool = tool
        
        if self._tool:
            self._tool.setView(self)
            self.setCursor(self._tool.cursor())
            self._tool.done.connect(self.toolDone)
            # 注意：destroyed信号在PyQt中需要特殊处理
    
    def resetRotate(self):
        """重置旋转"""
        self.rotate(-self.rotateAngle)
        self.rotateAngle = 0
    
    def floorplanChanged(self):
        """平面图改变时调用"""
        if self.scene():
            self.scene().update()
    
    def gridChanged(self):
        """网格改变时调用"""
        if self.scene():
            self.scene().update()
    
    def originChanged(self):
        """原点改变时调用"""
        if self.scene():
            self.scene().update()
    
    def toolDone(self):
        """工具完成"""
        if self.sender() != self._tool:
            return
        
        try:
            self._tool.done.disconnect(self.toolDone)
        except:
            pass
        
        self.unsetCursor()
        self._tool = None
        
        if self.scene():
            self.scene().update()
    
    def toolDestroyed(self):
        """工具被销毁"""
        self.unsetCursor()
        self._tool = None
    
    def eventFilter(self, obj, event):
        """事件过滤器"""
        if obj == self.viewport():
            if event.type() == event.MouseButtonPress:
                # 处理视口鼠标事件
                pass
        return super().eventFilter(obj, event)

class ViewSettings(QObject):
    """视图设置类"""
    floorplanChanged = pyqtSignal()
    gridChanged = pyqtSignal()
    originChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._floorplanShow = False
        self._gridShow = True
        self._originShow = True
        self._gridWidth = 1.0
        self._gridHeight = 1.0
        self._floorplanPixmap = QPixmap()
        self._floorplanTransform = QTransform()
    
    def getFloorplanShow(self):
        """获取是否显示平面图"""
        return self._floorplanShow
    
    def setFloorplanShow(self, show):
        """设置是否显示平面图"""
        if self._floorplanShow != show:
            self._floorplanShow = show
            self.floorplanChanged.emit()
    
    def gridShow(self):
        """获取是否显示网格"""
        return self._gridShow
    
    def setGridShow(self, show):
        """设置是否显示网格"""
        if self._gridShow != show:
            self._gridShow = show
            self.gridChanged.emit()
    
    def originShow(self):
        """获取是否显示原点"""
        return self._originShow
    
    def setOriginShow(self, show):
        """设置是否显示原点"""
        if self._originShow != show:
            self._originShow = show
            self.originChanged.emit()
    
    def gridWidth(self):
        """获取网格宽度"""
        return self._gridWidth
    
    def setGridWidth(self, width):
        """设置网格宽度"""
        self._gridWidth = width
        if self._gridShow:
            self.gridChanged.emit()
    
    def gridHeight(self):
        """获取网格高度"""
        return self._gridHeight
    
    def setGridHeight(self, height):
        """设置网格高度"""
        self._gridHeight = height
        if self._gridShow:
            self.gridChanged.emit()
    
    def floorplanPixmap(self):
        """获取平面图图像"""
        return self._floorplanPixmap
    
    def setFloorplanPixmap(self, pixmap):
        """设置平面图图像"""
        self._floorplanPixmap = pixmap
        if self._floorplanShow:
            self.floorplanChanged.emit()
    
    def floorplanTransform(self):
        """获取平面图变换"""
        return self._floorplanTransform
    
    def setFloorplanTransform(self, transform):
        """设置平面图变换"""
        self._floorplanTransform = transform
        if self._floorplanShow:
            self.floorplanChanged.emit()

# 工具管理器
class ToolManager:
    """工具管理器"""
    def __init__(self):
        self._tools = {}
        self._currentTool = None
    
    def registerTool(self, name, toolClass):
        """注册工具"""
        self._tools[name] = toolClass
    
    def getTool(self, name):
        """获取工具"""
        return self._tools.get(name)
    
    def createTool(self, name, view=None):
        """创建工具实例"""
        toolClass = self.getTool(name)
        if toolClass:
            return toolClass(view)
        return None

# 全局工具管理器实例
toolManager = ToolManager()

# 注册默认工具
toolManager.registerTool("rubberband", RubberBandTool)
toolManager.registerTool("pan", PanTool)
toolManager.registerTool("zoom", ZoomTool)

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsRectItem
    
    # 设置DPI策略
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # 创建视图
    view = GraphicsView()
    
    # 创建场景
    scene = QGraphicsScene()
    view.setScene(scene)
    
    # 添加一些测试项目
    rect = QGraphicsRectItem(-5, -5, 10, 10)
    rect.setPen(QPen(Qt.red))
    rect.setBrush(QBrush(Qt.yellow))
    scene.addItem(rect)
    
    # 创建测试工具
    rubberTool = RubberBandTool(view)
    view.setTool(rubberTool)
    
    view.show()
    
    sys.exit(app.exec_())