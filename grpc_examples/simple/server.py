"""
@author: Jim
@project: python-examples
@file: server.py
@time: 2022/9/6 9:26
@desc:  
    
"""

import logging
from concurrent import futures

import grpc

from simple.proto import user_pb2, user_pb2_grpc


class UserService(user_pb2_grpc.UserServicer):

    # 实现proto文件中rpc的调用
    def AddUser(self, request: user_pb2.UserRequest, context):
        return user_pb2.UserResponse(msg='add user(name={},age={}) success'.format(request.name, request.age), code=0)

    def GetUser(self, request: user_pb2.GetUserRequest, context):
        return user_pb2.GetUserResponse(name=request.name, age="1888")


def serve():
    # 使用线程池来完成grpc的请求
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    user_pb2_grpc.add_UserServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')  # 绑定端口
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
