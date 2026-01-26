#!/usr/bin/env bash
set -e

# 获取脚本所在目录，支持被软链接调用
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 配置区
ENV_FILE="env.txt"
LOGFILE="run.log"

# 记录日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOGFILE"
}

log "======== 脚本开始执行，工作目录: $SCRIPT_DIR ========"

# 自动更新逻辑
{
    set +e
    GIT_BRANCH="main"
    UPDATE_LOG="update.log"

    log "检查更新..."
    git fetch origin "$GIT_BRANCH" >> "$UPDATE_LOG" 2>&1
    git merge -X ours origin/"$GIT_BRANCH" -m "Auto-merge" >> "$UPDATE_LOG" 2>&1
    log "更新检查完成"
    set -e
}

# 检查环境文件
if [ ! -f "$ENV_FILE" ]; then
    log "错误：未找到 $ENV_FILE，请先创建并配置该文件"
    echo "错误：未找到 $ENV_FILE"
    exit 1
fi

# 确保 data 目录存在
mkdir -p "$SCRIPT_DIR/data"

# 使用 Docker Compose 运行
log "开始构建并启动 Docker Compose 服务..."

# 后台运行并构建
# 注意：容器日志现在由 Docker 管理，请使用 'docker compose logs -f' 查看
docker compose up -d --build >> "$LOGFILE" 2>&1
RET=$?

if [ $RET -ne 0 ]; then
    log "Docker Compose 启动失败，退出码 $RET"
    exit $RET
fi

log "服务已启动/更新。使用 'docker compose logs -f' 查看实时日志。"
log "======== 脚本执行结束 ========"
