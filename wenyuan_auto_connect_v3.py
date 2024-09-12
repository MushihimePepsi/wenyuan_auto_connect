"""
这个是加上显示状态的版本，比较复杂。
@Version: 3.0
@Date: 2024/09/11
@Author: MushihimePepsi
@Email: mushihimepepsi@gmail.com
"""

import sys
import os
import subprocess
import logging
import requests
import time
import random
import json
import schedule
from urllib import request
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
from threading import Thread

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
        open_folder_action = QAction("Open Log Folder", self.tray_icon)
        open_folder_action.triggered.connect(self.open_log_folder)
        self.menu.addAction(open_folder_action)

        # 添加退出按钮
        exit_action = QAction("Exit", self.tray_icon)
        exit_action.triggered.connect(self.quit_app)
        self.menu.addAction(exit_action)

        self.tray_icon.setContextMenu(self.menu)

        # 设置并显示托盘图标
        self.tray_icon.show()

    def open_log_folder(self):
        """打开软件所在目录"""
        if os.path.isdir(self.app_path):
            subprocess.Popen(f'explorer "{self.app_path}"' if os.name == 'nt' else ['open', self.app_path])

    def quit_app(self):
        """退出应用"""
        QCoreApplication.quit()

    def logout(self):
        """登出操作"""
        try:
            response = requests.post(self.logout_URL, headers=self.headers, data=self.logout_data)
            if response.status_code == 200:
                logging.info("成功登出")
            else:
                logging.error(f"登出失败: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"登出时出现异常: {e}")

    def login_status_check(self, user_data, info_URL, login_URL):
        """检测登录状态并执行登录操作"""
        while True:
            reply_code = -1

            try:
                response = request.urlopen(info_URL)
                html = response.read()
                json_str = html.decode(encoding="utf-8", errors="strict")
                data = json.loads(json_str)
                reply_code = data.get("reply_code")
            except Exception as e:
                logging.error(e)

            if reply_code == 0:
                logging.info("已登录")
            elif reply_code == 404:
                logging.info("当前未登录，尝试登录...")
                response = requests.post(login_URL, headers=self.headers, data=user_data).status_code
                logging.info(f"已尝试登录：状态码 {response}")
            else:
                logging.info("请检查是否连接到宿舍网")

            # 每5分钟检查一次
            rand = random.uniform(0, 30)
            time.sleep(300.0 + rand)

    def log_file_check(self, log_file_path):
        """检查日志文件大小并清空"""
        if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > 16 * 1024 * 1024:
            with open(log_file_path, 'w'):
                pass  # 清空日志文件
            logging.info("日志文件过大，已清空")

def main():
    app = QApplication(sys.argv)

    # 获取软件所在目录的路径
    app_path = os.path.dirname(os.path.abspath(__file__))
    icon = QIcon('q_icon.png')

    # 日志文件配置
    log_file_path = 'auto_connect.log'
    logging.basicConfig(filename=log_file_path, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
    logging.info("自动联网脚本开始运行...")

    # 创建托盘图标实例
    tray_icon = SystemTrayIcon(icon, app_path)

    # 读取用户数据
    user_data_path = 'user_data.txt'
    with open(user_data_path, 'r', encoding='utf-8') as file:
        user_data = file.read()

    # API URL
    info_URL = 'http://10.10.16.12/api/portal/v1/getinfo'
    login_URL = 'http://10.10.16.12/api/portal/v1/login'

    # 定时任务安排
    schedule.every(24).hours.do(tray_icon.logout)

    # 启动线程进行登录状态检查
    login_thread = Thread(target=tray_icon.login_status_check, args=(user_data, info_URL, login_URL))
    login_thread.start()

    # 启动日志文件大小检查
    log_check_thread = Thread(target=tray_icon.log_file_check, args=(log_file_path,))
    log_check_thread.start()

    # 启动计划任务
    schedule_thread = Thread(target=schedule.run_pending)
    schedule_thread.start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
