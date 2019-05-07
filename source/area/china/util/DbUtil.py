# -*- coding: UTF-8 -*-
"""
@description 工具类，数据库
@author wendell
"""
from pymongo import MongoClient


def get_client():
    """
    获取连接客户端
    :return: 链接客户端
    """
    return MongoClient("mongodb://localhost:27017/", connect=False)


def get_db(db=None):
    """
    获取数据库
    :param db: 默认链接到python数据库
    :return:
    """
    if not db:
        db = 'python'
    return get_client().get_database(name=db)


def close_client(client):
    """
    关闭客户端连接
    :param client: 连接客户端
    :return:
    """
    if client:
        client.close()
