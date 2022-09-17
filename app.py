# -*- coding: UTF-8 -*-
import os
import sys
from datetime import datetime, timedelta, timezone
from distutils.util import strtobool
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from sanic import Sanic
from sanic.response import Request, html, json, redirect, text
from sanic_ext import Extend, render
from sanic_session import InMemorySessionInterface, Session

from verification_model import verification

app = Sanic('MyApp')
app.static('/static', './templates/static', name='get_static')
# app.url_for('static', name='get_static', filename='jquery-3.6.1.min.js')
session = Session(app, interface=InMemorySessionInterface())
# 加载env配置环境变量
load_dotenv(find_dotenv(str(Path.cwd().joinpath('.env'))))
app.config['HOST'] = os.getenv('HOST')
app.config['PORT'] = os.getenv('PORT')
app.config['DEBUG'] = os.getenv('DEBUG')
app.config['AUTO_RELOAD'] = os.getenv('AUTO_RELOAD')
# CORS跨域资源共享
app.config['CORS_ORIGINS'] = '*'
Extend(app)
# 初始化验证模型类
verify = verification()


# 创建请求中间件
@app.middleware('request')
async def get_request_middleware(request):
    # 截取到login请求进行是否开启网络验证判断,如果关闭则直接通过.
    if request.path.split('/')[1] == 'login':
        if not strtobool(os.getenv('NETWORK_AUTH')):
            return json({'code': 10000, 'msg': '未开启网络验证直接通过验证', 'expireDate': '2099-12-31 23:59:59'})
    # 截取到admin分类请求的路径进行权限认证
    if len(request.path.split('/')) == 3:  #防止IndexError: list index out of range报错
        if request.path.split('/')[1] == 'admin' and request.path.split('/')[2] != 'login':
            if not strtobool(os.getenv('DEBUG')):  # 如果DEBUG模式等于True直接跳过登录验证
                # print('get session:', request.ctx.session.get('admin_login_status'))
                if not request.ctx.session.get('admin_login_status'):
                    return redirect('/admin/login')  # return json({'code': 10030, 'msg': '管理员未登录'})


# http://127.0.0.1:8081
@app.get('/')
async def index(request: Request):
    return html('欢迎使用极简网络验证Python3版</br>作者：@jiayouzl</br>Github：<a href="https://github.com/jiayouzl/python_web_auth" target="_blank">点击访问</a></br>服务器时间：' + verify.get_server_time() + '</br>服务器Python版本：' + sys.version)


'''
curl --request POST \
  --url http://127.0.0.1:8081/reg \
  --data '{
	"machineCode": "12345abcde"
}'
'''


@app.post('/reg')
async def reg(request: Request):
    parametes = request.json
    machineCode = parametes['machineCode']
    if len(machineCode) > 32:
        return json({'code': 10012, 'msg': '非法的机器码长度'})
    # 取现行时间(2022-09-10 12:48:08)
    expire_date_time = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
    if strtobool(os.getenv('IS_TRIAL')):
        # 增加*分钟
        expire_date_time = (datetime.now(timezone(timedelta(hours=8))) + timedelta(minutes=int(os.getenv('TRIAL_TIME')))).strftime('%Y-%m-%d %H:%M:%S')
        # expire_date_time = datetime.strptime(expire_date_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=int(os.getenv('TRIAL_TIME')))
    result = verify.reg(machineCode, str(expire_date_time))
    return json(result)


'''
curl --request POST \
  --url http://127.0.0.1:8081/login \
  --data '{
	"machineCode": "12345abcde"
}'
'''


@app.post('/login')
async def login(request: Request):
    parametes = request.json
    result = verify.login(parametes['machineCode'])
    return json(result)


'''
curl --request POST \
  --url http://127.0.0.1:8081/recharge \
  --data '{
    "machineCode": "12345abcde",
    "card_number": "20220915RWLLG",
    "card_password": "OGPVQZSV"
}'
'''


@app.post('/recharge')
async def recharge(request: Request):
    parametes = request.json
    result = verify.recharge(parametes['machineCode'], parametes['card_number'], parametes['card_password'])
    return json(result)


# http://127.0.0.1:8081/admin/login
# http://127.0.0.1:8081/admin/login?user=admin&pass=admin888
@app.get('/admin/login')
async def admin_login(request: Request):
    # print(request.args)
    if request.args == {}:
        return await render('login.html', status=200)
    # print(request.args.get('user'))
    # print(request.args.get('pass'))
    else:
        if request.args.get('user') == os.getenv('ADMIN_USER') and request.args.get('pass') == os.getenv('ADMIN_PASS'):
            # 写入session
            request.ctx.session['admin_login_status'] = True
            return redirect('/admin/user_info')
        else:
            return html('管理员账号或密码错误</br><a href=# onclick="javascript:history.back(-1);">返回上一页</a>')


@app.get('/admin/logout')
async def admin_logout(request: Request):
    # 清除session
    request.ctx.session.clear()
    return redirect('/admin/login')


# 充值卡管理
# http://127.0.0.1:8081/admin/card_info?page=1
@app.get('/admin/card_info/')
@app.ext.template('card_info.html')
async def card_info(request: Request):
    page = 1 if (request.args.get('page') is None) else int(request.args.get('page'))
    card_info = verify.get_card(page, 20)
    # print(card_info)
    home_page = 1
    previous_page = 1 if (page - 1 == 0) else page - 1
    next_page = card_info['all_page'] if (page + 1 > card_info['all_page']) else page + 1
    end_page = card_info['all_page']
    # print([home_page, previous_page, next_page, end_page])
    return {'title': '充值卡管理', 'card_data': card_info['data'], 'page': [home_page, previous_page, next_page, end_page]}
    # return await render(context={'test': 'aaaa1', 'card_data': [dict(name='Tom', age=22), dict(name='Jerry', age=20)]}, status=200)


# http://127.0.0.1:8081/admin/card_info/delete?key=20220902DHOPD
@app.get('/admin/card_info/delete')
async def card_info_delete(request: Request):
    key = request.args.get('key')
    # print(key)
    result = verify.delete_card(key)
    return json(result)


# http://127.0.0.1:8081/admin/card_info/search?key=20220902DHOPD
@app.get('/admin/card_info/search')
async def card_info_search(request: Request):
    key = request.args.get('key')
    result = verify.search_card(key)
    return json(result)


@app.post('/admin/card_info/make')
async def make_card(request: Request):
    parametes = request.json
    # print(parametes)
    result = verify.make_new_card(int(parametes['number']), int(parametes['days']))
    return json(result)


# 用户管理
# http://127.0.0.1:8081/admin/user_info?page=1
@app.get('/admin/user_info/')
@app.ext.template('user_info.html')
async def user_info(request: Request):
    page = 1 if (request.args.get('page') is None) else int(request.args.get('page'))
    user_info = verify.get_user(page, 20)
    # print(user_info)
    home_page = 1
    previous_page = 1 if (page - 1 == 0) else page - 1
    next_page = user_info['all_page'] if (page + 1 > user_info['all_page']) else page + 1
    end_page = user_info['all_page']
    # print([home_page, previous_page, next_page, end_page])
    return {'title': '用户管理', 'user_data': user_info['data'], 'page': [home_page, previous_page, next_page, end_page]}


# 修改用户过期时间
@app.post('/admin/user_info/update')
async def user_update(request: Request):
    parametes = request.json
    # print(parametes)
    result = verify.update_user(parametes['machine_code'], parametes['expire_date'])
    return json(result)


# 删除用户
# http://127.0.0.1:8081/admin/user_info/delete?key=223456789111111
@app.get('/admin/user_info/delete')
async def user_info_delete(request: Request):
    key = request.args.get('key')
    # print(key)
    result = verify.delete_user(key)
    return json(result)


# 查询用户
# http://127.0.0.1:8081/admin/user_info/search?key=123456789111111
@app.get('/admin/user_info/search')
async def user_info_search(request: Request):
    key = request.args.get('key')
    result = verify.search_user(key)
    return json(result)


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=int(app.config['PORT']), debug=strtobool(app.config['DEBUG']), auto_reload=strtobool(app.config['AUTO_RELOAD']), access_log=False, workers=1)
