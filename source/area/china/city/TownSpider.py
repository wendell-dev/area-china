# -*- coding: UTF-8 -*-
"""
@description 获取统计用区划代码和城乡划分代码 (四级：镇、乡、民族乡、县辖区、街道)
@author wendell
"""
import random
import time

from pyquery import PyQuery

from source.area.china.util import DbUtil, RequestUtil


def start_requests(encoding, headers):
    """
    开始请求四级：镇、乡、民族乡、县辖区、街
    :param encoding 编码
    :param headers header
    :return:
    """
    db = DbUtil.get_db()
    while True:
        try:
            # 查询三级集合中存在URL的并且没有搜索过下级链接地址的数据
            counties = db['county'].find({'searched': False, 'url': {'$ne': None}})
            if not counties.count():
                break
            for county in counties:
                if not county.get('url'):
                    continue
                print('开始获取[', county.get('province_name'), '-', county.get('city_name'),
                      '-', county.get('name'), ']下的四级乡镇信')
                res = RequestUtil.get(url=county.get('url'), timeout=5, headers=headers, encoding=encoding)
                if not res:
                    print(county.get('name'), '请求失败...')
                    continue
                doc = PyQuery(res, url=county.get('url'), encoding=encoding)
                if not doc:
                    print('四级乡镇信息获取错误,检查页面变化...')
                towns = []
                for tr in doc('.towntr').items():
                    tr.make_links_absolute()
                    data = tr('a').text().split()
                    towns.append({
                        'code': data[0],  # 统计汇总识别码-划分代码
                        'name': data[1],  # 镇级名称
                        'county_id': county.get('_id'),  # 区县ID
                        'county_name': county.get('name'),  # 区县名称
                        'city_id': county.get('city_id'),  # 市ID
                        'city_name': county.get('city_name'),  # 市名称
                        'province_id': county.get('province_id'),  # 省ID
                        'province_name': county.get('province_name'),  # 省名称
                        'url': tr('a').attr('href'),  # 下级链接地址
                        'searched': False  # 是否搜索过下级链接地址
                    })
                # 更新区县信息
                county['searched'] = True
                db['county'].save(county)
                print(towns)
                # 准备入库, 镇级信息, 添加到collection集合(数据库表)里
                db['town'].insert_many(towns)
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
