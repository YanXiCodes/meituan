import asyncio
import json
import time
from playwright.async_api import async_playwright
from nonebot import on_message, on_command, get_driver, get_bot
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v12 import Bot, MessageEvent, PrivateMessageEvent, MessageSegment
from nonebot.log import logger
import random
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v12 import Message

LOGIN_URL = "https://e.dianping.com/app/merchant-platform/63f74389b8cd474?iUrl=Ly9lLmRpYW5waW5nLmNvbS92Zy1wYy1wbGF0Zm9ybS1jdXN0b21lci1jZW50ZXIvaW5kZXguaHRtbA"
GROUP_ID = "56504189798@chatroom"
MONITOR_ENABLED = False

last_heartbeat_time = time.time()
is_cooling_down = False
playwright_browser = None

ADMIN_USER_IDS = {"wxid_u9377ranh6rz22", "wxid_h8l54q5wx7s122"}

# ====== 新增：可调速率（默认值）======
HUMAN_DELAY_MIN = 0.3   # 秒
HUMAN_DELAY_MAX = 0.3   # 秒
COOLDOWN_SECONDS = 5.0  # 秒


async def is_admin(event: PrivateMessageEvent) -> bool:
    return event.get_user_id() in ADMIN_USER_IDS

# -------------------------------------------------------------------------

start_cmd = on_command("开", rule=is_admin, priority=1, block=True)
@start_cmd.handle()
async def handle_start_monitor():
    global MONITOR_ENABLED
    if not MONITOR_ENABLED:
        MONITOR_ENABLED = True
        await start_cmd.finish("嗷嗷，哦晓迪咯🚀")
    else:
        await start_cmd.finish("嗷嗷，哦晓迪咯🚀")

stop_cmd = on_command("关", rule=is_admin, priority=1, block=True)
@stop_cmd.handle()
async def handle_stop_monitor():
    global MONITOR_ENABLED
    if MONITOR_ENABLED:
        MONITOR_ENABLED = False
        await stop_cmd.finish("嗷嗷哦呗抢单了哦💤")
    else:
        await stop_cmd.finish("嗷嗷哦呗抢单了哦💤")

simulate_cmd = on_command("模拟触发", rule=is_admin, priority=1, block=True)
@simulate_cmd.handle()
async def handle_simulate_trigger():
    if not MONITOR_ENABLED:
        await simulate_cmd.finish("管理员，监控当前已暂停，无法模拟。请先“开启听单”。")
        return

    logger.info("="*20 + " [🕹️] 收到管理员“模拟触发”指令 " + "="*20)
    fake_new_lead_message = {
      "contentSize": 748, "v": 1, "c": 2,
      "d": "{\"command\":7,\"data\":\"{\\\"message\\\":\\\"{\\\\\\\"templateId\\\\\\\":\\\\\\\"116\\\\\\\"}\\\"}\"}"
    }
    await simulate_cmd.send("正在模拟新客户通知，请观察...")
    await process_new_customer_lead(fake_new_lead_message)
    await simulate_cmd.finish("模拟结束。")

# ====== 新增：速率 / 状态（极简 & 不再误抓 FinishedException）======

rate_cmd = on_command("速率", rule=is_admin, priority=1, block=True)
@rate_cmd.handle()
async def handle_rate(arg: Message = CommandArg()):
    global HUMAN_DELAY_MIN, HUMAN_DELAY_MAX, COOLDOWN_SECONDS
    text = arg.extract_plain_text().strip()
    if not text:
        await rate_cmd.finish("用法：速率 <延迟区间或单值> [冷却秒数]\n例：速率 0.4-0.8 5")
        return

    parts = text.split()
    delay_str = parts[0]
    cooldown_str = parts[1] if len(parts) > 1 else None

    # 只把“解析”放进 try，finish 不在 try 内
    try:
        if "-" in delay_str:
            a, b = delay_str.split("-", 1)
            a, b = float(a), float(b)
            if a > b:
                a, b = b, a
            HUMAN_DELAY_MIN, HUMAN_DELAY_MAX = a, b
        else:
            v = float(delay_str)
            HUMAN_DELAY_MIN = HUMAN_DELAY_MAX = v

        if cooldown_str is not None:
            COOLDOWN_SECONDS = float(cooldown_str)
    except Exception as e:
        await rate_cmd.finish("参数解析失败。示例：速率 0.4-0.8 5  或  速率 0.6 3")

    await rate_cmd.finish(
        f"OK ✅ 延迟={HUMAN_DELAY_MIN:.2f}~{HUMAN_DELAY_MAX:.2f}s 冷却={COOLDOWN_SECONDS:.2f}s"
    )

status_cmd = on_command("状态", rule=is_admin, priority=1, block=True)
@status_cmd.handle()
async def handle_status():
    await status_cmd.finish(
        f"监听：{'开' if MONITOR_ENABLED else '关'}｜延迟：{HUMAN_DELAY_MIN:.2f}~{HUMAN_DELAY_MAX:.2f}s｜冷却：{COOLDOWN_SECONDS:.2f}s"
    )

# -------------------------------------------------------------------------

async def process_new_customer_lead(event_data: dict):
    global is_cooling_down
    if not MONITOR_ENABLED: return

    try:
        inner_data = json.loads(event_data.get('d', '{}'))
        is_new_lead = False
        if inner_data.get("command") == 7:
            data_str = inner_data.get("data", "{}")
            if isinstance(data_str, str):
                data = json.loads(data_str)
                message_str = data.get("message", "{}")
                if isinstance(message_str, str):
                    message = json.loads(message_str)
                    if message.get("templateId") == "116":
                        is_new_lead = True

        if is_new_lead and not is_cooling_down:
            logger.success("[🎯] 精准命中新客户通知！")
            # === 改动点：使用可调延迟 ===
            human_like_delay = random.uniform(HUMAN_DELAY_MIN, HUMAN_DELAY_MAX)
            logger.info(f"[*] 模拟人类反应中... 延迟 {human_like_delay:.2f} 秒")
            await asyncio.sleep(human_like_delay)

            logger.info("[*] 反应结束！执行抢单！")
            try:
                bot = get_bot()
                await bot.send_message(
                    detail_type="group",
                    group_id=GROUP_ID,
                    message=MessageSegment.text("1")
                )
                logger.info(f"[✔] 已在群 {GROUP_ID} 中发送“1”！")
            except Exception as e:
                logger.error(f"[❌] 发送微信消息失败: {e}")

            is_cooling_down = True
            # === 改动点：使用可调冷却 ===
            await asyncio.sleep(COOLDOWN_SECONDS)
            is_cooling_down = False

    except Exception as e:
        logger.error(f"[❌] 处理Pike消息时发生错误: {e}")

# --- Playwright 后台监控主函数 ---
async def monitor_main_task():
    global playwright_browser, last_heartbeat_time
    logger.info("--- [抢单模块] 正在启动 Playwright ... ---")

    p = await async_playwright().start()
    playwright_browser = await p.chromium.launch(headless=False)
    context = await playwright_browser.new_context()
    page = await context.new_page()

    def handle_websocket(ws):
        if "bizId=msg_pike_client_dz" in ws.url:
            logger.success(f"[抢单模块] 已锁定业务通道: {ws.url}")
            ws.on("framereceived", handle_frame_received)

    async def handle_frame_received(payload_str: str):
        global last_heartbeat_time
        if payload_str == '3':
            last_heartbeat_time = time.time()
            return
        if isinstance(payload_str, str) and payload_str.startswith('42["pike"'):
            try:
                data_list = json.loads(payload_str[2:])
                await process_new_customer_lead(data_list[1])
            except Exception: pass

    page.on("websocket", handle_websocket)

    logger.info("--- [抢单模块] 请在弹出的浏览器窗口中完成扫码登录 ---")
    await page.goto(LOGIN_URL)
    await page.wait_for_function("() => !location.href.includes('login')", timeout=120000)
    logger.success("[抢单模块] 登录成功！进入持续监控状态。")
    logger.warning("[抢单模块] 请勿关闭浏览器，可以最小化。")
    last_heartbeat_time = time.time()

    async def anti_sleep_task():
        while True:
            await asyncio.sleep(45)
            try:
                await page.mouse.move(0, 0)
                # 检查心跳
                if time.time() - last_heartbeat_time > 60:
                    logger.warning(f"超过60秒未收到心跳，连接可能已断开！")
                else:
                    logger.info(f"[❤] 连接正常，上次心跳在 {int(time.time() - last_heartbeat_time)} 秒前。")
            except Exception:
                logger.error("[抢单模块] 浏览器页面似乎已关闭！监控任务停止。")
                break

    await anti_sleep_task()

# --- 注册到 NoneBot 生命周期 ---
driver = get_driver()
@driver.on_startup
async def start_monitor():
    asyncio.create_task(monitor_main_task())

@driver.on_shutdown
async def stop_monitor():
    if playwright_browser:
        await playwright_browser.close()
