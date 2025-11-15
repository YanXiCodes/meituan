import subprocess # 用于在后台运行其他程序的标准库
import os
import time
import sys

# --- 配置 ---
CONDA_ENV_NAME = "meituan"
WECHAT_BOT_CLIENT_PATH = "D:\\meituan\\ComWeChatBotClient"
NONEBOT_PROJECT_PATH = "D:\\meituan\\wechatbot\\wechat"

def run_in_conda_env(command, working_dir):
    """一个辅助函数，用于在指定的Conda环境中以后台模式运行命令"""
    # 构建完整的conda命令
    # 'call' 是为了确保conda的环境变量能被正确设置
    full_command = f'call conda activate {CONDA_ENV_NAME} && {command}'
    
    # 使用 subprocess.Popen 启动一个新进程
    # CREATE_NEW_CONSOLE 会为它创建一个新的、独立的黑窗口
    return subprocess.Popen(
        full_command,
        shell=True,
        cwd=working_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

def main():
    print("--- [启动器] 自动化一键启动脚本 ---")

    # 1. 启动 PC 微信 (这里假设您已经手动登录了)
    print("[*] 请确保您的PC微信已经登录...")
    time.sleep(3) # 留时间给用户确认

    # 2. 在后台启动“微信连接器” (ComWeChatBotClient)
    print("[*] 正在后台启动“微信连接器”...")
    client_process = run_in_conda_env(
        "python main.py",
        WECHAT_BOT_CLIENT_PATH
    )
    print("[✔] “微信连接器”进程已启动。")
    time.sleep(5) # 等待它完全初始化

    # 3. 在后台启动“机器人大脑” (NoneBot2 + Playwright)
    print("\n[*] 正在后台启动“机器人大脑”...")
    nonebot_process = run_in_conda_env(
        "nb run", # 注意，这里不能用 --reload，因为我们不是在调试
        NONEBOT_PROJECT_PATH
    )
    print("[✔] “机器人大脑”进程已启动。")
    print("\n" + "="*50)
    print("[🎉] 所有服务已启动！")
    print("     现在应该会自动弹出一个浏览器窗口，请在其中扫码登录美团。")
    print("     之后，您只需要保持【PC微信】、【自动弹出的浏览器】和【本启动器窗口】开启即可。")
    print("="*50)

    try:
        # 保持主启动器运行，并监控子进程
        # 如果我们关闭这个启动器，两个后台进程也会被自动关闭
        client_process.wait()
        nonebot_process.wait()
    except KeyboardInterrupt:
        print("\n[*] 收到关闭指令，正在关闭所有后台服务...")
        client_process.terminate()
        nonebot_process.terminate()
        print("[✔] 所有服务已关闭。")


if __name__ == "__main__":
    main()