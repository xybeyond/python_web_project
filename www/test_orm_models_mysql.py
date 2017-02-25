import orm,asyncio,logging
from models import User, Blog, Comment
from orm import destroy_pool

loop = asyncio.get_event_loop()

#在这里才知道写测试用例的重要性，否则一旦整体联调的时候再去找bug，我操，那是要死人的，而且用去的时间
#也是大把大把的，太浪费时间和效率了，
#还有再这个过程中跟别人比发现自己太他妈的懒了，难怪就是一个错比
async def test():
    
    await orm.create_pool(loop=loop,user='xiaoyuan', password='123654', db='awesome')
    #u = User(name='Test', email='test8@example.com', passwd='1234567890', image='about:blank')
    #await u.save()
    # 测试count rows语句
    rows = await User.findNumber('id')
    logging.info('rows is %s' % rows)
    rows = 1
    if rows < 3:
        for idx in range(5):
            u = User(
                name='test18%s' % idx,
                email='test18%s@org.com' % idx,
                passwd='orm1234%s' % idx,
                image='about:blank'
            )
            row = await User.findNumber('id')
            if rows > 0:
                await u.save()
            else:
                print('the email is already registered...')

    # 测试select语句
    users = await User.findAll(orderBy='created_at')
    for user in users:
        logging.info('name: %s, password: %s, created_at: %s' % (user.name, user.passwd, user.created_at))

    # 测试update语句
    user = users[1]
    user.email = 'guest@orm.com'
    user.name = 'guest'
    await user.update()

    # 测试查找指定用户
    test_user = await User.find(user.id)
    logging.info('name: %s, email: %s' % (test_user.name, test_user.email))

    # 测试delete语句
    users = await User.findAll(orderBy='created_at', limit=(0, 3))
    for user in users:
        logging.info('delete user: %s' % user.name)
        await user.remove()

    await destroy_pool()  # 这里先销毁连接池
    print('test ok')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()   

#loop.run_until_complete(test())
#loop.close()
