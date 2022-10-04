<h2 align="center">极简网络验证Python3版</h2>
<p>一款轻量级的网络验证服务端应用程序，基于JSON改造的数据库，免去部署MySQL等数据库的烦恼，实现快速部署上线生产的目的。</p>
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

## 后续优化准备规划`删除线代表已完成`

- ~~验证相关类接口加密返回数据~~
- ~~登陆验证接口安全认证~~
- ~~后台管理在增加一些常用功能~~
- ~~增加使用DEMO~~

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
##### `2022-09-28`更新增加`接口签名认证`，POST需带上`header`协议头并增加`2`个参数，详细参考/demo/python3/demo.py代码。
```
curl --request POST \
  --url http://domain:8081/login \
  --header 'sign: 7272d8673cc676d594cda7aea94ca84f' \
  --header 'timestamp: 1664210885' \
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
[http://domain:8081/admin/login](http://domain:8081/admin/login)

## 开发环境

1. macOS `12.6` / Ubuntu Desktop `22.04`
2. Python `3.9.14`
3. VS Code `1.71.2` / PyCharm `2022.2.2`
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
├── Dockerfile                  docker Dockerfile文件
├── aes_model.py                AEC加解密类
└── verification_model.py       网络验证核心库类
```

## 安装&运行

### 本地克隆运行方式(Python≥3.7)
- clone the repo
- cd into the repo directory
- mkdir venv
- virtualenv venv
- source venv/bin/activate
- pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
- python3 app.py

### docker运行方式
```
git clone https://github.com/jiayouzl/python_web_auth.git
# docker怎么安装？百度或谷歌吧~

cd python_web_auth

# 编译镜像
docker build -t wlyz:v1 .

# 运行镜像(~/python3/docker_volumes/wlyz_data改为你自己的路径)
# 1.把[database]目录下的[db.json]文件先拷贝至[~/python3/docker_volumes/wlyz_data]目录下。
# 2.把根目录下的[.env]文件先拷贝至[~/python3/docker_volumes]目录下。
docker run --name wlyz -p 8081:8081 -itd -v ~/python3/docker_volumes/wlyz_data:/app/database:rw -v ~/python3/docker_volumes/.env:/app/.env:rw --restart=always wlyz:v1

# 测试访问(这个内网IP是我自己的，可能与你的不同，自行查找自己的内网IP地址)
http://192.168.5.100:8081
```

## 更新记录
`2022-10-02`
1. 增加后台充值卡批量复制导出功能。
<img src="https://myimages.25531.com/20221002/iShot_2022-10-02_15.11.28.png" style="zoom:20%;" />

`2022-09-29`
1. 增加认证接口签名加密认证。
2. 增加认证接口结果加密返回，杜绝结果本地重写规则破解方式。

`2022-09-25`
1. 增加Python3的DEMO。`/demo/python3/demo.py`
2. 其他语言DEMO后续新增，也可参考`curl`样板进行自行修改。

`2022-09-22`
1. 增加`Dockerfile`，我都写好了，直接编译镜像即能以`docker`方式运行。

## 交流群组
### 进QQ群验证问答
```
问：这是什么？
答：网络验证
```

<a target="_blank" href="https://qm.qq.com/cgi-bin/qm/qr?k=IyIaQmjYElaHExKSOzqf4gqY7YhKmDwk&jump_from=webapi"><img border="0" src="https://pub.idqqimg.com/wpa/images/group.png" alt="Python3网络验证交流群" title="Python3网络验证交流群"></a>

![QQ群二维码](/templates/static/images/qrcode-302.png "Python3网络验证交流群")

## License

MIT
