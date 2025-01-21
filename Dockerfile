# 使用官方的 Python 镜像作为基础镜像
FROM python:3.9-slim

RUN apt-get update
RUN apt-get install -y python3
# 设置工作目录
WORKDIR /app

# 将当前目录下的所有文件复制到容器的 /app 目录
COPY . /app

# 安装项目依赖
RUN pip install -r requirements.txt

# 运行应用程序
CMD python3 run.py