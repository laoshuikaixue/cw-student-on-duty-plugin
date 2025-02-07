# cw-student-on-duty-plugin(LaoShui)

## 简介
一个用于展示班级值日生信息的插件，能够根据配置文件中的组别信息，动态显示当前组别的值日生名单。

插件配备了可视化编辑面板，用户可以快速编辑值日生列表。
![QQ20250114-150910](https://github.com/user-attachments/assets/2abedd0e-3ec9-48e4-be68-0f022950cd31)

## 可视化编辑面板使用方法
1. 打开插件目录下的`web`目录 修改`student_list.txt`文件为自己班级的姓名词库
2. 打开插件的设置页面启动本地服务器打开编辑面板（部分用户出现`未发送任何数据`的错误提示 原因正在排查）
3. 编辑完成后 导出数据 放到插件的运行目录下（与`main.py`文件同级）即可使用
> [!NOTE]
> 
> 目前只有10个组别和一个临时组别，7个类别。如果需要更多组别，请自行编辑`index.html`文件，仿照已有的类别进行添加即可（更改后使用`Ctrl + R`刷新）

## 主要功能
- **显示值日生信息**：根据配置文件中的组别信息，动态显示当前组别的值日生名单。
- **配置组别**：通过设置界面，用户可以更改当前显示的组别。

## 配置文件
- **config.json**：存储当前组别的配置信息。
- **duty_list.json**：存储各组别的值日生名单信息。

Powered By LaoShui @ 2025
