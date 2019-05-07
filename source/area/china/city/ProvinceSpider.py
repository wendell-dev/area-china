# -*- coding: UTF-8 -*-
"""
@description 获取统计用区划代码和城乡划分代码 (一级：省、直辖市、自治区)
@author wendell
"""
from source.area.china.util import DbUtil, RequestUtil
from pyquery import PyQuery


def start_requests(domain_url, encoding, headers):
    """
    开始请求一级：省、直辖市、自治区
    :param domain_url url
    :param encoding 编码
    :param headers header
    :return:
    """
    res = RequestUtil.get(url=domain_url, headers=headers, encoding=encoding)
    if not res:
        print('请求失败...')
        return None
    doc = PyQuery(res, url=domain_url, encoding=encoding).find('.provincetr')
    if not doc:
        print('首页省份信息获取错误,检查页面变化...')
        return None
    # 获取到数据库链接
    client = DbUtil.get_client()
    # 选择数据库
    db = client["python"]
    provinces = []
    for td in doc('td').items():
        a_tag = td('a')
        if a_tag:
            # 生成URL绝对路径
            a_tag.make_links_absolute()
            # print('%s %s' % (a_tag.attr('href'), a_tag.text()))
            provinces.append({
                'code': a_tag.attr('href').split('/')[-1].split('.')[0],  # 统计汇总识别码-划分代码
                'name': a_tag.text(),  # 省份名称
                'url': a_tag.attr('href'),  # 下级链接地址
                'searched': False  # 是否搜索过下级链接地址
            })
    print(provinces)
    # 准备入库, 省份信息, 添加到collection集合(数据库表)里
    db['province'].insert_many(provinces)
    DbUtil.close_client(client)


def main():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.stats.gov.cn',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 '
                      'Safari/537.36'
    }
    # 更改年份只需要更改这里即可,明年2020年的时候会发布2019年的数据，如果想获取2019年的就把这里改为2019再重新执行程序即可
    year = '2018'
    domain_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/' + year + '/index.html'
    encoding = 'gb2312'
    start_requests(domain_url, encoding, headers)


if __name__ == '__main__':
    main()
