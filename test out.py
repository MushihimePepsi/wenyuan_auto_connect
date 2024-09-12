"""
@Version:
@Date: 2024/09/11
@Author: MushihimePepsi
@Email: mushihimepepsi@gmail.com
"""

from urllib import request
import requests
import schedule
import time
import random
import os
import json
import logging

import sys
import os

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
import subprocess


class SystemTrayIcon:
    def __init__(self, icon, app_path):
        self.app_path = app_path  # 软件所在目录的路径
        self.tray_icon = QSystemTrayIcon(QIcon(icon))
        self.logout_URL = 'http://10.10.16.12/api/portal/v1/logout'
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}
        self.logout_data = '{"domain":"default"}'

        # 创建菜单
        self.menu = QMenu()

        # 添加打开软件所在目录的按钮
        open_folder_action = QAction("Open App Folder", self.tray_icon)
        open_folder_action.triggered.connect(self.open_app_folder)
        self.menu.addAction(open_folder_action)

        # 添加退出按钮
        exit_action = QAction("Exit", self.tray_icon)
        exit_action.triggered.connect(self.quit_app)
        self.menu.addAction(exit_action)

        self.tray_icon.setContextMenu(self.menu)

        # 设置并显示托盘图标
        self.tray_icon.show()

    def open_app_folder(self):
        """打开软件所在目录"""
        if os.path.isdir(self.app_path):
            # 使用默认文件管理器打开目录
            subprocess.Popen(f'explorer "{self.app_path}"' if os.name == 'nt' else ['open', self.app_path])

    def quit_app(self):
        """退出应用"""
        QCoreApplication.quit()

    def logout(self):
        requests.post(self.logout_URL, headers=self.headers, data=self.logout_data)
        logging.info("尝试登出")

    # 设置用户数据、日志文件路径
    user_data_path = 'user_data.txt'
    log_file_path = 'auto_connect.log'
    with open(user_data_path, 'r', encoding='utf-8') as file:
        user_data = file.read()

    # 用于登录和获取登录状态的链接
    login_URL = 'http://10.10.16.12/api/portal/v1/login'
    info_URL = 'http://10.10.16.12/api/portal/v1/getinfo'

    # 配置日志记录器
    logging.basicConfig(filename=log_file_path, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        encoding='utf-8')

    logging.info("自动联网脚本开始运行...")
    # 启动时刷新登录状态
    logout()
    # 安排每24小时执行一次命令
    schedule.every(24).hours.do(logout)
    time.sleep(1)  # 等待网络刷新

    while True:
        reply_code = -1

        try:
            # 检查是否登录，获取当前状态
            response = request.urlopen(info_URL)
            html = response.read()
            json_str = html.decode(encoding="utf-8", errors="strict")
            print(json_str)
            # 使用json模块解析JSON字符串
            data = json.loads(json_str)
            # 直接访问解析后的字典中的值
            reply_code = data.get("reply_code")
        except Exception as e:
            logging.error(e)

        # 此时已经登录
        if reply_code == 0:
            cur_status = "已登录"
            logging.info(cur_status)
            # print(cur_status)
            pass


        # 此时未登录，进行登录操作
        elif reply_code == 404:
            cur_status = "当前未登录"
            logging.info(cur_status)
            # print(cur_status)
            # data = '{"domain":"telecom","username":"17388888888","password":"246135"}'
            data = user_data
            # 发送post请求
            response = requests.post('http://10.10.16.12/api/portal/v1/login', headers=headers,data=data).status_code  # POST 方式向 URL 发送表单，同时获取状态码
            # print("状态码{}".format(response))  # 打印状态码
            logging.info("已尝试登录：{}".format(response))


        # 此时不在宿舍网中
        else:
            cur_status = "请检查是否连接到宿舍网"
            logging.info(cur_status)
            # print(cur_status)
            pass

        # 检查文件大小，如果大于16MB则清空文件
        if os.path.getsize(log_file_path) > 16 * 1024 * 1024:
            open(log_file_path, 'w').close()

        # 每5min左右检测一次是否成功连接
        rand = random.uniform(0, 30)
        # print("休眠",int(300.0 + rand),"s")
        time.sleep(300.0 + rand)

        schedule.run_pending()
        time.sleep(1)  # 让CPU休息一下


    def show(self):
        self.tray_icon.show()

    def exit(self):
        self.tray_icon.hide()


    def open_app_folder(self):
        # 使用 os.startfile（Windows）或 subprocess.Popen（跨平台）来打开文件夹
        if sys.platform.startswith('win'):
            os.startfile(self.app_path)
        elif sys.platform.startswith('darwin'):
            # import subprocess
            subprocess.Popen(['open', self.app_path])
        else:
            # Linux 用户可能需要安装 xdg-utils
            try:
                subprocess.Popen(['xdg-open', self.app_path])
            except FileNotFoundError:
                print("xdg-open not found, please install xdg-utils")


def main():
    app = QApplication(sys.argv)

    # 获取软件所在目录的路径（这里假设是当前脚本所在的目录）
    app_path = os.path.dirname(os.path.abspath(__file__))
    # 加载图标
    icon = QIcon('q_icon.png')  # 确保图标文件与脚本在同一目录下，或提供正确的路径

    # 创建 SystemTrayIcon 实例
    system_tray_icon = SystemTrayIcon(icon, app_path)
    system_tray_icon.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


# app = QApplication(sys.argv)
# icon = QSystemTrayIcon(QIcon('q_icon.png'), app)
# icon.show()
# menu = QMenu(app)
# exit_action = menu.addAction("Exit")
# exit_action.triggered.connect(app.quit)
# menu.addAction(exit_action)
# icon.setContextMenu(menu)
# sys.exit(app.exec_())

# app = QApplication(sys.argv)
# menu = QMenu()
# exit_action = menu.addAction("Exit")
# exit_action.triggered.connect(app.quit)
# system_tray_icon = SystemTrayIcon("icon.png", menu)
# system_tray_icon.show()
# sys.exit(app.exec_())

