FROM python:3.9.14-slim-buster

LABEL maintainer="jiayouzl@vip.qq.com"

RUN mkdir /app
COPY . /app/

RUN cd /app \
    && python3.9 -m pip install --upgrade pip -i https://pypi.douban.com/simple/\
    && pip3.9 install --no-cache-dir -r requirements.txt --extra-index-url https://pypi.douban.com/simple/ \
    && rm -rf /tmp/* && rm -rf /root/.cache/* \
    && sed -i 's#http://deb.debian.org#http://mirrors.aliyun.com/#g' /etc/apt/sources.list\
    && apt-get --allow-releaseinfo-change update && apt install libgl1-mesa-glx libglib2.0-0 -y

WORKDIR /app

CMD ["python3.9", "app.py", "--port", "8081"]