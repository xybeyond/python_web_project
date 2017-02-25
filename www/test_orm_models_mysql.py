import orm,asyncio
from models import User, Blog, Comment

loop = asyncio.get_event_loop()

async def test():
    
    await orm.create_pool(loop=loop,user='xiaoyuan', password='123654', db='awesome')
    u = User(name='Test', email='test8@example.com', passwd='1234567890', image='about:blank')
    await u.save()
       

loop.run_until_complete(test())
loop.close()
