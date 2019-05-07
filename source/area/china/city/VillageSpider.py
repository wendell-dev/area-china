# -*- coding: UTF-8 -*-
"""
@description 获取统计用区划代码和城乡划分代码 (五级：村、居委会)
@author wendell
"""
from source.area.china.util import DbUtil, RequestUtil
from pyquery import PyQuery
import time
import random


def start_requests(encoding, headers):
    """
    开始请求五级：村、居委会
    :param encoding 编码
    :param headers header
    :return:
    """
    db = DbUtil.get_db()
    while True:
        try:
            # 查询四级集合中存在URL的并且没有搜索过下级链接地址的数据
            towns = db['town'].find({'searched': False, 'url': {'$ne': None}})
            if not towns.count():
                break
            data_list = list(towns)
            towns.close()
            for town in data_list:
                if not town.get('url'):
                    continue
                print('开始获取[', town.get('province_name'), '-', town.get('city_name'),
                      '-', town.get('county_name'), '-', town.get('name'), ']下的五级村居委会信息')
                res = RequestUtil.get(url=town.get('url'), timeout=3, headers=headers, encoding=encoding)
                if not res:
                    print(town.get('name'), '请求失败...')
                    continue
                doc = PyQuery(res, url=town.get('url'), encoding=encoding)
                if not doc:
                    print('五级村居委会信息获取错误,检查页面变化...')
                villages = []
                for tr in doc('.villagetr').items():
                    data = tr('td').text().split()
                    villages.append({
                        'code': data[0],  # 统计汇总识别码-划分代码
                        'code_type': data[1],  # 城乡分类代码
                        'name': data[2],  # 村级名称
                        'town_id': town.get('_id'),  # 镇级ID
                        'town_name': town.get('name'),  # 镇级名称
                        'county_id': town.get('county_id'),  # 区县ID
                        'county_name': town.get('county_name'),  # 区县名称
                        'city_id': town.get('city_id'),  # 市ID
                        'city_name': town.get('city_name'),  # 市名称
                        'province_id': town.get('province_id'),  # 省ID
                        'province_name': town.get('province_name')  # 省名称
                    })
                doc.clear()
                # 更新镇级信息
                town['searched'] = True
                db['town'].save(town)
                print(villages)
                # 准备入库, 村级信息, 添加到collection集合(数据库表)里
                db['village'].insert_many(villages)
                villages.clear()
        except Exception as e:
            print(e)
            print('休眠中.....')
            time.sleep(round(1 + random.uniform(1, 3), 2))
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
