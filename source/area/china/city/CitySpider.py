# -*- coding: UTF-8 -*-
"""
@description 获取统计用区划代码和城乡划分代码 (二级：地级市)
@author wendell
"""
from source.area.china.util import DbUtil, RequestUtil
from pyquery import PyQuery
import time
import random


def start_requests(encoding, headers):
    """
    开始请求二级：地级市
    :param encoding 编码
    :param headers header
    :return:
    """
    db = DbUtil.get_db()
    while True:
        try:
            # 查询一级集合中存在URL的并且没有搜索过下级链接地址的数据
            provinces = db['province'].find({'searched': False, 'url': {'$ne': None}})
            if not provinces.count():
                break
            for province in provinces:
                if not province.get('url'):
                    continue
                print('开始获取[', province.get('name'), ']下的二级地级市...')
                res = RequestUtil.get(url=province.get('url'), headers=headers, encoding=encoding)
                if not res:
                    print(province.get('name'), '请求失败...')
                    continue
                doc = PyQuery(res, url=province.get('url'), encoding=encoding)
                if not doc:
                    print('二级地级市信息获取错误,检查页面变化...')
                    continue
                # 当前一级下的所有二级地级市信息
                cities = []
                for tr in doc('.citytr').items():
                    tr.make_links_absolute()
                    data = tr('a').text().split()
                    cities.append({
                        'code': data[0],  # 统计汇总识别码-划分代码
                        'name': data[1],  # 城市名称
                        'province_id': province.get('_id'),  # 省ID
                        'province_name': province.get('name'),  # 省名称
                        'url': tr('a').attr('href'),  # 下级链接地址
                        'searched': False  # 是否搜索过下级链接地址
                    })
                # 更新省级信息
                province['searched'] = True
                db['province'].save(province)
                print(cities)
                # 准备入库, 城市信息, 添加到collection集合(数据库表)里
                db['city'].insert_many(cities)
        except Exception as e:
            print(e)
            print('休眠中.....')
            time.sleep(round(5 + random.uniform(1, 3), 2))
    print('数据获取完毕')
    DbUtil.close_client(db.client)


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
    encoding = 'gb2312'
    start_requests(encoding, headers)


if __name__ == '__main__':
    main()
