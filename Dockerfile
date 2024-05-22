# 使用官方Python基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到工作目录
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露应用运行的端口
EXPOSE 5001

# 设置环境变量以确保Python输出直接进入控制台
ENV PYTHONUNBUFFERED=1

# 运行Flask应用
CMD ["python", "app.py"]