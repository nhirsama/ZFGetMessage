# 使用官方 slim-image
FROM python:3.9-slim

# 升级 pip
RUN pip install --upgrade pip

# 设置工作目录
WORKDIR /app

# 复制依赖声明并安装，再复制代码——这样能更好利用 Docker 缓存
COPY requirements.txt .
# 使用阿里源，加快下载速度
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 设置环境变量，确保 Python 输出不被缓存
ENV PYTHONUNBUFFERED=1

# 复制源代码
COPY . .

# 指定容器启动命令
CMD ["python", "main.py"]
