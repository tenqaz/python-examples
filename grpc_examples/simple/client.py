"""
@author: Jim
@project: python-examples
@file: client.py
@time: 2022/9/6 10:23
@desc:  
    
"""

import logging

import grpc

from simple.proto import user_pb2, user_pb2_grpc


def run():
    # 连接rpc服务
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = user_pb2_grpc.UserStub(channel)

        # 调用rpc服务的AddUser方法
        response: user_pb2.UserResponse = stub.AddUser(user_pb2.UserRequest(name="zhangsan", age=18))
        print("add user, response is 'msg={}, code={}'".format(response.msg, response.code))

        # 调用rpc服务的GetUser方法
        response: user_pb2.GetUserResponse = stub.GetUser(user_pb2.GetUserRequest(name="lisi"))
        print("get user[name={}, age={}]".format(response.name, response.age))


if __name__ == '__main__':
    logging.basicConfig()
    run()
