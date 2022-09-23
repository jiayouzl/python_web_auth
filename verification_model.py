# -*- coding: UTF-8 -*-

import math
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from random import Random

from dotenv import find_dotenv, load_dotenv
from tinydb import Query, TinyDB


class verification(object):

    def __init__(self) -> None:
        # 设置数据库文件
        self.db_user = TinyDB('./database/db.json', indent=4)
        self.db_user.default_table_name = 'user'
        self.db_card = TinyDB('./database/db.json', indent=4)
        self.db_card.default_table_name = 'card'
        # 设置时区
        self.tz = timezone(timedelta(hours=8))
        # 加载env配置环境变量
        load_dotenv(find_dotenv(str(Path.cwd().joinpath('.env'))))

    # 机器码注册
    def reg(self, machine_code: str, expire_date: str):
        result_search = self.db_user.get(Query().machine_code == machine_code)
        if result_search in [None, []]:
            result_insert = self.db_user.insert({'machine_code': machine_code, 'expire_date': expire_date, 'reg_date': datetime.now(self.tz).strftime('%Y-%m-%d %H:%M:%S')})
            # return True if result_insert > 0 else False
            if result_insert > 0:
                return {'code': 10000, 'msg': '机器码注册成功', 'expireDate': expire_date}
            else:
                return {'code': 10011, 'msg': '机器码注册失败'}
        else:
            return {'code': 10010, 'msg': '机器码已存在'}

    # 机器码登录验证
    def login(self, machine_code: str):
        result = self.db_user.search(Query().machine_code == machine_code)
        # 判断机器码是否存在数据库中
        if result not in [None, []]:
            # 判断该机器码是否过期
            if result[0]['expire_date'] > datetime.now(self.tz).strftime('%Y-%m-%d %H:%M:%S'):
                return {'code': 10000, 'msg': '机器码未过期', 'expireDate': result[0]['expire_date']}
            else:
                return {'code': 10011, 'msg': '机器码已过期', 'expireDate': result[0]['expire_date']}
        else:
            return {'code': 10010, 'msg': '机器码不存在'}

    # 机器码充值
    def recharge(self, machine_code: str, card_number: str, card_pass: str):
        # 查询机器码是否存在
        result_user = self.db_user.get(Query().machine_code == machine_code)
        if result_user in [None, []]:
            return {'code': 10030, 'msg': '机器码不存在'}
        # 查询充值卡信息
        result_card = self.db_card.get(Query().card_number == card_number and Query().card_pass == card_pass)
        if result_card not in [None, []]:
            if not result_card.get('used'):
                user_expire_date = result_user.get('expire_date')
                card_days = result_card.get('days')
                # print(user_expire_date, card_days)
                # 判断机器码授权日期是否过期
                if user_expire_date >= datetime.now(self.tz).strftime('%Y-%m-%d %H:%M:%S'):
                    new_date_time = datetime.strptime(user_expire_date, '%Y-%m-%d %H:%M:%S') + timedelta(days=card_days)
                    new_date_time = new_date_time.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    new_date_time = datetime.now(self.tz) + timedelta(days=card_days)
                    new_date_time = new_date_time.strftime('%Y-%m-%d %H:%M:%S')
                # print(new_date_time)
                # 修改机器码授权日期
                result_user_update = self.db_user.update({'expire_date': new_date_time}, Query().machine_code == machine_code)
                if len(result_user_update) == 1:
                    # 修改充值卡使用状态
                    # yapf: disable
                    result_card_update = self.db_card.update({'used': True, 'used_machine_code': result_user.get('machine_code'), 'used_time': datetime.now(self.tz).strftime('%Y-%m-%d %H:%M:%S')},
                                                             Query().card_number == card_number and Query().card_pass == card_pass)
                    # yapf: enable
                    if len(result_card_update) != 1:
                        # print('充值卡使用状态修改失败')
                        # 追加写入日志文件
                        with open('error.log', 'a') as f:
                            f.write(self.get_server_time() + '\t充值卡使用状态修改失败\t' + machine_code + '\t' + card_number + '\t' + card_pass + '\r\n')
                    return {'code': 10000, 'msg': '充值成功', 'expireDate': new_date_time}
                else:
                    return {'code': 10033, 'msg': '充值失败，请于管理员联系。'}
            else:
                return {'code': 10032, 'msg': '充值卡已使用'}
        else:
            return {'code': 10031, 'msg': '充值卡不存在'}

    # 充值卡生成
    def make_new_card(self, number: int, days: int):
        # 批量生成充值卡
        insert_result = self.db_card.insert_multiple({'card_number': self.new_card_number(), 'card_pass': self.random_str(8), 'days': days, 'used': False, 'used_machine_code': '', 'used_time': ''} for i in range(number))
        if insert_result not in [None, []]:
            print_result = []
            for i in insert_result:
                get_data = self.db_card.get(doc_id=i)
                print_result.append([get_data["card_number"], get_data["card_pass"], get_data["days"]])
                # print_result += f'{get_data["card_number"]}\t{get_data["card_pass"]}\t{get_data["days"]}\r\n'
            return {'code': 10000, 'msg': '充值卡生成成功', 'data': print_result}
        else:
            return {'code': 10020, 'msg': '充值卡生成失败'}

    # 获取充值卡列表(分页)
    def get_card(self, page: int, limit: int):
        # 查询充值卡列表
        result_card = self.db_card.all()
        # 逆序排列
        result_card.reverse()
        # 总条数
        count_data = len(result_card)
        # print(count_data)
        # 向上取整得到总页数
        all_page = math.ceil(len(result_card) / limit)
        # print(all_page)
        if result_card not in [None, []]:
            result_card = result_card[(page - 1) * limit:page * limit]
            result_card_list = []
            for i in result_card:
                result_card_list.append([i["card_number"], i["card_pass"], i["days"], str(i["used"]), i["used_machine_code"], i["used_time"]])
            return {'code': 10000, 'msg': '查询成功', 'count_data': count_data, 'page': page, 'all_page': all_page, 'data': result_card_list}
        else:
            return {'code': 10021, 'msg': '查询失败'}

    # 删除充值卡
    def delete_card(self, card_number: str):
        result_card = self.db_card.remove(Query().card_number == card_number)
        if len(result_card) == 1:
            return {'code': 10000, 'msg': '充值卡删除成功'}
        else:
            return {'code': 10022, 'msg': '充值卡删除失败'}

    # 充值卡查询
    def search_card(self, card_number: str):
        result_card = self.db_card.get(Query().card_number == card_number)
        if result_card not in [None, []]:
            return {'code': 10000, 'msg': '查询成功', 'data': [result_card["card_number"], result_card["card_pass"], result_card["days"], str(result_card["used"]), result_card["used_machine_code"], result_card["used_time"]]}
        else:
            return {'code': 10023, 'msg': '该充值卡不存在'}

    # 获取用户(机器码)列表(分页)
    def get_user(self, page: int, limit: int):
        # 查询用户列表
        result_user = self.db_user.all()
        # 逆序排列
        result_user.reverse()
        # 总条数
        count_data = len(result_user)
        # print(count_data)
        # 向上取整得到总页数
        all_page = math.ceil(len(result_user) / limit)
        # print(all_page)
        if result_user not in [None, []]:
            result_user = result_user[(page - 1) * limit:page * limit]
            result_user_list = []
            for i in result_user:
                result_user_list.append([i["machine_code"], i["expire_date"], i["reg_date"]])
            return {'code': 10000, 'msg': '查询成功', 'count_data': count_data, 'page': page, 'all_page': all_page, 'data': result_user_list}
        else:
            return {'code': 10022, 'msg': '查询失败'}

    # 修改用户(机器码)过期时间
    def update_user(self, machine_code: str, expire_date: str):
        result_user = self.db_user.update({'expire_date': expire_date}, Query().machine_code == machine_code)
        # print('返回结果:', result_user)
        if len(result_user) == 1:
            return {'code': 10000, 'msg': '修改成功'}
        else:
            return {'code': 10024, 'msg': '机器码过期时间修改失败'}

    # 删除用户(机器码)
    def delete_user(self, machine_code: str):
        result_user = self.db_user.remove(Query().machine_code == machine_code)
        if len(result_user) == 1:
            return {'code': 10000, 'msg': '用户删除成功'}
        else:
            return {'code': 10025, 'msg': '用户删除失败'}

    # 用户(机器码)查询
    def search_user(self, machine_code: str):
        result_user = self.db_user.get(Query().machine_code == machine_code)
        if result_user not in [None, []]:
            return {'code': 10000, 'msg': '查询成功', 'data': [result_user["machine_code"], result_user["expire_date"], result_user["reg_date"]]}
        else:
            return {'code': 10026, 'msg': '该用户不存在'}

    # 工具函数集
    def new_card_number(self):
        local_time = time.strftime('%Y%m%d', time.localtime(time.time()))
        card_number = local_time + self.random_str(5)
        return card_number

    def random_str(self, randomlength=8):
        result_str = ''
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        # chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        length = len(chars) - 1
        random = Random()
        for i in range(randomlength):
            result_str += chars[random.randint(0, length)]
        return result_str

    def get_server_time(self):
        return datetime.now(self.tz).strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    v = verification()
    # print(v.reg('123456789111111', '2021-12-31 13:29:59'))
    # for i in range(20):
    #     print(v.reg(v.random_str(16), '2021-12-31 13:29:59'))
    # print(v.login('123456789111111'))
    # print(v.make_new_card(100, 90))
    # print(v.recharge('223456789111111', '20220901BRDID', 'HGVSPQGE'))
    # print(v.get_card(1, 5))  # (1, 5)=[0, 5],(2, 5)=[5, 10]
    # print(v.delete_card('20220905ZQUCY'))
    # print(v.search_card('20220905NLHYL'))

    # print(v.get_user(1, 5))  # (1, 5)=[0, 5],(2, 5)=[5, 10]
    # print(v.update_user('123456789111111', '2021-12-31 13:29:59'))
    # print(v.delete_user('123456789111111'))
    # print(v.search_user('123456789111111'))
