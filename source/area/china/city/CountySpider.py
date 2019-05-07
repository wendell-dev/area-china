# -*- coding: UTF-8 -*-
"""
@description 获取统计用区划代码和城乡划分代码 (三级：市辖区、县（旗）、县级市、自治县（自治旗）、特区、林区)
@author wendell
"""
from source.area.china.util import DbUtil, RequestUtil
from pyquery import PyQuery
import time
import random


def start_requests(encoding, headers):
    """
    开始请求三级：市辖区、县（旗）、县级市、自治县（自治旗）、特区、林区
    :param encoding 编码
    :param headers header
    :return:
    """
    db = DbUtil.get_db()
    while True:
        try:
            # 查询二级集合中存在URL的并且没有搜索过下级链接地址的数据
            cities = db['city'].find({'searched': False, 'url': {'$ne': None}})
            if not cities.count():
                break
            for city in cities:
                if not city.get('url'):
                    continue
                print('开始获取[', city.get('province_name'), '-', city.get('name'), ']下的三级区县信息...')
                res = RequestUtil.get(url=city.get('url'), headers=headers, encoding=encoding)
                if not res:
                    print(city.get('name'), '请求失败...')
                    continue
                doc = PyQuery(res, url=city.get('url'), encoding=encoding)
                if not doc:
                    print('三级区县信息获取错误,检查页面变化...')
                    continue
                # 当前二级下的所有三级区县信息
                counties = []
                for tr in doc('.countytr').items():
                    tr.make_links_absolute()
                    data = tr('a').text().split()
                    if not tr('a') or not data:
                        # 当非直辖市的区县有一个市辖区无下级链接
                        data = tr('td').text().split()
                    item = {
                        'code': data[0],  # 统计汇总识别码-划分代码
                        'name': data[1],  # 区县名称
                        'city_id': city.get('_id'),  # 市ID
                        'city_name': city.get('name'),  # 市名称
                        'province_id': city.get('province_id'),  # 省ID
                        'province_name': city.get('province_name')  # 省名称
                    }
                    if not tr('a') or not data:
                        item.setdefault('url', None)
                        item.setdefault('searched', True)
                    else:
                        item.setdefault('url', tr('a').attr('href'))  # 下级链接地址
                        item.setdefault('searched', False)  # 是否搜索过下级链接地址
                    counties.append(item)
                # 更新市级信息
                city['searched'] = True
                db['city'].save(city)
                print(counties)
                # 准备入库, 区县信息, 添加到collection集合(数据库表)里
                db['county'].insert_many(counties)
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
