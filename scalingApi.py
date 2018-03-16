#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/3/16 17:12
# @Author  : ysj
from baseApi import BaseApi
import _config as conf


class ScalingApi(BaseApi):
    """
    api版本,及请求地址需要变更，其他继承即可
    """
    def __init__(self, ak, secret, region_id, formats='json', url='https://ess.aliyuncs.com', version='2014-08-28'):
        super().__init__(ak, secret, region_id, formats=formats, url=url, version=version)


if __name__ == '__main__':
    b = ScalingApi(conf.ak, conf.secret, conf.region)
    print(b.get('DescribeScalingGroups', RegionId=conf.region))
