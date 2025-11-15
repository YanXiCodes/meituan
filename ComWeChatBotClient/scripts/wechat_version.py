old_version = "3.7.0.30"
new_version = "4.0.6.26"


def decode_version(version: str) -> str:
    hex_version = "".join(
        map(lambda x: hex(int(x)).replace("x", "")[-2:], version.split("."))
    )
    return "0x6" + hex_version[1:]


old_hex = decode_version(old_version)
new_hex = decode_version(new_version)
print(old_version, ":", old_hex)
print(new_version, ":", new_hex)


def encode_version(hex_version: str) -> str:
    # 去掉0x
    hex_str = hex_version[2:]
    # 把第一个字符（最高位）替换为 0
    new_hex_str = "0" + hex_str[1:]
    # 转回10进制
    new_hex_num = int(new_hex_str, 16)
    # 按位还原版本号
    major = (new_hex_num >> 24) & 0xFF
    minor = (new_hex_num >> 16) & 0xFF
    patch = (new_hex_num >> 8) & 0xFF
    build = (new_hex_num >> 0) & 0xFF
    # 拼接版本号
    return "{}.{}.{}.{}".format(major, minor, patch, build)


print(old_hex, ":", encode_version(old_hex))
print(new_hex, ":", encode_version(new_hex))
