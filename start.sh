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
#下面是自动拉取git库脚本，取消注释后在下次运行时更新git，之后被git库中的start.sh覆盖。
#{
#  set +e
#  # 拉取或更新代码
#  if [ -d ".git" ]; then
#      log "已有 Git 仓库，执行 fetch && reset"
#      git fetch origin "$GIT_BRANCH" >> "$LOGFILE" 2>&1
#      git reset --hard "origin/$GIT_BRANCH" >> "$LOGFILE" 2>&1
#      log "代码已更新到 origin/$GIT_BRANCH"
#  else
#      log "克隆仓库 $REPO_URL 到当前目录"
#      # 若已在 SCRIPT_DIR，但可能已有其他内容，建议确保空目录或无冲突
#      git clone --branch "$GIT_BRANCH" "$REPO_URL" . >> "$LOGFILE" 2>&1
#      log "克隆完成"
#  fi
#  set -e
#}
# 检查 env.txt
if [ ! -f "$ENV_FILE" ]; then
    log "错误：未找到 env.txt ($SCRIPT_DIR/$ENV_FILE)，退出"
    exit 1
fi

# 检查 data 目录
DATA_DIR="$SCRIPT_DIR/data"
if [ ! -d "$DATA_DIR" ]; then
    log "未找到 data 目录，创建：$DATA_DIR"
    mkdir -p "$DATA_DIR"
    # 可根据需要在此处初始化文件，如：touch "$DATA_DIR/file1.ext"
else
    log "找到 data 目录：$DATA_DIR"
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

# 运行容器并挂载 data 目录
log "开始运行容器 $IMAGE_NAME，挂载 data 目录: $DATA_DIR"
podman run --rm \
    --env-file "$ENV_FILE" \
    -v "$DATA_DIR":/app/data:Z \
    "$IMAGE_NAME" >> "$LOGFILE" 2>&1
RET=$?
if [ $RET -ne 0 ]; then
    log "容器运行失败，退出码 $RET"
    exit $RET
fi

log "======== 脚本执行完成 ========"
