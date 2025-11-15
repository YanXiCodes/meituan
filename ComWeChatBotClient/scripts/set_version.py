from pymem import Pymem
import struct
import time

old_value = 0x63090c2d
new_value = 0x6400061a


def work_time(func):
    print("Working...")
    start_time = time.time()
    func()
    print(f"Time: {time.time() - start_time}")


def fix_version(pm: Pymem):
    WeChatWindll_base = 0
    WeChatWindll_size = 0
    for m in list(pm.list_modules()):
        path: str = m.filename
        if path.endswith("WeChatWin.dll"):
            WeChatWindll_size = m.SizeOfImage
            WeChatWindll_base = m.lpBaseOfDll

    print("WeChatWin.dll size: ", hex(WeChatWindll_size))
    print("WeChatWin.dll base address: ", hex(WeChatWindll_base))

    @work_time
    def _():
        wheres = []
        data = pm.read_bytes(WeChatWindll_base, WeChatWindll_size)
        values = list(struct.unpack_from(f"<{len(data) // 4}I", data))
        try:
            while index := values.index(old_value, wheres[-1] + 1 if wheres else 0):
                wheres.append(index)
        except ValueError:
            print(wheres)
            for where in wheres:
                pm.write_uint(WeChatWindll_base + where * 4, new_value)


if __name__ == "__main__":
    pm = Pymem("WeChat.exe")
    fix_version(pm)
