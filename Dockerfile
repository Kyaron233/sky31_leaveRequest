# 使用官方 Python 镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt .
RUN rm -f /etc/apt/sources.list.d/debian.sources
COPY debian.sources /etc/apt/sources.list.d/
RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    gcc
RUN apt-get update && apt-get install -y libmariadb-dev && pip3 install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV FLASK_APP=app/app.py
ENV FLASK_ENV=production

# 配置 Gunicorn 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]