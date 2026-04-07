#!/bin/sh

# 等待60秒，确保系统启动完成
sleep 60

# ===================== 配置项 =====================
CHECK_INTERVAL=300       # 5分钟 = 300秒
API_URL="http://192.168.66.1/api/qos"
PING_IP="192.168.66.2"
REBOOT_CMD="reboot"      # 重启命令
LOG_FILE="/home/root/ttyd/qos_monitor.log"
PID_FILE="/var/run/qos_monitor.pid"
# =================================================

# 日志输出
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# ===================== 防重复执行（兼容 BusyBox）=====================
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    # BusyBox 专用进程判断：ps | grep 匹配PID
    ps | grep -v grep | grep -q "$PID"
    if [ $? -eq 0 ]; then
        # 进程存在，直接退出
        exit 0
    else
        # 进程不存在，删除旧PID文件
        rm -f "$PID_FILE"
    fi
fi
# 写入当前进程PID
echo $$ > "$PID_FILE"

# ===================== 主循环 =====================
log "==== 监控脚本启动，每5分钟检查一次 ===="

while true; do
    log "---------------- 开始检查 ----------------"

    # 1. 请求接口（BusyBox curl 兼容写法）
    log "请求接口：$API_URL"
    response=$(curl -s --connect-timeout 10 "$API_URL" 2>/dev/null)

    if [ -z "$response" ]; then
        log "接口请求失败，执行重启"
        $REBOOT_CMD
        sleep $CHECK_INTERVAL
        continue
    fi

    # 2. 截取第 50 个字符（无jq，纯shell实现）
    char50=$(echo -n "$response" | dd bs=1 skip=49 count=1 2>/dev/null)
    log "接口返回第50个字符：[$char50]"

    # 3. 字符 = 0 → 重启
    if [ "$char50" = "0" ]; then
        log "第50字符为0，触发重启"
        $REBOOT_CMD
        sleep $CHECK_INTERVAL
        continue
    fi

    # 4. 字符≠0 → ping 检测（BusyBox ping 兼容）
    log "第50字符不是0，开始ping：$PING_IP"
    ping -c 1 -W 2 "$PING_IP" > /dev/null 2>&1

    if [ $? -ne 0 ]; then
        log "ping失败，触发重启"
        $REBOOT_CMD
    else
        log "检查完成：一切正常"
    fi

    # 等待5分钟
    sleep $CHECK_INTERVAL
done
