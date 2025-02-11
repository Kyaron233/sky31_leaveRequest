# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 运行 Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]