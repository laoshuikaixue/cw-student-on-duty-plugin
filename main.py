import json

from PyQt5 import uic
from PyQt5.QtWidgets import QHBoxLayout, QLabel
from loguru import logger
from qfluentwidgets import ComboBox

from .ClassWidgets.base import PluginBase, SettingsBase, PluginConfig

# 自定义小组件
WIDGET_CODE = 'duty_widget.ui'
WIDGET_NAME = '值日生组件'
WIDGET_WIDTH = 245


class Plugin(PluginBase):  # 插件类
    def __init__(self, cw_contexts, method):  # 初始化
        super().__init__(cw_contexts, method)  # 调用父类初始化方法

        self.method.register_widget(WIDGET_CODE, WIDGET_NAME, WIDGET_WIDTH)  # 注册小组件到CW
        self.cfg = PluginConfig(self.PATH, 'config.json')  # 实例化配置类

        logger.debug("Loading duty_list.json data.")
        # 加载 duty_list.json 数据
        with open(f'{self.PATH}/duty_list.json', 'r', encoding='utf-8') as f:
            self.duty_list = json.load(f)

        self.duty_label = None  # 初始化 duty_label 属性
        logger.debug("Plugin initialized.")

    def execute(self):  # 自启动执行部分
        # 小组件自定义（照PyQt的方法正常写）
        self.duty_widget = self.method.get_widget(WIDGET_CODE)  # 获取小组件对象

        if self.duty_widget:  # 判断小组件是否存在
            contentLayout = self.duty_widget.findChild(QHBoxLayout, 'contentLayout')  # 内容布局
            contentLayout.setSpacing(1)  # 设置间距

            self.duty_label = QLabel('')  # 值日生标签
            contentLayout.addWidget(self.duty_label)  # 添加标签到布局

        self.update_duty_info()

        logger.success('Duty Plugin executed!')

    def update(self, cw_contexts):  # 自动更新部分
        super().update(cw_contexts)  # 调用父类更新方法
        self.cfg.update_config()  # 更新配置

        self.update_duty_info()

    def update_duty_info(self):
        if self.duty_label:  # 判断 duty_label 是否存在
            group = self.cfg['group']  # 获取当前组别

            # 查找当前组别的值日生信息
            duty_info = [d['name'] for d in self.duty_list if d['group'] == group]
            duty_names = '  ' + ' '.join(duty_info).strip() if duty_info else '无值日生'

            # 更新小组件标题和内容
            widget_title = '今日值日生 | LaoShui'
            self.method.change_widget_content(WIDGET_CODE, widget_title, f'{duty_names}')


# 设置页
class Settings(SettingsBase):
    def __init__(self, plugin_path, parent=None):
        super().__init__(plugin_path, parent)
        uic.loadUi(f'{self.PATH}/settings.ui', self)  # 加载设置界面

        default_config = {
            "group": "1"
        }

        self.cfg = PluginConfig(self.PATH, 'config.json')  # 实例化配置类
        self.cfg.load_config(default_config)  # 加载配置

        # 组别选择框
        self.groupComboBox = self.findChild(ComboBox, 'groupComboBox')
        self.load_group_options()

        self.groupComboBox.setCurrentText(self.cfg['group'])
        self.groupComboBox.currentIndexChanged.connect(
            lambda: self.cfg.upload_config('group', self.groupComboBox.currentText()))
        logger.debug("Settings initialized.")

    def load_group_options(self):
        logger.debug("Loading group options from duty_list.json.")
        # 从 duty_list.json 读取组别选项
        with open(f'{self.PATH}/duty_list.json', 'r', encoding='utf-8') as f:
            duty_list = json.load(f)

        groups = sorted(set(d['group'] for d in duty_list))  # 获取所有组别，并去重排序
        self.groupComboBox.addItems(groups)  # 添加组别选项
        logger.info(f"Loaded groups: {groups}")
