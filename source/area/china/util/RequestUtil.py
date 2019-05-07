# -*- coding: UTF-8 -*-
"""
@description 工具类，requests库二次封装
@author wendell
"""
import requests
from requests.exceptions import InvalidURL


def get(url, timeout=None, headers=None, encoding=None):
    """
    发送GET请求
    :param url: URL
    :param timeout: 超时时间(秒)
    :param headers: 头部信息
    :param encoding: 编码
    :return:
    """
    # 参数验证,URL不能为空
    if not url:
        raise InvalidURL("Invalid URL %r" % url)
    response = requests.get(url, headers=headers, timeout=timeout)
    if not response:
        return None
    if encoding:
        response.encoding = encoding
    if response.status_code == 200:
        r_text = response.text
        response.close()
        return r_text
    response.close()
    return None


def prepare_url(url):
    """
    预处理URL连接，规范url
    www.a.com  //www.a.com ==>> http://www.a.com
    :param url: URL
    :return: 处理的URL
    """
    if not url:
        return None
    res = url
    if url.startswith('//'):
        res = 'http:' + url
    elif not url.startswith('http://') and not url.startswith('https://'):
        res = 'http://' + url
    return res
