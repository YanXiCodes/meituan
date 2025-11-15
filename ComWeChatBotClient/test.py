import httpx
import json
import time

# ====================【 配置 】====================
CLIENT_API_URL = "http://127.0.0.1:8000"
# 输出文件的路径和名称
OUTPUT_FILE_PATH = "my_wechat_groups.txt" 
# ==================================================

def get_and_save_group_list():
    """通过API获取群聊列表，并保存到指定文件中"""
    
    action_name = "get_group_list"
    payload = {"action": action_name, "params": {}}
    
    print(f"[*] 准备向 {CLIENT_API_URL} 发送 '{action_name}' 请求...")

    try:
        response = httpx.post(CLIENT_API_URL, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") == "ok" and result.get("data"):
            groups = result["data"]
            
            print(f"[✔] 成功获取到 {len(groups)} 个群聊的信息。")
            
            # --- 核心：写入文件 ---
            try:
                # 使用 'w' (写入) 模式和 'utf-8' 编码打开文件
                # with open(...) 语句能确保文件在使用后被自动关闭
                with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as f:
                    # 写入一个标题和生成时间
                    f.write(f"微信群聊列表 (生成于: {time.strftime('%Y-%m-%d %H:%M:%S')})\n")
                    f.write(f"共找到 {len(groups)} 个群聊。\n")
                    f.write("="*60 + "\n\n")

                    # 遍历每一个群聊信息
                    for group in groups:
                        group_name = group.get("group_name", "未知群名")
                        group_id = group.get("group_id", "未知ID")
                        
                        # 向文件写入格式化的内容
                        f.write(f"群聊名称: {group_name}\n")
                        f.write(f"群聊ID:   {group_id}\n")
                        f.write("-" * 60 + "\n")
                
                print(f"[🎉] 所有群聊信息已成功保存到文件: {OUTPUT_FILE_PATH}")
                print("[*] 请打开这个文件，在里面查找您需要的 group_id。")

            except IOError as e:
                print(f"\n[❌] 写入文件时发生错误: {e}")

        else:
            print(f"\n[❌] API调用成功，但返回的状态不正确或数据为空。")
            print(f"    服务器原始响应: {result}")

    except httpx.HTTPStatusError as e:
        print(f"\n[❌] API服务器返回错误状态码: {e.response.status_code}")
    except httpx.RequestError as e:
        print(f"\n[❌] 请求失败，无法连接到 ComWeChatBotClient。")
        print(f"    错误信息: {e}")
        print("    请确认您的新微信账号已在 ComWeChatBotClient 上成功登录。")

if __name__ == "__main__":
    get_and_save_group_list()