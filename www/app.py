#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    web App建立在asyncio的基础上，因此用aiohttp写一个基本的app.py
    
    在这里遇到三个坑：
    坑1:加上utf-8编码提示，否则有可能报错，虽然我没有
    
    坑2：默认notepad++使用ASCI编码导致编译一直报错，改成UTF-8 无BOM后，没事了
    
    坑3：如下所示如果一个语句后面需要再跟一个语句，应该用分号分开，这样的好处是可以
         把紧密相关，又至关重要的语句放在显眼的地方，因为随时可以方便修改日志显示级别
"""
import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime
'''
    使用 pip3 install aiohttp 安装aiohttp
'''
from aiohttp import web

'''
    url处理函数，通过下面的add_route方法与服务器代码相连
    Response函数的body参数对应网页的代码
    看着这个简单，但是后面大部分不过是在这个框架上加更多的细节，
    譬如把add_route封装等等的方法，后面遇见复杂的情形应该再回来
    看看

    问题:访问网址提示下载文件
    原因:不指定 content_type 的话，默认返回 application/octet-stream ，也就是返回文件是“.*（ 二进制流，不知道下载文件类型）”
         没有扩展名，浏览器没法正常解读；看来这个锅应该要aiohttp来背

    content-type 是 octet-stream 表明他就是一个字节流，浏览器默认处理字节流的方式就是下载。
'''

def index(request):
    return web.Response(body=b'<h1>Awesome</h1>',content_type='text/html')

    
'''   
    @asyncio.coroutine
    将以上换成如下，yield from换成了 await
    这里的loop.create_server 和 之前的wsgiref.simple_server 中的make_server
    loop.create_server利用asyncio创建TCP服务
    make_server也是创建TCP服务

    感觉这里的服务相对TCP编程那节更上层了，TCP编程那节更基础，这里只是用来做HTTP相关的网络传输
    而TCP是http的基础但比它更基础，可以做更多的事情不仅仅是http，还可以有其他的协议，只不过他们
    都是比TCP更抽象
'''
async def init(loop):
    app = web.Application(loop=loop)
    #这就是我们有的时候面对巨大的代码
    #迫切想要找到的整体的框架
    app.router.add_route('GET', '/', index)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv

  
'''
    异步io的消息循环机制，这个也需要好好看看
    异步IO模型需要一个消息循环，在消息循环中，主线程不断地重复“读取消息-处理消息”这一过程：

    loop = get_event_loop()
    while True:
        event = loop.get_event()
        process_event(event)

    asyncio可以实现单线程并发IO操作
    把asyncio用在服务器端，例如Web服务器，由于HTTP连接就是IO操作，因此可以用单线程+coroutine实现多用户的高并发支持   
'''  
loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
