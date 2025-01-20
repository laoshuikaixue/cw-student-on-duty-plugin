import json

from PyQt5 import uic
from PyQt5.QtCore import QUrl, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QScrollBar, QScrollArea, QWidget, QVBoxLayout
from loguru import logger
from qfluentwidgets import ComboBox, PrimaryPushButton, isDarkTheme
from .ClassWidgets.base import SettingsBase, PluginConfig, PluginBase

# 自定义小组件
WIDGET_CODE = 'duty_widget.ui'
WIDGET_NAME = '值日生组件 | LaoShui'
WIDGET_WIDTH = 245


class SmoothScrollBar(QScrollBar):
    """平滑滚动条"""
    scrollFinished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ani = QPropertyAnimation(self, b"value")
        self.ani.setEasingCurve(QEasingCurve.OutCubic)
        self.ani.setDuration(400)  # 设置动画持续时间
        self.ani.finished.connect(self.scrollFinished)

    def setValue(self, value: int):
        if value != self.value():
            self.ani.stop()
            self.scrollFinished.emit()
            self.ani.setStartValue(self.value())
            self.ani.setEndValue(value)
            self.ani.start()

    def wheelEvent(self, e):
        e.ignore()  # 阻止默认滚轮事件


class SmoothScrollArea(QScrollArea):
    """平滑滚动区域"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vScrollBar = SmoothScrollBar()
        self.setVerticalScrollBar(self.vScrollBar)
        self.setStyleSheet("QScrollBar:vertical { width: 0px; }")  # 隐藏滚动条

    def wheelEvent(self, e):
        if hasattr(self.vScrollBar, 'setValue'):
            self.vScrollBar.setValue(self.vScrollBar.value() - e.angleDelta().y())


class Plugin(PluginBase):
    def __init__(self, cw_contexts, method):
        super().__init__(cw_contexts, method)
        self.cw_contexts = cw_contexts
        self.method = method
        self.CONFIG_PATH = f'{cw_contexts["PLUGIN_PATH"]}/config.json'
        self.PATH = cw_contexts['PLUGIN_PATH']
        self.cfg = PluginConfig(self.PATH, 'config.json')

        self.method.register_widget(WIDGET_CODE, WIDGET_NAME, WIDGET_WIDTH)

        self.scroll_position = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_scroll)
        self.timer.start(30)  # 设置滚动速度

        self.load_duty_info()  # 加载值日生信息
        self.previous_group = self.cfg['group']  # 保存初始组别值

    def load_duty_info(self):
        """加载 duty_list.json 数据"""
        try:
            with open(f'{self.PATH}/duty_list.json', 'r', encoding='utf-8') as f:
                self.duty_list = json.load(f)
        except FileNotFoundError:
            logger.error("未找到 duty_list.json 文件，请先设置值日生数据!")
            self.duty_list = []

    def update_duty_info(self):
        """更新值日生信息"""
        group = self.cfg['group']  # 获取当前组别
        duty_info = [f"{d['name']} - {d['category']}号" for d in self.duty_list if d['group'] == group]
        duty_names = '\n'.join(duty_info).strip() if duty_info else '请先设置值日生数据！'
        self.update_widget_content(duty_names)

    def update_widget_content(self, duty_names):
        """更新小组件内容"""
        self.test_widget = self.method.get_widget(WIDGET_CODE)
        if not self.test_widget:
            logger.error(f"未找到小组件，WIDGET_CODE: {WIDGET_CODE}")
            return

        content_layout = self.find_child_layout(self.test_widget, 'contentLayout')
        if not content_layout:
            logger.error("未能找到小组件的'contentLayout'布局")
            return

        content_layout.setSpacing(5)
        self.method.change_widget_content(WIDGET_CODE, WIDGET_NAME, WIDGET_NAME)
        self.clear_existing_content(content_layout)

        scroll_area = self.create_scroll_area(duty_names)
        if scroll_area:
            content_layout.addWidget(scroll_area)
            logger.success('值日生信息更新成功！')
        else:
            logger.error("滚动区域创建失败")

    @staticmethod
    def find_child_layout(widget, layout_name):
        """根据名称查找并返回布局"""
        return widget.findChild(QHBoxLayout, layout_name)

    def create_scroll_area(self, duty_names):
        scroll_area = SmoothScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_content_layout = QVBoxLayout()
        scroll_content.setLayout(scroll_content_layout)
        self.clear_existing_content(scroll_content_layout)

        font_color = "#FFFFFF" if isDarkTheme() else "#000000"
        content_label = QLabel(duty_names)
        content_label.setAlignment(Qt.AlignCenter)
        content_label.setWordWrap(True)
        content_label.setStyleSheet(f"""
            font-size: 25px;
            color: {font_color};
            padding: 10px;
            font-weight: bold;
            background: none;
        """)
        scroll_content_layout.addWidget(content_label)

        scroll_area.setWidget(scroll_content)
        return scroll_area

    @staticmethod
    def clear_existing_content(content_layout):
        """清除布局中的旧内容"""
        while content_layout.count() > 0:
            item = content_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()  # 确保子组件被销毁

    def auto_scroll(self):
        """自动滚动功能"""
        if not self.test_widget:
            return

        scroll_area = self.test_widget.findChild(SmoothScrollArea)
        if not scroll_area:
            logger.warning("无法找到 SmoothScrollArea，停止自动滚动")
            return

        vertical_scrollbar = scroll_area.verticalScrollBar()
        if not vertical_scrollbar:
            logger.warning("无法找到垂直滚动条，停止自动滚动")
            return

        max_value = vertical_scrollbar.maximum()
        self.scroll_position = 0 if self.scroll_position >= max_value else self.scroll_position + 1
        vertical_scrollbar.setValue(self.scroll_position)

    def update(self, cw_contexts):
        super().update(cw_contexts)
        self.cfg.update_config()

        current_group = self.cfg['group']
        if current_group != self.previous_group:
            self.update_duty_info()
            self.previous_group = current_group

    def execute(self):
        self.update_duty_info()
        logger.success('Duty Plugin executed!')


class Settings(SettingsBase):
    def __init__(self, plugin_path, parent=None):
        super().__init__(plugin_path, parent)
        uic.loadUi(f'{self.PATH}/settings.ui', self)  # 加载设置界面

        default_config = {"group": "1"}
        self.cfg = PluginConfig(self.PATH, 'config.json')
        self.cfg.load_config(default_config)

        self.groupComboBox = self.findChild(ComboBox, 'groupComboBox')
        self.load_group_options()
        self.groupComboBox.setCurrentText(self.cfg['group'])
        self.groupComboBox.currentIndexChanged.connect(
            lambda: self.cfg.upload_config('group', self.groupComboBox.currentText()))

        self.openWebButton = PrimaryPushButton('打开值日生编辑器', self)
        self.openWebButton.clicked.connect(self.open_web_editor)
        self.verticalLayout.addWidget(self.openWebButton)

        logger.debug("Settings initialized.")

    def open_web_editor(self):
        web_path = QUrl.fromLocalFile(f'{self.PATH}/web/index.html').toString()
        QDesktopServices.openUrl(QUrl(web_path))

    def load_group_options(self):
        logger.debug("从 duty_list.json 加载组别选项")
        try:
            with open(f'{self.PATH}/duty_list.json', 'r', encoding='utf-8') as f:
                duty_list = json.load(f)
        except FileNotFoundError:
            logger.error("未找到 duty_list.json 文件，请先设置值日生数据!")
            duty_list = []

        groups = sorted(set(d['group'] for d in duty_list))  # 获取所有组别，并去重排序
        self.groupComboBox.addItems(groups)  # 添加组别选项
        logger.info(f"加载的组别: {groups}")
