# 使用官方 Python 运行时作为基础镜像，基于 Alpine Linux 以减小体积
FROM python:3.13-alpine

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_DISABLE_CONCURRENT_INDEXES=1

# 安装编译依赖（仅在构建期间需要）
RUN apk add --no-cache gcc musl-dev libffi-dev

# 复制项目依赖文件
COPY pyproject.toml requirements.txt ./

# 安装 uv 并使用它来安装项目依赖
RUN pip install uv && \
    uv pip install --system --no-cache-dir -r requirements.txt

# 复制项目源代码
COPY . .

# 创建非特权用户
RUN adduser -D mcp-user && \
    chown -R mcp-user:mcp-user /app
USER mcp-user

# 暴露端口
EXPOSE 8000

# 启动命令：以 HTTP 模式运行 MCP 服务
CMD ["python", "main.py"]