#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/3/15 17:02
# @Author  : ysj
from baseApi import BaseApi
import _config as conf


class EcsApi(BaseApi):
    """
        api版本,及请求地址需要变更，其他继承即可
    """
    def __init__(self, ak, secret, region_id, formats='json', url='https://ecs.aliyuncs.com/', version='2014-05-26'):
        super().__init__(ak, secret, region_id, formats=formats, url=url)


if __name__ == '__main__':
    a = EcsApi(conf.ak, conf.secret, conf.region)
    print(a.get('DescribeInstances', PageSize=100, RegionId=conf.region))
