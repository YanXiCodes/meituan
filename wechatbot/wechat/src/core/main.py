import asyncio
import json
import websockets # 导入我们刚刚安装的库
from nonebot import get_bot, get_driver
from nonebot.log import logger


GROUP_ID = "43754149608@chatroom" 

HEADERS = {
    "Cookie": "bizType=2; edper=BqJDFOSadHaxdFY860BxcFvX3gBMRAarUaImyJrCAFu135wXDKUtOg-pupYXTi2OdPcGFMEdJT2i3KYtWJAtPw; _gw_ab_call_15533_83=TRUE; _gw_ab_15533_83=478; utm_source_rg=; merchantCategoryID=34319; _lxsdk_cuid=1986474fd0bc8-0fadebe4a7984c-4c657b58-384000-1986474fd0bc8; _lxsdk=1986474fd0bc8-0fadebe4a7984c-4c657b58-384000-1986474fd0bc8; _hc.v=2922436f-af95-bd1c-3f95-cd879f69da94.1754032045; AWPTALOS2056=; AWPTALOS32837=; WEBDFPID=4v4vz801v0y55u590046w1081562w4uy8013524848797958x4u79915-1754118452887-1754032043028OISWUQMfd79fef3d01d5e9aadc18ccd4d0c95071881; mpmerchant_portal_shopid=674479677; merchantBookShopID=674479677; _lxsdk_s=1986474fd0b-a83-843-880%7C%7C341; logan_session_token=dcy9nsqiui1itsl439f2",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
}

WEBSOCKET_URL = "wss://pikem0-bj.sankuai.com/pike/?bizId=msg_pike_client_dz&EIO=3&transport=websocket" 



