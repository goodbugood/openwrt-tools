import requests
import json
from datetime import datetime, timedelta

# 检查网络状态的函数
def check_network():
    try:
        response = requests.get("http://192.168.66.1:9527/api/sysinfo", timeout=5)
        data = response.json()
        # 检查 ambr.dl 是否为 0
        if data.get("ambr", {}).get("dl", 0) == 0:
            return False
        return True
    except Exception as e:
        print(f"检查网络状态失败: {e}")
        return False

# 获取系统时间的函数
def get_system_time():
    try:
        response = requests.get("http://192.168.66.1:51888/current_time", timeout=5)
        data = response.json()
        current_time_str = data.get("current_time")
        # 解析时间字符串
        current_time = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
        return current_time
    except Exception as e:
        print(f"获取系统时间失败: {e}")
        return None

# 设置系统重启时间的函数
def set_reboot_time(reboot_time):
    try:
        # 格式化时间为 "HH,MM"
        time_str = f"1,{reboot_time.hour},{reboot_time.minute},1,1,1,1,1,1,1"
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(
            "http://192.168.66.1:51888/set_reboot_config",
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

# 主程序逻辑
def main():
    # 检查网络状态
    if not check_network():
        print("检测到网络异常，准备设置重启时间...")
        # 获取系统时间
        system_time = get_system_time()
        if system_time:
            # 加 1 分钟
            reboot_time = system_time + timedelta(minutes=1)
            # 设置重启时间
            set_reboot_time(reboot_time)
        else:
            print("无法获取系统时间，无法设置重启时间")
    else:
        print("网络正常，无需设置重启时间")

if __name__ == "__main__":
    main()
