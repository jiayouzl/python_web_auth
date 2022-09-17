<h2 align="center">极简网络验证Python3版</h2>
<p align="center">一款轻量级的网络验证服务端应用程序，基于JSON改造的数据库，免去部署MySQL等数据库的烦恼，实现快速部署上线生产的目的。</p>
<h4 align="center">后台管理界面预览</h4>
<p align="center">
<img src="https://myimages.25531.com/20220915/iShot_2022-09-15_13.22.42.png" width="50%" height="50%" alt="Empty interface" />
<img src="https://myimages.25531.com/20220915/iShot_2022-09-15_13.23.11.png" width="50%" height="50%" alt="Empty interface" />
</p>

## 简介

之前网上乱转看到一篇文章在介绍Sanic这款Python3的Web应用框架，看着介绍挺不错，就有了大家现在看到的这款我用来练手作品。

如要直接外网访问将.env配置文件中HOST改为`0.0.0.0`利用Sanic自带服务端用于生产环境(Sanic框架官方允许这样做)，但是不建议这样做，强烈建议使用Nginx反向代理。

这款网络验证要优化的地方还是很多的，后续我会对该项目慢慢进行升级优化。

使用前务必阅读.env配置文件中的相关参数说明。

## 后续优化准备规划

- 验证相关类接口加密返回数据
- 登陆验证接口安全认证
- 后台管理在增加一些常用功能
- 常用语言的DEMO

## 接口文档

#### 机器码注册
```
curl --request POST \
  --url http://domain:8081/reg \
  --data '{
	"machineCode": "12345abcde"
}'
```

#### 机器码验证
```
curl --request POST \
  --url http://domain:8081/login \
  --data '{
	"machineCode": "12345abcde"
}'
```

#### 机器码充值
```
curl --request POST \
  --url http://domain:8081/recharge \
  --data '{
    "machineCode": "12345abcde",
    "card_number": "20220915RWLLG",
    "card_password": "OGPVQZSV"
}'
```

#### 后台管理(默认账号：`admin` 默认密码：`admin888`)
```
http://domain:8081/admin/login
```

## 开发环境

1. macOS `12.6` / Ubuntu Desktop `22.04`
2. Python `3.9.14`
3. VS Code `1.71.2` / PyCharm `2022.2.1`
4. Sanic `22.6.2`

## 文件说明
```
├── .env                        应用配置文件
├── app.py                      Web路由相关
├── db.json                     JSON数据库文件
├── error.log                   错误日志
├── requirements.txt            依赖组件库
├── templates                   静态模版目录
│   ├── base.html               后台管理UI头文件
│   ├── card_info.html          充值卡管理
│   ├── login.html              管路员登录
│   ├── static                  第三方js库目录
│   └── user_info.html          机器码管理
└── verification_model.py       网络验证核心库类
```

## 安装(Python≥3.7)
- clone the repo
- cd into the repo directory
- pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
- python3 app.py

## 交流群组
<a target="_blank" href="https://qm.qq.com/cgi-bin/qm/qr?k=IyIaQmjYElaHExKSOzqf4gqY7YhKmDwk&jump_from=webapi"><img border="0" src="https://pub.idqqimg.com/wpa/images/group.png" alt="Python3网络验证交流群" title="Python3网络验证交流群"></a>

![QQ群二维码](/templates/static/images/qrcode-302.png "Python3网络验证交流群")

## License

MIT