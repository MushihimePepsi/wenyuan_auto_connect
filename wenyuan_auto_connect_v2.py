"""
这个是只有退出的托盘的版本，后续3.0版加上显示状态比较复杂。
@Version: 2.0
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
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu


class SystemTrayIcon:
    def __init__(self, icon, menu):
        self.tray_icon = QSystemTrayIcon(QIcon('q_icon.png'))
        self.tray_icon.setContextMenu(menu)

    def show(self):
        self.tray_icon.show()

    def exit(self):
        self.tray_icon.hide()


app = QApplication(sys.argv)
menu = QMenu()
exit_action = menu.addAction("Exit")
exit_action.triggered.connect(app.quit)
system_tray_icon = SystemTrayIcon("icon.png", menu)
system_tray_icon.show()
sys.exit(app.exec_())

def logout():
    requests.post(logout_URL, headers=headers, data=logout_data)
    logging.info("尝试登出")


# 设置用户数据、日志文件路径
user_data_path = 'user_data.txt'
log_file_path = 'auto_connect.log'
with open(user_data_path, 'r', encoding='utf-8') as file:
    user_data = file.read()

# 用于登录和获取登录状态的链接
login_URL = 'http://10.10.16.12/api/portal/v1/login'
info_URL = 'http://10.10.16.12/api/portal/v1/getinfo'
logout_URL = 'http://10.10.16.12/api/portal/v1/logout'
headers = {'Content-Type': 'application/json; charset=utf-8'}
logout_data = '{"domain":"default"}'

# 配置日志记录器
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')

logging.info("自动联网脚本开始运行...")
# 启动时刷新登录状态
logout()
# 安排每24小时执行一次命令
schedule.every(24).hours.do(logout)


while True:
    reply_code = -1

    try:
        # 检查是否登录，获取当前状态
        response = request.urlopen(info_URL)
        html = response.read()
        json_str = html.decode(encoding="utf-8", errors="strict")
        # print(json_str)
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
        response = requests.post('http://10.10.16.12/api/portal/v1/login', headers = headers, data = data).status_code  # POST 方式向 URL 发送表单，同时获取状态码
        # print("状态码{}".format(response))  # 打印状态码
        logging.info("已尝试登录：{}".format(response))


    # 此时不在宿舍网中
    else:
        cur_status = "请检查是否连接到宿舍网"
        logging.info(cur_status)
        # print(cur_status)
        pass


    # 检查文件大小，如果大于16MB则清空文件
    if os.path.getsize(log_file_path) > 16*1024*1024:
        open(log_file_path, 'w').close()

    # 每5min左右检测一次是否成功连接
    rand = random.uniform(0, 30)
    # print("休眠",int(300.0 + rand),"s")
    time.sleep(300.0 + rand)

    schedule.run_pending()
    time.sleep(1)  # 让CPU休息一下

