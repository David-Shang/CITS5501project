# 使用官方的Python镜像作为基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到Docker容器中的/app目录
COPY . /app

# 安装依赖项，如果你有 requirements.txt 文件
# RUN pip install --no-cache-dir -r requirements.txt

# 运行Python文件
CMD ["python", "ExtraQuestion.py"]
