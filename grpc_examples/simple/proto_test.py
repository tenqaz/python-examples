"""
@author: Jim
@project: python-examples
@file: proto_test.py
@time: 2022/9/6 9:58
@desc:  
    
"""

from simple.proto import user_pb2

# 创建Student对象，将该对象序列化成字符串
s = user_pb2.UserRequest()
s.name = "zhangsan"
s.age = 12
req_str = s.SerializeToString()
print(req_str)

# 将上面的输出的序列化字符串反序列化成对象
s2 = user_pb2.UserRequest()
s2.ParseFromString(req_str)
print(s2.name)
print(s2.age)
