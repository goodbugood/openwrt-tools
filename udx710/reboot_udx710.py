import requests
import json
from datetime import datetime, timedelta
import os

# 检查网络状态的函数
def check_network(current_time: str):
    try:
        response = requests.get("http://192.168.66.1:9527/api/sysinfo", timeout=5)
        data = response.json()
        # 检查 ambr.dl 是否为 0
        if data.get("ambr", {}).get("dl", 0) == 0:
            return False
        return True
    except Exception as e:
        print(f"{current_time} 检查网络状态失败: {e}")
        return False

# 获取系统时间的函数
def get_system_time(current_time: str):
    try:
        response = requests.get("http://192.168.66.1:51888/current_time", timeout=5)
        data = response.json()
        # 获取接口返回的时间字符串：{ "current_time": "2025-09-01 21:48:47" }
        current_time_str = data.get("current_time")
        # 解析时间字符串
        current_time1 = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
        return current_time1
    except Exception as e:
        print(f"{current_time} 获取系统时间失败: {e}")
        return None

# 设置系统重启时间的函数
def set_reboot_time(reboot_time, need_reboot=True):
    try:
        reboot_flag = 1 if need_reboot else 0
        # 格式化时间为 "HH,MM"
        time_str = f"{reboot_flag},{reboot_time.hour},{reboot_time.minute},1,1,1,1,1,1,1"
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(
            "http://192.168.66.1:51888/set_reboot_config",
            #"http://192.168.8.189:8080/set_reboot_config",
            data=time_str,
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            print(f"系统重启时间已设置为: {reboot_time.strftime('%H:%M')}")
        else:
            print(f"设置重启时间失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"设置重启时间时发生错误: {e}")

# 获取自动重启状态的函数
def close_auto_reboot_status(now: datetime) -> bool:
    try:
        response = requests.get("http://192.168.66.1:51888/reboot_config", timeout=5)
        #print(response.text)
        data = response.json()
        reboot_flag = data.get("auto_reboot_enabled", 1)
        if reboot_flag == 1:
            # 18:45
            reboot_hour = data.get("reboot_hour", now.hour)
            reboot_minute = data.get("reboot_minute", now.minute)
            reboot_time = datetime.combine(now.date(), datetime.strptime(f"{reboot_hour}:{reboot_minute}", "%H:%M").time())
            set_reboot_time(reboot_time, need_reboot=False)
    except Exception as e:
        print(f"检查自动重启状态失败: {e}")
        return False
    return True

# 主程序逻辑
def main():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    # 检查网络状态
    if not check_network(current_time):
        print(f"{current_time} 检测到网络异常，准备设置重启时间...")
        # 获取系统时间
        system_time = get_system_time(current_time)
        if system_time:
            # 加 1 分钟
            reboot_time = system_time + timedelta(minutes=1)
            # 设置重启时间
            set_reboot_time(reboot_time)
        else:
            print(f"{current_time} 无法获取系统时间，无法设置重启时间")
            print("开始重启 openwrt 系统")
            os.system('reboot')
    else:
        print(f"{current_time} 网络正常，无需设置重启时间")
        close_auto_reboot_status(now)

if __name__ == "__main__":
    main()
