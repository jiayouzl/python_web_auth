# -*- coding: UTF-8 -*-

import requests
import subprocess

HOST = 'http://127.0.0.1:8081/'


# 获取机器码(MacOS)
def get_serial_number():
    cmd = "system_profiler SPHardwareDataType | grep 'Serial Number' | awk '{print $4}'"
    result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True)
    return result.stdout.strip().decode('utf-8')


# 注册机器码
def reg_machine_code(machine_code):
    url = HOST + 'reg'
    data = {'machineCode': machine_code}
    response = requests.request('POST', url, json=data)
    return response.json()

# 机器码验证
def verify_machine_code(machine_code):
    url = HOST + 'login'
    data = {'machineCode': machine_code}
    response = requests.request('POST', url, json=data)
    return response.json()

# 机器码充值
def recharge_machine_code(machine_code, card_number, card_password):
    url = HOST + 'recharge'
    data = {'machineCode': machine_code, 'card_number': card_number, 'card_password': card_password}
    response = requests.request('POST', url, json=data)
    return response.json()


if __name__ == '__main__':
    # 获取机器码
    # print(get_serial_number())
    # 注册机器码
    # print(reg_machine_code(get_serial_number()))
    # 机器码验证
    # print(verify_machine_code(get_serial_number()))
    # 机器码充值
    # print(recharge_machine_code(get_serial_number(), '20220902EPEHT', 'SAVXWOQM'))
    pass