from simplemapper import BaseMapper

class TestOrClass(BaseMapper):
    rows=(('num', 'int'), ('body', 'text'))

mapper=TestOrClass()
mapper.create(ignore_error=True)

for i in range(10):
    ins=mapper.insert(num=1, body='body'+str(i))

ins=TestOrClass(id=1)
ins.num=200
ins.body='shimizu'
ins.update()
    
for ins in mapper.select(num_gt=5):
    print(ins)
