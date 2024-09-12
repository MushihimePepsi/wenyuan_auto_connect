"""
在后台运行的版本，只能通过任务管理器关闭
@Version: 1.0
@Date: 2024/09/11
@Author: MushihimePepsi
@Email: mushihimepepsi@gmail.com
"""

from urllib import request
import requests
import time
import random
import os
import json
import logging


# 设置用户数据、日志文件路径
user_data_path = 'user_data.txt'
log_file_path = 'auto_connect.log'
with open(user_data_path, 'r', encoding='utf-8') as file:
    user_data = file.read()

# 用于登录和获取登录状态的链接
post_URL = 'http://10.10.16.12/api/portal/v1/login'
get_URL = 'http://10.10.16.12/api/portal/v1/getinfo'

# print(user_data)

# 配置日志记录器
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')

logging.info("自动联网脚本开始运行...")
# print("自动联网脚本开始运行...")

while True:
    reply_code = -1

    try:
        # 检查是否登录，获取当前状态
        response = request.urlopen(get_URL)
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

        headers = {'Content-Type': 'application/json; charset=utf-8'}
        # data = '{"domain":"telecom","username":"17388888888","password":"246135"}'
        data = user_data
        # 发送post请求（设置好header和data）
        response = requests.post('http://10.10.16.12/api/portal/v1/login', headers = headers, data = data).status_code  # POST 方式向 URL 发送表单，同时获取状态码
        # print("状态码{}".format(response))  # 打印状态码
        logging.info("已尝试登录：{}".format(response))


    # 此时不在宿舍网中
    else:
        cur_status = "请检查是否连接到宿舍网"
        logging.info(cur_status)
        # print(cur_status)
        pass


    # 检查文件大小，如果大于4MB则清空文件
    if os.path.getsize(log_file_path) > 4*1024*1024:
        open(log_file_path, 'w').close()

    # 每5min左右检测一次是否成功连接
    rand = random.uniform(0, 30)
    # print("休眠",int(300.0 + rand),"s")
    time.sleep(300.0 + rand)

