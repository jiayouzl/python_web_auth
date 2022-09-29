# -*- coding: UTF-8 -*-

import hashlib
import json
import os
import subprocess
import sys
import time

import requests

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))  # 或sys.path.append('../../')
from aes_model import AEScryptor

HOST = 'http://127.0.0.1:8081/'


# 获取机器码(MacOS)
def get_serial_number():
    cmd = "system_profiler SPHardwareDataType | grep 'Serial Number' | awk '{print $4}'"
    result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True)
    return result.stdout.strip().decode('utf-8')


# 校检是否为json格式
def check_json_format(raw_msg):
    if isinstance(raw_msg, str):
        try:
            json.loads(raw_msg)
        except ValueError:
            return False
        return True
    else:
        return False


# 注册机器码
def reg_machine_code(machine_code):
    url = HOST + 'reg'
    data = {'machineCode': machine_code}
    response = requests.request('POST', url, json=data)
    return response.json()


# 机器码验证
def verify_machine_code(machine_code):
    # Api接口签名认证
    key = 'rrm652gz4atq7jqc'
    timestamp = str(time.time())[:10]
    sign = hashlib.md5((machine_code + timestamp + key).encode('utf-8')).hexdigest()
    headers = dict(timestamp=timestamp, sign=sign)

    url = HOST + 'login'
    data = {'machineCode': machine_code}
    response = requests.request('POST', url, json=data, headers=headers)
    try:
        return json.loads(response.text)
    except ValueError:
        key = 'vqwn3p22uics8xv8'  # 16位
        iv = 's0Q~ioZ(AYJxyvLQ'  # 16位
        aes = AEScryptor(key=key, iv=iv, paddingMode='ZeroPadding', characterSet='utf-8')
        rData = aes.decryptFromBase64(response.text)
        # print('明文：', rData)
        dic_str = json.loads(str(rData).replace("'", "\""))
        time_ = int(time.time()) - dic_str['nowtime']
        if time_ > 600 or time_ < -600:
            return '防破解时间戳校验失败'
        else:
            return dic_str


# 机器码充值
def recharge_machine_code(machine_code, card_number, card_password):
    url = HOST + 'recharge'
    data = {'machineCode': machine_code, 'card_number': card_number, 'card_password': card_password}
    response = requests.request('POST', url, json=data)
    return response.json()


if __name__ == '__main__':
    print(int(time.time()))
    # 获取机器码
    # print(get_serial_number())
    # 注册机器码
    # print(reg_machine_code(get_serial_number()))
    # 机器码验证
    # print(verify_machine_code(get_serial_number()))
    # 机器码充值
    # print(recharge_machine_code(get_serial_number(), '20220902EPEHT', 'SAVXWOQM'))