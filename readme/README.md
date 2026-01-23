# ========== 关于为什么使用 RTLSDisplayApplication.viewSettings() ==========
"""
解答你的问题：

**为什么 ViewSettingsWidget 在初始化连接信号时要用 
RTLSDisplayApplication::viewSettings() 而不是 self？**

1. **单例模式架构**
   - RTLSDisplayApplication 是应用程序的单例类
   - ViewSettings 是全局配置对象，也是单例
   - ViewSettingsWidget 是 UI 组件，可能有多个实例

2. **实例化顺序**
   C++ 代码中的实例化顺序：
   ```cpp
   RTLSDisplayApplication::RTLSDisplayApplication() {
       _viewSettings = new ViewSettings(this);      // 1. 先创建ViewSettings
       _serialConnection = new SerialConnection(this);
       _client = new RTLSClient(this);
       _mainWindow = new MainWindow();              // 2. 创建MainWindow
       // MainWindow 构造函数中会创建 ViewSettingsWidget
       _ready = true;
       emit ready();  // 3. 发出ready信号
   }
   ```

3. **连接的是 ViewSettings 的信号，不是 ViewSettingsWidget 的信号**
   - `RTLSDisplayApplication::viewSettings()` 返回的是 **ViewSettings 对象**（数据模型）
   - `ViewSettingsWidget` 是 **UI 组件**（视图）
   - 信号 `floorplanChanged()` 是 **ViewSettings** 发出的，不是 ViewSettingsWidget 发出的

4. **MVC 模式**
   ```
   ViewSettings (Model)          ←─ 数据模型，存储配置
        ↓ signals
   ViewSettingsWidget (View)     ←─ UI组件，显示和操作
        ↓ slots
   GraphicsView                  ←─ 响应配置变化
   ```

5. **Python 中的对应关系**
   ```python
   # ViewSettings 类（需要单独创建，类似C++的ViewSettings）
   class ViewSettings(QObject):
       floorplanChanged = pyqtSignal()
       showGrid = True
       gridWidth = 1.0
       # ... 更多配置
   
   # ViewSettingsWidget 连接 ViewSettings 的信号
   def onReady(self):
       # 连接的是全局 ViewSettings 对象的信号
       RTLSDisplayApplication.viewSettings().floorplanChanged.connect(
           self.floorplanChanged)  # self 是 ViewSettingsWidget
   ```

**总结**：
- 使用 `RTLSDisplayApplication.viewSettings()` 是为了访问**全局配置对象**
- 这个配置对象在 ViewSettingsWidget 创建**之前**就已经被 RTLSDisplayApplication 实例化了
- ViewSettingsWidget 只是配置的 UI 界面，真正的数据存储在 ViewSettings 中
- 这是典型的 **MVC (Model-View-Controller)** 设计模式
"""
        