#!/usr/bin/env bash
set -e

# 获取脚本所在目录，支持被软链接调用
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 配置区（均为相对或基于脚本目录的文件名）
REPO_URL="https://github.com/nhirsama/ZFGetMessage"
GIT_BRANCH="main"

ENV_FILE="env.txt"          # 位于脚本同一目录下
LOGFILE="run.log"           # 日志文件位于脚本目录
IMAGE_NAME="zfgetmessage:latest"

# 记录日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOGFILE"
}

log "======== 脚本开始执行，工作目录: $SCRIPT_DIR ========"

# 拉取或更新代码
if [ -d ".git" ]; then
    log "已有 Git 仓库，执行 fetch && reset"
    git fetch origin "$GIT_BRANCH" >> "$LOGFILE" 2>&1
    git reset --hard "origin/$GIT_BRANCH" >> "$LOGFILE" 2>&1
    log "代码已更新到 origin/$GIT_BRANCH"
else
    log "克隆仓库 $REPO_URL 到当前目录"
    # 若已在 SCRIPT_DIR，但可能已有其他内容，建议确保空目录或无冲突
    git clone --branch "$GIT_BRANCH" "$REPO_URL" . >> "$LOGFILE" 2>&1
    log "克隆完成"
fi

# 检查 env.txt
if [ ! -f "$ENV_FILE" ]; then
    log "错误：未找到 env.txt ($SCRIPT_DIR/$ENV_FILE)，退出"
    exit 1
fi

# 解析 env.txt 构建 build-arg 数组
BUILD_ARGS=()
while IFS= read -r line || [ -n "$line" ]; do
    # 去除前后空白
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    # 跳过空行或注释
    if [[ -z "$line" || "${line:0:1}" == "#" ]]; then
        continue
    fi
    if [[ "$line" != *=* ]]; then
        log "警告：env.txt 中行 '$line' 格式不合法，跳过"
        continue
    fi
    KEY="${line%%=*}"
    VALUE="${line#*=}"
    BUILD_ARGS+=(--build-arg "$KEY=$VALUE")
done < "$ENV_FILE"

# 构建镜像
log "开始构建镜像 $IMAGE_NAME，build-args: ${BUILD_ARGS[*]}"
# 如需网络选项，可在调用时加 --network=host
podman build "${BUILD_ARGS[@]}" -t "$IMAGE_NAME" . >> "$LOGFILE" 2>&1
log "镜像构建完成"

# 运行容器
log "开始运行容器 $IMAGE_NAME"
# 使用 --env-file 传入 env.txt
podman run --rm --env-file "$ENV_FILE" "$IMAGE_NAME" >> "$LOGFILE" 2>&1
log "容器运行结束"

log "======== 脚本执行完成 ========"
