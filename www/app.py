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
from jinja2 import Environment, FileSystemLoader

import orm
import pdb
from coroweb import add_routes, add_static

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
    def index(request):
    return web.Response(body=b'<h1>Awesome</h1>',content_type='text/html')
'''

def index(request):
    return web.Response(body=b'<h1>Awesome</h1>',content_type='text/html')

def init_jinja2(app, **kw):
    logging.info('init jinja2...')
    options = dict(
        autoescape = kw.get('autoescape', True),
        block_start_string = kw.get('block_start_string', '{%'),
        block_end_string = kw.get('block_end_string', '%}'),
        variable_start_string = kw.get('variable_start_string', '{{'),
        variable_end_string = kw.get('variable_end_string', '}}'),
        auto_reload = kw.get('auto_reload', True)
        )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 templates path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env
    

async def logger_factory(app, handler):
    
    async def logger(request):
        #pdb.set_trace()
        logging.info('Request: %s %s' %(request.method, request.path))
        return await handler(request)
    return logger

    

async def data_factory(app, handler):
    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()
                logging.info('request json: %s' % str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencode'):
                request.__data__ = await request.post()
                logging.info('request form: %s' % str(request.__data__))
        return (await handler(request))
    return parse_data

#找了半天终于找到问题在哪了，擦竟然是缩进有问题导致程序无法按照正常的顺序运行造成的
async def response_factory(app, handler):
    async def response(request):
        logging.info('Response handler...')
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json; charset=utf-8'
                return resp
            else:
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
         
        if isinstance(r, int) and r >= 100 and r < 600:
            return web.Response(r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                return web.Response(t, str(m))
    
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/html;charset=utf-8'
        return resp
    return response

def datetime_filter(t):
    delta = int(time.time() - t)
    if delta  < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' %( delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.formtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)
    
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
    await orm.create_pool(loop=loop, host='127.0.0.1', port= 3306, user='xiaoyuan', password='123654', db='awesome')
    #app = web.Application(loop=loop,middlewares=[logger_factory])
    app = web.Application(loop=loop, middlewares=[logger_factory,response_factory])
    #这就是我们有的时候面对巨大的代码
    #迫切想要找到的整体的框架
    #app.router.add_route('GET', '/', index)
    init_jinja2(app, filters=dict(datetime = datetime_filter))
    add_routes(app, 'handlers')
    add_static(app)
    #app.router.add_route('GET', '/', index)
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
