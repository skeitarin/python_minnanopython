print('==========start============')

def test():
    # a=''
    # b='keita'
    # print(a, b)
    # locals().update(a)
    # print(locals())
    # print(a, b)
    print(locals())
    locals().update({'aaa':1})

    print(locals())
    print(aaa)
    aaaaaa=eval('aaa')
    # print(eval('aaa'))
    print(locals())


test()

print('==========end============')